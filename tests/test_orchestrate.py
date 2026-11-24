import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import sys
import unittest
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[1] / 'tools' / 'orchestrate.py'
spec = importlib.util.spec_from_file_location('orchestrate', MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def sample_pr(sha='a' * 40):
    return {
        'number': 90, 'url': 'https://github.com/williamwhorton/The-Producer/pull/90',
        'state': 'OPEN', 'isDraft': False, 'baseRefName': 'main',
        'headRefName': 'agent/issue-14-test', 'headRefOid': sha,
        'body': ('## Evidence\nAutomated tests and GUI walkthrough\n\nCloses #14\n\n'
                 '## Human Testing\n1. Run `godot --path spikes/issue-4-3d`. '
                 'Expected: the 3D house launches and markers are visible.\n'),
        'files': [{'path': 'spikes/issue-4-3d/main.tscn'}],
    }


class ParserTests(unittest.TestCase):
    def test_model_rejects_non_openai_and_malformed(self):
        for name in ('lmstudio/qwen', 'openrouter/gpt-6', 'openai/', 'openai/gpt 6', 'openai/gpt#h/i'):
            with self.subTest(name=name), self.assertRaises(mod.Blocked):
                mod.require_model(name)
        self.assertEqual(mod.require_model('openai/gpt-6.2-sol#high'), 'openai/gpt-6.2-sol#high')

    def test_closing_reference(self):
        self.assertTrue(mod.closes_issue('Closes #14', 14))
        self.assertTrue(mod.closes_issue('Fixes williamwhorton/The-Producer#14', 14))
        self.assertFalse(mod.closes_issue('Refs #14', 14))
        self.assertFalse(mod.closes_issue('Closes #140', 14))
        self.assertFalse(mod.closes_issue('Closes #13', 14))

    def test_explicit_verdict_required(self):
        self.assertEqual(mod.review_verdict('Checks passed\nREVIEW_VERDICT: APPROVE\n'), 'APPROVE')
        for value in ('Approve — looks good', 'REVIEW_VERDICT: APPROVE\nREVIEW_VERDICT: REQUEST_CHANGES', ''):
            with self.subTest(value=value), self.assertRaises(mod.Blocked):
                mod.review_verdict(value)

    def test_human_testing_required_and_actionable(self):
        valid = ('## Human Testing\n1. Run `godot --path spikes/issue-4-3d`. '
                 'Expected: the house launches with all three markers visible.\n')
        mod.validate_human_testing(valid)
        for body in (
            '## Evidence\nGodot passed.',
            '## Human Testing\nTODO add steps later',
            '## Human Testing\n1. Run <exact command>. Expected: <specific result>.',
            '## Human Testing\n1. Check the thing.',
            '## Human Testing\n1. Open the 3D application and look around at all rooms and markers.',
            '## Human Testing\nThe reviewer said it works and no manual check is needed.',
        ):
            with self.subTest(body=body), self.assertRaises(mod.Blocked):
                mod.validate_human_testing(body)

    def test_pr_requires_correct_commit_scope_and_evidence(self):
        p = sample_pr()
        with patch.object(mod, 'json_cmd', side_effect=[[{'number': 90}], p]):
            self.assertEqual(mod.pr_details(p['headRefName'], 14, Path('/tmp'))['number'], 90)
        for replacement in ({'body': 'Refs #14\n## Evidence'}, {'isDraft': True},
                            {'files': []}, {'headRefOid': 'bad'},
                            {'baseRefName': 'other'}, {'body': 'Closes #14'},
                            {'body': '## Evidence\nTested.\nCloses #14'}):
            broken = {**p, **replacement}
            with self.subTest(replacement=replacement), patch.object(mod, 'json_cmd', side_effect=[[{'number': 90}], broken]):
                with self.assertRaises(mod.Blocked):
                    mod.pr_details(p['headRefName'], 14, Path('/tmp'))

    def test_subprocess_output_is_logged_and_exit_failures_block(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            good = folder / 'good.log'
            output = mod.run_agent([sys.executable, '-c', 'print("child is alive")'],
                                   folder, good, 5)
            self.assertIn('child is alive', output)
            self.assertIn('child is alive', good.read_text())
            bad = folder / 'bad.log'
            with self.assertRaisesRegex(mod.Blocked, 'exited 3'):
                mod.run_agent([sys.executable, '-c', 'import sys; sys.exit(3)'],
                              folder, bad, 5)

    def test_open_issue_required(self):
        for state in ('CLOSED', 'MERGED'):
            with patch.object(mod, 'json_cmd', return_value={'number': 14, 'state': state, 'body': 'requirements'}):
                with self.assertRaises(mod.Blocked):
                    mod.issue_details(14, Path('/tmp'))



class StartupIdentityTests(unittest.TestCase):
    def test_agent_subprocess_replaces_stale_inherited_pwd(self):
        with tempfile.TemporaryDirectory() as temp:
            child = Path(temp) / "target-worktree"
            child.mkdir()
            log = Path(temp) / "agent.log"
            script = ("import json, os; "
                      "print(json.dumps({'cwd': os.getcwd(), 'PWD': os.environ.get('PWD')}))")
            with patch.dict(os.environ, {"PWD": str(Path(temp) / "main")}):
                transcript = mod.run_agent([sys.executable, "-c", script], child, log, 10)
            result = json.loads(transcript.strip())
            self.assertEqual(result, {"cwd": str(child), "PWD": str(child)})
            self.assertEqual(os.environ.get("PWD") == str(child), False)

    def test_checkout_gate_rejects_main_and_accepts_worktree(self):
        with tempfile.TemporaryDirectory() as temp:
            main = Path(temp) / "main"
            child = Path(temp) / "issue-worktree"
            main.mkdir()
            def git(*args, cwd=main):
                return subprocess.run(["git", *args], cwd=cwd, text=True,
                                      capture_output=True, check=True).stdout.strip()
            git("init", "-b", "main")
            git("config", "user.name", "Unit Test")
            git("config", "user.email", "test@example.invalid")
            (main / "README.md").write_text("fixture\n")
            git("add", "README.md")
            git("commit", "-m", "base")
            git("worktree", "add", "-b", "agent/issue-15-test", str(child))
            sha = git("rev-parse", "HEAD", cwd=child)
            mod.verify_checkout(child, expected_branch="agent/issue-15-test")
            with self.assertRaisesRegex(mod.Blocked, "branch mismatch"):
                mod.verify_checkout(child, expected_branch="main")
            with self.assertRaisesRegex(mod.Blocked, "checkout mismatch"):
                mod.verify_checkout(main / "other", expected_branch="main")
            git("checkout", "--detach", cwd=child)
            mod.verify_checkout(child, expected_sha=sha)
            with self.assertRaisesRegex(mod.Blocked, "SHA mismatch"):
                mod.verify_checkout(child, expected_sha="b" * 40)
            with self.assertRaisesRegex(mod.Blocked, "must be detached"):
                mod.verify_checkout(main, expected_sha=sha)

    def test_archive_blocked_run_preserves_logs(self):
        with tempfile.TemporaryDirectory() as temp:
            main = Path(temp) / "The-Producer"
            main.mkdir()
            state_dir = main.parent / ".The-Producer-agent-runs" / "issue-15"
            state_dir.mkdir(parents=True)
            (state_dir / "state.json").write_text(json.dumps(
                {"issue": 15, "phase": "blocked", "development_worktree": str(main.parent / "old")}))
            (state_dir / "developer-0.log").write_text("old failure evidence")
            with patch.object(mod, "cleanup_worktrees", return_value=(0, [])), \
                 patch.object(mod, "registered_worktrees", return_value=[]):
                history = mod.archive_blocked_run(main, 15, state_dir)
            self.assertFalse(state_dir.exists())
            self.assertTrue(history.name.startswith("issue-15-history-"))
            self.assertEqual((history / "developer-0.log").read_text(), "old failure evidence")

    def test_archive_rejects_unverified_or_active_previous_run(self):
        with tempfile.TemporaryDirectory() as temp:
            main = Path(temp) / "The-Producer"
            main.mkdir()
            state_dir = main.parent / ".The-Producer-agent-runs" / "issue-15"
            state_dir.mkdir(parents=True)
            (state_dir / "state.json").write_text(json.dumps(
                {"issue": 15, "phase": "blocked", "pr": "https://github.com/example/pull/1"}))
            with self.assertRaisesRegex(mod.Blocked, "no PR"):
                mod.archive_blocked_run(main, 15, state_dir)
            (state_dir / "state.json").write_text(json.dumps(
                {"issue": 15, "phase": "blocked"}))
            with patch.object(mod, "cleanup_worktrees",
                              return_value=(0, ["worktree busy"])):
                with self.assertRaisesRegex(mod.Blocked, "could not be cleaned"):
                    mod.archive_blocked_run(main, 15, state_dir)
            self.assertTrue(state_dir.exists())


class FlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / 'The-Producer'
        self.repo.mkdir()
        self.args = argparse.Namespace(issue=14, repo=str(self.repo), model='openai/gpt-test#high',
                                       dry_run=False, approve_issue=True, retry_blocked=False,
                                       timeout_minutes=2)
        self.issue = {'number': 14, 'title': '3D prototype', 'url': 'https://github.com/williamwhorton/The-Producer/issues/14',
                      'state': 'OPEN', 'body': 'acceptance criteria'}

    def test_requires_explicit_issue_approval(self):
        self.args.approve_issue = False
        with patch.object(mod, 'preflight', return_value=self.issue):
            with self.assertRaisesRegex(mod.Blocked, 'approve-issue'):
                mod.orchestrate(self.args)
        self.assertFalse((self.repo.parent / '.The-Producer-agent-runs').exists())

    def test_dry_run_creates_nothing(self):
        self.args.dry_run = True
        with patch.object(mod, 'preflight', return_value=self.issue):
            self.assertEqual(mod.orchestrate(self.args), 0)
        self.assertFalse((self.repo.parent / '.The-Producer-agent-runs').exists())

    def test_success_developer_then_fresh_reviewer(self):
        calls = []
        sha = 'a' * 40
        def cmd(argv, cwd, **kwargs):
            calls.append(('git', argv, cwd))
            if argv[:3] == ['git', 'rev-parse', 'FETCH_HEAD']:
                return sha
            return sha
        def pr(branch, issue, cwd):
            return {**sample_pr(), 'headRefName': branch}
        def agent(argv, cwd, logfile, timeout):
            calls.append(('agent', argv, cwd))
            return 'REVIEW_VERDICT: APPROVE' if 'producer-reviewer' in argv else 'Developer done'
        with patch.object(mod, 'preflight', return_value=self.issue), \
             patch.object(mod, 'run_cmd', side_effect=cmd), \
             patch.object(mod, 'pr_details', side_effect=pr), \
             patch.object(mod, 'verify_checkout') as verify, \
             patch.object(mod, 'run_agent', side_effect=agent):
            self.assertEqual(mod.orchestrate(self.args), 0)
            self.assertEqual(verify.call_count, 3)
        state = self.repo.parent / '.The-Producer-agent-runs/issue-14/state.json'
        self.assertIn('ready_for_human_acceptance', state.read_text())
        agents = [c for c in calls if c[0] == 'agent']
        self.assertEqual(len(agents), 2)
        self.assertIn('build', agents[0][1])
        self.assertIn('producer-reviewer', agents[1][1])
        self.assertNotEqual(agents[0][2], agents[1][2])
        self.assertTrue(any(a[:3] == ['git', 'worktree', 'add'] for _, a, _ in calls if a[0] == 'git'))

    def test_review_correction_cycle_is_bounded(self):
        calls = []
        original = 'a' * 40
        changed = 'b' * 40
        def pr(branch, issue, cwd):
            # After corrective dev run updated sha is b
            sha = changed if len([x for x in calls if x == 'dev']) > 1 else original
            return {**sample_pr(sha), 'headRefName': branch}
        def cmd(argv, cwd, **kwargs):
            if argv[:3] == ['git', 'rev-parse', 'FETCH_HEAD']:
                return changed if len([x for x in calls if x == 'dev']) > 1 else original
            return ''
        def agent(argv, cwd, log, timeout):
            if 'producer-reviewer' in argv:
                calls.append('review')
                return 'REVIEW_VERDICT: REQUEST_CHANGES'
            calls.append('dev')
            return 'Implemented'
        with patch.object(mod, 'preflight', return_value=self.issue), \
             patch.object(mod, 'run_cmd', side_effect=cmd), \
             patch.object(mod, 'pr_details', side_effect=pr), \
             patch.object(mod, 'verify_checkout'), \
             patch.object(mod, 'run_agent', side_effect=agent):
            with self.assertRaisesRegex(mod.Blocked, 'still requests changes'):
                mod.orchestrate(self.args)
        self.assertEqual(calls, ['dev', 'review', 'dev', 'review'])
        self.assertIn('blocked', (self.repo.parent / '.The-Producer-agent-runs/issue-14/state.json').read_text())

    def test_refuse_duplicate_run(self):
        folder = self.repo.parent / '.The-Producer-agent-runs/issue-14'
        folder.mkdir(parents=True)
        with patch.object(mod, 'preflight', return_value=self.issue):
            with self.assertRaisesRegex(mod.Blocked, 'Existing run'):
                mod.orchestrate(self.args)


class CleanupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "The-Producer"
        self.repo.mkdir()
        self.agent = Path(self.temp.name) / "The-Producer-agent-14-test"
        self.agent.mkdir()
        self.record = {"path": self.agent, "branch": "refs/heads/agent/issue-14-test",
                       "HEAD": "a" * 40}

    def test_worktree_parser(self):
        raw = (f"worktree {self.repo}\nHEAD {'0'*40}\nbranch refs/heads/main\n\n"
               f"worktree {self.agent}\nHEAD {'a'*40}\n"
               "branch refs/heads/agent/issue-14-test\n")
        with patch.object(mod, "run_cmd", return_value=raw):
            result = mod.registered_worktrees(self.repo)
        self.assertEqual([x["path"] for x in result], [self.repo, self.agent])

    def test_clean_pushed_branch_is_removed_without_force(self):
        commands = []
        def cmd(argv, cwd, **kwargs):
            commands.append(argv)
            return "a" * 40 if "rev-parse" in argv else ""
        with patch.object(mod, "registered_worktrees", return_value=[self.record]), \
             patch.object(mod, "worktree_in_use", return_value=False), \
             patch.object(mod, "run_cmd", side_effect=cmd), \
             patch.object(mod, "pr_preserves_head", return_value=True):
            count, skipped = mod.cleanup_worktrees(self.repo)
        self.assertEqual((count, skipped), (1, []))
        self.assertIn(["git", "worktree", "remove", str(self.agent)], commands)
        self.assertFalse(any("--force" in c for c in commands))

    def test_busy_worktree_remains_intact(self):
        with patch.object(mod, "registered_worktrees", return_value=[self.record]), \
             patch.object(mod, "worktree_in_use", return_value=True), \
             patch.object(mod, "run_cmd") as command:
            count, skipped = mod.cleanup_worktrees(self.repo)
        self.assertEqual(count, 0)
        self.assertIn("running process", skipped[0])
        command.assert_not_called()

    def test_uncommitted_changes_are_preserved(self):
        def cmd(argv, cwd, **kwargs):
            return " M main.gd" if "status" in argv else ""
        with patch.object(mod, "registered_worktrees", return_value=[self.record]), \
             patch.object(mod, "worktree_in_use", return_value=False), \
             patch.object(mod, "run_cmd", side_effect=cmd):
            count, skipped = mod.cleanup_worktrees(self.repo)
        self.assertEqual(count, 0)
        self.assertIn("uncommitted", skipped[0])

    def test_unpushed_commits_are_preserved(self):
        def cmd(argv, cwd, **kwargs):
            return "a" * 40 if "rev-parse" in argv else ""
        with patch.object(mod, "registered_worktrees", return_value=[self.record]), \
             patch.object(mod, "worktree_in_use", return_value=False), \
             patch.object(mod, "run_cmd", side_effect=cmd), \
             patch.object(mod, "pr_preserves_head", return_value=False), \
             patch.object(mod.subprocess, "run") as sub:
            sub.return_value.returncode = 1
            count, skipped = mod.cleanup_worktrees(self.repo)
        self.assertEqual(count, 0)
        self.assertIn("not verified", skipped[0])

    def test_detached_review_requires_matching_recorded_commit(self):
        review = self.repo.parent / "The-Producer-review-14-test"
        review.mkdir()
        state_dir = self.repo.parent / ".The-Producer-agent-runs" / "issue-14"
        state_dir.mkdir(parents=True)
        (state_dir / "state.json").write_text(
            '{"issue":14,"review_worktree":"' + str(review) +
            '","head_sha":"' + "b" * 40 + '"}')
        record = {"path": review, "HEAD": "a" * 40, "detached": ""}
        def cmd(argv, cwd, **kwargs):
            return "a" * 40 if "rev-parse" in argv else ""
        with patch.object(mod, "registered_worktrees", return_value=[record]), \
             patch.object(mod, "worktree_in_use", return_value=False), \
             patch.object(mod, "run_cmd", side_effect=cmd):
            count, skipped = mod.cleanup_worktrees(self.repo)
        self.assertEqual(count, 0)
        self.assertIn("detached review commit", skipped[0])

    def test_legacy_requires_merged_pr(self):
        legacy = self.repo.parent / "The-Producer-issue-13-followup"
        legacy.mkdir()
        record = {"path": legacy, "HEAD": "a" * 40,
                  "branch": "refs/heads/spike/issue-13-isometric-followup"}
        def cmd(argv, cwd, **kwargs):
            return "a" * 40 if "rev-parse" in argv else ""
        with patch.object(mod, "registered_worktrees", return_value=[record]), \
             patch.object(mod, "worktree_in_use", return_value=False), \
             patch.object(mod, "run_cmd", side_effect=cmd), \
             patch.object(mod, "pr_preserves_head", return_value=True) as proof:
            count, skipped = mod.cleanup_worktrees(self.repo)
        self.assertEqual((count, skipped), (1, []))
        self.assertTrue(proof.call_args.args[3])


if __name__ == '__main__':
    unittest.main()
