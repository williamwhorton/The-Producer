# Simulation boundary

This module owns private simulation timing and event ordering. It runs without
a scene tree, renderer, HUD, or persistence. The static #27 house preview does
not instantiate it.

## Event scheduler (#28)

`event_scheduler.gd` implements the clock and live-trigger portion of the
[approved #17 pacing model](../../docs/issue-17-simulation-pacing.md):

- Construct with a seed, positive fixed tick duration (microseconds), and
  increasing fast/very-fast integer multipliers. Normal speed is 1×. There are
  no production defaults for duration or multipliers.
- A caller supplies elapsed time via `advance()` and applies pause/speed
  changes between calls. Speed changes how quickly ticks become due, not what
  a tick does. Pause discards elapsed time without clearing sub-tick progress
  from before the pause. No event pauses or slows the clock.
- Resolve each tick in order: pending manual live triggers first in submission
  order, then due autonomous events in registration order. Each trigger
  revalidates against current domain state immediately before execution, after
  any earlier trigger has resolved. Requests made during pause may be cancelled
  while paused; remaining requests are tried on the first update after resume.
  Running requests are tried on the next tick too.
- Only simulation code schedules autonomous work for future ticks. Resolvers
  cannot extend the current tick's batch. This is not a player API for timed
  or conditional triggers.

`advance()` does not publish raw events or logs. The regression fixture owns
its private trace and final state; neither is returned to the preview, renderer,
or HUD. Any future player view of live events must go through the approved
[observation boundary](../../docs/decisions/ADR-0004-producer-observation-boundary.md),
not the scheduler or test fixture.

Run from the repository root:

```sh
godot --headless --path game --script res://tests/scheduler.gd
```

On Godot `4.7.2.stable.official.ed1daf0bf`, this exited 0 with
`PASS: seeded scheduler ordering, tactical pause, live triggers, and speed invariance`.
The fixture compares ordered traces and final state for the same seed and
simulation-time inputs across reruns, elapsed-time chunks, speeds and pause
durations. A different seed changes actual results, not just metadata.
Same-version determinism is tested; cross-version determinism and save/load are
not claimed.

No new gameplay is wired into the preview. Contestant behavior, dialogue,
curfew/staging, actual device rules, player controls and live observation
remain separate work.
