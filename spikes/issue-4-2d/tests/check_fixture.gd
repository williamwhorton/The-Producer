extends SceneTree

const House = preload("res://main.gd")
const MAIN = preload("res://main.tscn")

var failures: Array[String] = []


func _initialize() -> void:
	call_deferred("run")


func run() -> void:
	var house := MAIN.instantiate() as House
	root.add_child(house)
	check_geometry(house)
	check_picking(house)
	check_demo(house)
	if failures.is_empty():
		print("PASS: #4 fixture, projection, room picking, and scripted A-to-B route")
	else:
		for failure in failures:
			printerr("FAIL: ", failure)
	quit(0 if failures.is_empty() else 1)


func check_geometry(house: House) -> void:
	expect(House.GRID_SIZE == 10, "10x10 ground grid")
	for y in range(-1, 11):
		for x in range(-1, 11):
			var expected := -1
			if x in range(1, 9) and y in range(1, 9):
				expected = 0 if x <= 4 else (1 if y <= 4 else 2)
			expect(house.ground_room_at(Vector2i(x, y)) == expected, "room at (%d,%d)" % [x, y])
	expect(House.UPPER_ROOM == Rect2i(5, 1, 4, 4), "upper floor matches B")
	expect(House.STAIR_CELL == Vector2i(6, 3), "stair cell")
	expect(House.CONTESTANT_1 == Vector2(2.5, 2.5), "contestant 1 center")
	expect(House.CONTESTANT_2 == Vector2(6.5, 2.5), "contestant 2 center")
	expect(House.SUPERNATURAL == Vector2(7.5, 7.5), "supernatural center")
	expect(House.DOOR_AB == Vector4i(5, 3, 5, 4), "A-B opening edge")
	expect(House.DOOR_BC == Vector4i(7, 5, 8, 5), "B-C opening edge")

	var ground: Array[Vector4i] = []
	for i in 10:
		ground.append_array([
			Vector4i(i, 0, i + 1, 0), Vector4i(i, 10, i + 1, 10),
			Vector4i(0, i, 0, i + 1), Vector4i(10, i, 10, i + 1),
		])
	for y in range(1, 9):
		if y != 3:
			ground.append(Vector4i(5, y, 5, y + 1))
	for x in range(5, 9):
		if x != 7:
			ground.append(Vector4i(x, 5, x + 1, 5))
	var upper: Array[Vector4i] = []
	for i in 4:
		upper.append_array([
			Vector4i(5 + i, 1, 6 + i, 1), Vector4i(5 + i, 5, 6 + i, 5),
			Vector4i(5, 1 + i, 5, 2 + i), Vector4i(9, 1 + i, 9, 2 + i),
		])
	expect_edges(house.ground_walls, ground, "ground")
	expect_edges(house.upper_walls, upper, "upper")

	var origin := house.project_cell(Vector2.ZERO)
	var dx := house.project_cell(Vector2.RIGHT) - origin
	var dy := house.project_cell(Vector2.DOWN) - origin
	expect(dx.x > 0 and dx.y > 0 and dy == Vector2(-dx.x, dx.y), "symmetric diagonal axes")
	expect(house.project_cell(Vector2.ZERO, House.UPPER_ELEVATION).y < origin.y, "upper is elevated")


func check_picking(house: House) -> void:
	var overlap := house.project_cell(Vector2(5.5, 1.5))
	expect(house.pick_room(overlap) == 1, "B is selectable before showing upper floor")
	expect(house.pick_room(house.project_cell(Vector2(2.5, 5.5))) == 0, "A is selectable")
	expect(house.pick_room(house.project_cell(Vector2(6.5, 6.5))) == 2, "C is selectable")
	expect(house.pick_room(house.project_cell(Vector2(0.5, 0.5))) == -1, "rim is not selectable")
	house.upper_visible = true
	expect(house.pick_room(overlap) == 3, "visible U wins over B")
	house.upper_visible = false
	var partition_face := house.project_cell(Vector2(5, 6.5)) - Vector2(0, 16)
	expect(house.pick_room(partition_face) == 0, "cutaway reveals selectable ground behind wall")
	house.cutaway = false
	expect(house.pick_room(partition_face) == -1, "full wall blocks the same pick")
	house.cutaway = true


func check_demo(house: House) -> void:
	expect(house.demo_marker == Vector2(2.5, 2.5), "marker starts at fixture spawn")
	house.play_demo()
	house.demo_tween.pause()
	expect(house.demo_marker == Vector2(3.5, 3.5), "demo starts at cell (3,3)")
	house.demo_tween.custom_step(House.DEMO_STEP_SECONDS)
	expect(house.demo_marker.is_equal_approx(Vector2(4.5, 3.5)), "demo passes cell (4,3)")
	house.demo_tween.custom_step(House.DEMO_STEP_SECONDS / 2.0)
	expect(house.demo_marker.is_equal_approx(Vector2(5, 3.5)), "demo crosses the A-B opening")
	var previous := house.demo_tween
	house.play_demo()
	house.demo_tween.pause()
	expect(not previous.is_valid() and house.demo_marker == Vector2(3.5, 3.5), "replay restarts cleanly")
	house.demo_tween.custom_step(2.0 * House.DEMO_STEP_SECONDS + 0.01)
	expect(house.demo_marker == Vector2(5.5, 3.5) and house.demo_status == "Done", "ends in B")


func expect_edges(actual: Array[Vector4i], expected: Array[Vector4i], level: String) -> void:
	expect(actual.size() == expected.size(), "%s wall count" % level)
	for edge in expected:
		expect(actual.has(edge), "%s wall %s" % [level, edge])


func expect(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)
