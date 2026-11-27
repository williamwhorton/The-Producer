extends Node3D

signal room_selected(room_id: StringName)

const NO_ROOM := &""
const SELECTION_COLOR := Color("#a8814f")
const STATIONARY_COLOR := Color("#dce8ee")
const MOVING_COLOR := Color("#ffe297")

var _floors: Dictionary[StringName, MeshInstance3D] = {}
var _contestant_markers: Dictionary[StringName, Node3D] = {}
var _selection_material := StandardMaterial3D.new()
var _selected := NO_ROOM
var _pending_click := false
var _click_position := Vector2.ZERO

@onready var _camera: Camera3D = $Camera3D
@onready var _initial_camera_size: float = _camera.size


func _ready() -> void:
	_camera.look_at(Vector3(0, 0.25, 0))
	_selection_material.albedo_color = SELECTION_COLOR


func show_plan(plan: Dictionary) -> void:
	var rim := Color("#252c3a")
	_box(Vector3(0, -0.31, 0), Vector3(8.35, 0.42, 5.35), rim)
	var room_colors := {&"parlor": Color("#697d77"), &"study": Color("#867268")}
	for room_id: StringName in plan.rooms:
		var bounds: Rect2i = plan.rooms[room_id]
		_box(_rect_center(bounds) + Vector3.DOWN * 0.1,
				Vector3(bounds.size.x, 0.20, bounds.size.y), room_colors[room_id], room_id)
	for edge: Array in plan.walls:
		var outward: Vector3i = edge[1] - edge[0]
		# The near walls and interior partition are cut down for floor visibility.
		var tall := outward.x < 0 or outward.z < 0
		var height := 1.6 if tall else 0.2
		var center := _cell_center(edge[0]).lerp(_cell_center(edge[1]), 0.5)
		var size := Vector3(1, height, 0.15) if outward.x == 0 else Vector3(0.15, height, 1)
		_box(center + Vector3.UP * height / 2, size, Color("#566176") if tall else rim)
	for edge: Array in plan.exits:
		_draw_exit(edge[0], edge[1])
	_furnish(plan.obstacles)
	if not plan.example_route.is_empty():
		_draw_route(plan.example_route)


func show_contestants(observed: Array[Dictionary]) -> void:
	var missing := _contestant_markers.keys()
	var cell_counts: Dictionary[Vector3i, int] = {}
	for entry: Dictionary in observed:
		var id: StringName = entry.contestant_id
		var cell: Vector3i = entry.location.cell
		var marker := _contestant_markers.get(id) as Node3D
		if marker == null:
			marker = _add_contestant_marker(id)
			_contestant_markers[id] = marker
		missing.erase(id)
		marker.position = _cell_center(cell)

		# Contestant routes can cross or share a cell. Stack the labels
		# without displacing the projected positions.
		var label: Label3D = marker.get_node("Identity")
		var rank: int = cell_counts.get(cell, 0)
		label.offset.y = rank * 53.0
		cell_counts[cell] = rank + 1
		label.modulate = MOVING_COLOR if entry.activity == &"moving" else STATIONARY_COLOR

	for id: StringName in missing:
		var marker: Node3D = _contestant_markers[id]
		$Contestants.remove_child(marker)
		marker.queue_free()
		_contestant_markers.erase(id)


func _add_contestant_marker(id: StringName) -> Node3D:
	var marker := Node3D.new()
	$Contestants.add_child(marker)
	_mesh_box(marker, Vector3(0, 0.25, 0), Vector3(0.26, 0.5, 0.26), STATIONARY_COLOR, true)
	var label := Label3D.new()
	label.name = "Identity"
	label.text = String(id)
	label.position.y = 0.73
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.font_size = 48
	label.pixel_size = 0.007
	# This label represents the composite camera feed, even behind a prop.
	label.no_depth_test = true
	marker.add_child(label)
	return marker


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and event.button_mask & MOUSE_BUTTON_MASK_RIGHT:
		var units_per_pixel := _camera.size / get_viewport().get_visible_rect().size.y
		var axes := _camera.transform.basis
		_camera.position += (axes.y * event.relative.y - axes.x * event.relative.x) * units_per_pixel
		get_viewport().set_input_as_handled()
	elif event is InputEventMouseButton and event.pressed:
		match event.button_index:
			MOUSE_BUTTON_LEFT:
				_click_position = event.position
				_pending_click = true
			MOUSE_BUTTON_WHEEL_UP, MOUSE_BUTTON_WHEEL_DOWN:
				var factor := 1.1 if event.button_index == MOUSE_BUTTON_WHEEL_UP else 1.0 / 1.1
				_camera.size = clampf(_camera.size / factor,
						_initial_camera_size / 1.8, _initial_camera_size / 0.55)
			_:
				return
		get_viewport().set_input_as_handled()


