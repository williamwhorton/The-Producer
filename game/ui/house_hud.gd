extends CanvasLayer

@onready var _room: Label = $Footer/Room


func show_room(room_name: String) -> void:
	_room.text = "No room selected" if room_name.is_empty() else room_name
