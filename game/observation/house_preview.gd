extends RefCounted

const HouseLayout = preload("res://simulation/house_layout.gd")

# Static room names from the production's known floor plan, not simulation data.
const ROOM_NAMES := {
	&"parlor": "Parlor",
	&"study": "Study",
}


static func room_name(room_id: StringName) -> String:
	return ROOM_NAMES.get(room_id, "")


static func floor_plan(show_navigation: bool) -> Dictionary:
	# This is known architecture plus an optional fixed example, not an actor's plan.
	var example: Array[Vector3i] = []
	if show_navigation:
		example = HouseLayout.route_to_exit(Vector3i(-3, HouseLayout.GROUND, 2), &"front")
	return {
		"rooms": HouseLayout.ROOMS.duplicate(),
		"walls": HouseLayout.wall_edges(),
		"exits": HouseLayout.EXITS.values().duplicate(true),
		"obstacles": HouseLayout.OBSTACLES.duplicate(),
		"example_route": example,
	}
