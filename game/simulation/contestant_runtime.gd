extends RefCounted
## Private, scene-free contestant behavior for the authored prototype house.

const Scheduler = preload("res://simulation/event_scheduler.gd")
const House = preload("res://simulation/house_layout.gd")

enum Motive { UNDERSTAND_CUE, KEEP_DISTANCE }
# These describe perceived cues, not the true cause of an event.
enum Cue { STARTLE, ANOMALOUS_EVIDENCE, STAGING_EVIDENCE, CHRONIC_PRESSURE, RELIEF }

# Walkable activity spots near the existing furniture, not new scenario properties.
const _REST := Vector3i(-3, 0, 0)
const _READ := Vector3i(2, 0, 0)
const _LEAD_OFFSETS := [Vector3i.RIGHT, Vector3i.BACK, Vector3i.LEFT, Vector3i.FORWARD]

# Prototype values only: no final memory capacity, psychology scale, or balance.
const _MEMORY_LIMIT := 8
const _NATURAL_BASELINE := 0
const _EVIDENCE_SUPPORT := 1
const _PRESSURE_BASELINE := 1
const _UNLOADED_STARTLE := 2
const _LOADED_STARTLE := 3

var _clock: Scheduler
var _actors: Dictionary[StringName, Dictionary] = {}


func _init(cast: Dictionary[StringName, Dictionary], clock: Scheduler, motives: Dictionary) -> void:
	_clock = clock
	for id: StringName in cast:
		_actors[id] = {
			"cell": cast[id].start_cell,
			"motive": motives.get(id, Motive.KEEP_DISTANCE),
			"pending_cue": null,
			"rest_next": cast[id].room_id == &"parlor",
			"activity": &"",
			"route": [] as Array[Vector3i],
			"memory": [],
			"fear": _NATURAL_BASELINE,
			"stress": _NATURAL_BASELINE,
			"effective_stress_baseline": _NATURAL_BASELINE,
			"supernatural_belief": 0,
			"staging_suspicion": 0,
		}
	_clock.schedule_autonomous(_clock.current_tick() + 1, _step)


# The #31 shared fixture explicitly assumes the whole cast perceived this cue.
func present_disturbance(cell: Vector3i) -> bool:
	return perceive_event(cell, Cue.STARTLE, _actors.keys())


# Trusted simulation input: the caller supplies actual witnesses, not potential
# recipients or producer surveillance coverage. Until perception is implemented
# these are synthetic inputs; no player-facing command feeds this method.
func perceive_event(cell: Vector3i, cue: Cue, witnesses: Array[StringName]) -> bool:
	if not House.is_walkable(cell) or cue not in Cue.values():
		return false
	for id: StringName in witnesses:
		if not _actors.has(id):
			return false
	for id: StringName in _actors:
		if id in witnesses:
			_remember(_actors[id], cell, cue)
	return true


func _remember(actor: Dictionary, cell: Vector3i, cue: Cue) -> void:
	var memory: Array = actor.memory
	if memory.size() == _MEMORY_LIMIT:
		memory.pop_front()
	memory.append({"tick": _clock.current_tick(), "cell": cell, "cue": cue})
	match cue:
		Cue.STARTLE:
			var spike := _LOADED_STARTLE if actor.stress > _NATURAL_BASELINE else _UNLOADED_STARTLE
			actor.fear = maxi(actor.fear, spike)
			# Only the latest perceived startle is pending at the next decision.
			actor.pending_cue = cell
		Cue.ANOMALOUS_EVIDENCE:
			actor.supernatural_belief = _EVIDENCE_SUPPORT
		Cue.STAGING_EVIDENCE:
			actor.staging_suspicion = _EVIDENCE_SUPPORT
		Cue.CHRONIC_PRESSURE:
			actor.effective_stress_baseline = _PRESSURE_BASELINE
			actor.stress = maxi(actor.stress, actor.effective_stress_baseline)
		Cue.RELIEF:
			actor.effective_stress_baseline = _NATURAL_BASELINE
			actor.stress = actor.effective_stress_baseline


func _step() -> void:
	# Authored cast order is stable, including when two actors draw on the same tick.
	for actor: Dictionary in _actors.values():
		var route: Array[Vector3i] = actor.route
		if not route.is_empty():
			actor.cell = route.pop_front()
		else:
			_choose(actor)
	_clock.schedule_autonomous(_clock.current_tick() + 1, _step)


func _choose(actor: Dictionary) -> void:
	var start: Vector3i = actor.cell
	if actor.pending_cue != null:
		var cue: Vector3i = actor.pending_cue
		actor.pending_cue = null
		if actor.motive == Motive.UNDERSTAND_CUE:
			var reaction := _investigate(start, cue)
			if not reaction.is_empty():
				_begin(actor, &"investigate", reaction)
				return
		else:
			var refuge := _READ if House.room_at(cue) == &"parlor" else _REST
			var blocked: Array[Vector3i] = []
			if start != cue:
				blocked.append(cue)
			# If the cue cuts off the refuge, stay put for this reaction.
			_begin(actor, &"avoid", House.find_route(start, refuge, blocked))
			return

	var rest: bool = actor.rest_next
	actor.rest_next = not rest
	_begin(actor, &"rest" if rest else &"read", House.find_route(start, _REST if rest else _READ))


func _investigate(start: Vector3i, cue: Vector3i) -> Array[Vector3i]:
	var best: Array[Array] = []
	for offset: Vector3i in _LEAD_OFFSETS:
		var lead := cue + offset
		if not House.can_step(cue, lead) or House.room_at(lead) != House.room_at(cue):
			continue
		var route := House.find_route(start, lead)
		if route.is_empty():
			continue
		if not best.is_empty() and route.size() < best[0].size():
			best.clear()
		if best.is_empty() or route.size() == best[0].size():
			best.append(route)
	if best.is_empty():
		return []
	# As in #5, the seed only breaks ties between equivalent leads, not motives.
	return best[0] if best.size() == 1 else best[_clock.draw_int(0, best.size() - 1)]


func _begin(actor: Dictionary, activity: StringName, route: Array[Vector3i]) -> void:
	actor.activity = activity
	# #29 routes include the current cell; consume at most one new cell next tick.
	if not route.is_empty():
		route.pop_front()
	actor.route = route
