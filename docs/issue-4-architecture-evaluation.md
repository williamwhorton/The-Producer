# Issue #4 — Godot architecture experiment: evidence and comparison

**Status:** Evaluation complete; recommendation **proposed**, not approved.  
**Date:** 2026-11-23  
**Owner:** Architect (proposal); Creative Director (decision)  
**Primary issue:** [#4](https://github.com/williamwhorton/The-Producer/issues/4)  
**Child proofs:** [#13 2D](https://github.com/williamwhorton/The-Producer/issues/13) · [#14 3D](https://github.com/williamwhorton/The-Producer/issues/14) · [#15 simulation](https://github.com/williamwhorton/The-Producer/issues/15)  
**Decision proposal:** [ADR-0002](../decisions/ADR-0002-engine-and-presentation-approach.md)

## Executive assessment

**Recommendation for Creative Director review:** Godot 4 with GDScript for the first production slice, with a **fixed-angle 3D orthographic dollhouse** as the initial presentation path. Keep domain simulation testable without rendering and route player-visible data through an explicit observation boundary. This is an **architectural recommendation, not an adopted decision**. The existing 2D prototype is a viable fallback if the 3D presentation proves too expensive or fails aesthetic/visibility acceptance.

The evidence is adequate to justify a *reversible first implementation path*, **not** to claim 3D looks better to the Creative Director, performs better, scales better, or is the correct production art pipeline. A short native-GPU visual/usability check and a production-slice test should be the first validation gates after approval, not a retroactive claim that the disposable prototypes already proved those things.

## Evidence inventory and provenance

| Proof | Delivered | Observed results | Important limit |
| --- | --- | --- | --- |
| [#13 / 2D isometric](../../spikes/issue-4-2d/README.md) | Godot project in `spikes/issue-4-2d/`; scripted grid projection, room picking, wall cutaway, floor toggle, camera pan/zoom, debug A–B movement | Recorded import, bounded headless launch and `tests/check_fixture.gd` passing; GUI interaction inspected under Xvfb/X11 with Mesa llvmpipe; [merged PR #72](https://github.com/williamwhorton/The-Producer/pull/72) | Primitive art and scripted geometry only; no real stair navigation, autonomous NPCs or native display/GPU comparison |
| [#14 / 3D orthographic](../../spikes/issue-4-3d/README.md) | Same 10×10 house and interactions; primitive 3D meshes, orthographic camera, depth-tested visibility and ray-based picking | Recorded import, headless scene test, fixture assertions and GUI/Xvfb checks passing; an initial A-edge picking regression was reproduced and fixed, then checked; [merged PR #75](https://github.com/williamwhorton/The-Producer/pull/75) | Different projected wall/level heights limit direct appearance comparison; no representative asset pipeline, shadow/lighting performance or real navigation |
| [#15 / headless boundary](../../spikes/issue-4-simulation/README.md) | Independent GDScript `RefCounted` simulation, fixed steps and RNG seed, ordered event trace, player observation projection, negative leakage tests | Recorded Godot `4.7.2.stable.official.ed1daf0bf`: repeated runs exit 0 with equal traces and `PASS: determinism and observation isolation (100 ticks)`; different seeds produce different actions; forced assertion exits 1; independent Reviewer recommended approval and [PR #79 merged](https://github.com/williamwhorton/The-Producer/pull/79) | Within-version/runtime proof only; no persistence, performance/load benchmark, actual player UI or enforceable encapsulation against arbitrary GDScript access |

**Evidence classification:** Results above are *recorded results from the merged prototypes and their READMEs*, cross-checked against the actual source. This architecture-only PR does **not** rerun Godot on the Creative Director's Bazzite machine. No native GPU or shipping build was measured. The 2D and 3D prototypes satisfy the **same approved room/door/marker/debug-route fixture**, but they are not pixel-identical and their projected wall/slab heights differ.

### Rendering alternatives evaluated

| Criterion | 2D isometric proof (#13) | 3D orthographic proof (#14) | Architectural interpretation |
| --- | --- | --- | --- |
| Required dollhouse look (G-03) | Explicit 2:1 projection of 2D cells/elevation | Fixed-angle `Camera3D` with orthographic projection of 3D geometry | **Both** meet the perspective requirement at prototype fidelity; art direction still needs human review |
| Occlusion / cutaway | Manual projected polygon and wall/marker depth ordering; fixed cutaway toggle | Depth buffer handles opaque overlap; fixed near-wall cutaway still required | **3D advantage in built-in visibility**, not an automatic solution to hiding walls |
| Upper level | Raised scripted slab/layer; upper room U hides underlying content | Physical upper slab; ground details can remain partly visible, depending on mesh heights | **No clear winner** from this fixture; both require deliberate multistory visibility UX |
| Room selection | Custom projected floor/wall polygon picking | Camera ray picking with visible tile top and obstruction handling | Both validated; **3D initially had a real edge-picking bug**, corrected in PR #75 |
| Camera / navigation affordance | `Camera2D` translate/zoom; scripted A–B route | Orthographic camera pan/zoom; same scripted A–B route | Near parity; **neither tests stair traversal, collision, pathfinding, autonomous movement or orbit** |
| Lighting / atmosphere potential | Face colors manually authored | Ambient and one key light shade 3D faces | 3D has a **plausible future tool advantage**, but dynamic horror lighting/shadows were not implemented or benchmarked |
| Implementation / authoring | One procedural `Node2D` `_draw()` scene, hand projection and sorting | Runtime mesh generation, `Camera3D`, materials and ray pick logic | Trade manual projection/sorting for mesh/camera/rendering complexity; both need a data-driven production level workflow |
| UI readability | Controlled layering and strong illustrative clarity possible | Geometry may obscure markers, especially under upper slab | Both need acceptance testing at playable scale, on intended displays |
| Performance | Unmeasured at production scale | Unmeasured at production scale | **No ranking justified** |
| Local agent ergonomics | Implemented, repaired and visually verified | Implemented, repaired and visually verified | Both compatible with current GitHub/OpenCode workflow; 3D had a fixable picking regression |

**Suggested choice:** Choose 3D orthographic *provisionally* because built-in depth, ray casting and 3D face lighting are a reasonable fit for several stacked floors and horror presentation, while preserving the dollhouse camera rather than converting the game into a freely rotating 3D exploration game. This is a preference among **functioning alternatives**, not a demonstrated quantitative performance or gameplay win. If the Creative Director prefers the 2D reading/style in the actual windows, 2D remains technically credible.

### Simulation, observation and integration

- The [#15 `simulation.gd`](../../spikes/issue-4-simulation/simulation.gd) uses GDScript `RefCounted` with explicit `step()`, seeded `RandomNumberGenerator`, a tick counter, and event append order. It runs without rendering or scene dependencies and requires no extra process, C#, IPC or database. This supports *trying* GDScript for a testable core, not certifying production-scale simulation throughput.
- The proof's `get_observation()` projects only `tick`, `kind`, and `source` from camera-sourced events, suppresses an internal unsourced note, and returns new arrays/records so caller mutation does not modify internal events. Its tests verify the known private fixture fields and nested event data are absent from player reports.
- **Privacy caveat:** GDScript underscore-prefixed members are conventions, not enforced data hiding. The simulation test directly accesses internal fields for assertions. Production code should avoid injecting references to simulation objects or private event dictionaries into player-facing nodes, serialized reports, overlays or logs. The **actual observation/estimate contract and leak tests remain Issue #3**, pending Creative Director approval; this proposal does not select unapproved observation mechanics.
- Rendering should depend on published observation data rather than read contestant fear/intent directly. Keep reproducibility tests on the domain side and GUI tests on the presentation side; do **not** harden this disposable fixture into an invented production framework.
- Seed replay is verified only within one installed Godot version/runtime. Floating-point use, timers, physics and unordered iteration can change the guarantees. Design those decisions later and test them against actual scenarios.

### Other architecture criteria in #4

| Criterion | Verified now | Remaining validation |
| --- | --- | --- |
| Godot on Bazzite / Linux | Native Godot `4.7.2` was used to execute two GUI prototypes and a headless GDScript proof. Xvfb + software rendering GUI evidence was captured. | Test on the Creative Director's **native compositor/GPU** and target hardware; log actual driver/runtime issues |
| Automated tests / deterministic headless logic | Built-in `godot --headless --path ... --script ...` executes without third-party test framework; #15 proved same-seed traces and negative observation tests | Longer/load scenarios, failure reproduction, version pinning and stability in CI |
| Save / load | **Not implemented or tested in any spike.** Godot provides `FileAccess`, `JSON` and binary variant I/O in its documented API | Prototype versioned save/load, snapshot migration, stable event/order/seed restoration and private-vs-public save boundaries as a separate scoped issue |
| Packaging / deployment | **No exported build produced.** Godot supports export presets and downloadable templates for desktop and other platforms | Pick initial platform in [#21](https://github.com/williamwhorton/The-Producer/issues/21), produce real exports, test startup, UI, accessibility and performance on target hardware |
| Licensing | Godot itself is MIT-licensed and commercially usable; include required attribution/license notice in distributed projects. [Official Godot license](https://godotengine.org/license/), [license compliance](https://docs.godotengine.org/en/stable/about/complying_with_licenses.html) | Review *all* eventual third-party asset/plugin/audio licenses individually; prototype placeholders do not clear future content |
| Agent-driven implementation | #13, #14, #15 produced runnable PRs with CLI/test evidence, fresh review and human acceptance; README commands are reproducible | Do not assume agents can validate atmosphere, usability or packaging without human checks; keep PR Human Testing instructions mandatory |
| Cost / cloud | Godot tests and runtime prototypes use no cloud inference; development AI uses the separately approved [ADR-0003](../decisions/ADR-0003-cloud-first-agent-development.md) | Do not introduce paid/cloud runtime services or external simulation processes without separate authorization |

Authoritative background: [Godot exporting projects](https://docs.godotengine.org/en/stable/tutorials/export/exporting_projects.html), [Godot saving games](https://docs.godotengine.org/en/stable/tutorials/io/saving_games.html), [Godot FileAccess](https://docs.godotengine.org/en/stable/classes/class_fileaccess.html). These document *available capabilities*, not results of tests in this project.

## Reproducible inspection before the decision

From the normal main checkout (after pulling merged PRs):

```sh
godot --path spikes/issue-4-2d
godot --path spikes/issue-4-3d
godot --headless --path spikes/issue-4-2d --script res://tests/check_fixture.gd
godot --headless --path spikes/issue-4-3d --script res://tests/check_fixture.gd
godot --headless --path spikes/issue-4-simulation --script res://tests/determinism_test.gd
```

Compare *C* (full walls / cutaway), *F* (upper floor visibility), *Space* (debug crossing), room selection and pan/zoom in **both** windows. When judging renderer choice, prioritize readability of overlapping rooms, desired horror atmosphere, ability to select a room behind an obstruction, and expected asset-authoring burden. Avoid mistaking the differing wall/upper heights for a controlled image quality measurement.

## Decision and follow-up boundaries

1. **Creative Director decides:** approve proposed Godot 4 + GDScript + 3D orthographic, choose 2D isometric instead, or defer for a *specific* missing test. Do not auto-approve based on an agent's recommendation.
2. Record the human decision and any conditions in [ADR-0002](../decisions/ADR-0002-engine-and-presentation-approach.md), update `P-01` and `docs/technical-architecture.md` only **after** approval.
3. A signed-off engine choice does **not** automatically approve the private-state contract, gameplay loop, save schema, exact rendering art style, autonomous contestant algorithms or platform targets.
4. [#27](https://github.com/williamwhorton/The-Producer/issues/27) (minimal production project) additionally depends on #20 MVP scope; [#5](https://github.com/williamwhorton/The-Producer/issues/5) remains blocked until **both** the engine/language choice and [#3](https://github.com/williamwhorton/The-Producer/issues/3) observation contract are approved. Parent #4 remains open until the human accepts the ADR.
