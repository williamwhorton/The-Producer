extends Node2D

const HALF_TILE := Vector2(40, 20)
const GROUND_ORIGIN := Vector2(0, -196)
const GRID_SIZE := 10
const GROUND_ROOMS := [Rect2i(1, 1, 4, 8), Rect2i(5, 1, 4, 4), Rect2i(5, 5, 4, 4)]
const UPPER_ROOM: Rect2i = GROUND_ROOMS[1]
const UPPER_ROOM_INDEX := 3
const UPPER_ELEVATION := 96.0
const SLAB_DEPTH := Vector2(0, 11)
const STAIR_CELL := Vector2i(6, 3)
const DOOR_AB := Vector4i(5, 3, 5, 4)
const DOOR_BC := Vector4i(7, 5, 8, 5)
const CONTESTANT_1 := Vector2(2.5, 2.5)
const CONTESTANT_2 := Vector2(6.5, 2.5)
const SUPERNATURAL := Vector2(7.5, 7.5)
const DEMO_ROUTE := [Vector2(3.5, 3.5), Vector2(4.5, 3.5), Vector2(5.5, 3.5)]
const DEMO_STEP_SECONDS := 0.85
const ROOM_NAMES := ["A", "B", "C", "U"]
const ROOM_COLORS := [Color("#788862"), Color("#4b7d8a"), Color("#966653"), Color("#816d98")]
const ROOM_LABEL_CELLS := [Vector2(2.5, 5.5), Vector2(7.5, 3.5), Vector2(6.5, 6.5), Vector2(7.5, 2.5)]
const WALL_HEIGHT := 44.0
const CUT_HEIGHT := 7.0
const INK := Color("#152024")
const CONTESTANT_1_COLOR := Color("#fde099")
const CONTESTANT_2_COLOR := Color("#a9eadf")
const SUPERNATURAL_COLOR := Color("#e3b8fc")

var ground_walls: Array[Vector4i] = []
var upper_walls: Array[Vector4i] = []
var upper_visible := false
var cutaway := true
var selected_room := -1
var demo_marker := CONTESTANT_1
var demo_tween: Tween
var demo_status := "Ready"

@onready var camera: Camera2D = $Camera2D
@onready var status_label: Label = $HUD/Status


func _ready() -> void:
	add_perimeter(ground_walls, Rect2i(0, 0, GRID_SIZE, GRID_SIZE))
	add_wall_run(ground_walls, Vector2i(5, 1), Vector2i(5, 9), DOOR_AB)
	add_wall_run(ground_walls, Vector2i(5, 5), Vector2i(9, 5), DOOR_BC)
	add_perimeter(upper_walls, UPPER_ROOM)
	update_status()


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and event.button_mask & MOUSE_BUTTON_MASK_RIGHT:
		camera.position -= event.relative / camera.zoom
	elif event is InputEventMouseButton and event.pressed:
		match event.button_index:
			MOUSE_BUTTON_LEFT:
				var mouse_position: Vector2 = event.position
				var local_point := get_global_transform_with_canvas().affine_inverse() * mouse_position
				selected_room = pick_room(local_point)
			MOUSE_BUTTON_WHEEL_UP, MOUSE_BUTTON_WHEEL_DOWN:
				var factor := 1.1 if event.button_index == MOUSE_BUTTON_WHEEL_UP else 1.0 / 1.1
				camera.zoom = Vector2.ONE * clampf(camera.zoom.x * factor, 0.55, 1.8)
			_:
				return
	elif event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_F:
				upper_visible = not upper_visible
				if not upper_visible and selected_room == UPPER_ROOM_INDEX:
					selected_room = -1
			KEY_C:
				cutaway = not cutaway
			KEY_SPACE:
				play_demo()
			_:
				return
	else:
		return
	queue_redraw()
	update_status()


func update_status() -> void:
	status_label.text = "Floors: %s     |     Walls: %s     |     Room: %s     |     Debug route: %s" % [
		"Ground + upper" if upper_visible else "Ground",
		"Cutaway" if cutaway else "Full",
		ROOM_NAMES[selected_room] if selected_room >= 0 else "None",
		demo_status,
	]


func play_demo() -> void:
	if demo_tween and demo_tween.is_valid():
		demo_tween.kill()
	set_demo_marker(DEMO_ROUTE[0])
	demo_status = "Running"
	update_status()
	demo_tween = create_tween()
	for i in range(1, DEMO_ROUTE.size()):
		demo_tween.tween_method(set_demo_marker, DEMO_ROUTE[i - 1], DEMO_ROUTE[i], DEMO_STEP_SECONDS)
	demo_tween.finished.connect(func() -> void:
		demo_status = "Done"
		update_status()
	)


