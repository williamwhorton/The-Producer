extends SceneTree
## Fixture v1. Run directly with Godot's --script option.

const Simulation := preload("res://simulation.gd")
const TICKS := 100
const SEED := 12345
const FEAR := 87
const INTENT := "fixture-only private intent"

var _failures := 0


func _initialize() -> void:
	var first := _run(SEED)
	var repeat := _run(SEED)
	var other := _run(67890)
	_test_determinism(first, repeat, other)
	_test_observation(first)

	if "--force-failure" in OS.get_cmdline_user_args():
		_check(false, "intentional assertion failure")
	if _failures == 0:
		print("PASS: determinism and observation isolation (100 ticks)")
	quit(0 if _failures == 0 else 1)


func _run(run_seed: int) -> Simulation:
	var sim := Simulation.new(run_seed, FEAR, INTENT)
	for i in range(TICKS):
		sim.step()
	return sim


func _test_determinism(first: Simulation, repeat: Simulation, other: Simulation) -> void:
	# Direct inspection here is test-only, not part of the player-facing API.
	_check(first._events == repeat._events, "same seed: identical ordered internal events")
	_check(_final_state(first) == _final_state(repeat), "same seed: identical final state")
	_check(first._tick == TICKS, "simulation completes the fixed tick count")
	_check(first._contestant == {"fear": FEAR, "intent": INTENT}, "private fixture exists")
	_check(first._rng.seed == SEED, "explicit fixture seed is used")
	_check(first.get_observation() == repeat.get_observation(), "same seed: identical report")
	# Compare public action sequences; differing seed metadata alone does not count.
	var actions := _actions(first.get_observation())
	var other_actions := _actions(other.get_observation())
	_check(actions.size() == TICKS and other_actions.size() == TICKS, "both action traces are complete")
	_check(actions != other_actions, "different seed changes visible actions")
	print("Public trace, ticks 1–5, seed ", SEED, ": ", actions.slice(0, 5))
	print("Public trace, ticks 1–5, seed 67890: ", other_actions.slice(0, 5))


func _test_observation(sim: Simulation) -> void:
	var report := sim.get_observation()
	var expected: Array[Dictionary] = []
	var ordered_ticks: Array = []
	var hidden_count := 0
	for event in sim._events:
		ordered_ticks.append(event.tick)
		if event.kind == "private_note":
			hidden_count += 1
			_check(event.tick == 3 and event.source == "", "note has no observation source")
			_check(event.internal == {"text": "fixture-only hidden note"}, "private note has content")
		else:
			_check(event.kind in ["turn_left", "turn_right"], "fixture emits a known action")
			_check(event.internal == {
				"contestant": {"fear": FEAR, "intent": INTENT}, "seed": SEED,
			}, "visible events carry nested private data internally")
			expected.append({"tick": event.tick, "kind": event.kind, "source": "fixture_camera"})

	var expected_ticks := range(1, TICKS + 1)
	expected_ticks.insert(3, 3)
	_check(ordered_ticks == expected_ticks, "internal trace is tick-ordered")
	_check(hidden_count == 1, "one hidden event exists in the internal trace")
	if sim._events.size() >= 4:
		_check(sim._events[3].kind == "private_note", "same-tick note follows visible action")
	_check(report.size() == TICKS and report == expected,
		"report contains exactly the sourced actions and allowed scalar fields, in order")

	var serialized := JSON.stringify(report)
	for forbidden in ["fear", "intent", "contestant", "seed", "internal",
			"private_note", "fixture-only hidden note"]:
		_check(not serialized.contains(forbidden), "report does not contain " + forbidden)

	# Arrays/dictionaries are references in GDScript. Mutating the result must not
	# alter the underlying simulation or invalidate another caller's report.
	if not report.is_empty():
		var second_report := sim.get_observation()
		var before := sim._events.duplicate(true)
		report[0]["kind"] = "tampered"
		report.clear()
		_check(sim._events == before, "caller cannot mutate internal event records")
		_check(second_report == expected and sim.get_observation() == expected,
			"callers receive independent arrays and records")


func _final_state(sim: Simulation) -> Array:
	return [sim._tick, sim._contestant, sim._rng.seed, sim._rng.state]


func _actions(report: Array[Dictionary]) -> Array[String]:
	var actions: Array[String] = []
	for event in report:
		actions.append(event.kind)
	return actions


func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: ", message)
