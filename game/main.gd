extends Node

const HousePreview = preload("res://observation/house_preview.gd")
const ScenarioLoader = preload("res://simulation/scenario_loader.gd")


func _ready() -> void:
	var result := ScenarioLoader.load_file(ScenarioLoader.DEFAULT_PATH)
	if not result.error.is_empty():
		push_error("Cannot launch house preview: " + result.error)
		get_tree().quit(1)
		return

	var parameters: Dictionary = result.scenario.parameters
	var show_navigation := "--show-navigation" in OS.get_cmdline_user_args()
	$Dollhouse.show_plan(HousePreview.floor_plan(
			show_navigation, parameters.navigation_example_start, parameters.required_exit_id))
	$Dollhouse.room_selected.connect(_show_room)
	_show_room(&"")


func _show_room(room_id: StringName) -> void:
	$HouseHUD.show_room(HousePreview.room_name(room_id))
