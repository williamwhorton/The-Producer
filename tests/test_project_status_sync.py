"""Offline tests for the GitHub Project status sync logic."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "tools" / "sync_project_status.py"
spec = importlib.util.spec_from_file_location("project_sync", FILE)
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


class WorkflowTests(unittest.TestCase):
    def test_all_events_share_one_queued_non_cancelling_group(self):
        workflow = (ROOT / ".github/workflows/project-status-sync.yml").read_text()
        # Check workflow-level concurrency without adding a YAML dependency.
        self.assertRegex(
            workflow,
            r"(?m)^concurrency:\n  group: project-status-sync\n"
            r"  cancel-in-progress: false\n  queue: max\n",
        )


class CommandTests(unittest.TestCase):
    def test_exact_command(self):
        self.assertEqual(sync.comment_status(" /status in progress \n"), "In Progress")
        self.assertEqual(sync.comment_status("/status Blocked"), "Blocked")

    def test_do_not_match_prose(self):
        self.assertIsNone(sync.comment_status("working on it"))
        self.assertIsNone(sync.comment_status("/status Done\nother text"))
        self.assertIsNone(sync.comment_status("/status SomethingElse"))

    def test_closing_refs(self):
        body = ("Closes #4\nFixes #5\n"
                "resolves williamwhorton/The-Producer#11\n"
                "Closes other/repo#100")
        self.assertEqual(
            sync.closing_issues(body, "williamwhorton", "The-Producer"),
            [4, 5, 11],
        )

    def test_one_time_bootstrap(self):
        self.assertEqual(
            sync.parse_bootstrap("4=In Progress,5=Blocked"),
            {4: "In Progress", 5: "Blocked"},
        )
        with self.assertRaises(sync.SyncError):
            sync.parse_bootstrap("4=invalid")
        with self.assertRaises(sync.SyncError):
            sync.parse_bootstrap("x=Ready")


class EventTests(unittest.TestCase):
    OWNER, REPO = "williamwhorton", "The-Producer"

    def run_event(self, event, payload):
        return sync.decide_event(event, payload, self.OWNER, self.REPO)

    def test_issue_lifecycle(self):
        for action, expected in [
            ("opened", "Backlog"),
            ("closed", "Done"),
            ("reopened", "Backlog"),
        ]:
            self.assertEqual(
                self.run_event(
                    "issues", {"action": action, "issue": {"number": 4}}
                ),
                {4: expected},
            )

    def test_comment_permissions_and_pr_exclusion(self):
        event = {
            "action": "created",
            "issue": {"number": 4, "state": "open"},
            "comment": {
                "body": "/status In Progress",
                "user": {"login": "stranger"},
            },
        }
        self.assertEqual(self.run_event("issue_comment", event), {})
        event["comment"]["user"]["login"] = "williamwhorton"
        self.assertEqual(
            self.run_event("issue_comment", event), {4: "In Progress"}
        )
        event["issue"]["pull_request"] = {"url": "https://example.com"}
        self.assertEqual(self.run_event("issue_comment", event), {})

    def test_done_requires_closed_issue(self):
        event = {
            "action": "created",
            "issue": {"number": 4, "state": "open"},
            "comment": {
                "body": "/status Done",
                "user": {"login": "williamwhorton"},
            },
        }
        with self.assertRaises(sync.SyncError):
            self.run_event("issue_comment", event)
        event["issue"]["state"] = "closed"
        self.assertEqual(self.run_event("issue_comment", event), {4: "Done"})

    def test_pr_lifecycle(self):
        pr = {
            "head": {"repo": {"full_name": "williamwhorton/The-Producer"}},
            "base": {"ref": "main"},
            "body": "Closes #4",
            "draft": False,
        }
        self.assertEqual(
            self.run_event("pull_request_target", {
                "action": "opened", "pull_request": pr,
            }),
            {4: "In Review"},
        )
        pr["draft"] = True
        self.assertEqual(
            self.run_event("pull_request_target", {
                "action": "opened", "pull_request": pr,
            }),
            {4: "In Progress"},
        )
        pr["draft"] = False
        self.assertEqual(
            self.run_event("pull_request_target", {
                "action": "ready_for_review", "pull_request": pr,
            }),
            {4: "In Review"},
        )
        self.assertEqual(
            self.run_event("pull_request_target", {
                "action": "converted_to_draft", "pull_request": pr,
            }),
            {4: "In Progress"},
        )
        self.assertEqual(
            self.run_event("pull_request_target", {
                "action": "closed", "pull_request": pr,
            }),
            {4: "In Progress"},
        )
        pr["merged"] = True
        self.assertEqual(
            self.run_event("pull_request_target", {
                "action": "closed", "pull_request": pr,
            }),
            {},
        )

    def test_ignore_fork_pr(self):
        pr = {
            "head": {"repo": {"full_name": "other/fork"}},
            "base": {"ref": "main"},
            "body": "Closes #4",
        }
        self.assertEqual(
            self.run_event("pull_request_target", {
                "action": "opened", "pull_request": pr,
            }),
            {},
        )


class ProjectTests(unittest.TestCase):
    def setUp(self):
        class FakeAPI:
            def __init__(self):
                self.calls = []
                self.current = "In Progress"
                self.apply_update = True

            def graphql(self, query, variables):
                self.calls.append(query)
                if query == sync.PROJECT_QUERY:
                    return {"user": {"projectV2": {
                        "id": "P_1", "title": "Producer",
                        "field": {"id": "SF_1", "options": [
                            {"id": f"O_{i}", "name": name}
                            for i, name in enumerate(sync.STATUSES)
                        ]},
                    }}}
                if query == sync.ISSUE_QUERY:
                    return {"repository": {"issue": {
                        "id": "I_1",
                        "projectItems": {"nodes": [{
                            "id": "PV_1", "project": {"id": "P_1"},
                            "fieldValues": {"nodes": [{
                                "name": self.current,
                                "field": {"id": "SF_1"},
                            }]},
                        }]},
                    }}}
                if query == sync.UPDATE_QUERY:
                    if self.apply_update:
                        self.current = sync.STATUSES[int(variables["option"][2:])]
                    return {"updateProjectV2ItemFieldValue": {
                        "projectV2Item": {"id": "PV_1"}
                    }}
                raise AssertionError(query)

        self.api = FakeAPI()
        self.project = sync.Project(self.api, "williamwhorton", "The-Producer", 3)
        self.api.calls.clear()

    def test_preserve_active_status(self):
        self.project.update(4, "Backlog", preserve_open=True)
        self.assertEqual(self.api.calls, [sync.ISSUE_QUERY])
        self.assertEqual(self.api.current, "In Progress")

    def test_write_reads_back_status(self):
        self.project.update(4, "In Review")
        self.assertEqual(self.api.calls, [
            sync.ISSUE_QUERY, sync.UPDATE_QUERY, sync.ISSUE_QUERY,
        ])
        self.assertEqual(self.api.current, "In Review")

    def test_matching_status_needs_no_write(self):
        self.project.update(4, "In Progress")
        self.assertEqual(self.api.calls, [sync.ISSUE_QUERY])

    def test_mismatched_status_fails_without_retry(self):
        self.api.apply_update = False
        with self.assertRaisesRegex(sync.SyncError, r"#4: could not verify Blocked"):
            self.project.update(4, "Blocked")
        self.assertEqual(self.api.calls, [
            sync.ISSUE_QUERY, sync.UPDATE_QUERY, sync.ISSUE_QUERY,
        ])

    def test_verification_requires_same_card(self):
        for item, status in [(None, None), ("PV_2", "In Review")]:
            with self.subTest(item=item):
                self.project.find_item = Mock(side_effect=[
                    ("PV_1", "In Progress", "I_1"), (item, status, "I_1"),
                ])
                with self.assertRaisesRegex(sync.SyncError, "different or missing card"):
                    self.project.update(4, "In Review")


if __name__ == "__main__":
    unittest.main()
