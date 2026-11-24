# Issue #4 — Godot architecture experiment: evidence and comparison

**Status:** Evaluation complete; **provisional 3D direction approved** by Creative Director on 2026-11-23 (ET).  
**Date:** 2026-11-23  
**Owner:** Architect (proposal); Creative Director (decision)  
**Primary issue:** [#4](https://github.com/williamwhorton/The-Producer/issues/4)  
**Child proofs:** [#13 2D](https://github.com/williamwhorton/The-Producer/issues/13) · [#14 3D](https://github.com/williamwhorton/The-Producer/issues/14) · [#15 simulation](https://github.com/williamwhorton/The-Producer/issues/15)  
**Decision record:** [ADR-0002](decisions/ADR-0002-engine-and-presentation-approach.md) — provisionally approved

## Executive assessment

**Approved provisional direction:** Godot 4 with GDScript, using a **fixed-angle 3D orthographic dollhouse** initially. Keep simulation, player observation/application services, world renderer and UI/HUD separate. The Creative Director values the cleaner, comic-like aesthetic of the 2D proof and wants to test whether stylized 3D can retain it **while enabling lighting and shadows**. This is a hypothesis for the first cheap-art slice, not an already-demonstrated outcome. The existing 2D proof remains a viable fallback before significant art investment.

The evidence supports a *reversible initial implementation path*, **not** a claim that the current 3D proof already matches the appealing 2D style, performs better, or proves a production art pipeline. Separate the simulation and observation/application contracts from both the renderer and the HUD. A switch will still require renderer-specific camera, picking, assets, shaders and layout work. A native-GPU comic-like 3D style/lighting and usability check is an early post-decision validation gate, not a result already measured.

## Evidence inventory and provenance

| Proof | Delivered | Observed results | Important limit |
| --- | --- | --- | --- |
| [#13 / 2D isometric](../spikes/issue-4-2d/README.md) | Godot project in `spikes/issue-4-2d/`; scripted grid projection, room picking, wall cutaway, floor toggle, camera pan/zoom, debug A–B movement | Recorded import, bounded headless launch and `tests/check_fixture.gd` passing; GUI interaction inspected under Xvfb/X11 with Mesa llvmpipe; [merged PR #72](https://github.com/williamwhorton/The-Producer/pull/72) | Primitive art and scripted geometry only; no real stair navigation, autonomous NPCs or native display/GPU comparison |
| [#14 / 3D orthographic](../spikes/issue-4-3d/README.md) | Same 10×10 house and interactions; primitive 3D meshes, orthographic camera, depth-tested visibility and ray-based picking | Recorded import, headless scene test, fixture assertions and GUI/Xvfb checks passing; an initial A-edge picking regression was reproduced and fixed, then checked; [merged PR #75](https://github.com/williamwhorton/The-Producer/pull/75) | Different projected wall/level heights limit direct appearance comparison; no representative asset pipeline, shadow/lighting performance or real navigation |
| [#15 / headless boundary](../spikes/issue-4-simulation/README.md) | Independent GDScript `RefCounted` simulation, fixed steps and RNG seed, ordered event trace, player observation projection, negative leakage tests | Recorded Godot `4.7.2.stable.official.ed1daf0bf`: repeated runs exit 0 with equal traces and `PASS: determinism and observation isolation (100 ticks)`; different seeds produce different actions; forced assertion exits 1; independent Reviewer recommended approval and [PR #79 merged](https://github.com/williamwhorton/The-Producer/pull/79) | Within-version/runtime proof only; no persistence, performance/load benchmark, actual player UI or enforceable encapsulation against arbitrary GDScript access |

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

- The [#15 `simulation.gd`](../spikes/issue-4-simulation/simulation.gd) uses GDScript `RefCounted` with explicit `step()`, seeded `RandomNumberGenerator`, a tick counter, and event append order. It runs without rendering or scene dependencies and requires no extra process, C#, IPC or database. This supports *trying* GDScript for a testable core, not certifying production-scale simulation throughput.
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

## Recorded decision and follow-up boundaries

1. **Approved provisionally:** Godot 4 + GDScript + 3D orthographic as the initial renderer; retain 2D as a fallback. [ADR-0002](decisions/ADR-0002-engine-and-presentation-approach.md) records the Creative Director's preference for 2D's clean, comic-like look and the hypothesis that 3D can achieve a similar aesthetic while retaining lighting/shadow options. This is **not** an automatic mandate for realistic art or camera orbit.
2. **Architecture safeguard:** Keep **game logic / hidden world state**, **observation and game-application interface**, **world renderer**, and **UI/HUD** distinct. Only authorized player-facing data crosses into UI/presentation; do not make UI logic depend on 3D scene nodes or hard-code 2D coordinates into the simulation. Rendering adapters remain replaceable *in principle*, but replacement has real visual/asset and integration cost.
3. **Open creative direction:** Contestant exits, elimination/public accounting, how additional seasons remain plausible, and whether the show itself is genuine or an elaborate fiction are **deferred design questions**, not blockers to the engine decision or a narrow technical skeleton. Current confirmed G-01 remains in force until explicitly amended. Track these before implementing narrative or gameplay contracts dependent on them.
4. **Human merge/acceptance:** The architecture proposal and proof comparison were accepted in principle. Parent #4 should close when this updated documentation PR is accepted/merged; do not misrepresent a provisional choice as final art direction, a performance guarantee or approval for additional systems.
5. **Other dependencies:** [#27](https://github.com/williamwhorton/The-Producer/issues/27) also depends on #20 MVP scope; [#5](https://github.com/williamwhorton/The-Producer/issues/5) remains blocked until [#3](https://github.com/williamwhorton/The-Producer/issues/3) observation contract is approved. No actual UI observation policy, save schema, NPC algorithms, finished art, or release platforms are chosen in this ADR.
