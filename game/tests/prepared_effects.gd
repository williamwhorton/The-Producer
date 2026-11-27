extends SceneTree

const Runtime = preload("res://simulation/contestant_runtime.gd")
const Scheduler = preload("res://simulation/event_scheduler.gd")
const Loader = preload("res://simulation/scenario_loader.gd")
const Preview = preload("res://observation/house_preview.gd")
const House = preload("res://simulation/house_layout.gd")

const TICK_USEC := 100
const A := &"test_a"
const B := &"test_b"
const SKEPTIC := &"skeptic"
const PARLOR := &"parlor"
const STUDY := &"study"
const PHONE := Vector3i(-2, 0, 1)
const TELEPHONE := {"cell": PHONE, "disconnected": true, "ringer_prepared": true}
const PREPARATIONS := {"thermostat_rooms": [PARLOR], "telephone": TELEPHONE}
const MOTIVES := {A: Runtime.Motive.UNDERSTAND_CUE}

var _failures := 0


func _initialize() -> void:
	var loaded := Loader.load_file(Loader.DEFAULT_PATH)
	_check(loaded.error.is_empty(), "authored house and cast load")
	if _failures == 0:
		var cast: Dictionary[StringName, Dictionary] = loaded.scenario.cast
		_test_invalid(cast)
		_test_unwitnessed(cast)
		_test_departed(cast)
		_test_relief(cast)
		var comfortable := _run(loaded.scenario, Runtime.Temperature.COMFORTABLE, false)
		var hot := _run(loaded.scenario, Runtime.Temperature.HOT, false)
		var cold := _run(loaded.scenario, Runtime.Temperature.COLD, false)
		_check(comfortable[2].a.cell == hot[2].a.cell and hot[2].a.cell == cold[2].a.cell
				and comfortable[3].ring == hot[3].ring and hot[3].ring == cold[3].ring
				and hot[3].a.fear > comfortable[3].a.fear and cold[3].a.fear == hot[3].a.fear,
				"the first otherwise identical ring hits harder with prior heat or cold")
		_check(hot == _run(loaded.scenario, Runtime.Temperature.HOT, true),
				"identical seed and schedule reproduce world, witness and behavior traces across speeds")
		if _failures == 0:
			print("Fixture: first-ring fear comfortable=%d, hot=%d, cold=%d; repeated hot ring=%d" %
					[comfortable[3].a.fear, hot[3].a.fear, cold[3].a.fear, hot[5].a.fear])
			print("PASS: prepared temperature, gradual relief, localized ringing, and private appraisal")
	quit(0 if _failures == 0 else 1)


func _test_invalid(cast: Dictionary[StringName, Dictionary]) -> void:
	for phone: Dictionary in [{}, {"cell": PHONE, "disconnected": true},
			{"cell": PHONE, "disconnected": false, "ringer_prepared": true},
			{"cell": Vector3i(2, 0, 3), "disconnected": true, "ringer_prepared": true}]:
		var clock := _clock()
		var runtime := Runtime.new(cast, clock, MOTIVES, {}, {}, &"front",
				{"thermostat_rooms": [PARLOR, &"missing"], "telephone": phone})
		var control_clock := _clock()
		var control := Runtime.new(cast, control_clock, MOTIVES)
		runtime.queue_temperature(STUDY, Runtime.Temperature.HOT)
		runtime.queue_temperature(&"missing", Runtime.Temperature.COLD)
		runtime.queue_temperature(PARLOR, 99 as Runtime.Temperature)
		runtime.queue_telephone_ring()
		clock.advance(TICK_USEC)
		control_clock.advance(TICK_USEC)
		_check(runtime._temperatures == {PARLOR: Runtime.Temperature.COMFORTABLE}
				and runtime._last_ring.is_empty() and runtime._actors == control._actors,
				"invalid rooms, setting or phone preparation have no world or contestant effect")


func _test_unwitnessed(cast: Dictionary[StringName, Dictionary]) -> void:
	var clock := _clock()
	var away: Dictionary[StringName, Dictionary] = {B: cast[B]}
	var runtime := Runtime.new(away, clock, MOTIVES, {}, {}, &"front", PREPARATIONS)
	runtime.queue_telephone_ring()
	clock.advance(TICK_USEC)
	var b: Dictionary = runtime._actors[B]
	_check(runtime._last_ring == _ring_event(1) and b.memory.is_empty()
			and b.fear == 0 and b.ring_familiarity == 0 and b.activity == &"read",
			"an empty source room still rings, with no automatic effect in the next room")


func _test_departed(cast: Dictionary[StringName, Dictionary]) -> void:
	var clock := _clock()
	var exit_cell: Vector3i = House.EXITS[&"front"][0]
	var at_exit: Dictionary[StringName, Dictionary] = {
		A: {"start_cell": exit_cell, "room_id": STUDY}, B: cast[B]}
	var runtime := Runtime.new(at_exit, clock, MOTIVES, {}, {A: 1}, &"front",
			{"thermostat_rooms": [STUDY],
				"telephone": {"cell": exit_cell, "disconnected": true, "ringer_prepared": true}})
	runtime.perceive_event(exit_cell, Runtime.Cue.STAGING_EVIDENCE, [A])
	clock.advance(TICK_USEC)
	var archived := runtime._departed.duplicate(true)
	runtime.queue_temperature(STUDY, Runtime.Temperature.COLD)
	runtime.queue_telephone_ring()
	clock.advance(TICK_USEC)
	_check(archived.has(A) and runtime._departed == archived
			and runtime._actors[B].memory.back().cue == Runtime.Cue.TELEPHONE_RING
			and runtime._actors[B].stress == 1,
			"active occupants hear and accrue pressure; the archived contestant at the same location does not")


