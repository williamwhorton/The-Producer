extends Node3D

const GRID := Rect2i(0, 0, 10, 10)
const ROOMS := [Rect2i(1, 1, 4, 8), Rect2i(5, 1, 4, 4), Rect2i(5, 5, 4, 4)]
const UPPER_ROOM := 3
const ROOM_NAMES := ["A", "B", "C", "U"]
const ROOM_COLORS := [Color("#788862"), Color("#4b7d8a"), Color("#966653"), Color("#816d98")]
const ROOM_LABELS := [Vector2i(2, 5), Vector2i(7, 3), Vector2i(6, 5), Vector2i(7, 2)]
const DOOR_AB := Vector2i(5, 3)
const DOOR_BC := Vector2i(7, 5)
const STAIR := Vector2i(6, 3)
const MARKER_CELLS := [Vector2i(2, 2), Vector2i(6, 2), Vector2i(7, 7)]
const ROUTE := [Vector2i(3, 3), Vector2i(4, 3), Vector2i(5, 3)]
const STEP_SECONDS := 0.85
const WALL_HEIGHT := 1.45
const CUT_HEIGHT := 0.20
const SLAB_TOP := -0.035
const TILE_WIDTH := 0.97

# Fixture x/y map to Godot x/z. Godot y is elevation.
var walls: Array[MeshInstance3D] = []
var cut_walls: Array[MeshInstance3D] = []
var slabs: Array[MeshInstance3D] = []
var outlines: Array[Node3D] = []
var markers: Array[Node3D] = []
var selected_room := -1
var cutaway := true
var demo_status := "Ready"
var demo_tween: Tween
var materials: Dictionary = {}

@onready var camera: Camera3D = $Camera3D
@onready var initial_camera_size := camera.size
@onready var ground: Node3D = $Ground
@onready var upper: Node3D = $Upper
@onready var status_label: Label = $HUD/Status


func _ready() -> void:
	var target := Vector3(5, 0.85, 5)
	camera.position = target + Vector3(12, 9.8, 12)
	camera.look_at(target)
	build_floor(ground, GRID)
	build_floor(upper, ROOMS[1])
	add_perimeter(ground, GRID)
	add_perimeter(upper, ROOMS[1])
	add_wall_run(ground, Vector2i(5, 1), Vector2i(0, 1), 8, true, DOOR_AB)
	add_wall_run(ground, Vector2i(5, 5), Vector2i(1, 0), 4, true, DOOR_BC)
	box(ground, Vector3(5, 0.012, 3.5), Vector3(0.21, 0.024, 0.88), Color("#dfb66f")).name = "ThresholdAB"
	box(ground, Vector3(7.5, 0.012, 5), Vector3(0.88, 0.024, 0.21), Color("#dfb66f")).name = "ThresholdBC"
	build_stair()
	for room in ROOM_NAMES.size():
		var parent := upper if room == UPPER_ROOM else ground
		add_label(parent, ROOM_NAMES[room], cell_center(ROOM_LABELS[room], 0.27), 0.012)
		make_outline(parent, room_bounds(room))
	for i in MARKER_CELLS.size():
		add_marker(MARKER_CELLS[i], ["1", "2", "S"][i],
			[Color("#fde099"), Color("#a9eadf"), Color("#e3b8fc")][i])
	set_cutaway(true)


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and event.button_mask & MOUSE_BUTTON_MASK_RIGHT:
		var units_per_pixel := camera.size / get_viewport().get_visible_rect().size.y
		var axes := camera.global_transform.basis
		camera.position += (axes.y * event.relative.y - axes.x * event.relative.x) * units_per_pixel
	elif event is InputEventMouseButton and event.pressed:
		match event.button_index:
			MOUSE_BUTTON_LEFT:
				select_room(pick_room(camera.project_ray_origin(event.position),
					camera.project_ray_normal(event.position)))
			MOUSE_BUTTON_WHEEL_UP, MOUSE_BUTTON_WHEEL_DOWN:
				var factor := 1.1 if event.button_index == MOUSE_BUTTON_WHEEL_UP else 1.0 / 1.1
				camera.size = clampf(camera.size / factor,
					initial_camera_size / 1.8, initial_camera_size / 0.55)
	elif event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_F:
				set_upper_visible(not upper.visible)
			KEY_C:
				set_cutaway(not cutaway)
			KEY_SPACE:
				play_demo()


