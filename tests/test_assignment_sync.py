"""Offline integration tests of the owner command and GitHub write/read-back flow."""
from copy import deepcopy
import json
import unittest
from unittest.mock import Mock, mock_open, patch

from tools import sync_assignment as assignment
from tools import sync_project_status as status
from tools.sync_issue_metadata import GitHub, MetadataError


OWNER = "williamwhorton"
REPO = "The-Producer"
PATH = f"/repos/{OWNER}/{REPO}/issues"
TARGET = f"{PATH}/35"
DEPENDENCIES = TARGET + "/dependencies/blocked_by"
FIELDS = TARGET + "/issue-field-values"


def body(**changes):
    data = {
        "type": "Feature",
        "priority": "High",
        "workstreams": ["Simulation", "QA"],
        "requires_human_approval": False,
        "prerequisites": [16, 34],
        **changes,
    }
    marker = "native" if data["prerequisites"] else "none"
    return (f"Selection-ready implementation; prerequisites: {marker}\n\n"
            f"```assignment-v1\n{json.dumps(data)}\n```\n\nApproved scope.")


def issue(number, *, state="closed"):
    return {
        "id": 1000 + number,
        "number": number,
        "url": f"https://api.github.com{PATH}/{number}",
        "html_url": f"https://github.com/{OWNER}/{REPO}/issues/{number}",
        "state": state,
        "state_reason": "completed" if state == "closed" else None,
        "updated_at": "2026-11-26T00:00:00Z",
        "issue_dependencies_summary": {"total_blocked_by": 0},
    }


def field(field_id, name, values, kind="single_select"):
    return {"id": field_id, "name": name, "data_type": kind,
            "options": [{"name": value} for value in values]}


class FakeGitHub:
    def __init__(self):
        self.issue = {**issue(35, state="open"), "type": None, "body": body(),
                      "labels": [{"name": "agent:developer"}], "assignees": []}
        self.issues = {35: self.issue, 16: issue(16), 34: issue(34), 99: issue(99)}
        self.definitions = {
            1: field(1, "Priority", ["High", "Low"]),
            2: field(2, "Workstream", ["Simulation", "QA"], "multi_select"),
            3: field(3, assignment.APPROVAL_FIELD, ["Yes", "No"]),
        }
        self.values = {9: {"issue_field_id": 9, "issue_field_name": "Notes",
                           "data_type": "text", "value": "preserve"}}
        self.links = {number: set() for number in self.issues}
        self.current_status = "Backlog"
        self.writes = []
        self.linked_prs = []
        self.reject_once = None
        self.drop_dependency = None
        self.lose_ready_response = False

    def list_all(self, path):
        if path == FIELDS:
            return deepcopy(list(self.values.values()))
        if path.endswith("/dependencies/blocked_by"):
            number = int(path.split("/")[-3])
            return deepcopy([self.issues[n] for n in sorted(self.links[number])])
        raise AssertionError(path)

    def request(self, path, method="GET", payload=None):
        if method == "GET":
            if path == "/user/issue-fields":
                return deepcopy(list(self.definitions.values()))
            if path.endswith("/issue-types"):
                return [{"name": "Feature", "is_enabled": True}]
            if path.startswith(PATH + "/"):
                number = int(path.rsplit("/", 1)[1])
                if number in self.issues:
                    result = deepcopy(self.issues[number])
                    result["issue_dependencies_summary"]["total_blocked_by"] = len(self.links[number])
                    return result
                raise MetadataError("HTTP 404")
        else:
            self.writes.append((method, path, payload))
            if self.reject_once == path:
                self.reject_once = None
                raise MetadataError("HTTP 503")
            if (method, path) == ("PATCH", TARGET):
                self.issue["type"] = {"name": payload["type"]}
                return
            if (method, path) == ("POST", FIELDS):
                for change in payload["issue_field_values"]:
                    field_id, value = change["field_id"], change["value"]
                    definition = self.definitions[field_id]
                    options = ({"multi_select_options": [{"name": name} for name in value]}
                               if isinstance(value, list) else {"single_select_option": {"name": value}})
                    self.values[field_id] = {
                        "issue_field_id": field_id, "issue_field_name": definition["name"],
                        "data_type": definition["data_type"], **options,
                    }
                return
            if (method, path) == ("POST", DEPENDENCIES):
                number = payload["issue_id"] - 1000
                if number != self.drop_dependency:
                    self.links[35].add(number)
                return
            if method == "DELETE" and path.startswith(DEPENDENCIES):
                self.links[35].remove(int(path.rsplit("/", 1)[1]) - 1000)
                return
        raise AssertionError((method, path))

    def graphql(self, query, variables):
        if query == status.PROJECT_QUERY:
            return {"user": {"projectV2": {
                "id": "P", "title": "Producer",
                "field": {"id": "S", "options": [{"id": name, "name": name} for name in status.STATUSES]},
            }}}
        if query == status.ISSUE_QUERY:
            return {"repository": {"issue": {"id": "I", "projectItems": {"nodes": [{
                "id": "card", "project": {"id": "P"},
                "fieldValueByName": {"name": self.current_status, "field": {"id": "S"}},
            }]}}}}
        if query == assignment.ISSUE_PRS:
            return {"repository": {"issue": {"closedByPullRequestsReferences": {"nodes": self.linked_prs}}}}
        if query == status.UPDATE_QUERY:
            self.current_status = variables["option"]
            self.writes.append(("STATUS", self.current_status, None))
            if self.current_status == "Ready" and self.lose_ready_response:
                raise status.SyncError("Ready request timed out after write")
            return {}
        raise AssertionError(query)


