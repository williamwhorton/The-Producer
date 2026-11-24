#!/usr/bin/env python3
"""Supervised OpenCode Build -> independent Reviewer runner.

Run one explicitly approved issue, or opt in to the owner-authorized Ready queue.
No merging, forced cleanup, permission auto-approval, model fallback or paid API selection.
"""

from __future__ import annotations

import argparse
import codecs
from contextlib import contextmanager
import datetime as dt
import fcntl
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
import time

REPOSITORY = "williamwhorton/The-Producer"
BASE_BRANCH = "main"
VERDICTS = ("APPROVE", "REQUEST_CHANGES", "UNABLE_TO_VERIFY")


class Blocked(RuntimeError):
    """A fail-closed, human-actionable workflow blocker."""


class GitHubUnavailable(Blocked):
    """The control plane could not verify GitHub; do not keep dispatching."""


class Interrupted(Blocked):
    """An agent was stopped by the operator rather than failing a task."""


def run_cmd(argv: list[str], cwd: Path, *, timeout: int = 40) -> str:
    error = GitHubUnavailable if argv[0] == "gh" else Blocked
    try:
        result = subprocess.run(argv, cwd=cwd, capture_output=True, text=True,
                                timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise error(f"Command unavailable or timed out: {argv[0]} ({exc})") from exc
    if result.returncode:
        excerpt = (result.stderr or result.stdout).strip()[-900:]
        raise error(f"{argv[0]} failed (exit {result.returncode}): {excerpt}")
    return result.stdout.strip()


def json_cmd(argv: list[str], cwd: Path) -> object:
    raw = run_cmd(argv, cwd)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        error = GitHubUnavailable if argv[0] == "gh" else Blocked
        raise error(f"Unexpected JSON from {argv[0]}: {exc}") from exc


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


def verify_checkout(cwd: Path, *, expected_branch: str | None = None,
                    expected_sha: str | None = None) -> None:
    """Fail closed before an agent starts on an unintended checkout.

    Git's actual worktree root/branch are authoritative, not a parent session,
    the Git common directory, the project label or the LLM's own claims.
    """
    cwd = cwd.resolve()
    actual_root = Path(run_cmd(["git", "rev-parse", "--show-toplevel"], cwd)).resolve()
    if actual_root != cwd:
        raise Blocked(f"Agent checkout mismatch: expected {cwd}, Git reports {actual_root}.")
    actual_branch = run_cmd(["git", "branch", "--show-current"], cwd)
    if expected_branch is not None and actual_branch != expected_branch:
        raise Blocked(f"Agent branch mismatch in {cwd}: expected {expected_branch!r}, "
                      f"got {actual_branch!r}.")
    if expected_sha is not None:
        if actual_branch:
            raise Blocked(f"Reviewer must be detached at {expected_sha}; "
                          f"found branch {actual_branch!r} in {cwd}.")
        actual_sha = run_cmd(["git", "rev-parse", "HEAD"], cwd)
        if actual_sha != expected_sha:
            raise Blocked(f"Reviewer SHA mismatch in {cwd}: expected {expected_sha}, "
                          f"got {actual_sha}.")


def agent_environment(cwd: Path) -> dict[str, str]:
    """Keep process cwd and PWD consistent when launching OpenCode.

    Some OpenCode run versions prefer inherited PWD over the child process cwd.
    Python's Popen(cwd=...) does not rewrite PWD; without this, a process
    started in the main checkout may bind its session back to main.
    """
    env = os.environ.copy()
    env["PWD"] = str(cwd.resolve())
    return env


def run_agent(argv: list[str], cwd: Path, log_path: Path, timeout: int) -> str:
    """Run a fresh CLI session, stream its output, and bound its process group.

    Inherit terminal stdin rather than silently pre-approving tool permissions.
    An OpenCode permission interaction unavailable in CLI mode will time out and
    block the run, rather than receiving an unsafe '--auto' override.
    """
    cwd = cwd.resolve()
    agent_name = argv[argv.index("--agent") + 1] if "--agent" in argv else argv[0]
    print(f"Starting {agent_name} in {cwd}. Transcript: {log_path}", flush=True)
    with log_path.open("wb") as log:
        try:
            process = subprocess.Popen(argv, cwd=cwd, env=agent_environment(cwd),
                                       stdin=None, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, start_new_session=True)
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
        try:
            pump.start()
            code = process.wait(timeout=timeout)
        except (subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
            # The leader can exit on TERM before its children do.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            if process.returncode is None:
                process.wait()
            if pump.ident is not None:
                pump.join(timeout=2)
            if process.stdout is not None:
                process.stdout.close()
            error = Interrupted if isinstance(exc, KeyboardInterrupt) else Blocked
            reason = "interrupted" if isinstance(exc, KeyboardInterrupt) else "timed out"
            raise error(f"Agent {reason}; check {log_path}.") from exc
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


def review_prompt(issue: int, pr: dict, worktree: Path) -> str:
    return (f"Independently review PR #{pr['number']} for Issue #{issue} in "
            f"worktree {worktree.resolve()} at exact "
            f"commit {pr['headRefOid']} in {REPOSITORY}. The Python runner has "
            "already independently verified this worktree's Git root and "
            "detached commit before launching you. Confirm with INDIVIDUAL "
            "shell tool calls using EXACTLY these commands (each as its own "
            "invocation): pwd ; git rev-parse --show-toplevel ; "
            "git rev-parse HEAD ; git branch --show-current ; "
            "git status --short --branch. The semicolons in this sentence "
            "SEPARATE examples; NEVER send them together as a single command, "
            "pipeline, script, or multi-line request. Do not use printf, "
            "pwd -P, git symbolic-ref, or git remote -v in this preflight. "
            "If the returned location/commit differs, stop with "
            "REVIEW_VERDICT: UNABLE_TO_VERIFY. Read AGENTS.md, the issue "
            "and authoritative parent requirements; inspect actual code and diff, "
            "reproduce appropriate tests and visual checks where possible. "
            "This is a read-only review; do not edit files, commits, or GitHub state. "
            "Identify confirmed defects with files/lines; distinguish unverified "
            "concerns from scope requirements. Do not rely on developer claims. "
            "Conclude with exactly one final line: REVIEW_VERDICT: APPROVE, "
            "REVIEW_VERDICT: REQUEST_CHANGES, or REVIEW_VERDICT: UNABLE_TO_VERIFY. "
            "Provide evidence before the verdict line.")


def developer_prompt(issue: int, branch: str, worktree: Path) -> str:
    return (f"Implement GitHub Issue #{issue} in {REPOSITORY}, worktree "
            f"{worktree.resolve()}, following AGENTS.md "
            "and docs/agent-workflow.md. You are already in an isolated worktree "
            f"on branch '{branch}' based on origin/main; preserve it. BEFORE doing "
            "any work, run 'pwd', 'git rev-parse --show-toplevel' and "
            "'git branch --show-current'. If the worktree or branch is not "
            "this exact assigned worktree/branch, STOP without edits. Verify the "
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
            "Before edits, independently verify pwd, Git worktree root, and "
            "current branch match the assigned issue worktree; stop if not. "
            "If findings are incorrect, document concrete proof.\n\n"
            f"Independent review:\n{review_text[-18000:]}")


def host_preflight(repo: Path) -> tuple[str, str]:
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
    help_text = run_cmd(["opencode", "run", "--help"], repo)
    if not version:
        raise Blocked("Cannot determine installed OpenCode version.")
    if not (repo / ".opencode/agents/producer-reviewer.md").is_file():
        raise Blocked("Missing project Reviewer profile.")
    review_config = (repo / ".opencode/agents/producer-reviewer.md").read_text()
    if "mode: primary" not in review_config or "effect: deny" not in review_config:
        raise Blocked("Reviewer profile not verified as primary with deny rules.")
    return version, help_text


def preflight(repo: Path, issue: int, model: str, *, allow_open_pr: bool = False) -> dict:
    version, _ = host_preflight(repo)
    data = issue_details(issue, repo)
    if not allow_open_pr:
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


def merged_pr_contains_review_commit(repo: Path, issue: int, sha: str,
                                     pr_url: str | None) -> bool:
    """For old runner logs, establish a detached SHA was part of a merged PR.

    This is only a fallback when an older runner did not record review SHA
    history. Do not trust a directory's name or the local commit alone.
    """
    if not isinstance(pr_url, str):
        return False
    match = re.fullmatch(
        rf"https://github\.com/{re.escape(REPOSITORY)}/pull/([0-9]+)", pr_url)
    if not match or not re.fullmatch(r"[0-9a-f]{40}", sha):
        return False
    pr = json_cmd(["gh", "pr", "view", match[1], "--repo", REPOSITORY,
                   "--json", "state,headRefOid,body"], repo)
    if (not isinstance(pr, dict) or pr.get("state") != "MERGED"
            or not closes_issue(pr.get("body") or "", issue)
            or not re.fullmatch(r"[0-9a-f]{40}", pr.get("headRefOid") or "")):
        return False
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", sha, pr["headRefOid"]],
        cwd=repo, capture_output=True, check=False)
    return result.returncode == 0


def godot_ignored_cache_dirs(worktree: Path, ignored: list[str]) -> list[Path]:
    """Recognize only disposable .godot caches, including nested Godot projects."""
    caches: set[Path] = set()
    for name in ignored:
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts or ".godot" not in relative.parts:
            raise Blocked("ignored files outside disposable .godot cache")
        cache_parts = relative.parts[:relative.parts.index(".godot") + 1]
        cache = worktree.joinpath(*cache_parts)
        if cache.is_symlink() or not cache.is_dir():
            raise Blocked("Godot cache is not a normal directory; refusing to delete it")
        if not cache.resolve().is_relative_to(worktree.resolve()):
            raise Blocked("Godot cache resolves outside the worktree")
        caches.add(cache)
    return sorted(caches)


def cleanup_worktrees(repo: Path, *, issue: int | None = None) -> tuple[int, list[str]]:
    """Remove only inactive, clean, owned worktrees with safely preserved commits.

    This deliberately never calls git worktree remove --force or deletes logs.
    """
    repo = repo.resolve()
    known: set[Path] = set()
    review_heads: dict[Path, str] = {}
    review_prs: dict[int, str] = {}
    state_home = repo.parent / f".{repo.name}-agent-runs"
    if state_home.is_dir():
        for file in state_home.glob("issue-*/state.json"):
            try:
                state = json.loads(file.read_text())
            except (OSError, ValueError):
                continue
            if issue is not None and state.get("issue") != issue:
                continue
            if isinstance(state.get("issue"), int) and isinstance(state.get("pr"), str):
                review_prs[state["issue"]] = state["pr"]
            for name in ("development_worktree", "review_worktree"):
                value = state.get(name)
                if isinstance(value, str):
                    known.add(Path(value).resolve())
            if isinstance(state.get("review_worktree"), str) and isinstance(state.get("head_sha"), str):
                review_heads[Path(state["review_worktree"]).resolve()] = state["head_sha"]
            for prior in state.get("review_worktrees", []):
                if isinstance(prior, dict) and isinstance(prior.get("path"), str):
                    recorded = Path(prior["path"]).resolve()
                    known.add(recorded)
                    if isinstance(prior.get("sha"), str):
                        review_heads[recorded] = prior["sha"]
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
            cache_dirs = godot_ignored_cache_dirs(path, extras)
            head = run_cmd(["git", "-C", str(path), "rev-parse", "HEAD"], repo)
            branch = record.get("branch", "").removeprefix("refs/heads/")
            if is_review and "detached" in record:
                if review_heads.get(path) != head:
                    match = re.match(rf"{re.escape(repo.name)}-review-(\d+)-", name)
                    review_issue = int(match[1]) if match else None
                    if review_issue is None or not merged_pr_contains_review_commit(
                            repo, review_issue, head, review_prs.get(review_issue)):
                        raise Blocked("detached review commit not verified in runner state or merged PR")
            elif branch and pr_preserves_head(repo, branch, head, is_legacy):
                pass
            elif (branch and is_agent and not is_legacy and
                  subprocess.run(["git", "-C", str(path), "merge-base",
                                  "--is-ancestor", "HEAD", "origin/main"],
                                 capture_output=True, check=False).returncode == 0):
                # Failed before the Developer created any unique commits.
                pass
            else:
                raise Blocked("local commit is not verified on an eligible GitHub PR")
            # Godot's generated .godot caches are safe to remove; Git refuses
            # worktree removal when ignored generated files remain in the checkout.
            # Never delete any other ignored content or follow cache symlinks.
            for cache_dir in cache_dirs:
                shutil.rmtree(cache_dir)
            run_cmd(["git", "worktree", "remove", str(path)], repo, timeout=120)
            removed += 1
            print(f"CLEANED: {path}", flush=True)
        except (Blocked, OSError) as exc:
            skipped.append(f"{path}: {exc}")
            print(f"RETAINED: {path} ({exc})", flush=True)
    print(f"Worktree cleanup: {removed} removed, {len(skipped)} retained.", flush=True)
    return removed, skipped


def archive_blocked_run(repo: Path, issue: int, state_dir: Path) -> Path:
    """Allow an explicitly authorized retry without discarding old audit logs.

    Only an earlier blocked run with no PR and no surviving worktrees may be
    archived. Uncommitted/active/unknown worktrees must be investigated rather
    than overwritten by another agent.
    """
    state_file = state_dir / "state.json"
    try:
        previous = json.loads(state_file.read_text())
    except (OSError, ValueError) as exc:
        raise Blocked("Cannot inspect old run state; refusing automatic retry.") from exc
    if (previous.get("issue") != issue or previous.get("phase") not in ("blocked", "interrupted")
            or previous.get("pr")):
        raise Blocked("Retry is only allowed for a blocked run with no PR.")
    old_branch = previous.get("branch")
    if isinstance(old_branch, str) and old_branch:
        prior_prs = json_cmd(["gh", "pr", "list", "--repo", REPOSITORY,
                             "--state", "all", "--head", old_branch,
                             "--limit", "100", "--json", "number"], repo)
        if not isinstance(prior_prs, list) or prior_prs:
            raise Blocked("Previous branch has a GitHub PR or cannot be verified; "
                          "do not duplicate that work.")
    _, retained = cleanup_worktrees(repo, issue=issue)
    if retained:
        raise Blocked("Previous run still owns worktrees that could not be cleaned: "
                      + "; ".join(retained))
    registered = {x["path"] for x in registered_worktrees(repo)}
    candidates = [previous.get("development_worktree"),
                  previous.get("review_worktree")]
    candidates += [x.get("path") for x in previous.get("review_worktrees", [])
                   if isinstance(x, dict)]
    for item in candidates:
        if not isinstance(item, str):
            continue
        path = Path(item).resolve()
        if path in registered or path.exists():
            raise Blocked(f"Previous run worktree still exists: {path}")
    archive = state_dir.with_name(
        state_dir.name + "-history-" +
        dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + "-" + secrets.token_hex(3))
    state_dir.rename(archive)
    print(f"Preserved previous blocked run logs: {archive}", flush=True)
    return archive


def review_existing_pr(args: argparse.Namespace) -> int:
    """Independent review of an existing PR, without restarting Build.

    Explicit user invocation is the authorization for this read-only action.
    The normal develop/review run for the issue may remain blocked or complete.
    """
    repo = Path(args.repo).expanduser().resolve()
    if not repo.is_dir():
        raise Blocked(f"Repository directory not found: {repo}")
    model = require_model(args.model)
    issue = args.issue
    pr_number = args.review_pr
    preflight(repo, issue, model, allow_open_pr=True)
    overview = json_cmd(
        ["gh", "pr", "view", str(pr_number), "--repo", REPOSITORY,
         "--json", "number,headRefName,state"], repo)
    if not isinstance(overview, dict) or overview.get("number") != pr_number:
        raise Blocked("Cannot verify requested PR number.")
    if overview.get("state") != "OPEN":
        raise Blocked("Review-only mode requires an open PR.")
    branch = overview.get("headRefName")
    if not isinstance(branch, str) or not branch.startswith("agent/"):
        raise Blocked("Review-only mode requires an agent/ issue branch.")
    pr = pr_details(branch, issue, repo)
    if pr["number"] != pr_number:
        raise Blocked("PR branch resolves to a different PR; refusing review.")
    if args.dry_run:
        print(f"DRY RUN: would independently review {pr['url']} for Issue #{issue}, "
              f"head {pr['headRefOid']}, using model {model}.")
        print("No AI session, Git fetch, state file, or worktree created.")
        return 0

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"{issue}-{stamp}-{secrets.token_hex(3)}"
    review = repo.parent / f"{repo.name}-review-{run_id}-pr{pr_number}"
    state_dir = (repo.parent / f".{repo.name}-agent-runs" /
                 f"issue-{issue}-review-pr-{pr_number}-{stamp}-{secrets.token_hex(3)}")
    state_dir.mkdir(parents=True, exist_ok=False)
    state_file = state_dir / "state.json"
    write_state(state_file, issue=issue, pr=pr["url"], head_sha=pr["headRefOid"],
                model=model, phase="preparing_review", review_attempt=0)
    try:
        run_cmd(["git", "fetch", "origin", branch], repo, timeout=120)
        sha = run_cmd(["git", "rev-parse", "FETCH_HEAD"], repo)
        if sha != pr["headRefOid"]:
            raise Blocked("PR head changed while preparing independent review.")
        run_cmd(["git", "worktree", "add", "--detach", str(review), sha],
                repo, timeout=120)
        write_state(state_file, phase="reviewing", review_worktree=str(review),
                    review_worktrees=[{"path": str(review), "sha": sha}])
        verify_checkout(review, expected_sha=sha)
        print(f"Fresh review transcript: {state_dir / 'review-0.log'}", flush=True)
        output = run_agent(
            ["opencode", "run", "--standalone", "--agent",
             "producer-reviewer", "--model", model, review_prompt(issue, pr, review)],
            review, state_dir / "review-0.log", args.timeout_minutes * 60)
        verdict = review_verdict(output)
        current = pr_details(branch, issue, repo)
        if current["headRefOid"] != sha:
            raise Blocked("PR head changed during independent review; verdict is stale.")
        write_state(state_file, last_verdict=verdict)
        if verdict == "APPROVE":
            write_state(state_file, phase="ready_for_human_acceptance")
            print(f"REVIEWED: {pr['url']} at {sha}", flush=True)
            print("Reviewer recommended APPROVE; human acceptance and merge "
                  f"remain required. Transcript: {state_dir / 'review-0.log'}",
                  flush=True)
            return 0
        if verdict == "REQUEST_CHANGES":
            write_state(state_file, phase="changes_requested")
            raise Blocked("Reviewer requested changes to existing PR; do not "
                          f"restart development. Inspect {state_dir / 'review-0.log'}")
        raise Blocked("Reviewer could not independently verify existing PR; "
                      f"inspect {state_dir / 'review-0.log'}")
    except Blocked as exc:
        write_state(state_file, phase="blocked", reason=str(exc))
        raise
    finally:
        try:
            _, retained = cleanup_worktrees(repo)
            write_state(state_file, cleanup_pending=retained)
        except (Blocked, OSError) as exc:
            print(f"CLEANUP WARNING: {exc}", file=sys.stderr)
            write_state(state_file, cleanup_pending=[str(exc)])


def orchestrate(args: argparse.Namespace) -> int:
    repo = Path(args.repo).expanduser().resolve()
    if not repo.is_dir():
        raise Blocked(f"Repository directory not found: {repo}")
    model = require_model(args.model)
    issue = args.issue
    info = preflight(repo, issue, model)
    state_dir = run_home(repo) / f"issue-{issue}"
    if state_dir.exists() and not args.retry_blocked:
        raise Blocked(f"Existing run for Issue #{issue}: {state_dir}. "
                      "For a previous blocked run with no PR, use --retry-blocked "
                      "with --approve-issue after inspecting its last error.")
    if args.dry_run:
        print(f"DRY RUN: would create a separate worktree from origin/{BASE_BRANCH}, "
              "launch OpenCode Build and Reviewer as fresh sessions, and leave PR unmerged.")
        print("No branches, worktrees, agent sessions, or state files created.")
        return 0
    if not args.approve_issue:
        raise Blocked("Execution requires --approve-issue, explicitly authorizing "
                      "this open issue for the supervised pilot. Use --dry-run first.")
    if args.retry_blocked:
        if not state_dir.is_dir():
            raise Blocked("--retry-blocked requires an existing blocked run state.")
        archive_blocked_run(repo, issue, state_dir)
    run_cmd(["git", "fetch", "origin", BASE_BRANCH], repo, timeout=120)
    run_cmd(["git", "rev-parse", "--verify", f"origin/{BASE_BRANCH}"], repo)
    return develop_and_review(args, repo, model, info, state_dir)


def develop_and_review(args, repo, model, info, state_dir, *, before_build=None) -> int:
    """The shared, single-issue execution and independent review workflow."""
    issue = info["number"]
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"{issue}-{stamp}-{secrets.token_hex(3)}"
    branch = f"agent/issue-{issue}-{stamp.lower()}-{secrets.token_hex(2)}"
    dev = repo.parent / f"{repo.name}-agent-{run_id}"
    queued = before_build is not None
    state_dir.mkdir(parents=True, exist_ok=queued)
    state_file = state_dir / "state.json"
    write_state(state_file, phase="starting", issue=issue, title=info["title"],
                model=model, branch=branch, development_worktree=str(dev),
                created_at=stamp, approved_by_human=True)
    print(f"Run log/state: {state_dir}")
    try:
        run_cmd(["git", "worktree", "add", "-b", branch, str(dev),
                 f"origin/{BASE_BRANCH}"], repo, timeout=120)
        write_state(state_file, phase="developing")
        verify_checkout(dev, expected_branch=branch)
        prompt = developer_prompt(issue, branch, dev)
        queue_instructions = ("\nThe host runner owns Project status transitions for this queue "
                              "assignment. Do not post /status commands or change Project status; "
                              "report blockers and evidence to the host.")
        if queued:
            prompt += queue_instructions
            before_build()
        run_agent(["opencode", "run", "--standalone", "--agent", "build", "--model", model,
                   prompt], dev, state_dir / "developer-0.log", args.timeout_minutes * 60)
        verify_checkout(dev, expected_branch=branch)
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
            state = json.loads(state_file.read_text())
            history = state.get("review_worktrees", [])
            history.append({"path": str(review), "sha": actual_sha})
            write_state(state_file, phase="reviewing", review_worktree=str(review),
                        review_worktrees=history, review_attempt=attempt,
                        head_sha=actual_sha)
            verify_checkout(review, expected_sha=actual_sha)
            review_text = run_agent(["opencode", "run", "--standalone", "--agent",
                                     "producer-reviewer", "--model", model,
                                     review_prompt(issue, pr, review)], review,
                                    state_dir / f"review-{attempt}.log",
                                    args.timeout_minutes * 60)
            verdict = review_verdict(review_text)
            latest = pr_details(branch, issue, repo)
            if latest["number"] != pr["number"] or latest["headRefOid"] != pr["headRefOid"]:
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
                raise Blocked("Independent reviewer could not verify the PR; "
                              f"inspect {state_dir / f'review-{attempt}.log'} for the "
                              "specific reason. Do not rerun development; PR remains open.")
            if attempt:
                raise Blocked("Independent review still requests changes after one correction cycle.")
            write_state(state_file, phase="correcting")
            verify_checkout(dev, expected_branch=branch)
            prompt = correction_prompt(issue, pr, review_text)
            if queued:
                prompt += queue_instructions
                before_build(current_pr=pr["number"])
            run_agent(["opencode", "run", "--standalone", "--agent", "build", "--model",
                       model, prompt], dev,
                      state_dir / "developer-1.log", args.timeout_minutes * 60)
            verify_checkout(dev, expected_branch=branch)
            updated = pr_details(branch, issue, repo)
            if updated["number"] != pr["number"] or updated["headRefOid"] == pr["headRefOid"]:
                raise Blocked("Correction did not update the same PR with a new commit.")
            pr = updated
            write_state(state_file, head_sha=pr["headRefOid"])
        raise Blocked("No decisive review outcome.")
    except Blocked as exc:
        stage = json.loads(state_file.read_text())["phase"]
        write_state(state_file, phase="blocked", reason=str(exc), failure_stage=stage)
        raise
    finally:
        if not queued:
            record_cleanup(repo, state_file)


def record_cleanup(repo, state_file, *, issue=None):
    try:
        _, retained = cleanup_worktrees(repo, issue=issue)
        write_state(state_file, cleanup_pending=retained)
    except (Blocked, OSError) as exc:
        print(f"CLEANUP WARNING: {exc}", file=sys.stderr)
        write_state(state_file, cleanup_pending=[str(exc)])


OWNER = REPOSITORY.split("/")[0]
QUEUE_LABEL = "agent:developer"
PRIORITIES = ("Urgent", "High", "Medium", "Low")
ISSUE_TYPES = ("Feature", "Bug", "Task", "Spike")
STATUSES = ("Backlog", "Ready", "In Progress", "In Review", "Blocked", "Done")
STATUS_COMMAND = re.compile(r"/status\s+(" + "|".join(STATUSES) + r")", re.I)
PROJECT_ITEM = """
    id isArchived project { id }
    content { __typename ... on Issue { number repository { nameWithOwner } } }
    fieldValueByName(name: "Status") {
      ... on ProjectV2ItemFieldSingleSelectValue { name optionId }
    }
"""
BOARD_QUERY = """
query($owner: String!, $number: Int!, $after: String) {
  user(login: $owner) {
    projectV2(number: $number) {
      id title closed
      field(name: "Status") {
        ... on ProjectV2SingleSelectField { options { id name } }
      }
      items(first: 100, after: $after) {
        pageInfo { hasNextPage endCursor }
        nodes { """ + PROJECT_ITEM + """ }
      }
    }
  }
}
"""
CARD_QUERY = """
query($id: ID!) {
  node(id: $id) { ... on ProjectV2Item { """ + PROJECT_ITEM + """ } }
}
"""
QUEUE_ISSUE_QUERY = """
query($owner: String!, $repo: String!, $number: Int!) {
  repository(owner: $owner, name: $repo) {
    issue(number: $number) {
      number lastEditedAt
      closedByPullRequestsReferences(first: 1, includeClosedPrs: true) {
        totalCount
        nodes { number repository { nameWithOwner } }
      }
      openImplementation: closedByPullRequestsReferences(first: 1) { totalCount }
      timelineItems(last: 1, itemTypes: [CLOSED_EVENT, REOPENED_EVENT]) {
        nodes {
          __typename
          ... on ReopenedEvent { createdAt }
          ... on ClosedEvent {
            createdAt stateReason actor { login }
            closer {
              __typename
              ... on PullRequest {
                state baseRefName repository { nameWithOwner }
                mergedBy { login }
              }
            }
          }
        }
      }
    }
  }
}
"""


def declared_prerequisites(body, native):
    """Never guess from a prose reference or silently discard a native edge."""
    lines = re.findall(r"(?im)^[ \t]*Queue prerequisites:[ \t]*(.*)$", body)
    if re.search(r"(?im)^[ \t#*-]*prerequisites[ \t]*\**:", body):
        raise Blocked("replace legacy prerequisites with the reviewed queue declaration")
    if not lines:
        if native:
            return native
        raise Blocked("declare Queue prerequisites (or reconcile legacy prerequisites)")
    if len(lines) != 1:
        raise Blocked("ambiguous Queue prerequisites declarations")
    value = lines[0].strip()
    if value == "none" and not native:
        return set()
    if not re.fullmatch(r"#[1-9][0-9]*(?:[ \t]*,[ \t]*#[1-9][0-9]*)*", value):
        raise Blocked("Queue prerequisites must list #N values, or none if no native blockers exist")
    explicit = {int(number) for number in re.findall(r"#([0-9]+)", value)}
    if native - explicit:
        raise Blocked("Queue prerequisites omits a native blocker; reconcile both sources")
    return explicit


def accepted_dependency(detail):
    """Verify human completion, not a Done card or a closed-as-not-planned issue."""
    if detail["state"] != "closed" or detail.get("state_reason") != "completed":
        return False
    graph = detail["graph"]
    events = graph["timelineItems"]["nodes"]
    if not events or events[0]["__typename"] != "ClosedEvent":
        return False
    event = events[0]
    if (event["stateReason"] != "COMPLETED" or event["createdAt"] != detail.get("closed_at")
            or graph["openImplementation"]["totalCount"]):
        return False
    closer = event["closer"]
    if closer is None:
        # Manual closure is evidence for non-PR work, not for abandoned PRs.
        return (graph["closedByPullRequestsReferences"]["totalCount"] == 0
                and (event.get("actor") or {}).get("login") == OWNER)
    return (closer["__typename"] == "PullRequest" and closer["state"] == "MERGED"
            and closer["baseRefName"] == BASE_BRANCH
            and closer["repository"]["nameWithOwner"] == REPOSITORY
            and (closer.get("mergedBy") or {}).get("login") == OWNER)


class ReadyBoard:
    def __init__(self, repo, number):
        self.repo, self.number = repo, number
        self.project_id, self.options = None, None

    def api(self, path, *, pages=False, body=None):
        args = ["gh", "api", "--hostname", "github.com", "-H",
                "X-GitHub-Api-Version: 2026-03-10"]
        if pages:
            args += ["--paginate", "--slurp"]
        if body is not None:
            args += ["-X", "POST", "-f", f"body={body}"]
        data = json_cmd([*args, path], self.repo)
        if not pages:
            return data
        if not isinstance(data, list) or not all(isinstance(page, list) for page in data):
            raise GitHubUnavailable(f"Invalid paginated GitHub response for {path}")
        return [item for page in data for item in page]

    def graphql(self, query, **variables):
        args = ["gh", "api", "graphql", "--hostname", "github.com", "-f", f"query={query}"]
        for key, value in variables.items():
            if value is not None:
                args += ["-F" if type(value) is int else "-f", f"{key}={value}"]
        payload = json_cmd(args, self.repo)
        if not isinstance(payload, dict) or payload.get("errors") or not isinstance(payload.get("data"), dict):
            raise GitHubUnavailable("Unverifiable GitHub GraphQL response.")
        return payload["data"]

    def card_status(self, item):
        if item["project"]["id"] != self.project_id:
            raise GitHubUnavailable("Project card belongs to a different board.")
        field = item["fieldValueByName"]
        if field is None:
            return None
        value = field["name"]
        if value in STATUSES and field["optionId"] != self.options.get(value):
            raise GitHubUnavailable("Project Status option changed; rerun preflight.")
        return value

    def ready(self):
        ready, cursors = {}, set()
        after = None
        while True:
            user = self.graphql(BOARD_QUERY, owner=OWNER, number=self.number, after=after)["user"]
            project = user and user["projectV2"]
            if not project or project["closed"]:
                raise GitHubUnavailable(f"Project #{self.number} is unavailable or closed.")
            options = {o["name"]: o["id"] for o in (project["field"] or {}).get("options", [])}
            if not set(STATUSES) <= options.keys():
                raise GitHubUnavailable(f"Project #{self.number} lacks required Status options.")
            if self.project_id and (self.project_id, self.options) != (project["id"], options):
                raise GitHubUnavailable("Project identity or Status configuration changed.")
            self.project_id, self.options = project["id"], options
            for item in project["items"]["nodes"]:
                if item["isArchived"] or self.card_status(item) != "Ready":
                    continue
                content = item["content"]
                if content is None or content["__typename"] == "RedactedProjectV2Item":
                    raise GitHubUnavailable("Cannot verify identity of a Ready Project item.")
                if content["__typename"] != "Issue" or content["repository"]["nameWithOwner"] != REPOSITORY:
                    continue
                number = content["number"]
                if number in ready:
                    raise GitHubUnavailable(f"Duplicate or inconsistent Ready cards for #{number}.")
                ready[number] = item["id"]
            paging = project["items"]["pageInfo"]
            if not paging["hasNextPage"]:
                return ready
            after = paging["endCursor"]
            if not after or after in cursors:
                raise GitHubUnavailable("Board pagination did not advance.")
            cursors.add(after)

    def status(self, number, card):
        item = self.graphql(CARD_QUERY, id=card)["node"]
        content = item and item["content"]
        if (not content or item["id"] != card or item["isArchived"]
                or content["__typename"] != "Issue" or content["number"] != number
                or content["repository"]["nameWithOwner"] != REPOSITORY):
            raise GitHubUnavailable(f"Cannot verify the active Project card for #{number}.")
        return self.card_status(item)

    def issue(self, number):
        detail = self.api(f"repos/{REPOSITORY}/issues/{number}")
        if (detail["number"] != number or "pull_request" in detail
                or detail["html_url"] != f"https://github.com/{REPOSITORY}/issues/{number}"):
            raise GitHubUnavailable(f"Cannot verify issue identity for #{number}.")
        return detail

    def graph_issue(self, number):
        data = self.graphql(QUEUE_ISSUE_QUERY, owner=OWNER,
                            repo=REPOSITORY.split("/")[1], number=number)
        issue = (data["repository"] or {}).get("issue")
        if not issue or issue["number"] != number:
            raise GitHubUnavailable(f"Cannot verify issue #{number} in GraphQL.")
        return issue

    def dependency(self, number):
        try:
            detail = self.issue(number)
        except GitHubUnavailable as exc:
            if "HTTP 404" in str(exc):
                return False  # Missing or invisible prerequisite: this issue must wait.
            raise
        if detail["state"] != "closed":
            return False
        detail["graph"] = self.graph_issue(number)
        return accepted_dependency(detail)

    def status_commands(self, number):
        comments = self.api(f"repos/{REPOSITORY}/issues/{number}/comments?per_page=100", pages=True)
        commands = [
            c for c in comments if (c.get("user") or {}).get("login") == OWNER
            and STATUS_COMMAND.fullmatch(c["body"].strip())
        ]
        return sorted(commands, key=lambda c: (c["created_at"], c["id"]), reverse=True)

    def post_comment(self, number, body):
        comment = self.api(f"repos/{REPOSITORY}/issues/{number}/comments", body=body)
        if (comment["user"]["login"] != OWNER or comment["body"] != body
                or type(comment["id"]) is not int):
            raise GitHubUnavailable(f"Could not verify owner-authored comment for #{number}.")
        return comment["id"]

    def transition(self, number, card, status, *, in_place_of, from_status):
        commands = self.status_commands(number)
        if not commands or commands[0]["id"] != in_place_of:
            raise GitHubUnavailable(f"#{number}: owner status command changed; will not overwrite it.")
        if self.status(number, card) not in from_status:
            raise GitHubUnavailable(f"#{number}: Project status changed; will not overwrite it.")
        posted = self.post_comment(number, f"/status {status}")
        for attempt in range(25):
            current = self.status(number, card)
            if current == status:
                commands = self.status_commands(number)
                if (not commands or commands[0]["id"] != posted
                        or commands[0]["body"].strip() != f"/status {status}"):
                    raise GitHubUnavailable(f"#{number}: {status} command was superseded or cannot be verified.")
                # A newer owner command can arrive between our last read and POST.
                previous = commands[1]["id"] if len(commands) > 1 else None
                if previous != in_place_of:
                    raise GitHubUnavailable(
                        f"#{number}: status conflict: command {posted} followed {previous}, not "
                        f"expected command {in_place_of}. Reconcile the owner commands and board before resuming.")
                return posted
            if current not in from_status:
                break
            if attempt < 24:
                time.sleep(5)
        raise GitHubUnavailable(
            f"#{number}: {status} not verified (last board value: {current}); inspect "
            "Sync GitHub Project Status, PROJECT_NUMBER and the owner comment before resuming.")


def implementation_pr(pr, number):
    return (closes_issue(pr["body"] or "", number)
            or re.match(rf"agent/issue-{number}(?:-|$)", pr["head"]["ref"]))


def queue_candidate(board, number, *, claim=None, current_pr=None):
    detail = board.issue(number)
    if detail["state"] != "open":
        raise Blocked("issue is not open")
    if detail["assignees"]:
        raise Blocked("has a GitHub assignee; not Developer-owned")
    if not any(label["name"] == QUEUE_LABEL for label in detail["labels"]):
        raise Blocked(f"missing {QUEUE_LABEL} assignment")
    issue_type = (detail.get("type") or {}).get("name")
    if issue_type == "Design Decision":
        raise Blocked("Design Decision; human-owned")
    if issue_type not in ISSUE_TYPES:
        raise Blocked("missing/unknown native Type; use the metadata backfill")
    if not (detail.get("body") or "").strip() or detail["locked"]:
        raise Blocked("missing requirements or issue is locked")
    graph = board.graph_issue(number)
    linked = graph["closedByPullRequestsReferences"]
    if linked["totalCount"]:
        expected = {"number": current_pr, "repository": {"nameWithOwner": REPOSITORY}}
        if current_pr is None or linked["totalCount"] != 1 or linked["nodes"] != [expected]:
            raise Blocked("unexpected linked implementation PR; inspect it instead")
    fields = board.api(f"repos/{REPOSITORY}/issues/{number}/issue-field-values")
    if not isinstance(fields, list):
        raise GitHubUnavailable(f"Cannot verify issue fields for #{number}.")

    def option(name):
        values = [f for f in fields if f.get("issue_field_name") == name]
        if len(values) == 1 and values[0]["data_type"] == "single_select":
            return (values[0].get("single_select_option") or {}).get("name")
        return None

    priority, workstream = option("Priority"), option("Workstream")
    if priority not in PRIORITIES or not workstream:
        raise Blocked("missing/unknown native Priority or Workstream; use the metadata backfill")
    native = set()
    for dependency in board.api(
            f"repos/{REPOSITORY}/issues/{number}/dependencies/blocked_by?per_page=100", pages=True):
        linked = dependency["number"]
        if dependency["html_url"] != f"https://github.com/{REPOSITORY}/issues/{linked}":
            raise Blocked("external or unverifiable native prerequisite; reconcile with the owner")
        native.add(linked)
    dependencies = declared_prerequisites(detail["body"], native)
    if number in dependencies:
        raise Blocked("issue cannot depend on itself")
    commands = board.status_commands(number)
    if claim is not None:
        if (not commands or commands[0]["id"] != claim
                or commands[0]["body"].strip() != "/status In Progress"
                or commands[0]["updated_at"] != commands[0]["created_at"]):
            raise Blocked("owner changed or withdrew the claim")
        commands = commands[1:]
    command = commands[0] if commands else None
    boundary = max([graph["lastEditedAt"] or ""]
                   + [e["createdAt"] for e in graph["timelineItems"]["nodes"]])
    if (not command or command["body"].strip().casefold() != "/status ready"
            or command["updated_at"] != command["created_at"]
            or command["created_at"] <= boundary):
        raise Blocked("needs a fresh, unedited owner /status Ready after issue edits or reopening")
    return {"number": number, "title": detail["title"], "body": detail["body"],
            "url": detail["html_url"], "issue_type": issue_type,
            "priority": priority, "workstream": workstream, "dependencies": dependencies,
            "status_comment": command["id"], "last_edit": graph["lastEditedAt"]}


def run_home(repo):
    return repo.parent / f".{repo.name}-agent-runs"


def local_assignment_exists(board, number, trees):
    return ((run_home(board.repo) / f"issue-{number}").exists()
            or any((run_home(board.repo)).glob(f"issue-{number}-review-pr-*"))
            or any(re.match(rf"(?:{re.escape(board.repo.name)}-(?:agent|review|issue)-{number}(?:-|$))",
                            tree["path"].name)
                   or re.match(rf"refs/heads/agent/issue-{number}(?:-|$)", tree.get("branch", ""))
                   for tree in trees))


def open_prs(board):
    return board.api(f"repos/{REPOSITORY}/pulls?state=open&per_page=100", pages=True)


def queue_snapshot(board):
    ready = board.ready()
    candidates, eligible, accepted = {}, [], {}
    prs, trees = open_prs(board), registered_worktrees(board.repo)
    for number, card in sorted(ready.items()):
        try:
            if local_assignment_exists(board, number, trees):
                raise Blocked("local run/worktree exists; resolve manually")
            if any(implementation_pr(pr, number) for pr in prs):
                raise Blocked("implementation PR already open")
            detail = candidates[number] = queue_candidate(board, number)
        except GitHubUnavailable:
            raise
        except Blocked as exc:
            print(f"SKIP #{number}: {exc}", flush=True)
            continue
        for dependency in sorted(detail["dependencies"]):
            if dependency not in accepted:
                accepted[dependency] = board.dependency(dependency)
        waiting = sorted(n for n in detail["dependencies"] if not accepted[n])
        if waiting:
            print(f"WAIT #{number}: awaiting owner acceptance of "
                  + ", ".join(f"#{n}" for n in waiting), flush=True)
        else:
            eligible.append((detail, card))
    return sorted(eligible, key=lambda pair: (
        -sum(pair[0]["number"] in c["dependencies"] for c in candidates.values()),
        PRIORITIES.index(pair[0]["priority"]), pair[0]["number"]))


def dispatch_ready(args, board, model, detail, card):
    number = detail["number"]
    state_dir = run_home(board.repo) / f"issue-{number}"
    # Persist intent before posting. A killed runner must not silently reclaim.
    state_dir.mkdir(parents=True, exist_ok=False)
    state = state_dir / "state.json"
    write_state(state, phase="claiming", issue=number, model=model, title=detail["title"],
                project=board.number, card=card, ready_comment=detail["status_comment"],
                prerequisites=sorted(detail["dependencies"]))
    claim = None
    interrupted = False

    def before_build(*, current_pr=None):
        try:
            if not all(board.dependency(n) for n in sorted(detail["dependencies"])):
                raise Blocked("a prerequisite is no longer accepted")
            if any(implementation_pr(pr, number) and pr["number"] != current_pr
                   for pr in open_prs(board)):
                raise Blocked("another implementation PR exists")
            expected = ("In Progress", "In Review") if current_pr is not None else ("In Progress",)
            if board.status(number, card) not in expected:
                raise Blocked("Project status changed since claim")
            if queue_candidate(board, number, claim=claim, current_pr=current_pr) != detail:
                raise Blocked("issue scope or Ready authorization changed since claim")
        except Blocked as exc:
            raise GitHubUnavailable(f"#{number}: claim could not be revalidated: {exc}") from exc

    try:
        claim = board.transition(number, card, "In Progress",
                                 in_place_of=detail["status_comment"], from_status=("Ready",))
        write_state(state, verified_status="In Progress", claim_comment=claim)
        print(f"#{number}: verified In Progress on Project #{board.number}.", flush=True)
        develop_and_review(args, board.repo, model, detail, state_dir, before_build=before_build)
        handoff = board.transition(number, card, "In Review", in_place_of=claim,
                                   from_status=("In Progress", "In Review"))
        write_state(state, verified_status="In Review", handoff_comment=handoff)
        print(f"#{number}: verified In Review on Project #{board.number}.", flush=True)
    except (GitHubUnavailable, KeyError, TypeError, ValueError, IndexError) as exc:
        write_state(state, phase="status_unverified", reason=str(exc))
        raise
    except (KeyboardInterrupt, Blocked) as exc:
        interrupted = isinstance(exc, (Interrupted, KeyboardInterrupt))
        reason = str(exc) or "Operator stopped the queue."
        phase = "interrupted" if interrupted else "blocked"
        write_state(state, phase=phase, reason=reason)
        if claim is not None:
            try:
                # Use runner-owned text rather than echoing credential-bearing CLI output.
                evidence = json.loads(state.read_text())
                stage = evidence.get("failure_stage", "preparing")
                board.post_comment(number, f"Queue run {phase} during {stage}. "
                                   f"Inspect issue-{number}/state.json and the corresponding host transcript. "
                                   "Use review-only if a PR exists; do not restart Build automatically.")
                handoff = board.transition(number, card, "Blocked", in_place_of=claim,
                                           from_status=("In Progress", "In Review"))
                write_state(state, verified_status="Blocked", handoff_comment=handoff)
                print(f"#{number}: verified Blocked on Project #{board.number}.", flush=True)
            except GitHubUnavailable as status_error:
                write_state(state, status_error=str(status_error))
                raise
        print(f"#{number} {phase.upper()}: {reason} Logs/state: {state_dir}", flush=True)
        return 130 if interrupted else 2
    else:
        record_cleanup(board.repo, state, issue=number)
    return 0


def stop_queue(_signal, _frame):
    raise KeyboardInterrupt


def queue_mode(args):
    repo = Path(args.repo).expanduser().resolve()
    model = require_model(args.model)
    version, help_text = host_preflight(repo)
    if not all(flag in help_text for flag in ("--standalone", "--model", "--agent")):
        raise Blocked("Installed OpenCode does not advertise the runner's required flags.")
    models = run_cmd(["opencode", "models"], repo)
    if model.split("#", 1)[0] not in models.splitlines():
        raise Blocked("Configured model was not listed by OpenCode; verify the connected account/model.")
    if not args.dry_run:
        trees = registered_worktrees(repo)
        if not trees or trees[0]["path"] != repo:
            raise Blocked("Run the live queue against the primary checkout via --repo.")
        for tree in trees[1:]:
            path = tree["path"]
            if (path.name.startswith((f"{repo.name}-agent-", f"{repo.name}-review-", f"{repo.name}-issue-"))
                    or tree.get("branch", "").startswith("refs/heads/agent/issue-")):
                if worktree_in_use(path):
                    raise Blocked(f"An agent/review checkout is still in use: {path}.")
    board = ReadyBoard(repo, args.project)
    if board.api("user")["login"] != OWNER:
        raise GitHubUnavailable(f"Queue requires gh authentication as {OWNER}.")
    configured = run_cmd(["gh", "variable", "get", "PROJECT_NUMBER", "--repo", REPOSITORY], repo)
    if configured != str(args.project):
        raise GitHubUnavailable("--project must match the status workflow's PROJECT_NUMBER.")
    print(f"Queue preflight: Project #{args.project}; OpenCode {version}; model {model}.", flush=True)
    while True:
        eligible = queue_snapshot(board)
        if args.dry_run:
            print("DRY RUN: eligible in order: "
                  + (", ".join(f"#{d['number']}" for d, _ in eligible) or "(none)")
                  + ". No writes or AI sessions.")
            return 0
        if not eligible:
            if args.once:
                print("No eligible Ready issues; no assignment started.", flush=True)
                return 0
            print(f"No eligible Ready issues; idle for {args.poll_seconds}s.", flush=True)
            time.sleep(args.poll_seconds)
            continue
        detail, card = eligible[0]
        number = detail["number"]
        # A checkout/origin failure is a host problem, not a failure of this assignment.
        run_cmd(["git", "fetch", "origin", BASE_BRANCH], repo, timeout=120)
        run_cmd(["git", "rev-parse", "--verify", f"origin/{BASE_BRANCH}"], repo)
        try:
            current = queue_candidate(board, number)
        except GitHubUnavailable:
            raise
        except Blocked as exc:
            print(f"SKIP #{number}: eligibility changed before claim: {exc}", flush=True)
            continue
        if (current != detail
                or not all(board.dependency(n) for n in sorted(current["dependencies"]))
                or any(implementation_pr(pr, number) for pr in open_prs(board))
                or local_assignment_exists(board, number, registered_worktrees(repo))
                or board.status(number, card) != "Ready"):
            continue
        result = dispatch_ready(args, board, model, detail, card)
        if args.once or result == 130:
            return result


@contextmanager
def runner_lock():
    """One writer on this host/account, even across linked worktrees/clones."""
    path = Path.home() / ".local/state/the-producer/runner.lock"
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with path.open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise Blocked(f"Another runner is active ({path}).") from exc
        yield


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("issue", type=int, nargs="?", help="approved GitHub issue number")
    parser.add_argument("--cleanup-worktrees", action="store_true", help="clean idle completed worktrees")
    parser.add_argument("--repo", default=".", help="path to the main repository checkout")
    parser.add_argument("--model", help="explicit OpenAI model ID from OpenCode")
    parser.add_argument("--dry-run", action="store_true", help="preflight only; no writes or AI runs")
    parser.add_argument("--approve-issue", action="store_true", help="authorize this issue's execution")
    parser.add_argument("--queue", action="store_true", help="opt in to the owner-authorized Ready queue")
    parser.add_argument("--project", type=int, help="owner Project number (must match PROJECT_NUMBER)")
    parser.add_argument("--poll-seconds", type=int, help="idle interval (default: 60 seconds)")
    parser.add_argument("--once", action="store_true", help="queue: attempt at most one assignment, no idle wait")
    parser.add_argument("--retry-blocked", action="store_true",
                        help="archive a previous blocked run with no PR after safe cleanup")
    parser.add_argument("--review-pr", type=int, help="independently review an existing open PR without running Build")
    parser.add_argument("--timeout-minutes", type=int, default=60,
                        help="timeout per model session (default: 60)")
    args = parser.parse_args(argv)
    if args.queue:
        if (args.issue is not None or args.approve_issue or args.cleanup_worktrees
                or args.retry_blocked or args.review_pr is not None or not args.model
                or not args.project or args.project < 1 or not 1 <= args.timeout_minutes <= 180
                or (args.poll_seconds is not None and args.poll_seconds < 1)
                or (args.once and args.dry_run)):
            parser.error("--queue requires --project and --model; use --dry-run or --once, or poll continuously")
        args.poll_seconds = args.poll_seconds or 60
        previous = signal.signal(signal.SIGTERM, stop_queue)
        try:
            if args.dry_run:
                return queue_mode(args)
            with runner_lock():
                return queue_mode(args)
        except KeyboardInterrupt:
            print("Queue interrupted; no further assignments. Inspect retained run state if a claim started.",
                  file=sys.stderr)
            return 130
        except (Blocked, OSError, KeyError, ValueError, TypeError, IndexError) as exc:
            print(f"QUEUE STOPPED: {exc}", file=sys.stderr)
            return 2
        finally:
            signal.signal(signal.SIGTERM, previous)
    if args.project is not None or args.poll_seconds is not None or args.once:
        parser.error("--project, --poll-seconds and --once require --queue")
    if args.cleanup_worktrees:
        if (args.issue is not None or args.model or args.dry_run or
                args.approve_issue or args.retry_blocked or args.review_pr is not None):
            parser.error("--cleanup-worktrees takes no issue/model/approval arguments")
        try:
            repo = Path(args.repo).expanduser().resolve()
            actual = Path(run_cmd(["git", "rev-parse", "--show-toplevel"], repo)).resolve()
            if actual != repo or repo.name != "The-Producer":
                raise Blocked("Cleanup must run from the main The-Producer checkout.")
            remote = run_cmd(["git", "remote", "get-url", "origin"], repo)
            if not re.search(r"(?:github\.com[:/])williamwhorton/The-Producer(?:\.git)?$", remote):
                raise Blocked("Origin is not the expected The-Producer repository.")
            with runner_lock():
                _, retained = cleanup_worktrees(repo)
            return 2 if retained else 0
        except (Blocked, OSError) as exc:
            print(f"BLOCKED: {exc}", file=sys.stderr)
            return 2
    if args.retry_blocked and args.dry_run:
        parser.error("--retry-blocked must not be combined with --dry-run")
    if args.issue is None or args.issue < 1 or not args.model or not 1 <= args.timeout_minutes <= 180:
        parser.error("provide ISSUE and --model; timeout must be 1–180 minutes")
    if args.review_pr is not None and (args.review_pr < 1 or args.retry_blocked or args.approve_issue):
        parser.error("--review-pr requires an open PR number and cannot perform development/retry")
    try:
        execute = review_existing_pr if args.review_pr is not None else orchestrate
        if args.dry_run:
            return execute(args)
        with runner_lock():
            return execute(args)
    except (Blocked, OSError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
