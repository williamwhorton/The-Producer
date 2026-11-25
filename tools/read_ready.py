#!/usr/bin/env python3
"""Report The Producer's GitHub Project Ready column without changing it."""

import argparse
import json
import os
import re
import subprocess
import sys

if __package__:
    from .ready_selection import APPROVAL_FIELD, SelectionError, native_options, select
else:
    from ready_selection import APPROVAL_FIELD, SelectionError, native_options, select

OWNER = "williamwhorton"
REPOSITORY = f"{OWNER}/The-Producer"
API_VERSION = "2026-03-10"
UNAVAILABLE = "(unavailable)"
MISSING = "(not set)"

# See GitHub's GraphQL Projects reference and the gh api pagination manual.
PROJECT_QUERY = """
query ($owner: String!, $number: Int!, $endCursor: String) {
  user(login: $owner) {
    projectV2(number: $number) {
      title url
      field(name: "Status") {
        ... on ProjectV2SingleSelectField { options { id name } }
      }
      items(first: 100, after: $endCursor, archivedStates: [NOT_ARCHIVED]) {
        nodes {
          type
          fieldValueByName(name: "Status") {
            ... on ProjectV2ItemFieldSingleSelectValue { optionId }
          }
          content {
            ... on Issue { number repository { nameWithOwner } }
          }
        }
        pageInfo { hasNextPage endCursor }
      }
    }
  }
}
"""


class ReadError(Exception):
    pass


def gh_json(context, *args, missing_issue_ok=False):
    try:
        result = subprocess.run(
            ["gh", "api", "--hostname", "github.com", *args],
            capture_output=True, text=True, timeout=60, check=False,
        )
    except OSError as error:
        raise ReadError(f"{context}: could not run GitHub CLI ({type(error).__name__})") from error
    except subprocess.TimeoutExpired as error:
        raise ReadError(f"{context}: GitHub CLI request timed out") from error
    if result.returncode:
        # Report only the status, never raw CLI output (which may contain debug data).
        match = re.search(r"\(HTTP ([1-5][0-9]{2})\)", result.stderr)
        status = match[1] if match else None
        if result.returncode == 4 or status == "401":
            raise ReadError(f"{context}: GitHub authentication failed; check gh auth status")
        if missing_issue_ok and status is None:
            # GraphQL may return partial data and a typed NOT_FOUND for this
            # one prerequisite. Do not downgrade repo, auth, or query errors.
            try:
                page = json.loads(result.stdout)
                errors = page.get("errors")
                repo = page["data"]["repository"]
                if (repo["issue"] is None and errors and all(
                        e.get("type") == "NOT_FOUND" and e.get("path") == ["repository", "issue"]
                        for e in errors)):
                    return {"data": page["data"]}
            except (ValueError, AttributeError, KeyError, TypeError):
                pass
        detail = f"HTTP {status}" if status else f"gh exit {result.returncode}"
        raise ReadError(f"{context}: GitHub API/CLI error ({detail}); check access and configuration")
    try:
        return json.loads(result.stdout)
    except ValueError as error:
        raise ReadError(f"{context}: GitHub returned invalid JSON") from error


def project_issues(number, *, status_names=("Ready",)):
    pages = gh_json(
        f"Project #{number}", "graphql", "--paginate", "--slurp", "-f",
        f"query={PROJECT_QUERY}", "-f", f"owner={OWNER}", "-F", f"number={number}",
    )
    if not isinstance(pages, list) or not pages:
        raise ReadError("GitHub returned no Project pages")
    numbers = {name: [] for name in status_names}
    for index, page in enumerate(pages):
        if page.get("errors"):
            raise ReadError(f"Project #{number}: GitHub GraphQL API error; check project access")
        project = (page["data"]["user"] or {}).get("projectV2")
        if not project:
            raise ReadError(f"Project #{number} not found for {OWNER}; check PROJECT_NUMBER and access")
        options = (project["field"] or {}).get("options", [])
        requested = {}
        for name in status_names:
            ids = [option["id"] for option in options if option["name"] == name]
            if len(ids) != 1 or not ids[0] or ids[0] in requested:
                raise ReadError(f"Project #{number}: expected one {name} option in the Status field")
            requested[ids[0]] = name
        items = project["items"]
        if items["pageInfo"]["hasNextPage"] is not (index < len(pages) - 1):
            raise ReadError(f"Project #{number}: incomplete or inconsistent item pagination")
        for item in items["nodes"]:
            status = (item["fieldValueByName"] or {}).get("optionId")
            if item["type"] == "REDACTED" and (status is None or status in requested):
                raise ReadError(f"Project #{number}: an inaccessible item may be a "
                                f"{requested.get(status, '/'.join(status_names))} issue")
            if item["type"] != "ISSUE" or status not in requested:
                continue
            issue = item["content"]
            if not issue:
                raise ReadError(f"Project #{number}: {requested[status]} issue content is unavailable")
            if issue["repository"]["nameWithOwner"].casefold() == REPOSITORY.casefold():
                numbers[requested[status]].append(issue["number"])
    return project["title"], project["url"], numbers


