# AI-agent development workflow

**Status:** Cloud-first working baseline (provisional beyond the smoke test). **Decision:** [ADR-0003](decisions/ADR-0003-cloud-first-agent-development.md), which supersedes the local model choice in [ADR-0001](decisions/ADR-0001-local-agent-model-selection.md). This is a **development tooling** decision, not a production game-engine or in-game inference decision.

## Environment and default setup
- Bazzite Linux; OpenCode Desktop is installed as a Flatpak. The default **implementation agent is OpenCode's standard Build role using a cloud coding model connected through ChatGPT sign-in**. Verify the actual selected provider/model at each session start; model availability and plan limits may change.
- The existing project-local profiles under `.opencode/agents/` remain available for specialized duties, but they were tuned in part for local-model tool compatibility. **Do not assume `producer-developer` is equivalent to the verified Build configuration.** Do not modify these profiles just to make a particular task appear successful.
- Local LM Studio models are **not** routine development, lead, architect, or review defaults. They may be evaluated for optional bounded tasks, but local inference is no longer a dependency for project delivery.
- Keep credentials, ChatGPT session tokens, API keys, provider secrets, model weights, and machine-specific local paths out of Git.
- Cloud-based **development assistance** does not authorize cloud inference, cloud service dependencies, or paid API calls in the **shipped game**; game architecture decisions remain governed by their own requirements and approvals.

## Role assignments (provisional)
| Responsibility | Default | Evidence and limits |
|---|---|---|
| Implementation and self-debugging | OpenCode **Build**, ChatGPT-connected cloud coding model | Successfully completed an independently launched, visually correct minimal Godot project in a reported ~2 minutes; larger tasks remain unproven |
| Reviewer / QA | Fresh cloud-model session with **read-only** tools/permissions, separate from implementation | Review actual diff, exact issue and parent constraints; confirm errors independently where possible; no automatic approval |
| Lead / Producer | Cloud assistant; project-specific role instructions as appropriate | Prepare bounded tasks and trace requirements; may not approve scope |
| Architect | Cloud assistant; project-specific role instructions as appropriate | Evaluate tradeoffs and ADRs; cannot select production architecture without Creative Director approval |
| Automated verification | Local Godot CLI, tests and CI | No LLM required; cannot substitute headless checks for rendered visual acceptance |
| Creative Director | Human | Approves scope, accepts visual work, makes architecture decisions and merges PRs |

A reviewer can share the **same underlying model** as the developer if it uses a **fresh independent session**, has read-only access, and inspects source code and actual evidence instead of inheriting the developer's claims. Cross-model review is optional, not a prerequisite. Existing specialized agent profiles must be checked for effective permissions before use.

## Evidence and rationale
- Earlier local-model utility work showed some success, but the subsequent Issue #13 minimal Godot GUI assignment repeatedly failed despite direct tool access, execution errors and substantial human intervention. The reviewer also raised incorrect scope requirements and missed observable defects.
- On **2026-11-23**, a **ChatGPT-connected cloud coding model in OpenCode Build** reportedly completed a separate minimal Godot capability test in **about two minutes**, with a successful independent launch and visible markers, and no implementation debugging required from the Creative Director.
- **Both model and agent role changed**, and the tasks were not benchmark-controlled. The result establishes a practical working baseline, not proof that either component alone caused the improvement or that larger autonomous features will succeed.
- Preserve the historical experiments and their limitations in ADR-0001. Prefer observed task completion and human intervention per accepted deliverable over parameter-count comparisons or theoretical throughput.

## Cost and tool boundaries
- **Preferred initial funding:** existing ChatGPT subscription through supported OpenCode sign-in, subject to subscription and usage limits. Sign-in does not imply unlimited access or unrestricted API billing.
- **No paid API credits, automatic top-ups, new subscriptions, or paid provider fallback without explicit Creative Director approval.** Check the selected provider before running long tasks; report when plan limits or billing could force a change.
- Use the built-in **Build** agent for the known working implementation path; do not transfer experimental local-model `execute`/tool-routing restrictions into Build without evidence of need.
- At session start verify `git rev-parse --show-toplevel`, `git status --short --branch`, exact issue contents, and actual access to the intended Godot binary and required tools. Distinguish an OpenCode/Flatpak tool-access problem from a code defect.
- For visual work, demand executable project configuration, real GUI launch, and **observed** content. A scene node in source code is not evidence that its sprite/shape actually renders. Use screenshot inspection when tooling permits; otherwise mark visual behavior unverified and leave it for explicit human inspection.
- Limit repeated identical failures; after two unsuccessful attempts at the same underlying blocker, stop and report what failed and what is needed. Do not manufacture test results or repeatedly modify prompt templates to avoid a failed task.

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

