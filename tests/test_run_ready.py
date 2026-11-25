import io
import os
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, call, patch

from tools import run_ready as pilot
from tools.ready_selection import Selection


class PilotTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name) / "The-Producer"
        self.run_home = self.repo.parent / ".The-Producer-agent-runs"
        self.project = Mock(spec=pilot.Project)
        self.selection = Mock(side_effect=[Selection([14, 15], ["Next issue: #14"]),
                                          Selection([14], ["Next issue: #14"])])
        self.execute = Mock(side_effect=self.fake_runner)
        self.identity = Mock(return_value={"login": pilot.board.OWNER})
        self.stdout, self.stderr = io.StringIO(), io.StringIO()

    def fake_runner(self, args, *, claim, verify_status):
        self.assertEqual((args.issue, args.model, args.approve_issue, args.retry_blocked),
                         (14, "openai/test", True, False))
        claim(args.issue)
        verify_status(args.issue, "In Progress")
        print("one fake Build + independent Reviewer")
        verify_status(args.issue, "In Review")
        return 0

    def run_cli(self, *args, number="7"):
        with (patch.dict(os.environ, {"PROJECT_NUMBER": number}),
              patch.object(pilot.Path, "cwd", return_value=self.repo),
              patch.object(pilot.runner, "registered_worktrees", return_value=[{"path": self.repo}]),
              patch.object(pilot.runner, "run_cmd", return_value="https://github.com/" + pilot.board.REPOSITORY),
              patch.object(pilot.board, "project_issues", return_value=("Board", "board-url", {"Ready": [14, 15]})),
              patch.object(pilot.board, "gh_json", self.identity),
              patch.object(pilot.selector, "select", self.selection),
              patch.object(pilot, "Project", return_value=self.project),
              patch.object(pilot.runner, "orchestrate", self.execute),
              redirect_stdout(self.stdout), redirect_stderr(self.stderr)):
            return pilot.main(["--model", "openai/test", *args])

    def test_no_work_does_not_start_runner_or_create_lock(self):
        self.selection.side_effect = [Selection([], ["No eligible work."])]
        self.assertEqual(self.run_cli(), 0)
        self.assertIn("No eligible work.", self.stdout.getvalue())
        self.execute.assert_not_called()
        self.identity.assert_not_called()
        self.assertFalse(self.run_home.exists())

    def test_dry_run_has_no_writes_or_sessions(self):
        self.assertEqual(self.run_cli("--dry-run"), 0)
        self.assertIn("would claim #14", self.stdout.getvalue())
        self.execute.assert_not_called()
        self.identity.assert_not_called()
        self.project.post.assert_not_called()
        self.assertFalse(self.run_home.exists())

    def test_expected_issue_does_not_override_ranking(self):
        self.assertEqual(self.run_cli("--expect-issue", "15"), 1)
        self.execute.assert_not_called()
        self.project.post.assert_not_called()

    def test_one_issue_claim_verified_before_build_and_handoff(self):
        self.project.status.side_effect = ["Ready", "Ready", "In Progress",
                                           "In Progress", "In Progress", "In Review"]
        with patch.object(pilot.time, "sleep"):
            self.assertEqual(self.run_cli("--expect-issue", "14"), 0)
        self.execute.assert_called_once()
        self.project.post.assert_called_once_with(14, "In Progress")
        self.assertEqual([entry.args[0] for entry in self.selection.call_args_list], [[14, 15], [14]])
        out = self.stdout.getvalue()
        self.assertLess(out.index("is In Progress"), out.index("one fake Build"))
        self.assertLess(out.index("one fake Build"), out.index("is In Review"))

    def test_recheck_refusal_does_not_fall_through_to_second_issue(self):
        self.selection.side_effect = [Selection([14, 15], []), Selection([], ["WAIT #14: prerequisite open"])]
        self.assertEqual(self.run_cli(), 1)
        self.assertIn("WAIT #14", self.stderr.getvalue())
        self.assertNotIn("one fake Build", self.stdout.getvalue())
        self.project.post.assert_not_called()
        self.execute.assert_called_once()

    def test_owner_withdrawal_before_claim_does_not_post(self):
        self.project.status.return_value = "Backlog"
        self.assertEqual(self.run_cli(), 1)
        self.assertIn("Backlog, not Ready", self.stderr.getvalue())
        self.project.post.assert_not_called()

    def test_withdrawal_or_error_after_claim_comment_stops_without_more_writes(self):
        for observed in ("Backlog", pilot.BoardError("Project API unavailable")):
            with self.subTest(observed=observed):
                self.selection.side_effect = [Selection([14], []), Selection([14], [])]
                self.project.post.reset_mock()
                self.project.status.side_effect = ["Ready", observed]
                self.assertEqual(self.run_cli(), 1)
                self.project.post.assert_called_once_with(14, "In Progress")
                self.assertNotIn("one fake Build", self.stdout.getvalue())

    def test_claim_transition_timeout_never_starts_build(self):
        self.project.status.return_value = "Ready"
        with patch.object(pilot.time, "monotonic", side_effect=[0, 0, 121]):
            self.assertEqual(self.run_cli(), 1)
        self.assertIn("stayed Ready", self.stderr.getvalue())
        self.assertNotIn("one fake Build", self.stdout.getvalue())

    def test_review_transition_lost_is_not_replayed(self):
        self.project.status.side_effect = ["Ready", "In Progress", "In Progress", "In Progress"]
        with patch.object(pilot.time, "monotonic", side_effect=[0, 0, 0, 0, 121]):
            self.assertEqual(self.run_cli(), 1)
        self.assertIn("stayed In Progress; expected In Review", self.stderr.getvalue())
        self.project.post.assert_called_once_with(14, "In Progress")

    def test_failed_runner_marks_blocked_only_while_still_in_progress(self):
        def fail(args, *, claim, verify_status):
            claim(args.issue)
            raise pilot.runner.Blocked("Build permission denied")

        self.execute.side_effect = fail
        for status, expected in [("In Progress", [call(14, "In Progress"), call(14, "Blocked")]),
                                 ("In Review", [call(14, "In Progress")]),
                                 ("Backlog", [call(14, "In Progress")]),
                                 (pilot.BoardError("API failed"), [call(14, "In Progress")])]:
            with self.subTest(status=status):
                self.selection.side_effect = [Selection([14], []), Selection([14], [])]
                self.project.post.reset_mock()
                self.project.status.side_effect = ["Ready", "In Progress", status, "Blocked"]
                self.assertEqual(self.run_cli(), 1)
                self.assertEqual(self.project.post.call_args_list, expected)
                self.assertIn("Build permission denied", self.stderr.getvalue())

    def test_api_and_non_owner_auth_fail_without_dispatch(self):
        self.selection.side_effect = pilot.board.ReadError("GitHub authentication failed")
        self.assertEqual(self.run_cli("--dry-run"), 1)
        self.assertIn("authentication failed", self.stderr.getvalue())
        self.selection.side_effect = [Selection([14], [])]
        self.identity.return_value = {"login": "non-owner"}
        self.assertEqual(self.run_cli(), 1)
        self.assertIn("require gh authentication as", self.stderr.getvalue())
        self.execute.assert_not_called()
        self.project.post.assert_not_called()

    def test_configuration_fails_before_api(self):
        with self.assertRaises(SystemExit) as failure:
            self.run_cli(number="")
        self.assertEqual(failure.exception.code, 2)
        self.selection.assert_not_called()
        self.execute.assert_not_called()

    def test_lock_contention_and_unfinished_run_refuse_dispatch(self):
        with pilot.pilot_lock(self.run_home):
            self.assertEqual(self.run_cli(), 1)
        self.assertIn("holds the local lock", self.stderr.getvalue())
        entry = self.run_home / "issue-99"
        entry.mkdir()
        (entry / "state.json").write_text('{"phase": "developing"}')
        self.assertEqual(self.run_cli(), 1)
        self.assertIn("Active or unfinished run", self.stderr.getvalue())
        self.execute.assert_not_called()
        self.project.post.assert_not_called()

    def test_status_read_requires_one_unambiguous_card(self):
        project = pilot.Project(7)
        with patch.object(pilot.board, "project_issues", return_value=("Board", "url", {"In Progress": [14]})):
            self.assertEqual(project.status(14), "In Progress")
            with self.assertRaises(pilot.BoardError):
                project.status(15)
        with patch.object(pilot.board, "project_issues", return_value=("Board", "url",
                                                                      {"In Progress": [14], "Ready": [14]})):
            with self.assertRaises(pilot.BoardError):
                project.status(14)

    def test_status_write_uses_exact_existing_owner_command(self):
        body = "/status In Progress"
        comment = {"body": body, "user": {"login": pilot.board.OWNER}}
        with patch.object(pilot.board, "gh_json", return_value=comment) as request:
            pilot.Project(7).post(14, "In Progress")
        self.assertEqual(request.call_args.args[1:],
                         ("--method", "POST", f"repos/{pilot.board.REPOSITORY}/issues/14/comments", "-f", f"body={body}"))
