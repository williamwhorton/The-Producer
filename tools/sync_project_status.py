#!/usr/bin/env python3
"""Sync issue lifecycle and explicit commands to a GitHub Projects v2 Status field.

Standard-library only. Designed for a trusted GitHub Actions workflow using
the repository's default-branch script. Never execute PR-provided code.
"""
import json
import os
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

STATUSES = ("Backlog", "Ready", "In Progress", "In Review", "Blocked", "Done")
COMMAND_RE = re.compile(r"^/status\s+(Backlog|Ready|In Progress|In Review|Blocked|Done)\s*$", re.I)
CLOSING_RE = re.compile(
    r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+"
    r"(?:(?P<owner>[\w.-]+)/(?P<repo>[\w.-]+))?#(?P<number>\d+)\b", re.I
)


class SyncError(Exception):
    pass


def normalize_status(value):
    for status in STATUSES:
        if status.casefold() == value.strip().casefold():
            return status
    raise SyncError(f"Unknown Status: {value!r}; expected one of {STATUSES}")


def comment_status(body):
    match = COMMAND_RE.fullmatch(body.strip())
    return normalize_status(match.group(1)) if match else None


def closing_issues(body, owner, repo):
    result = set()
    for match in CLOSING_RE.finditer(body or ""):
        if match.group("owner") and (
            match.group("owner").casefold(), match.group("repo").casefold()
        ) != (owner.casefold(), repo.casefold()):
            continue
        result.add(int(match.group("number")))
    return sorted(result)


def parse_bootstrap(value):
    """One-time reconciliation overrides, e.g. '4=In Progress,5=Blocked'."""
    result = {}
    if not value.strip():
        return result
    for pair in value.split(","):
        if "=" not in pair:
            raise SyncError("Bootstrap requires ISSUE=STATUS pairs")
        number, status = pair.split("=", 1)
        if not number.strip().isdigit() or int(number.strip()) <= 0:
            raise SyncError(f"Invalid issue number: {number!r}")
        result[int(number.strip())] = normalize_status(status)
    return result


def decide_event(event_name, payload, owner, repo):
    """Resolve requested status transitions without network calls."""
    action = payload.get("action")
    if event_name == "issues":
        issue = payload.get("issue", {})
        if "pull_request" in issue or not issue.get("number"):
            return {}
        mapping = {"opened": "Backlog", "closed": "Done", "reopened": "Backlog"}
        return {int(issue["number"]): mapping[action]} if action in mapping else {}

    if event_name == "issue_comment" and action == "created":
        issue = payload.get("issue", {})
        if "pull_request" in issue or not issue.get("number"):
            return {}
        author = payload.get("comment", {}).get("user", {}).get("login", "")
        if author.casefold() != owner.casefold():
            print(f"Ignoring status comment by non-owner {author!r}")
            return {}
        status = comment_status(payload.get("comment", {}).get("body", ""))
        if not status:
            return {}
        if status == "Done" and issue.get("state") != "closed":
            raise SyncError("Cannot mark an open issue Done: close it after acceptance")
        return {int(issue["number"]): status}

    if event_name == "pull_request_target":
        pr = payload.get("pull_request", {})
        head = pr.get("head", {}).get("repo") or {}
        if head.get("full_name", "").casefold() != f"{owner}/{repo}".casefold():
            print("Ignoring PR from outside this repository")
            return {}
        if pr.get("base", {}).get("ref") != "main":
            return {}
        numbers = closing_issues(pr.get("body") or "", owner, repo)
        if action in ("opened", "reopened", "ready_for_review"):
            status = "In Progress" if pr.get("draft") else "In Review"
        elif action == "converted_to_draft":
            status = "In Progress"
        elif action == "closed" and not pr.get("merged"):
            status = "In Progress"
        else:
            # Merging a PR with closing references triggers issue closed events.
            return {}
        return {number: status for number in numbers}
    return {}