func _test_relief(cast: Dictionary[StringName, Dictionary]) -> void:
	for restore_comfort: bool in [true, false]:
		var clock := _clock()
		var runtime := Runtime.new(cast, clock, MOTIVES, {}, {}, &"front", PREPARATIONS)
		runtime.queue_temperature(PARLOR, Runtime.Temperature.HOT)
		clock.advance(3 * TICK_USEC)
		var a: Dictionary = runtime._actors[A]
		_check(a.stress == 3 and runtime._actors[B].stress == 0,
				"three occupied ticks build bounded pressure only in the hot room")
		if restore_comfort:
			runtime.queue_temperature(PARLOR, Runtime.Temperature.COMFORTABLE)
		else:
			# A's own read routine crosses into the study at tick 7.
			clock.advance(4 * TICK_USEC)
			_check(House.room_at(a.cell) == STUDY and a.stress == 3,
					"autonomous movement leaves the hot room without changing its setpoint")
		for remaining: int in [2, 1, 0]:
			clock.advance(TICK_USEC)
			_check(a.effective_stress_baseline == 0 and a.stress == remaining,
					"relief lowers the target immediately; accumulated load recovers one step per tick")


func _run(scenario: Dictionary, setting: Runtime.Temperature, fast: bool) -> Array:
	var cast: Dictionary[StringName, Dictionary] = scenario.cast.duplicate(true)
	cast[A]["ring_appraisal"] = Runtime.RingAppraisal.ANOMALOUS
	cast[SKEPTIC] = cast[A].duplicate()
	cast[SKEPTIC]["ring_appraisal"] = Runtime.RingAppraisal.STAGED
	var clock := _clock()
	var runtime := Runtime.new(cast, clock, MOTIVES, {}, {SKEPTIC: 9},
			scenario.parameters.required_exit_id, PREPARATIONS)
	var start: Vector3i = scenario.parameters.navigation_example_start
	var exit_id: StringName = scenario.parameters.required_exit_id
	var preview_before := Preview.floor_plan(true, start, exit_id)
	var elapsed := TICK_USEC
	if fast:
		clock.set_speed(Scheduler.Speed.FAST)
		elapsed = TICK_USEC / 2
	clock.set_paused(true)
	var cancelled := runtime.queue_telephone_ring()
	_check(clock.cancel_live_trigger(cancelled), "a queued phone trigger can be cancelled while paused")
	runtime.queue_temperature(PARLOR, setting)
	clock.advance(10 * TICK_USEC)
	_check(runtime._last_ring.is_empty() and clock.current_tick() == 0
			and runtime._temperatures[PARLOR] == Runtime.Temperature.COMFORTABLE,
			"pause freezes the setpoint, ringing and exposure")
	clock.set_paused(false)

	var trace: Array = []
	for tick in range(1, 7):
		if tick in [4, 6]:
			runtime.queue_telephone_ring()
		clock.advance(elapsed)
		trace.append({"ring": runtime._last_ring.duplicate(), "a": runtime._actors[A].duplicate(true),
			"b": runtime._actors[B].duplicate(true), "skeptic": runtime._actors[SKEPTIC].duplicate(true)})

	var first: Dictionary = trace[3]
	var repeated: Dictionary = trace[5]
	_check(trace[0].ring.is_empty() and runtime._temperatures[PARLOR] == setting
			and first.ring == _ring_event(4) and repeated.ring == _ring_event(6),
			"only the two valid running triggers emit localized sound; the setpoint persists")
	_check(first.a.memory == [{"tick": 4, "cell": PHONE, "cue": Runtime.Cue.TELEPHONE_RING}]
			and first.a.supernatural_belief > 0 and first.a.staging_suspicion == 0
			and first.skeptic.supernatural_belief == 0 and first.skeptic.staging_suspicion > 0
			and first.a.fear == first.skeptic.fear
			and first.a.activity == &"investigate" and first.skeptic.activity == &"avoid",
			"the same sound and fear permit contrasting interpretations and autonomous responses")
	_check(first.b.memory.is_empty() and repeated.b.memory.is_empty()
			and first.b.fear == 0 and first.b.stress == 0,
			"the study contestant does not hear the parlor ring or acquire its effects")
	_check(repeated.a.ring_familiarity == 2 and repeated.a.fear < first.a.fear
			and repeated.a.stress == first.a.stress,
			"ring familiarity reduces startle without erasing physical discomfort")
	if setting == Runtime.Temperature.COMFORTABLE:
		runtime.perceive_event(PHONE, Runtime.Cue.STARTLE, [A])
		_check(runtime._actors[A].fear == first.a.fear,
				"ring familiarity does not attenuate a different acute cue")
	_check(Preview.floor_plan(true, start, exit_id) == preview_before,
			"the static projection exposes no sound history, dialogue, or private changes")
	return trace


func _ring_event(tick: int) -> Dictionary:
	return {"kind": &"telephone_ring", "cell": PHONE, "room": PARLOR, "tick": tick}


func _clock() -> Scheduler:
	return Scheduler.new(21, TICK_USEC, 2, 4)


func _check(passed: bool, description: String) -> void:
	if not passed:
		_failures += 1
		push_error("FAIL: " + description)
