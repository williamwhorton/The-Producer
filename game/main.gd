extends Node

const HousePreview = preload("res://observation/house_preview.gd")
const ScenarioLoader = preload("res://simulation/scenario_loader.gd")
const Scheduler = preload("res://simulation/event_scheduler.gd")
const ContestantRuntime = preload("res://simulation/contestant_runtime.gd")
const ObservationProjector = preload("res://observation/observation_projector.gd")

# Provisional preview timing, independent of the simulation rules.
const TICK_USEC := 500_000
const FAST_RATE := 2
const VERY_FAST_RATE := 4
const PREVIEW_SEED := 21

var _clock: Scheduler
var _runtime: ContestantRuntime


func _ready() -> void:
	var result := ScenarioLoader.load_file(ScenarioLoader.DEFAULT_PATH)
	if not result.error.is_empty():
		push_error("Cannot launch house preview: " + result.error)
		set_process(false)
		get_tree().quit(1)
		return

	var parameters: Dictionary = result.scenario.parameters
	var projector := ObservationProjector.new(result.scenario.surveillance.camera_rooms, [])
	_clock = Scheduler.new(PREVIEW_SEED, TICK_USEC, FAST_RATE, VERY_FAST_RATE)
	_runtime = ContestantRuntime.new(result.scenario.cast, _clock, {}, {}, {},
			parameters.required_exit_id, {}, projector)

	var show_navigation := "--show-navigation" in OS.get_cmdline_user_args()
	$Dollhouse.show_plan(HousePreview.floor_plan(
			show_navigation, parameters.navigation_example_start, parameters.required_exit_id))
	$Dollhouse.room_selected.connect(_show_room)
	$HouseHUD.pause_changed.connect(_clock.set_paused)
	$HouseHUD.speed_changed.connect(_set_speed)
	_show_room(&"")
	_show_camera_snapshot()


func _process(delta: float) -> void:
	var previous_tick := _clock.current_tick()
	_clock.advance(roundi(delta * 1_000_000.0))
	if _clock.current_tick() != previous_tick:
		_show_camera_snapshot()


func _set_speed(index: int) -> void:
	_clock.set_speed(Scheduler.Speed.values()[index])


func _show_camera_snapshot() -> void:
	$Dollhouse.show_contestants(_runtime.camera_snapshot().contestants)


func _show_room(room_id: StringName) -> void:
	$HouseHUD.show_room(HousePreview.room_name(room_id))
