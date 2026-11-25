"""Read-only Developer selection policy for read_ready.py --select."""

import json
from dataclasses import dataclass
from pathlib import Path
import re

if __package__:
    from .orchestrate import BASE_BRANCH, REPOSITORY, Blocked, registered_worktrees, run_cmd
else:
    from orchestrate import BASE_BRANCH, REPOSITORY, Blocked, registered_worktrees, run_cmd

OWNER, REPO = REPOSITORY.split("/")
PRIORITIES = ("Urgent", "High", "Medium", "Low")
IMPLEMENTATION_TYPES = {"Feature", "Bug", "Task", "Spike"}
APPROVAL_FIELD = "Requires human approval"

OPEN_PRS = """
query ($owner: String!, $repo: String!, $endCursor: String) {
  repository(owner: $owner, name: $repo) {
    pullRequests(states: [OPEN], first: 30, after: $endCursor) {
      nodes {
        number headRefName isDraft
        closingIssuesReferences(first: 100) {
          nodes { number repository { nameWithOwner } }
          pageInfo { hasNextPage }
        }
      }
      pageInfo { hasNextPage endCursor }
    }
  }
}
"""

ISSUE_PRS = """
query ($owner: String!, $repo: String!, $number: Int!) {
  repository(owner: $owner, name: $repo) {
    issue(number: $number) {
      closedByPullRequestsReferences(first: 1, includeClosedPrs: false) {
        nodes { url isDraft }
      }
    }
  }
}
"""

CLOSURE = """
query ($owner: String!, $repo: String!, $number: Int!) {
  repository(owner: $owner, name: $repo) {
    issue(number: $number) {
      state stateReason body author { login } editor { login }
      timelineItems(last: 1, itemTypes: [CLOSED_EVENT, REOPENED_EVENT]) {
        nodes {
          __typename
          ... on ClosedEvent {
            actor { login }
            closer {
              __typename
              ... on PullRequest {
                number merged baseRefName repository { nameWithOwner } mergedBy { login }
              }
            }
          }
        }
      }
    }
  }
}
"""


class SelectionError(Exception):
    pass


def repository_query(read, context, query, *args, **kwargs):
    return read(context, "graphql", "-f", f"query={query}",
                "-f", f"owner={OWNER}", "-f", f"repo={REPO}", *args, **kwargs)


def repository_result(page, context):
    if page.get("errors") or not page["data"]["repository"]:
        raise SelectionError(f"{context}: GitHub GraphQL error or repository unavailable")
    return page["data"]["repository"]


def open_prs(read):
    context = "Open pull requests"
    result = []
    seen_cursors = set()
    cursor_args = ()
    while True:
        # gh --paginate can read hasNextPage from the nested closing links
        # instead of the outer pullRequests connection.
        page = repository_query(read, context, OPEN_PRS, *cursor_args)
        prs = repository_result(page, context)["pullRequests"]
        for pr in prs["nodes"]:
            refs = pr["closingIssuesReferences"]
            if not refs or refs["pageInfo"]["hasNextPage"] is not False:
                raise SelectionError(f"PR #{pr['number']}: closing issue links could not be fully verified")
            result.append((pr, {issue["number"] for issue in refs["nodes"]
                                if issue["repository"]["nameWithOwner"].casefold() == REPOSITORY.casefold()}))
        page_info = prs["pageInfo"]
        if page_info["hasNextPage"] is False:
            break
        if page_info["hasNextPage"] is not True:
            raise SelectionError(f"{context}: invalid pagination flag")
        cursor = page_info.get("endCursor")
        if not isinstance(cursor, str) or not cursor.strip():
            raise SelectionError(f"{context}: missing or invalid cursor")
        if cursor in seen_cursors:
            raise SelectionError(f"{context}: repeated cursor")
        seen_cursors.add(cursor)
        cursor_args = ("-f", f"endCursor={cursor}")
    return sorted(result, key=lambda entry: entry[0]["number"])


def issue_pr_exclusion(read, number):
    # One open link is enough to exclude a candidate, including links made
    # from the issue sidebar to PRs targeting another repository.
    context = f"Linked pull requests for #{number}"
    issue = repository_result(repository_query(read, context, ISSUE_PRS, "-F", f"number={number}"),
                              context)["issue"]
    refs = issue["closedByPullRequestsReferences"] if issue else None
    if refs is None or refs["nodes"] is None:
        raise SelectionError(f"{context}: closing issue links could not be verified")
    if refs["nodes"]:
        pr = refs["nodes"][0]
        draft = "draft " if pr["isDraft"] else ""
        return f"existing open {draft}PR {pr['url']}; Lead triage"
    return None


def branch_issue(branch):
    match = re.match(r"^agent/issue-(\d+)(?:[-/]|$)", branch)
    return int(match[1]) if match else None