func set_cutaway(enabled: bool) -> void:
	cutaway = enabled
	var height := CUT_HEIGHT if enabled else WALL_HEIGHT
	for wall in cut_walls:
		var mesh := wall.mesh as BoxMesh
		mesh.size.y = height
		wall.position.y = height / 2.0
	update_status()


func set_upper_visible(enabled: bool) -> void:
	upper.visible = enabled
	if not enabled and selected_room == UPPER_ROOM:
		select_room(-1)
	update_status()


func select_room(room: int) -> void:
	if selected_room >= 0:
		outlines[selected_room].hide()
	selected_room = room
	if room >= 0:
		outlines[room].show()
	update_status()


func update_status() -> void:
	status_label.text = "Floors: %s     |     Walls: %s     |     Room: %s     |     Debug route: %s" % [
		"Ground + upper" if upper.visible else "Ground",
		"Cutaway" if cutaway else "Full",
		ROOM_NAMES[selected_room] if selected_room >= 0 else "None",
		demo_status,
	]


func play_demo() -> void:
	if demo_tween and demo_tween.is_valid():
		demo_tween.kill()
	markers[0].position = cell_center(ROUTE[0])
	demo_status = "Running"
	update_status()
	demo_tween = create_tween()
	for i in range(1, ROUTE.size()):
		demo_tween.tween_property(markers[0], "position", cell_center(ROUTE[i]), STEP_SECONDS)
	demo_tween.finished.connect(func() -> void:
		demo_status = "Done"
		update_status()
	)


func cell_center(cell: Vector2i, elevation := 0.0) -> Vector3:
	return Vector3(cell.x + 0.5, elevation, cell.y + 0.5)


func room_bounds(room: int) -> Rect2i:
	return ROOMS[1] if room == UPPER_ROOM else ROOMS[room]


func ground_room_at(cell: Vector2i) -> int:
	for room in ROOMS.size():
		if ROOMS[room].has_point(cell):
			return room
	return -1


func build_floor(parent: Node3D, bounds: Rect2i) -> void:
	var center := Vector2(bounds.position) + Vector2(bounds.size) / 2.0
	slabs.append(box(parent, Vector3(center.x, SLAB_TOP - 0.125, center.y),
		Vector3(bounds.size.x, 0.25, bounds.size.y), Color("#34434b")))
	for y in range(bounds.position.y, bounds.end.y):
		for x in range(bounds.position.x, bounds.end.x):
			var cell := Vector2i(x, y)
			var room := UPPER_ROOM if parent == upper else ground_room_at(cell)
			var color: Color = Color("#46535d") if room < 0 else ROOM_COLORS[room]
			box(parent, cell_center(cell, SLAB_TOP / 2.0),
				Vector3(TILE_WIDTH, -SLAB_TOP, TILE_WIDTH), color)


func add_perimeter(parent: Node3D, bounds: Rect2i) -> void:
	var along_x := Vector2i(1, 0)
	var along_y := Vector2i(0, 1)
	add_wall_run(parent, bounds.position, along_x, bounds.size.x, false)
	add_wall_run(parent, bounds.position, along_y, bounds.size.y, false)
	add_wall_run(parent, Vector2i(bounds.position.x, bounds.end.y), along_x, bounds.size.x, true)
	add_wall_run(parent, Vector2i(bounds.end.x, bounds.position.y), along_y, bounds.size.y, true)


func add_wall_run(parent: Node3D, start: Vector2i, axis: Vector2i, count: int,
		can_cut: bool, opening := Vector2i(-1, -1)) -> void:
	for i in count:
		var edge := start + i * axis
		if edge == opening:
			continue
		var center := Vector2(edge) + Vector2(axis) / 2.0
		var wall := box(parent, Vector3(center.x, WALL_HEIGHT / 2.0, center.y),
			Vector3(1.0 if axis.x else 0.12, WALL_HEIGHT, 1.0 if axis.y else 0.12),
			Color("#a1a19a") if parent == ground else Color("#ada0bc"))
		walls.append(wall)
		if can_cut:
			cut_walls.append(wall)


