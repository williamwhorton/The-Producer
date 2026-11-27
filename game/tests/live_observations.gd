extends SceneTree

const Runtime = preload("res://simulation/contestant_runtime.gd")
const Scheduler = preload("res://simulation/event_scheduler.gd")
const Loader = preload("res://simulation/scenario_loader.gd")
const Projector = preload("res://observation/observation_projector.gd")
const House = preload("res://simulation/house_layout.gd")

const TICK_USEC := 100
const A := &"test_a"
const B := &"test_b"
const PARLOR := &"parlor"
const STUDY := &"study"
const PHONE_CELL := Vector3i(-2, 0, 1)
const OUTSIDE := Vector3i(2, 0, 3)
const PREPARATIONS := {
	"telephone": {"cell": PHONE_CELL, "disconnected": true, "ringer_prepared": true},
}

var _failures := 0


func _initialize() -> void:
	var loaded := Loader.load_file(Loader.DEFAULT_PATH)
	_check(loaded.error.is_empty(), "authored scenario loads")
	if _failures == 0:
		var trace := _run(loaded.scenario, false)
		_check(not trace.is_empty() and trace == _run(loaded.scenario, true),
				"live observations repeat across playback speeds")
		_test_coverage(loaded.scenario)
		_test_speech()
	if _failures == 0:
		print("PASS: live camera motion and departure, localized ringing, coverage, and attended-only text")
	quit(0 if _failures == 0 else 1)


func _run(scenario: Dictionary, fast: bool) -> Array:
	var clock := Scheduler.new(21, TICK_USEC, 2, 4)
	if fast:
		clock.set_speed(Scheduler.Speed.FAST)
	var elapsed := TICK_USEC / 2 if fast else TICK_USEC
	var projector := Projector.new(scenario.surveillance.camera_rooms, House.ROOMS.keys())
	var exit_id: StringName = scenario.parameters.required_exit_id
	var runtime := Runtime.new(scenario.cast, clock, {}, {}, {A: 1}, exit_id, PREPARATIONS, projector)
	var exit_route := House.route_to_exit(scenario.cast[A].start_cell, exit_id)
	var initial := runtime.camera_snapshot()
	_check(initial == {"tick": 0, "contestants": [
		_marker(A, PARLOR, scenario.cast[A].start_cell, 0, &"stationary"),
		_marker(B, STUDY, scenario.cast[B].start_cell, 0, &"stationary"),
	]}, "both covered rooms have only allowlisted camera fields at initialization")

	# A private appraisal changes the autonomous choice, not the visible state.
	runtime.perceive_event(PHONE_CELL, Runtime.Cue.ANOMALOUS_EVIDENCE, [A])
	runtime.perceive_event(PHONE_CELL, Runtime.Cue.STAGING_EVIDENCE, [A])
	runtime.perceive_event(PHONE_CELL, Runtime.Cue.CHRONIC_PRESSURE, [A])
	runtime.perceive_event(PHONE_CELL, Runtime.Cue.STARTLE, [A])
	var private_before := runtime._actors.duplicate(true)
	var detached := runtime.camera_snapshot()
	_check(detached == initial, "fear, stress, beliefs, suspicion and memories do not change camera evidence")
	detached.contestants[0].location.cell = OUTSIDE
	detached.contestants.clear()
	_check(runtime._actors == private_before and runtime.camera_snapshot() == initial,
			"mutating nested camera evidence cannot change the world or future snapshots")

	clock.set_paused(true)
	runtime.queue_telephone_ring()
	clock.advance(5 * elapsed)
	_check(runtime.camera_snapshot() == initial and runtime.take_audible_events().is_empty(),
			"paused time produces neither movement nor queued ring evidence")
	clock.set_paused(false)
	var trace: Array = [initial]
	for i in exit_route.size():
		clock.advance(elapsed)
		var tick := i + 1
		var frame := runtime.camera_snapshot()
		var cell: Vector3i = exit_route[i]
		if i < exit_route.size() - 1:
			var activity := &"stationary" if i == 0 else &"moving"
			_check(frame.contestants.size() == 2 and frame.contestants.front() ==
					_marker(A, House.room_at(cell), cell, tick, activity),
					"the camera follows actual movement across rooms, never the exit plan")
		else:
			_check(frame.contestants.size() == 1 and frame.contestants.front().contestant_id == B
					and runtime._departed.has(A),
					"the live marker is removed when the runtime completes departure")
		trace.append(frame)

	# B's normal routine brings B back to the study, leaving the parlor empty.
	clock.advance(3 * elapsed)
	var observed_cast: Array = runtime.camera_snapshot().contestants
	_check(observed_cast.size() == 1 and observed_cast.front().location.room_id == STUDY,
			"the parlor is empty before the next rings")
	# Multiple captures survive the same advance even when no contestant hears them.
	runtime.queue_telephone_ring()
	runtime.queue_telephone_ring()
	clock.advance(elapsed)
	var tick := clock.current_tick()
	var sounds := runtime.take_audible_events()
	_check(sounds == [_ring(1, &"stale"), _ring(tick, &"current"), _ring(tick, &"current")],
			"real rings preserve order, locality, source, tick and freshness, including an empty room")
	_check(runtime.take_audible_events().is_empty() and projector.attended_speech_history().is_empty(),
			"delivered cues cannot replay and a ring never makes a call or transcript")
	trace.append(sounds.duplicate(true))
	if not sounds.is_empty():
		sounds.back().location.cell = OUTSIDE
		_check(runtime._last_ring.cell == PHONE_CELL and sounds.front().location.cell == PHONE_CELL,
				"audio locations are detached from the world and other observations")
	return trace


