extends SceneTree

const Runtime = preload("res://simulation/contestant_runtime.gd")
const Scheduler = preload("res://simulation/event_scheduler.gd")
const Loader = preload("res://simulation/scenario_loader.gd")
const House = preload("res://simulation/house_layout.gd")
const Preview = preload("res://observation/house_preview.gd")

const TICK_USEC := 100
const A := &"test_a"
const B := &"test_b"
const PARLOR_CUE := Vector3i(-2, 0, 1)
const STUDY_CUE := Vector3i(1, 0, 1)
const THRESHOLD := Vector3i(2, 0, 2)
const STAGING := Runtime.Cue.STAGING_EVIDENCE
const ANOMALY := Runtime.Cue.ANOMALOUS_EVIDENCE
const STARTLE := Runtime.Cue.STARTLE
const PRESSURE := Runtime.Cue.CHRONIC_PRESSURE
const MOTIVES := {A: Runtime.Motive.UNDERSTAND_CUE, B: Runtime.Motive.KEEP_DISTANCE}
const STAY_WEIGHTS := {A: 1, B: 3}

var _failures := 0


func _initialize() -> void:
	var loaded := Loader.load_file(Loader.DEFAULT_PATH)
	_check(loaded.error.is_empty(), "authored fixture loads")
	if _failures == 0:
		var first := _run(loaded.scenario, false)
		_check(first == _run(loaded.scenario, true),
				"same seed and tick inputs reproduce movement, departure and survivor state across speeds")
		_test_decision_at_threshold(loaded.scenario.parameters.required_exit_id)
	if _failures == 0:
		print("PASS: autonomous voluntary departure, legal exit travel, and active-cast isolation")
	quit(0 if _failures == 0 else 1)


