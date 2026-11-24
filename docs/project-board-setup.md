# GitHub Issues and Project triage conventions

**Status:** Team conventions for The Producer. The GitHub Projects board and branch rules were configured manually by the Creative Director. This document defines the intended metadata and agent behavior; it does not assert that individual GitHub fields, issue types, or existing issue values were already migrated.

## Scope: different concepts

- **Issue Type** identifies the kind of work and its expected deliverable. Configure through GitHub Issue Types.
- **Issue fields** (Priority, Effort, Workstream, Human Approval Required) add issue metadata. **Pin to types** controls which types display a field by default; it does **not** assign a field value.
- **Project Status** records workflow progress on the GitHub Projects board. It is separate from Issue Type and Priority.
- **Dependencies** determine whether work is ready. High priority is not permission to bypass a blocked decision.

## Actual GitHub metadata fields — authoritative

**Use GitHub's native Issue Type** for the nature of work and existing **Priority** and **Workstream issue fields** for classification. These are **not** GitHub labels and must not be recreated as prefix labels, parallel Project fields or duplicated descriptions.

- **Type** determines whether an issue is a Feature, Bug, Task, Spike or Design Decision. It never, by itself, prohibits executable evidence: **Spikes may require intentionally throwaway code**; read the approved issue deliverable and acceptance criteria first.
- **Priority** indicates importance: Urgent / High / Medium / Low.
- **Workstream** identifies the product/engineering domain, not the issue type. Use an existing option; if no suitable option exists, request an option change rather than silently inventing one.
- **Status** is the GitHub Project workflow stage and remains separately synchronized by `project-status-sync.yml`.
- The old `[Spike]`, `[Task]`, `[Feature]` prefixes and free-form `**Priority:**`/`**Workstream:**` lines in older issue descriptions are **migration hints only**, not authoritative metadata.
- For **new** issues created by a connector that cannot set fields, put a small `**Issue Type:** Task` / `**Priority:** High` / `**Workstream:** Architecture` block in the issue body. The secure [metadata workflow](issue-metadata-migration.md) imports it into the native fields. Confirm that the actual fields changed; do not assume because the text exists.
- Only the Type, Priority and Workstream **field values** should be used for scheduling and reporting once migrated. A Developer must not skip implementation just because a Type is Spike when executable prototype code is specifically approved.

**The approved runnable proofs #13, #14 and #15 are Tasks.** Their parent engine-comparison investigation #4 is a Spike. A general future Spike can still ask a Developer to write disposable experiment code.

## Issue Types

| Type | When to use | Expected outcome |
|---|---|---|
| **Feature** | Implement approved player-facing or simulation behavior | Tested implementation meeting acceptance criteria |
| **Bug** | Correct behavior that demonstrably violates an approved requirement | Reproduction, targeted fix, regression test |
| **Task** | Concrete maintenance, infrastructure, tests, implementation preparation or **approved executable proof** | Verified deliverable, runnable prototype where specified, or completed procedure |
| **Spike** | Bounded investigation, comparison or experiment **that may require executable prototype code** | Measured evidence, reproductions/throwaway code if approved, options, tradeoffs and recommendation; no automatic production commitment |
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

Existing GitHub issues have **native Type fields**; use the safe [metadata import](issue-metadata-migration.md) to fill or correct them. #13–#15 are explicit Task corrections, even if a previously entered Spike field still appears pending import.

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

## Automated status updates
See [GitHub Project Status automation](project-status-automation.md) for the repository workflow, owner-only `/status ...` commands, first-run bootstrap and required GitHub Actions secret/variable.

The board is **not** expected to be maintained by the Creative Director manually. The Lead and working agents must publish verified status transitions at handoffs. Issue/PR lifecycle events drive Backlog, In Review, and Done when the automation is configured. The GitHub integration does not directly edit Projects-v2 fields; Actions performs those updates with an explicit Project-scoped secret.

## Ready versus Backlog — including Creative Director decisions

