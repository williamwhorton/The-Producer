extends SceneTree

const Simulation = preload("res://contestant_simulation.gd")
const Projector = preload("res://observation_projector.gd")

var _failures := 0


func _initialize() -> void:
	_check_unmonitored_conversation()
	_check_missing_or_ineligible_sources()
	_check_allowlist_and_detachment()
	_check_delayed_testimony()
	if _failures == 0:
		print("PASS: independent observation privacy checks")
	quit(0 if _failures == 0 else 1)


func _check_unmonitored_conversation() -> void:
	var actors: Array[Dictionary] = [
		{"id": "alex", "beliefs": {"suspects_staging": true}, "perceives_danger": true,
			"motive_to_stay": true, "quit_attempted": false},
		{"id": "bea", "beliefs": {"suspects_staging": false}, "perceives_danger": true,
			"motive_to_stay": true, "quit_attempted": false},
	]
	var talked := Simulation.new(42, actors)
	var silent := Simulation.new(42, actors)
	var talked_events := talked.step({"listener_index": 1, "speaker": "alex"})
	var silent_events := silent.step()
	var capture := _sighting()
	capture.location = "common_room"
	_check(talked_events.size() == 3 and talked_events[0].kind == "private_conversation",
			"the domain records the private conversation")
	_check(talked.step()[1].private.beliefs.suspects_staging
			and not silent.step()[1].private.beliefs.suspects_staging,
			"the private exchange changes only the listener's knowledge")
	var observed := Projector.project(1, talked_events, [capture])
	_check(observed.size() == 2 and observed == Projector.project(1, silent_events, [capture]),
			"equivalent sightings do not reveal whether the private exchange took place")
	capture.location = "pantry"
	_check(Projector.project(1, talked_events, [capture]).is_empty(),
			"even sighting coverage at the conversation location cannot capture speech")


func _check_missing_or_ineligible_sources() -> void:
	var events: Array[Dictionary] = [_movement()]
	_check(Projector.project(1, events, []).is_empty(), "no source means no observation")
	var missing_access := _sighting()
	missing_access.erase("authorized")
	_check(Projector.project(1, events, [missing_access]).is_empty(), "missing access fails closed")
	for overrides in [
		{"authorized": false}, {"active": false}, {"active": "true"}, {"source": ""},
		{"source": {"id": "fixture_hall"}}, {"kind": "unknown"}, {"tick": 2},
		{"location": "pantry"},
	]:
		var capture := _sighting()
		capture.merge(overrides, true)
		_check(Projector.project(1, events, [capture]).is_empty(), "ineligible source: %s" % overrides)


func _check_allowlist_and_detachment() -> void:
	var events: Array[Dictionary] = [_movement(), {
		"tick": 1, "kind": "supernatural_action", "location": "exit_hall",
		"actor": "hidden_entity", "cause": "SECRET_CAUSE",
	}]
	var capture := _sighting()
	capture["internal_metadata"] = {"raw_events": events}
	var expected := [{
		"kind": "sighting", "tick": 1, "source": "fixture_hall",
		"actor": "bea", "location": "exit_hall",
	}]
	var before := events.duplicate(true)
	var actual := Projector.project(1, events, [capture])
	_check(actual == expected and JSON.stringify(actual) == JSON.stringify(expected),
			"exact public shape omits decision, nested secrets and the unobserved supernatural event")
	if not actual.is_empty():
		actual[0]["actor"] = "injected"
		actual[0]["extra"] = true
		actual.clear()
	_check(events == before and Projector.project(1, events, [capture]) == expected,
			"mutating the view leaves the trace and the next public read unchanged")


func _check_delayed_testimony() -> void:
	var events: Array[Dictionary] = [_movement()]
	var testimony := {
		"kind": "testimony", "tick": 3, "source": "fixture_witness",
		"authorized": true, "active": true, "claim": "Bea went to the pantry earlier.",
		"private": {"actual_location": "exit_hall"},
	}
	_check(Projector.project(1, events, [testimony]).is_empty(), "testimony does not appear early")
	_check(Projector.project(3, [], [testimony]) == [{
		"kind": "unverified_claim", "tick": 3, "source": "fixture_witness",
		"claim": "Bea went to the pantry earlier.",
	}], "a later claim is attributed, not corrected or promoted to private truth")
	_check(Projector.project(4, [], [testimony]).is_empty(), "testimony is not redelivered")


func _movement() -> Dictionary:
	return {
		"tick": 1, "kind": "movement", "actor": "bea", "location": "exit_hall",
		"decision": "attempt_quit", "private": {"beliefs": [{"thought": "SECRET_BELIEF"}]},
	}


func _sighting() -> Dictionary:
	return {
		"kind": "sighting", "source": "fixture_hall", "tick": 1,
		"authorized": true, "active": true, "location": "exit_hall",
	}


func _check(condition: bool, description: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: ", description)
