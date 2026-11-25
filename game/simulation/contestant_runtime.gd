extends RefCounted
## Private, scene-free contestant behavior for the authored prototype house.

const Scheduler = preload("res://simulation/event_scheduler.gd")
const House = preload("res://simulation/house_layout.gd")

enum Motive { UNDERSTAND_CUE, KEEP_DISTANCE }

# Walkable activity spots near the existing furniture, not new scenario properties.
const _REST := Vector3i(-3, 0, 0)
const _READ := Vector3i(2, 0, 0)
const _LEAD_OFFSETS := [Vector3i.RIGHT, Vector3i.BACK, Vector3i.LEFT, Vector3i.FORWARD]

var _clock: Scheduler
var _actors: Dictionary[StringName, Dictionary] = {}
var _cue: Vector3i


func _init(cast: Dictionary[StringName, Dictionary], clock: Scheduler, motives: Dictionary) -> void:
	_clock = clock
	for id: StringName in cast:
		_actors[id] = {
			"cell": cast[id].start_cell,
			"motive": motives.get(id, Motive.KEEP_DISTANCE),
			"cue_pending": false,
			"rest_next": cast[id].room_id == &"parlor",
			"activity": &"",
			"route": [] as Array[Vector3i],
		}
	_clock.schedule_autonomous(_clock.current_tick() + 1, _step)


# A domain input describing a shared circumstance, not a player action or actor order.
# Each actor considers the latest cue once at its next decision point.
func present_disturbance(cell: Vector3i) -> bool:
	if not House.is_walkable(cell):
		return false
	_cue = cell
	for actor: Dictionary in _actors.values():
		actor.cue_pending = true
	return true


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
	if actor.cue_pending:
		actor.cue_pending = false
		if actor.motive == Motive.UNDERSTAND_CUE:
			var reaction := _investigate(start)
			if not reaction.is_empty():
				_begin(actor, &"investigate", reaction)
				return
		else:
			var refuge := _READ if House.room_at(_cue) == &"parlor" else _REST
			var blocked: Array[Vector3i] = []
			if start != _cue:
				blocked.append(_cue)
			# If the cue cuts off the refuge, stay put for this reaction.
			_begin(actor, &"avoid", House.find_route(start, refuge, blocked))
			return

	var rest: bool = actor.rest_next
	actor.rest_next = not rest
	_begin(actor, &"rest" if rest else &"read", House.find_route(start, _REST if rest else _READ))


func _investigate(start: Vector3i) -> Array[Vector3i]:
	var best: Array[Array] = []
	for offset: Vector3i in _LEAD_OFFSETS:
		var lead := _cue + offset
		if not House.can_step(_cue, lead) or House.room_at(lead) != House.room_at(_cue):
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
