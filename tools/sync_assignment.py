"""Owner-command reconciliation of one assignment's native issue metadata."""
import json
import re

if __package__:
    from .ready_selection import (
        APPROVAL_FIELD, ISSUE_PRS, exclusion, native_options, valid_name,
    )
    from .sync_issue_metadata import MetadataError, VALID_PRIORITIES, VALID_TYPES, current_type
else:
    from ready_selection import (
        APPROVAL_FIELD, ISSUE_PRS, exclusion, native_options, valid_name,
    )
    from sync_issue_metadata import MetadataError, VALID_PRIORITIES, VALID_TYPES, current_type


COMMAND = "/assignment sync"
REPLACE_COMMAND = COMMAND + " --replace"
FENCE = "```assignment-v1"
KEYS = {"type", "priority", "workstreams", "requires_human_approval", "prerequisites"}
EDITABLE = (None, "Backlog", "Blocked", "Ready")


class ProtectedAssignment(MetadataError):
    """A closed, claimed, or superseded assignment must be left alone."""


def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise MetadataError("Duplicate assignment declaration key")
        obj[key] = value
    return obj


def declaration(body):
    lines = (body or "").splitlines()
    first_lines = [i for i, line in enumerate(lines) if line.strip()]
    begins = [i for i, line in enumerate(lines)
              if re.match(r"^\s*(?:`{3,}|~{3,})\s*assignment\b", line, re.I)]
    if len(first_lines) < 2 or begins != first_lines[1:2] or lines[begins[0]] != FENCE:
        raise MetadataError("Expected one standalone assignment-v1 fence immediately after the selection marker")
    start = begins[0] + 1
    try:
        end = lines.index("```", start)
        data = json.loads("\n".join(lines[start:end]), object_pairs_hook=unique_object)
    except ValueError as error:
        raise MetadataError("Invalid assignment-v1 JSON or closing fence") from error
    if not isinstance(data, dict) or data.keys() != KEYS:
        raise MetadataError("Assignment declaration must contain exactly the five documented keys")
    for key, values in (("type", VALID_TYPES), ("priority", VALID_PRIORITIES)):
        if not isinstance(data[key], str) or data[key] not in values:
            raise MetadataError(f"Unknown assignment {key}")
    workstreams = data["workstreams"]
    if (not isinstance(workstreams, list) or not workstreams
            or not all(valid_name(name) for name in workstreams)
            or len({name.casefold() for name in workstreams}) != len(workstreams)):
        raise MetadataError("Workstreams must be a nonempty list of distinct option names")
    if type(data["requires_human_approval"]) is not bool:
        raise MetadataError("requires_human_approval must be a JSON boolean")
    prerequisites = data["prerequisites"]
    if (not isinstance(prerequisites, list)
            or not all(type(number) is int and 0 < number < 2**31 for number in prerequisites)
            or len(set(prerequisites)) != len(prerequisites)):
        raise MetadataError("Prerequisites must be a list of distinct positive local issue numbers")
    marker = "native" if prerequisites else "none"
    if lines[first_lines[0]] != f"Selection-ready implementation; prerequisites: {marker}":
        raise MetadataError("Selection marker disagrees with the declared prerequisites")
    if not any(line.strip() for line in lines[end + 1:]):
        raise MetadataError("Issue scope must follow the assignment declaration")
    return data


def resolve_fields(api, data):
    definitions = api.request("/user/issue-fields")
    targets = {
        "Priority": [data["priority"]],
        "Workstream": data["workstreams"],
        APPROVAL_FIELD: ["Yes" if data["requires_human_approval"] else "No"],
    }
    result = {}
    for name, values in targets.items():
        matches = [row for row in definitions if row["name"].casefold() == name.casefold()]
        if len(matches) != 1 or matches[0]["name"] != name:
            raise MetadataError(f"Expected one native field named {name}")
        field = matches[0]
        kind = field["data_type"]
        if kind == "multi_select" and name == "Workstream":
            value = values
        elif kind == "single_select" and len(values) == 1:
            value = values[0]
        else:
            raise MetadataError(f"Native field {name} cannot store the declared selection")
        option_names = [option["name"] for option in field["options"]]
        if any([name for name in option_names if name.casefold() == option.casefold()] != [option]
               for option in values):
            raise MetadataError(f"Unknown or ambiguous native option for {name}")
        field_id = field["id"]
        if type(field_id) is not int or field_id <= 0 or any(
            field_id == write["field_id"] for _, _, write in result.values()
        ):
            raise MetadataError(f"Invalid or ambiguous native field ID for {name}")
        result[name] = (kind, set(values), {"field_id": field_id, "value": value})
    return result


