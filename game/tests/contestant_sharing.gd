extends SceneTree

const Runtime = preload("res://simulation/contestant_runtime.gd")
const Scheduler = preload("res://simulation/event_scheduler.gd")
const Loader = preload("res://simulation/scenario_loader.gd")
const Preview = preload("res://observation/house_preview.gd")

const TICK_USEC := 100
const SEED := 21
const A := &"test_a"
const B := &"test_b"
const C := &"test_c"
const PARLOR_CUE := Vector3i(-2, 0, 1)
const STUDY_CUE := Vector3i(1, 0, 1)
const OTHER_CELL := Vector3i(-3, 0, 2)
const ANOMALY := Runtime.Cue.ANOMALOUS_EVIDENCE
const STAGING := Runtime.Cue.STAGING_EVIDENCE
const MOTIVES := {A: Runtime.Motive.UNDERSTAND_CUE, B: Runtime.Motive.KEEP_DISTANCE}

var _failures := 0


func _initialize() -> void:
	var loaded := Loader.load_file(Loader.DEFAULT_PATH)
	var extra := Loader.load_file("res://tests/fixtures/modified_scenario.json")
	_check(loaded.error.is_empty() and extra.error.is_empty(), "authored fixtures load")
	if _failures == 0:
		var cast: Dictionary[StringName, Dictionary] = loaded.scenario.cast.duplicate()
		cast[C] = extra.scenario.cast[C]
		var shared := _exchange(cast, loaded.scenario.parameters, true)
		var repeated := _exchange(cast, loaded.scenario.parameters, true)
		var withheld := _exchange(cast, loaded.scenario.parameters, false)
		_check(shared == repeated and shared != withheld,
				"same seed and contact inputs reproduce the private results; changing trust changes them")
	if _failures == 0:
		print("PASS: selective evidence sharing, attributed memory, recipient isolation, and no public report")
	quit(0 if _failures == 0 else 1)


func _exchange(cast: Dictionary[StringName, Dictionary], parameters: Dictionary,
		a_trusts_b: bool) -> Dictionary:
	var clock := Scheduler.new(SEED, TICK_USEC, 2, 4)
	var contacts := {A: [B] if a_trusts_b else [], B: [A, C]}
	var runtime := Runtime.new(cast, clock, MOTIVES, contacts)
	var start: Vector3i = parameters.navigation_example_start
	var exit_id: StringName = parameters.required_exit_id
	var plain := Preview.floor_plan(false, start, exit_id)
	var with_route := Preview.floor_plan(true, start, exit_id)
	runtime.perceive_event(PARLOR_CUE, ANOMALY, [A])
	runtime.perceive_event(STUDY_CUE, ANOMALY, [A])
	runtime.perceive_event(STUDY_CUE, STAGING, [B])
	clock.advance(TICK_USEC)
	var before := runtime._actors.duplicate(true)
	var a: Dictionary = runtime._actors[A]
	var b: Dictionary = runtime._actors[B]
	_check(before[B].supernatural_belief == 0 and before[A].staging_suspicion == 0,
			"one contestant's direct evidence does not immediately inform the other")

	# Explicit synthetic no-source contact. The cells label the evidence, not
	# the conversation venue; this is not speech in an uncovered house room.
	_check(not runtime.consider_sharing_evidence(A, &"missing", PARLOR_CUE, ANOMALY)
			and not runtime.consider_sharing_evidence(A, A, PARLOR_CUE, ANOMALY)
			and not runtime.consider_sharing_evidence(A, B, PARLOR_CUE, STAGING)
			and not runtime.consider_sharing_evidence(A, B, OTHER_CELL, ANOMALY)
			and not runtime.consider_sharing_evidence(A, C, PARLOR_CUE, ANOMALY)
			and runtime._actors == before, "invalid, unknown-evidence and untrusted offers do not mutate state")
	_check(runtime.consider_sharing_evidence(A, B, PARLOR_CUE, ANOMALY) == a_trusts_b,
			"A's provisional relationship decides whether to share with B")
	if a_trusts_b:
		_check(a == before[A] and b.memory.size() == 2 and b.memory.back() ==
				{"tick": 1, "cell": PARLOR_CUE, "cue": ANOMALY, "reported_by": A}
				and b.supernatural_belief > before[B].supernatural_belief
				and b.staging_suspicion == before[B].staging_suspicion
				and b.fear == before[B].fear and b.stress == before[B].stress,
				"only the selected cue reaches B as a claim, supporting one private theory")
		_check(not runtime.consider_sharing_evidence(B, C, PARLOR_CUE, ANOMALY),
				"a reported cue cannot be passed on as first-hand evidence")
	else:
		_check(runtime._actors == before, "withholding leaves even the intended listener unchanged")

	_check(runtime.consider_sharing_evidence(B, A, STUDY_CUE, STAGING)
			and a.memory.size() == 3 and a.memory.front() ==
			{"tick": 0, "cell": PARLOR_CUE, "cue": ANOMALY}
			and a.memory.back() ==
			{"tick": 1, "cell": STUDY_CUE, "cue": STAGING, "reported_by": B}
			and a.staging_suspicion > before[A].staging_suspicion,
			"reciprocal sharing records the speaker without rewriting the listener's prior witness memory")
	_check(runtime._actors[C] == before[C], "a nonparticipant neither learns nor reacts")
	_check(JSON.stringify(Preview.floor_plan(false, start, exit_id)) == JSON.stringify(plain)
			and JSON.stringify(Preview.floor_plan(true, start, exit_id)) == JSON.stringify(with_route),
			"the no-source exchange changes no producer report, text, or private-state projection")
	return runtime._actors.duplicate(true)


func _check(passed: bool, description: String) -> void:
	if not passed:
		_failures += 1
		push_error("FAIL: " + description)
