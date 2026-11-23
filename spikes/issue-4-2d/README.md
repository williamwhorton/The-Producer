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

## Figure 1: Ground Floor Layout (ASCII Diagram)

```
   Iso View (Top-Left Corner)
   ┌─────────────────────────────┐
   │      Upper Floor (hidden by default)      │
   │     ╔═════════════════╗          R key toggles
   │     ║                 ║        visibility
   │     ║  UPER ROOM      ║
   │     ║                 ║
   │     ╚════════════════╣│
   │                     ║ │┌─┐ ┌─┐ Doorway
   │                   ────║ ├┤ ├─── Connected Cell
   │                     ║ │└─┘    (Room A)
   │                     ║ │       ┌─┐
   │        ╔═══════════╣│╬│      │A│ Doorway
   │        ║           ║│╬│──────┤B│ Connected Cell
   │        ║  GROUND   ║│╬│       └─┘
   │        ║     FLOOR ║│╬│   ┌─┐ Room C
   │        ║           ║│╬│   └─┘
   │        ╚═══════════╣│╬│       ┌─┐ Doorway
   │                    ║ │      ───┤C│ Connected Cell
   │                    ║ │
   │                  Doorway
   └─────────────────────┘
```

**Legend:**
- `═══════════` = Wall (vertical line segments in isometric view)
- `╬` = Doorway opening between connected cells
- `┌─┐ └─┘` = Room boundaries
- `A`, `B`, `C` = Room labels (highlighted by red selection rect via Space bar)

The prototype uses Control nodes with ColorRects to represent walls, doors, and floor areas. Coordinates follow Godot's isometric convention as shown in the diagram above.

## Controls (in scene tree)
- **R** – Toggle upper floor visibility
- **Space** – Cycle selected room (A → B → C)
- **Left/Right arrow** – Move PlayerMarker left/right (debug movement demo between Room A and B cells)

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
├── main.tscn              # Main scene with camera and floor layout (SupernaturalMarker removed)
├── main.gd                # Root node script with controls and demo logic
├── project.godot          # Godot 4.7 project configuration
├── README.md              # This documentation file
├── scripts/
│   ├── Contestant.gd      # Base PlayerMarker behavior (renamed from ContestantMarker)
│   ├── MaroonContestant.gd  # First contestant marker behavior (renamed from MaroonContestantMarker)
│   └── Spirit.gd          # DELETED - supernatural entity not included in Issue #13 scope
├── scenes/
│   └── Camera2D.tscn      # Camera scene template
└── .godot/                # Godot import cache (auto-generated)
```

---

This prototype satisfies the acceptance criteria for Issue #13: a Godot 4.7 2D proof-of-concept demonstrating isometric-style presentation, two-floor layout with rooms and doors, camera controls, and marker movement demo. It is intentionally minimal and disposable.
