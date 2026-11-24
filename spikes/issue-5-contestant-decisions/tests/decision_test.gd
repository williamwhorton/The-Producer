extends SceneTree

const Simulation = preload("res://contestant_simulation.gd")
const Projector = preload("res://observation_projector.gd")

var _failures := 0


func _initialize() -> void:
	var first := _run(12345, false)
	var repeat := _run(12345, false)
	var alternate := _run(67890, false)
	_check(first == repeat, "same seed and initial state reproduce raw and public traces")
	_check(first.raw != alternate.raw, "another seed changes the fixture's tie-break route trace")
	for run in [first, alternate]:
		for index in range(32):
			var events: Array = run.raw[index]
			var expected_actors := ["alex", "bea", "cam", "dev"] if index == 0 else ["alex", "bea", "dev"]
			var actual_actors: Array = []
			for event in events:
				actual_actors.append(event.actor)
				_check(event.tick == index + 1, "raw events retain tick order")
			_check(actual_actors == expected_actors, "actors stay ordered and Cam attempts to quit only once")
			_check(events[0].actor == "alex" and events[0].decision == "investigate"
					and events[0].private.beliefs.suspects_staging and events[0].private.perceives_danger == false,
					"distrust does not force a motivated contestant to quit")
			_check(events[1].actor == "bea" and events[1].decision == "avoid"
					and not events[1].private.beliefs.suspects_staging, "danger alone can cause avoidance")
			_check(run.public[index].size() == 1
					and run.public[index][0].actor == "alex", "only the covered route is observed")
		_check(run.raw[0][2].actor == "cam" and run.raw[0][2].decision == "attempt_quit"
				and not run.raw[0][2].private.perceives_danger, "distrust can prompt quitting without danger")
		_check(run.raw[0][3].actor == "dev" and run.raw[0][3].decision == "avoid",
				"danger need not prompt quitting even with weak motive")

	var reversed_belief := _run(12345, true)
	_check(reversed_belief.raw[0][2].decision == "investigate",
			"changing only Cam's starting belief changes Cam's decision")
	if "--force-failure" in OS.get_cmdline_user_args():
		_check(false, "intentional assertion failure")
	if _failures == 0:
		print("PASS: seeded decisions and ordered observations (32 ticks)")
	quit(0 if _failures == 0 else 1)


func _run(seed_value: int, cam_trusts_contest: bool) -> Dictionary:
	var initial: Array[Dictionary] = [
		_contestant("alex", true, false, true),
		_contestant("bea", false, true, true),
		_contestant("cam", not cam_trusts_contest, false, false),
		_contestant("dev", false, true, false),
	]
	var original := initial.duplicate(true)
	var simulation := Simulation.new(seed_value, initial)
	var raw: Array = []
	var public: Array = []
	for tick in range(1, 33):
		var events := simulation.step()
		# Both investigation routes are covered in this synthetic context.
		var captures: Array[Dictionary] = []
		for location in ["east_landing", "west_landing"]:
			captures.append({
				"kind": "sighting", "source": "fixture_route", "tick": tick,
				"authorized": true, "active": true, "location": location,
			})
		raw.append(events)
		public.append(Projector.project(tick, events, captures))
	_check(initial == original, "running the domain does not mutate the initial fixture")
	return {"raw": raw, "public": public}


func _contestant(id: String, distrust: bool, danger: bool, motive: bool) -> Dictionary:
	return {
		"id": id, "beliefs": {"suspects_staging": distrust}, "perceives_danger": danger,
		"motive_to_stay": motive, "quit_attempted": false,
	}


func _check(condition: bool, description: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: ", description)
