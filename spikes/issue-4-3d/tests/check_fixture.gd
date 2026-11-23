extends SceneTree

const HOUSE := preload("res://main.tscn")
var failures := 0


func _initialize() -> void:
	call_deferred("run")


func check(condition: bool, description: String) -> void:
	if not condition:
		failures += 1
		push_error(description)


func run() -> void:
	var house = HOUSE.instantiate()
	root.add_child(house)
	check(house.camera.projection == Camera3D.PROJECTION_ORTHOGONAL, "Orthographic camera")
	check(house.slabs[0].get_aabb().size.is_equal_approx(Vector3(10, 0.25, 10)), "10×10 slab")
	check(house.slabs[1].get_aabb().size.is_equal_approx(Vector3(4, 0.25, 4)), "4×4 upper slab")
	check(house.slabs[0].position.is_equal_approx(Vector3(5, -0.16, 5)), "Ground slab center")
	check(house.slabs[1].position.is_equal_approx(Vector3(7, -0.16, 3))
		and house.upper.position.y > 0.0, "Upper slab directly above B")
	check(not house.upper.visible and house.cutaway, "Launch shows ground in cutaway")
	for y in 10:
		for x in 10:
			var expected := -1
			if x in range(1, 5) and y in range(1, 9):
				expected = 0
			elif x in range(5, 9) and y in range(1, 9):
				expected = 1 if y < 5 else 2
			check(house.pick_room(Vector3(x + 0.5, 10, y + 0.5), Vector3.DOWN) == expected,
				"Ground selection at (%d,%d)" % [x, y])
	check(house.pick_room(Vector3(-1, 10, -1), Vector3.DOWN) == -1, "Miss clears selection")

	check_walls(house)
	var marker_positions := [Vector3(2.5, 0, 2.5), Vector3(6.5, 0, 2.5), Vector3(7.5, 0, 7.5)]
	check(house.markers.size() == marker_positions.size(), "Exactly three markers")
	for i in house.markers.size():
		check(house.markers[i].position == marker_positions[i], "Marker %d initial cell" % i)
	check(house.upper.get_node("StairSymbol").position == Vector3(6.5, 0, 3.5), "Stair cell")

	# A shallow ray from the foreground hits C unless the near wall blocks it.
	var origin := Vector3(7.5, 1.2, 11)
	var direction := Vector3(0, -1.2, -3.5).normalized()
	check(house.pick_room(origin, direction) == 2, "Near cutaway exposes C")
	house.set_cutaway(false)
	check(house.pick_room(origin, direction) == -1, "Full near wall blocks C")
	house.set_cutaway(true)
	check(house.pick_room(origin, direction) == 2, "Restoring cutaway exposes C again")

	# At the real camera angle the horizontal offset from elevation matters.
	var click: Vector2 = house.camera.unproject_position(Vector3(8.65, 2.75, 4.65))
	var ray_origin: Vector3 = house.camera.project_ray_origin(click)
	var ray_direction: Vector3 = house.camera.project_ray_normal(click)
	check(house.pick_room(ray_origin, ray_direction) == 1, "Camera ray reaches B with upper hidden")
	house.set_upper_visible(true)
	check(house.pick_room(ray_origin, ray_direction) == 3, "Same click selects upper slab when visible")
	check(house.pick_room(Vector3(7.5, 2.6, 0), Vector3.BACK) == -1, "Slab side isn't selectable")
	house.select_room(3)
	check(house.outlines[3].is_visible_in_tree(), "Selected U is outlined")
	house.set_upper_visible(false)
	check(house.selected_room == -1 and not house.outlines[3].visible, "Hiding U clears its selection")

	house.play_demo()
	house.demo_tween.pause()
	check(house.markers[0].position == Vector3(3.5, 0, 3.5), "Route starts in A at (3,3)")
	house.demo_tween.custom_step(0.85)
	check(house.markers[0].position.is_equal_approx(Vector3(4.5, 0, 3.5)), "Route reaches (4,3)")
	house.demo_tween.custom_step(0.425)
	check(house.markers[0].position.is_equal_approx(Vector3(5, 0, 3.5)), "Route crosses A–B opening")
	house.demo_tween.custom_step(0.426)
	check(house.markers[0].position.is_equal_approx(Vector3(5.5, 0, 3.5))
		and house.demo_status == "Done", "Route ends in B at (5,3)")
	house.play_demo()
	check(house.markers[0].position == Vector3(3.5, 0, 3.5), "Route is replayable")
	house.demo_tween.kill()

	if failures == 0:
		print("PASS: #4 3D fixture, wall and floor occlusion, room picking, and scripted A–B route")
	quit(1 if failures else 0)


func check_walls(house: Node3D) -> void:
	# Midpoints encode which one-cell edge a wall occupies (not occupied cells).
	var expected_ground: Array[Vector2] = []
	var expected_upper: Array[Vector2] = []
	for i in 10:
		expected_ground.append_array([Vector2(i + 0.5, 0), Vector2(i + 0.5, 10),
			Vector2(0, i + 0.5), Vector2(10, i + 0.5)])
	for y in range(1, 9):
		if y != 3:
			expected_ground.append(Vector2(5, y + 0.5))
	for x in range(5, 9):
		if x != 7:
			expected_ground.append(Vector2(x + 0.5, 5))
		expected_upper.append_array([Vector2(x + 0.5, 1), Vector2(x + 0.5, 5)])
	for y in range(1, 5):
		expected_upper.append_array([Vector2(5, y + 0.5), Vector2(9, y + 0.5)])
	for wall in house.walls:
		var midpoint := Vector2(wall.position.x, wall.position.z)
		var expected := expected_upper if wall.get_parent() == house.upper else expected_ground
		check(midpoint in expected, "No extra or duplicate wall at %s" % midpoint)
		expected.erase(midpoint)
		var size: Vector3 = wall.get_aabb().size
		var along_x := not is_equal_approx(midpoint.x, floorf(midpoint.x))
		check(is_equal_approx(size.x if along_x else size.z, 1.0), "Wall spans its edge")
	check(expected_ground.is_empty() and expected_upper.is_empty(), "All required walls present")
	check(house.ground.get_node("ThresholdAB").position.is_equal_approx(Vector3(5, 0.012, 3.5)),
		"A–B threshold lies in its wall opening")
	check(house.ground.get_node("ThresholdBC").position.is_equal_approx(Vector3(7.5, 0.012, 5)),
		"B–C threshold lies in its wall opening")
