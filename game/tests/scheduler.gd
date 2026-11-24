extends SceneTree

const Scheduler = preload("res://simulation/event_scheduler.gd")


# Private instrumentation lives in this headless fixture, not in the game views.
class Fixture:
	var clock: Scheduler
	var trace: Array[String] = []
	var draws: Array[int] = []
	var value := 7
	var remaining := 1
	var rejected_current_tick := false

	func _init(seed_value: int) -> void:
		# Illustrative test values only: 100 microseconds, 1×/2×/5×.
		clock = Scheduler.new(seed_value, 100, 2, 5)

	func record(label: String) -> void:
		trace.append("%d:%s" % [clock.current_tick(), label])

	func autonomous(label: String) -> void:
		var draw := clock.draw_int(0, 999)
		draws.append(draw)
		value += draw
		record(label)

	func follow_up() -> void:
		autonomous("first")
		rejected_current_tick = not clock.schedule_autonomous(
			clock.current_tick(), autonomous.bind("late same-tick"))
		clock.schedule_autonomous(3, autonomous.bind("follow-up"))

	func can_trigger(label: String) -> bool:
		record("check " + label)
		return remaining > 0

	func trigger(label: String) -> void:
		remaining -= 1
		record(label)

	func evidence() -> Dictionary:
		return {
			"trace": trace,
			"draws": draws,
			"final": {"tick": clock.current_tick(), "value": value, "remaining": remaining},
		}


var _failures := 0


func _initialize() -> void:
	var normal := _run_scenario(12345, false)
	var repeated := _run_scenario(12345, false)
	var accelerated := _run_scenario(12345, true)
	var different_seed := _run_scenario(67890, false)

	_check(normal == repeated, "identical seed, state and commands repeat trace and final state")
	_check(normal == accelerated, "speed, elapsed-time chunks and pause duration do not change results")
	_check(normal.draws != different_seed.draws, "different seed changes actual simulated outcomes")
	_check(normal.trace == [
		"1:check live A", "1:live A", "1:check live C", "1:check live D", "1:live D",
		"1:first", "1:second", "2:check submitted while running", "2:submitted while running",
		"2:middle", "3:already scheduled", "3:follow-up",
	], "tick/phase/insertion order, cancellation, validation and autonomous follow-up")

	if _failures == 0:
		print("PASS: seeded scheduler ordering, tactical pause, live triggers, and speed invariance")
	quit(0 if _failures == 0 else 1)


func _run_scenario(seed_value: int, accelerated: bool) -> Dictionary:
	var fixture := Fixture.new(seed_value)
	var clock := fixture.clock

	# Add events out of chronological order and two autonomous events to tick 1.
	clock.schedule_autonomous(3, fixture.autonomous.bind("already scheduled"))
	clock.schedule_autonomous(1, fixture.follow_up)
	clock.schedule_autonomous(2, fixture.autonomous.bind("middle"))
	clock.schedule_autonomous(1, fixture.autonomous.bind("second"))

	if accelerated:
		clock.set_speed(Scheduler.Speed.FAST)
	clock.advance(20 if accelerated else 40)
	clock.set_paused(true)
	clock.queue_live_trigger(fixture.can_trigger.bind("live A"), fixture.trigger.bind("live A"))
	var cancelled := clock.queue_live_trigger(
		fixture.can_trigger.bind("live B"), fixture.trigger.bind("live B"))
	clock.queue_live_trigger(fixture.can_trigger.bind("live C"), fixture.trigger.bind("live C"))
	clock.queue_live_trigger(_allow.bind(fixture, "live D"), fixture.record.bind("live D"))
	_check(clock.cancel_live_trigger(cancelled), "pending paused command is cancellable")
	_check(not clock.cancel_live_trigger(cancelled), "cancelled command is no longer pending")
	if accelerated:
		clock.set_speed(Scheduler.Speed.VERY_FAST)
	clock.advance(1_000_000 if accelerated else 100)
	_check(clock.current_tick() == 0 and fixture.trace.is_empty() and fixture.remaining == 1,
		"paused elapsed time and queued commands cause no simulation progress")

	clock.set_paused(false)
	clock.advance(11 if accelerated else 55)
	_check(clock.current_tick() == 0 and fixture.trace.is_empty(), "no premature tick after pause")
	clock.advance(1 if accelerated else 5)
	_check(clock.current_tick() == 1, "resume retains the running fraction and reaches the next tick")
	_check(fixture.remaining == 0, "commands revalidate after the earlier command spends the resource")

	clock.queue_live_trigger(
		_allow.bind(fixture, "submitted while running"),
		fixture.record.bind("submitted while running"))
	_check(fixture.trace.size() == 7, "running command waits for the next update")
	if accelerated:
		clock.advance(40)
	else:
		clock.advance(100)
		clock.advance(100)
	_check(clock.current_tick() == 3, "scheduler drains all due ticks without stopping on events")
	_check(fixture.rejected_current_tick and not clock.schedule_autonomous(2, fixture.follow_up),
		"cannot insert events into the current or past tick")
	return fixture.evidence()


func _allow(fixture: Fixture, label: String) -> bool:
	fixture.record("check " + label)
	return true


func _check(passed: bool, description: String) -> void:
	if not passed:
		_failures += 1
		push_error("FAIL: " + description)
