#!/usr/bin/env python3
"""Backfill native GitHub Issue Type and Priority/Workstream issue fields.

Run only from trusted default-branch GitHub Actions. Uses the preconfigured
PROJECTS_TOKEN; never loads code or metadata from PR branches. Standard library.
"""
import json
import os
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

VERSION = "2026-03-10"
VALID_TYPES = {"Feature", "Bug", "Task", "Spike", "Design Decision"}
VALID_PRIORITIES = {"Urgent", "High", "Medium", "Low"}
# Existing issue titles without a literal type are classified explicitly.
TYPE_OVERRIDES = {
    1: "Design Decision", 2: "Task", 3: "Spike", 4: "Spike",
    5: "Task", 6: "Design Decision", 7: "Design Decision",
    11: "Task", 13: "Task", 14: "Task", 15: "Task",
    16: "Design Decision", 17: "Design Decision", 64: "Task",
}
# These are explicitly approved corrections even if Type is currently Spike.
FORCE_TYPE_CORRECTIONS = {13, 14, 15}
TYPE_PREFIX = {
    "Design Decision": "Design Decision",
    "Design": "Design Decision",
    "Feature": "Feature",
    "Bug": "Bug",
    "Task": "Task",
    "Spike": "Spike",
    "Prototype": "Task",
    "Infrastructure": "Task",
    "Architecture": "Spike",
}
# Use an existing exact workstream option whenever possible. Where the user's
# field only has broad original options, choose a genuinely related category.
WORKSTREAM_CANDIDATES = {
    "Design": ("Design",),
    "Architecture": ("Architecture",),
    "Infrastructure": ("Infrastructure",),
    "Simulation": ("Simulation",),
    "QA": ("QA",),
    "Design/Simulation": ("Design", "Simulation"),
    "Architecture / Design": ("Architecture", "Design"),
    "Simulation / Infrastructure": ("Infrastructure", "Simulation"),
    "Presentation / UI": ("Presentation", "UI", "Design"),
    "UI": ("UI", "Presentation", "Design"),
    "Content": ("Content", "Design"),
    "Persistence": ("Persistence", "Infrastructure"),
    "Simulation / Presentation": ("Simulation", "Presentation"),
    "QA / Architecture": ("QA", "Architecture"),
    "Design / QA": ("QA", "Design"),
    "Release / Infrastructure": ("Release", "Infrastructure"),
    "Release": ("Release", "Infrastructure"),
    "QA / UX": ("QA", "Design"),
    "Infrastructure / Planning": ("Infrastructure",),
}


class MetadataError(Exception):
    pass


def parse_issue_metadata(number, title, body):
    """Existing issue body serves only as a one-time migration input."""
    title = title or ""
    body = body or ""
    match = re.match(r"^\[([^\]]+)\]", title)
    category = match.group(1) if match else ""
    typ = TYPE_OVERRIDES.get(number) or TYPE_PREFIX.get(category)
    if typ not in VALID_TYPES:
        typ = None

    priorities = re.findall(
        r"\*\*Priority:\*\*\s*(Urgent|High|Medium|Low|P0|P1|P2)\b", body, re.I
    )
    priority = priorities[-1].title() if priorities else None
    if priority and priority.startswith("P"):
        priority = {"P0": "High", "P1": "High", "P2": "Medium"}[priority.upper()]
    if priority not in VALID_PRIORITIES:
        priority = None

    workstreams = re.findall(r"\*\*Workstream:\*\*\s*([^;\n·|]+)", body)
    raw = workstreams[-1].strip().rstrip("* ").strip() if workstreams else ""
    # Strip accidental inline markdown punctuation but preserve slash categories.
    candidates = WORKSTREAM_CANDIDATES.get(raw, (raw,)) if raw else ()
    return {"type": typ, "priority": priority, "workstream": candidates}


def select_option(field, candidates):
    options = field.get("options") or []
    for candidate in candidates:
        for option in options:
            if option["name"].casefold() == candidate.casefold():
                return option["name"]
    return None


def current_type(issue):
    value = issue.get("type")
    return (value.get("name") if isinstance(value, dict) else value) or None


def plan_changes(issue, existing_values, fields, available_types, replace=False):
    number = int(issue["number"])
    target = parse_issue_metadata(number, issue.get("title"), issue.get("body"))
    existing_by_name = {
        item.get("issue_field_name", "").casefold(): item
        for item in existing_values
    }
    change_type = None
    requested_type = target["type"]
    if requested_type and requested_type not in available_types:
        print(f"#{number}: Type {requested_type!r} not enabled; skipped")
    elif requested_type:
        actual = current_type(issue)
        if actual != requested_type and (
            actual is None or replace or number in FORCE_TYPE_CORRECTIONS
        ):
            change_type = requested_type
        elif actual != requested_type:
            print(f"#{number}: preserving existing Type {actual!r}")

    changes = []
    for name, targets in [
        ("Priority", (target["priority"],) if target["priority"] else ()),
        ("Workstream", target["workstream"]),
    ]:
        if not targets:
            print(f"#{number}: no source value for {name}; skipped")
            continue
        field = fields.get(name.casefold())
        if field is None:
            print(f"#{number}: missing GitHub issue field {name!r}; skipped")
            continue
        if field.get("data_type") != "single_select":
            print(f"#{number}: {name} is not a single-select field; skipped")
            continue
        selected = select_option(field, targets)
        if not selected:
            print(
                f"#{number}: no {name} option for {targets!r}; "
                f"available: {[o['name'] for o in field.get('options', [])]}"
            )
            continue
        current = existing_by_name.get(name.casefold())
        current_name = (current.get("single_select_option") or {}).get("name") if current else None
        if current_name == selected:
            continue
        if current_name and not replace:
            print(f"#{number}: preserving existing {name} {current_name!r}")
            continue
        changes.append({"field_id": field["id"], "value": selected})
    return change_type, changes


