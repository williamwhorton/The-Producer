extends SceneTree

const Main = preload("res://main.gd")
const Runtime = preload("res://simulation/contestant_runtime.gd")
const World = preload("res://world/dollhouse.gd")
const Loader = preload("res://simulation/scenario_loader.gd")

var _failures := 0


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	if change_scene_to_file(ProjectSettings.get_setting("application/run/main_scene")) != OK:
		push_error("Cannot load the configured main scene")
		quit(1)
		return
	await scene_changed

	var main: Main = current_scene
	main.set_process(false)
	var world: World = main.get_node("Dollhouse")
	var markers: Node3D = world.get_node("Contestants")
	var pause_button: Button = main.get_node("HouseHUD/TimeControls/Pause")
	var speed_button: OptionButton = main.get_node("HouseHUD/TimeControls/Speed")
	var scenario: Dictionary = Loader.load_file(Loader.DEFAULT_PATH).scenario
	var step := Main.TICK_USEC / 1_000_000.0

	_check(main._runtime.camera_snapshot().contestants.size() == scenario.cast.size()
			and scenario.cast.size() >= 2, "the authored cast is initially visible")
	_check_frame(world, main._runtime.camera_snapshot())
	var initial_a: Vector3 = world._contestant_markers[&"test_a"].position
	_check(speed_button.get_item_text(0) == "Normal" and speed_button.get_item_text(1) == "Fast"
			and speed_button.get_item_text(2) == "Very Fast", "the HUD offers all approved speeds")

	# Send a real HUD click, then drive the same process callback with exact
	# elapsed values so engine frame timing cannot affect the checks.
	await process_frame
	_click(pause_button)
	main._process(step * 8)
	_check(main._clock.current_tick() == 0 and pause_button.text == "Resume",
			"the HUD pauses the scheduler, even with a large elapsed time")
	_check_frame(world, main._runtime.camera_snapshot())
	_click(pause_button)
	main._process(step)
	_check(main._clock.current_tick() == 1 and pause_button.text == "Pause",
			"the HUD resumes at normal speed without catching up paused time")
	_check(world._contestant_markers[&"test_a"].position == initial_a,
			"choosing a private activity is not visible as moving")
	_check_frame(world, main._runtime.camera_snapshot())

	speed_button.get_popup().index_pressed.emit(1)
	main._process(step)
	_check(main._clock.current_tick() == 3 and world._contestant_markers[&"test_a"].position != initial_a,
			"Fast advances two ticks and the normal scene refreshes the marker")
	_check_frame(world, main._runtime.camera_snapshot())
	speed_button.get_popup().index_pressed.emit(2)
	main._process(step)
	_check(main._clock.current_tick() == 7, "Very Fast advances four ticks")
	_check_frame(world, main._runtime.camera_snapshot())

	# Privileged fixture: cause an existing autonomous departure through
	# perception, without adding a player command or modifying the shipped cast.
	var camera_before := main._runtime.camera_snapshot()
	var cue_cell: Vector3i = scenario.cast[&"test_a"].start_cell
	main._runtime._actors[&"test_a"].stay_motivation = 1
	main._runtime.perceive_event(cue_cell, Runtime.Cue.STAGING_EVIDENCE, [&"test_a"])
	main._runtime.perceive_event(cue_cell, Runtime.Cue.CHRONIC_PRESSURE, [&"test_a"])
	main._runtime.perceive_event(cue_cell, Runtime.Cue.STARTLE, [&"test_a"])
	_check(main._runtime.camera_snapshot() == camera_before,
			"private cue, appraisal and pressure produce no immediate visual disclosure")
	_check_frame(world, camera_before)
	speed_button.get_popup().index_pressed.emit(0)
	for i in range(24):
		main._process(step)
		_check_frame(world, main._runtime.camera_snapshot())
		if not world._contestant_markers.has(&"test_a"):
			break
	_check(markers.get_child_count() == 1 and world._contestant_markers.has(&"test_b")
			and main._runtime._departed.has(&"test_a"),
			"the scene removes the marker immediately when camera coverage ends on departure")

	if _failures == 0:
		print("PASS: live dollhouse positions and activity, time controls, and observation isolation")
	quit(0 if _failures == 0 else 1)


func _check_frame(world: World, frame: Dictionary) -> void:
	_check(world.get_node("Contestants").get_child_count() == frame.contestants.size(),
			"only currently projected contestants have scene markers")
	for entry: Dictionary in frame.contestants:
		var marker: Node3D = world._contestant_markers.get(entry.contestant_id)
		var cell: Vector3i = entry.location.cell
		_check(marker != null and marker.position == Vector3(cell.x + 0.5, 0, cell.z),
				"marker follows the projected cell")
		if marker != null:
			var label: Label3D = marker.get_node("Identity")
			_check(label.text == String(entry.contestant_id), "marker text contains only the projected ID")
			var color := World.MOVING_COLOR if entry.activity == &"moving" else World.STATIONARY_COLOR
			_check(label.modulate == color, "movement feedback reflects projected activity")


func _click(button: Button) -> void:
	var event := InputEventMouseButton.new()
	event.button_index = MOUSE_BUTTON_LEFT
	event.position = button.get_global_rect().get_center()
	event.pressed = true
	root.push_input(event, true)
	event = event.duplicate()
	event.pressed = false
	root.push_input(event, true)


func _check(passed: bool, description: String) -> void:
	if not passed:
		_failures += 1
		push_error("FAIL: " + description)
