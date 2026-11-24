extends RefCounted
## The authored prototype floor plan. Cells are (column, floor, row), not world positions.

const GROUND := 0
const ROOMS := {
	&"parlor": Rect2i(-4, -2, 4, 5),
	&"study": Rect2i(0, -2, 4, 5),
}
const DOORS := [
	[Vector3i(-1, GROUND, 0), Vector3i(0, GROUND, 0)],
]
# An exit runs from an interior threshold to the adjacent exterior. Routing stops inside.
const EXITS := {
	&"front": [Vector3i(2, GROUND, 2), Vector3i(2, GROUND, 3)],
}
const OBSTACLES := {
	&"sofa": Rect2i(-4, -2, 3, 1),
	&"table": Rect2i(-4, -1, 3, 1),
	&"bookshelf": Rect2i(1, -2, 3, 1),
	&"desk": Rect2i(1, -1, 3, 1),
}
const _DIRECTIONS := [Vector3i.RIGHT, Vector3i.BACK, Vector3i.LEFT, Vector3i.FORWARD]


static func room_at(cell: Vector3i) -> StringName:
	if cell.y == GROUND:
		for room: StringName in ROOMS:
			if ROOMS[room].has_point(Vector2i(cell.x, cell.z)):
				return room
	return &""


static func is_walkable(cell: Vector3i) -> bool:
	if room_at(cell) == &"":
		return false
	for footprint: Rect2i in OBSTACLES.values():
		if footprint.has_point(Vector2i(cell.x, cell.z)):
			return false
	return true


static func can_step(from: Vector3i, to: Vector3i) -> bool:
	if to - from not in _DIRECTIONS or not is_walkable(from) or not is_walkable(to):
		return false
	return room_at(from) == room_at(to) or _is_door(from, to)


static func find_route(
	start: Vector3i, goal: Vector3i, blocked_cells: Array[Vector3i] = []
) -> Array[Vector3i]:
	if not is_walkable(start) or not is_walkable(goal):
		return []
	if start in blocked_cells or goal in blocked_cells:
		return []

	# Breadth-first search visits each reachable cell once. Cardinal steps all cost one.
	var frontier: Array[Vector3i] = [start]
	var came_from: Dictionary[Vector3i, Vector3i] = {start: start}
	var index := 0
	while index < frontier.size():
		var current := frontier[index]
		if current == goal:
			var route: Array[Vector3i] = [goal]
			while current != start:
				current = came_from[current]
				route.append(current)
			route.reverse()
			return route
		for direction: Vector3i in _DIRECTIONS:
			var next := current + direction
			if not came_from.has(next) and next not in blocked_cells and can_step(current, next):
				came_from[next] = current
				frontier.append(next)
		index += 1
	return []


static func route_to_exit(
	start: Vector3i, exit_id: StringName, blocked_cells: Array[Vector3i] = []
) -> Array[Vector3i]:
	if not EXITS.has(exit_id):
		return []
	return find_route(start, EXITS[exit_id][0], blocked_cells)


static func wall_edges() -> Array[Array]:
	var edges: Array[Array] = []
	for room: StringName in ROOMS:
		var bounds: Rect2i = ROOMS[room]
		for row in range(bounds.position.y, bounds.end.y):
			for column in range(bounds.position.x, bounds.end.x):
				var cell := Vector3i(column, GROUND, row)
				for direction: Vector3i in _DIRECTIONS:
					var neighbor := cell + direction
					var other_room := room_at(neighbor)
					if other_room == room:
						continue
					# Each interior partition is shared by two rooms; emit it once.
					if other_room != &"" and (direction.x < 0 or direction.z < 0):
						continue
					if not _is_door(cell, neighbor) and [cell, neighbor] not in EXITS.values():
						edges.append([cell, neighbor])
	return edges


static func _is_door(from: Vector3i, to: Vector3i) -> bool:
	return [from, to] in DOORS or [to, from] in DOORS