func set_demo_marker(point: Vector2) -> void:
	demo_marker = point
	queue_redraw()


func add_perimeter(walls: Array[Vector4i], bounds: Rect2i) -> void:
	var top := bounds.position
	var bottom := bounds.end
	var right := Vector2i(bottom.x, top.y)
	var left := Vector2i(top.x, bottom.y)
	add_wall_run(walls, top, right)
	add_wall_run(walls, top, left)
	add_wall_run(walls, right, bottom)
	add_wall_run(walls, left, bottom)


func add_wall_run(
	walls: Array[Vector4i], from: Vector2i, to: Vector2i, door := Vector4i.ZERO
) -> void:
	var step := (to - from).sign()
	var start := from
	while start != to:
		var end := start + step
		var edge := Vector4i(start.x, start.y, end.x, end.y)
		if edge != door:
			walls.append(edge)
		start = end


# Continuous grid coordinates are corners; add (0.5, 0.5) for cell centers.
func project_cell(point: Vector2, elevation := 0.0) -> Vector2:
	return GROUND_ORIGIN + Vector2(
		(point.x - point.y) * HALF_TILE.x,
		(point.x + point.y) * HALF_TILE.y - elevation
	)


func _draw() -> void:
	for y in GRID_SIZE:
		for x in GRID_SIZE:
			var cell := Vector2i(x, y)
			var room := ground_room_at(cell)
			var color: Color = ROOM_COLORS[room] if room >= 0 else Color("#37444c")
			draw_floor_cell(cell, 0.0, color)
	for room in GROUND_ROOMS.size():
		draw_room_label(room, 0.0)
	if selected_room >= 0 and selected_room < GROUND_ROOMS.size():
		draw_selection(GROUND_ROOMS[selected_room], 0.0)
	draw_threshold(DOOR_AB)
	draw_threshold(DOOR_BC)

	# Merge wall faces and markers by baseline depth so a wall can actually occlude a marker.
	var layers: Array[Dictionary] = []
	for edge in ground_walls:
		layers.append({"depth": (edge.x + edge.y + edge.z + edge.w) * 0.5,
			"paint": draw_wall.bind(edge, 0.0, Vector2i.ZERO)})
	for marker in [[demo_marker, "1", CONTESTANT_1_COLOR],
			[CONTESTANT_2, "2", CONTESTANT_2_COLOR], [SUPERNATURAL, "S", SUPERNATURAL_COLOR]]:
		var foot: Vector2 = marker[0]
		layers.append({"depth": foot.x + foot.y, "paint": draw_marker.bind(foot, marker[1], marker[2])})
	layers.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return a.depth < b.depth)
	for layer in layers:
		layer.paint.call()

	if upper_visible:
		draw_upper_floor()


func ground_room_at(cell: Vector2i) -> int:
	for room in GROUND_ROOMS.size():
		if GROUND_ROOMS[room].has_point(cell):
			return room
	return -1


func pick_room(point: Vector2) -> int:
	# Test the opaque upper layer first; do not select through walls or slab sides.
	if upper_visible:
		for edge in upper_walls:
			if Geometry2D.is_point_in_polygon(point, wall_face(edge, UPPER_ELEVATION, UPPER_ROOM.position)):
				return -1
		var slab := floor_outline(Rect2(UPPER_ROOM), UPPER_ELEVATION)
		if Geometry2D.is_point_in_polygon(point, slab):
			return UPPER_ROOM_INDEX
		for i in [1, 2]:
			if Geometry2D.is_point_in_polygon(point, slab_side(slab[i], slab[i + 1])):
				return -1
	for edge in ground_walls:
		if Geometry2D.is_point_in_polygon(point, wall_face(edge, 0.0, Vector2i.ZERO)):
			return -1
	var axes := (point - GROUND_ORIGIN) / HALF_TILE
	var grid_point := Vector2((axes.y + axes.x) * 0.5, (axes.y - axes.x) * 0.5)
	return ground_room_at(Vector2i(grid_point.floor()))


func floor_outline(bounds: Rect2, elevation: float) -> PackedVector2Array:
	return PackedVector2Array([
		project_cell(bounds.position, elevation),
		project_cell(Vector2(bounds.end.x, bounds.position.y), elevation),
		project_cell(bounds.end, elevation),
		project_cell(Vector2(bounds.position.x, bounds.end.y), elevation),
	])


