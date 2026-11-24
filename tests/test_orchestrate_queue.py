"""Offline queue tests; no GitHub or OpenCode credentials are needed."""

import argparse
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from test_orchestrate import mod, sample_pr


NOW = "2026-11-24T21:18:52Z"
EARLIER = "2026-11-24T21:03:21Z"
MODEL = "openai/test-model#high"


def issue(number, body="Queue prerequisites: none", **extra):
    return {"number": number, "title": f"Task {number}", "body": body,
            "html_url": f"https://github.com/{mod.REPOSITORY}/issues/{number}",
            "state": "open", "assignees": [], "labels": [{"name": mod.QUEUE_LABEL}],
            "locked": False, "type": {"name": "Task"}, **extra}


def native_field(name, value):
    return {"issue_field_name": name, "data_type": "single_select",
            "single_select_option": {"name": value}}


def card(number, status="Ready", repo=mod.REPOSITORY, archived=False):
    return {"id": f"card-{number}", "isArchived": archived, "project": {"id": "project"},
            "content": {"__typename": "Issue", "number": number,
                        "repository": {"nameWithOwner": repo}},
            "fieldValueByName": {"name": status, "optionId": f"id-{status}"}}


def board_page(cards, cursor=None):
    return {"user": {"projectV2": {
        "id": "project", "title": "The Producer", "closed": False,
        "field": {"options": [{"name": s, "id": f"id-{s}"} for s in mod.STATUSES]},
        "items": {"nodes": cards, "pageInfo": {"hasNextPage": cursor is not None,
                                              "endCursor": cursor}},
    }}}


class FakeBoard(mod.ReadyBoard):
    """Fixture responses at the API boundary, including real claim verification."""

    def __init__(self, repo, number=7):
        super().__init__(repo, number)
        self.cards = {}
        self.issues = {}
        self.comments = {}
        self.fields = {}
        self.blocked_by = {}
        self.events = {}
        self.linked_prs = {}
        self.open_linked_prs = {}
        self.prs = []
        self.posts = []
        self.next_id = 100
        self.actor = mod.OWNER
        self.sync = True

    def add(self, number, *, priority="High", status="Ready", **detail):
        self.cards[number] = card(number, status)
        self.issues[number] = {**issue(number), **detail}
        self.fields[number] = [native_field("Priority", priority),
                               native_field("Workstream", "Infrastructure")]
        self.comments[number] = [{
            "id": number, "body": "/status Ready", "created_at": NOW, "updated_at": NOW,
            "user": {"login": mod.OWNER}}]

    def accept(self, number, *, closer=None, actor=mod.OWNER, reason="completed"):
        self.issues[number].update(state="closed", state_reason=reason, closed_at=NOW)
        self.events[number] = [{"__typename": "ClosedEvent", "stateReason": reason.upper(),
                                "createdAt": NOW, "actor": {"login": actor}, "closer": closer}]

    def graphql(self, query, **variables):
        if query == mod.BOARD_QUERY:
            return board_page(list(self.cards.values()))
        if query == mod.CARD_QUERY:
            return {"node": next((c for c in self.cards.values() if c["id"] == variables["id"]), None)}
        if query == mod.QUEUE_ISSUE_QUERY:
            n = variables["number"]
            return {"repository": {"issue": {
                "number": n, "lastEditedAt": self.issues[n].get("lastEditedAt"),
                "timelineItems": {"nodes": self.events.get(n, [])},
                "closedByPullRequestsReferences": {"totalCount": self.linked_prs.get(n, 0)},
                "openImplementation": {"totalCount": self.open_linked_prs.get(n, 0)},
            }}}
        raise AssertionError(query)

    def api(self, path, *, pages=False, body=None):
        if path == "user":
            return {"login": self.actor}
        path = path.removeprefix(f"repos/{mod.REPOSITORY}/")
        if path == "pulls?state=open&per_page=100" and pages:
            return self.prs
        _, n, *extra = path.split("/")
        number = int(n)
        if not extra:
            if number not in self.issues:
                raise mod.GitHubUnavailable("gh: Not Found (HTTP 404)")
            return self.issues[number].copy()
        if extra == ["issue-field-values"]:
            return self.fields[number]
        if extra == ["dependencies", "blocked_by?per_page=100"] and pages:
            return self.blocked_by.get(number, [])
        if extra == ["comments?per_page=100"] and pages:
            return self.comments[number]
        if extra == ["comments"] and body is not None:
            self.next_id += 1
            posted = {"id": self.next_id, "body": body, "created_at": NOW,
                      "updated_at": NOW, "user": {"login": mod.OWNER}}
            self.comments[number].append(posted)
            self.posts.append((number, body))
            if self.sync and body.startswith("/status "):
                self.cards[number] = card(number, body.removeprefix("/status "))
            return posted
        raise AssertionError(path)


class QueueTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name) / "The-Producer"
        self.repo.mkdir()
        self.board = FakeBoard(self.repo)
        self.args = argparse.Namespace(repo=str(self.repo), project=7, model=MODEL, dry_run=False,
                                       once=True, poll_seconds=60, timeout_minutes=1)
        self.enterContext(patch.object(mod, "registered_worktrees", return_value=[{"path": self.repo}]))
        self.output = self.enterContext(contextlib.redirect_stdout(io.StringIO()))

    def preflight_mocks(self):
        self.enterContext(patch.object(mod, "ReadyBoard", return_value=self.board))
        self.enterContext(patch.object(mod, "host_preflight",
                                      return_value=("2.4.1", "--agent --standalone --model")))
        def command(argv, *_args, **_kwargs):
            if argv[:2] == ["opencode", "models"]:
                return MODEL.split("#")[0]
            if argv[:2] == ["gh", "variable"]:
                return "7"
            if argv[0] == "git":
                return "a" * 40
            raise AssertionError(argv)
        return self.enterContext(patch.object(mod, "run_cmd", side_effect=command))

    def ordered_numbers(self):
        return [d["number"] for d, _ in mod.queue_snapshot(self.board)]

    def state(self, n):
        return json.loads((mod.run_home(self.repo) / f"issue-{n}/state.json").read_text())

    def test_projects_pagination_uses_real_status_and_identity(self):
        board = mod.ReadyBoard(self.repo, 7)
        first = board_page([card(1), card(2, "Blocked"), card(3, repo="other/repo")], "next")
        second = board_page([card(4), card(5, archived=True)])
        with patch.object(board, "graphql", side_effect=[first, second]) as graphql:
            self.assertEqual(board.ready(), {1: "card-1", 4: "card-4"})
        self.assertEqual([c.kwargs["after"] for c in graphql.call_args_list], [None, "next"])
        with patch.object(board, "graphql", side_effect=[first, board_page([], "next")]):
            with self.assertRaisesRegex(mod.GitHubUnavailable, "did not advance"):
                board.ready()

    def test_rest_pagination_and_graphql_partial_errors(self):
        board = mod.ReadyBoard(self.repo, 7)
        with patch.object(mod, "json_cmd", return_value=[[{"number": 5}], [{"number": 6}]]) as cli:
            self.assertEqual(board.api("repos/path?per_page=100", pages=True),
                             [{"number": 5}, {"number": 6}])
            self.assertIn("--slurp", cli.call_args.args[0])
        with patch.object(mod, "json_cmd", return_value={"data": {}, "errors": [{"message": "denied"}]}):
            with self.assertRaisesRegex(mod.GitHubUnavailable, "GraphQL"):
                board.ready()

    def test_unblocks_then_authoritative_priority_then_number(self):
        self.board.add(2, priority="Urgent")
        self.board.add(4, priority="Low")
        self.board.add(5, priority="Urgent", body="Queue prerequisites: #4")
        self.board.add(6, priority="High", body="**Priority:** Urgent\nQueue prerequisites: none")
        self.board.add(8, priority="High")
        self.board.add(9, priority="Medium")
        self.assertEqual(self.ordered_numbers(), [4, 2, 6, 8, 9])
        self.assertIn("WAIT #5", self.output.getvalue())
        self.board.accept(4)
        self.assertEqual(self.ordered_numbers(), [2, 5, 6, 8, 9])

    def test_owner_merge_and_completion_not_just_closed_or_done(self):
        self.board.add(4, body="Queue prerequisites: #7")
        self.board.add(7, status="Done")
        self.assertEqual(self.ordered_numbers(), [])
        for reason, actor in [("not_planned", mod.OWNER), ("completed", "collaborator")]:
            self.board.accept(7, reason=reason, actor=actor)
            self.assertEqual(self.ordered_numbers(), [])
        closer = {"__typename": "PullRequest", "state": "MERGED", "baseRefName": "different",
                  "repository": {"nameWithOwner": mod.REPOSITORY}, "mergedBy": {"login": mod.OWNER}}
        self.board.accept(7, closer=closer)
        self.assertEqual(self.ordered_numbers(), [])
        closer["baseRefName"] = "main"
        self.board.open_linked_prs[7] = 1
        self.assertEqual(self.ordered_numbers(), [])
        self.board.open_linked_prs[7] = 0
        self.assertEqual(self.ordered_numbers(), [4])

    def test_missing_ambiguous_or_contradictory_dependencies_fail_closed(self):
        self.board.add(1, body="Queue prerequisites: #9999")
        self.board.add(2, body="- **Prerequisites:** #1 and maybe #6")
        self.board.add(3)
        self.board.blocked_by[3] = [issue(1)]
        self.board.add(4, body="Queue prerequisites: #4")
        self.board.add(5, body="Queue prerequisites: #1\nQueue prerequisites: none")
        self.board.add(6, body="Queue prerequisites: #1")
        self.board.blocked_by[6] = [issue(1, html_url="https://github.com/other/repo/issues/1")]
        self.board.add(7, body="Queue prerequisites: none\n- **Prerequisites:** #1")
        self.assertEqual(self.ordered_numbers(), [])
        for text in ("WAIT #1", "SKIP #2", "SKIP #3", "SKIP #4", "SKIP #5", "SKIP #6", "SKIP #7"):
            self.assertIn(text, self.output.getvalue())

    def test_excludes_human_decision_missing_metadata_stale_auth_pr_and_local_runs(self):
        self.board.add(1, assignees=[{"login": mod.OWNER}])
        self.board.add(2, labels=[])
        self.board.add(3, type={"name": "Design Decision"})
        self.board.add(4, type=None)
        self.board.add(5, priority="P0")
        self.board.add(6)
        self.board.comments[6][0]["user"]["login"] = "someone"
        self.board.add(7, lastEditedAt=NOW)
        self.board.add(8)
        self.board.linked_prs[8] = 1
        self.board.add(9)
        self.board.prs.append({"body": None, "head": {"ref": "agent/issue-9-being-developed"}})
        self.board.add(10)
        (mod.run_home(self.repo) / "issue-10").mkdir(parents=True)
        self.board.add(11, state="closed")
        self.board.add(12)
        self.board.events[12] = [{"__typename": "ReopenedEvent", "createdAt": NOW}]
        self.board.add(13)
        self.board.fields[13].pop()
        self.board.add(14)
        self.board.comments[14][0]["updated_at"] = "2026-11-25T00:00:00Z"
        self.board.add(15)
        self.assertEqual(self.ordered_numbers(), [15])

    def test_queue_dry_run_reads_board_but_never_writes(self):
        tool = self.preflight_mocks()
        self.board.add(1)
        self.args.dry_run = True
        with patch.object(mod, "runner_lock") as lock, patch.object(mod, "run_agent") as launch:
            result = mod.main(["--repo", str(self.repo), "--queue", "--project", "7",
                               "--model", MODEL, "--dry-run"])
        self.assertEqual(result, 0)
        self.assertIn("eligible in order: #1", self.output.getvalue())
        lock.assert_not_called()
        launch.assert_not_called()
        self.assertFalse(mod.run_home(self.repo).exists())
        self.assertFalse(self.board.posts)
        self.assertTrue(all(c.args[0][0] != "git" for c in tool.call_args_list))

    def test_continuous_poll_notices_new_ready_then_resolved_prerequisite(self):
        self.preflight_mocks()
        self.args.once = False
        self.board.add(5, status="In Review")
        polls = []
        def sleep(seconds):
            polls.append(seconds)
            if len(polls) == 1:
                self.board.add(3, body="Queue prerequisites: #5")
            elif len(polls) == 2:
                self.board.accept(5)
            else:
                raise AssertionError("dispatch was expected")
        with patch.object(mod.time, "sleep", side_effect=sleep), \
             patch.object(mod, "dispatch_ready", return_value=130) as dispatch:
            self.assertEqual(mod.queue_mode(self.args), 130)
        self.assertEqual(polls, [60, 60])
        self.assertEqual(dispatch.call_args.args[3]["number"], 3)

    def test_success_uses_actual_shared_workflow_and_keeps_pr_unmerged(self):
        commands = self.preflight_mocks()
        self.board.add(1)
        with patch.object(mod, "verify_checkout"), patch.object(mod, "record_cleanup"), \
             patch.object(mod, "pr_details", return_value=sample_pr()), \
             patch.object(mod, "run_agent", side_effect=["Build done", "REVIEW_VERDICT: APPROVE"]) as agent:
            self.assertEqual(mod.queue_mode(self.args), 0)
        build, review = [call.args for call in agent.call_args_list]
        self.assertIn("build", build[0])
        self.assertIn("host runner owns Project status", build[0][-1])
        self.assertIn("producer-reviewer", review[0])
        self.assertNotEqual(build[1], review[1])
        self.assertEqual(self.board.posts, [(1, "/status In Progress"), (1, "/status In Review")])
        evidence = self.state(1)
        self.assertEqual(evidence["verified_status"], "In Review")
        self.assertEqual(evidence["last_verdict"], "APPROVE")
        self.assertEqual(evidence["head_sha"], sample_pr()["headRefOid"])
        self.assertEqual(evidence["pr"], sample_pr()["url"])
        self.assertFalse(any("merge" in c.args[0] for c in commands.call_args_list))

    def test_task_failure_blocks_then_unrelated_issue_runs(self):
        self.preflight_mocks()
        self.args.once = False
        self.board.add(1)
        self.board.add(2, body="Queue prerequisites: #1")
        self.board.add(3)
        with patch.object(mod, "verify_checkout"), \
             patch.object(mod, "run_agent", side_effect=[mod.Blocked("exited 3"), mod.Interrupted("signal")]) as agent:
            self.assertEqual(mod.queue_mode(self.args), 130)
        self.assertEqual(agent.call_count, 2)
        self.assertEqual(self.state(1)["phase"], "blocked")
        self.assertEqual(self.state(1)["verified_status"], "Blocked")
        self.assertEqual(self.state(1)["reason"], "exited 3")
        self.assertEqual(self.state(3)["phase"], "interrupted")
        self.assertEqual(self.state(3)["verified_status"], "Blocked")
        self.assertFalse((mod.run_home(self.repo) / "issue-2").exists())
        self.assertIn("WAIT #2", self.output.getvalue())
        # A manual Ready transition alone cannot resume this locally unresolved run.
        self.board.cards[1] = card(1)
        self.assertEqual(self.ordered_numbers(), [])
        self.assertIn("local run/worktree", self.output.getvalue())

    def test_claim_status_timeout_stops_queue_without_starting_any_agent(self):
        self.preflight_mocks()
        self.board.add(1)
        self.board.add(2)
        self.board.sync = False
        with patch.object(mod.time, "sleep"), patch.object(mod, "run_agent") as launch:
            with self.assertRaisesRegex(mod.GitHubUnavailable, "In Progress not verified"):
                mod.queue_mode(self.args)
        launch.assert_not_called()
        self.assertEqual(self.state(1)["phase"], "status_unverified")
        self.assertFalse((mod.run_home(self.repo) / "issue-2").exists())

    def test_rechecks_claim_against_same_scope_before_build(self):
        self.preflight_mocks()
        self.board.add(1)
        def change_issue(*_args, **_kwargs):
            self.board.issues[1]["assignees"] = [{"login": mod.OWNER}]
        with patch.object(mod, "verify_checkout", side_effect=change_issue), \
             patch.object(mod, "run_agent") as launch:
            with self.assertRaisesRegex(mod.GitHubUnavailable, "could not be revalidated"):
                mod.queue_mode(self.args)
        launch.assert_not_called()
        self.assertEqual(self.board.posts, [(1, "/status In Progress")])
        self.assertEqual(self.state(1)["phase"], "status_unverified")

    def test_unverified_blocked_handoff_stops_unrelated_dispatch(self):
        self.preflight_mocks()
        self.args.once = False
        self.board.add(1)
        self.board.add(2)

        def build_failed(*_args):
            self.board.sync = False
            raise mod.Blocked("No implementation artifact")

        with patch.object(mod, "verify_checkout"), patch.object(mod.time, "sleep"), \
             patch.object(mod, "run_agent", side_effect=build_failed) as launch:
            with self.assertRaisesRegex(mod.GitHubUnavailable, "Blocked not verified"):
                mod.queue_mode(self.args)
        launch.assert_called_once()
        state = self.state(1)
        self.assertEqual(state["phase"], "blocked")
        self.assertEqual(state["verified_status"], "In Progress")
        self.assertIn("Blocked not verified", state["status_error"])
        self.assertFalse((mod.run_home(self.repo) / "issue-2").exists())

    def test_api_and_auth_failures_do_not_dispatch(self):
        self.preflight_mocks()
        self.board.actor = "different-user"
        with self.assertRaisesRegex(mod.GitHubUnavailable, "authentication"):
            mod.queue_mode(self.args)
        self.board.actor = mod.OWNER
        with patch.object(self.board, "ready", side_effect=mod.GitHubUnavailable("GraphQL down")):
            with self.assertRaisesRegex(mod.GitHubUnavailable, "GraphQL down"):
                mod.queue_mode(self.args)
        self.assertFalse(self.board.posts)

    def test_cli_idle_interrupt_restores_signal_and_exits_without_writes(self):
        self.preflight_mocks()
        sigterm = mod.signal.getsignal(mod.signal.SIGTERM)
        with patch.object(mod, "runner_lock", side_effect=contextlib.nullcontext), \
             patch.object(mod.time, "sleep", side_effect=KeyboardInterrupt) as sleep:
            result = mod.main(["--repo", str(self.repo), "--queue", "--project", "7",
                               "--model", MODEL])
        self.assertEqual(result, 130)
        sleep.assert_called_once_with(60)
        self.assertEqual(mod.signal.getsignal(mod.signal.SIGTERM), sigterm)
        self.assertFalse(mod.run_home(self.repo).exists())

    def test_writer_lock_rejects_overlap_then_releases(self):
        with patch.object(Path, "home", return_value=self.repo):
            with mod.runner_lock():
                with self.assertRaisesRegex(mod.Blocked, "Another runner"):
                    with mod.runner_lock():
                        self.fail("overlapping writer")
            with mod.runner_lock():
                pass

    def test_real_interrupted_child_is_terminated_and_log_retained(self):
        transcript = self.repo / "child.log"
        script = (
            "import os, signal, time\n"
            "print('child started', flush=True)\n"
            "time.sleep(0.05)\n"
            "os.kill(os.getppid(), signal.SIGINT)\n"
            "time.sleep(10)\n"
        )
        with self.assertRaisesRegex(mod.Interrupted, "Agent interrupted"):
            mod.run_agent([sys.executable, "-c", script], self.repo, transcript, 5)
        self.assertIn("child started", transcript.read_text())


if __name__ == "__main__":
    unittest.main()
