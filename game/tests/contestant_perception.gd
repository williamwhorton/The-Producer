extends SceneTree

const Runtime = preload("res://simulation/contestant_runtime.gd")
const Scheduler = preload("res://simulation/event_scheduler.gd")
const Loader = preload("res://simulation/scenario_loader.gd")
const Preview = preload("res://observation/house_preview.gd")

const TICK_USEC := 100
const PARLOR_CUE := Vector3i(-2, 0, 1)
const STUDY_CUE := Vector3i(1, 0, 1)
const A := &"test_a"
const B := &"test_b"
const MOTIVES := {A: Runtime.Motive.UNDERSTAND_CUE, B: Runtime.Motive.KEEP_DISTANCE}

var _failures := 0


func _initialize() -> void:
	var loaded := Loader.load_file(Loader.DEFAULT_PATH)
	_check(loaded.error.is_empty(), "the authored scenario loads")
	if _failures == 0:
		var cast: Dictionary[StringName, Dictionary] = loaded.scenario.cast
		_test_witnesses(cast)
		_test_private_appraisal(cast)
		_test_chronic_pressure(cast)
		_test_distinct_decisions(cast)
		_test_public_projection(loaded.scenario)
	if _failures == 0:
		print("PASS: private witness memory, separate appraisals, autonomous decisions, and no preview leakage")
	quit(0 if _failures == 0 else 1)


func _test_witnesses(cast: Dictionary[StringName, Dictionary]) -> void:
	var clock := _new_clock()
	var runtime := Runtime.new(cast, clock, MOTIVES)
	var initial := runtime._actors.duplicate(true)
	_check(runtime.perceive_event(PARLOR_CUE, Runtime.Cue.STARTLE, [])
			and runtime._actors == initial, "an unwitnessed event updates nobody")
	_check(not runtime.perceive_event(PARLOR_CUE, Runtime.Cue.STARTLE, [A, &"missing"])
			and runtime._actors == initial, "invalid recipients cause no partial update")
	_check(runtime.perceive_event(PARLOR_CUE, Runtime.Cue.STARTLE, [A, A]),
			"the witnessed startle is accepted")
	var a: Dictionary = runtime._actors[A]
	var b: Dictionary = runtime._actors[B]
	_check(a.memory == [{"tick": 0, "cell": PARLOR_CUE, "cue": Runtime.Cue.STARTLE}]
			and a.fear > initial[A].fear and b == initial[B],
			"only the witness remembers and responds, once per delivery")
	clock.advance(TICK_USEC)
	_check(a.activity == &"investigate" and b.activity == &"read",
			"the unwitnessing actor continues ordinary activity")
	runtime.perceive_event(STUDY_CUE, Runtime.Cue.STAGING_EVIDENCE, [A])
	_check(a.memory.size() == 2 and a.memory.back() ==
			{"tick": 1, "cell": STUDY_CUE, "cue": Runtime.Cue.STAGING_EVIDENCE}
			and b.memory.is_empty(), "private memories survive decision ticks in perception order")
	for _i in range(Runtime._MEMORY_LIMIT):
		runtime.perceive_event(STUDY_CUE, Runtime.Cue.ANOMALOUS_EVIDENCE, [A])
	_check(a.memory.size() == Runtime._MEMORY_LIMIT and a.memory.front().tick == 1
			and a.memory.front().cue == Runtime.Cue.ANOMALOUS_EVIDENCE and b.memory.is_empty(),
			"the memory cap evicts only the oldest entries from the witnessing actor")


func _test_private_appraisal(cast: Dictionary[StringName, Dictionary]) -> void:
	var runtime := Runtime.new(cast, _new_clock(), MOTIVES)
	var a: Dictionary = runtime._actors[A]
	var initial := a.duplicate(true)
	runtime.perceive_event(PARLOR_CUE, Runtime.Cue.STARTLE, [A])
	var fear: int = a.fear
	_check(fear > initial.fear and a.stress == initial.stress
			and a.supernatural_belief == initial.supernatural_belief
			and a.staging_suspicion == initial.staging_suspicion,
			"an unexplained shock increases fear without implying either cause or chronic stress")
	runtime.perceive_event(PARLOR_CUE, Runtime.Cue.ANOMALOUS_EVIDENCE, [A])
	var belief: int = a.supernatural_belief
	_check(belief > initial.supernatural_belief and a.staging_suspicion == initial.staging_suspicion
			and a.fear == fear and a.stress == initial.stress,
			"anomalous evidence supports a haunting without changing other appraisals")
	runtime.perceive_event(STUDY_CUE, Runtime.Cue.STAGING_EVIDENCE, [A])
	_check(a.staging_suspicion > initial.staging_suspicion and a.supernatural_belief == belief
			and a.fear == fear and a.stress == initial.stress,
			"evidence of staging changes suspicion only; both theories can coexist")