def superseded(event_name, payload, comments, owner):
    """An older PR or comment job must not undo a later owner command."""
    commands = [
        c for c in comments
        if (c.get("user") or {}).get("login", "").casefold() == owner.casefold()
        and comment_status(c.get("body") or "")
    ]
    if not commands:
        return False
    latest = max(commands, key=lambda c: (c["created_at"], c["id"]))
    if event_name == "issue_comment":
        posted = payload["comment"]
        return latest["id"] != posted["id"] or latest["body"] != posted["body"]
    if event_name == "pull_request_target":
        pr = payload["pull_request"]
        timestamp = pr["created_at"] if payload["action"] == "opened" else pr["updated_at"]
        return latest["created_at"] > timestamp or (
            latest["created_at"] == timestamp and comment_status(latest["body"]) == "Blocked")
    return False


class GitHub:
    def __init__(self, token):
        if not token:
            raise SyncError("Missing PROJECTS_TOKEN repository Actions secret")
        self.token = token

    def request(self, path, payload=None):
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = Request(
            "https://api.github.com" + path, data=data,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "Content-Type": "application/json",
                "User-Agent": "the-producer-project-status-sync",
            },
            method="POST" if data is not None else "GET",
        )
        try:
            with urlopen(request, timeout=30) as response:
                return json.load(response)
        except HTTPError as error:
            # Never print request headers or the token.
            raise SyncError(f"GitHub API HTTP {error.code} at {path}") from error
        except (OSError, URLError) as error:
            raise SyncError(f"GitHub API failed at {path}: {type(error).__name__}") from error

    def graphql(self, query, variables):
        result = self.request("/graphql", {"query": query, "variables": variables})
        if result.get("errors"):
            details = "; ".join(e.get("message", "GraphQL error") for e in result["errors"])
            raise SyncError(f"GitHub Projects API error: {details}")
        return result["data"]

    def issues(self, owner, repo):
        page = 1
        while True:
            batch = self.request(f"/repos/{owner}/{repo}/issues?state=all&per_page=100&page={page}")
            for issue in batch:
                if "pull_request" not in issue:
                    yield issue
            if len(batch) < 100:
                break
            page += 1

    def issue(self, owner, repo, number):
        issue = self.request(f"/repos/{owner}/{repo}/issues/{number}")
        if "pull_request" in issue:
            raise SyncError(f"#{number} is a PR, not an issue")
        return issue

    def issue_comments(self, owner, repo, number):
        page = 1
        while True:
            batch = self.request(
                f"/repos/{owner}/{repo}/issues/{number}/comments?per_page=100&page={page}")
            yield from batch
            if len(batch) < 100:
                return
            page += 1


PROJECT_QUERY = """
query ($owner: String!, $number: Int!) {
  user(login: $owner) {
    projectV2(number: $number) {
      id title
      field(name: "Status") {
        ... on ProjectV2SingleSelectField { id options { id name } }
      }
    }
  }
}
"""
ISSUE_QUERY = """
query ($owner: String!, $repo: String!, $number: Int!) {
  repository(owner: $owner, name: $repo) {
    issue(number: $number) {
      id
      projectItems(first: 100) {
        nodes {
          id
          project { id }
          fieldValues(first: 30) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                name field { ... on ProjectV2SingleSelectField { id } }
              }
            }
          }
        }
      }
    }
  }
}
"""
ADD_QUERY = """
mutation ($project: ID!, $issue: ID!) {
  addProjectV2ItemById(input: {projectId: $project, contentId: $issue}) { item { id } }
}
"""
UPDATE_QUERY = """
mutation ($project: ID!, $item: ID!, $field: ID!, $option: String!) {
  updateProjectV2ItemFieldValue(input: {
    projectId: $project, itemId: $item, fieldId: $field,
    value: { singleSelectOptionId: $option }
  }) { projectV2Item { id } }
}
"""


