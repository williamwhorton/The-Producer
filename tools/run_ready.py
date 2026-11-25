#!/usr/bin/env python3
"""On the trusted host, run at most one eligible Developer assignment."""

import argparse
from contextlib import contextmanager
import fcntl
import json
from pathlib import Path
import re
import sys
import time

if __name__ == "__main__":
    # A read-only CLI preview should not create local import cache files.
    sys.dont_write_bytecode = True

if __package__:
    from . import orchestrate as runner, read_ready as board, ready_selection as selector
    from .sync_project_status import STATUSES
else:
    import orchestrate as runner
    import read_ready as board
    import ready_selection as selector
    from sync_project_status import STATUSES


class BoardError(runner.Blocked):
    """Uncertain or withdrawn board authorization: do not write another status."""


class Project:
    def __init__(self, number):
        self.number = number

    def status(self, issue):
        try:
            _, _, cards = board.project_issues(self.number, status_names=STATUSES)
        except (board.ReadError, AttributeError, KeyError, TypeError) as error:
            raise BoardError(f"Could not verify Project status for #{issue}: {error}") from error
        matches = [name for name, numbers in cards.items() for n in numbers if n == issue]
        if len(matches) != 1:
            raise BoardError(f"#{issue}: expected one unarchived Project card with a known Status")
        return matches[0]

    def post(self, issue, status):
        # Same owner-only issue comment consumed by project-status-sync.yml.
        body = f"/status {status}"
        comment = board.gh_json(
            f"#{issue} {body}", "--method", "POST",
            f"repos/{board.REPOSITORY}/issues/{issue}/comments", "-f", f"body={body}",
        )
        if not selector.owner_login(comment.get("user")) or comment.get("body") != body:
            raise BoardError(f"#{issue}: could not verify the posted owner command {body!r}")


def require_status(project, issue, expected, *, pending=None):
    # Bounded verification of one transition, not polling for queue work.
    deadline = time.monotonic() + 120
    while True:
        current = project.status(issue)
        if current == expected:
            print(f"Verified Project card: #{issue} is {expected}.", flush=True)
            return
        if pending is None or current != pending:
            raise BoardError(f"#{issue}: Project card is {current}, not {expected}; stop without another status write")
        if time.monotonic() >= deadline:
            raise BoardError(f"#{issue}: Project card stayed {current}; expected {expected}. "
                             "Inspect Sync GitHub Project Status in Actions before taking further action.")
        time.sleep(3)


@contextmanager
def pilot_lock(run_home):
    run_home.mkdir(parents=True, exist_ok=True)
    # Leave the inode in place: unlinking it could allow two owners of the lock.
    with (run_home / "ready-pilot.lock").open("a") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise runner.Blocked("Another Ready pilot holds the local lock.") from error
        yield


def refuse_active_work(repo, run_home):
    terminal = {"blocked", "changes_requested", "ready_for_human_acceptance"}
    for entry in run_home.iterdir():
        if not re.fullmatch(r"issue-\d+(?:-review-pr-.+)?", entry.name):
            continue
        try:
            state = json.loads((entry / "state.json").read_text())
        except (OSError, ValueError) as error:
            raise runner.Blocked(f"Cannot verify whether {entry} is active; inspect its local state.") from error
        if not isinstance(state, dict) or state.get("phase") not in terminal:
            raise runner.Blocked(f"Active or unfinished run at {entry}; inspect it before running the pilot.")

    for tree in runner.registered_worktrees(repo):
        path = tree["path"]
        branch = tree.get("branch", "").removeprefix("refs/heads/")
        named = path.parent == repo.parent and re.fullmatch(
            rf"{re.escape(repo.name)}-(?:agent|review|issue)-\d+(?:-.+)?", path.name)
        if (named or selector.branch_issue(branch) is not None) and runner.worktree_in_use(path):
            raise runner.Blocked(f"An active process is using {path}; do not start parallel work.")


