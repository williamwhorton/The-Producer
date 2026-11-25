# Simulation boundary

This module owns simulation timing, event ordering, house routing, and prototype
contestant autonomy. It runs without a scene tree, renderer, HUD, or persistence.
The house preview uses a projection of the static floor plan; it does not run
the scheduler or contestants.

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
Other floors are therefore invalid. The route model does not implement door
locks or actor collision avoidance.

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

## Prototype contestant autonomy (#31)

`contestant_runtime.gd` consumes the validated cast from `ScenarioLoader` (#30)
without changing its IDs or starting cells. It schedules decisions in authored
cast order on the #28 clock and follows #29 routes one cell per tick. In the
absence of a cue, actors alternate between resting in the parlor and reading
in the study. These activity spots and the decision cadence are placeholders,
not final needs, timing, or content.

A simulation-only startle input names a walkable cell and the actual witnesses,
not a goal or chosen reaction. Each witness considers their latest startle once
at the next decision point after their current route. Private placeholder motives favor
either investigating a nearby lead or avoiding the cue by taking refuge in the
other room. If the cue blocks the only path to refuge, the avoider waits for
that reaction instead of crossing it. From #5, circumstances and motives
determine the response, and the scheduler seed only breaks ties between equally
near investigation leads. After the reaction, ordinary activity resumes.

The runtime is exercised headlessly and is **not connected to the preview**.
There are no player commands or actor data in the preview, and `--show-navigation`
still draws the same static route, not a contestant's route. Any future live
display must use a source-mediated projection under ADR-0004, not the runtime
records inspected by the tests. The prototype adds no final psychology,
social simulation, device rules, or departures.

From the repository root:

```sh
godot --headless --path game --script res://tests/contestant_runtime.gd
```

Expect `PASS: authored contestant autonomy, seeded choices, legal movement, and preview isolation`.

## Private perception and memory (#32)

`perceive_event()` accepts a walkable event cell, a perceived cue category, and
the IDs of the contestants who actually witnessed it. The simulation or test
fixture supplies this list; being in the cast or visible to a producer camera
does not imply witnessing an event. An empty list changes nothing and an unknown
ID rejects the delivery. The original `present_disturbance()` remains the #31
shared fixture: it explicitly assumes all contestants perceived the same startle.

Each witness keeps a private bounded history of the cue, cell and simulation
tick. Fear, stress, belief in a haunting, and suspicion of deliberate staging
are distinct. A startle raises fear without assigning a cause; apparent anomalous
evidence and signs of staging support separate suspicions that can coexist.
Synthetic chronic exposure raises that witness's effective stress baseline and
makes the same startle more frightening. Synthetic relief removes that chronic
stress without erasing the acute fear. Appraisal is not an action order: routes and motives
still govern decisions, including opposite reactions at identical fear.

The integer values, history cap and immediate relief are implementation/test
placeholders, not final mechanics or balance. This slice does not model passive
recovery, residual stress, cue habituation, personality thresholds, sensory
range or communication delivery. There is no dialogue, producer intervention,
entity or departure behavior. There are no new public observations: the preview
still consumes only the detached static plan and optional example route.

```sh
godot --headless --path game --script res://tests/contestant_perception.gd
```

Expect `PASS: private witness memory, separate appraisals, autonomous decisions, and no preview leakage`.
