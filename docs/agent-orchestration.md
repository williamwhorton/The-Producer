# Lead-agent orchestration: implementation options and pilot contract

**Status:** Option A is a **supervised pilot** (`tools/orchestrate.py`). Board-driven single assignments completed #30–32. Opt-in continuous execution (#111) needs separate live acceptance before closing #96. Other options remain proposals. This does **not** authorize autonomous backlog execution, change permissions, or certify the workflow as production-ready.
**Environment:** The Creative Director runs OpenCode CLI on Bazzite Linux with ChatGPT-connected cloud models. Verify the installed version, effective permissions and account/model before launching a pilot.

## Objective and authority

The Creative Director should be able to ask: `Take approved Issue #N through development and independent review.` The Lead verifies prerequisites and coordinates a **separate Build developer**, a **fresh independent Reviewer**, and any bounded corrections. It hands off a verified PR and remaining acceptance questions to the Creative Director. It may prepare/reconcile existing issues and propose missing work, but **cannot self-approve game design, start unapproved work, change production architecture, merge PRs or introduce paid API charges**.

Authoritative issue body/parent fixtures, PR diffs, tests, screenshots, status comments and ADRs are the durable exchange format. A Developer's self-reported success is not the independent QA verdict. The reviewer must retrieve the issue and inspect the actual head commit/diff, and report `Approve`, `Request changes` or `Unable to verify` as a technical recommendation.

## Routine permissions (broker intentionally deferred)

The project-level `opencode.jsonc` uses ordered OpenCode V2 rules to preapprove routine inspect/test commands, plus normal Build agent commit, `agent/*` feature-branch push and PR creation. Exceptional commands still require approval, and dangerous operations such as force pushes, destructive resets and PR merges are explicitly denied for Build. The Reviewer profile has its own read-only shell allowances/denials. Do not use `--auto`, install an API permission broker, or broaden to unconditional shell execution.

After pulling the config, inspect the **effective** permissions locally using `opencode debug agent build` and `opencode debug agent producer-reviewer`. Local/global policy, saved approvals and MCP-specific permission requests may influence the actual result. Noninteractive OpenCode runs still cannot solicit permission decisions through the runner. This is intentionally a scoped reduction in prompt frequency, **not** a full solution to every permission request.

## Automatic worktree cleanup and local Godot testing

**Default behavior:** When a manual supervised runner invocation finishes (success, review rejection or blocked run), the runner automatically checks **all** known agent worktrees and safely removes eligible finished ones. The Ready pilot instead retains its worktrees on failure and checks only its own worktrees for safe cleanup after verified handoff. The runner reports how many were removed and why any were retained. The primary checkout, PRs, local review logs/state and repository history are never deleted. A failed cleanup is reported, not ignored.

