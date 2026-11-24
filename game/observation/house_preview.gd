extends RefCounted

# Static room names from the production's known floor plan, not simulation data.
const ROOM_NAMES := {
	&"parlor": "Parlor",
	&"study": "Study",
}


static func room_name(room_id: StringName) -> String:
	return ROOM_NAMES.get(room_id, "")
