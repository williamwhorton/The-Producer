# ADR-0002 — Godot engine and dollhouse presentation approach

**Status:** **APPROVED — PROVISIONAL** (Creative Director; 2026-11-23, America/New_York). Godot 4 + GDScript with 3D orthographic presentation is the initial direction; 2D remains an explicitly supported fallback before major art investment.  
**Date:** 2026-11-23  
**Owner:** Architect (recommendation); Creative Director (decision authority)  
**Related issue:** [#4](https://github.com/williamwhorton/The-Producer/issues/4)  
**Related requirements:** G-02, G-03, G-06 (confirmed); T-01, T-04 (proposed); T-03 (approved boundary principle; detailed contracts TBD); P-01 (approved provisionally)  
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

### B. Godot 4 + GDScript, fixed-angle **3D orthographic** (selected provisionally)

- **Demonstrated strengths:** same fixture and interactions; built-in depth testing and camera-ray picking replace aspects of 2D manual overlap management. Primitive 3D meshes already receive basic shading, with a fixed projected dollhouse view. No third-party renderer, external simulation service or runtime paid LLM is needed.
- **Costs/risks:** mesh/material production and camera-space input are more involved; actual 3D geometry can obstruct room selection and ground markers, so cutaway/floor UX remains essential. The initial A-tile-edge ray-picking bug required a corrective PR. Real lighting atmosphere, scale performance, asset workflow and native compositor/GPU results are **not established**.
- **Why recommended:** for a multistory horror dollhouse, using Godot's native 3D depth and scene controls is a defensible simplification of long-term visibility/lighting concerns, provided the camera remains fixed-angle and scope is kept small. This is a **qualitative architectural judgment**, not a controlled performance or aesthetics win.

### C. Separate non-GDScript simulation service / TypeScript or C# core

- Could provide familiar ecosystems or more independent simulation tooling, but introduces language/toolchain and IPC/integration complexity **without evidence of necessity**.
- Neither the Godot-only headless proof nor current requirements show a need for external C#, a Node service, TCP/IPC or a database. **Not recommended initially.** Reconsider only on a concrete measured blocker and with explicit separate approval.

### D. Defer engine decision entirely

- Avoids commitment but blocks [#27](https://github.com/williamwhorton/The-Producer/issues/27) and the engine dependency for [#5](https://github.com/williamwhorton/The-Producer/issues/5) despite three functioning experiments. More generic comparison without a falsifiable question would create work without a clear decision benefit.
- Reasonable only if the Creative Director finds both visuals unacceptable, or specifies a critical missing acceptance test.

## Decision — APPROVED PROVISIONALLY

**Creative Director's decision, 2026-11-23 (America/New_York):** Begin with **Godot 4 + GDScript and a fixed-angle 3D orthographic dollhouse**. The 2D prototype has a cleaner, appealing comic-like visual treatment; the Director expects the 3D renderer may reproduce that stylization while also permitting dynamic lighting and shadows. This is an **art direction hypothesis to test**, not a claim that the existing 3D prototype already achieves the look.

The decision is explicitly **reversible before substantial art production**. The architectural boundary must make a presentation swap practical without rebuilding contestant simulation or player-information rules. It does not promise switching 2D↔3D is cost-free: asset formats, occlusion, lighting, cameras, picking, animation and visual composition remain renderer-specific.

1. **Engine/language:** Godot 4 and GDScript for the initial production path. Pin the chosen stable Godot version for the first production slice and log any upgrade; the disposable prototypes used `4.7.2.stable.official.ed1daf0bf`.
2. **Presentation adapter:** Initial implementation uses **fixed-angle 3D orthographic** scene nodes and controls, supporting floor visibility, wall cutaway, room selection and atmospheric lighting/shadows as needed. Keep all engine-specific projection, picking, mesh, materials, camera and visual layer logic **behind an explicit presentation boundary**. Preserve the 2D approach as a fallback, not a second production renderer to maintain in parallel.
3. **Separate three concerns:** (a) **game/simulation domain**, with deterministic and headless-testable state/events; (b) **observation/application interface**, exposing allowed evidence, state changes and producer actions to player features (exact observation contract remains **Issue #3**); and (c) **presentation**, split into the **world view renderer** (2D or 3D) and the **UI/HUD/producer tools**. UI must not import renderer-specific scene classes to determine game rules, and neither UI nor renderer receives unfiltered private simulation dictionaries. Share stable IDs and authorized view data, not 3D node references or 2D pixel coordinates, across boundaries. Avoid designing heavyweight frameworks before there is a real production use case.
4. **Low-art-cost validation:** Test readable comic-like/stylized 3D treatment, camera/selection and lighting/shadows with cheap placeholders and native desktop viewing **before committing substantial custom art assets**. If 3D cannot meet the desired readability/aesthetic or shows meaningful measured complexity/performance problems, re-evaluate using the retained #13 2D proof and specific evidence; bring significant scope changes back for human approval.
5. **Scope control:** No external simulation service, paid inference runtime, C#/TypeScript/IPC bridge, database, ECS, save format, free-roaming camera, gameplay rule, or permanent observation schema is selected by this ADR. Do not carry disposable prototype code wholesale into production.

**Approved by:** Creative Director, 2026-11-23 (ET). **Approval scope:** provisional engine/language and renderer default **plus separation of simulation, observation, world presentation and UI**. This sign-off **does not** constitute acceptance/merge of the documentation PR or approval of later mechanics.

**Explicitly deferred creative questions:** How voluntary exits, eliminations, deaths and disappearances are handled; how multiple seasons credibly operate; and even whether the ostensible TV show is genuine or an elaborate lie told to contestants. These are exploration options, **not new confirmed fiction or mechanics**. The current reality-show premise (G-01) remains confirmed **unless changed through a separate Creative Director decision**. These questions need not hold up engine selection, engineering boundaries or the early technical skeleton; revisit before implementing dependent season/exit/narrative systems (including #7/P-04 and relevant planning).


## Visual reference direction — to validate, not a final art bible

The Creative Director identifies **Darkest Dungeon** and **Cult of the Lamb** as *broad visual and tonal references*, not assets, characters, trademarks or compositions to reproduce. They value the 2D proof's clean comic-like appeal, and want to explore a **stylized 3D treatment that preserves that readability while adding controlled lighting and shadows**.

- **Visual language to investigate:** strong, readable silhouettes and deliberate shape design; graphic/illustrative edges rather than realism; selective heavy shadows and directional or dramatic lighting; a restrained palette with purposeful contrasting accents; legible room geometry, contestants and production information at the actual isometric zoom level. A stylized 3D environment may use simplified geometry, painterly color blocks, color grading or toon/ink-inspired shaders. Those are **candidate techniques, not mandated implementation choices**.
- **Tonal balance:** avoid photorealistic depictions that could make the player's complicity in cruelty too viscerally alienating; equally, avoid an excessively cute, glib or jokey tone that turns contestants into disposable punchlines or drains the horror of consequence. Charm and occasional darkly humorous juxtaposition may invite engagement, while dread, uncertainty, humanity and the consequences of harm remain credible. This describes the **intended player experience**, not approval of violence, narrative outcomes or a final content rating.
- **3D-specific caution:** graphic shadows and thick edges should support mood **without hiding room selection, contestant silhouettes or actionable observations**. Thin animated outlines, hard shadow maps and high-contrast patterns can still shimmer or alias at distance; stylization **reduces dependence on photorealistic surface detail**, but does **not** eliminate the need to test edge stability, shadow quality and legibility on the native desktop.
- **Art-cost gate:** before commissioning or generating production assets, make a *small, inexpensive* style validation using the existing or similarly simple 3D room, at the intended camera scale. Compare (A) a mundane, inviting/normal scene and (B) the **same room under an unsettling supernatural-lighting treatment**. Keep geometry and gameplay identical so the lighting and treatment are the tested differences. Assess silhouettes, room picking, camera zoom, upper-floor occlusion, readable UI, edge/shadow stability and whether the mood stays genuinely unsettling rather than silly or merely gruesome. Document observed results and exact human testing steps.
- **Architecture boundary:** materials, post-processing, lighting, outlines and camera controls belong to the replaceable **world renderer**, not simulation or UI business rules. The HUD can have a coherent illustrative identity, but remains a separate interface with its own accessibility/readability checks. Do not create a permanent art pipeline, shader stack or second simultaneous renderer merely to support this exploration.

This guidance helps scope [Issue #22 — visual/audio/content presentation](https://github.com/williamwhorton/The-Producer/issues/22), which still owns approval of a practical style guide, audio approach, content boundaries, asset licensing and final MVP art scope. **The visual references are direction, not a lock on detailed assets, shaders, gore levels, or character treatment.**

## Consequences and guardrails (provisional approval)

- Native Godot scene/render/test tools can serve both the presentation and the headless GDScript test harness, reducing initially necessary tooling. The existing proof demonstrates **feasibility for the toy scenario**, not production throughput, renderer scalability or full security isolation.
- A 3D fixed-camera workflow potentially eases overlapping floors and lighting, but demands careful cutaways, selectable room surfaces, readable markers and a measured asset pipeline. Maintain a small visibility regression fixture across future changes. **Prove a stylized, comic-like 3D visual treatment and assess shadows in cheap assets before production art investment.**
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

1. **Decision recorded:** the Creative Director approved the **provisional** engine and rendering approach on 2026-11-23 (ET). The requirements register and technical architecture now reflect that bounded decision. **Parent #4 closes only after the human accepts and merges this documentation PR**; the ADR does not approve game implementation by itself.
2. **Issue #3:** independently propose and approve the private/observation/estimate contract. Until then, do not treat the #15 fixture projection as a permanent mechanics decision.
3. **Issue #27:** a minimal production project, **after** the approved engine ADR and the separate #20 MVP scope gate. First verify native-GPU launch, fixed-angle room visibility/selection and a simple no-simulation presentation path.
4. **Issue #5:** only unblock seeded contestant-decision harness after both the approved engine/language direction and approved #3 observation contract. Fixture `fear`, `intent` and random turn choices are **not** approved gameplay mechanics.
5. **Additional future validation:** first production slice must demonstrate a native-desktop GUI acceptance walkthrough, sensible multistory cutaway/selection, reproducible headless tests, and an initial scoped asset-authoring path. Plan save/load and packaging as explicit future tests. Set measurable frame-time targets only after platform/performance-budget decision (#21).

**External technical references (capabilities only):** [Godot license](https://godotengine.org/license/); [license compliance](https://docs.godotengine.org/en/stable/about/complying_with_licenses.html); [exporting projects](https://docs.godotengine.org/en/stable/tutorials/export/exporting_projects.html); [saving games](https://docs.godotengine.org/en/stable/tutorials/io/saving_games.html).