**One-time cleanup of existing worktrees** from previous runs (including the previously merged #13 and #14 prototype worktrees) needs only one command **after this PR is merged**:

```sh
cd ~/Projects/The-Producer
git switch main
git pull --ff-only
python3 tools/orchestrate.py --cleanup-worktrees
```

The cleanup command requires neither an issue number nor a model and starts **no AI agents**. It examines registered sibling worktrees matching the project's agent/issue/review naming conventions, not arbitrary directories. It removes a candidate only if:
- No running Linux process has its working directory inside the worktree.
- There are no uncommitted/untracked files, and ignored files are limited to disposable Godot `.godot/` caches (including caches nested under `spikes/*/`). These generated cache directories are removed **only after** commit preservation is verified; all other ignored files are retained.
- The worktree's HEAD is proved preserved in the matching GitHub PR (legacy issue worktrees must have a **merged** PR), or a fresh agent branch has no commits beyond `origin/main`.
- A detached review checkout has its expected commit recorded in runner state; for older runs that did not record every Reviewer commit, its commit must be verified as an ancestor of the head of a **merged PR that closes the same issue**, using the original issue's recorded PR URL.

Any unsafe or unverifiable checkout is **retained with an explicit explanation**. No `git clean`, `git reset --hard`, force-removal, or directory-level `rm` is used. Logs/state under `../.The-Producer-agent-runs/issue-N/` are intentionally retained as a durable audit trail; removing worktrees does not reset the runner's duplicate-issue protection.

After pulling merged work to `main`, test from the **single stable checkout**:

```sh
godot --path "$PWD/spikes/issue-4-2d"
godot --path "$PWD/spikes/issue-4-3d"
```

No issue branch checkout or separate Godot worktree is needed.

## Re-review an existing PR without re-running development

An earlier Issue #15 attempt produced [PR #79](https://github.com/williamwhorton/The-Producer/pull/79), but independent review stopped before inspecting the code because the Reviewer bundled several repository checks into **one composite shell command**. OpenCode 2.4.1 treated that entire string as an `ask` operation and automatically rejected it in noninteractive mode. No code defect or failed test was established by that verdict.

The Reviewer profile now **requires separate single-command shell calls** for its allowlisted read-only checks, including `pwd`, `git rev-parse --show-toplevel`, `git rev-parse HEAD`, `git branch --show-current`, and `git status --short --branch`. It must not combine those with `;`, `&&`, `printf`, pipes or redirects. Do not widen to `shell: *` / `external_directory: *` approval, and do not introduce the deferred permission broker.

To retry the **review only** of an existing open PR (with no additional Build session):

```sh
cd ~/Projects/The-Producer
git switch main
git pull --ff-only
python3 tools/orchestrate.py 15 --review-pr 79 \
  --model 'openai/YOUR-VERIFIED-MODEL#high'
```

Replace the model placeholder with the verified ChatGPT-connected model ID. For a no-write preflight, add `--dry-run`. The command validates the exact Issue #15/PR #79 relationship, expected branch, unchanged PR head, and real detached review SHA. It creates one new Reviewer session in a temporary worktree and records its transcript under a new issue-scoped review-only directory in `../.The-Producer-agent-runs/`. **It does not create another development branch, amend the PR, merge anything, or erase previous blocked-run transcripts.** At exit it performs the same safe worktree cleanup as the main runner. A Reviewer's `APPROVE` verdict is independent technical evidence, not Creative Director acceptance.

If an individually allowlisted command is still rejected, preserve the new transcript and report the exact command/denial; no repeated developer run is needed. Any substantive `REQUEST_CHANGES` finding should be addressed against the existing PR, not by creating a duplicate.

## Correct worktree startup and safe retry after a blocked run

**Root cause addressed:** Python's `subprocess.Popen(cwd=...)` changes the launched process's working directory but does **not** rewrite the inherited `PWD` environment variable. Some OpenCode `run` versions prefer `PWD` to process cwd and can therefore initialize a new session in the primary checkout on `main`, even though the runner launched the CLI for a sibling worktree. The runner now sets **both the child cwd and `PWD` to the same resolved worktree path**, and checks Git's actual top-level directory and branch before and after Build, before correction, and verifies the Reviewer's detached HEAD matches the exact PR commit. Agent instructions also demand an independent startup identity check and stop rather than change files on an unexpected branch.

**Recovering the previously blocked Issue #15 run:** Once this change is merged and you have confirmed Issue #15 is still approved and no implementation PR exists, run the standard supervised assignment with `--retry-blocked`:

```sh
cd ~/Projects/The-Producer
git switch main
git pull --ff-only
python3 -m unittest discover -s tests -p 'test_orchestrate.py' -v
python3 tools/orchestrate.py 15 --model 'openai/YOUR-VERIFIED-MODEL#high' --approve-issue --retry-blocked
```

Replace the model placeholder with the **exact** working ChatGPT-connected model ID from `opencode models`. The retry flag only applies if the previous state is explicitly **blocked with no PR**. It safely attempts cleanup of old inactive worktrees, refuses any old worktree with changes or unpreserved commits, archives previous state/transcripts instead of deleting them, then starts a fresh branch/worktree and fresh Build session. If a run is still active, has a PR, or has an unsafe checkout, it refuses to retry. Do **not** delete state files, permit cross-directory access, or disable approval prompts to work around the problem.

The fix has **automated regression tests** for a stale parent `PWD`, wrong worktree/branch, exact detached reviewer SHA and conservative blocked-run recovery. A real OpenCode 2.4.1 execution on the Creative Director's computer is still necessary to validate the provider/session behavior; the Python test cannot prove OpenCode itself has no other worktree bugs.

## Supervised runner: commands and guardrails

### Read-only Ready selection

From a checkout of this repository on the trusted host, with the existing `gh` login and configured `PROJECT_NUMBER`, run `python3 tools/read_ready.py` for the original Ready diagnostic or `python3 tools/read_ready.py --select` for the selection report. Use the runner's normal primary checkout and local run location for a complete duplicate-work check; a linked worktree uses that same checkout's run directory. The report is a snapshot, not a claim or permission to dispatch, and performs no writes.

The Lead should only place a bounded, approved Developer deliverable in Ready with `agent:developer`, no human assignees, a native Feature/Bug/Task/Spike Type, native Priority and Workstream, and the native **Requires human approval** single-select field set to **No** (no further approval outstanding). The diagnostic lists all selected Workstream options; the selector requires one or more valid named selections (and also accepts a valid single-select Workstream). Missing or ambiguous metadata and any approval value other than a valid single-select **No** do not authorize selection. Keep unsettled scope and known unresolved prior work out of selection. No status-comment history or issue-body copies of native fields are used.

Before making an issue selectable, the Lead verifies the approved implementation scope and reconciles all prerequisites in the body to native **Blocked by** links. Remove obsolete or unreconciled prerequisite instructions, then put exactly one of these plain standalone declarations on the first nonempty line of the issue body, before the scope:

- `Selection-ready implementation; prerequisites: none` — reviewed, with no prerequisites.
- `Selection-ready implementation; prerequisites: native` — reviewed, with all prerequisites represented by native links.

The line must match exactly: no indentation, quoting, or surrounding Markdown. Leading blank lines are fine; a declaration later in the body, including in a fenced example, does not count. This is a triage declaration, not a second dependency graph or a grant of new approval. Remove or update it if scope or prerequisites change. The selector checks the declaration against the visible links and GitHub's total and skips an absent or inconsistent declaration/count. It does not interpret links, references or headings in arbitrary prose.

Ready publishes authorized, specified work, including assignments with unfinished native prerequisites. For dispatch, every prerequisite must be closed as **Completed**. For code work, the latest closure must directly identify a PR merged into this repo's `main` by `williamwhorton`. For known non-code work only, an owner-authored (and not last edited by someone else) issue may use the exact standalone declaration `Selection completion: non-code` under the same first-nonempty-line rule; its latest manual **Completed** closure must be by the owner. The selector reports `WAIT` for open, inaccessible, external, not-planned or otherwise unverified prerequisites and can still recommend independent eligible work. The Lead handles exceptions instead of replaying history.

Drafts and other open implementation PRs found by GitHub closing link or `agent/issue-N` head, and retained local runner directories or registered issue worktrees, exclude the assignment. The selector checks native links from the PR and issue sides, including links to PRs targeting another repository. It does not interpret PR body text as a link. Archived retry logs are retained and are not active runs. The diagnostic does not search or repair abandoned history; the Lead must resolve any known ambiguity before declaring the assignment ready. Eligible issues are ranked first by how many unique, otherwise-valid Ready issues would have **no other** unsatisfied direct prerequisite after their acceptance, then by native Priority, then by ascending issue number. Successors still wait until acceptance. API/auth errors exit nonzero instead of reporting an empty queue.

### Ready pilot: one explicitly launched assignment

On the trusted Linux host, set `PROJECT_NUMBER` to the same configured number that Actions uses, and verify `gh` access and the exact ChatGPT-connected model with `opencode models`. From the **primary repository root**, run a read-only preview:

```sh
python3 tools/run_ready.py --model openai/gpt-6.2-sol --dry-run
```

Use the exact model ID available on your host. No eligible work exits successfully without creating a run or invoking agents. An API/auth/configuration failure is not an empty queue. After the pilot code is merged, the Lead should prepare one approved prototype using the native fields, reconciled blockers, and first-line declaration above. Proceed only when the preview recommends that issue. For one separately authorized invocation, use the number confirmed in the preview:

```sh
read -r -p "Approved prototype issue number: " PILOT_ISSUE
python3 tools/run_ready.py --model openai/gpt-6.2-sol --expect-issue "$PILOT_ISSUE"
```

`--expect-issue` refuses a different recommendation; it never forces selection. The live command requires `gh` authentication as `williamwhorton`. Do not start a parallel manual runner, review-only run, or cleanup while this pilot is running. The primary checkout's local pilot lock excludes concurrent pilots; a scan also refuses known active or unfinished runs and in-use agent worktrees. The lock is not a remote or cross-host claim and does not coordinate with manual invocations.

The host rechecks the selected issue's eligibility and actual Ready card before posting `/status In Progress`, then waits for the Project field to reflect it and verifies it again immediately before Build. Status reads have a bounded verification window, not a queue loop; GitHub comment/Actions updates are asynchronous and not atomic with the card read. The host stops on observed withdrawal, ambiguous status or API failure. Build does not post a duplicate status command. The non-draft PR event owns `In Review`; a missing transition stops the handoff instead of replaying status commands or treating a technically approved PR as ready for acceptance. Consult the status workflow's Actions logs and the current card if verification fails.

Any correction Build requires a fresh `In Review` read immediately before launch. If the card is missing, has a different status, or cannot be verified, the host stops without launching the correction or writing another status. For handoff, the host re-reads the PR after verifying `In Review` and requires the same PR number and reviewed SHA. Success reports that verified head, technical verdict and logs, with human acceptance and merge still pending. A runner failure retains any PR, local state, transcripts and worktrees. For failures other than board verification, if the card is still `In Progress`, the host posts and verifies `/status Blocked`; otherwise it leaves the card alone (including `In Review` on a failed review) and reports the problem for owner triage. `In Review` by itself is not an approval. A single-assignment run ends after this handoff; neither mode retries a failed assignment, merges or closes an issue.

### Ready pilot: opt-in continuous execution

From the primary checkout on `main`, with the existing `PROJECT_NUMBER`, preview the actual queue before authorizing a session:

```sh
python3 tools/run_ready.py --model openai/gpt-6.2-sol --dry-run
python3 tools/run_ready.py --model openai/gpt-6.2-sol --continuous
```

Run the second command only if you intend to authorize **all** approved, eligible Ready assignments as they become available, not just the preview's recommendation. `--dry-run` takes one read-only snapshot and cannot be combined with `--continuous`. `--expect-issue` works for a single assignment or preview only. `--poll-seconds` is continuous-only (whole seconds, 1–3600; default 60).

The session holds the same local lock across assignments and idle waits. A default live invocation must acquire that lock even if the queue is empty; `--dry-run` does not take the lock. Continuous mode checks local run state and worktrees again, then refreshes the board after each verified handoff without waiting for merge to start independent work. An open PR or unresolved run still excludes a duplicate; dependent work waits for verified prerequisite acceptance, not technical approval. If nothing is eligible, it reports wait/skip reasons and polls without launching models or promoting Backlog. Each assignment uses the existing fresh `origin/main` fetch for its own worktree. Stop the session **before switching branches, pulling/updating the primary checkout, or running any manual orchestrate, review or cleanup command**. The lock only covers live Ready invocations from this host; it does not coordinate with manual runners or other hosts.

Ctrl+C or SIGTERM stops the session; an active OpenCode process group is stopped and its artifacts retained. This includes interruption while draining the transcript after the process leader exits. If the bounded drain expires, the group is stopped and the assignment fails rather than handing off incomplete output. If an assignment with local state is interrupted before verified handoff, its local phase becomes `blocked` with a reason. An interruption does not post another status command, and interruption during cleanup does not undo a verified handoff. A failed assignment (including usage limits or failed review), uncertain claim/handoff, observed withdrawal, API/authentication error or invalid local state stops the session. A GitHub API error during post-handoff cleanup also stops the session before the next selection; ordinary worktree retention (such as for untracked files) is not an API failure. No automatic retry, model/payment fallback or resumption. Inspect the actual card, Actions logs, `state.json`, transcripts, worktrees and any PR before deciding what to do:

- If there is a PR, preserve it. Resolve findings on that PR or use [review-only recovery](#re-review-an-existing-pr-without-re-running-development) if the owner reauthorizes review. Do not restart Build on a new assignment for the issue.
- If the run is explicitly `blocked` with no PR, the owner must reauthorize that issue before manually using `--approve-issue --retry-blocked` with the [existing archive checks](#correct-worktree-startup-and-safe-retry-after-a-blocked-run). If local state is unfinished or unverifiable, a worktree is unsafe, or the card and artifacts disagree, stop for owner triage; do not delete or edit state to force a restart. Reconcile any stale card with the [status workflow procedure](project-status-automation.md) before returning to the pilot.

Offline tests do not establish Actions delivery, permissions, or multiple real assignments. If only one approved real issue is available, record the live handoff and idle behavior separately from the offline multiple-assignment evidence.

### Explicit single-issue execution

The initial runner is standard-library Python 3 (no pip dependencies). From the main checkout **after this PR merges**:

```sh
cd ~/Projects/The-Producer
git switch main
git pull --ff-only
python3 -m unittest discover -s tests -p 'test_orchestrate.py' -v
opencode models
```

Choose the **exact OpenAI model ID** from the working OpenCode sign-in. A previously selected interactive model does not necessarily become the default of a new CLI session; use an explicit ID and variant. The following **placeholder must be replaced**, not pasted literally:

```sh
python3 tools/orchestrate.py 14 --model 'openai/YOUR-VERIFIED-MODEL#high' --dry-run
```

The dry-run checks local commands, GitHub repo/auth, issue contents, existing open PRs, reviewer profile, and OpenCode CLI availability; **it does not call a model, fetch branches, write a worktree, or launch Build**. Once you have explicitly approved the issue's requirements and checked its dependencies and Ready status:

```sh
python3 tools/orchestrate.py 14 --model 'openai/YOUR-VERIFIED-MODEL#high' --approve-issue
```

For a real run, the script (1) requires the explicit `--approve-issue` authorization, (2) creates its own branch and sibling worktree from freshly fetched `origin/main`, (3) runs `opencode run --standalone --agent build --model ...`, (4) requires an open non-draft PR on the expected branch with `Closes #N`, a nonempty diff, an Evidence/Verification/Tests section and **Human Testing** steps for final acceptance, (5) creates a **separate detached worktree at the exact PR SHA** and runs a fresh `producer-reviewer` primary agent, and (6) allows one corrective Build pass followed by fresh review. It validates the PR head hasn't changed during review and only returns "ready for acceptance" for a single explicit `REVIEW_VERDICT: APPROVE`. The Reviewer verdict remains a technical recommendation; the human still visually accepts and merges.

**Local state and cleanup:** State/transcripts remain under `../.The-Producer-agent-runs/issue-N/`, outside Git, while eligible worktrees are removed automatically on run exit. The runner records every Reviewer worktree and cleanup exceptions in `state.json`. Uncommitted, unpushed, in-use or unverifiable worktrees are retained and clearly reported. It does not automatically resume an interrupted run or delete audit records; see the cleanup command above.

**Important limitations:** This is not a headless permission-approval mechanism. It does **not** pass `--auto`, and any OpenCode permission request that cannot be serviced from the CLI will cause a failure or timeout, leaving evidence for diagnosis. It checks an explicit `openai/...` model ID and rejects `OPENAI_API_KEY` in the shell environment, but **cannot prove which OpenAI credential/payment route the saved OpenCode account uses**; confirm ChatGPT plan access before a run. Logs can contain sensitive output and should not be shared or committed. The script checks the issue is open and has content; `--approve-issue` is the human affirmation that the issue and dependencies are approved, **not** an automated GitHub Projects Ready-field check. It does not independently interpret game acceptance criteria or execute arbitrary test suites: those remain Developer/Reviewer responsibilities, and PR evidence text alone is not proof. No autonomous backlog selection, event listening, automatic Project status writes, or PR merges.

## Candidate approaches

### A. Local CLI process runner (recommended first)

A small Python script or similarly simple executable, invoked intentionally by the Creative Director, controls a single issue's state machine:

1. Validate repo/issue/approval, `gh` auth and `opencode` binary/agents/provider. Check clean worktrees and avoid reusing an active issue branch without explicit consent.
2. Dispatch a **new, isolated** development session through `opencode run --agent build` in the issue worktree. Use the working ChatGPT-connected model; select it explicitly with `--model` only after verifying its exact CLI ID. Do not assume an interactive TUI's model choice transfers to every subprocess.
3. Capture exit status and logs; verify a real PR and its linked issue, commit, changed files and concrete test evidence. Never interpret a convincing final paragraph as success without artifacts.
4. Create a **fresh read-only Reviewer** session using `opencode run --agent producer-reviewer` in a separate disposable checkout at the PR head, with effective permissions verified. Some tests create cache files: keep those confined to the disposable checkout. Do not reuse the Developer's conversation/session.
5. On confirmed review blockers, hand findings to a new/continued Developer session in the development worktree; then rerun validation and fresh review, with **one bounded correction cycle** initially. On ambiguity, failed tools, timeouts, or repeated defects, stop and escalate.
6. Return the PR URL, issue, head SHA, validation commands/results, review verdict, evidence and pending Creative Director acceptance. Do not merge, close issues manually, or delete worktrees automatically.

**Why first:** Native `opencode run` already supports one-shot prompts, `--agent`, `--model` and `--format json`; plain subprocess and `gh` operations are easier to inspect and debug than an event-driven service. Sequential execution avoids competing writer sessions and runaway token use. **This first version is implemented, with an authenticated live end-to-end pilot still pending.**

### B. OpenCode native subagents

Change suitable role profiles to `mode: subagent` or `mode: all` and let the Lead invoke them through OpenCode's native `subagent` tool, with explicit permission rules. Subagents have fresh child context and report to their parent. Good for research, architecture advice and **review**.

**Constraint:** The proven built-in **Build** agent is a **primary** agent; the standard native subagent tool is not an equivalent way to start a separate Build primary session. Replacing Build with a custom Developer subagent would be a separate capability experiment. Native subagents also need carefully verified permission and workspace separation. Therefore do **not** use this as the initial replacement for A.

### C. OpenCode server/API or SDK orchestrator

Use the local shared OpenCode server (or an explicitly started local server), session endpoints, and event/status APIs to create and observe **separate primary sessions**. This can support pause/resume, richer reporting, status visibility, and eventually parallel approved tasks. Keep the service local and authenticated; do not expose it to the internet.

**Tradeoff:** More moving parts (session tracking, permission events, crashes/reconnects, cancellation, idempotency) than a CLI runner. Consider only when the CLI pilot succeeds and additional control is justified.

### D. OpenCode built-in automations (version-dependent)

OpenCode **v2.4.0+** documents time/interval/cron and MCP-event automations; check `opencode --version` and `/automation` before relying on the feature. Useful later for reminding the Lead about a PR, a failed CI result, or a change in an issue. **Do not assume an automation can independently orchestrate all Build-primary/Reviewer permission and worktree boundaries**. The event-source/MCP integration would still need to be designed and authorized. Avoid unattended runs at first.

### E. GitHub Actions / webhook service

GitHub events can trigger CI and, eventually, an external coordinator. This is strongest for deterministic tests or a later always-on workflow. It is **not** the preferred initial AI worker: GitHub-hosted runners do not inherit the Creative Director's local ChatGPT sign-in; a hosted inference credential and potentially additional API spending would be required. Never copy local authentication credentials into CI.

## Recommended sequence

**Stage 0 — Verify locally (read-only).** From the repository root:

```sh
command -v opencode
opencode --version
opencode run --help
opencode debug agents
command -v gh
gh auth status
git status --short --branch
```

Do not paste any credentials. Confirm the exact connected model and that `producer-reviewer` is recognized with effective read-only tool restrictions. `opencode run --agent build "..." ` is a *documented syntax example*, not evidence that a background session has been successfully launched on this computer. Confirm the CLI supports the flags used before coding the runner.

**Stage 1 — One issue, supervised.** The standard-library CLI runner and unit tests are now committed. **Next:** perform a dry-run and one explicitly authorized live pilot on the Creative Director's machine. Validate the exact model/provider, permission handling, developer artifact, fresh Reviewer, PR gate and human acceptance. Do not advance to board automation until this succeeds.

**Stage 2 — After the pilot succeeds.** Make the Lead a consistent user-facing entry point that invokes the verified runner through a bounded interface. Introduce event-driven triggers or API orchestration only if continuous monitoring measurably reduces manual work. Do not run a fully autonomous backlog worker by default.

## Operational and safety contracts

- **Status and idempotency:** Record issue ID, authorized scope, branch/worktree, developer/reviewer session IDs (when available), PR, head SHA and phase. Do not open duplicate PRs or restart already-running work on repeated invocations.
- **Execution safeguards:** No `--auto` permission bypass by default; never silently use `git clean`, force-reset, overwrite existing work, push to `main`, or merge. Exact permissions must be tested; role text does not enforce filesystem or shell security. A Reviewer can run permitted tests in a disposable copy but must not mutate production or submit commits.
- **Failure detection:** Nonzero process exit, missing PR, missing main scene, failed tests, missing verification evidence, unsupported CLI flags, changed model/provider or repeated review defects are explicit blockers—not success.
- **Costs:** Use the existing ChatGPT subscription allowance; no API key fallbacks, paid credits, new subscriptions or unattended high-volume schedules without Creative Director approval. One issue at a time for the pilot.
- **PR handoff:** Include issue and parent references, exact tested commit, actual commands and outputs, screenshots or stated limits, independently grounded Reviewer verdict, and explicit pending Creative Director acceptance. No automatic merge/closure by the runner.
- **Scope:** This orchestration plan does not choose the production game engine. Issue #4 remains the architecture decision authority; Issue #14 is a comparison prototype, not permission to commit production rendering.

## Sources (check against installed version)

- OpenCode CLI: https://opencode.ai/docs/cli/commands/ (`run --agent`, `run --format json`, sessions)
- OpenCode agents and modes: https://opencode.ai/docs/agents/ (primary vs subagent, fresh contexts and permission rules)
- OpenCode service and API: https://opencode.ai/docs/api and https://opencode.ai/docs/cli/web
- OpenCode v2.4.0 automations: https://opencode.ai/changelog/v2.4.0