func _test_chronic_pressure(cast: Dictionary[StringName, Dictionary]) -> void:
	var runtime := Runtime.new(cast, _new_clock(), MOTIVES)
	var a: Dictionary = runtime._actors[A]
	var b: Dictionary = runtime._actors[B]
	runtime.perceive_event(PARLOR_CUE, Runtime.Cue.CHRONIC_PRESSURE, [A])
	_check(a.stress == a.effective_stress_baseline and a.stress > b.stress and a.fear == b.fear
			and a.supernatural_belief == b.supernatural_belief
			and a.staging_suspicion == b.staging_suspicion,
			"chronic exposure raises the witness's stress baseline, not fear or beliefs")
	runtime.perceive_event(PARLOR_CUE, Runtime.Cue.STARTLE, [A, B])
	_check(a.fear > b.fear and b.fear > 0, "the same startle has a greater effect after exposure")
	var loaded_fear: int = a.fear
	runtime.perceive_event(PARLOR_CUE, Runtime.Cue.RELIEF, [A])
	_check(a.stress == b.stress and a.effective_stress_baseline == b.effective_stress_baseline
			and a.fear == loaded_fear and b.memory.size() == 1,
			"only the exposed actor receives stress relief, which is not fear recovery")


func _test_distinct_decisions(cast: Dictionary[StringName, Dictionary]) -> void:
	var clock := _new_clock()
	var runtime := Runtime.new(cast, clock, MOTIVES)
	var a: Dictionary = runtime._actors[A]
	var b: Dictionary = runtime._actors[B]
	runtime.perceive_event(PARLOR_CUE, Runtime.Cue.STARTLE, [A, B])
	_check(a.fear > 0 and a.fear == b.fear and a.activity == &"" and b.activity == &"",
			"the cue causes equal fear but does not issue an immediate decision")
	clock.advance(TICK_USEC)
	_check(a.activity == &"investigate" and b.activity == &"avoid",
			"equal fear and cue still allow opposite decisions from private motives")

	# Later witnesses must not overwrite the location stored by earlier ones.
	clock = _new_clock()
	runtime = Runtime.new(cast, clock, MOTIVES)
	runtime.perceive_event(PARLOR_CUE, Runtime.Cue.STARTLE, [A])
	runtime.perceive_event(STUDY_CUE, Runtime.Cue.STARTLE, [B])
	clock.advance(TICK_USEC)
	var route: Array[Vector3i] = runtime._actors[A].route
	_check(not route.is_empty() and route.back() in [Vector3i(-3, 0, 1), Vector3i(-2, 0, 2)],
			"the investigator follows a lead at their own cue, not the later unseen cue")


func _test_public_projection(scenario: Dictionary) -> void:
	var runtime := Runtime.new(scenario.cast, _new_clock(), MOTIVES)
	var start: Vector3i = scenario.parameters.navigation_example_start
	var exit_id: StringName = scenario.parameters.required_exit_id
	var plain := Preview.floor_plan(false, start, exit_id)
	var with_route := Preview.floor_plan(true, start, exit_id)
	runtime.perceive_event(PARLOR_CUE, Runtime.Cue.CHRONIC_PRESSURE, [A])
	runtime.perceive_event(PARLOR_CUE, Runtime.Cue.STARTLE, [A])
	runtime.perceive_event(STUDY_CUE, Runtime.Cue.ANOMALOUS_EVIDENCE, [A])
	runtime.perceive_event(STUDY_CUE, Runtime.Cue.STAGING_EVIDENCE, [A])
	var private_state: Dictionary = runtime._actors[A].duplicate(true)
	_check(private_state.memory.size() == 4 and private_state.fear > 0 and private_state.stress > 0
			and private_state.supernatural_belief > 0 and private_state.staging_suspicion > 0,
			"the synthetic no-capture fixture actually populates all private fields")
	var public_view := Preview.floor_plan(true, start, exit_id)
	_check(public_view.keys() == ["rooms", "walls", "exits", "obstacles", "example_route"]
			and JSON.stringify(public_view) == JSON.stringify(with_route)
			and JSON.stringify(Preview.floor_plan(false, start, exit_id)) == JSON.stringify(plain),
			"neither preview mode reveals a private change, event record, or actor route")
	public_view.example_route.clear()
	public_view.exits[0][0] = Vector3i(99, 0, 99)
	_check(runtime._actors[A] == private_state
			and Preview.floor_plan(true, start, exit_id) == with_route,
			"editing the public result changes neither private state nor the next projection")


func _new_clock() -> Scheduler:
	return Scheduler.new(21, TICK_USEC, 2, 4)


func _check(passed: bool, description: String) -> void:
	if not passed:
		_failures += 1
		push_error("FAIL: " + description)