class Project:
    def __init__(self, api, owner, repo, number):
        self.api, self.owner, self.repo = api, owner, repo
        data = api.graphql(PROJECT_QUERY, {"owner": owner, "number": number}).get("user")
        project = data.get("projectV2") if data else None
        if not project:
            raise SyncError(f"Project #{number} not found for user {owner!r}, or token lacks access")
        status = project.get("field")
        if not status or not status.get("id"):
            raise SyncError(f"Project {project['title']!r} has no Status single-select field")
        self.id, self.title, self.field = project["id"], project["title"], status["id"]
        self.options = {option["name"]: option["id"] for option in status["options"]}
        missing = set(STATUSES) - set(self.options)
        if missing:
            raise SyncError(f"Project Status is missing options: {', '.join(sorted(missing))}")

    def find_item(self, number):
        data = self.api.graphql(
            ISSUE_QUERY, {"owner": self.owner, "repo": self.repo, "number": number}
        )
        issue = data.get("repository", {}).get("issue")
        if not issue:
            raise SyncError(f"Issue #{number} not found")
        for item in issue["projectItems"]["nodes"]:
            if item.get("project", {}).get("id") != self.id:
                continue
            for field in item.get("fieldValues", {}).get("nodes", []):
                if field and field.get("field", {}) and field["field"].get("id") == self.field:
                    return item["id"], field["name"], issue["id"]
            return item["id"], None, issue["id"]
        return None, None, issue["id"]

    def update(self, number, status, *, preserve_open=False):
        status = normalize_status(status)
        item, current, issue = self.find_item(number)
        if preserve_open and current and current != "Done":
            print(f"#{number}: keep existing {current}")
            return
        if current == status:
            print(f"#{number}: already {status}")
            return
        if not item:
            item = self.api.graphql(
                ADD_QUERY, {"project": self.id, "issue": issue}
            )["addProjectV2ItemById"]["item"]["id"]
        self.api.graphql(
            UPDATE_QUERY, {
                "project": self.id, "item": item,
                "field": self.field, "option": self.options[status],
            }
        )
        print(f"#{number}: {current or '(none)'} -> {status}")


def main():
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    if "/" not in repository:
        raise SyncError("GITHUB_REPOSITORY must be owner/repository")
    owner, repo = repository.split("/", 1)
    number = os.environ.get("PROJECT_NUMBER", "")
    if not number.isdigit() or int(number) <= 0:
        raise SyncError("Set PROJECT_NUMBER in repository Actions variables")
    api = GitHub(os.environ.get("PROJECTS_TOKEN", ""))
    project = Project(api, owner, repo, int(number))
    print(f"Syncing GitHub Project {project.title!r} (#{number})")

    if os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch":
        bootstrap = parse_bootstrap(os.environ.get("BOOTSTRAP_STATUSES", ""))
        for issue in api.issues(owner, repo):
            n = issue["number"]
            if issue["state"] == "closed":
                if bootstrap.get(n) and bootstrap[n] != "Done":
                    raise SyncError(f"Cannot override closed issue #{n} with open status")
                project.update(n, "Done")
            elif n in bootstrap:
                if bootstrap[n] == "Done":
                    raise SyncError(f"Cannot mark open issue #{n} Done; close it first")
                project.update(n, bootstrap[n])
            else:
                # Do not clobber an active work status during routine reconciliation.
                project.update(n, "Backlog", preserve_open=True)
        return 0

    path = os.environ.get("GITHUB_EVENT_PATH", "")
    if not path:
        raise SyncError("Missing GITHUB_EVENT_PATH")
    with open(path, encoding="utf-8") as file:
        event = json.load(file)
    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    updates = decide_event(event_name, event, owner, repo)
    for number, status in updates.items():
        issue = api.issue(owner, repo, number)
        if status == "Done" and issue["state"] != "closed":
            raise SyncError(f"Cannot mark open issue #{number} Done")
        if status != "Done" and issue["state"] == "closed":
            project.update(number, "Done")
        elif event_name in ("issue_comment", "pull_request_target") and superseded(
                event_name, event, api.issue_comments(owner, repo, number), owner):
            print(f"#{number}: skip stale status event; newer owner command exists")
        else:
            project.update(number, status)
    if not updates:
        print("No project status updates required")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SyncError as error:
        print(f"Project sync failed: {error}", file=sys.stderr)
        sys.exit(1)