def run_one(args, project, recheck, execute):
    issue = args.issue
    claimed = False

    def claim(number):
        nonlocal claimed
        result = recheck(number)
        if result.eligible != [number]:
            print("\n".join(result.lines), file=sys.stderr)
            raise BoardError(f"#{number} is no longer eligible; no replacement assignment will be started.")
        require_status(project, number, "Ready")
        project.post(number, "In Progress")
        require_status(project, number, "In Progress", pending="Ready")
        claimed = True

    def verify_status(number, expected):
        # The PR-open event owns In Review. Never replay a status command if
        # that event is lost; leave the artifacts for the owner to reconcile.
        require_status(project, number, expected,
                       pending="In Progress" if expected == "In Review" else None)

    try:
        result = execute(args, claim=claim, verify_status=verify_status)
        if result != 0:
            raise runner.Blocked(f"Single-issue runner exited {result}; inspect its state and transcripts.")
    except BoardError:
        raise
    except (runner.Blocked, OSError) as error:
        if not claimed:
            raise
        print(f"Runner failed for #{issue}: {error}. Inspect retained state/logs, PR and worktrees; do not retry automatically.",
              file=sys.stderr)
        current = project.status(issue)
        if current == "In Progress":
            project.post(issue, "Blocked")
            require_status(project, issue, "Blocked", pending="In Progress")
        else:
            print(f"#{issue}: preserving Project status {current}; owner triage required.", file=sys.stderr)
        return 1
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="explicit OpenAI model ID from OpenCode")
    parser.add_argument("--dry-run", action="store_true", help="show the intended issue without writes or agents")
    parser.add_argument("--expect-issue", type=int, help="refuse a different issue than the one you prepared")
    args = parser.parse_args(argv)
    try:
        project_number = board.configured_project()
    except ValueError as error:
        parser.error(str(error))

    def select_issues(numbers):
        return selector.select(numbers, board.ready_issue, board.gh_json)

    try:
        model = runner.require_model(args.model)
        repo = Path.cwd()
        trees = runner.registered_worktrees(repo)
        if not trees or trees[0]["path"] != repo:
            raise runner.Blocked("Run from the primary The-Producer repository root.")
        origin = runner.run_cmd(["git", "remote", "get-url", "origin"], repo)
        if not re.search(rf"github\.com[:/]{re.escape(board.REPOSITORY)}(?:\.git)?$", origin, re.I):
            raise runner.Blocked(f"Origin is not {board.REPOSITORY}.")
        _, url, cards = board.project_issues(project_number)
        result = select_issues(cards["Ready"])
        if not result.eligible:
            print("\n".join(result.lines))
            return 0
        issue = result.eligible[0]
        if args.expect_issue is not None and args.expect_issue != issue:
            raise runner.Blocked(f"Expected #{args.expect_issue}, but selector recommends #{issue}.")
        print(f"Project: {url}", flush=True)
        print("\n".join(result.lines), flush=True)
        if args.dry_run:
            print(f"DRY RUN: would claim #{issue} for model {model}. No writes or agent sessions.")
            return 0

        run_home = repo.parent / f".{repo.name}-agent-runs"
        with pilot_lock(run_home):
            if not selector.owner_login(board.gh_json("GitHub pilot identity", "--method", "GET", "user")):
                raise runner.Blocked(f"Status commands require gh authentication as {board.OWNER}.")
            refuse_active_work(repo, run_home)
            invocation = argparse.Namespace(repo=str(repo), issue=issue, model=model, approve_issue=True,
                                            retry_blocked=False, dry_run=False, timeout_minutes=60)
            return run_one(invocation, Project(project_number),
                           lambda n: select_issues([n]), runner.orchestrate)
    except (runner.Blocked, board.ReadError, selector.SelectionError, OSError) as error:
        print(f"run_ready: {error}", file=sys.stderr)
        return 1
    except (AttributeError, KeyError, TypeError):
        print("run_ready: unexpected GitHub API or local state shape; inspect before proceeding", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("run_ready: interrupted; inspect the Project card and retained artifacts before proceeding",
              file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
