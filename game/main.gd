extends Node

const HousePreview = preload("res://observation/house_preview.gd")


func _ready() -> void:
	$Dollhouse.room_selected.connect(_show_room)
	_show_room(&"")


func _show_room(room_id: StringName) -> void:
	$HouseHUD.show_room(HousePreview.room_name(room_id))
