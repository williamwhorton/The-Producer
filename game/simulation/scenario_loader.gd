extends RefCounted
## Load the local authored scenario against the existing single-house layout.

const HouseLayout = preload("res://simulation/house_layout.gd")
const DEFAULT_PATH := "res://scenarios/house_preview.json"


static func load_file(path: String) -> Dictionary:
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		return _failure("%s: %s" % [path, error_string(FileAccess.get_open_error())])
	var result := parse(file.get_as_text())
	if not result.error.is_empty():
		result.error = "%s: %s" % [path, result.error]
	return result


static func parse(text: String) -> Dictionary:
	var json := JSON.new()
	if json.parse(text) != OK:
		return _failure("JSON line %d: %s" % [json.get_error_line(), json.get_error_message()])
	if not json.data is Dictionary:
		return _failure("expected a scenario object")
	var data: Dictionary = json.data
	var id: Variant = data.get("id")
	if not _is_id(id):
		return _failure("id: expected a non-empty scenario identifier")
	var house_id: Variant = data.get("house_id")
	if not house_id is String or house_id != HouseLayout.ID:
		return _failure("house_id: unknown house '%s' (expected '%s')" % [house_id, HouseLayout.ID])

	var parameters: Variant = data.get("parameters")
	if not parameters is Dictionary:
		return _failure("parameters: expected an object")
	var exit_id: Variant = parameters.get("required_exit_id")
	if not exit_id is String or not HouseLayout.EXITS.has(StringName(exit_id)):
		return _failure("parameters.required_exit_id: unknown exit '%s'" % [exit_id])
	var example: Variant = _read_cell(parameters.get("navigation_example_start"))
	if example == null or HouseLayout.route_to_exit(example, StringName(exit_id)).is_empty():
		return _failure("parameters.navigation_example_start: expected a walkable cell with a route to exit '%s'" % exit_id)

	var cast_rows: Variant = data.get("cast")
	if not cast_rows is Array or cast_rows.is_empty():
		return _failure("cast: expected a non-empty array")
	var cast: Dictionary[StringName, Dictionary] = {}
	for i in cast_rows.size():
		var member: Variant = cast_rows[i]
		var field := "cast[%d]" % i
		if not member is Dictionary or not _is_id(member.get("id")):
			return _failure("%s.id: expected a non-empty cast identifier" % field)
		var member_id := StringName(member.id)
		field += " (%s)" % member_id
		if cast.has(member_id):
			return _failure("%s.id: duplicate cast identifier" % field)
		var room: Variant = member.get("room_id")
		if not room is String or not HouseLayout.ROOMS.has(StringName(room)):
			return _failure("%s.room_id: unknown room '%s'" % [field, room])
		var cell: Variant = _read_cell(member.get("start_cell"))
		if cell == null:
			return _failure("%s.start_cell: expected three integers [column, floor, row]" % field)
		if not HouseLayout.is_walkable(cell) or HouseLayout.room_at(cell) != StringName(room):
			return _failure("%s.start_cell: %s is not walkable in room '%s'" % [field, cell, room])
		if HouseLayout.route_to_exit(cell, StringName(exit_id)).is_empty():
			return _failure("%s.start_cell: %s cannot reach exit '%s'" % [field, cell, exit_id])
		cast[member_id] = {"room_id": StringName(room), "start_cell": cell}

	var surveillance: Variant = data.get("surveillance")
	if not surveillance is Dictionary or not surveillance.get("camera_rooms") is Array:
		return _failure("surveillance.camera_rooms: expected an array of room identifiers")
	var camera_rooms: Array[StringName] = []
	for room: Variant in surveillance.camera_rooms:
		if not room is String or not HouseLayout.ROOMS.has(StringName(room)):
			return _failure("surveillance.camera_rooms: unknown room '%s'" % [room])
		if StringName(room) in camera_rooms:
			return _failure("surveillance.camera_rooms: duplicate room '%s'" % room)
		camera_rooms.append(StringName(room))
	for room: StringName in HouseLayout.ROOMS:
		if room not in camera_rooms:
			return _failure("surveillance.camera_rooms: missing coverage for room '%s'" % room)

	return {"error": "", "scenario": {
		"id": id,
		"house_id": house_id,
		"cast": cast,
		"surveillance": {"camera_rooms": camera_rooms},
		"parameters": {"required_exit_id": StringName(exit_id), "navigation_example_start": example},
	}}


static func _read_cell(value: Variant) -> Variant:
	if not value is Array or value.size() != 3:
		return null
	# Godot's JSON parser returns floats; reject fractions and int32 overflow before converting.
	for component: Variant in value:
		if not component is float or component != floorf(component) \
				or component < -2147483648.0 or component > 2147483647.0:
			return null
	return Vector3i(int(value[0]), int(value[1]), int(value[2]))


static func _is_id(value: Variant) -> bool:
	return value is String and not value.is_empty() and value == value.strip_edges()


static func _failure(message: String) -> Dictionary:
	return {"error": message, "scenario": {}}
