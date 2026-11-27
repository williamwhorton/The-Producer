extends SceneTree
## Explicit development entry point; it is excluded from the player export.

const Runtime = preload("res://simulation/contestant_runtime.gd")
const Scheduler = preload("res://simulation/event_scheduler.gd")
const Loader = preload("res://simulation/scenario_loader.gd")
const Projector = preload("res://observation/observation_projector.gd")
const House = preload("res://simulation/house_layout.gd")

const TICK_USEC := 100
const A := &"test_a"
const B := &"test_b"
const PHONE_CELL := Vector3i(-2, 0, 1)
const PREPARATIONS := {
	"telephone": {"cell": PHONE_CELL, "disconnected": true, "ringer_prepared": true},
}

var _failures := 0


func _initialize() -> void:
	if not OS.has_feature("editor") or DisplayServer.get_name() != "headless":
		printerr("The causal trace requires a headless run from the Godot development editor.")
		quit(1)
		return
	var args := OS.get_cmdline_user_args()
	if args.size() == 2 and args[0] == "--verify-pack":
		_verify_player_pack(args[1])
		quit(0 if _failures == 0 else 1)
		return
	var loaded := Loader.load_file(Loader.DEFAULT_PATH)
	if not loaded.error.is_empty():
		printerr(loaded.error)
		quit(1)
		return

	if not args.is_empty():
		if args.size() != 3 or args[0] != "--print-trace" or args[1] != "--seed" \
				or not args[2].is_valid_int() or str(args[2].to_int()) != args[2]:
			printerr("Usage: -- --print-trace --seed INTEGER")
			quit(1)
			return
		var run := _run(loaded.scenario, args[2].to_int(), true)
		for entry: Dictionary in run.trace:
			print(JSON.stringify(entry))
	else:
		_test_trace(loaded.scenario)
		if _failures == 0:
			print("PASS: ordered causal trace, private snapshots, and unchanged public observations")
	quit(0 if _failures == 0 else 1)


func _verify_player_pack(path: String) -> void:
	var archive := ZIPReader.new()
	if archive.open(path) != OK:
		_check(false, "could not open exported player pack: " + path)
		return
	var entries := archive.get_files()
	archive.close()
	_check(entries.has("project.binary") and entries.has("scenarios/house_preview.json"),
			"the pack contains the configured project and its scenario")
	for entry: String in entries:
		_check(not entry.begins_with("tests/") and not entry.contains("causal_trace"),
				"developer tooling cannot ship: " + entry)
	if _failures == 0:
		print("PASS: player pack omits developer tooling")


func _run(scenario: Dictionary, seed_value: int, trace_enabled: bool, fast := false) -> Dictionary:
	var trace: Array[Dictionary] = []
	var sink := Callable.create(trace, &"append") if trace_enabled else Callable()
	var clock := Scheduler.new(seed_value, TICK_USEC, 2, 4, sink)
	var projector := Projector.new(scenario.surveillance.camera_rooms, House.ROOMS.keys())
	var runtime := Runtime.new(scenario.cast, clock, {A: Runtime.Motive.UNDERSTAND_CUE},
			{}, {B: 2}, scenario.parameters.required_exit_id, PREPARATIONS, projector)
	var initial := runtime.camera_snapshot()
	runtime.perceive_event(PHONE_CELL, Runtime.Cue.ANOMALOUS_EVIDENCE, [A])
	runtime.perceive_event(PHONE_CELL, Runtime.Cue.STAGING_EVIDENCE, [B])
	runtime.perceive_event(PHONE_CELL, Runtime.Cue.CHRONIC_PRESSURE, [B])
	_check(runtime.camera_snapshot() == initial, "private appraisals cannot change current camera evidence")
	clock.set_paused(true)
	runtime.queue_telephone_ring()
	runtime.queue_temperature(&"study", Runtime.Temperature.HOT) # Not installed.
	var cancelled := runtime.queue_telephone_ring()
	_check(clock.cancel_live_trigger(cancelled), "paused command can be cancelled")
	clock.advance(10 * TICK_USEC)
	_check(clock.current_tick() == 0 and runtime.take_audible_events().is_empty(),
			"paused commands cannot resolve or expose evidence")
	clock.set_paused(false)
	if fast:
		clock.set_speed(Scheduler.Speed.FAST)
	var frames: Array[Dictionary] = [initial]
	var audio: Array[Dictionary] = []
	for step in 12:
		clock.advance(TICK_USEC / 2 if fast else TICK_USEC)
		frames.append(runtime.camera_snapshot())
		audio.append_array(runtime.take_audible_events())
	return {"trace": trace, "camera": frames, "audio": audio,
		"history": projector.attended_speech_history(),
		"final_state": {"active": runtime._actors, "departed": runtime._departed}}


