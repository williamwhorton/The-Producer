# Issue #15 — Headless simulation and observation proof

This disposable Godot/GDScript fixture (v1) supplies evidence for [#4](https://github.com/williamwhorton/The-Producer/issues/4). It tests a headless simulation (proposed T-01/T-03) with autonomous fixture actions (G-02) and limited player information (G-06). It does not implement quitting, contestant psychology, scoring, the visual house fixture, the eventual observation contract in #3, or the gameplay harness in #5.

## How the fixture works

- `simulation.gd` is a `RefCounted` with no scene-tree, physics, graphics, or external dependency. Each explicit `step()` consumes a seeded random choice and records one toy turn action. Events are ordered by tick, then append order within a tick. There is no game-time tick rate or player control.
- The private fixture includes `fear`, `intent`, and the RNG seed/state. At tick 3 the simulation also appends a private note without a camera source. The visible action still occurs at that tick.
- `get_observation()` is the only player-facing read interface in this proof. Its report contains fresh records with only `tick` (integer), `kind` (`turn_left` or `turn_right`), and `source` (`fixture_camera`). It excludes the private note, private state, and nested event payloads, even those attached to visible events. A future scene can instantiate the same script and read this projection; it should not inspect simulation internals.
- The runner inspects internal trace and final state directly for tests only. Underscore-prefixed GDScript fields are a convention, not enforced access control against arbitrary scripts. There is no production UI, release build, or visual check.

## Rerun on Bazzite

From the repository root in a Bazzite terminal, use a native stable Godot 4 executable available as `godot` (or substitute its full path). No editor import or framework install is needed. These commands are the launch and test entry point; this project intentionally has no GUI main scene.

```bash
godot --version
godot --headless --path spikes/issue-4-simulation --script res://tests/determinism_test.gd
echo "$?"
```

Expect the version, two short public action traces, `PASS`, and exit status `0`. Run the test a second time in the same runtime to compare the printed traces. The runner itself compares all 100 ticks for repeated seed `12345`, checks the final private state and ordering (including the same-tick note), and compares the public action sequence with seed `67890` so changing seed metadata alone cannot pass. It also checks exact report contents, serialization, and isolation from caller mutation.

To check the runner's nonzero exit path, run this separate command:

```bash
godot --headless --path spikes/issue-4-simulation --script res://tests/determinism_test.gd -- --force-failure
echo "$?"
```

Expect `FAIL: intentional assertion failure` and exit status `1`.

## Recorded evidence

Fixture script v1 with `godot --version`: `4.7.2.stable.official.ed1daf0bf`. Two normal invocations exited `0` with the same output:

```text
Godot Engine v4.7.2.stable.official.ed1daf0bf - https://godotengine.org

Public trace, ticks 1–5, seed 12345: ["turn_left", "turn_right", "turn_right", "turn_left", "turn_left"]
Public trace, ticks 1–5, seed 67890: ["turn_left", "turn_left", "turn_right", "turn_right", "turn_left"]
PASS: determinism and observation isolation (100 ticks)
```

The forced-failure invocation printed the same engine banner and trace lines, then `FAIL: intentional assertion failure`, and exited `1`. No GUI inspection was performed (headless-only proof). This evidence covers the tested runtime only; it makes no determinism claim across Godot versions or machines. The Bazzite steps are provided for reproduction, not as evidence of a separate run.
