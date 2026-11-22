# Local AI-agent workflow

**Status:** Initial operating baseline; validated on a small utility task, not yet proven on game-system development. **Decision:** [ADR-0001](decisions/ADR-0001-local-agent-model-selection.md).

## Environment
- Bazzite Linux; LM Studio exposes locally downloaded models to OpenCode.
- OpenCode Desktop is installed as Flatpak. Project agent profiles live in `.opencode/agents/` and were confirmed visible in the Desktop selector.
- Do not commit credentials, local model weights, machine-specific provider identifiers, or model file paths.
- Agent **profile** and active **model** are separate selectors. The model is deliberately **not hard-coded** in profile frontmatter; verify it manually at the start of each session.
- Use one active local model workload at a time unless concurrency has been explicitly validated with the available GPU/RAM.

## Current model assignments (provisional)
| Role | Preferred model | Responsibilities |
|---|---|---|
| `producer-developer` | **gpt-oss-20b** | Implement approved issues, run tests, report real results |
| `producer-reviewer` | **gpt-oss-20b** | Fresh-session, read-only technical review and QA |
| `producer-architect` | **gpt-oss-20b** | Evaluate options, tradeoffs and ADRs; no implementation |
| `producer-lead` | **gpt-oss-20b** | Plan issues and dependencies, prepare self-contained handoffs |

**Optional second opinion:** Qwen3-Coder-30B-A3B-Instruct for complex or high-risk changes where a different model family adds value. Its initial review was very slow (~42 minutes on a small utility) and had speculative high-severity findings, so it is **not** the routine reviewer. The earlier Qwen3.5 9B reviewer and Gemma 4 12B QAT developer are **not** active default agents.

This assignment is based on limited practical evidence rather than a broad model benchmark. Revisit reviewer selection only if real review quality, shared blind spots, tool failures, or throughput create problems.

## Evidence from Issue #2 (reported in local sessions)
- **gpt-oss-20b development:** completed a Markdown link-checker exercise in approximately **12 minutes**, with no reported tool errors, loops, or human rescue; reported unit tests passing. **Seven tests** were later reported passing during review.
- **Qwen3-Coder review:** completed a review in approximately **42 minutes** and reported running seven passing tests; overall recommendation **Approve**. Some alleged high-priority risks lacked concrete failure cases and were assessed as low-value/speculative.
- **Gemma attempt:** repeated tool-call loops, tool-identifier errors and unsuccessful recovery; the earlier Markdown checker implementation also failed three of four tests in the initial run.
- **Qwen3.5 9B review:** identified one genuine fixture error but also proposed unnecessary fixes and missed known issues.
- These are **human-reported local results**, not independently reproduced by this document. Exact gpt-oss inference load parameters and total intervention counts were not recorded uniformly; do not invent them. This exercise validated a useful baseline, not a rigorous comparative benchmark.

## Issue intake and triage
Follow [GitHub issue types, fields and priority conventions](project-board-setup.md).

- **GitHub's native Issue Type**: **Feature**, **Bug**, **Task**, **Spike**, **Design Decision**; it is **not** a label, title prefix or Workstream. **Priority** and **Workstream** are existing issue custom fields and should be populated in the actual field UI/API, not represented only by issue-body prose.
- **Executable Spike rule:** an approved investigation can explicitly require disposable code, test harnesses, scenes or measurements. The Developer carries out those acceptance criteria even when Type=Spike; do not use the issue type to decline authorized prototype work. A prototype does not establish a production engine, mechanics or architecture without Creative Director approval. In #13–#15 the correct Type is **Task**, with #4 as the broader investigative Spike.
- On creating new issues, use the actual Issue Type/Priority/Workstream fields. When a connector cannot write them, supply `**Issue Type:** Task`, `**Priority:** High`, `**Workstream:** Architecture` (with appropriate values) as **temporary intake metadata** and verify GitHub Actions populates the fields. See [Issue metadata migration](issue-metadata-migration.md).
- Priority: **Urgent / High / Medium / Low**. A High-priority issue can still be Blocked.
- Before starting, check **Type**, **Status**, prerequisites, approval field, issue body and supporting ADR. A missing or inaccurate field cannot override human decision authority.
- Spikes gather evidence; Design Decisions require documented human approval before implementation.
- Do not invent dates, effort estimates, approvals or completed checks.

