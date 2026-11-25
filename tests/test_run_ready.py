import argparse
import io
import json
import os
import signal
import subprocess
import sys
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
        self.board_read = Mock(return_value=("Board", "board-url", {"Ready": [14, 15]}))
        self.branch = "main"
        self.stdout, self.stderr = io.StringIO(), io.StringIO()

    def fake_runner(self, args, *, claim, verify_status):
        self.assertEqual((args.model, args.approve_issue, args.retry_blocked),
                         ("openai/test", True, False))
        claim(args.issue)
        verify_status(args.issue, "In Progress")
        print("one fake Build + independent Reviewer")
        verify_status(args.issue, "In Review", pending="In Progress")
        return 0

    def run_cli(self, *args, number="7", with_signals=False):
        def git(argv, _repo):
            if argv == ["git", "branch", "--show-current"]:
                return self.branch
            self.assertEqual(argv, ["git", "remote", "get-url", "origin"])
            return "https://github.com/" + pilot.board.REPOSITORY

        with (patch.dict(os.environ, {"PROJECT_NUMBER": number}),
              patch.object(pilot.Path, "cwd", return_value=self.repo),
              patch.object(pilot.runner, "registered_worktrees", return_value=[{"path": self.repo}]),
              patch.object(pilot.runner, "run_cmd", side_effect=git),
              patch.object(pilot.board, "project_issues", self.board_read),
              patch.object(pilot.board, "gh_json", self.identity),
              patch.object(pilot.selector, "select", self.selection),
              patch.object(pilot, "Project", return_value=self.project),
              patch.object(pilot.runner, "orchestrate", self.execute),
              redirect_stdout(self.stdout), redirect_stderr(self.stderr)):
            argv = ["--model", "openai/test", *args]
            if with_signals:
                with patch.object(pilot.sys, "argv", ["run_ready.py", *argv]):
                    return pilot.cli()
            return pilot.main(argv)

    def test_no_work_does_not_start_runner_or_create_lock(self):
        self.selection.side_effect = [Selection([], ["No eligible work."])]
        self.assertEqual(self.run_cli(), 0)
        self.assertIn("No eligible work.", self.stdout.getvalue())
        self.execute.assert_not_called()
        self.identity.assert_not_called()
        self.assertFalse(self.run_home.exists())

    def test_dry_run_has_no_writes_or_sessions(self):
        self.branch = "agent/issue-14"
        self.assertEqual(self.run_cli("--dry-run", "--expect-issue", "14"), 0)
        self.assertIn("would claim #14", self.stdout.getvalue())
        self.execute.assert_not_called()
        self.identity.assert_not_called()
        self.project.post.assert_not_called()
        self.assertFalse(self.run_home.exists())
        self.board_read.assert_called_once_with(7)

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

    def run_real_runner_offline(self, pr, verdict, *, board_error=None):
        self.repo.mkdir()
        args = argparse.Namespace(issue=14, repo=str(self.repo), model="openai/test",
                                  dry_run=False, approve_issue=True, retry_blocked=False,
                                  timeout_minutes=2)
        with (patch.object(pilot.runner, "preflight", return_value={"title": "Prototype"}),
              patch.object(pilot.runner, "run_cmd", return_value="a" * 40),
              patch.object(pilot.runner, "verify_checkout"),
              patch.object(pilot.runner, "pr_details", side_effect=pr),
              patch.object(pilot.runner, "run_agent",
                           side_effect=["Implemented", f"REVIEW_VERDICT: {verdict}"]) as agent,
              patch.object(pilot.runner, "cleanup_worktrees") as cleanup,
              patch.object(pilot.time, "sleep"),
              redirect_stdout(self.stdout), redirect_stderr(self.stderr)):
            def run():
                return pilot.run_one(args, self.project, lambda n: Selection([n], []),
                                     pilot.runner.orchestrate)

            if board_error:
                with self.assertRaisesRegex(pilot.BoardError, board_error):
                    run()
            else:
                self.assertEqual(run(), 1)
            self.assertEqual([entry.args[2].name for entry in agent.call_args_list],
                             ["developer-0.log", "review-0.log"])
            cleanup.assert_not_called()
        return json.loads((self.run_home / "issue-14/state.json").read_text())

    def test_handoff_rechecks_pr_head_after_the_board_wait(self):
        pr = {"number": 90, "url": "https://github.com/williamwhorton/The-Producer/pull/90",
              "headRefOid": "a" * 40}
        statuses = iter(["Ready", "In Progress", "In Progress", "In Progress",
                         "In Review", "In Review"])

        def status(issue):
            current = next(statuses)
            if current == "In Review":
                pr["headRefOid"] = "b" * 40
            return current

        self.project.status.side_effect = status
        state = self.run_real_runner_offline(lambda *_: dict(pr), "APPROVE")
        self.assertEqual((state["phase"], state["head_sha"]), ("blocked", "a" * 40))
        self.assertIn("verdict is stale", state["reason"])
        self.assertNotIn("READY FOR YOUR ACCEPTANCE", self.stdout.getvalue())
        self.project.post.assert_called_once_with(14, "In Progress")

    def test_withdrawn_card_stops_correction_without_another_status_write(self):
        pr = {"number": 90, "url": "https://github.com/williamwhorton/The-Producer/pull/90",
              "headRefOid": "a" * 40}
        self.project.status.side_effect = ["Ready", "In Progress", "In Progress", "Backlog"]

        state = self.run_real_runner_offline(lambda *_: dict(pr), "REQUEST_CHANGES",
                                             board_error="Backlog, not In Review")
        self.assertEqual(state["phase"], "blocked")
        self.assertIn("Backlog, not In Review", state["reason"])
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

    def test_continuous_refreshes_independent_work_then_waits_for_human_merge(self):
        merged = False
        self.board_read.side_effect = [
            ("Board", "board-url", {"Ready": numbers})
            for numbers in ([14, 15, 16], [15, 16], [16], [16], [])
        ]

        def select(numbers, *_):
            if numbers == [16] and not merged:
                return Selection([], ["WAIT #16: prerequisite #14 has not been accepted"])
            return Selection([n for n in numbers if n != 16 or merged], ["Selection snapshot"])

        def idle(seconds):
            nonlocal merged
            self.assertEqual(seconds, 1)
            with self.assertRaisesRegex(pilot.runner.Blocked, "holds the local lock"):
                with pilot.pilot_lock(self.run_home):
                    self.fail("overlapping Ready run acquired the lock")
            if merged:
                raise KeyboardInterrupt
            self.assertEqual([c.args[0].issue for c in self.execute.call_args_list], [14, 15])
            merged = True

        self.selection.side_effect = select
        self.project.status.side_effect = ["Ready", "In Progress", "In Progress", "In Review"] * 3
        with (patch.object(pilot.time, "sleep", side_effect=idle) as sleep,
              patch.object(pilot, "pilot_lock", wraps=pilot.pilot_lock) as lock,
              patch.object(pilot, "refuse_active_work", wraps=pilot.refuse_active_work) as active):
            self.assertEqual(self.run_cli("--continuous", "--poll-seconds", "1"), 130)
            self.assertEqual(lock.call_count, 3)  # one session plus the two refused probes
            self.assertEqual(active.call_count, 5)
            self.assertEqual(sleep.call_count, 2)
        self.assertEqual([c.args[0].issue for c in self.execute.call_args_list], [14, 15, 16])
        self.assertEqual(self.board_read.call_count, 5)
        self.assertIn("WAIT #16", self.stdout.getvalue())
        with pilot.pilot_lock(self.run_home):
            pass  # Released on interrupt.

    def test_continuous_stops_after_nonzero_runner_exit(self):
        def quota_failure(args, *, claim, verify_status):
            claim(args.issue)
            return 9

        self.execute.side_effect = quota_failure
        self.project.status.side_effect = ["Ready", "In Progress", "In Progress", "Blocked"]
        self.assertEqual(self.run_cli("--continuous"), 1)
        self.board_read.assert_called_once_with(7)
        self.execute.assert_called_once()
        self.assertEqual(self.project.post.call_args_list, [call(14, "In Progress"), call(14, "Blocked")])

    def test_continuous_stops_on_api_error_refreshing_after_handoff(self):
        self.board_read.side_effect = [self.board_read.return_value, pilot.board.ReadError("API unavailable")]
        self.project.status.side_effect = ["Ready", "In Progress", "In Progress", "In Review"]
        self.assertEqual(self.run_cli("--continuous"), 1)
        self.assertIn("API unavailable", self.stderr.getvalue())
        self.execute.assert_called_once()
        self.project.post.assert_called_once_with(14, "In Progress")

    def test_continuous_rechecks_new_unfinished_local_state_after_handoff(self):
        def execute(*args, **kwargs):
            result = self.fake_runner(*args, **kwargs)
            entry = self.run_home / "issue-99"
            entry.mkdir()
            (entry / "state.json").write_text('{"phase": "developing"}')
            return result

        self.project.status.side_effect = ["Ready", "In Progress", "In Progress", "In Review"]
        self.execute.side_effect = execute
        self.assertEqual(self.run_cli("--continuous"), 1)
        self.assertIn("Active or unfinished run", self.stderr.getvalue())
        self.board_read.assert_called_once_with(7)
        self.execute.assert_called_once()

    def test_continuous_idle_sigterm_exits_before_refresh(self):
        self.selection.side_effect = [Selection([], ["No eligible work."])]
        before = signal.getsignal(signal.SIGTERM)
        with patch.object(pilot.time, "sleep", side_effect=lambda _: signal.raise_signal(signal.SIGTERM)) as idle:
            self.assertEqual(self.run_cli("--continuous", with_signals=True), 130)
        idle.assert_called_once_with(60)
        self.assertIs(signal.getsignal(signal.SIGTERM), before)
        self.board_read.assert_called_once_with(7)
        self.execute.assert_not_called()
        self.project.post.assert_not_called()

    def test_sigterm_during_agent_start_stops_the_child_and_session(self):
        self.project.status.side_effect = ["Ready", "In Progress", "In Progress", "Blocked"]
        popen = subprocess.Popen
        children = []
        log = self.repo / "stand-in-agent.log"
        self.repo.mkdir()

        def start_and_interrupt(*args, **kwargs):
            process = popen(*args, **kwargs)
            children.append(process)
            signal.raise_signal(signal.SIGTERM)
            return process

        def execute(args, *, claim, verify_status):
            claim(args.issue)
            pilot.runner.run_agent(
                [sys.executable, "-c", "import threading; threading.Event().wait()"],
                self.repo, log, 5,
            )
            self.fail("interrupted agent returned normally")

        self.execute.side_effect = execute
        with patch.object(pilot.runner.subprocess, "Popen", side_effect=start_and_interrupt):
            self.assertEqual(self.run_cli("--continuous", with_signals=True), 1)
        self.assertEqual(len(children), 1)
        self.assertIsNotNone(children[0].poll())
        self.assertTrue(log.exists())
        self.assertIn("Agent stopped (timeout or interruption)", self.stderr.getvalue())
        self.board_read.assert_called_once_with(7)
        self.project.post.assert_has_calls([call(14, "In Progress"), call(14, "Blocked")])

    def test_continuous_rechecks_branch_after_idle(self):
        self.selection.side_effect = [Selection([], ["No eligible work."])]

        def change_branch(_):
            self.branch = "agent/issue-14"

        with patch.object(pilot.time, "sleep", side_effect=change_branch):
            self.assertEqual(self.run_cli("--continuous"), 1)
        self.assertIn("require the primary checkout on main; found agent/issue-14", self.stderr.getvalue())
        self.board_read.assert_called_once_with(7)
        self.execute.assert_not_called()

    def test_live_non_main_refused_before_board_or_active_process_checks(self):
        self.branch = "agent/issue-14"
        with patch.object(pilot, "refuse_active_work") as active:
            self.assertEqual(self.run_cli(), 1)
        self.assertIn("require the primary checkout on main", self.stderr.getvalue())
        self.board_read.assert_not_called()
        active.assert_not_called()

    def test_invalid_continuous_options_fail_before_board_reads(self):
        for args in (("--continuous", "--dry-run"), ("--continuous", "--expect-issue", "14"),
                     ("--poll-seconds", "1"), ("--continuous", "--poll-seconds", "0"),
                     ("--continuous", "--poll-seconds", "3601")):
            with self.subTest(args=args), self.assertRaises(SystemExit) as failure:
                self.run_cli(*args)
            self.assertEqual(failure.exception.code, 2)
        self.board_read.assert_not_called()
        self.execute.assert_not_called()

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
