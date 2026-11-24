"""Offline tests for the GitHub Project status sync logic."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

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

    def test_newer_owner_command_supersedes_queued_pr_and_comment_jobs(self):
        opened = "2026-11-24T21:00:00Z"
        failed = "2026-11-24T21:02:00Z"
        claim = {"id": 4, "body": "/status In Progress", "created_at": "2026-11-24T20:59:00Z",
                 "user": {"login": self.OWNER}}
        blocked = {"id": 5, "body": "/status Blocked", "created_at": failed,
                   "user": {"login": self.OWNER}}
        stranger = {**blocked, "id": 6, "body": "/status Ready", "user": {"login": "stranger"}}
        pr = {"action": "opened", "pull_request": {"created_at": opened}}
        self.assertFalse(sync.superseded("pull_request_target", pr, [claim], self.OWNER, pr_time=opened))
        self.assertTrue(sync.superseded("pull_request_target", pr, [claim, blocked], self.OWNER, pr_time=opened))
        self.assertTrue(sync.superseded("pull_request_target", pr, [{**blocked, "created_at": opened}],
                                        self.OWNER, pr_time=opened))
        self.assertTrue(sync.superseded("issue_comment", {"comment": claim}, [claim, blocked], self.OWNER))
        self.assertFalse(sync.superseded("issue_comment", {"comment": blocked},
                                         [claim, blocked, stranger], self.OWNER))
        self.assertTrue(sync.superseded("issue_comment", {"comment": claim},
                                         [{**claim, "body": "/status Backlog"}], self.OWNER))

    def test_delayed_open_or_reopen_preserves_owner_status_and_closed_issues_stay_done(self):
        created = "2026-11-24T21:00:00Z"
        reopened = "2026-11-24T21:02:00Z"
        later = "2026-11-24T21:03:00Z"
        for action, state, command_time, expected in [
            ("opened", "open", "2026-11-24T21:01:00Z", None),
            ("reopened", "open", later, None),
            ("reopened", "open", reopened, None),  # GitHub timestamps have second precision.
            ("reopened", "open", created, "Backlog"),
            ("reopened", "closed", later, "Done"),
            ("closed", "closed", later, "Done"),
        ]:
            with self.subTest(action=action, state=state, command_time=command_time), \
                 tempfile.TemporaryDirectory() as tmp:
                event_path = Path(tmp) / "event.json"
                event_path.write_text(json.dumps({"action": action, "issue": {
                    "number": 4, "created_at": created, "updated_at": reopened,
                }}))
                with patch.dict(os.environ, {"GITHUB_REPOSITORY": f"{self.OWNER}/{self.REPO}",
                                             "PROJECT_NUMBER": "7", "GITHUB_EVENT_NAME": "issues",
                                             "GITHUB_EVENT_PATH": str(event_path)}), \
                     patch.object(sync, "GitHub") as github, patch.object(sync, "Project") as project:
                    project.return_value.title = "The Producer"
                    github.return_value.issue.return_value = {"state": state}
                    github.return_value.issue_comments.return_value = [{
                        "id": 1, "body": "/status Ready" if action == "opened" else "/status In Progress",
                        "created_at": command_time, "user": {"login": self.OWNER},
                    }]
                    self.assertEqual(sync.main(), 0)
                if expected is None:
                    project.return_value.update.assert_not_called()
                else:
                    project.return_value.update.assert_called_once_with(4, expected)

    def run_status_job(self, event_name, event, *, prs, comments, transition=None, state="open"):
        def request(path, payload=None):
            if path.endswith("/issues/4"):
                return {"state": state}
            if "/issues/4/comments?" in path:
                return comments
            if "/pulls?state=all&base=main&" in path:
                return prs
            if path == "/graphql":
                self.assertEqual(payload["variables"], {"id": "PR_123"})
                self.assertIn("... on ReadyForReviewEvent { createdAt }", payload["query"])
                return {"data": {"node": {"timelineItems": {"nodes": [transition] if transition else []}}}}
            self.fail(f"Unexpected GitHub request: {path}")

        with tempfile.TemporaryDirectory() as tmp:
            event_path = Path(tmp) / "event.json"
            event_path.write_text(json.dumps(event))
            with patch.dict(os.environ, {"GITHUB_REPOSITORY": f"{self.OWNER}/{self.REPO}",
                                          "PROJECT_NUMBER": "7",
                                          "PROJECTS_TOKEN": "test",
                                          "GITHUB_EVENT_NAME": event_name,
                                          "GITHUB_EVENT_PATH": str(event_path)}), \
                 patch.object(sync.GitHub, "request", side_effect=request), \
                 patch.object(sync, "Project") as project:
                self.assertEqual(sync.main(), 0)
        return [call.args for call in project.return_value.update.call_args_list]

    def pr_list_entry(self):
        return {"number": 123, "node_id": "PR_123", "state": "open", "draft": False,
                "head": {"repo": {"full_name": f"{self.OWNER}/{self.REPO}"}},
                "base": {"ref": "main"}, "body": "Closes #4",
                "created_at": "2026-11-24T21:00:00Z",
                "updated_at": "2026-11-24T21:10:00Z", "closed_at": None, "merged_at": None}

    def comment_event(self, body, created_at):
        return {"action": "created", "issue": {"number": 4, "state": "open"},
                "comment": {"id": 42, "body": body, "created_at": created_at,
                            "user": {"login": self.OWNER}}}

    def test_delayed_in_progress_comment_does_not_overwrite_newer_ready_pr_transition(self):
        pr = self.pr_list_entry()
        event = self.comment_event("/status In Progress", "2026-11-24T21:03:00Z")
        sources = {"prs": [pr], "comments": [event["comment"]],
                   "transition": {"__typename": "ReadyForReviewEvent", "createdAt": "2026-11-24T21:05:00Z"}}
        self.assertEqual(self.run_status_job("pull_request_target", {
            "action": "ready_for_review", "pull_request": pr}, **sources), [(4, "In Review")])
        self.assertEqual(self.run_status_job("issue_comment", event, **sources), [])

    def test_blocked_wins_if_older_pr_open_job_writes_review_after_comment_was_posted(self):
        pr = self.pr_list_entry()
        event = self.comment_event("/status Blocked", "2026-11-24T21:03:00Z")
        opened = {"action": "opened", "pull_request": pr}
        # The old job read comments before Blocked was posted but its write landed
        # after the post. Neither its write time nor PR updated_at is event evidence.
        self.assertEqual(self.run_status_job("pull_request_target", opened, prs=[pr], comments=[]),
                         [(4, "In Review")])
        self.assertEqual(self.run_status_job("issue_comment", event, prs=[pr], comments=[event["comment"]]),
                         [(4, "Blocked")])
        self.assertEqual(self.run_status_job("pull_request_target", opened,
                                             prs=[pr], comments=[event["comment"]]), [])

    def test_newer_owner_override_uses_ready_event_time_not_pr_updated_at(self):
        pr = self.pr_list_entry()
        event = self.comment_event("/status Blocked", "2026-11-24T21:07:00Z")
        sources = {"prs": [pr], "comments": [event["comment"]],
                   "transition": {"__typename": "ReadyForReviewEvent", "createdAt": "2026-11-24T21:05:00Z"}}
        self.assertEqual(self.run_status_job("pull_request_target", {
            "action": "ready_for_review", "pull_request": pr}, **sources), [])
        self.assertEqual(self.run_status_job("issue_comment", event, **sources), [(4, "Blocked")])
        self.assertEqual(self.run_status_job("issue_comment", event, state="closed", **sources), [(4, "Done")])


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
