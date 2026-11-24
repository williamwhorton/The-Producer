extends RefCounted
## Disposable fixture, not a production contestant model.

const CAMERA := "fixture_camera"
const UNOBSERVED_TICK := 3

var _tick := 0
var _rng := RandomNumberGenerator.new()
var _contestant: Dictionary
var _events: Array[Dictionary] = []


func _init(initial_seed: int, initial_fear: int, initial_intent: String) -> void:
	_rng.seed = initial_seed
	_contestant = {"fear": initial_fear, "intent": initial_intent}


func step() -> void:
	_tick += 1
	# A seeded choice between two visible actions, with no psychology or player input.
	var action := "turn_left" if _rng.randi_range(0, 1) == 0 else "turn_right"
	_events.append({
		"tick": _tick,
		"kind": action,
		"source": CAMERA,
		"internal": {"contestant": _contestant, "seed": _rng.seed},
	})
	if _tick == UNOBSERVED_TICK:
		# A hidden event shares a tick with the visible one. Append order breaks ties.
		_events.append({
			"tick": _tick,
			"kind": "private_note",
			"source": "",
			"internal": {"text": "fixture-only hidden note"},
		})


func get_observation() -> Array[Dictionary]:
	var report: Array[Dictionary] = []
	for event in _events:
		if event.source != CAMERA:
			continue
		# Project only allowed scalar facts into fresh records; never return event payloads.
		report.append({"tick": event.tick, "kind": event.kind, "source": event.source})
	return report
