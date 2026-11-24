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

1. The window opens to **The Producer / HOUSE PREVIEW**, with a furnished
   parlor and study visible together from a fixed elevated angle. The footer
   reads **No room selected**.
2. Left-click the exposed greenish floor in the parlor by the sofa. Only that
   floor turns gold and the footer reads **Parlor**.
3. Left-click the exposed tan floor in the study by the desk. Only the study
   floor turns gold and the footer reads **Study**.
4. Click the top of the desk. The floor returns to its original color and the
   footer reads **No room selected**. Select either floor again, then click
   the dark background outside the house to clear the selection again.

`res://main.tscn` is the configured entry point. No prior editor import,
asset downloads, plugins, or runtime services are needed.

## Boundaries

| Path | Responsibility in this slice |
| --- | --- |
| `main.tscn`, `main.gd` | Compose the world view and HUD. Map the renderer's selected room ID through the application boundary and pass only its display name to the HUD. |
| `observation/` | Public information from the static, producer-known floor plan. The lookup returns a display name or no label; it neither receives private state nor grants access to additional information. Future live evidence must follow [ADR-0004](../docs/decisions/ADR-0004-producer-observation-boundary.md). |
| `world/` | Preview geometry, camera, lighting, cutaway, picking and floor highlight. The adapter emits a room ID, not a collider or 3D position. |
| `ui/` | Title, room label and controls hint; no world or domain script dependency. |
| `simulation/` | [Private seeded scheduler and clock](simulation/README.md) (#28). The static house preview does not run a contest simulation. |
| `persistence/` | Reserved for save/load and campaign state. No save API, format or storage is chosen or used. |

The preview uses local Godot scenes/scripts only: a headless boot path (T-01
foundation, not a deterministic simulation), separated modules (T-03), no
runtime network or paid API dependency (T-04), and a 3D dollhouse view (G-03).
No gameplay, actor movement, camera controls, or multi-floor behavior is added.

## Smoke checks

From the repository root on Bazzite, with the pinned native `godot` above on
`PATH`, run the same check as [GitHub Actions](../.github/workflows/godot-headless.yml):

```sh
bash game/tests/headless.sh
```

CI verifies the official Linux x86_64 archive checksum before running this
script on Ubuntu 24.04. The script checks the full engine version, keeps Godot's
output visible, and fails on a nonzero exit, a 60-second command timeout, or a
Godot error in the logs. It runs these commands in order:

```sh
godot --headless --path game --editor --import
godot --headless --path game --quit-after 2
godot --headless --path game --script res://tests/smoke.gd
godot --headless --path game --script res://tests/scheduler.gd
```

The first two commands should exit successfully without script/scene errors.
The smoke test loads the configured main scene and checks the active orthographic
camera, initial HUD, both floor picks, desk occlusion, background clearing and
unknown room IDs. Expect exit 0 and
`PASS: configured main scene, orthographic camera, room picking, and HUD`.
The scheduler test runs separately from the scene; expect exit 0 and
`PASS: seeded scheduler ordering, tactical pause, live triggers, and speed invariance`.
The disposable `spikes/` are not used as substitutes. Headless checks do not
verify rendered output.
To repeat the automated checks with graphics enabled, run
`godot --path game --script res://tests/smoke.gd`.

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
