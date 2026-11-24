extends RefCounted
## Private simulation clock and event ordering. No scene tree or player-facing output.

enum Speed { NORMAL, FAST, VERY_FAST }

var _rng := RandomNumberGenerator.new()
var _tick_usec: int
var _rates: Array[int]
var _speed := Speed.NORMAL
var _paused := false
var _advancing := false
var _elapsed_sim_usec := 0
var _tick := 0
var _events: Dictionary[int, Array] = {}
var _live_triggers: Dictionary[int, Callable] = {}
var _next_trigger_id := 1


func _init(seed_value: int, tick_usec: int, fast_rate: int, very_fast_rate: int) -> void:
	if tick_usec <= 0 or fast_rate <= 1 or very_fast_rate <= fast_rate:
		push_error("Simulation timing requires a positive tick and increasing speed rates.")
		return
	_rng.seed = seed_value
	_tick_usec = tick_usec
	_rates = [1, fast_rate, very_fast_rate]


func current_tick() -> int:
	return _tick


func set_paused(paused: bool) -> void:
	if not _advancing:
		_paused = paused


func set_speed(speed: Speed) -> void:
	if not _advancing:
		_speed = speed


func draw_int(minimum: int, maximum: int) -> int:
	return _rng.randi_range(minimum, maximum)


func schedule_autonomous(due_tick: int, resolve: Callable) -> bool:
	# Resolvers may schedule follow-up work, but cannot extend the current batch.
	if due_tick <= _tick:
		return false
	var events: Array = _events.get_or_add(due_tick, [])
	events.append(resolve)
	return true


func queue_live_trigger(can_execute: Callable, execute: Callable) -> int:
	var trigger_id := _next_trigger_id
	_next_trigger_id += 1
	_live_triggers[trigger_id] = func() -> void:
		if can_execute.call():
			execute.call()
	return trigger_id


func cancel_live_trigger(trigger_id: int) -> bool:
	return _paused and _live_triggers.erase(trigger_id)


func advance(elapsed_usec: int) -> void:
	if _paused or _advancing or elapsed_usec <= 0 or _tick_usec == 0:
		return
	# Paused wall time is discarded; keep any fractional progress from running.
	_elapsed_sim_usec += elapsed_usec * _rates[_speed]
	_advancing = true
	while _elapsed_sim_usec >= _tick_usec:
		_elapsed_sim_usec -= _tick_usec
		_tick += 1
		_resolve_tick()
	_advancing = false


func _resolve_tick() -> void:
	# Godot dictionaries iterate in insertion order. Detach the current commands
	# so work queued during resolution is eligible on the next tick, not this one.
	var triggers := _live_triggers
	_live_triggers = {}
	for resolve: Callable in triggers.values():
		resolve.call()

	if _events.has(_tick):
		var events: Array = _events[_tick]
		_events.erase(_tick)
		for resolve: Callable in events:
			resolve.call()
