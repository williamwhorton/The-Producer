extends SceneTree

var _failures := 0


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var main_scene: String = ProjectSettings.get_setting("application/run/main_scene")
	if change_scene_to_file(main_scene) != OK:
		push_error("Cannot load configured main scene: %s" % main_scene)
		quit(1)
		return
	await scene_changed

	var camera: Camera3D = root.get_camera_3d()
	var room: Label = current_scene.get_node("HouseHUD/Footer/Room")
	var world := current_scene.get_node("Dollhouse")
	_check(camera.projection == Camera3D.PROJECTION_ORTHOGONAL, "orthographic camera is active")
	_check(room.text == "No room selected", "HUD starts with no selection")
	var overlay := world.get_node_or_null("NavigationPreview")
	var route_requested := "--show-navigation" in OS.get_cmdline_user_args()
	_check((overlay != null) == route_requested, "static route is opt-in")
	if overlay != null:
		_check(overlay.get_child_count() == 19, "ten route cells and nine connecting segments")

	await _click(camera.unproject_position(Vector3(-1.60, 0, 0.85)))
	_check(room.text == "Parlor", "parlor floor is selectable")
	await _click(camera.unproject_position(Vector3(0.50, 0, 0)))
	_check(room.text == "Study", "study floor is selectable through the route overlay")
	await _click(camera.unproject_position(Vector3(2.50, 0.72, -1)))
	_check(room.text == "No room selected", "desk blocks a floor pick and clears selection")
	await _click(camera.unproject_position(Vector3(-1.60, 0, 0.85)))
	_check(room.text == "Parlor", "parlor can be reselected")
	await _click(Vector2(10, 10))
	_check(room.text == "No room selected", "background clears selection")

	world.room_selected.emit(&"not_in_floor_plan")
	_check(room.text == "No room selected", "unknown room ID does not yield a label")

	var space := camera.get_world_3d().direct_space_state
	_check(not _hits_wall(space, Vector3(-0.4, 0.1, 0), Vector3(0.4, 0.1, 0)),
			"interior doorway is an opening")
	_check(_hits_wall(space, Vector3(-0.4, 0.1, 1), Vector3(0.4, 0.1, 1)),
			"the partition still blocks the adjacent crossing")
	_check(not _hits_wall(space, Vector3(2.5, 0.1, 2.3), Vector3(2.5, 0.1, 2.8)),
			"front exit is an opening")
	_check(_hits_wall(space, Vector3(1.5, 0.1, 2.3), Vector3(1.5, 0.1, 2.8)),
			"front wall still blocks the adjacent crossing")

	if _failures == 0:
		print("PASS: configured main scene, room picking, doorway, exit, and route overlay")
	quit(0 if _failures == 0 else 1)


func _click(position: Vector2) -> void:
	var event := InputEventMouseButton.new()
	event.button_index = MOUSE_BUTTON_LEFT
	event.pressed = true
	event.position = position
	root.push_input(event, true)
	# physics_frame is emitted before Node._physics_process().
	await physics_frame
	await physics_frame


func _hits_wall(space: PhysicsDirectSpaceState3D, from: Vector3, to: Vector3) -> bool:
	return not space.intersect_ray(PhysicsRayQueryParameters3D.create(from, to)).is_empty()


func _check(passed: bool, description: String) -> void:
	if not passed:
		_failures += 1
		push_error("FAIL: " + description)