func _test_trace(scenario: Dictionary) -> void:
	var run := _run(scenario, 21, true)
	var trace: Array[Dictionary] = run.trace
	_check(run == _run(scenario, 21, true) and run == _run(scenario, 21, true, true),
			"identical inputs repeat the full trace and final state at either speed")
	var untraced := _run(scenario, 21, false)
	var expected := run.duplicate()
	expected.trace = []
	_check(untraced == expected, "tracing is opt-in and does not change private state or public evidence")

	var first_tick := trace.filter(func(entry: Dictionary) -> bool: return entry.tick == 1)
	var kinds := first_tick.map(func(entry: Dictionary) -> StringName: return entry.kind)
	_check(kinds == [&"live_trigger", &"perception", &"live_trigger", &"autonomous_event",
		&"random_draw", &"decision", &"decision", &"contestant_state"],
		"the accepted ring, rejected setpoint, seeded draw and decisions are recorded in order")
	if kinds.size() != 8:
		return
	_check(trace[0].kind == &"run" and trace[0].details.seed == 21,
			"trace identifies its seed before simulation work")
	_check(first_tick[0].details == {"id": 1, "accepted": true}
		and first_tick[2].details == {"id": 2, "accepted": false}
		and first_tick[1].details.witnesses == [A], "only A heard the accepted ring")
	var investigate: Dictionary = first_tick[5].details
	var leave: Dictionary = first_tick[6].details
	_check(investigate.contestant_id == A and investigate.activity == &"investigate"
		and investigate.reason == &"investigate_perceived_cue" and investigate.cue == PHONE_CELL
		and investigate.route.size() == 1, "A's decision retains the cue and chosen lead")
	_check(leave.contestant_id == B and leave.activity == &"leave"
		and leave.reason == &"distrust_and_stress_outweigh_staying" and leave.staging_suspicion == 1
		and leave.stress == 1 and leave.stay_motivation == 2,
		"B's decision retains the chronic pressure that tipped the choice")

	var other := _run(scenario, 22, true)
	var other_tick: Array = other.trace.filter(func(entry: Dictionary) -> bool: return entry.tick == 1)
	_check(other_tick.size() == 8 and other_tick[4].details.value != first_tick[4].details.value
		and other_tick[5].details.activity == investigate.activity
		and other_tick[5].details.route != investigate.route, "another seed changes the tied lead, not the motive")

	var initial: Dictionary = trace[1].details.active
	var state: Dictionary = first_tick[7].details.active
	_check(initial[A].memory.is_empty() and state[A].memory.size() == 2 and state[B].memory.size() == 2
		and state[A].fear == 2 and state[A].supernatural_belief == 1 and state[B].staging_suspicion == 1
		and state[A].route == investigate.route, "historical snapshots retain detached private values and routes")
	_check(trace.back().details == run.final_state and run.final_state.departed.has(B),
			"the ordered trace ends with the actual final state, including departure")
	_check(run.camera[1].contestants[1] == {"contestant_id": B, "source": Projector.HOUSE_CAMERAS,
		"tick": 1, "location": {"room_id": &"study", "cell": scenario.cast[B].start_cell},
		"activity": &"stationary"}, "camera evidence reveals neither private departure intent nor debug records")
	_check(run.audio == [{"kind": &"telephone_ring", "source": Projector.HOUSE_AUDIO,
		"tick": 1, "location": {"room_id": &"parlor", "cell": PHONE_CELL}, "freshness": &"current"}]
		and run.history.is_empty(), "the audible cue exposes no witnesses, appraisals, or transcript")


func _check(passed: bool, description: String) -> void:
	if not passed:
		_failures += 1
		push_error("FAIL: " + description)
