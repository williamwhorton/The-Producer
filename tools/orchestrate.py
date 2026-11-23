#!/usr/bin/env python3
"""Supervised, single-issue OpenCode Build -> independent Reviewer pilot.

Only the explicitly specified issue may run. No merging, forced cleanup, permission auto-approval, model fallback
or paid API selection.
"""

from __future__ import annotations

import argparse
import codecs
import datetime as dt
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import signal
import subprocess
import sys
import threading

REPOSITORY = "williamwhorton/The-Producer"
BASE_BRANCH = "main"
VERDICTS = ("APPROVE", "REQUEST_CHANGES", "UNABLE_TO_VERIFY")


class Blocked(RuntimeError):
    """A fail-closed, human-actionable workflow blocker."""


def run_cmd(argv: list[str], cwd: Path, *, timeout: int = 40) -> str:
    try:
        result = subprocess.run(argv, cwd=cwd, capture_output=True, text=True,
                                timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Blocked(f"Command unavailable or timed out: {argv[0]} ({exc})") from exc
    if result.returncode:
        excerpt = (result.stderr or result.stdout).strip()[-900:]
        raise Blocked(f"{argv[0]} failed (exit {result.returncode}): {excerpt}")
    return result.stdout.strip()


def json_cmd(argv: list[str], cwd: Path) -> object:
    raw = run_cmd(argv, cwd)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise Blocked(f"Unexpected JSON from {argv[0]}: {exc}") from exc


def require_model(value: str) -> str:
    # Directly invoking OpenAI by ID avoids accidental LM Studio/paid third-party
    # provider selection. It cannot, by itself, prove the method of OpenAI billing.
    if not re.fullmatch(r"openai/[A-Za-z0-9._-]+(?:#[A-Za-z0-9._-]+)?", value):
        raise Blocked("Use an explicit OpenAI model ID such as openai/<model>#high; "
                      "verify the exact ID in OpenCode first.")
    return value


def issue_details(issue: int, cwd: Path) -> dict:
    data = json_cmd(["gh", "issue", "view", str(issue), "--repo", REPOSITORY,
                     "--json", "number,title,state,body,url"], cwd)
    if not isinstance(data, dict) or data.get("number") != issue:
        raise Blocked("Fetched issue number does not match the assigned issue.")
    if data.get("state") != "OPEN":
        raise Blocked(f"Issue #{issue} is not open; do not reopen or duplicate work automatically.")
    if not (data.get("body") or "").strip():
        raise Blocked(f"Issue #{issue} has no requirements body; cannot authorize work.")
    return data


def closes_issue(text: str, issue: int) -> bool:
    return bool(re.search(rf"(?i)\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+(?:{re.escape(REPOSITORY)}#|#){issue}\b", text))


def existing_prs(issue: int, cwd: Path) -> None:
    items = json_cmd(["gh", "pr", "list", "--repo", REPOSITORY, "--state", "open",
                      "--limit", "200", "--json", "number,body,headRefName"], cwd)
    if not isinstance(items, list):
        raise Blocked("Cannot enumerate existing PRs.")
    for pr in items:
        if closes_issue(pr.get("body") or "", issue):
            raise Blocked(f"Issue #{issue} already has open PR #{pr['number']}; "
                          "review it rather than creating duplicate work.")


def validate_human_testing(body: str) -> None:
    """Require actionable human acceptance steps in every runner-generated PR.

    This validates presence and a minimal structure, not quality or truthfulness.
    """
    match = re.search(
        r"(?ims)^#{1,4}\s+Human Testing(?: Instructions)?\s*$\n(.*?)(?=^#{1,4}\s|\Z)",
        body,
    )
    if not match:
        raise Blocked("PR body must contain a ## Human Testing section with reproducible steps.")
    section = match.group(1).strip()
    if (len(section) < 45
            or not re.search(r"(?m)^\s*(?:[-*]|\d+[.)])\s+\S", section)
            or not re.search(r"(?i)\b(?:expected|should|verify|confirm)\b", section)
            or re.search(r"(?i)<[^>]+>|REPLACE WITH|\bTODO\b|\bTBD\b", section)):
        raise Blocked("Human Testing must contain non-placeholder, actionable steps "
                      "and expected outcomes; include exact commands where applicable.")


def pr_details(branch: str, issue: int, cwd: Path) -> dict:
    matches = json_cmd(["gh", "pr", "list", "--repo", REPOSITORY, "--state", "open",
                        "--head", branch, "--json", "number"], cwd)
    if not isinstance(matches, list) or len(matches) != 1:
        raise Blocked("Expected exactly one open PR for the issue worktree branch.")
    pr = json_cmd(["gh", "pr", "view", str(matches[0]["number"]), "--repo", REPOSITORY,
                   "--json", "number,url,state,isDraft,baseRefName,headRefName,headRefOid,body,files"], cwd)
    if not isinstance(pr, dict):
        raise Blocked("Invalid PR payload.")
    if (pr.get("state") != "OPEN" or pr.get("isDraft") or
            pr.get("baseRefName") != BASE_BRANCH or pr.get("headRefName") != branch):
        raise Blocked("PR is draft, closed, targets another base, or has the wrong head branch.")
    if not re.fullmatch(r"[0-9a-f]{40}", pr.get("headRefOid") or ""):
        raise Blocked("PR lacks a valid head commit SHA.")
    if not closes_issue(pr.get("body") or "", issue):
        raise Blocked(f"PR must explicitly include 'Closes #{issue}' in its body.")
    if not pr.get("files"):
        raise Blocked("PR has no changed files; no deliverable exists to review.")
    if not re.search(r"(?im)^#{1,4}\s*(?:evidence|verification|test(?:s| results)?)\b", pr.get("body") or ""):
        raise Blocked("PR description lacks an Evidence/Verification/Tests section.")
    validate_human_testing(pr.get("body") or "")
    return pr


def review_verdict(log: str) -> str:
    # Only an explicit final verdict line counts. Free-form sentiment is insufficient.
    matches = re.findall(r"(?im)^REVIEW_VERDICT:\s*(APPROVE|REQUEST_CHANGES|UNABLE_TO_VERIFY)\s*$", log)
    if len(matches) != 1:
        raise Blocked("Reviewer must emit one unambiguous REVIEW_VERDICT line; "
                      "cannot promote a PR based on unstructured or conflicting prose.")
    return matches[0]


def run_agent(argv: list[str], cwd: Path, log_path: Path, timeout: int) -> str:
    """Run a fresh CLI session, stream its output, and bound its process group.

    Inherit terminal stdin rather than silently pre-approving tool permissions.
    An OpenCode permission interaction unavailable in CLI mode will time out and
    block the run, rather than receiving an unsafe '--auto' override.
    """
    agent_name = argv[argv.index("--agent") + 1] if "--agent" in argv else argv[0]
    print(f"Starting {agent_name} in {cwd}. Transcript: {log_path}", flush=True)
    with log_path.open("wb") as log:
        try:
            process = subprocess.Popen(argv, cwd=cwd, stdin=None,
                                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       start_new_session=True)
        except OSError as exc:
            raise Blocked(f"Cannot start OpenCode: {exc}") from exc
        def stream() -> None:
            assert process.stdout is not None
            decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
            while True:
                block = os.read(process.stdout.fileno(), 4096)
                if not block:
                    break
                log.write(block)
                log.flush()
                rendered = decoder.decode(block)
                if rendered:
                    print(rendered, end="", flush=True)
            remainder = decoder.decode(b"", final=True)
            if remainder:
                print(remainder, end="", flush=True)
        pump = threading.Thread(target=stream, daemon=True)
        pump.start()
        try:
            code = process.wait(timeout=timeout)
        except (subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()
            pump.join(timeout=2)
            if process.stdout is not None:
                process.stdout.close()
            raise Blocked("Agent stopped (timeout or interruption); check logs. "
                          "The worktree is preserved for inspection.") from exc
        pump.join(timeout=2)
        if process.stdout is not None:
            process.stdout.close()
    if code != 0:
        raise Blocked(f"OpenCode exited {code}; read {log_path} before retrying.")
    return log_path.read_text(encoding="utf-8", errors="replace")


def write_state(path: Path, **fields: object) -> None:
    data = json.loads(path.read_text()) if path.exists() else {}
    data.update(fields)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    tmp.replace(path)


def review_prompt(issue: int, pr: dict) -> str:
    return (f"Independently review PR #{pr['number']} for Issue #{issue} at exact "
            f"commit {pr['headRefOid']} in {REPOSITORY}. Read AGENTS.md, the issue "
            "and authoritative parent requirements; inspect actual code and diff, "
            "reproduce appropriate tests and visual checks where possible. "
            "This is a read-only review; do not edit files, commits, or GitHub state. "
            "Identify confirmed defects with files/lines; distinguish unverified "
            "concerns from scope requirements. Do not rely on developer claims. "
            "Conclude with exactly one final line: REVIEW_VERDICT: APPROVE, "
            "REVIEW_VERDICT: REQUEST_CHANGES, or REVIEW_VERDICT: UNABLE_TO_VERIFY. "
            "Provide evidence before the verdict line.")


def developer_prompt(issue: int, branch: str) -> str:
    return (f"Implement GitHub Issue #{issue} in {REPOSITORY} following AGENTS.md "
            "and docs/agent-workflow.md. You are already in an isolated worktree "
            f"on branch '{branch}' based on origin/main; preserve it. Verify the "
            "actual issue, all authoritative parent fixtures, and approval scope. "
            "Implement, execute real tests and GUI inspection where available, "
            "document actual evidence, push this branch and open one non-draft PR "
            f"to main whose body contains 'Closes #{issue}', an Evidence section, "
            "and a ## Human Testing section containing exact launch/test commands "
            "when applicable, step-by-step manual checks, and expected results. "
            "Do not merge or change unrelated files. If blocked, report the blocker. "
            "Do not invent test evidence or imply visual inspection happened if it did not.")


def correction_prompt(issue: int, pr: dict, review_text: str) -> str:
    # Keep the corrective agent grounded in a durable review log. The entire review
    # text comes from the independent review run, not from a claimed verdict alone.
    return (f"Correct verified findings on PR #{pr['number']} for Issue #{issue}. "
            "Review independent QA notes below and fix only substantiated issues; "
            "rerun appropriate tests, update the existing branch and PR evidence, "
            "and do not merge. Preserve or update the PR's ## Human Testing "
            "steps with accurate commands and expected results. "
            "If findings are incorrect, document concrete proof.\n\n"
            f"Independent review:\n{review_text[-18000:]}")


def preflight(repo: Path, issue: int, model: str) -> dict:
    for exe in ("git", "gh", "opencode"):
        if not shutil.which(exe):
            raise Blocked(f"Missing '{exe}' from PATH.")
    if os.environ.get("OPENAI_API_KEY"):
        raise Blocked("OPENAI_API_KEY is set. Unset it to avoid accidental direct API billing; "
                      "verify ChatGPT sign-in in OpenCode instead.")
    actual = Path(run_cmd(["git", "rev-parse", "--show-toplevel"], repo)).resolve()
    if actual != repo.resolve():
        raise Blocked(f"Run from the primary repository root, not nested worktree: {actual}")
    remote = run_cmd(["git", "remote", "get-url", "origin"], repo)
    if not re.search(r"(?:github\.com[:/])williamwhorton/The-Producer(?:\.git)?$", remote):
        raise Blocked("Origin remote does not point to the intended GitHub repository.")
    named = json_cmd(["gh", "repo", "view", REPOSITORY, "--json", "nameWithOwner"], repo)
    if named.get("nameWithOwner") != REPOSITORY:
        raise Blocked("GitHub repository identity differs from configured repository.")
    run_cmd(["gh", "auth", "status"], repo)
    version = run_cmd(["opencode", "--version"], repo)
    run_cmd(["opencode", "run", "--help"], repo)
    if not version:
        raise Blocked("Cannot determine installed OpenCode version.")
    if not (repo / ".opencode/agents/producer-reviewer.md").is_file():
        raise Blocked("Missing project Reviewer profile.")
    review_config = (repo / ".opencode/agents/producer-reviewer.md").read_text()
    if "mode: primary" not in review_config or "effect: deny" not in review_config:
        raise Blocked("Reviewer profile not verified as primary with deny rules.")
    data = issue_details(issue, repo)
    existing_prs(issue, repo)
    print(f"OpenCode {version}; issue #{issue}: {data['title']} ({data['url']})")
    print(f"Requested cloud model: {model}. Ensure it uses ChatGPT plan authentication.")
    return data



def registered_worktrees(repo: Path) -> list[dict]:
    entries = []
    raw = run_cmd(["git", "worktree", "list", "--porcelain"], repo)
    for record in raw.split("\n\n"):
        item = {}
        for line in record.splitlines():
            key, _, value = line.partition(" ")
            if key == "worktree":
                item["path"] = Path(value).resolve()
            elif key in ("branch", "HEAD", "detached"):
                item[key] = value
        if "path" in item:
            entries.append(item)
    return entries


def worktree_in_use(path: Path) -> bool:
    """Linux check: refuse removal while any process has cwd in the checkout."""
    proc = Path("/proc")
    if not proc.is_dir():
        raise Blocked("Cannot verify active processes without /proc.")
    for entry in proc.iterdir():
        if not entry.name.isdigit() or int(entry.name) == os.getpid():
            continue
        try:
            cwd = Path(os.readlink(entry / "cwd"))
        except (OSError, PermissionError):
            continue
        if cwd == path or path in cwd.parents:
            return True
    return False


def pr_preserves_head(repo: Path, branch: str, sha: str, merged_only: bool) -> bool:
    results = json_cmd(["gh", "pr", "list", "--repo", REPOSITORY, "--state", "all",
                        "--head", branch, "--limit", "100",
                        "--json", "state,headRefName,headRefOid"], repo)
    if not isinstance(results, list):
        return False
    allowed = ("MERGED",) if merged_only else ("OPEN", "CLOSED", "MERGED")
    return any(p.get("headRefName") == branch and p.get("headRefOid") == sha
               and p.get("state") in allowed for p in results)


def cleanup_worktrees(repo: Path, *, issue: int | None = None) -> tuple[int, list[str]]:
    """Remove only inactive, clean, owned worktrees with safely preserved commits.

    This deliberately never calls git worktree remove --force or deletes logs.
    """
    repo = repo.resolve()
    known: set[Path] = set()
    state_home = repo.parent / f".{repo.name}-agent-runs"
    if state_home.is_dir():
        for file in state_home.glob("issue-*/state.json"):
            try:
                state = json.loads(file.read_text())
            except (OSError, ValueError):
                continue
            if issue is not None and state.get("issue") != issue:
                continue
            for name in ("development_worktree", "review_worktree"):
                value = state.get(name)
                if isinstance(value, str):
                    known.add(Path(value).resolve())
    removed, skipped = 0, []
    for record in registered_worktrees(repo):
        path = record["path"]
        if path == repo or path.parent != repo.parent:
            continue
        name = path.name
        is_review = name.startswith(repo.name + "-review-")
        is_agent = name.startswith(repo.name + "-agent-")
        is_legacy = bool(re.fullmatch(rf"{re.escape(repo.name)}-issue-\d+[-\w]*", name))
        if not (is_review or is_agent or is_legacy):
            continue
        if issue is not None and path not in known:
            continue
        try:
            if worktree_in_use(path):
                raise Blocked("a running process is using this checkout")
            if run_cmd(["git", "-C", str(path), "status", "--porcelain",
                        "--untracked-files=all"], repo):
                raise Blocked("uncommitted or untracked files exist")
            ignored = run_cmd(["git", "-C", str(path), "status", "--porcelain",
                               "--ignored", "--untracked-files=all"], repo)
            extras = [line[3:] for line in ignored.splitlines() if line.startswith("!! ")]
            if any(not (item == ".godot/" or item.startswith(".godot/")) for item in extras):
                raise Blocked("ignored files outside disposable .godot cache")
            head = run_cmd(["git", "-C", str(path), "rev-parse", "HEAD"], repo)
            branch = record.get("branch", "").removeprefix("refs/heads/")
            if is_review and "detached" in record:
                pass
            elif branch and pr_preserves_head(repo, branch, head, is_legacy):
                pass
            else:
                raise Blocked("local commit is not verified on an eligible GitHub PR")
            run_cmd(["git", "worktree", "remove", str(path)], repo, timeout=120)
            removed += 1
            print(f"CLEANED: {path}", flush=True)
        except Blocked as exc:
            skipped.append(f"{path}: {exc}")
            print(f"RETAINED: {path} ({exc})", flush=True)
    print(f"Worktree cleanup: {removed} removed, {len(skipped)} retained.", flush=True)
    return removed, skipped


def orchestrate(args: argparse.Namespace) -> int:
    repo = Path(args.repo).expanduser().resolve()
    if not repo.is_dir():
        raise Blocked(f"Repository directory not found: {repo}")
    model = require_model(args.model)
    issue = args.issue
    info = preflight(repo, issue, model)
    run_home = repo.parent / f".{repo.name}-agent-runs"
    state_dir = run_home / f"issue-{issue}"
    if state_dir.exists():
        raise Blocked(f"Existing run for Issue #{issue}: {state_dir}. "
                      "Inspect its state/logs; manual recovery is required in v1.")
    if args.dry_run:
        print(f"DRY RUN: would create a separate worktree from origin/{BASE_BRANCH}, "
              "launch OpenCode Build and Reviewer as fresh sessions, and leave PR unmerged.")
        print("No branches, worktrees, agent sessions, or state files created.")
        return 0
    if not args.approve_issue:
        raise Blocked("Execution requires --approve-issue, explicitly authorizing "
                      "this open issue for the supervised pilot. Use --dry-run first.")
    run_cmd(["git", "fetch", "origin", BASE_BRANCH], repo, timeout=120)
    run_cmd(["git", "rev-parse", "--verify", f"origin/{BASE_BRANCH}"], repo)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"{issue}-{stamp}-{secrets.token_hex(3)}"
    branch = f"agent/issue-{issue}-{stamp.lower()}-{secrets.token_hex(2)}"
    dev = repo.parent / f"{repo.name}-agent-{run_id}"
    state_dir.mkdir(parents=True, exist_ok=False)
    state_file = state_dir / "state.json"
    write_state(state_file, phase="starting", issue=issue, title=info["title"],
                model=model, branch=branch, development_worktree=str(dev),
                created_at=stamp, approved_by_human=True)
    print(f"Run log/state: {state_dir}")
    try:
        run_cmd(["git", "worktree", "add", "-b", branch, str(dev),
                 f"origin/{BASE_BRANCH}"], repo, timeout=120)
        write_state(state_file, phase="developing")
        prompt = developer_prompt(issue, branch)
        run_agent(["opencode", "run", "--standalone", "--agent", "build", "--model", model,
                   prompt], dev, state_dir / "developer-0.log", args.timeout_minutes * 60)
        pr = pr_details(branch, issue, repo)
        write_state(state_file, phase="reviewing", pr=pr["url"], head_sha=pr["headRefOid"])
        for attempt in range(2):
            # Fetch remote head, then review the exact GitHub PR commit detached.
            run_cmd(["git", "fetch", "origin", branch], repo, timeout=120)
            actual_sha = run_cmd(["git", "rev-parse", "FETCH_HEAD"], repo)
            if actual_sha != pr["headRefOid"]:
                raise Blocked("PR commit changed while preparing review; stop to avoid a stale review.")
            review = repo.parent / f"{repo.name}-review-{run_id}-{attempt}"
            run_cmd(["git", "worktree", "add", "--detach", str(review), actual_sha],
                    repo, timeout=120)
            write_state(state_file, phase="reviewing", review_worktree=str(review),
                        review_attempt=attempt)
            review_text = run_agent(["opencode", "run", "--standalone", "--agent",
                                     "producer-reviewer", "--model", model,
                                     review_prompt(issue, pr)], review,
                                    state_dir / f"review-{attempt}.log",
                                    args.timeout_minutes * 60)
            verdict = review_verdict(review_text)
            latest = pr_details(branch, issue, repo)
            if latest["headRefOid"] != pr["headRefOid"]:
                raise Blocked("PR head changed during review; verdict is stale.")
            write_state(state_file, last_verdict=verdict)
            if verdict == "APPROVE":
                write_state(state_file, phase="ready_for_human_acceptance")
                print(f"READY FOR YOUR ACCEPTANCE: {pr['url']}")
                print(f"Issue #{issue}, verified PR head {pr['headRefOid']}, "
                      f"review verdict {verdict}; logs: {state_dir}")
                print("Human visual acceptance and merge remain required.")
                return 0
            if verdict == "UNABLE_TO_VERIFY":
                raise Blocked("Independent reviewer could not verify the PR; see logs.")
            if attempt:
                raise Blocked("Independent review still requests changes after one correction cycle.")
            write_state(state_file, phase="correcting")
            run_agent(["opencode", "run", "--standalone", "--agent", "build", "--model",
                       model, correction_prompt(issue, pr, review_text)], dev,
                      state_dir / "developer-1.log", args.timeout_minutes * 60)
            updated = pr_details(branch, issue, repo)
            if updated["number"] != pr["number"] or updated["headRefOid"] == pr["headRefOid"]:
                raise Blocked("Correction did not update the same PR with a new commit.")
            pr = updated
        raise Blocked("No decisive review outcome.")
    except Blocked as exc:
        write_state(state_file, phase="blocked", reason=str(exc))
        raise
    finally:
        try:
            _, retained = cleanup_worktrees(repo, issue=issue)
            write_state(state_file, cleanup_pending=retained)
        except (Blocked, OSError) as exc:
            print(f"CLEANUP WARNING: {exc}", file=sys.stderr)
            write_state(state_file, cleanup_pending=[str(exc)])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("issue", type=int, nargs="?", help="approved GitHub issue number")
    parser.add_argument("--cleanup-worktrees", action="store_true", help="clean idle completed worktrees")
    parser.add_argument("--repo", default=".", help="path to the main repository checkout")
    parser.add_argument("--model", help="explicit OpenAI model ID from OpenCode")
    parser.add_argument("--dry-run", action="store_true", help="preflight only; no writes or AI runs")
    parser.add_argument("--approve-issue", action="store_true", help="authorize this issue's execution")
    parser.add_argument("--timeout-minutes", type=int, default=60,
                        help="timeout per model session (default: 60)")
    args = parser.parse_args(argv)
    if args.cleanup_worktrees:
        if args.issue is not None or args.model or args.dry_run or args.approve_issue:
            parser.error("--cleanup-worktrees takes no issue/model/approval arguments")
        try:
            repo = Path(args.repo).expanduser().resolve()
            actual = Path(run_cmd(["git", "rev-parse", "--show-toplevel"], repo)).resolve()
            if actual != repo or repo.name != "The-Producer":
                raise Blocked("Cleanup must run from the main The-Producer checkout.")
            remote = run_cmd(["git", "remote", "get-url", "origin"], repo)
            if not re.search(r"(?:github\.com[:/])williamwhorton/The-Producer(?:\.git)?$", remote):
                raise Blocked("Origin is not the expected The-Producer repository.")
            _, retained = cleanup_worktrees(repo)
            return 2 if retained else 0
        except Blocked as exc:
            print(f"BLOCKED: {exc}", file=sys.stderr)
            return 2
    if args.issue is None or args.issue < 1 or not args.model or not 1 <= args.timeout_minutes <= 180:
        parser.error("provide ISSUE and --model; timeout must be 1–180 minutes")
    try:
        return orchestrate(args)
    except Blocked as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
