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

	await _click(camera.unproject_position(Vector3(-1.60, 0, 0.85)))
	_check(room.text == "Parlor", "parlor floor is selectable")
	await _click(camera.unproject_position(Vector3(2.40, 0, 0.85)))
	_check(room.text == "Study", "study floor is selectable")
	await _click(camera.unproject_position(Vector3(2.27, 0.72, -1.03)))
	_check(room.text == "No room selected", "desk blocks a floor pick and clears selection")
	await _click(camera.unproject_position(Vector3(-1.60, 0, 0.85)))
	_check(room.text == "Parlor", "parlor can be reselected")
	await _click(Vector2(10, 10))
	_check(room.text == "No room selected", "background clears selection")

	world.room_selected.emit(&"not_in_floor_plan")
	_check(room.text == "No room selected", "unknown room ID does not yield a label")

	if _failures == 0:
		print("PASS: configured main scene, orthographic camera, room picking, and HUD")
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


func _check(passed: bool, description: String) -> void:
	if not passed:
		_failures += 1
		push_error("FAIL: " + description)
