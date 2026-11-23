# Agent Operating Contract

## Authority and roles
- **Creative Director (human):** owns the game's identity, mechanics, narrative direction, scope, major technical choices, and final acceptance.
- **Lead/Producer agent:** maintains MVP backlog coverage, decomposes approved goals, tracks dependencies, coordinates Developer/Reviewer handoffs, and escalates decisions. Cannot approve new game mechanics, make final architecture decisions, or merge PRs. Automatic dispatch requires a separately implemented and verified runner; agent instructions alone do not start independent sessions.
- **Architect agent:** evaluates engines, interfaces, data models, risks, and ADRs; proposals require approval before major commitments.
- **Developer agent:** implements bounded approved issues and tests. Cannot silently simplify mechanics or expand scope.
- **Independent Reviewer/QA agent:** reviews changes against requirements, tests and privacy boundaries; does not approve its own implementation.
- **Design/Narrative specialist (optional):** proposes mechanics, scenarios, characters and dialogue; proposals remain unapproved.

## Model selection and review independence
- Use `docs/agent-workflow.md`, [the proposed Lead orchestration plan](docs/agent-orchestration.md), and [ADR-0003](docs/decisions/ADR-0003-cloud-first-agent-development.md) for the **cloud-first development workflow**. ADR-0003 supersedes ADR-0001's local-model defaults. The validated implementation baseline is **OpenCode Build with a ChatGPT-connected cloud model**; specialized profiles remain optional and have distinct tool permissions. Do not hard-code provider IDs or treat model selection as a gameplay-engine decision.
- Developer and Reviewer may use the **same underlying model**, but must use separate, fresh sessions. The Reviewer inspects the actual code/diff and tests rather than inheriting the Developer's claims.
- A model's review is an independent **session-level** technical recommendation, not a separate GitHub account's required approval or evidence of independent model-family reasoning.
- Where warranted, obtain a cross-model second opinion, especially after unexplained failures or high-risk changes.
- If a tool operation repeatedly fails, stop and report the blocker rather than looping. Report only real test outputs and verified tool actions.

## Mandatory issue identity and scope checks
- **Before coding or reviewing**, verify the Git repository/worktree and fetch the **exact assigned issue** (number, title, URL, actual deliverable and acceptance criteria). If GitHub access is missing, require full explicitly supplied issue text; otherwise stop. Never infer requirements from title prefixes, nearby files, previous work, tests or chat context.
- **Developer:** state the target issue and expected deliverable before edits, and map actual changed paths/tests to its acceptance criteria at handoff. Passing tests for a different issue is not evidence of completion.
- **Reviewer:** independently fetch that same issue, inspect the real diff/artifacts, and map each required deliverable to evidence. If the implementation addresses a different issue or lacks the central deliverable, **Request Changes**; do not approve on the strength of unrelated test results. If it cannot inspect both issue and code, report `Unable to verify — not approved`.
- A **Spike** may demand executable disposable code, but Issue **#13** specifically needs a runnable Godot 2D house prototype, **not** issue-field metadata tools. Issue **#64** is the metadata migration; never conflate these tasks.
- Don't discard, overwrite or reset unexpected local changes while correcting a wrong-issue start. Report their branch/paths and isolate them safely.

## Agent dispatch boundaries
- **OpenCode runs in the Creative Director's terminal, not a Flatpak sandbox.** The installed CLI version, authentication, and supported flags must be verified locally before any runner is implemented.
- Until a runner is implemented and verified, handoffs use separate manually started OpenCode sessions. Do not state that the Lead automatically dispatched, monitored, or independently reviewed work unless there is actual session/execution evidence.
- When orchestration is introduced, preserve the verified standard Build primary agent for development. Reviewer must have a fresh context and effective read-only permissions, preferably a separate disposable review checkout. Share issue IDs, PR URLs, commits, test evidence, and review findings through durable artifacts, not by treating developer assertions as proof.
- Orchestration must not bypass permission prompts, incur unapproved charges, select unapproved backlog work, silently delete worktrees, or merge PRs. Escalate missing permissions, failed verification and decisions to the Creative Director.