class GitHub:
    def __init__(self, token):
        if not token:
            raise MetadataError("PROJECTS_TOKEN is missing. Set the Actions secret.")
        self.token = token

    def request(self, path, method="GET", payload=None):
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = Request(
            "https://api.github.com" + path,
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": VERSION,
                "Content-Type": "application/json",
                "User-Agent": "the-producer-issue-metadata-backfill",
            },
        )
        try:
            with urlopen(req, timeout=30) as resp:
                return json.load(resp) if resp.status != 204 else None
        except HTTPError as err:
            raise MetadataError(f"GitHub API HTTP {err.code} ({method} {path})") from err
        except (URLError, OSError) as err:
            raise MetadataError(f"GitHub API {method} {path}: {type(err).__name__}") from err

    def issues(self, owner, repo):
        page = 1
        while True:
            batch = self.request(
                f"/repos/{owner}/{repo}/issues?state=all&per_page=100&page={page}"
            )
            for issue in batch:
                if "pull_request" not in issue:
                    yield issue
            if len(batch) < 100:
                break
            page += 1


def parse_numbers(value):
    if not (value or "").strip():
        return None
    numbers = set()
    for item in value.split(","):
        item = item.strip()
        if not item.isdigit() or int(item) < 1:
            raise MetadataError("Issue numbers must be positive integers separated by commas")
        numbers.add(int(item))
    return numbers


def run(api, owner, repo, *, numbers=None, dry_run=True, replace=False):
    # Native account-level issue types and issue fields (not labels).
    issue_types = api.request(f"/repos/{owner}/{repo}/issue-types")
    type_names = {t["name"] for t in issue_types}
    try:
        fields_raw = api.request("/user/issue-fields")
    except MetadataError as error:
        raise MetadataError(
            f"{error}. GitHub classic PATs require the read:user scope "
            "to discover Priority and Workstream issue fields. "
            "Add it to the PAT, update PROJECTS_TOKEN in Actions Secrets, retry."
        ) from error
    fields = {f["name"].casefold(): f for f in fields_raw}
    print(f"Available native issue types: {sorted(type_names)}")
    for name in ("Priority", "Workstream"):
        f = fields.get(name.casefold())
        print(f"{name}: {[o['name'] for o in f.get('options', [])] if f else 'NOT FOUND'}")

    changed = missing = reviewed = 0
    for issue in api.issues(owner, repo):
        num = issue["number"]
        if numbers is not None and num not in numbers:
            continue
        reviewed += 1
        path = f"/repos/{owner}/{repo}/issues/{num}"
        existing = api.request(path + "/issue-field-values")
        new_type, field_changes = plan_changes(issue, existing, fields, type_names, replace)
        if not new_type and not field_changes:
            print(f"#{num}: already set, preserved, or no matching fields")
            continue
        print(f"#{num}: {'DRY RUN' if dry_run else 'APPLY'} Type={new_type} Fields={field_changes}")
        if dry_run:
            continue
        if new_type:
            api.request(path, method="PATCH", payload={"type": new_type})
            verified = api.request(path)
            if current_type(verified) != new_type:
                raise MetadataError(
                    f"#{num}: Type update not verified; expected {new_type!r}"
                )
        if field_changes:
            # POST adds/updates listed fields without wiping unrelated metadata.
            api.request(
                path + "/issue-field-values",
                method="POST",
                payload={"issue_field_values": field_changes},
            )
            latest = api.request(path + "/issue-field-values")
            now = {x.get("issue_field_id"): (x.get("single_select_option") or {}).get("name")
                   for x in latest}
            for field in field_changes:
                if now.get(field["field_id"]) != field["value"]:
                    raise MetadataError(f"#{num}: {field} not verified after update")
        changed += 1
    print(f"Scanned {reviewed} issues; {changed} changed; dry_run={dry_run}")
    return changed


def main():
    repo_slug = os.environ.get("GITHUB_REPOSITORY", "")
    if "/" not in repo_slug:
        raise MetadataError("Missing GITHUB_REPOSITORY")
    owner, repo = repo_slug.split("/", 1)
    numbers = parse_numbers(os.environ.get("ISSUE_NUMBERS", ""))
    dry_run = os.environ.get("DRY_RUN", "true").lower() != "false"
    replace = os.environ.get("REPLACE_EXISTING", "false").lower() == "true"
    if replace and numbers is None:
        raise MetadataError("replace_existing requires explicit issue_numbers to avoid bulk overwrites")
    run(
        GitHub(os.environ.get("PROJECTS_TOKEN")),
        owner,
        repo,
        numbers=numbers,
        dry_run=dry_run,
        replace=replace,
    )


if __name__ == "__main__":
    try:
        main()
    except MetadataError as error:
        print(f"Metadata migration failed: {error}", file=sys.stderr)
        sys.exit(1)
