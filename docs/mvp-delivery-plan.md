# MVP-to-release delivery plan

**Status:** Living planning baseline — created 2026-11-22; **not** approval of undecided game rules, implementation details, exact MVP content count or platform targets.  
**Owner:** Lead Technical Producer maintains the issue map; **Creative Director** owns game/product decisions and acceptance.  
**Related:** [#62 — MVP backlog maintenance](https://github.com/williamwhorton/The-Producer/issues/62), [requirements](requirements.md), [vision](vision.md), [open questions](open-questions.md), [project board conventions](project-board-setup.md), [status automation](project-status-automation.md).

## Why this exists

The **GitHub Project** is meant to show a credible route from the current design to a **releasable minimum viable product**, not just the next few coding tasks. Every necessary category of work must have a backlog issue or a documented dependency that will produce one. Existing issues should be extended rather than duplicated. New issues arise when genuine new work, defects, approved feature changes, prototype findings or release constraints justify them.

**Do not confuse:**
- **Engine evaluation Spike** (#4), supported by three explicitly approved **executable Tasks** (#13–#15): disposable code and evidence, not a chosen production architecture. A Spike may also include runnable experimental code when its acceptance criteria require it.
- **Vertical slice**: one playable representative sample used to prove the core loop.
- **MVP** (#20): a small but coherent, distributable game with enough content, usability, persistence and quality for actual players. Exact release scope remains a **Creative Director decision**.

The plan is **comprehensive by workstream**, not a promise that every candidate mechanic or every listed content item must ship. #20 and related decisions will define the approved MVP baseline; if a story is deferred, document the reason, replacement coverage and updated acceptance criteria. Keep the route to an actual release complete.

## Workflow interpretation and role ownership

| Project Status | Interpretation |
|---|---|
| **Backlog** | Known future work, including scoped implementation stories awaiting decisions, sequencing or selection |
| **Ready** | A bounded **task or decision can begin now**, independently of other unfinished deliverables. Ready does **not** approve its proposed output or authorize game mechanics |
| **In Progress** | Owner/agent actually started and is producing work |
| **In Review** | Implementation PR or design proposal awaiting independent/human evaluation |
| **Blocked** | A specific unresolved dependency is actively preventing previously queued/attempted work; record the actual reason |
| **Done** | Acceptance and human merge/closure completed, with required evidence |

**Creative Director stories in Ready:** these are decisions the human may work on **in parallel** with agents. Assign them to `williamwhorton` in GitHub; Lead/Architect can supply options or research, but neither decides unapproved mechanics. An agent-owned investigation can be Ready at the same time. Do not mark an item Blocked merely because the Creative Director has not yet chosen to work on it; likewise do not promote dependent implementation to Ready before required approvals.

**Status maintenance:** use the owner-authored standalone `/status Ready`, `/status In Progress`, etc. issue comments or automatic PR/issue events as described in [project-status-automation.md](project-status-automation.md). Confirm successful posting and review Actions when synchronization is in doubt. New issues should enter Backlog automatically.

## Milestone 1 — Establish creative and technical decisions

The following issues may be worked in parallel from current documents; they do **not** require the finished engine decision:

| Issue(s) | Deliverable | Initial accountable role |
|---|---|---|
| [#1](https://github.com/williamwhorton/The-Producer/issues/1) | Confirm/correct baseline vision, requirements and open claims | Creative Director — Ready |
| [#20](https://github.com/williamwhorton/The-Producer/issues/20) | Approve MVP scope, supported user journeys and release gates | Creative Director — Ready |
| [#3](https://github.com/williamwhorton/The-Producer/issues/3) | Propose observation/private-state contract for human approval | Architect — Ready |
| [#6](https://github.com/williamwhorton/The-Producer/issues/6) | Decide supernatural agency and contestant counterplay limits | Creative Director — Ready |
| [#7](https://github.com/williamwhorton/The-Producer/issues/7) | Decide haunting outcomes, franchise continuity and credible exits | Creative Director — Ready |
| [#16](https://github.com/williamwhorton/The-Producer/issues/16) | Decide producer powers and surveillance channels | Creative Director — Ready |
| [#17](https://github.com/williamwhorton/The-Producer/issues/17) | Decide time controls and season pacing | Creative Director — Ready |
| [#4](https://github.com/williamwhorton/The-Producer/issues/4), [#13](https://github.com/williamwhorton/The-Producer/issues/13), [#14](https://github.com/williamwhorton/The-Producer/issues/14), [#15](https://github.com/williamwhorton/The-Producer/issues/15) | Compare visual renderers, test headless simulation and prepare **ADR-0002** | Architect/Developer — #4 In Progress; spikes Ready |

**Further decisions, staged in Backlog pending input:** [#21](https://github.com/williamwhorton/The-Producer/issues/21) initial platforms, controls/accessibility and performance budget; [#22](https://github.com/williamwhorton/The-Producer/issues/22) art/audio/content style; [#23](https://github.com/williamwhorton/The-Producer/issues/23) escalation-model spike (follows #6); [#24](https://github.com/williamwhorton/The-Producer/issues/24) season/cast content strategy; [#25](https://github.com/williamwhorton/The-Producer/issues/25) optional artifacts/carryover; [#26](https://github.com/williamwhorton/The-Producer/issues/26) producer workflow and information UX spike. Move these to Ready when they genuinely no longer depend on unfinished inputs, not merely because they are important.

**Decision gate:** No production implementation that depends on unapproved engine, pacing, player-action, escalation, fate or observation rules. Preserve **G-13** survivor requirement and exact death-to-haunting relationship as *proposals*, not mandatory victory rules.

## Milestone 2 — Production runtime, simulation and testable world

| Issue(s) | Required capability / primary dependency |
|---|---|
| [#27](https://github.com/williamwhorton/The-Producer/issues/27) | Production engine skeleton after #4/ADR-0002 |
| [#28](https://github.com/williamwhorton/The-Producer/issues/28) | Reproducible event scheduler after #17 and #15 |
| [#29](https://github.com/williamwhorton/The-Producer/issues/29) | Rooms, exits, routes, doors and navigation |
| [#30](https://github.com/williamwhorton/The-Producer/issues/30) | Data-driven season/house/cast scenarios after #24 |
| [#5](https://github.com/williamwhorton/The-Producer/issues/5) | Seeded contestant-decision prototype, presently Blocked on engine and observation approval |
| [#31](https://github.com/williamwhorton/The-Producer/issues/31) | Autonomous contestant actions and goals |
| [#32](https://github.com/williamwhorton/The-Producer/issues/32) | Private memories/beliefs, fear and suspicion without omniscient UI |
| [#33](https://github.com/williamwhorton/The-Producer/issues/33) | Social contact and selective evidence sharing |
| [#34](https://github.com/williamwhorton/The-Producer/issues/34) | Voluntary quitting and credible show exits after #7 |
| [#35](https://github.com/williamwhorton/The-Producer/issues/35) | Approved producer interventions and staged scares |
| [#36](https://github.com/williamwhorton/The-Producer/issues/36) | Genuine supernatural buildup using approved #23 candidate |
| [#37](https://github.com/williamwhorton/The-Producer/issues/37) | Autonomous entity that can complicate producer goals |
| [#38](https://github.com/williamwhorton/The-Producer/issues/38) | Contestant avoidance, investigation and effective counterplay |
| [#18](https://github.com/williamwhorton/The-Producer/issues/18) | Persistence proof/format decision; engine and observation contract prerequisite |
| [#19](https://github.com/williamwhorton/The-Producer/issues/19) | Headless CI running real tests on selected runtime |

Prefer small, seeded and explainable simulations. Game logic must not depend on rendering, and developer inspection must not silently expose private state in shipped gameplay.

## Milestone 3 — Playable producer loop and observational interface

| Issue(s) | Required capability |
|---|---|
| [#39](https://github.com/williamwhorton/The-Producer/issues/39) | Observations derived from defensible source/time/coverage rules |
| [#40](https://github.com/williamwhorton/The-Producer/issues/40) | Player-facing dollhouse rendering with room/floor navigation |
| [#41](https://github.com/williamwhorton/The-Producer/issues/41) | Surveillance reports, uncertainty and history |
| [#42](https://github.com/williamwhorton/The-Producer/issues/42) | Producer action scheduling and time controls |
| [#43](https://github.com/williamwhorton/The-Producer/issues/43) | Development-only causal trace and private-state inspector |
| [#44](https://github.com/williamwhorton/The-Producer/issues/44) | Coherent feedback distinguishing staged and genuine horror |

**Vertical-slice gate:** A player can observe imperfect evidence, intervene through production tools, experience autonomous contestant/entity reactions, and understand outcomes in a limited playable scenario. Passing this gate **is not** MVP release readiness.

## Milestone 4 — Complete seasons, consequences and replayability

| Issue(s) | Required capability |
|---|---|
| [#45](https://github.com/williamwhorton/The-Producer/issues/45) | Post-production haunting persistence, separate from mere activity |
| [#46](https://github.com/williamwhorton/The-Producer/issues/46) | Franchise continuity, credible consequences and contestant dispositions |
| [#47](https://github.com/williamwhorton/The-Producer/issues/47) | Start/end/transition seasons using distinct scenario data |
| [#48](https://github.com/williamwhorton/The-Producer/issues/48) | **Conditional** optional carryover artifact/knowledge implementation if approved by #20/#25 |
| [#49](https://github.com/williamwhorton/The-Producer/issues/49) | Coherent first playable season with ordinary downtime and horror development |
| [#50](https://github.com/williamwhorton/The-Producer/issues/50) | Distinct second location/cast and repeatability, or approved smaller variation if #20 narrows scope |
| [#51](https://github.com/williamwhorton/The-Producer/issues/51) | Player-facing separate haunting and franchise outcome reports |
| [#52](https://github.com/williamwhorton/The-Producer/issues/52) | Onboarding, discoverability and first-session guidance |
| [#53](https://github.com/williamwhorton/The-Producer/issues/53) | Save/reload season and campaign with failure recovery |

The MVP must preserve the ability to play an **artifact-free season** and the confirmed goal of a franchise that can plausibly continue. The exact content count and artifact implementation are conditional until the Creative Director decides them.

## Milestone 5 — Release-quality game and distribution

| Issue(s) | Required capability |
|---|---|
| [#54](https://github.com/williamwhorton/The-Producer/issues/54) | Controls, readable UI, audio settings and MVP accessibility |
| [#55](https://github.com/williamwhorton/The-Producer/issues/55) | Legally distributable art/audio/credits; coherent style |
| [#56](https://github.com/williamwhorton/The-Producer/issues/56) | Seeded end-to-end regression and private-state leak tests |
| [#57](https://github.com/williamwhorton/The-Producer/issues/57) | Balance, pacing and gameplay tuning based on evidence |
| [#58](https://github.com/williamwhorton/The-Producer/issues/58) | Stability, memory, save reliability and performance profiling |
| [#59](https://github.com/williamwhorton/The-Producer/issues/59) | Offline distributable build and clean-install smoke test |
| [#60](https://github.com/williamwhorton/The-Producer/issues/60) | External usability playtesting and fixes for release blockers |
| [#61](https://github.com/williamwhorton/The-Producer/issues/61) | Release readiness, license/credit audit and human go/no-go |

**Public MVP release gate:** All required MVP journeys, supported build targets, critical bug fixes, offline operation, essential accessibility, save/recovery, legal asset rights, basic onboarding and reproducible test evidence are satisfied and approved. Publish and smoke-test the downloadable release. Do not label the technical prototype or a one-house sketch as a finished MVP.

## Requirement coverage check

| Confirmed direction | Main backlog coverage |
|---|---|
| G-01 Producer's concealed role and interventions | #16, #35, #42, #49 |
| G-02 Autonomy and quitting | #5, #28, #31, #34 |
| G-03 Dollhouse view | #4, #13, #14, #40, #55 |
| G-04 Primary horror with organic relief | #22, #44, #49, #55, #57 |
| G-05 Independent supernatural agents | #6, #23, #36, #37 |
| G-06 Imperfect observation | #3, #15, #32, #39, #41, #43, #56 |
| G-07 Contestant counterplay | #6, #33, #38 |
| G-08 Distinct seasons/locations/casts | #24, #30, #47, #49, #50 |
| G-09 Artifacts non-mandatory | #25, #47, #48, #56 |
| G-10 Optional inherited progression | #25, #47, #48, #53 |
| G-11 Persistent haunting after filming | #7, #23, #45, #51 |
| G-12 Show-continuity objective | #7, #46, #47, #51 |
| G-14 Credible consequences of deaths/absences | #7, #34, #46, #51 |
| G-13 Survivor mandate | **Proposed only** — investigate with #7/#20, do not impose |

## Backlog completeness and refinement protocol

At every design approval, engine prototype, gameplay PR, playtest, release review or substantial new discovery, the **Lead** must:

1. **Review requirement coverage and player journeys** from first launch through season end, save/resume, optional next season and public release. Identify missing deliverables, including non-code work.
2. **Search existing issues first.** Update or split a current story when possible; create a new story/spike only when necessary. Keep issues independently reviewable and sized for the local-agent workflow.
3. For uncertainty that **blocks a dependent story**, create a **Spike** to gather evidence or **Design Decision** to authorize a direction. A discovery can be Ready **even while dependent implementation remains Backlog** if it does not itself need unfinished prerequisites.
4. Give each issue an outcome, acceptance criteria, requirement links, predecessor decisions, approximate priority, workstream/type, accountable role and meaningful verification. Avoid invented due dates, hours and arbitrary numerical mechanics.
5. **Ready** is not a fixed-length sprint queue; it includes any independently startable bounded issue, especially **Creative Director** decision stories that can progress in parallel with agent work. Assign those human-owned decisions to `williamwhorton`. Starting a Ready issue moves it to In Progress, not straight to Done.
6. Add/reconcile Project statuses via the established Actions automation. **Do not claim a successful board update without verifying the triggering comment and, when needed, workflow run.**
7. When approved decisions change MVP scope, update this map, the affected issues, requirement status, and ADRs. Preserve an explicit release path even if content/features are deferred. Human decision authority is unchanged.
8. Recheck the map periodically against the current GitHub issue inventory; this document is a **planning baseline** and will evolve, not an immutable feature promise.

**Next planning review:** after #20 MVP scope approval and after #4's prototype comparisons/ADR-0002. These may proceed concurrently.