def local_work():
    """Use the runner's primary-checkout-relative run and registered worktree conventions."""
    current = Path.cwd()
    try:
        origin = run_cmd(["git", "remote", "get-url", "origin"], current)
        if not re.search(rf"github\.com[:/]{re.escape(REPOSITORY)}(?:\.git)?$", origin, re.I):
            raise SelectionError(f"--select requires a checkout with origin pointing to {REPOSITORY}")
        trees = registered_worktrees(current)
        if not trees:
            raise SelectionError("Git did not identify the primary checkout")
        primary = trees[0]["path"]
        run_home = primary.parent / f".{primary.name}-agent-runs"
        try:
            entries = list(run_home.iterdir())
        except FileNotFoundError:
            entries = []
    except (Blocked, OSError) as error:
        raise SelectionError("Cannot inspect local runner state and worktrees; verify the checkout and access") from error

    found = {}
    for entry in sorted(entries):
        match = re.fullmatch(r"issue-(\d+)(?:-review-pr-.+)?", entry.name)
        if match:
            found[int(match[1])] = f"existing local run {entry.name}; Lead triage"
    for tree in trees:
        number = branch_issue(tree.get("branch", "").removeprefix("refs/heads/"))
        if number is None and tree["path"] != primary and tree["path"].parent == primary.parent:
            match = re.fullmatch(rf"{re.escape(primary.name)}-(?:agent|review|issue)-(\d+)(?:-.+)?",
                                 tree["path"].name)
            if match:
                number = int(match[1])
        if number is not None:
            found.setdefault(number, f"existing registered worktree {tree['path'].name}; Lead triage")
    return found


def native_options(fields, name, *, allow_multiple=False):
    """Return option names, () for an absent field, or None if not verifiable."""
    rows = []
    for field in fields:
        if not isinstance(field, dict) or not valid_name(field.get("issue_field_name")):
            return None
        if field["issue_field_name"] == name:
            rows.append(field)
    if not rows:
        return ()
    if len(rows) > 1:
        return None
    row = rows[0]
    if (row.get("data_type") == "single_select"
            and row.get("multi_select_options") in (None, [])):
        options = [row.get("single_select_option")]
    elif (allow_multiple and row.get("data_type") == "multi_select"
          and row.get("single_select_option") is None):
        options = row.get("multi_select_options")
    else:
        return None
    if not isinstance(options, list) or not options:
        return None
    names = []
    for option in options:
        value = option.get("name") if isinstance(option, dict) else None
        if not valid_name(value) or value in names:
            return None
        names.append(value)
    return tuple(names)


def valid_name(value):
    return isinstance(value, str) and bool(value.strip()) and value.strip() == value


def native_option(fields, name):
    names = native_options(fields, name)
    return names[0] if names else None


def nonempty_body_lines(body):
    return [line for line in (body or "").splitlines() if line.strip()]


def exclusion(issue, fields, blockers):
    if issue.get("state") != "open":
        return "issue is not open or state is unavailable"
    if not isinstance(issue.get("labels"), list):
        return "Developer assignment is unavailable"
    if not any((label if isinstance(label, str) else label.get("name")) == "agent:developer"
               for label in issue["labels"]):
        return "missing agent:developer label"
    if not isinstance(issue.get("assignees"), list):
        return "assignees are unavailable"
    if any(user.get("type") != "Bot" for user in issue["assignees"]):
        return "human or unverified assignee"
    kind = (issue.get("type") or {}).get("name")
    if kind not in IMPLEMENTATION_TYPES:
        return "Design Decision is human-owned" if kind == "Design Decision" else "missing or invalid native Type"
    if native_option(fields, "Priority") not in PRIORITIES:
        return "missing, invalid or ambiguous native Priority"
    if not native_options(fields, "Workstream", allow_multiple=True):
        return "missing or ambiguous native Workstream"
    approval = native_option(fields, APPROVAL_FIELD)
    if approval != "No":
        return ("human approval is outstanding" if approval == "Yes"
                else f"missing or ambiguous native {APPROVAL_FIELD}")

    body = nonempty_body_lines(issue.get("body"))
    prefix = "Selection-ready implementation;"
    if (not body or not body[0].startswith(prefix)
            or not any(not line.startswith(prefix) for line in body[1:])):
        return "approved implementation or legacy prerequisite reconciliation not confirmed; Lead triage"
    expected = "native" if blockers else "none"
    if body[0] != f"{prefix} prerequisites: {expected}":
        return "ambiguous prerequisite reconciliation or declaration disagrees with native Blocked by; Lead triage"
    total = (issue.get("issue_dependencies_summary") or {}).get("total_blocked_by")
    if type(total) is not int or total != len({b.get("html_url") or b.get("number") for b in blockers}):
        return "native prerequisite count unavailable or disagrees with visible dependencies; Lead triage"
    return None