def configured_project():
    number = os.environ.get("PROJECT_NUMBER", "").strip()
    if not re.fullmatch(r"[0-9]{1,10}", number) or not 0 < int(number) < 2**31:
        raise ValueError("Configuration error: set PROJECT_NUMBER to a positive GitHub Project number.")
    return int(number)


def issue_data(number, suffix="", *, paginate=False):
    endpoint = f"repos/{REPOSITORY}/issues/{number}{suffix}"
    paging = ["--paginate", "--slurp"] if paginate else []
    data = gh_json(
        f"#{number}{suffix}", "--method", "GET", "-H", f"X-GitHub-Api-Version: {API_VERSION}",
        "-H", "Accept: application/vnd.github+json",
        *paging, endpoint + ("?per_page=100" if paginate else ""),
    )
    if not paginate:
        return data
    if not isinstance(data, list) or not data or not all(isinstance(page, list) for page in data):
        raise ReadError(f"#{number}{suffix}: expected paginated GitHub REST lists")
    return [row for page in data for row in page]


def ready_issue(number):
    issue = issue_data(number)
    fields = issue_data(number, "/issue-field-values", paginate=True)
    blockers = issue_data(number, "/dependencies/blocked_by", paginate=True)
    return issue, fields, blockers


def issue_lines(number):
    issue, values, blockers = ready_issue(number)

    def option(name, *, allow_multiple=False):
        names = native_options(values, name, allow_multiple=allow_multiple)
        return UNAVAILABLE if names is None else ", ".join(names) or MISSING

    labels = issue.get("labels")
    assigned = issue.get("assignees")
    developer = UNAVAILABLE if labels is None else (
        "yes" if any(
            (label if isinstance(label, str) else label["name"]) == "agent:developer"
            for label in labels
        ) else "no"
    )
    assignees = UNAVAILABLE if assigned is None else (
        ", ".join(f"@{user['login']}" for user in assigned if user.get("type") != "Bot") or "(none)"
    )
    issue_type = UNAVAILABLE if "type" not in issue else (
        (issue["type"] or {}).get("name") or MISSING
    )
    lines = [
        f"#{number} {json.dumps(issue['title'], ensure_ascii=False)}",
        f"  agent:developer: {developer}; human assignees: {assignees}",
        f"  Type: {issue_type}; Priority: {option('Priority')}; "
        f"Workstream: {option('Workstream', allow_multiple=True)}; {APPROVAL_FIELD}: {option(APPROVAL_FIELD)}",
        "  Blocked by:" if blockers else "  Blocked by: (none)",
    ]
    for blocker in blockers:
        reason = UNAVAILABLE if "state_reason" not in blocker else blocker["state_reason"] or MISSING
        url = f" — {blocker['html_url']}" if blocker.get("html_url") else ""
        lines.append(f"    #{blocker['number']}: {blocker.get('state') or UNAVAILABLE}; reason: {reason}{url}")
    return lines


def main():
    parser = argparse.ArgumentParser(
        description=__doc__ + " Set PROJECT_NUMBER to the configured project number."
    )
    parser.add_argument("--select", action="store_true",
                        help="rank eligible Developer issues without starting work")
    args = parser.parse_args()
    try:
        number = configured_project()
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2
    try:
        title, url, statuses = project_issues(number)
        numbers = statuses["Ready"]
        # Do not print a successful-looking partial report if a later read fails.
        if args.select:
            lines = select(numbers, ready_issue, gh_json).lines
        else:
            lines = [line for issue in numbers for line in issue_lines(issue)]
    except (ReadError, SelectionError) as error:
        print(f"read_ready: {error}", file=sys.stderr)
        return 1
    except (AttributeError, KeyError, TypeError):
        print("read_ready: unexpected GitHub API response shape", file=sys.stderr)
        return 1
    print(f"{json.dumps(title, ensure_ascii=False)} ({url}) — Ready issues for {REPOSITORY}")
    print("\n".join(lines) if lines else "No Ready issues for this repository.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