def field_changes(current, targets, replace):
    changes = []
    for name, (kind, wanted, write) in targets.items():
        rows = [row for row in current if row["issue_field_id"] == write["field_id"]
                or row["issue_field_name"].casefold() == name.casefold()]
        if rows and (len(rows) != 1 or rows[0]["issue_field_name"] != name
                     or rows[0]["issue_field_id"] != write["field_id"]
                     or rows[0]["data_type"] != kind):
            raise MetadataError(f"Ambiguous native field value for {name}")
        actual = native_options(current, name, allow_multiple=kind == "multi_select")
        if actual is None:
            raise MetadataError(f"Cannot verify native field value for {name}")
        if set(actual) != wanted:
            if actual and not replace:
                raise MetadataError(f"Conflicting native {name}; owner replacement required")
            changes.append(write)
    return changes


def blockers(api, path, issue):
    rows = api.list_all(f"{path}/{issue['number']}/dependencies/blocked_by")
    by_id = {row["id"]: row for row in rows}
    count = issue["issue_dependencies_summary"]["total_blocked_by"]
    if (type(count) is not int or count != len(rows) or len(rows) != len(by_id)
            or any(type(issue_id) is not int or issue_id <= 0 for issue_id in by_id)):
        raise MetadataError(f"#{issue['number']}: native prerequisite list is incomplete or ambiguous")
    return by_id


def local_issue(api, path, number):
    issue = api.request(f"{path}/{number}")
    issue_id = issue["id"]
    if ("pull_request" in issue or type(issue["number"]) is not int or issue["number"] != number
            or issue["url"] != f"https://api.github.com{path}/{number}"
            or type(issue_id) is not int or issue_id <= 0):
        raise MetadataError(f"#{number}: expected a local issue")
    return issue


def check_cycles(api, path, target_id, roots):
    # An iterative DFS keeps a shared prerequisite from being mistaken for a cycle.
    visiting = {target_id}
    verified_numbers = {}
    stack = [(target_id, iter(roots))]
    while stack:
        parent, children = stack[-1]
        child = next(children, None)
        if child is None:
            stack.pop()
            visiting.remove(parent)
            continue
        issue_id = child["id"]
        if issue_id in visiting:
            raise MetadataError("Self or cyclic native prerequisite")
        number = child["number"]
        if type(number) is not int or not 0 < number < 2**31:
            raise MetadataError("Invalid native prerequisite number")
        if child["url"] != f"https://api.github.com{path}/{number}":
            raise MetadataError("Cannot verify an external prerequisite chain")
        if issue_id in verified_numbers:
            if verified_numbers[issue_id] != number:
                raise MetadataError("Native prerequisite identity changed")
            continue
        current = local_issue(api, path, number)
        if current["id"] != issue_id:
            raise MetadataError("Native prerequisite identity changed")
        verified_numbers[issue_id] = number
        visiting.add(issue_id)
        stack.append((issue_id, iter(blockers(api, path, current).values())))


