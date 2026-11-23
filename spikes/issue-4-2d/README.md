# Godot 4: 2D isometric dollhouse

Disposable presentation proof for [#13](https://github.com/williamwhorton/The-Producer/issues/13)
and the [#4 engine comparison](https://github.com/williamwhorton/The-Producer/issues/4).
This does not select a production engine (P-01) or implement contestant logic.

## Launch on Bazzite/Linux

Verified with **Godot `4.7.2.stable.official.ed1daf0bf`**, Linux x86-64, Compatibility renderer.
From the repository root, with `godot` on `PATH`:

```sh
godot --path spikes/issue-4-2d
```

If Godot is installed at `~/.local/bin/godot/godot`, substitute that path for `godot`.
The configured main scene is `res://main.tscn`. No editor import or asset download is
required before the GUI launch.

## Controls and manual walkthrough

1. At launch, look for olive A, teal B, and terracotta C on the 10×10 grid;
   markers **1**, **2**, and **S** should be visible. Click each room's floor
   to outline it. Click outside the rooms or on a wall to clear selection.
2. Press **C** to raise the walls. Check both gold thresholds: each should sit in
   a gap, not in a wall. Press **C** again to lower the near walls and partitions
   to short stubs, exposing the floor behind them. The two far exterior walls stay up.
3. Press **F** to show the purple upper room and the striped stair symbol.
   Click inside the purple floor to select U. Press **F** again: B and contestant
   2 are uncovered, and the U selection clears.
4. With the upper floor hidden, press **Space**. Marker 1 jumps to the debug
   start in A, moves through the A–B opening, and stops in B. The HUD changes
   from `Running` to `Done`. Press Space again to replay.
5. **Right-drag** to pan in either axis and **scroll** to zoom in or out around
   the camera center. Click a visible floor again to check room selection still aligns.

## Fixture

Cells use zero-based `(x,y)` coordinates; the gray rim is part of the 10×10
ground footprint. The outer walls enclose the rim. Wall runs occupy *edges*,
not cells. Gold threshold strips mark openings without closing them.

| Element | #4 coordinates |
| --- | --- |
| A (west) | `x=1..4, y=1..8` |
| B (northeast) | `x=5..8, y=1..4` |
| C (southeast) | `x=5..8, y=5..8` |
| A–B partition | Between columns 4 and 5, rows `1..8`; opening at row `3` |
| B–C partition | Between rows 4 and 5, columns `5..8`; opening at column `7` |
| U (directly over B) | `x=5..8, y=1..4`; stair symbol at `(6,3)` |
| Ground markers 1, 2, S | `(2,2)`, `(6,2)`, `(7,7)` respectively |
| Debug marker 1 route | `(3,3)` → `(4,3)` → `(5,3)`, crossing the A–B opening |

## 2D approach and limits

One `Node2D` draws primitive shapes from continuous grid coordinates. The game-style
2:1 isometric projection maps the ground axes to opposite diagonals and elevation
to a vertical screen offset. Custom drawing instead of `TileMapLayer` makes
edge-based walls, gaps, and the raised slab possible without a tileset. Floor
polygons and wall faces also drive picking, so opaque surfaces block clicks.

Ground wall and marker ordering uses projected baseline depth; the upper slab
and its walls draw on top of the ground layer. Cutaway is a fixed toggle, not
automatic clipping or a 3D depth test. The stairs are symbolic; there is no
collision, pathfinding, stair traversal, direct movement input, supernatural
behavior, or private contestant state. The demo follows a fixed tween, not
autonomous navigation. There are no external runtime assets, LLM calls, C#,
TCP/IPC, or database. No performance or native GPU comparison was made.

## Observed verification

```sh
godot --headless --path spikes/issue-4-2d --editor --import
godot --headless --path spikes/issue-4-2d --quit-after 2
godot --headless --path spikes/issue-4-2d --script res://tests/check_fixture.gd
```

- Import and bounded headless main-scene launch exited 0 with no script errors.
  The fixture test reported `PASS: #4 fixture, projection, room picking, and scripted A-to-B route`.
  It checks all room cells, all wall segments and both openings, stairs and
  marker coordinates, picking with occlusion, and the route through the doorway.
- The documented GUI command opened a real 1060×640 X11 window under Xvfb using
  Mesa llvmpipe. X11 input and inspected screenshots verified the three ground
  markers, A/B/C/U selection, upper-floor reveal and hide, full walls and cutaway,
  movement into B, pan, zoom in/out, and selection after a camera change.
  No script/runtime errors; the virtual display driver reported that it could
  not change V-Sync mode. Native compositor/GPU behavior was not tested.
- Screenshots: [ground](evidence/ground.png), [full walls and A selected](evidence/full-walls.png),
  [upper room and stairs](evidence/upper.png), [route in progress](evidence/route-mid.png),
  [route complete](evidence/route-end.png), [panned/zoomed with C selected](evidence/camera.png).
  These are test evidence, excluded from Godot import.

Independent, read-only review of the diff and Creative Director visual acceptance
are still required. The walkthrough above is also the manual reproduction procedure.
