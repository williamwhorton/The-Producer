extends SceneTree

const Runtime = preload("res://simulation/contestant_runtime.gd")
const Scheduler = preload("res://simulation/event_scheduler.gd")
const Loader = preload("res://simulation/scenario_loader.gd")
const House = preload("res://simulation/house_layout.gd")
const Preview = preload("res://observation/house_preview.gd")

const TICK_USEC := 100
const CUE := Vector3i(-2, 0, 1)
const A := &"test_a"
const B := &"test_b"
const MOTIVES := {A: Runtime.Motive.UNDERSTAND_CUE, B: Runtime.Motive.KEEP_DISTANCE}
const SWAPPED := {A: Runtime.Motive.KEEP_DISTANCE, B: Runtime.Motive.UNDERSTAND_CUE}

var _failures := 0


func _initialize() -> void:
	var original := Loader.load_file(Loader.DEFAULT_PATH)
	var modified := Loader.load_file("res://tests/fixtures/modified_scenario.json")
	_check(original.error.is_empty() and modified.error.is_empty(), "both scenarios load")
	if _failures == 0:
		_test_authored_runtime(original.scenario)
		_test_motives(original.scenario)
		_test_avoiding_blocked_door(original.scenario.cast)
		var other := Runtime.new(modified.scenario.cast, _new_clock(21), {})
		_check(other._actors.keys() == [&"test_c"]
				and other._actors[&"test_c"].cell == Vector3i(2, 0, 1),
				"modified fixture supplies a different cast and start")
	if _failures == 0:
		print("PASS: authored contestant autonomy, seeded choices, legal movement, and preview isolation")
	quit(0 if _failures == 0 else 1)


func _test_authored_runtime(scenario: Dictionary) -> void:
	var clock := _new_clock(21)
	var runtime := Runtime.new(scenario.cast, clock, MOTIVES)
	_check(runtime._actors.keys() == [A, B], "authored cast IDs and order are retained")
	_check(runtime._actors[A].cell == Vector3i(-3, 0, 2)
			and runtime._actors[B].cell == Vector3i(1, 0, 1), "authored start cells are retained")

	var before := _snapshot(runtime)
	_check(not runtime.present_disturbance(Vector3i(-4, 0, -2))
			and not runtime.present_disturbance(Vector3i(2, 0, 3))
			and _snapshot(runtime) == before, "blocked and exterior cues are ignored")
	clock.advance(TICK_USEC)
	_check(runtime._actors[A].activity == &"rest" and runtime._actors[B].activity == &"read",
			"without a cue the actors choose ordinary activities")
	_check(runtime.present_disturbance(CUE), "walkable cue is accepted during ordinary activities")

	var crossed_door := false
	var saw_investigation := false
	for tick in range(40):
		var previous := _snapshot(runtime)
		clock.advance(TICK_USEC)
		for id: StringName in runtime._actors:
			var actor: Dictionary = runtime._actors[id]
			var from: Vector3i = previous[id].cell
			var to: Vector3i = actor.cell
			_check(House.is_walkable(to) and (from == to or House.can_step(from, to)),
					"tick %d contestant %s stays inside and takes at most one legal step" % [tick, id])
			crossed_door = crossed_door or House.room_at(from) != House.room_at(to)
		var investigator: Dictionary = runtime._actors[A]
		saw_investigation = saw_investigation or investigator.activity == &"investigate"
	_check(crossed_door, "ordinary movement uses the actual doorway")
	_check(saw_investigation and runtime._actors[A].activity in [&"read", &"rest"],
			"the investigation ends and ordinary activities resume without a new cue")