def synchronize(api, project, number, body, *, replace=False):
    """Apply a pinned declaration; resolve every conflict before writing metadata."""
    path = f"/repos/{project.owner}/{project.repo}/issues"
    issue_path = f"{path}/{number}"
    fields_path = issue_path + "/issue-field-values"
    dependencies_path = issue_path + "/dependencies/blocked_by"
    variables = {"owner": project.owner, "repo": project.repo, "number": number}

    def check_editable():
        _, status, _ = project.find_item(number)
        if status not in EDITABLE:
            raise ProtectedAssignment(f"#{number}: assignment cannot be synchronized in {status}")
        issue = local_issue(api, path, number)
        if issue["state"] != "open":
            raise ProtectedAssignment(f"#{number}: assignment is no longer open")
        project_issue = project.api.graphql(ISSUE_PRS, variables)["repository"]["issue"]
        refs = project_issue["closedByPullRequestsReferences"]["nodes"]
        if not isinstance(refs, list):
            raise MetadataError(f"#{number}: linked PR state unavailable")
        if refs:
            raise ProtectedAssignment(f"#{number}: open linked PR")
        return issue, status

    try:
        issue, _ = check_editable()
        if issue["body"] != body:
            raise ProtectedAssignment(f"#{number}: issue body changed; review it and post a fresh command")
        data = declaration(body)
        if number in data["prerequisites"]:
            raise MetadataError("Self or cyclic native prerequisite")
        requested_type = data["type"]
        issue_types = api.request(f"/repos/{project.owner}/{project.repo}/issue-types")
        types = [row for row in issue_types if row["name"] == requested_type]
        if len(types) != 1 or types[0]["is_enabled"] is not True:
            raise MetadataError("Declared native issue Type is not enabled")
        if "type" not in issue:
            raise MetadataError("Native issue Type is unavailable")
        actual_type = current_type(issue)
        type_change = actual_type != requested_type
        if type_change and actual_type is not None and not replace:
            raise MetadataError("Conflicting native Type; owner replacement required")
        fields = resolve_fields(api, data)
        changes = field_changes(api.list_all(fields_path), fields, replace)
        existing = blockers(api, path, issue)
        wanted = {}
        for dependency in data["prerequisites"]:
            row = local_issue(api, path, dependency)
            wanted[row["id"]] = row
        if len(wanted) != len(data["prerequisites"]):
            raise MetadataError("Ambiguous native prerequisite identity")
        extra = existing.keys() - wanted.keys()
        missing = wanted.keys() - existing.keys()
        if extra and not replace:
            raise MetadataError("Conflicting native prerequisites; owner replacement required")
        check_cycles(api, path, issue["id"], wanted.values())

        if type_change or changes or extra or missing:
            current, status = check_editable()
            if (current["updated_at"] != issue["updated_at"] or current["body"] != body
                    or current_type(current) != actual_type
                    or blockers(api, path, current).keys() != existing.keys()):
                raise MetadataError(f"#{number}: issue changed during preflight")
            if status == "Ready":
                project.update(number, "Blocked", only_from=("Ready",))
            pending_fields = field_changes(api.list_all(fields_path), fields, replace)
            if pending_fields != changes:
                raise MetadataError(f"#{number}: native field values changed during preflight")
            if type_change:
                api.request(issue_path, method="PATCH", payload={"type": requested_type})
            if changes:
                api.request(fields_path, method="POST", payload={"issue_field_values": changes})
            for issue_id in sorted(missing):
                api.request(dependencies_path, method="POST", payload={"issue_id": issue_id})
            for issue_id in sorted(extra):
                api.request(f"{dependencies_path}/{issue_id}", method="DELETE")

        current, _ = check_editable()
        actual_fields = api.list_all(fields_path)
        actual = blockers(api, path, current)
        if (current["body"] != body or current["id"] != issue["id"]
                or current_type(current) != requested_type
                or field_changes(actual_fields, fields, replace=True) or actual.keys() != wanted.keys()):
            raise MetadataError(f"#{number}: native assignment read-back did not match")
        for issue_id, row in actual.items():
            if (row["url"], row["number"]) != (wanted[issue_id]["url"], wanted[issue_id]["number"]):
                raise MetadataError(f"#{number}: native prerequisite identity did not match")
        print(f"#{number}: native Type, Priority, Workstream, approval field and prerequisites verified")
        reason = exclusion(current, actual_fields, list(actual.values()))
        if reason:
            raise MetadataError(f"#{number}: native metadata verified; not Ready: {reason}")
        # Ready publishes approved scope and valid links. Dispatch checks accepted completion.
        check_cycles(api, path, current["id"], actual.values())
        latest, latest_status = check_editable()
        if latest["body"] != body or latest["updated_at"] != current["updated_at"]:
            raise MetadataError(f"#{number}: issue changed before Ready")
        project.update(number, "Ready", only_from=(latest_status,))
    except ProtectedAssignment:
        raise
    except Exception:
        # A timed-out status write may have landed. Read the card and withdraw
        # Ready when possible, but never overwrite a claim or review in recovery.
        try:
            _, status, _ = project.find_item(number)
            if status == "Ready":
                project.update(number, "Blocked", only_from=("Ready",))
        except Exception:
            print(f"#{number}: could not verify withdrawal of Ready; stop dispatch and inspect the card")
        raise