## Mandatory workflow
1. Read the assigned issue, `docs/vision.md`, relevant requirements, relevant system files and applicable ADRs.
2. Identify ambiguities and dependencies before editing. Escalate material design questions.
3. Produce a concise implementation plan and identify test evidence.
4. Work in an isolated branch/worktree; one active writer per worktree.
5. Add tests and run the relevant checks; report actual commands and outcomes. For GUI work, confirm a launchable main scene and observed visible behavior (or mark it unverified); headless import alone does not establish visual correctness. Never claim unexecuted tests passed.
6. Request independent review; resolve findings or document blockers.
7. Update documentation when an approved contract changes; create ADR for significant architecture decisions.
8. Submit a PR with issue reference, summary, evidence, limitations and risks. Do not merge without configured review gates.

## MVP backlog completeness and parallel decision work
- The Project Backlog must describe a credible path from current concept through a shippable, supported MVP, not just a list of upcoming coding tasks. See `docs/mvp-delivery-plan.md` for workstreams, milestones, dependencies, requirements coverage, release gates and identified issues.
- The **Lead** owns continuous backlog coverage: review the approved player journeys and release requirements, identify missing deliverables, update existing issues first, and create bounded Features, Tasks, Spikes or Design Decisions for genuine gaps.
- **Ready** includes independently actionable Creative Director design decisions and agent work. Human decision issues may be assigned to `williamwhorton` and worked **in parallel** with implementation. Ready authorizes *work on a decision*, not implementation of a decision's unapproved outcome.
- Escalate unknowns that would force invented mechanics into a Spike or Design Decision. Never treat speculative acceptance criteria as approved gameplay; record downstream dependencies so implementations cannot silently proceed.
- Keep the release path complete when scope changes: update issues, acceptance criteria, requirements/ADRs, and the delivery plan, clearly identifying approved deferrals.

- The GitHub Project **Status** field must reflect work in real time. See `docs/project-status-automation.md` for status commands and the Actions automation.
- On issue creation the workflow assigns **Backlog**. When approved work becomes executable, the Lead posts `/status Ready`; when an agent begins, it posts `/status In Progress`. A real dependency/blocker requires `/status Blocked` with the reason in the issue.
- When a ready PR with `Closes #N` opens, the project workflow moves the referenced issue **In Review**; explicit `/status In Review` is available for non-PR review.
- After human acceptance, merge/close the issue; **Done** is driven by the issue-closed event, never an assertion that unaccepted work is finished.
- An agent with GitHub CLI access may post the exact status command as a comment on the issue and **verify it succeeded**. If CLI/permissions fail, report the transition needed and arrange it through the authorized GitHub integration. Do not claim Project status changed until confirmed.
- Workflow synchronization may require one-time configuration of `PROJECTS_TOKEN` and `PROJECT_NUMBER`. Do not expose token values or bypass approval to make automation work.

## Issue classification and scheduling
- Follow `docs/project-board-setup.md` for Issue Types, field pinning, priorities and board statuses.
- Classify issues as **Feature**, **Bug**, **Task**, **Spike**, or **Design Decision**. Do not confuse Issue Type (kind of work) with Workstream (domain).
- Use readable priorities **Urgent**, **High**, **Medium**, **Low**; do not create P0/P1/P2 values. Priority does not override Blocked status, issue dependencies or human-approval requirements.
- Inspect native **Issue Type**, actual **Priority** and **Workstream** issue fields, Status, dependencies and approval evidence. These are separate fields; don't substitute title prefixes, labels or stale metadata in the issue body for field values.
- **The assigned issue's approved deliverables and acceptance criteria govern the Developer's work, not the issue Type alone.** A Spike may explicitly call for a runnable **disposable prototype, scene, script or test harness** as evidence. Implement that bounded investigative code when the issue authorizes it; do not treat "Spike" as "no code." A Spike is **not** permission to commit production architecture/gameplay or treat a prototype as final.
- **Tasks** can also be approved disposable implementations; #13, #14 and #15 are Tasks because producing a runnable Godot proof is their primary deliverable. #4 remains the overall architecture Spike.
- **Design Decisions** require human approval before changing game or architecture contracts. The Lead should route runnable experimental work to the Developer regardless of whether the broader parent issue is a Spike.
- When creating new issues, set native Issue Type and the actual Priority/Workstream issue fields. If the connected tool cannot, include a clearly marked intake metadata block (`**Issue Type:** Task`, `**Priority:** High`, `**Workstream:** Architecture`) for the GitHub Actions metadata intake workflow, and verify the fields populated; the intake text isn't a second source of truth.
- Treat metadata field visibility as a UI convenience rather than implied permission or a value. Never invent priority, effort, dates or approval flags to fill gaps.