func _test_motives(scenario: Dictionary) -> void:
	var run := _trace(scenario.cast, 21, MOTIVES)
	_check(run == _trace(scenario.cast, 21, MOTIVES), "same seed and inputs repeat every state")
	_check(run == _trace(scenario.cast, 21, MOTIVES, true),
			"same simulation inputs repeat through pause and a faster speed")
	var swapped := _trace(scenario.cast, 21, SWAPPED)
	_check(run[0][A].cell == swapped[0][A].cell and run[0][B].cell == swapped[0][B].cell,
			"motive comparison keeps the environment and starting cells identical")
	_check(run[1][A].activity == &"investigate" and swapped[1][A].activity == &"avoid"
			and run[1][B].activity == &"avoid" and swapped[1][B].activity == &"investigate",
			"swapping only private motives reverses both actors' responses")
	var refuge: Array[Vector3i] = swapped[1][A].route
	_check(not refuge.is_empty() and House.room_at(refuge.back()) == &"study" and CUE not in refuge,
			"the avoidance route leads to the other room without passing the cue")
	var lead: Vector3i = run[2][A].cell
	_check(lead in [Vector3i(-3, 0, 1), Vector3i(-2, 0, 2)],
			"the investigation takes one of the two equally near leads")
	var other := _trace(scenario.cast, 22, MOTIVES)
	_check(other[2][A].activity == &"investigate" and other[2][A].cell != lead
			and other[2][A].cell in [Vector3i(-3, 0, 1), Vector3i(-2, 0, 2)],
			"another seed changes the lead, not the motive or activity")

	var plan := Preview.floor_plan(true, scenario.parameters.navigation_example_start,
			scenario.parameters.required_exit_id)
	_check(plan.keys() == ["rooms", "walls", "exits", "obstacles", "example_route"],
			"the unchanged player projection only contains static plan fields")
	_check(plan.example_route == House.route_to_exit(Vector3i(-3, 0, 2), &"front"),
			"the preview route is the fixed exit example, not either contestant's route")


func _test_avoiding_blocked_door(cast: Dictionary[StringName, Dictionary]) -> void:
	var clock := _new_clock(21)
	var runtime := Runtime.new(cast, clock, SWAPPED)
	var start: Vector3i = runtime._actors[A].cell
	# The only crossing to the refuge would go through the cue.
	_check(runtime.present_disturbance(Vector3i(-1, 0, 0)), "doorway cue is walkable")
	clock.advance(TICK_USEC)
	_check(runtime._actors[A].activity == &"avoid" and runtime._actors[A].route.is_empty()
			and runtime._actors[A].cell == start, "avoider stays put if no safe route exists")
	clock.advance(TICK_USEC)
	_check(runtime._actors[A].activity == &"rest", "waiting is a bounded response")


func _trace(cast: Dictionary[StringName, Dictionary], seed_value: int, motives: Dictionary,
		alternate_pacing := false) -> Array[Dictionary]:
	var clock := _new_clock(seed_value)
	var runtime := Runtime.new(cast, clock, motives)
	var initial := _snapshot(runtime)
	_check(runtime.present_disturbance(CUE), "the same valid cue reaches all actors")
	for id: StringName in initial:
		var actor: Dictionary = runtime._actors[id]
		_check(actor.motive == initial[id].motive and actor.cell == initial[id].cell
				and actor.activity == initial[id].activity and actor.route.is_empty(),
				"the circumstance input cannot set an actor's motive, action, or destination")
	var trace: Array[Dictionary] = [_snapshot(runtime)]
	if alternate_pacing:
		clock.set_paused(true)
		clock.advance(99 * TICK_USEC)
		_check(clock.current_tick() == 0 and _snapshot(runtime) == trace[0],
				"paused contestants neither decide nor move")
		clock.set_speed(Scheduler.Speed.FAST)
		clock.set_paused(false)
	for tick in range(1, 25):
		clock.advance(50 if alternate_pacing else TICK_USEC)
		_check(clock.current_tick() == tick, "each sample corresponds to one simulation tick")
		trace.append(_snapshot(runtime))
	return trace


func _new_clock(seed_value: int) -> Scheduler:
	return Scheduler.new(seed_value, TICK_USEC, 2, 4)


# Privileged test snapshots, never passed to presentation.
func _snapshot(runtime: Runtime) -> Dictionary:
	return runtime._actors.duplicate(true)


func _check(passed: bool, description: String) -> void:
	if not passed:
		_failures += 1
		push_error("FAIL: " + description)
