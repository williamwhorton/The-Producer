# Technical Architecture — Constraints and Evaluation

**Status: Godot 4 + GDScript and fixed-angle 3D orthographic presentation APPROVED PROVISIONALLY (ADR-0002, 2026-11-23 ET).** Exact contracts and other choices remain open.

## Preferred boundaries
- **Simulation domain:** contestants, relationships, beliefs, movement, supernatural entities, producer interventions and deterministic event scheduling.
- **Observation boundary:** transforms actual world events into production-observable evidence and estimates. Never bypass it for player UI. **Approved #16/ADR-0005 baseline:** the producer's hidden surveillance provides visual coverage of every house room; door/environment sounds and bubble-inspected in-house dialogue are authorized observational channels. One house telephone exists and contestants are prohibited cell phones. Only captured speech/call portions may pass into the UI; no private thought or unmonitored off-site knowledge leaks.
- **World presentation:** fixed-angle 3D orthographic dollhouse as the provisional renderer; camera, mesh, lighting, floor cutaway, selection and visual effects stay renderer-specific, behind a small replaceable presentation interface (2D fallback retained).
- **UI / producer tools:** HUD, accessible controls and workflow are distinct from the world renderer and domain logic; consume approved observations, stable IDs and application actions, never private world internals or renderer node references for game decisions.
- **Campaign/persistence:** scenario definitions, season outcomes, operation-continuity and external-exposure state, contestant disposition, artifact provenance, unlocks and save/load.
- **Season-outcome evaluation:** evaluate persistent haunting separately from future-operation viability, contestant-fate consequences and any eventual survivor/death requirement; exact rules remain partly OPEN.
- **Debug/test harness:** headless seeded scenarios, traces, assertions and hidden-state inspection restricted to development.

## Candidate engine evaluation
The three disposable Godot proofs are merged. The Creative Director **approved provisionally** the recommendation in [ADR-0002](decisions/ADR-0002-engine-and-presentation-approach.md): **Godot 4 + GDScript with fixed-angle 3D orthographic presentation**, retaining [the 2D comparison](issue-4-architecture-evaluation.md) as a viable early fallback. The target is the 2D proof's clean, comic-like legibility with 3D lighting/shadow potential; stylized 3D has **not yet been demonstrated**. P-01 is provisionally resolved. Keep simulation, observation/application interface, world rendering and player-facing UI separate so a renderer change does not demand a rewrite of game rules, while acknowledging art/selection/shader migration costs. A TypeScript simulation runtime or IPC service remains unsupported without demonstrated need and new approval. Headless toy simulation is verified; persistence, exports, native GPU performance and a production asset pipeline are not.

## Visual production constraints (direction; not a final art pipeline)

Use *Darkest Dungeon* and *Cult of the Lamb* as **high-level visual/tonal references**, not material to duplicate. Aim for a readable, graphic-novel/comic-like dollhouse through stylized 3D shading, intentional silhouettes and controllable pools of light/shadow. Keep suspense and human stakes serious; avoid both photorealistic brutality and overly cute, glib horror. Test graphic edges and shadows for shimmer/aliasing and usability at intended zoom before spending on assets. Lighting, materials, outlines, and camera belong to the **world renderer**, independently of gameplay simulation, observation rules and UI/HUD. Specific methods and production art/audio/content decisions remain #22's remit.

## Determinism [PROPOSED]
Central seeded random stream(s), explicit tick/event ordering, stable serialization, and repeatable scenario fixtures. Test thousands of simulated ticks without graphics. Maintain causal event logs for agent debugging.

## Approved observation boundary — Issue #3

[ADR-0004](decisions/ADR-0004-producer-observation-boundary.md) **approves a source-mediated, allowlisted evidence projection** between private world events and all producer-facing world renderers, HUD panels, optional off-site narrative vignettes and reports (Creative Director, 2026-11-23 ET). An unobserved event remains private; a witness or staff account conveys an **attributed claim**, not omniscient truth. Exact surveillance, reporting, confidence and producer-action mechanics are deliberately deferred. The game should not grant a dollhouse renderer omniscient access to unobserved contestant behavior simply because its simulation includes that state.

## Producer dossier information boundary [CONFIRMED direction]

Each contestant starts with an authorized, pre-researched **producer dossier**: picture, age, sex, occupation, extremely brief background and **any known** exploitable fear or significant event. **Some dossiers have no known hook**. This is historical/background information gathered in advance by the producer, not a way to query current hidden emotions, beliefs, memories, plans or precise numerical state. Dossier facts are source-allowlisted for player presentation under ADR-0004; **recruiting/selecting contestants and researching backgrounds are future proposed mechanics**, not part of the initial player loop. Personalized overnight options depend on dossier facts where available. See [ADR-0006](decisions/ADR-0006-producer-preparation-and-practical-effects.md).

## Non-leakage architecture [REQUIRED]
Separate private world state from observable production state. Player-facing views should consume only sanctioned observation/estimate interfaces. Add tests for accidental exposure through API, serialization, debug overlays and logs.

## AI use — development decision versus game runtime
[ADR-0003](decisions/ADR-0003-cloud-first-agent-development.md) **approved** cloud-first AI tooling through ChatGPT-connected OpenCode Build for development (replacing the earlier local-default ADR-0001). This is **not a game-engine decision and does not approve cloud services or LLMs in the shipped game**. Gameplay-inference architecture remains unapproved; testable non-LLM logic is a reasonable candidate, but no contestant behavior algorithm is adopted here.

## Quality gates
Automated tests; static analysis where supported; scenario simulations; reviewer checks; reproducible builds; no silent requirement changes. Document actual command outputs and known limitations in PRs.

## Architecture decisions pending
Engine/language and initial renderer are **provisionally decided in ADR-0002**; still pending: ECS vs conventional object model, save format, simulation tick rate, navigation/pathfinding, audio and asset tooling (#22), CI platform and release targets.