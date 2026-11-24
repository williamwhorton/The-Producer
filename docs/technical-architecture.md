# Technical Architecture — Constraints and Evaluation

**Status: PROPOSED. No engine or language has been approved.**

## Preferred boundaries
- **Simulation domain:** contestants, relationships, beliefs, movement, supernatural entities, producer interventions and deterministic event scheduling.
- **Observation boundary:** transforms actual world events into production-observable evidence and estimates. Never bypass it for player UI.
- **Presentation:** isometric/dollhouse rendering, interaction, audio and player-facing production tools.
- **Campaign/persistence:** scenario definitions, season outcomes, franchise-continuity state, contestant disposition, artifact provenance, unlocks and save/load.
- **Season-outcome evaluation:** evaluate persistent haunting separately from show continuity and any eventual survivor requirement; exact rules remain partly OPEN.
- **Debug/test harness:** headless seeded scenarios, traces, assertions and hidden-state inspection restricted to development.

## Candidate engine evaluation
The three disposable Godot proofs are merged. [Issue #4 architecture comparison](issue-4-architecture-evaluation.md) and [ADR-0002](decisions/ADR-0002-engine-and-presentation-approach.md) propose **Godot 4 + GDScript with fixed-angle 3D orthographic presentation**, with 2D isometric as a viable fallback. **This is a proposal, not a Creative Director-approved engine/language/rendering decision.** P-01 remains OPEN. A separate TypeScript simulation runtime or IPC service remains unsupported without a demonstrated need and new approval. Headless toy simulation is verified, but persistence, exports, native GPU performance and production scene/asset workflow are not.

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