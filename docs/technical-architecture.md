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
Godot + GDScript is a leading candidate, not a final choice. Compare 2D isometric and 3D orthographic scene approaches. A separate TypeScript simulation runtime is an alternative only if a prototype demonstrates sufficient value to justify integration complexity. Evaluate: agent tool compatibility, headless testability, data-driven levels, rendering, save/load, packaging, licensing, Bazzite/Linux workflow and developer ergonomics.

## Determinism [PROPOSED]
Central seeded random stream(s), explicit tick/event ordering, stable serialization, and repeatable scenario fixtures. Test thousands of simulated ticks without graphics. Maintain causal event logs for agent debugging.

## Non-leakage architecture [REQUIRED]
Separate private world state from observable production state. Player-facing views should consume only sanctioned observation/estimate interfaces. Add tests for accidental exposure through API, serialization, debug overlays and logs.

## AI runtime policy [PROPOSED]
Use local models to *develop* the game. Do not assume shipped gameplay requires an LLM. Rule-based, utility-based or other testable decision systems are preferable as a baseline. Optional narrative generation can be evaluated separately.

## Quality gates
Automated tests; static analysis where supported; scenario simulations; reviewer checks; reproducible builds; no silent requirement changes. Document actual command outputs and known limitations in PRs.

## Architecture decisions pending
Engine/language; ECS vs conventional object model; save format; simulation tick rate; navigation/pathfinding; audio and asset tooling; CI platform and release targets.