func _physics_process(_delta: float) -> void:
	if not _pending_click:
		return
	_pending_click = false
	var origin := _camera.project_ray_origin(_click_position)
	var direction := _camera.project_ray_normal(_click_position)
	var ray := PhysicsRayQueryParameters3D.create(origin, origin + direction * _camera.far)
	var hit := get_world_3d().direct_space_state.intersect_ray(ray)
	var room_id: StringName = NO_ROOM
	if not hit.is_empty():
		room_id = hit.collider.get_meta(&"room_id", NO_ROOM)
	_select_room(room_id)


func _select_room(room_id: StringName) -> void:
	if room_id == _selected:
		return
	if _floors.has(_selected):
		_floors[_selected].material_override = null
	_selected = room_id
	if _floors.has(_selected):
		_floors[_selected].material_override = _selection_material
	room_selected.emit(_selected)


func _furnish(obstacles: Dictionary) -> void:
	var oak := Color("#795c46")
	var pine := Color("#bb9670")
	var velvet := Color("#68374a")

	var sofa := _rect_center(obstacles.sofa)
	_box(sofa + Vector3(0, 0.24, 0), Vector3(2.25, 0.48, 0.73), velvet)
	_box(sofa + Vector3(0, 0.50, -0.26), Vector3(2.25, 0.55, 0.17), velvet)
	var table := _rect_center(obstacles.table)
	_box(table + Vector3(0, 0.18, 0), Vector3(0.74, 0.36, 0.31), oak)
	_box(table + Vector3(0, 0.39, 0), Vector3(1.28, 0.11, 0.64), pine)

	var shelf := _rect_center(obstacles.bookshelf)
	_box(shelf + Vector3(0, 0.55, -0.24), Vector3(1.88, 1.10, 0.28), oak)
	_box(shelf + Vector3(0, 1.12, -0.18), Vector3(1.98, 0.12, 0.43), pine)
	for i in range(6):
		var cloth := velvet if i % 2 == 0 else Color("#b58952")
		_box(shelf + Vector3(-0.62 + 0.22 * i, 0.76, -0.04), Vector3(0.17, 0.37, 0.16), cloth)
	var desk := _rect_center(obstacles.desk)
	_box(desk + Vector3(0, 0.31, 0), Vector3(1.31, 0.62, 0.61), oak)
	_box(desk + Vector3(0, 0.66, 0), Vector3(1.55, 0.12, 0.83), pine)


func _draw_exit(inside: Vector3i, outside: Vector3i) -> void:
	var center := _cell_center(inside).lerp(_cell_center(outside), 0.5)
	var size := Vector3(0.9, 0.04, 0.24) if inside.x == outside.x else Vector3(0.24, 0.04, 0.9)
	_mesh_box(self, center, size, Color("#d4a563"))
	var signpost := Label3D.new()
	signpost.text = "EXIT"
	signpost.font_size = 25
	signpost.pixel_size = 0.009
	signpost.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	signpost.modulate = Color("#f7cc8f")
	signpost.position = center + Vector3(outside - inside) * 0.48 + Vector3.UP * 0.12
	add_child(signpost)


func _draw_route(cells: Array[Vector3i]) -> void:
	var overlay := Node3D.new()
	overlay.name = "NavigationPreview"
	add_child(overlay)
	var color := Color("#77e8ec")
	for index in cells.size():
		var center := _cell_center(cells[index]) + Vector3.UP * 0.025
		_mesh_box(overlay, center, Vector3(0.23, 0.02, 0.23), color, true)
		if index > 0:
			var previous := _cell_center(cells[index - 1]) + Vector3.UP * 0.025
			var size := (center - previous).abs() + Vector3(0.08, 0.01, 0.08)
			_mesh_box(overlay, center.lerp(previous, 0.5), size, color, true)


func _cell_center(cell: Vector3i) -> Vector3:
	return Vector3(cell.x + 0.5, 0, cell.z)


func _rect_center(bounds: Rect2i) -> Vector3:
	var center := Vector2(bounds.position) + Vector2(bounds.size) / 2
	return Vector3(center.x, 0, center.y - 0.5)


func _box(center: Vector3, size: Vector3, color: Color, room_id := NO_ROOM) -> void:
	# The pick collider matches the mesh, so walls and furniture block floor picks.
	var body := StaticBody3D.new()
	body.position = center
	add_child(body)

	var shape := BoxShape3D.new()
	shape.size = size
	var collider := CollisionShape3D.new()
	collider.shape = shape
	body.add_child(collider)

	var visual := _mesh_box(body, Vector3.ZERO, size, color)
	if room_id != NO_ROOM:
		body.set_meta(&"room_id", room_id)
		_floors[room_id] = visual


func _mesh_box(
	parent: Node3D, center: Vector3, size: Vector3, color: Color, unshaded := false
) -> MeshInstance3D:
	var mesh := BoxMesh.new()
	mesh.size = size
	var material := StandardMaterial3D.new()
	material.albedo_color = color
	if unshaded:
		material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mesh.material = material
	var visual := MeshInstance3D.new()
	visual.mesh = mesh
	visual.position = center
	if unshaded:
		visual.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	parent.add_child(visual)
	return visual
