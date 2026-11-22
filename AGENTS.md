# Agent Operating Contract

## Authority and roles
- **Creative Director (human):** owns the game's identity, mechanics, narrative direction, scope, major technical choices, and final acceptance.
- **Lead/Producer agent:** decomposes approved goals, tracks dependencies, coordinates handoffs, and escalates decisions. Cannot approve new game mechanics.
- **Architect agent:** evaluates engines, interfaces, data models, risks, and ADRs; proposals require approval before major commitments.
- **Developer agent:** implements bounded approved issues and tests. Cannot silently simplify mechanics or expand scope.
- **Independent Reviewer/QA agent:** reviews changes against requirements, tests and privacy boundaries; does not approve its own implementation.
- **Design/Narrative specialist (optional):** proposes mechanics, scenarios, characters and dialogue; proposals remain unapproved.

## Local model selection and review independence
- Use `docs/agent-workflow.md` and ADR-0001 for the current preferred local model and role handoffs. Model assignment is provisional and **not** embedded in each agent's permissions.
- Developer and Reviewer may use the **same underlying model**, but must use separate, fresh sessions. The Reviewer inspects the actual code/diff and tests rather than inheriting the Developer's claims.
- A model's review is an independent **session-level** technical recommendation, not a separate GitHub account's required approval or evidence of independent model-family reasoning.
- Where warranted, obtain a cross-model second opinion, especially after unexplained failures or high-risk changes.
- If a tool operation repeatedly fails, stop and report the blocker rather than looping. Report only real test outputs and verified tool actions.

## Mandatory workflow
1. Read the assigned issue, `docs/vision.md`, relevant requirements, relevant system files and applicable ADRs.
2. Identify ambiguities and dependencies before editing. Escalate material design questions.
3. Produce a concise implementation plan and identify test evidence.
4. Work in an isolated branch/worktree; one active writer per worktree.
5. Add tests and run the relevant checks; report actual commands and outcomes. Never claim unexecuted tests passed.
6. Request independent review; resolve findings or document blockers.
7. Update documentation when an approved contract changes; create ADR for significant architecture decisions.
8. Submit a PR with issue reference, summary, evidence, limitations and risks. Do not merge without configured review gates.

## Issue classification and scheduling
- Follow `docs/project-board-setup.md` for Issue Types, field pinning, priorities and board statuses.
- Classify issues as **Feature**, **Bug**, **Task**, **Spike**, or **Design Decision**. Do not confuse Issue Type (kind of work) with Workstream (domain).
- Use readable priorities **Urgent**, **High**, **Medium**, **Low**; do not create P0/P1/P2 values. Priority does not override Blocked status, issue dependencies or human-approval requirements.
- Inspect Issue Type, Status, dependencies and approval evidence before beginning work. **Spikes** produce findings, not automatic feature implementation; **Design Decisions** require recorded human approval before changing game or architecture contracts.
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
Use bounded retries, timeouts and explicit approval for destructive commands, dependency additions, branch protection changes, release publication and data deletion. Keep model/API credentials out of the repository. Do not expose debug-only internal contestant state to player builds.

## Definition of done
Acceptance criteria met; relevant automated checks pass; independent review completed; no unresolved critical issues; documentation updated; reproducible build where applicable; no unrelated changes.