# Simulation boundary

This module owns simulation timing, event ordering and house routing. It runs
without a scene tree, renderer, HUD, or persistence. The house preview uses a
projection of the static floor plan; it does not run the scheduler.

## House layout and routing (#29)

`house_layout.gd` models the existing [#27 preview](../README.md) as one
authored floor. Coordinates are `(column, floor, row)`. On floor `0`, the
parlor occupies columns `-4..-1` and the study `0..3`, both in rows `-2..2`.
The four furniture footprints exclude cells conservatively; the remaining
cells are traversable. Walls span the partition except for a bidirectional
door between `(-1, 0, 0)` and `(0, 0, 0)`.

`find_route()` returns a shortest cardinal-cell route including both endpoints,
or an empty array for invalid, blocked or unreachable endpoints. Callers can
exclude obstructed cells for a query without mutating the plan. The `front`
exit in the study is an opening from `(2, 0, 2)` toward `(2, 0, 3)`;
`route_to_exit()` ends at the interior cell. An exterior cell is never a route
destination, and reaching the threshold does not decide whether someone leaves.

No floor changes are authored. The [#4 comparison fixture](https://github.com/williamwhorton/The-Producer/issues/4)
is disposable and only approved a stair *marker*, not character stair routing.
Other floors are therefore invalid. There is no runtime actor, door lock,
collision avoidance, or season-content pipeline in this slice.

```sh
godot --headless --path game --script res://tests/house_navigation.gd
```

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