Before starting an assignment, both the Developer and the Reviewer must independently establish:

1. **Exact issue:** authenticated `gh issue view ISSUE --repo williamwhorton/The-Producer` (or full user-provided issue text), with issue number, title, URL, expected deliverable and acceptance criteria. If neither source exists, stop; issue number alone is not enough without verified issue content.
2. **Actual workspace:** repository, current branch, working tree state and baseline/PR diff. The reviewer must not simply review whatever files are already open.
3. **Deliverable match:** a Godot prototype must contain relevant Godot project/scene/script files and Godot execution or manual inspection evidence; Python metadata tests only establish metadata functionality. Unrelated work cannot satisfy another issue, regardless of its passing tests.
4. **Explicit evidence map:** each criterion must be marked met with observed proof, not verified, or unmet. Missing the primary deliverable is a blocking defect; Reviewer returns **Request Changes**. Failure to retrieve the issue or inspect the diff is **Unable to verify — not approved**.
5. **Safe recovery:** when an agent starts on the wrong branch/issue, stop, report local changes and preserve them (no destructive reset/clean); start a fresh task-scoped context and dedicated branch before retrying.

This check is intentionally lightweight and procedural; it doesn't authorize the agents to approve creative decisions or bypass human merging.

## Development, verification and review cycle
1. Creative Director approves scope and acceptance criteria. Lead prepares a bounded assignment that includes the *actual* requirements from the assigned issue and all authoritative parent fixtures; don't invent or silently widen criteria.
2. Developer starts a **fresh Build session**, verifies its cloud model/provider and repository state, and uses a dedicated branch/worktree. Keep existing PRs and any uncommitted work intact.
3. Developer implements, **runs** the Godot project or relevant tests, inspects actual errors, and fixes them. Confirm the main scene is independently launchable; for visible features, run a GUI check where tools allow it. A successful headless import is necessary when relevant but not sufficient to claim visual success.
4. **Self-verification gate before review:** record the exact commands, actual results, files/commit, acceptance-criterion evidence map, GUI observations or explicitly unverified visuals, and outstanding blockers. If the primary deliverable cannot be demonstrated, **stop as blocked rather than requesting review**. Avoid more than two attempts at the same unresolved failure without escalation.
5. Reviewer starts a **different fresh session** using verified read-only permissions. Independently fetch the issue (including its authoritative parent constraints), inspect the real diff and artifacts, and run permitted checks. Do not take developer assertions as verified evidence.
6. Reviewer labels each finding **confirmed defect**, **plausible but unverified**, or **optional enhancement**, with file/line, reproducible impact and the requirement supporting a blocking claim. No invented requirements or changes beyond scope. Technical outcome: **Approve / Request changes / Unable to verify**.
7. Developer addresses substantiated findings and reruns checks; Creative Director independently inspects visual deliverables, accepts or rejects the result, and controls merging. Do not auto-merge while the workflow is being established.

**Review independence:** A fresh context is session-level independence, not model-family independence. A model acting through the repository owner's GitHub credentials does **not** count as approval by a separate GitHub user. PR-only changes, applicable CI, actual tests, and human acceptance remain the gates.

## Tool reliability and handoffs
- Use tools actually exposed in OpenCode; do not invent call syntax or tool identifiers.
- If a tool fails, inspect the result, correct the call, and stop/report the blocker after repeated identical failures. Do not enter a retry or self-talk loop.
- Keep durable context in docs, GitHub issues, ADRs, test evidence and PRs—not in indefinite conversations.
- Do not treat self-authored passing tests as the sole proof of correctness; avoid speculative fixes requested by a reviewer without a demonstrated need.
- Do not add unapproved dependencies, change major design decisions, publish releases, or incur additional paid API/service charges without Creative Director approval. Existing ChatGPT-connected development use is approved within the current subscription allowance.
