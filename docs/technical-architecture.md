# Technical Architecture — Constraints and Evaluation

**Status: Godot 4 + GDScript and fixed-angle 3D orthographic presentation APPROVED PROVISIONALLY (ADR-0002, 2026-11-23 ET).** Exact contracts and other choices remain open.

## Preferred boundaries
- **Simulation domain:** contestants, relationships, beliefs, movement, supernatural entities, producer interventions and deterministic event scheduling.
- **Observation boundary:** transforms actual world events into production-observable evidence and estimates. Never bypass it for player UI.
- **World presentation:** fixed-angle 3D orthographic dollhouse as the provisional renderer; camera, mesh, lighting, floor cutaway, selection and visual effects stay renderer-specific, behind a small replaceable presentation interface (2D fallback retained).
- **UI / producer tools:** HUD, accessible controls and workflow are distinct from the world renderer and domain logic; consume approved observations, stable IDs and application actions, never private world internals or renderer node references for game decisions.
- **Campaign/persistence:** scenario definitions, season outcomes, franchise-continuity state, contestant disposition, artifact provenance, unlocks and save/load.
- **Season-outcome evaluation:** evaluate persistent haunting separately from show continuity and any eventual survivor requirement; exact rules remain partly OPEN.
- **Debug/test harness:** headless seeded scenarios, traces, assertions and hidden-state inspection restricted to development.

## Candidate engine evaluation
The three disposable Godot proofs are merged. The Creative Director **approved provisionally** the recommendation in [ADR-0002](decisions/ADR-0002-engine-and-presentation-approach.md): **Godot 4 + GDScript with fixed-angle 3D orthographic presentation**, retaining [the 2D comparison](issue-4-architecture-evaluation.md) as a viable early fallback. The target is the 2D proof's clean, comic-like legibility with 3D lighting/shadow potential; stylized 3D has **not yet been demonstrated**. P-01 is provisionally resolved. Keep simulation, observation/application interface, world rendering and player-facing UI separate so a renderer change does not demand a rewrite of game rules, while acknowledging art/selection/shader migration costs. A TypeScript simulation runtime or IPC service remains unsupported without demonstrated need and new approval. Headless toy simulation is verified; persistence, exports, native GPU performance and a production asset pipeline are not.

## Determinism [PROPOSED]
Central seeded random stream(s), explicit tick/event ordering, stable serialization, and repeatable scenario fixtures. Test thousands of simulated ticks without graphics. Maintain causal event logs for agent debugging.

## Non-leakage architecture [REQUIRED]
Separate private world state from observable production state. Player-facing views should consume only sanctioned observation/estimate interfaces. Add tests for accidental exposure through API, serialization, debug overlays and logs.

## AI use — development decision versus game runtime
[ADR-0003](decisions/ADR-0003-cloud-first-agent-development.md) **approved** cloud-first AI tooling through ChatGPT-connected OpenCode Build for development (replacing the earlier local-default ADR-0001). This is **not a game-engine decision and does not approve cloud services or LLMs in the shipped game**. Gameplay-inference architecture remains unapproved; testable non-LLM logic is a reasonable candidate, but no contestant behavior algorithm is adopted here.

## Quality gates
Automated tests; static analysis where supported; scenario simulations; reviewer checks; reproducible builds; no silent requirement changes. Document actual command outputs and known limitations in PRs.

## Architecture decisions pending
Engine/language; ECS vs conventional object model; save format; simulation tick rate; navigation/pathfinding; audio and asset tooling; CI platform and release targets.