func _test_coverage(scenario: Dictionary) -> void:
	var cameras: Array[StringName] = [STUDY, &"outside"]
	var audio: Array[StringName] = [STUDY, &"outside"]
	var projector := Projector.new(cameras, audio)
	cameras.append(PARLOR)
	audio.append(PARLOR)
	var clock := Scheduler.new(21, TICK_USEC, 2, 4)
	var outside_cast: Dictionary[StringName, Dictionary] = scenario.cast.duplicate(true)
	outside_cast[&"outside"] = {"room_id": &"outside", "start_cell": OUTSIDE}
	var runtime := Runtime.new(outside_cast, clock, {}, {}, {}, &"front", PREPARATIONS, projector)
	_check(runtime.camera_snapshot().contestants == [
		_marker(B, STUDY, scenario.cast[B].start_cell, 0, &"stationary"),
	], "missing room coverage and off-site cells produce no identities or markers")
	runtime.queue_telephone_ring()
	clock.advance(TICK_USEC)
	_check(not runtime._last_ring.is_empty() and runtime.take_audible_events().is_empty(),
			"a real ring outside the audio coverage is withheld")
	projector._capture_sound({"kind": &"telephone_ring", "cell": OUTSIDE, "tick": 1}, 1)
	projector._capture_sound({"kind": &"hidden_event", "cell": Vector3i.ZERO, "tick": 1}, 1)
	_check(runtime.take_audible_events().is_empty(), "off-site cells and unknown event kinds fail closed")

	var event := {"kind": &"telephone_ring", "cell": Vector3i.ZERO, "tick": 1,
		"payload": {"witnesses": [A], "private": {"fear": 2, "intent": &"leave"}}}
	projector._capture_sound(event, 1)
	_check(runtime.take_audible_events() == [{"kind": &"telephone_ring", "source": Projector.HOUSE_AUDIO,
		"tick": 1, "location": {"room_id": STUDY, "cell": Vector3i.ZERO}, "freshness": &"current"}],
		"the audio projector reconstructs a nested allowlist instead of copying the event payload")

	var no_source := Runtime.new(scenario.cast, clock, {}, {}, {}, &"front", PREPARATIONS)
	var unprepared := Runtime.new(scenario.cast, clock, {}, {}, {}, &"front", {},
			Projector.new([], [PARLOR]))
	no_source.queue_telephone_ring()
	unprepared.queue_telephone_ring()
	clock.advance(TICK_USEC)
	_check(no_source.camera_snapshot().contestants.is_empty() and not no_source._last_ring.is_empty()
			and no_source.take_audible_events().is_empty(), "missing surveillance fails closed")
	_check(unprepared._last_ring.is_empty() and unprepared.take_audible_events().is_empty(),
			"an unprepared trigger produces no audible evidence")


func _test_speech() -> void:
	var projector := Projector.new([PARLOR, STUDY], [PARLOR])
	var room := {"kind": &"room_speech", "stream_id": &"room", "tick": 1,
		"cell": PHONE_CELL, "text": "I'm fine.", "private": {"belief": "I am not fine."}}
	var phone := {"kind": &"phone_speech", "stream_id": &"phone", "tick": 1,
		"cell": PHONE_CELL, "side": &"local", "text": "Missed phone words."}
	projector._capture_speech(room, 1)
	_check(projector.attended_speech_history().is_empty(), "no words before attention")
	projector.focus_audio_stream(&"room")
	projector._capture_speech(room, 1)
	projector._capture_speech(phone, 1)
	projector.focus_audio_stream(&"phone")
	projector._capture_speech(phone, 2)
	phone.tick = 2
	room.tick = 2
	room.text = "Now unattended room words."
	projector._capture_speech(room, 2)
	phone.side = &"remote"
	phone.text = "Remote words."
	projector._capture_speech(phone, 2)
	phone.side = &"local"
	phone.text = "Attended local words."
	projector._capture_speech(phone, 2)
	phone.cell = OUTSIDE
	phone.text = "Off-site words."
	projector._capture_speech(phone, 2)
	phone.cell = Vector3i.ZERO
	phone.text = "Uncovered study words."
	projector._capture_speech(phone, 2)
	projector.focus_audio_stream(&"")
	var expected := [
		{"stream_id": &"room", "source": Projector.HOUSE_AUDIO, "tick": 1,
			"location": {"room_id": PARLOR, "cell": PHONE_CELL}, "text": "I'm fine."},
		{"stream_id": &"phone", "source": Projector.HOUSE_PHONE, "tick": 2,
			"location": {"room_id": PARLOR, "cell": PHONE_CELL}, "text": "Attended local words."},
	]
	var history := projector.attended_speech_history()
	_check(history == expected, "only live, focused, source-authorized words enter the text history")
	if not history.is_empty():
		history.front().location.room_id = STUDY
		history.clear()
	_check(projector.attended_speech_history() == expected, "attended history is rereadable and detached")


func _marker(id: StringName, room: StringName, cell: Vector3i, tick: int, activity: StringName) -> Dictionary:
	return {"contestant_id": id, "source": Projector.HOUSE_CAMERAS, "tick": tick,
		"location": {"room_id": room, "cell": cell}, "activity": activity}


func _ring(tick: int, freshness: StringName) -> Dictionary:
	return {"kind": &"telephone_ring", "source": Projector.HOUSE_AUDIO, "tick": tick,
		"location": {"room_id": PARLOR, "cell": PHONE_CELL}, "freshness": freshness}


func _check(passed: bool, description: String) -> void:
	if not passed:
		_failures += 1
		push_error("FAIL: " + description)