## GitHub Project status sync
The automation and one-time setup are documented in [Project Status automation](project-status-automation.md). The board's **Status** field is an operational signal and must be maintained at each handoff, not at the end of a week.

- New issues enter **Backlog** automatically. Lead marks approved/unblocked work **Ready** through an owner-authored issue comment containing only `/status Ready`.
- When an agent starts on an issue, it posts `/status In Progress`. If a prerequisite prevents progress, the agent posts `/status Blocked` and describes the blocker in a separate issue comment or handoff. Resume with `/status In Progress`.
- A non-draft PR with `Closes #N` in its body transitions the linked issue to **In Review**. The Reviewer may use `/status In Review` when no PR exists.
- After Creative Director acceptance and issue closure, GitHub Actions moves it to **Done**. Closing or reopening an issue is never a substitute for human approval.
- Posting `/status ...` requires an authenticated GitHub actor: only comments authored by the repository owner trigger updates. If tools cannot post, report the exact pending transition rather than silently assuming it occurred. The Creative Director should not need to watch the board.
- Run the manual reconciliation workflow if an event is missed. Existing active statuses are preserved. It needs the Project token and number configured before it can succeed.

## Issue-to-artifact verification gate

Before starting a local assignment, both the Developer and the Reviewer must independently establish:

1. **Exact issue:** authenticated `gh issue view ISSUE --repo williamwhorton/The-Producer` (or full user-provided issue text), with issue number, title, URL, expected deliverable and acceptance criteria. If neither source exists, stop; issue number alone is not enough for an offline agent.
2. **Actual workspace:** repository, current branch, working tree state and baseline/PR diff. The reviewer must not simply review whatever files are already open.
3. **Deliverable match:** a Godot prototype must contain relevant Godot project/scene/script files and Godot execution or manual inspection evidence; Python metadata tests only establish metadata functionality. Unrelated work cannot satisfy another issue, regardless of its passing tests.
4. **Explicit evidence map:** each criterion must be marked met with observed proof, not verified, or unmet. Missing the primary deliverable is a blocking defect; Reviewer returns **Request Changes**. Failure to retrieve the issue or inspect the diff is **Unable to verify — not approved**.
5. **Safe recovery:** when an agent starts on the wrong branch/issue, stop, report local changes and preserve them (no destructive reset/clean); start a fresh task-scoped context and dedicated branch before retrying.

This check is intentionally lightweight and procedural; it doesn't authorize the agents to approve creative decisions or bypass human merging.

## Manual development cycle
1. Creative Director approves the issue's scope, acceptance criteria and blocking decisions.
2. Developer starts a **fresh session**, confirms the chosen model, reads relevant docs, works on a separate branch/worktree, implements and tests.
3. Developer records commit/branch, actual test commands and results, failures, known limits and requested reviewer focus.
4. Reviewer uses a **different fresh session** with **no Developer conversation history** and read-only permissions. Examine the actual diff/code and issue requirements; where permitted, run tests and suggest independent edge cases.
5. Reviewer distinguishes **confirmed defects**, **unverified concerns**, and **optional enhancements**; cites exact file/line plus reproducible impact. Do not manufacture findings. Report **Approve / Request changes** as a **technical recommendation**.
6. Developer resolves substantiated findings or records exceptions, reruns tests, and updates the PR.
7. Creative Director reviews and merges the PR according to repository rules. No automatic merge while this workflow is being established.

**Independence limitation:** Developer and Reviewer share the same underlying model, so a fresh context is not model-family independence. Compensate with actual tests, requirement-based review, negative cases, and explicit human acceptance. A review by a model operating through the user's GitHub credentials **does not count as approval by another GitHub account**. Required GitHub reviewer approvals may be zero for this solo project; maintain PR-only changes and appropriate CI gates when available.

## Tool reliability and handoffs
- Use tools actually exposed in OpenCode; do not invent call syntax or tool identifiers.
- If a tool fails, inspect the result, correct the call, and stop/report the blocker after repeated identical failures. Do not enter a retry or self-talk loop.
- Keep durable context in docs, GitHub issues, ADRs, test evidence and PRs—not in indefinite conversations.
- Do not treat self-authored passing tests as the sole proof of correctness; avoid speculative fixes requested by a reviewer without a demonstrated need.
- Do not add unapproved dependencies, change major design decisions, publish releases, or use paid cloud services.