class AssignmentTests(unittest.TestCase):
    def setUp(self):
        self.api = FakeGitHub()
        self.project = status.Project(self.api, OWNER, REPO, 3)

    def sync(self, *, replace=False):
        assignment.synchronize(self.api, self.project, 35, self.api.issue["body"], replace=replace)

    def test_success_multi_select_exact_dependencies_and_read_only_retry(self):
        self.sync()
        self.assertEqual(self.api.current_status, "Ready")
        self.assertEqual(self.api.issue["type"], {"name": "Feature"})
        self.assertEqual(self.api.values[1]["single_select_option"], {"name": "High"})
        self.assertEqual(self.api.values[2]["multi_select_options"], [{"name": "Simulation"}, {"name": "QA"}])
        self.assertEqual(self.api.values[3]["single_select_option"], {"name": "No"})
        self.assertEqual(self.api.values[9]["value"], "preserve")
        self.assertEqual(self.api.links[35], {16, 34})
        self.assertEqual(self.api.writes[-1], ("STATUS", "Ready", None))
        self.api.writes.clear()
        self.sync()
        self.assertEqual(self.api.writes, [])

    def test_single_select_and_explicit_no_prerequisites(self):
        self.api.issue["body"] = body(workstreams=["Simulation"], prerequisites=[])
        self.api.definitions[2]["data_type"] = "single_select"
        self.sync()
        self.assertEqual(self.api.values[2]["single_select_option"], {"name": "Simulation"})
        self.assertEqual(self.api.links[35], set())

    def test_wrong_single_select_size_and_unknown_option_fail_before_mutations(self):
        self.api.definitions[2]["data_type"] = "single_select"
        with self.assertRaisesRegex(MetadataError, "cannot store"):
            self.sync()
        self.api.issue["body"] = body(workstreams=["Unknown"])
        with self.assertRaisesRegex(MetadataError, "Unknown or ambiguous native option"):
            self.sync()
        self.assertEqual(self.api.writes, [])

    def test_malformed_and_ambiguous_declarations_fail_before_mutations(self):
        valid = body()
        for invalid in (
            "Priority: High", valid + "\n" + valid, valid.replace("```assignment-v1", "```assignment-v2"),
            valid.replace('"type":', '"type": "Task", "type":'), valid.replace('"type":', '"types":'),
            body(priority="high"), body(prerequisites=[16, 16]), body(prerequisites=[True]),
            body(workstreams=["Simulation", "simulation"]), body(requires_human_approval="No"),
            valid.replace("prerequisites: native", "prerequisites: none"),
            valid.replace("Approved scope.", ""), valid.replace("```assignment-v1", "<!--\n```assignment-v1"),
        ):
            with self.subTest(invalid=invalid):
                self.api.issue["body"] = invalid
                with self.assertRaises(MetadataError):
                    self.sync()
        self.assertEqual(self.api.writes, [])

    def test_body_edit_after_command_is_rejected(self):
        original = self.api.issue["body"]
        self.api.issue["body"] = body(prerequisites=[])
        with self.assertRaisesRegex(MetadataError, "issue body changed"):
            assignment.synchronize(self.api, self.project, 35, original, replace=True)
        self.assertEqual(self.api.writes, [])

    def test_dependency_conflict_requires_owner_replacement(self):
        self.api.links[35] = {16, 99}
        with self.assertRaisesRegex(MetadataError, "Conflicting native prerequisites"):
            self.sync()
        self.assertEqual(self.api.writes, [])
        self.assertEqual(self.api.links[35], {16, 99})
        self.sync(replace=True)
        self.assertEqual(self.api.links[35], {16, 34})
        self.assertIn(("DELETE", f"{DEPENDENCIES}/1099", None), self.api.writes)

    def test_type_and_field_conflicts_require_replacement(self):
        self.api.issue["type"] = {"name": "Task"}
        with self.assertRaisesRegex(MetadataError, "Conflicting native Type"):
            self.sync()
        self.api.issue["type"] = {"name": "Feature"}
        self.api.values[1] = {"issue_field_id": 1, "issue_field_name": "Priority",
                              "data_type": "single_select", "single_select_option": {"name": "Low"}}
        with self.assertRaisesRegex(MetadataError, "Conflicting native Priority"):
            self.sync()
        self.assertEqual(self.api.writes, [])
        self.sync(replace=True)
        self.assertEqual(self.api.values[1]["single_select_option"], {"name": "High"})

    def test_self_cycles_transitive_cycles_and_unknown_prerequisites(self):
        self.api.issue["body"] = body(prerequisites=[35])
        with self.assertRaisesRegex(MetadataError, "Self or cyclic"):
            self.sync()
        self.api.issue["body"] = body()
        self.api.issues[16] = issue(16, state="open")
        self.api.links[16] = {99}
        self.api.links[99] = {35}
        with self.assertRaisesRegex(MetadataError, "Self or cyclic"):
            self.sync()
        self.api.issue["body"] = body(prerequisites=[1234])
        with self.assertRaisesRegex(MetadataError, "404"):
            self.sync()
        self.assertEqual(self.api.writes, [])

    def test_duplicate_native_ids_cannot_collapse_declared_dependencies(self):
        self.api.issues[34]["id"] = self.api.issues[16]["id"]
        with self.assertRaisesRegex(MetadataError, "Ambiguous native prerequisite identity"):
            self.sync()
        self.assertEqual(self.api.writes, [])

    def test_shared_prerequisite_and_invalid_transitive_identity(self):
        self.api.links[16] = {99}
        self.api.links[34] = {99}
        list_all = self.api.list_all

        def external_second_link(path):
            rows = list_all(path)
            if path == f"{PATH}/34/dependencies/blocked_by":
                rows[0]["url"] = "https://api.github.com/repos/other/repo/issues/99"
            return rows

        with patch.object(self.api, "list_all", side_effect=external_second_link):
            with self.assertRaisesRegex(MetadataError, "external prerequisite chain"):
                self.sync()
        self.assertEqual(self.api.writes, [])
        self.sync()
        self.assertEqual(self.api.current_status, "Ready")

    def test_partial_write_stays_blocked_and_can_retry(self):
        self.api.current_status = "Ready"
        self.api.reject_once = FIELDS
        with self.assertRaisesRegex(MetadataError, "503"):
            self.sync()
        self.assertEqual(self.api.writes[0], ("STATUS", "Blocked", None))
        self.assertEqual(self.api.current_status, "Blocked")
        self.assertEqual(self.api.issue["type"], {"name": "Feature"})
        self.api.writes.clear()
        self.sync()
        self.assertEqual(self.api.current_status, "Ready")
        self.assertFalse(any(method == "PATCH" for method, _, _ in self.api.writes))

    def test_dependency_readback_mismatch_is_not_ready(self):
        self.api.drop_dependency = 34
        with self.assertRaisesRegex(MetadataError, "read-back did not match"):
            self.sync()
        self.assertEqual(self.api.current_status, "Backlog")
        self.assertEqual(self.api.links[35], {16})
        self.api.drop_dependency = None
        self.sync()
        self.assertEqual(self.api.links[35], {16, 34})

    def test_lost_ready_response_is_compensated(self):
        self.api.lose_ready_response = True
        with self.assertRaisesRegex(status.SyncError, "timed out"):
            self.sync()
        self.assertEqual(self.api.current_status, "Blocked")

    def test_approval_gate_stores_yes_but_never_publishes_ready(self):
        self.api.issue["body"] = body(requires_human_approval=True)
        with self.assertRaisesRegex(MetadataError, "human approval is outstanding"):
            self.sync()
        self.assertEqual(self.api.values[3]["single_select_option"], {"name": "Yes"})
        self.assertEqual(self.api.current_status, "Backlog")

    def test_open_and_unaccepted_prerequisites_do_not_prevent_publication(self):
        self.api.issues[16] = issue(16, state="open")
        self.api.issues[34]["state_reason"] = "not_planned"
        self.sync()
        self.assertEqual(self.api.links[35], {16, 34})
        self.assertEqual(self.api.current_status, "Ready")

    def test_active_board_status_open_pr_and_closed_issue_are_protected(self):
        for state in ("In Progress", "In Review"):
            self.api.current_status = state
            with self.assertRaisesRegex(MetadataError, "cannot be synchronized"):
                self.sync(replace=True)
        self.api.current_status = "Backlog"
        self.api.linked_prs = [{"url": "https://github.com/example", "isDraft": True}]
        with self.assertRaisesRegex(MetadataError, "open linked PR"):
            self.sync(replace=True)
        self.api.issue["state"] = "closed"
        with self.assertRaisesRegex(MetadataError, "no longer open"):
            self.sync()
        self.assertEqual(self.api.writes, [])


