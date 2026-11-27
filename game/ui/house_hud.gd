extends CanvasLayer

signal pause_changed(paused: bool)
signal speed_changed(index: int)

@onready var _room: Label = $Footer/Room
@onready var _pause: Button = $TimeControls/Pause


func _ready() -> void:
	_pause.toggled.connect(_set_paused)
	$TimeControls/Speed.item_selected.connect(speed_changed.emit)


func show_room(room_name: String) -> void:
	_room.text = "No room selected" if room_name.is_empty() else room_name


func _set_paused(paused: bool) -> void:
	_pause.text = "Resume" if paused else "Pause"
	pause_changed.emit(paused)
