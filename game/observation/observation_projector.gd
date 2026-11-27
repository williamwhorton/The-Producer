extends RefCounted
## The producer's live observation boundary. Capture inputs are simulation-side only.

const House = preload("res://simulation/house_layout.gd")
const HOUSE_CAMERAS := &"house_cameras"
const HOUSE_AUDIO := &"house_audio"
const HOUSE_PHONE := &"house_phone"

var _camera_rooms: Array
var _audio_rooms: Array
var _pending_sounds: Array[Dictionary] = []
var _listening_focus: StringName = &""
var _attended_text: Array[Dictionary] = []


func _init(camera_rooms: Array, audio_rooms: Array) -> void:
	_camera_rooms = camera_rooms.duplicate()
	_audio_rooms = audio_rooms.duplicate()


func _project_cameras(tick: int, active_cast: Dictionary[StringName, Dictionary]) -> Dictionary:
	var contestants: Array[Dictionary] = []
	for id: StringName in active_cast:
		var actor: Dictionary = active_cast[id]
		var cell: Variant = actor.get("cell")
		if not cell is Vector3i:
			continue
		var room := House.room_at(cell)
		if room == &"" or room not in _camera_rooms:
			continue
		# A route names a destination and activity before the actor even moves.
		# Cameras report physical movement, never the route or the decision behind it.
		contestants.append({
			"contestant_id": id,
			"source": HOUSE_CAMERAS,
			"tick": tick,
			"location": {"room_id": room, "cell": cell},
			"activity": &"moving" if actor.get("last_move_tick") == tick else &"stationary",
		})
	return {"tick": tick, "contestants": contestants}


func _capture_sound(event: Dictionary, tick: int) -> void:
	var room := _covered_sound_room(event, tick)
	if room == &"" or event.get("kind") != &"telephone_ring":
		return
	_pending_sounds.append({
		"kind": &"telephone_ring",
		"source": HOUSE_AUDIO,
		"tick": tick,
		"location": {"room_id": room, "cell": event.cell},
	})


func _take_audible_events(tick: int) -> Array[Dictionary]:
	# Transfer ownership of the batch. A caller cannot replay it or mutate our data.
	var result := _pending_sounds
	_pending_sounds = []
	for event: Dictionary in result:
		event["freshness"] = &"current" if event.tick == tick else &"stale"
	return result


func focus_audio_stream(stream_id: StringName) -> void:
	_listening_focus = stream_id


func attended_speech_history() -> Array[Dictionary]:
	return _attended_text.duplicate(true)


# Called only at the instant of capture, with no raw speech buffer to read back.
# No live speech producer exists yet; tests supply synthetic, source-captured words.
func _capture_speech(event: Dictionary, tick: int) -> void:
	if _listening_focus == &"" or event.get("stream_id") != _listening_focus:
		return
	var room := _covered_sound_room(event, tick)
	var words: Variant = event.get("text")
	if room == &"" or not words is String or words.is_empty():
		return
	var source: StringName
	match event.get("kind"):
		&"room_speech":
			source = HOUSE_AUDIO
		&"phone_speech":
			if event.get("side") != &"local":
				return
			source = HOUSE_PHONE
		_:
			return
	_attended_text.append({
		"stream_id": _listening_focus,
		"source": source,
		"tick": tick,
		"location": {"room_id": room, "cell": event.cell},
		"text": words,
	})


func _covered_sound_room(event: Dictionary, tick: int) -> StringName:
	var cell: Variant = event.get("cell")
	if not cell is Vector3i or event.get("tick") != tick:
		return &""
	var room := House.room_at(cell)
	if room == &"" or room not in _audio_rooms:
		return &""
	return room