class CommandTests(unittest.TestCase):
    def event(self, text="/assignment sync", author=OWNER):
        return {"action": "created", "issue": {"number": 35, "state": "open", "body": body()},
                "comment": {"body": text, "user": {"login": author}, "author_association": "OWNER"}}

    def test_exact_owner_commands_only(self):
        for text, author in (
            ("/assignment sync", "connector[bot]"), ("/assignment sync #34", OWNER),
            ("/assignment sync --replace\nMore text", OWNER), ("/status Ready", OWNER),
        ):
            self.assertIsNone(status.assignment_command("issue_comment", self.event(text, author), OWNER))
        for text, replace in (("/assignment sync", False), ("/assignment sync --replace", True)):
            event = self.event(text)
            self.assertEqual(status.assignment_command("issue_comment", event, OWNER), (35, body(), replace))
            event["issue"]["pull_request"] = {}
            self.assertIsNone(status.assignment_command("issue_comment", event, OWNER))
        event = self.event()
        event["action"] = "edited"
        self.assertIsNone(status.assignment_command("issue_comment", event, OWNER))
        event["action"] = "created"
        event["issue"]["state"] = "closed"
        with self.assertRaisesRegex(status.SyncError, "open issue"):
            status.assignment_command("issue_comment", event, OWNER)

    def test_main_routes_owner_command_without_falling_back_to_status(self):
        for author in (OWNER, "connector[bot]"):
            env = {
                "GITHUB_REPOSITORY": f"{OWNER}/{REPO}", "PROJECT_NUMBER": "3",
                "GITHUB_EVENT_PATH": "event.json", "GITHUB_EVENT_NAME": "issue_comment",
            }
            with patch.dict(status.os.environ, env, clear=True), \
                    patch("builtins.open", mock_open(read_data=json.dumps(self.event(author=author)))), \
                    patch.object(status, "GitHub"), patch.object(status, "MetadataAPI") as metadata, \
                    patch.object(status, "Project") as project, patch.object(status, "synchronize") as sync:
                self.assertEqual(status.main(), 0)
                if author == OWNER:
                    sync.assert_called_once_with(metadata.return_value, project.return_value, 35, body(),
                                                 replace=False)
                else:
                    metadata.assert_not_called()
                    sync.assert_not_called()
                project.return_value.update.assert_not_called()

    def test_historical_run_cannot_replay_replacement(self):
        env = {
            "GITHUB_REPOSITORY": f"{OWNER}/{REPO}", "PROJECT_NUMBER": "3",
            "GITHUB_EVENT_PATH": "event.json", "GITHUB_EVENT_NAME": "issue_comment",
            "GITHUB_RUN_ATTEMPT": "2",
        }
        event = json.dumps(self.event("/assignment sync --replace"))
        with patch.dict(status.os.environ, env, clear=True), \
                patch("builtins.open", mock_open(read_data=event)), \
                patch.object(status, "GitHub"), patch.object(status, "Project"), \
                patch.object(status, "synchronize") as sync:
            with self.assertRaisesRegex(status.SyncError, "fresh owner comment"):
                status.main()
            sync.assert_not_called()

    def test_paginated_rest_lists_include_later_pages(self):
        api = GitHub("mock")
        api.request = Mock(side_effect=[list(range(100)), [100]])
        self.assertEqual(api.list_all(FIELDS), list(range(101)))
        self.assertEqual([call.args[0] for call in api.request.call_args_list],
                         [f"{FIELDS}?per_page=100&page=1", f"{FIELDS}?per_page=100&page=2"])
