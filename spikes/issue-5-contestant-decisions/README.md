# Issue #5 — Seeded contestant decision harness

This standalone Godot 4/GDScript prototype demonstrates scoped parts of G-02, G-06 and G-07, using fixture examples for proposed S-01, S-02, S-04 and T-01. [ADR-0002](../../docs/decisions/ADR-0002-engine-and-presentation-approach.md) approves the engine and layer separation; [ADR-0004](../../docs/decisions/ADR-0004-producer-observation-boundary.md) approves the source-grounded boundary. The matched #13/#14 house and #15 random-turn mechanics are feasibility fixtures, not requirements for this harness.

- `contestant_simulation.gd` takes an explicit seed, ordered initial contestant states, and optional scripted private exchanges. Fixture beliefs, perceived danger and motive determine whether a contestant investigates, avoids or attempts to quit. The seed only breaks ties between equally viable investigation routes. An attempted quit ends that actor's participation in the **fixture**, without resolving whether they leave or what happens to them.
- `observation_projector.gd` is the only player-data projection. An authorized synthetic sighting attests to movement in a particular place and tick, not the decision or cause. Later testimony is an attributed, unverified claim at receipt, not evidence of private truth. The projected records are detached and contain only scalar, allowlisted fields. Raw traces are for the domain and privileged tests, not presentation.
- This is not a production psychology or sensor model, a release access-control guarantee, a final schema, or an implementation of defense/banishment. There is no GUI, so no rendered behavior was inspected. Determinism is verified only on the tested Godot runtime.

## Evidence

Run from the repository root with a native Godot 4 binary on `PATH`. No editor import or additional dependencies are required.

| Command | Observed result |
| --- | --- |
| `godot --version` | `4.7.2.stable.official.ed1daf0bf` |
| `godot --headless --path spikes/issue-5-contestant-decisions --script res://tests/decision_test.gd` | Exit `0` twice: `PASS: seeded decisions and ordered observations (32 ticks)` |
| `godot --headless --path spikes/issue-5-contestant-decisions --script res://tests/privacy_test.gd` | Exit `0`: `PASS: independent observation privacy checks` |
| `godot --headless --path spikes/issue-5-contestant-decisions --script res://tests/decision_test.gd -- --force-failure` | Exit `1` as intended: `FAIL: intentional assertion failure` |

The decision suite compares ordered private and public traces, checks that another seed changes a fixture route, and checks that a changed starting belief can change a decision with the seed held fixed. The separate privacy suite uses paired worlds and hand-authored expectations to check unmonitored speech, invalid sources, nested metadata, exact public serialization, mutation isolation, hidden supernatural activity, and delayed false testimony. A fresh-session review of the actual code and tests is still required.
