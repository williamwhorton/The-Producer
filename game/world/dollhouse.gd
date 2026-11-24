extends Node3D

signal room_selected(room_id: StringName)

const NO_ROOM := &""
const SELECTION_COLOR := Color("#a8814f")

var _floors: Dictionary[StringName, MeshInstance3D] = {}
var _selection_material := StandardMaterial3D.new()
var _selected := NO_ROOM
var _pending_click := false
var _click_position := Vector2.ZERO

@onready var _camera: Camera3D = $Camera3D


func _ready() -> void:
	_camera.look_at(Vector3(0, 0.25, 0))
	_selection_material.albedo_color = SELECTION_COLOR
	_build_preview()


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
		_click_position = event.position
		_pending_click = true
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


func _build_preview() -> void:
	var rim := Color("#252c3a")
	var plaster := Color("#566176")
	var oak := Color("#795c46")
	var pine := Color("#bb9670")
	var velvet := Color("#68374a")
	_box(Vector3(0, -0.31, 0), Vector3(8.35, 0.42, 5.35), rim)
	_box(Vector3(-2, -0.10, 0), Vector3(4, 0.20, 5), Color("#697d77"), &"parlor")
	_box(Vector3(2, -0.10, 0), Vector3(4, 0.20, 5), Color("#867268"), &"study")

	# The near walls and center partition are cut down to expose both rooms.
	_box(Vector3(0, 0.80, -2.50), Vector3(8.15, 1.60, 0.15), plaster)
	_box(Vector3(-4, 0.80, 0), Vector3(0.15, 1.60, 5), plaster)
	_box(Vector3(4, 0.10, 0), Vector3(0.15, 0.20, 5), rim)
	_box(Vector3(0, 0.10, 2.50), Vector3(8.15, 0.20, 0.15), rim)
	_box(Vector3(0, 0.10, -1.55), Vector3(0.13, 0.20, 1.90), rim)
	_box(Vector3(0, 0.10, 1.55), Vector3(0.13, 0.20, 1.90), rim)

	# Parlor: sofa and low table.
	_box(Vector3(-2.48, 0.24, -1.72), Vector3(2.25, 0.48, 0.73), velvet)
	_box(Vector3(-2.48, 0.50, -2.01), Vector3(2.25, 0.55, 0.17), velvet)
	_box(Vector3(-2.57, 0.18, -0.67), Vector3(0.74, 0.36, 0.31), oak)
	_box(Vector3(-2.57, 0.39, -0.67), Vector3(1.28, 0.11, 0.64), pine)

	# Study: bookshelf with upright books and a desk.
	_box(Vector3(2.72, 0.55, -2.24), Vector3(1.88, 1.10, 0.28), oak)
	_box(Vector3(2.72, 1.12, -2.18), Vector3(1.98, 0.12, 0.43), pine)
	for i in range(6):
		var cloth := velvet if i % 2 == 0 else Color("#b58952")
		_box(Vector3(2.10 + 0.22 * i, 0.76, -2.04), Vector3(0.17, 0.37, 0.16), cloth)
	_box(Vector3(2.27, 0.31, -1.03), Vector3(1.31, 0.62, 0.61), oak)
	_box(Vector3(2.27, 0.66, -1.03), Vector3(1.55, 0.12, 0.83), pine)


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

	var mesh := BoxMesh.new()
	mesh.size = size
	var material := StandardMaterial3D.new()
	material.albedo_color = color
	mesh.material = material
	var visual := MeshInstance3D.new()
	visual.mesh = mesh
	body.add_child(visual)

	if room_id != NO_ROOM:
		body.set_meta(&"room_id", room_id)
		_floors[room_id] = visual