**Ready** is a rolling two-day planning queue, not an assertion that every card can start now. An approved prerequisite and its dependent may both be queued; the dependent stays Ready until the prerequisite is accepted. The two-day horizon is a triage convention, not an automated expiry. The Creative Director may work Ready decision stories concurrently with implementation; assign them to `williamwhorton`.

- **Readiness is not creative approval.** An unblocked Design Decision can be Ready for research/decision while every implementation story that depends on its result remains in Backlog or Blocked.
- **Backlog** contains concrete, traceable *future* MVP work across every function from design through release, including stories that are not yet Ready due to dependencies, sequencing or current priorities.
- **Blocked** records an actual, specific impediment to work underway or selected for execution. An unscheduled future issue with dependencies can remain Backlog rather than cluttering Blocked.
- **In Progress** begins only when work actually starts; **In Review** means review/approval awaits; **Done** needs acceptance.
- Keep a **complete release path**, not merely a near-term sprint queue. The Lead maintains [MVP-to-release delivery plan](mvp-delivery-plan.md), reviews requirement coverage regularly, avoids duplicate issues, and adds bounded work/spikes when a real gap arises.
- Queue dispatch requires the actual `agent:developer` repository label **and no GitHub assignee**. An assignee overrides the label; Design Decisions are never dispatched. Set native Type, Priority and Workstream (use the [existing backfill](issue-metadata-migration.md) for missing values), then post a fresh standalone `/status Ready` as `williamwhorton` after any relevant issue edit or reopening. The actual card must also be Ready. This authorizes the bounded issue, not unapproved design.
- Prefer native **Blocked by** issue links. If all prerequisites are already in native links and no legacy declaration needs reconciliation, no extra line is needed. Otherwise replace legacy prose with exactly one standalone issue-body line, `Queue prerequisites: #27, #29` (same-repository issues), or `Queue prerequisites: none` after verifying the issue has no prerequisites. The explicit list must include every native blocker. Turn unresolved artifact or approval requirements into tracked prerequisites before authorizing the issue; do not write `none` to bypass them.
- Use an owner-merged closing PR to `main` or an owner **Completed** closure for an accepted non-PR deliverable/decision. Record the actual decision or acceptance in the issue or its PR. `Done`, a technically approved open PR, and `not planned` are not approval. To supersede a prerequisite, the owner records why, replaces it in both native links and the declaration (if used), and reauthorizes with `/status Ready`; the replacement must pass the same acceptance gate.
- New work from design changes, prototype evidence, playtests and release review is added through normal issue triage; don't invent approvals, exact content counts, estimates or deadlines.


Keep the board's **Status** values:

`Backlog` → `Ready` → `In Progress` → `In Review` → `Done`

Use `Blocked` for a concrete blocker on work that has started or needs intervention. A queued successor simply waits in Ready and is not eligible until its prerequisites are accepted. The board should be grouped by Status.

Do not automatically move issues to Done when a PR opens. Done requires acceptance criteria, actual test evidence and independent review under `AGENTS.md`.

## Agent triage rules

1. Read the Type, Priority, Workstream, Status, approval field, issue body, dependencies and relevant decisions before planning.
2. Do not select issues that are Blocked or require an unapproved design decision, regardless of priority.
3. For a Spike, gather evidence and **implement disposable experimental code when required by the approved issue**. Do not merge unapproved *production* code or canonize architecture as a side effect.
4. For a Design Decision, present alternatives and wait for Creative Director approval before implementation.
5. Do not fabricate field values, dates, approvals or estimates. If a crucial value is missing, make a recommendation and flag it.
6. Avoid duplicate issue fields and project fields that can drift apart.

## Practical repository notes

The GitHub integration used to establish the repository does not expose all Projects-v2 administrative actions. The Creative Director manages field configuration in GitHub's UI. This document describes the desired state but **does not** change those settings automatically.

This project originally used **P0/P1** in some initial issue descriptions. Those issue bodies and any real GitHub field values should be reconciled to **High/Medium/Low/Urgent** during issue triage; the present documentation change alone does not modify them.
