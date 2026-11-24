extends SceneTree

const Layout = preload("res://simulation/house_layout.gd")
const PARLOR_DOOR := Vector3i(-1, 0, 0)
const STUDY_DOOR := Vector3i(0, 0, 0)
const START := Vector3i(-3, 0, 2)
const THRESHOLD := Vector3i(2, 0, 2)
const EXTERIOR := Vector3i(2, 0, 3)

var _failures := 0


func _initialize() -> void:
	_test_plan()
	_test_routes()
	if _failures == 0:
		print("PASS: house cells, doorway constraints, shortest routes, and exit threshold")
	quit(0 if _failures == 0 else 1)


func _test_plan() -> void:
	var rows := ["###..###", "###..###", "........", "........", "........"]
	for row in range(-2, 3):
		for column in range(-4, 4):
			var cell := Vector3i(column, 0, row)
			var room_id := &"parlor" if column < 0 else &"study"
			_check(Layout.room_at(cell) == room_id, "expected room at %s" % cell)
			var walkable: bool = rows[row + 2][column + 4] == "."
			_check(Layout.is_walkable(cell) == walkable, "expected occupancy at %s" % cell)
		var west := Vector3i(-1, 0, row)
		var east := Vector3i(0, 0, row)
		_check(Layout.can_step(west, east) == (row == 0), "east partition at row %d" % row)
		_check(Layout.can_step(east, west) == (row == 0), "west partition at row %d" % row)
	_check(not Layout.can_step(START, START + Vector3i(1, 0, -1)), "no diagonal shortcuts")
	_check(not Layout.can_step(START, START + Vector3i(2, 0, 0)), "no skipped cells")
	_check(not Layout.can_step(THRESHOLD, EXTERIOR), "exit is not outdoor traversal")
	_check(not Layout.can_step(START, START + Vector3i.UP), "no approved floor connection")


func _test_routes() -> void:
	var route := Layout.route_to_exit(START, &"front")
	_check(route.size() == 10, "shortest exit route uses nine steps with the partition in place")
	_check(not route.is_empty() and route.front() == START and route.back() == THRESHOLD,
			"route stops inside the exit")
	var door_index := route.find(PARLOR_DOOR)
	_check(door_index >= 0 and route.find(STUDY_DOOR) == door_index + 1, "route crosses the doorway")
	for index in range(1, route.size()):
		_check(Layout.can_step(route[index - 1], route[index]), "exit route uses valid steps")

	var reversed := Layout.find_route(THRESHOLD, START)
	_check(reversed.size() == 10, "reverse route is reachable")
	var reverse_door_index := reversed.find(STUDY_DOOR)
	_check(reverse_door_index >= 0 and reversed.find(PARLOR_DOOR) == reverse_door_index + 1,
			"doorway can be crossed in reverse")
	_check(Layout.route_to_exit(START, &"front", [PARLOR_DOOR]).is_empty(),
			"open endpoints can be unreachable when the sole doorway landing is obstructed")
	_check(Layout.route_to_exit(START, &"front", [THRESHOLD]).is_empty(), "blocked exit threshold")
	_check(Layout.route_to_exit(START, &"missing").is_empty(), "unknown exit")
	_check(Layout.find_route(START, EXTERIOR).is_empty(), "out-of-bounds goal")
	_check(Layout.find_route(START, START + Vector3i.UP).is_empty(), "unsupported floor goal")
	_check(Layout.find_route(START, Vector3i(2, 0, -1)).is_empty(), "furniture-blocked goal")
	_check(Layout.find_route(Vector3i(-3, 0, -2), START).is_empty(), "furniture-blocked start")
	_check(Layout.find_route(START, START) == [START], "valid zero-step route")

	var detour_start := Vector3i(-4, 0, 0)
	var detour_goal := Vector3i(-2, 0, 0)
	var obstruction := Vector3i(-3, 0, 0)
	var detour := Layout.find_route(detour_start, detour_goal, [obstruction])
	_check(detour.size() == 5 and detour.front() == detour_start and detour.back() == detour_goal,
			"search finds a four-step detour instead of failing at the first obstruction")
	_check(obstruction not in detour, "detour avoids the obstructed cell")
	for index in range(1, detour.size()):
		_check(Layout.can_step(detour[index - 1], detour[index]), "detour uses valid steps")


func _check(passed: bool, description: String) -> void:
	if not passed:
		_failures += 1
		push_error("FAIL: " + description)
