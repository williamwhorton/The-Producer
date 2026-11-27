# The Producer — production project

[#27](https://github.com/williamwhorton/The-Producer/issues/27) starts the
production Godot project. [ADR-0002](../docs/decisions/ADR-0002-engine-and-presentation-approach.md)
provisionally selects Godot 4, GDScript and a fixed-angle 3D orthographic view.
The [approved prototype-first roadmap](../docs/roadmap.md) defers MVP scope
(#20). The projects under `spikes/` are experiments, not dependencies or
production content. This two-room preview is not a canonical house layout.

## Launch and inspect

Use the pinned **Godot `4.7.2.stable.official.ed1daf0bf`** executable on Bazzite
Linux. From the repository root, with `godot` on `PATH`:

```sh
godot --version
godot --path game
```

1. The window opens to **The Producer / HOUSE PREVIEW / LIVE CAMERAS**, with a furnished
   parlor and study visible together from a fixed elevated angle. Look for
   the gap in the dividing wall and the marked **EXIT** in the near study wall.
   The footer reads **No room selected**.
2. Watch `test_a` and `test_b` move autonomously. Their markers show the latest
   camera-projected cells; a gold name shows movement on that tick. A contestant
   absent from the latest camera snapshot has no marker.
3. Click **Pause** to freeze the latest camera view. **Resume** continues from
   that point without catching up on paused wall time. Choose **Normal**,
   **Fast**, or **Very Fast** to change clock speed. The preview uses a
   provisional 0.5-second normal tick and 2×/4× faster rates.
4. Left-click the exposed greenish floor in the parlor by the sofa. Only that
   floor turns gold and the footer reads **Parlor**.
5. Left-click the exposed tan floor in the study by the desk. Only the study
   floor turns gold and the footer reads **Study**.
6. Click the top of the desk. The floor returns to its original color and the
   footer reads **No room selected**. Select either floor again, then click
   the dark background outside the house to clear the selection again.
7. Right-drag to pan and scroll to zoom. Navigation and room picking also
   work while the simulation is paused.

`res://main.tscn` is the configured entry point. No prior editor import,
asset downloads, plugins, or runtime services are needed.

### Static navigation preview (#29)

```sh
godot --path game -- --show-navigation
```

Follow the cyan line from near the front of the parlor. It turns through the
only opening in the dividing wall, avoids the furnishings, and ends inside
the marked study exit. Click the line just inside the study: the study floor
and HUD selection work as usual. The ordinary launch shows both openings
without the line. This is a fixed route example, not an actor's intent or a
player movement control. See the [authored layout](simulation/README.md#house-layout-and-routing-29).

### Authored scenario (#30)

The preview loads [`scenarios/house_preview.json`](scenarios/house_preview.json)
on startup. It references the existing `preview_house` topology by ID and
defines placeholder cast IDs and starting cells, camera coverage for both rooms,
and the exit and origin of the static route example. Cells are
`[column, floor, row]`; only floor `0` exists. A start must be inside the named
room, clear of furniture, and able to reach the named exit's interior threshold.
Every room must appear once in `surveillance.camera_rooms`. A failed load
reports the file and the offending field (or JSON line) and exits nonzero.

These are authored scenario inputs, not a save format. The preview starts the
existing deterministic runtime with this cast and camera coverage. The
[modified test fixture](tests/fixtures/modified_scenario.json) uses the same
house with a different cast and a route example that starts in the study; it
is not used at startup or offered as another playable property.

## Boundaries

| Path | Responsibility in this slice |
| --- | --- |
| `main.tscn`, `main.gd` | Load the authored scenario, drive the simulation clock, and send the known floor plan and latest camera observations to the world view. Route HUD time controls to the clock and room selection to the HUD. |
| `observation/` | Project the producer-known floor plan and, separately, the runtime's [authorized live evidence](simulation/README.md#live-producer-observations-39) under ADR-0004/0005. |
| `world/` | Preview geometry, observed contestant markers, camera, lighting, cutaway, picking and floor highlight. The adapter emits a room ID, not a collider or 3D position. |
| `ui/` | Title, room label, controls hint, pause and speed controls; no world or domain script dependency. |
| `scenarios/` | Local authored scenario input; no gameplay scene or saved state. |
| `simulation/` | Scenario validation and [private seeded scheduler, authored house topology, routing, and contestant runtime](simulation/README.md). |
| `persistence/` | Reserved for save/load and campaign state. No save API, format or storage is chosen or used. |

The preview uses local Godot scenes/scripts only. It runs the authored cast's
ordinary movement without player interventions. Marker removal is exercised by
the headless live-dollhouse test with a controlled
[voluntary departure fixture](simulation/README.md#voluntary-departure-34).

## Smoke checks

From the repository root on Bazzite, with the pinned native `godot` above on
`PATH`, run the same check as [GitHub Actions](../.github/workflows/godot-headless.yml):

```sh
bash game/tests/headless.sh
```

CI verifies the official Linux x86_64 archive checksum before running this
script on Ubuntu 24.04. The script checks the full engine version, keeps Godot's
output visible, and fails on a nonzero exit, a 60-second command timeout, or a
Godot error in the logs. It includes these scene and foundation checks:

```sh
godot --headless --path game --editor --import
godot --headless --path game --quit-after 2
godot --headless --path game --script res://tests/smoke.gd
godot --headless --path game --script res://tests/smoke.gd -- --show-navigation
godot --headless --path game --script res://tests/scheduler.gd
godot --headless --path game --script res://tests/house_navigation.gd
godot --headless --path game --script res://tests/scenario_loading.gd
godot --headless --path game --script res://tests/live_dollhouse.gd
```

The first two commands should exit successfully without script/scene errors.
The smoke test loads the configured main scene and checks the active orthographic
camera, pan/zoom, room picking, desk occlusion, background clearing, both openings and their
adjacent wall segments, and the opt-in route. Expect exit 0 and
`PASS: configured main scene, room picking, pan/zoom, doorway, exit, and route overlay`.
The scheduler test runs separately from the scene; expect exit 0 and
`PASS: seeded scheduler ordering, tactical pause, live triggers, and speed invariance`.
The scene-free navigation test expects exit 0 and
`PASS: house cells, doorway constraints, shortest routes, and exit threshold`.
The scenario test loads both JSON files, checks that the modified parameters
change the static route, and rejects invalid references and locations. Expect
exit 0 and `PASS: authored and modified scenarios, reference and location validation`.
The live-dollhouse test checks projected position and movement feedback, clock
controls, private-state isolation and removal of a departed contestant's marker.
Expect exit 0 and `PASS: live dollhouse positions and activity, time controls, and observation isolation`.
The disposable `spikes/` are not used as substitutes. Headless checks do not
verify rendered output.
To repeat the scene smoke test with graphics enabled and the route visible, run
`godot --path game --script res://tests/smoke.gd -- --show-navigation`.

## Recorded evidence for the #27 preview

- On Bazzite `45.20261117.1` (Kinoite), using the pinned executable above,
  editor import and headless launch completed without script/scene errors.
  The smoke test printed `PASS` both headlessly and with graphics enabled.
- `godot --path game --quit-after 120` launched the configured scene on the
  X11 display at 1040×640, using the Compatibility renderer on an NVIDIA
  GeForce RTX 3080 Ti (OpenGL 3.3, NVIDIA 620.70.06).
- Inspected in-window captures of the initial preview, each room selected,
  and the selection cleared after a desk click. The captures showed both
  rooms and their furnishings, a gold highlight only on the selected floor
  with the matching HUD label, and original floor colors after clearing.
  Input was injected into the real window's Godot viewport; physical mouse
  verification and Creative Director acceptance remain separate.
