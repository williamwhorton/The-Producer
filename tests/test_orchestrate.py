import argparse
import importlib.util
from pathlib import Path
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


class FlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / 'The-Producer'
        self.repo.mkdir()
        self.args = argparse.Namespace(issue=14, repo=str(self.repo), model='openai/gpt-test#high',
                                       dry_run=False, approve_issue=True, timeout_minutes=2)
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
             patch.object(mod, 'run_agent', side_effect=agent):
            self.assertEqual(mod.orchestrate(self.args), 0)
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

if __name__ == '__main__':
    unittest.main()
