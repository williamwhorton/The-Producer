"""Offline tests for the GitHub Project status sync logic."""
import importlib.util
from pathlib import Path
import unittest

FILE = Path(__file__).resolve().parents[1] / "tools" / "sync_project_status.py"
spec = importlib.util.spec_from_file_location("project_sync", FILE)
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


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
    def test_preserve_active_status_and_set_review(self):
        class FakeAPI:
            def __init__(self):
                self.calls = []
                self.current = None

            def graphql(self, query, variables):
                self.calls.append(variables)
                if "user(login:" in query:
                    return {"user": {"projectV2": {
                        "id": "P_1", "title": "Producer",
                        "field": {"id": "SF_1", "options": [
                            {"id": f"O_{i}", "name": name}
                            for i, name in enumerate(sync.STATUSES)
                        ]},
                    }}}
                if "projectItems(first:" in query:
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
                if "updateProjectV2ItemFieldValue" in query:
                    return {"updateProjectV2ItemFieldValue": {
                        "projectV2Item": {"id": "PV_1"}
                    }}
                raise AssertionError(query)

        api = FakeAPI()
        project = sync.Project(api, "williamwhorton", "The-Producer", 3)
        api.current = "In Progress"
        project.update(4, "Backlog", preserve_open=True)
        self.assertEqual(len(api.calls), 2)
        project.update(4, "In Review")
        self.assertEqual(len(api.calls), 4)


if __name__ == "__main__":
    unittest.main()
