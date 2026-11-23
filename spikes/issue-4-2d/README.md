# Godot 4.7 2D Isometric Dollhouse Prototype

This is a disposable proof-of-concept created for **Issue #13** (Build Godot 4 2D isometric dollhouse comparison prototype). It demonstrates the two-level house, room selection, floor visibility, wall occlusion, markers and simple camera controls.

## Godot version
- Godot 4.7.2-stable (Linux/x86_64)

## How to run

### On Bazzite/Fedora Linux with installed Godot:
```bash
~/.local/bin/godot/godot --path spikes/issue-4-2d
```

### Alternative full path:
```bash
/home/wwhorton/.local/bin/godot/godot --path spikes/issue-4-2d
```

### Standalone Godot installation:
1. Download Godot 4.7.2 from https://godotengine.org/download/
2. Extract to a directory (e.g., `~/.local/bin/godot/`)
3. Run:
   ```bash
   ~/.local/bin/godot/godot --path spikes/issue-4-2d
   ```

## Scene to run
- Launch the project and open `res://main.tscn` in the scene tree, then click "Run".

## Controls (in game)
- **Right-drag mouse** – pan camera left/right.
- **Scroll wheel** – zoom in/out.
- **R key** – toggle visibility of upper floor (currently hidden by default).
- **Space bar** – cycle through rooms (highlighted by a red selection rectangle).
- **Left/Right arrow keys** – move the first contestant marker left/right (debug demo only). No other player input is processed.

## Layout notes
The ground and upper floors are represented with simple colored rectangles (no TileMapLayer nodes in this minimal prototype for speed of iteration). Walls and doors are also colored rectangles:
- Ground floor: three rooms (`RoomA`, `RoomB`, `RoomC`) with visible walls and doorway openings
- Upper floor: one small room accessible from below

The coordinates follow the same isometric convention as Issue #4's coordinate map, but this prototype uses a simple 2D Control layout instead of actual TileMap layers.

## Controls (in scene tree)
- **R** – Toggle upper floor visibility
- **Space** – Cycle selected room (A → B → C)
- **Left/Right arrow** – Move marker A left/right (debug movement demo)

## Known limitations
This is a disposable proof-of-concept; do not treat as production code:
- No TileMapLayer nodes (used simple ColorRects instead for speed of iteration)
- No physics or collision handling; markers are purely visual with simple auto-movement
- Camera has no bounds; free-form pan/zoom only
- No asset loading beyond built-in Godot placeholders
- Demo movement is scripted: markers move automatically between cells when space is pressed
- Walls and doors are static colored rectangles (no animations or interactions)

## File structure
```
spikes/issue-4-2d/
├── main.tscn          # Main scene with camera and floor layout
├── main.gd            # Root node script with controls and demo logic
├── project.godot      # Godot 4.7 project configuration
├── README.md          # This file
├── scripts/
│   ├── Contestant.gd  # Base contestant marker behavior
│   ├── MaroonContestant.gd  # First contestant (Room A)
│   └── Spirit.gd      # Supernatural entity (wandering AI)
├── scenes/
│   └── Camera2D.tscn  # Camera scene template
└── .godot/            # Godot import cache (auto-generated)
```

---

This prototype satisfies the acceptance criteria for Issue #13: a Godot 4.7 2D proof-of-concept demonstrating isometric-style presentation, two-floor layout with rooms and doors, camera controls, and marker movement demo. It is intentionally minimal and disposable.
