# Lead-agent orchestration: implementation options and pilot contract

**Status:** Option A implemented as a **supervised pilot** (`tools/orchestrate.py`); Python unit tests pass, but **no authenticated live OpenCode/GitHub run has been performed by this change**. Other options remain proposals. This does **not** authorize autonomous backlog execution, change permissions, or certify the entire workflow as production-ready.
**Environment:** The Creative Director uses **OpenCode CLI 2.4.1** on Bazzite Linux, with ChatGPT-connected cloud models. Build is the validated interactive implementation agent; the Python subprocess runner's live tool permissions, provider authentication, and model resolution have **not** yet been inspected on that machine.

## Objective and authority

The Creative Director should be able to ask: `Take approved Issue #N through development and independent review.` The Lead verifies prerequisites and coordinates a **separate Build developer**, a **fresh independent Reviewer**, and any bounded corrections. It hands off a verified PR and remaining acceptance questions to the Creative Director. It may prepare/reconcile existing issues and propose missing work, but **cannot self-approve game design, start unapproved work, change production architecture, merge PRs or introduce paid API charges**.

Authoritative issue body/parent fixtures, PR diffs, tests, screenshots, status comments and ADRs are the durable exchange format. A Developer's self-reported success is not the independent QA verdict. The reviewer must retrieve the issue and inspect the actual head commit/diff, and report `Approve`, `Request changes` or `Unable to verify` as a technical recommendation.

## Supervised runner: commands and guardrails

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

For a real run, the script (1) requires the explicit `--approve-issue` authorization, (2) creates its own branch and sibling worktree from freshly fetched `origin/main`, (3) runs `opencode run --standalone --agent build --model ...`, (4) requires an open non-draft PR on the expected branch with `Closes #N`, a nonempty diff and a section headed Evidence/Verification/Tests, (5) creates a **separate detached worktree at the exact PR SHA** and runs a fresh `producer-reviewer` primary agent, and (6) allows one corrective Build pass followed by fresh review. It validates the PR head hasn't changed during review and only returns "ready for acceptance" for a single explicit `REVIEW_VERDICT: APPROVE`. The Reviewer verdict remains a technical recommendation; the human still visually accepts and merges.

**Local state and cleanup:** State and text transcripts live under `../.The-Producer-agent-runs/issue-N/`, outside the Git checkout. Developer and Reviewer worktrees are sibling paths recorded in `state.json`. The first version intentionally **does not resume after interruption** or delete worktrees. If blocked, inspect `state.json`, the logs, `git worktree list`, the branch and any PR before deciding how to recover. Do not delete these records to force an unsafe duplicate run. After a successful human merge, clean up worktrees manually only after checking for uncommitted work.

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
