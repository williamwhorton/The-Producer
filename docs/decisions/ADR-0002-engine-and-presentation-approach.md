# ADR-0002 — Godot engine and dollhouse presentation approach

**Status:** **PROPOSED — Creative Director approval required; no production choice adopted**  
**Date:** 2026-11-23  
**Owner:** Architect (recommendation); Creative Director (decision authority)  
**Related issue:** [#4](https://github.com/williamwhorton/The-Producer/issues/4)  
**Related requirements:** G-02, G-03, G-06 (confirmed); T-01, T-03, T-04 (proposed); P-01 (OPEN)  
**Evidence:** [Issue #4 comparison](../issue-4-architecture-evaluation.md) and merged proofs [#13](../../spikes/issue-4-2d/README.md), [#14](../../spikes/issue-4-3d/README.md), [#15](../../spikes/issue-4-simulation/README.md)

## Context

*The Producer* needs an isometric/dollhouse presentation (G-03), autonomous contestants (G-02), deliberately imperfect player information (G-06), and an engineering workflow that supports reproducible headless tests and local development on Bazzite. A visually appealing renderer is insufficient if it makes multistory occlusion, selection and player-information controls fragile. Equally, the ability to pass a headless test does not prove a full simulation architecture or shipping readiness.

Issue #4 approved three disposable, deliberately comparable experiments. All three are now merged: the 2D isometric house (#13), the 3D orthographic equivalent (#14) and a deterministic headless GDScript simulation/observation boundary (#15). The detailed [comparison](../issue-4-architecture-evaluation.md) distinguishes measured or observed results from projections and missing evidence.

This decision concerns **production engine/language and initial rendering approach**. It is not a decision about gameplay mechanics, artistic style, platform targets, simulation tick rate, persistence schema, production observation contract, AI-in-game inference, or monetization. The separate [ADR-0003](ADR-0003-cloud-first-agent-development.md) governs **development AI only**.

## Options considered

### A. Godot 4 + GDScript, fixed-angle 2D isometric

- **Demonstrated strengths:** matched 10×10 floor fixture, wall gaps, room selection, two-level toggling, cutaway, pan/zoom and A–B debug route; predictable composed 2D presentation and a comparatively direct 2D art path.
- **Costs/risks:** manually projects world/height into screen space and maintains wall/marker draw order, polygon picking and upper-floor overlap. Future multi-level depth or complex lighting may require further hand-maintained rules or shaders.
- **When preferable:** if the human prefers its exact visual readability or an approved art direction centers on 2D assets, or if later measured performance/asset-production cost favors it.

### B. Godot 4 + GDScript, fixed-angle **3D orthographic** (recommended)

- **Demonstrated strengths:** same fixture and interactions; built-in depth testing and camera-ray picking replace aspects of 2D manual overlap management. Primitive 3D meshes already receive basic shading, with a fixed projected dollhouse view. No third-party renderer, external simulation service or runtime paid LLM is needed.
- **Costs/risks:** mesh/material production and camera-space input are more involved; actual 3D geometry can obstruct room selection and ground markers, so cutaway/floor UX remains essential. The initial A-tile-edge ray-picking bug required a corrective PR. Real lighting atmosphere, scale performance, asset workflow and native compositor/GPU results are **not established**.
- **Why recommended:** for a multistory horror dollhouse, using Godot's native 3D depth and scene controls is a defensible simplification of long-term visibility/lighting concerns, provided the camera remains fixed-angle and scope is kept small. This is a **qualitative architectural judgment**, not a controlled performance or aesthetics win.

### C. Separate non-GDScript simulation service / TypeScript or C# core

- Could provide familiar ecosystems or more independent simulation tooling, but introduces language/toolchain and IPC/integration complexity **without evidence of necessity**.
- Neither the Godot-only headless proof nor current requirements show a need for external C#, a Node service, TCP/IPC or a database. **Not recommended initially.** Reconsider only on a concrete measured blocker and with explicit separate approval.

### D. Defer engine decision entirely

- Avoids commitment but blocks [#27](https://github.com/williamwhorton/The-Producer/issues/27) and the engine dependency for [#5](https://github.com/williamwhorton/The-Producer/issues/5) despite three functioning experiments. More generic comparison without a falsifiable question would create work without a clear decision benefit.
- Reasonable only if the Creative Director finds both visuals unacceptable, or specifies a critical missing acceptance test.

## Proposed decision — NOT APPROVED

**If and only if the Creative Director approves this ADR**, establish the following initial technical direction:

1. **Engine/language:** Godot 4, GDScript. Pin and record the actual stable Godot version used for the first production slice rather than silently upgrading it; the prototypes were exercised with `4.7.2.stable.official.ed1daf0bf`.
2. **Presentation:** fixed-angle **3D orthographic** dollhouse, with deliberate floor visibility and wall cutaway controls. The game remains a **producer-directed strategy/management experience**, not direct first-person or free-roaming contestant control. No free-orbit camera is authorized by this proposal.
3. **Simulation and observation boundary:** keep world simulation callable headlessly without rendering, with explicit seeded tick/event ordering; expose player-facing information through a separate, allowlisted observation projection rather than direct references to private contestant state. **Exact interface, observations and estimate mechanics remain pending Issue #3**; the proof's three fields and dummy psychology do not establish a production schema.
4. **Scope control:** introduce no external C# service, JSON/TCP IPC, SQLite, paid inference API, speculative ECS, generated house framework, or third-party test dependency merely to implement this decision. Do not copy disposable scripts wholesale into production without scope/quality review.
5. **Reversibility:** retain both isolated visual spikes as comparison evidence. If the first scoped 3D slice fails the agreed visual usability, performance or authoring acceptance conditions, reconsider 2D using **observed failures**, not architectural loyalty.

**Approval record:** _Pending Creative Director decision. No approval date, acceptance conditions or sign-off has been supplied._  
**Required human disposition:** Approve Option B; select Option A instead; or defer with an explicit additional evidence requirement. Do not change this line automatically on PR merge.

## Consequences and guardrails if approved

- Native Godot scene/render/test tools can serve both the presentation and the headless GDScript test harness, reducing initially necessary tooling. The existing proof demonstrates **feasibility for the toy scenario**, not production throughput, renderer scalability or full security isolation.
- A 3D fixed-camera workflow potentially eases overlapping floors and lighting, but demands careful cutaways, selectable room surfaces, readable markers and a measured asset pipeline. Maintain a small visibility regression fixture across future changes.
- Keep presentation from accessing private simulation dictionaries: observational data is a separate architectural boundary, with independent negative tests. GDScript underscore-prefixed fields provide no true access-control guarantee.
- **Save/load is not proved.** Godot has documented `FileAccess`, `JSON` and binary variant serialization, but restoring seeds, event order, versioned snapshots and hidden-state separation needs its **own** design and tests. No save format is selected here.
- **Export and performance remain unproved.** Godot has desktop export templates and an MIT engine license suitable for commercial distribution (with required license notices), but **no shipped package or performance benchmark exists**. Initial supported platforms and budgets require [#21](https://github.com/williamwhorton/The-Producer/issues/21); review future asset/plugin licenses separately.
- Continue the approved OpenCode Build → independent Reviewer → human acceptance workflow. Headless tests complement, not replace, on-screen visual and accessibility acceptance.

## Evidence and human verification

| Requirement / concern | Evidence | Strength |
| --- | --- | --- |
| G-03 dollhouse geometry / controls | Both [2D](../../spikes/issue-4-2d/README.md) and [3D](../../spikes/issue-4-3d/README.md) GUI/headless fixture proofs on a shared 10×10 house; screenshots and manual walkthroughs | **Demonstrated for the fixture**, not production art/readability |
| Two levels, cutaway, room picking | Both observed; 3D A-edge picking regression fixed after QA | **Demonstrated for the fixture** |
| Deterministic simulation concept (proposed T-01) | [#15](../../spikes/issue-4-simulation/README.md): same seed and initial state → same 100-tick ordered trace/final state; different seed → different action sequence; forced failure exits nonzero | **Demonstrated in recorded Godot version**, not cross-platform scale |
| Private data projection (G-06) | [#15](../../spikes/issue-4-simulation/tests/determinism_test.gd): camera-only reports, negative tests against hidden notes/fields/nested references and caller mutation | **Demonstrated as a data projection**, not a formal enforced access-control policy |
| Godot/Bazzite/agent workflow | Reproduced GUI behavior under Xvfb/Mesa llvmpipe and headless tests; independent PR review and human merge of #13–#15 | **Demonstrated on recorded tooling**, native compositor and export untested |
| Saving/loading, production performance, exports, licenses of future assets | No project-specific demonstrations; Godot official docs establish available interfaces and engine license | **Outstanding**, must not infer passing tests |

Reproduce from a checkout containing all three merged spikes:

```sh
godot --path spikes/issue-4-2d
godot --path spikes/issue-4-3d
godot --headless --path spikes/issue-4-2d --script res://tests/check_fixture.gd
godot --headless --path spikes/issue-4-3d --script res://tests/check_fixture.gd
godot --headless --path spikes/issue-4-simulation --script res://tests/determinism_test.gd
```

Review both windows with `C` (cutaway/full walls), `F` (upper floor), `Space` (scripted door-crossing), room picking and camera pan/zoom. Compare readability and desired mood; check the headless command prints `PASS: determinism and observation isolation (100 ticks)`. These are **human instructions**, not a claim that this architecture-only PR executed them.

## Follow-up / decisions not implied

1. **Creative Director approval gate:** evaluate the visual alternatives and explicitly approve/reject this ADR. If approved, update P-01 and `docs/technical-architecture.md` and close parent #4 only after recording the decision. Do **not** close #4 via this proposal PR.
2. **Issue #3:** independently propose and approve the private/observation/estimate contract. Until then, do not treat the #15 fixture projection as a permanent mechanics decision.
3. **Issue #27:** a minimal production project, **after** the approved engine ADR and the separate #20 MVP scope gate. First verify native-GPU launch, fixed-angle room visibility/selection and a simple no-simulation presentation path.
4. **Issue #5:** only unblock seeded contestant-decision harness after both the approved engine/language direction and approved #3 observation contract. Fixture `fear`, `intent` and random turn choices are **not** approved gameplay mechanics.
5. **Additional future validation:** first production slice must demonstrate a native-desktop GUI acceptance walkthrough, sensible multistory cutaway/selection, reproducible headless tests, and an initial scoped asset-authoring path. Plan save/load and packaging as explicit future tests. Set measurable frame-time targets only after platform/performance-budget decision (#21).

**External technical references (capabilities only):** [Godot license](https://godotengine.org/license/); [license compliance](https://docs.godotengine.org/en/stable/about/complying_with_licenses.html); [exporting projects](https://docs.godotengine.org/en/stable/tutorials/export/exporting_projects.html); [saving games](https://docs.godotengine.org/en/stable/tutorials/io/saving_games.html).