func _run(scenario: Dictionary, fast: bool) -> Array:
	var clock := Scheduler.new(21, TICK_USEC, 2, 4)
	var exit_id: StringName = scenario.parameters.required_exit_id
	var start: Vector3i = scenario.cast[A].start_cell
	var example_start: Vector3i = scenario.parameters.navigation_example_start
	var preview_before := _preview(example_start, exit_id)
	var exit_route := House.route_to_exit(start, exit_id)
	_check(exit_route.size() > 2 and exit_route.back() == THRESHOLD,
			"authored exit has a multi-step interior route from the parlor")
	var runtime := Runtime.new(scenario.cast, clock, MOTIVES, {A: [B], B: [A]},
			STAY_WEIGHTS, exit_id)
	runtime.perceive_event(PARLOR_CUE, ANOMALY, [A])
	runtime.perceive_event(STUDY_CUE, PRESSURE, [B])
	runtime.perceive_event(STUDY_CUE, STARTLE, [B])
	runtime.perceive_event(STUDY_CUE, STAGING, [B])
	_check(runtime.consider_sharing_evidence(B, A, STUDY_CUE, STAGING),
			"accepted selective sharing can supply distrust without a startle")
	var a: Dictionary = runtime._actors[A]
	var b: Dictionary = runtime._actors[B]
	var prior_memory: Array = a.memory.duplicate(true)
	if fast:
		clock.set_speed(Scheduler.Speed.FAST)
	var elapsed := TICK_USEC / 2 if fast else TICK_USEC
	clock.advance(elapsed)
	_check(a.fear < b.fear and a.activity == &"leave" and b.activity == &"avoid"
			and a.cell == start and runtime._departed.is_empty(),
			"lower-fear contestant chooses to leave; fearful contestant stays despite knowing the same staging evidence")
	_check(_preview(example_start, exit_id) == preview_before, "no public intent or route projection")

	var trace: Array = [start]
	for i in range(1, exit_route.size()):
		if i == exit_route.size() - 1:
			clock.queue_live_trigger(func() -> bool: return true, func() -> void:
				_check(runtime.present_disturbance(STUDY_CUE), "ongoing event resolves on the arrival tick"))
		var previous: Vector3i = a.cell
		clock.advance(elapsed)
		trace.append(a.cell)
		_check(a.cell == exit_route[i] and House.can_step(previous, a.cell),
				"leaving moves exactly one legal cell on the existing exit route each tick")
		if i < exit_route.size() - 1:
			_check(runtime._actors.has(A) and runtime._departed.is_empty(),
					"route in progress keeps the contestant active")
		if i == 1:
			_check(runtime.consider_sharing_evidence(A, B, PARLOR_CUE, ANOMALY),
					"a departing contestant can still share while walking")

	_check(not runtime._actors.has(A) and runtime._actors.has(B)
			and runtime._departed.get(A, {}).get("departure") ==
			{"kind": &"voluntary_departure", "exit_id": exit_id, "tick": exit_route.size()},
			"arrival removes only A and records ordinary voluntary departure once")
	_check(a.memory.slice(0, prior_memory.size()) == prior_memory and a.memory.back() ==
			{"tick": exit_route.size(), "cell": STUDY_CUE, "cue": STARTLE},
			"departure preserves identity, earlier records, and perception before arrival")
	_check(b.memory.any(func(entry: Dictionary) -> bool: return entry.get("reported_by") == A),
			"other contestants retain evidence attributed to the departed contestant")

	var archived := runtime._departed.duplicate(true)
	var remaining := b.duplicate(true)
	_check(not runtime.perceive_event(PARLOR_CUE, STARTLE, [B, A]) and b == remaining
			and not runtime.consider_sharing_evidence(A, B, PARLOR_CUE, ANOMALY)
			and not runtime.consider_sharing_evidence(B, A, STUDY_CUE, STAGING),
			"departed IDs cannot receive explicit perceptions or participate in contacts")
	_check(runtime.present_disturbance(PARLOR_CUE) and b.memory.back().cell == PARLOR_CUE,
			"shared stimuli still reach the remaining active cast")
	for i in 24:
		clock.advance(elapsed)
		trace.append(b.cell)
	_check(b.cell != remaining.cell or b.activity != remaining.activity,
			"remaining contestant keeps moving or choosing activities")
	_check(runtime._departed.size() == 1 and runtime._departed == archived
			and not runtime._actors.has(A), "later ticks leave one unchanged departure record")
	_check(_preview(example_start, exit_id) == preview_before, "no public departure or private state")
	return [trace, archived, runtime._actors.duplicate(true)]


func _test_decision_at_threshold(exit_id: StringName) -> void:
	var cast: Dictionary[StringName, Dictionary] = {A: {"start_cell": THRESHOLD, "room_id": &"study"}}
	for example: Array in [
		[[STARTLE, PRESSURE], 1, exit_id, false],
		[[STAGING], 1, exit_id, true],
		[[STAGING], 2, exit_id, false],
		[[STAGING, PRESSURE], 2, exit_id, true],
		[[STAGING], 1, &"missing", false],
		[[], 1, exit_id, false],
	]:
		var clock := Scheduler.new(21, TICK_USEC, 2, 4)
		var runtime := Runtime.new(cast, clock, MOTIVES, {}, {A: example[1]}, example[2])
		for cue: Runtime.Cue in example[0]:
			runtime.perceive_event(STUDY_CUE, cue, [A])
		clock.advance(TICK_USEC)
		_check(runtime._departed.has(A) == example[3] and runtime._actors.has(A) != example[3],
				"threshold departure needs a valid choice and exit: %s" % [example])
		if runtime._departed.has(A):
			_check(runtime._departed[A].cell == THRESHOLD and runtime._departed[A].departure.tick == 1,
					"an eligible contestant already at the threshold completes on the decision tick")


func _preview(start: Vector3i, exit_id: StringName) -> String:
	return JSON.stringify([Preview.floor_plan(false, start, exit_id),
			Preview.floor_plan(true, start, exit_id)])


func _check(passed: bool, description: String) -> void:
	if not passed:
		_failures += 1
		push_error("FAIL: " + description)
