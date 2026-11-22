# GitHub Issues and Project triage conventions

**Status:** Team conventions for The Producer. The GitHub Projects board and branch rules were configured manually by the Creative Director. This document defines the intended metadata and agent behavior; it does not assert that individual GitHub fields, issue types, or existing issue values were already migrated.

## Scope: different concepts

- **Issue Type** identifies the kind of work and its expected deliverable. Configure through GitHub Issue Types.
- **Issue fields** (Priority, Effort, Workstream, Human Approval Required) add issue metadata. **Pin to types** controls which types display a field by default; it does **not** assign a field value.
- **Project Status** records workflow progress on the GitHub Projects board. It is separate from Issue Type and Priority.
- **Dependencies** determine whether work is ready. High priority is not permission to bypass a blocked decision.

## Issue Types

| Type | When to use | Expected outcome |
|---|---|---|
| **Feature** | Implement approved player-facing or simulation behavior | Tested implementation meeting acceptance criteria |
| **Bug** | Correct behavior that demonstrably violates an approved requirement | Reproduction, targeted fix, regression test |
| **Task** | Concrete maintenance, infrastructure, tests, or bounded implementation preparation | Verified deliverable or completed procedure |
| **Spike** | Time/budget-bounded investigation, comparison or throwaway prototype | Evidence, options, tradeoffs, recommendation; not automatically production code |
| **Design Decision** | Resolve a creative or major architecture question that requires approval | Recorded decision/ADR and downstream changes, after human approval |

**Distinction:** A Spike supplies evidence; a Design Decision approves a direction. Neither silently authorizes implementing an unapproved feature.

### Proposed types for the initial backlog

| Issue | Type | Why |
|---|---|---|
| #1 Review game vision | Design Decision | Creative approval of the design baseline |
| #2 Validate Gemma/Qwen workflow | Task | Concrete infrastructure validation |
| #3 Propose contestant observation boundary | Spike | Compare architectures and test constraints |
| #4 Evaluate engine options | Spike | Experiment before choosing engine |
| #5 Build deterministic contestant prototype | Task | Bounded prototype after prerequisite decisions |
| #6 Supernatural autonomy and counterplay | Design Decision | Resolve proposed gameplay rules |
| #7 Season outcomes and contestant exits | Design Decision | Resolve consequential creative/narrative rules |

Existing GitHub issues may need their actual **Type** set manually; this table documents the intended classification, not a completed metadata migration.

## Issue-field pinning matrix

**✓ = pin the field to that Issue Type by default.** Blank = leave unpinned (it can still be filled when needed).

| Field | Feature | Bug | Task | Spike | Design Decision |
|---|:---:|:---:|:---:|:---:|:---:|
| **Priority** | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Effort** | ✓ | ✓ | ✓ | ✓ | — |
| **Workstream** | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Human Approval Required** | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Start Date** | — | — | — | — | — |
| **Target Date** | — | — | — | — | — |

Also pin **Priority** and **Workstream** to **Issues without a type**, if GitHub offers that choice, so ideas can be triaged before classification.

- **Priority** belongs on all types because design choices and research can block a milestone.
- **Effort** is useful for implementation, repairs and research; omit from Design Decisions by default since estimating a decision isn't especially informative.
- **Workstream** distinguishes domain (Design, Architecture, Infrastructure, Simulation, QA) from the kind of work. It applies to every type.
- **Human Approval Required** is visible everywhere because agents need to know whether they can proceed. **Visibility does not imply a default Yes or No**. Any creative/major architectural choice requires approval regardless of this field's current value.
- **Start Date** and **Target Date** remain unpinned until there is a real scheduling requirement. Do not invent dates merely to populate fields.

## Priority vocabulary: use readable names

Use **Urgent**, **High**, **Medium**, and **Low**. **Do not use P0/P1/P2** in new documentation, issue bodies or board guidance.

| Priority | Meaning |
|---|---|
| **Urgent** | A serious active blocker or risk needing immediate attention (rare) |
| **High** | Important to the current milestone or unlocks dependent work |
| **Medium** | Normal planned work |
| **Low** | Useful improvement that can safely wait |

Priority is **importance**, not severity, development effort or readiness. Do not automatically mark the next task Urgent. Prefer GitHub's existing Priority field where available rather than maintaining an inconsistent duplicate in the Project. When a field is project-scoped rather than issue-scoped in the active UI, establish a single authoritative location and document it.

## Project workflow

Keep the board's **Status** values:

`Backlog` → `Ready` → `In Progress` → `In Review` → `Done`

Use `Blocked` whenever an unresolved dependency prevents progress. A blocked High-priority issue stays blocked until its prerequisite is approved. The board should be grouped by Status.

Do not automatically move issues to Done when a PR opens. Done requires acceptance criteria, actual test evidence and independent review under `AGENTS.md`.

## Agent triage rules

1. Read the Type, Priority, Workstream, Status, approval field, issue body, dependencies and relevant decisions before planning.
2. Do not select issues that are Blocked or require an unapproved design decision, regardless of priority.
3. For a Spike, gather evidence; do not merge speculative production code as a side effect.
4. For a Design Decision, present alternatives and wait for Creative Director approval before implementation.
5. Do not fabricate field values, dates, approvals or estimates. If a crucial value is missing, make a recommendation and flag it.
6. Avoid duplicate issue fields and project fields that can drift apart.

## Practical repository notes

The GitHub integration used to establish the repository does not expose all Projects-v2 administrative actions. The Creative Director manages field configuration in GitHub's UI. This document describes the desired state but **does not** change those settings automatically.

This project originally used **P0/P1** in some initial issue descriptions. Those issue bodies and any real GitHub field values should be reconciled to **High/Medium/Low/Urgent** during issue triage; the present documentation change alone does not modify them.