func make_outline(parent: Node3D, bounds: Rect2i) -> void:
	var outline := Node3D.new()
	parent.add_child(outline)
	outline.hide()
	outlines.append(outline)
	var center := Vector2(bounds.position) + Vector2(bounds.size) / 2.0
	var color := Color("#ffe7a8")
	for y in [bounds.position.y + 0.12, bounds.end.y - 0.12]:
		box(outline, Vector3(center.x, 0.03, y), Vector3(bounds.size.x - 0.16, 0.025, 0.08), color)
	for x in [bounds.position.x + 0.12, bounds.end.x - 0.12]:
		box(outline, Vector3(x, 0.03, center.y), Vector3(0.08, 0.025, bounds.size.y - 0.24), color)


func build_stair() -> void:
	var stair := Node3D.new()
	stair.name = "StairSymbol"
	upper.add_child(stair)
	stair.position = cell_center(STAIR)
	for i in 4:
		var height := 0.07 * (i + 1)
		box(stair, Vector3(0, height / 2.0, 0.30 - i * 0.20), Vector3(0.68, height, 0.18),
			Color("#f7dd9e") if i % 2 == 0 else Color("#ba976c"))


func add_marker(cell: Vector2i, text: String, color: Color) -> void:
	var marker := Node3D.new()
	ground.add_child(marker)
	marker.position = cell_center(cell)
	markers.append(marker)
	var peg := CylinderMesh.new()
	peg.top_radius = 0.22
	peg.bottom_radius = 0.29
	peg.height = 0.56
	peg.radial_segments = 12
	add_mesh(marker, peg, Vector3(0, 0.28, 0), color)
	add_label(marker, text, Vector3(0, 0.86, 0), 0.014)


func add_label(parent: Node3D, text: String, at: Vector3, pixel_size: float) -> void:
	var label := Label3D.new()
	label.text = text
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.pixel_size = pixel_size
	label.outline_size = 8
	parent.add_child(label)
	label.position = at


func box(parent: Node3D, at: Vector3, size: Vector3, color: Color) -> MeshInstance3D:
	var mesh := BoxMesh.new()
	mesh.size = size
	return add_mesh(parent, mesh, at, color)


func add_mesh(parent: Node3D, mesh: PrimitiveMesh, at: Vector3, color: Color) -> MeshInstance3D:
	if not materials.has(color):
		var material := StandardMaterial3D.new()
		material.albedo_color = color
		materials[color] = material
	var instance := MeshInstance3D.new()
	instance.mesh = mesh
	instance.material_override = materials[color]
	parent.add_child(instance)
	instance.position = at
	return instance


func pick_room(origin: Vector3, direction: Vector3) -> int:
	# Use visible geometry, so lowered or hidden walls don't leave click
	# blockers. Decorations and marker pegs are click-through.
	var closest := camera.far * camera.far
	var room := -1
	for slab in slabs:
		if not slab.is_visible_in_tree():
			continue
		var bounds: AABB = slab.global_transform * slab.get_aabb()
		var hit: Variant = bounds.intersects_ray(origin, direction)
		var floor_height := slab.get_parent_node_3d().global_position.y
		# Prefer the tile top where the ray actually lands on the inset face.
		# Between tiles, fall back to the slab; its sides still block clicks.
		if direction.y < 0.0:
			var face: Variant = Plane(Vector3.UP, floor_height).intersects_ray(origin, direction)
			if face != null:
				var point := Vector2(face.x, face.z)
				var footprint := Rect2(bounds.position.x, bounds.position.z, bounds.size.x, bounds.size.z)
				var offset := (point - point.floor() - Vector2(0.5, 0.5)).abs()
				if footprint.has_point(point) and maxf(offset.x, offset.y) <= TILE_WIDTH / 2.0:
					hit = face
		if hit == null or origin.distance_squared_to(hit) >= closest:
			continue
		closest = origin.distance_squared_to(hit)
		room = -1
		if is_equal_approx(hit.y, floor_height) or is_equal_approx(hit.y, bounds.end.y):
			room = UPPER_ROOM if slab.get_parent() == upper else ground_room_at(
				Vector2i(floori(hit.x), floori(hit.z)))
	for wall in walls:
		if wall.is_visible_in_tree():
			var hit: Variant = (wall.global_transform * wall.get_aabb()).intersects_ray(origin, direction)
			if hit != null and origin.distance_squared_to(hit) <= closest:
				return -1
	return room