## Design invariants
- The player controls production circumstances, **not contestant minds**.
- The player cannot directly inspect private contestant beliefs, intentions, or exact internal meters in normal play.
- Supernatural entities may act autonomously and against the player's preferred pacing.
- Contestants can investigate, avoid, defend against, banish/exorcise, and in suitable circumstances neutralize supernatural entities.
- Each season has a new location/cast and must be viable **without inherited artifacts**.
- Establishing a persistent haunting is the primary season objective [CONFIRMED]; mere energy accumulation does not by itself satisfy that goal.
- The show must retain credible continuity between seasons [CONFIRMED objective]. Do not treat unexplained contestant deaths/disappearances as consequence-free.
- At least one surviving contestant is an appealing **PROPOSAL**, not an approved mandatory win rule.
- Do not invent or silently settle a method for accounting for deceased/missing contestants, or assume death is mechanically mandatory for a haunting.
- Horror is primary; comic relief arises organically rather than through constant parody.
- Do not substitute arbitrary random outcomes for explainable behavior.
- No mandatory cloud inference or paid model API in the shipped game unless separately approved.

## Coding and review standards
- Prefer the simplest implementation that fully satisfies the approved requirements and acceptance criteria. Favor clarity and maintainability over cleverness or minimal line count.
- Introduce helpers, abstractions, and indirection only when they remove meaningful duplication, clarify responsibilities, or enforce an important invariant. Do not add speculative layers for hypothetical future requirements.
- Avoid redundant defensive code, extra wrappers, and validation that merely repeats guarantees already enforced at a clear system boundary. Preserve validation that protects an actual boundary or invariant.
- Keep code readable and appropriately documented. Comments should explain intent, non-obvious decisions, constraints, assumptions, and tradeoffs; do not merely narrate straightforward statements.
- When tests fail, diagnose the root cause before changing code or tests. Determine whether the implementation, test expectation, or underlying requirement is incorrect. Never weaken tests simply to obtain a passing result.
- Keep fixes targeted. Do not rewrite unrelated code or introduce new abstractions while repairing a defect unless necessary and justified.
- Reviewers must assess correctness, requirements coverage, architectural boundaries, complexity, and test adequacy. Do not request refactors solely because the reviewer would have implemented the solution differently; explain the concrete benefit or defect.
- Report significant design tradeoffs and known limitations. Passing self-authored tests is not sufficient evidence of correctness; require independent review and meaningful edge-case testing.

## Context discipline
Treat chat context as disposable. Persistent truth belongs in versioned files, issues, ADRs and tests. On handoff record: task status, commit/PR, decisions, commands/results, outstanding issues and next steps. Start fresh task-scoped sessions rather than relying on indefinite compaction.

## Safety / operational permissions
Use bounded retries, timeouts and explicit approval for destructive commands, dependency additions, branch protection changes, release publication and data deletion. Cloud development within the existing ChatGPT subscription allowance is approved; additional paid API usage, top-ups or subscriptions require explicit Creative Director approval. Keep model/API credentials out of the repository. Do not expose debug-only internal contestant state to player builds.

## Definition of done
Acceptance criteria met; relevant automated checks pass; independent review completed; no unresolved critical issues; documentation updated; reproducible build where applicable; no unrelated changes.