def owner_login(actor):
    return (actor or {}).get("login", "").casefold() == OWNER.casefold()


def accepted_closure(read, number):
    context = f"Closure of prerequisite #{number}"
    result = repository_result(repository_query(read, context, CLOSURE, "-F", f"number={number}",
                                                missing_issue_ok=True), context)
    issue = result["issue"]
    if not issue:
        return "prerequisite inaccessible"
    if issue["state"] != "CLOSED" or issue["stateReason"] != "COMPLETED":
        return "prerequisite is no longer closed as completed"
    nodes = issue["timelineItems"]["nodes"]
    event = nodes[0] if len(nodes) == 1 else None
    if not event or event["__typename"] != "ClosedEvent":
        return "no current closing event; Lead triage"
    closer = event["closer"]
    if closer is not None:
        if (closer["__typename"] == "PullRequest" and closer["merged"] is True
                and closer["baseRefName"] == BASE_BRANCH
                and closer["repository"]["nameWithOwner"].casefold() == REPOSITORY.casefold()
                and owner_login(closer["mergedBy"])):
            return None
    elif (owner_login(event["actor"]) and owner_login(issue["author"])
          and (issue["editor"] is None or owner_login(issue["editor"]))
          and nonempty_body_lines(issue["body"])[:1] == ["Selection completion: non-code"]):
        return None
    return "no owner-accepted closing merge to main or explicit owner-completed non-code work; Lead triage"


def dependency_waits(blockers, read, closures):
    waits = {}
    for blocker in blockers:
        number = blocker.get("number")
        url = blocker.get("html_url") or ""
        local = bool(number and url.casefold() == f"https://github.com/{REPOSITORY}/issues/{number}".casefold())
        key = (number if local else None, f"#{number}" if local else (url or "unidentified prerequisite"))
        if not local:
            waits[key] = "external or inaccessible prerequisite; Lead triage"
        elif blocker.get("state") == "open":
            waits[key] = "prerequisite is open"
        elif blocker.get("state") != "closed" or blocker.get("state_reason") != "completed":
            waits[key] = f"prerequisite not accepted (state reason: {blocker.get('state_reason') or 'unavailable'})"
        else:
            if number not in closures:
                closures[number] = accepted_closure(read, number)
            if closures[number]:
                waits[key] = closures[number]
    return waits


@dataclass
class Selection:
    eligible: list[int]
    lines: list[str]


def select(numbers, read_issue, read):
    labels, skipped, candidates, waits = {}, {}, {}, {}
    for number in sorted(set(numbers)):
        issue, fields, blockers = read_issue(number)
        if issue["number"] != number:
            raise SelectionError(f"Fetched issue does not match Ready issue #{number}")
        labels[number] = f"#{number} {json.dumps(issue['title'], ensure_ascii=False)}"
        reason = exclusion(issue, fields, blockers)
        if reason:
            skipped[number] = reason
        else:
            candidates[number] = (native_option(fields, "Priority"), blockers)

    if candidates:
        prs, local, closures = open_prs(read), local_work(), {}
        for number, (_, blockers) in candidates.items():
            for pr, links in prs:
                if number in links or branch_issue(pr["headRefName"]) == number:
                    draft = "draft " if pr["isDraft"] else ""
                    skipped[number] = f"existing open {draft}PR #{pr['number']}; Lead triage"
                    break
            if number not in skipped and number in local:
                skipped[number] = local[number]
            if number not in skipped:
                reason = issue_pr_exclusion(read, number)
                if reason:
                    skipped[number] = reason
                else:
                    waits[number] = dependency_waits(blockers, read, closures)

    # Only count unique direct successors that would have no other unsatisfied
    # prerequisite. A waiting successor never becomes eligible in this run.
    unlocks = {}
    for waiting in waits.values():
        if len(waiting) == 1:
            (prerequisite, _), reason = next(iter(waiting.items()))
            if prerequisite is not None and reason == "prerequisite is open":
                unlocks[prerequisite] = unlocks.get(prerequisite, 0) + 1
    eligible = sorted((n for n in waits if not waits[n]),
                      key=lambda n: (-unlocks.get(n, 0), PRIORITIES.index(candidates[n][0]), n))
    lines = ["Eligible issues (in selection order):"]
    for number in eligible:
        lines.append(f"  {labels[number]} — unlocks {unlocks.get(number, 0)} Ready issue(s); {candidates[number][0]}")
    if not eligible:
        lines.append("  (none)")
    lines.append(f"Next issue: {labels[eligible[0]]}" if eligible else "No eligible work.")
    for number, label in labels.items():
        if number in skipped:
            lines.append(f"SKIP {label}: {skipped[number]}")
        elif waits[number]:
            reasons = "; ".join(f"{ref}: {reason}" for (_, ref), reason in waits[number].items())
            lines.append(f"WAIT {label}: {reasons}")
    return Selection(eligible, lines)