func draw_floor_cell(cell: Vector2i, elevation: float, color: Color) -> void:
	var outline := floor_outline(Rect2(Vector2(cell), Vector2.ONE), elevation)
	draw_colored_polygon(outline, color.darkened(0.07) if (cell.x + cell.y) % 2 else color)
	outline.append(outline[0])
	draw_polyline(outline, Color(0.05, 0.10, 0.12, 0.34), 1.0, true)


func draw_room_label(room: int, elevation: float) -> void:
	var center := project_cell(ROOM_LABEL_CELLS[room], elevation)
	draw_centered_text(center + Vector2(0, 7), ROOM_NAMES[room], 20, Color("#f4f1e5"))


func draw_selection(bounds: Rect2i, elevation: float) -> void:
	# Inset the outline so low wall faces do not cover it entirely.
	var outline := floor_outline(Rect2(bounds).grow(-0.22), elevation)
	outline.append(outline[0])
	draw_polyline(outline, Color("#ffe1a2"), 2.5, true)


func draw_threshold(edge: Vector4i) -> void:
	var a := project_cell(Vector2(edge.x, edge.y))
	var b := project_cell(Vector2(edge.z, edge.w))
	draw_line(a, b, INK, 7, true)
	draw_line(a.lerp(b, 0.08), a.lerp(b, 0.92), Color("#f6c578"), 3, true)


func wall_face(edge: Vector4i, elevation: float, back_corner: Vector2i) -> PackedVector2Array:
	var a := project_cell(Vector2(edge.x, edge.y), elevation)
	var b := project_cell(Vector2(edge.z, edge.w), elevation)
	var back := (edge.x == edge.z and edge.x == back_corner.x) \
		or (edge.y == edge.w and edge.y == back_corner.y)
	var rise := Vector2(0, CUT_HEIGHT if cutaway and not back else WALL_HEIGHT)
	return PackedVector2Array([a, b, b - rise, a - rise])


func draw_wall(edge: Vector4i, elevation: float, back_corner: Vector2i) -> void:
	var face := wall_face(edge, elevation, back_corner)
	var color := Color("#4b5d66") if edge.x == edge.z else Color("#5d6d76")
	draw_colored_polygon(face, color)
	draw_line(face[0], face[1], INK, 1.0, true)
	draw_line(face[3], face[2], color.lightened(0.23), 2.0, true)


func draw_upper_floor() -> void:
	var slab := floor_outline(Rect2(UPPER_ROOM), UPPER_ELEVATION)
	for i in [1, 2]:
		draw_colored_polygon(slab_side(slab[i], slab[i + 1]), Color("#443952"))
	for y in range(UPPER_ROOM.position.y, UPPER_ROOM.end.y):
		for x in range(UPPER_ROOM.position.x, UPPER_ROOM.end.x):
			draw_floor_cell(Vector2i(x, y), UPPER_ELEVATION, ROOM_COLORS[UPPER_ROOM_INDEX])
	draw_room_label(UPPER_ROOM_INDEX, UPPER_ELEVATION)
	draw_stair()
	if selected_room == UPPER_ROOM_INDEX:
		draw_selection(UPPER_ROOM, UPPER_ELEVATION)
	# Perimeter order is the two far edges, then the two near edges.
	for edge in upper_walls:
		draw_wall(edge, UPPER_ELEVATION, UPPER_ROOM.position)


func slab_side(a: Vector2, b: Vector2) -> PackedVector2Array:
	return PackedVector2Array([a, b, b + SLAB_DEPTH, a + SLAB_DEPTH])


func draw_stair() -> void:
	var origin := Vector2(STAIR_CELL)
	var outline := floor_outline(Rect2(origin + Vector2(0.16, 0.16), Vector2(0.68, 0.68)),
		UPPER_ELEVATION)
	draw_colored_polygon(outline, INK)
	for i in 4:
		var x := 0.27 + 0.15 * i
		draw_line(project_cell(origin + Vector2(x, 0.25), UPPER_ELEVATION),
			project_cell(origin + Vector2(x, 0.75), UPPER_ELEVATION), Color("#e8d7fa"), 2.0, true)


func draw_marker(point: Vector2, label: String, color: Color) -> void:
	var foot := project_cell(point)
	var badge := foot + Vector2(0, -16)
	draw_circle(foot, 4, INK, true, -1.0, true)
	draw_line(foot, badge, INK, 3, true)
	draw_circle(badge, 13, INK, true, -1.0, true)
	draw_circle(badge, 11, color, true, -1.0, true)
	draw_centered_text(badge + Vector2(0, 5), label, 14, INK)


func draw_centered_text(baseline: Vector2, text: String, size: int, color: Color) -> void:
	var font := ThemeDB.fallback_font
	var width := font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
	draw_string(font, baseline - Vector2(width / 2, 0), text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, color)
