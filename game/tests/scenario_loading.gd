extends SceneTree

const Loader = preload("res://simulation/scenario_loader.gd")
const Preview = preload("res://observation/house_preview.gd")

var _failures := 0


func _initialize() -> void:
	_test_authored_scenarios()
	_test_rejections()
	if _failures == 0:
		print("PASS: authored and modified scenarios, reference and location validation")
	quit(0 if _failures == 0 else 1)


func _test_authored_scenarios() -> void:
	var original := Loader.load_file(Loader.DEFAULT_PATH)
	var modified := Loader.load_file("res://tests/fixtures/modified_scenario.json")
	for result in [original, modified]:
		_check(result.error.is_empty(), "expected a valid fixture: " + result.error)
	if not original.error.is_empty() or not modified.error.is_empty():
		return

	var first: Dictionary = original.scenario
	var second: Dictionary = modified.scenario
	_check(first.id == "prototype_preview" and second.id == "modified_test_only",
			"scenario identifiers come from the files")
	_check(first.house_id == "preview_house" and second.house_id == first.house_id,
			"both fixtures select the same house")
	_check(first.cast == {
		&"test_a": {"room_id": &"parlor", "start_cell": Vector3i(-3, 0, 2)},
		&"test_b": {"room_id": &"study", "start_cell": Vector3i(1, 0, 1)},
	}, "default cast and starts were loaded")
	_check(second.cast == {
		&"test_c": {"room_id": &"study", "start_cell": Vector3i(2, 0, 1)},
	}, "modified cast and start were loaded")
	_check(second.surveillance.camera_rooms == [&"study", &"parlor"],
			"authored surveillance values were retained")
	var start: Vector3i = second.parameters.navigation_example_start
	var exit_id: StringName = second.parameters.required_exit_id
	var plan := Preview.floor_plan(true, start, exit_id)
	_check(plan.example_route == [Vector3i(2, 0, 1), Vector3i(2, 0, 2)],
			"modified parameters change the preview projection without a new house")
	_check(not plan.has("cast") and not plan.has("surveillance") and not plan.has("parameters"),
			"the renderer gets the floor plan and example, not the scenario")


func _test_rejections() -> void:
	var text := FileAccess.get_file_as_string(Loader.DEFAULT_PATH)
	_expect_error(Loader.load_file("res://scenarios/missing.json"), "missing.json")
	_expect_error(Loader.parse("{broken"), "JSON line")
	_expect_error(Loader.parse("[]"), "expected a scenario object")
	_expect_error(Loader.parse(text.replace('"preview_house"', '"unbuilt"')), "unknown house 'unbuilt'")
	_expect_error(Loader.parse(text.replace('"front"', '"back"')), "unknown exit 'back'")
	_expect_error(Loader.parse(text.replace('"front"', '[]')), "parameters.required_exit_id")
	_expect_error(Loader.parse(text.replace('"test_b"', '"test_a"')), "duplicate cast identifier")
	_expect_error(Loader.parse(text.replace('"room_id": "study"', '"room_id": "attic"')),
			"cast[1] (test_b).room_id: unknown room 'attic'")
	for cell in ["[1, 0, -1]", "[1, 1, 1]", "[2, 0, 3]", "[-3, 0, 2]"]:
		_expect_error(Loader.parse(text.replace("[1, 0, 1]", cell)), "is not walkable in room 'study'")
	for cell in ["[1.5, 0, 1]", "[4294967297, 0, 1]", "[1, 0]"]:
		_expect_error(Loader.parse(text.replace("[1, 0, 1]", cell)), "expected three integers")
	_expect_error(Loader.parse(text.replace('["parlor", "study"]', '["parlor", "attic"]')),
			"surveillance.camera_rooms: unknown room 'attic'")
	_expect_error(Loader.parse(text.replace('["parlor", "study"]', '["parlor", "parlor"]')),
			"surveillance.camera_rooms: duplicate room 'parlor'")
	_expect_error(Loader.parse(text.replace('["parlor", "study"]', '["parlor"]')),
			"surveillance.camera_rooms: missing coverage for room 'study'")
	_expect_error(Loader.parse(text.replace('"navigation_example_start": [-3, 0, 2]',
			'"navigation_example_start": [2, 0, 3]')), "expected a walkable cell with a route")


func _expect_error(result: Dictionary, reason: String) -> void:
	_check(result.scenario.is_empty() and reason in result.error,
			"expected rejection mentioning '%s', got '%s'" % [reason, result.error])


func _check(passed: bool, description: String) -> void:
	if not passed:
		_failures += 1
		push_error("FAIL: " + description)
