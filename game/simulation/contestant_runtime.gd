extends RefCounted
## Private, scene-free contestant behavior for the authored prototype house.

const Scheduler = preload("res://simulation/event_scheduler.gd")
const House = preload("res://simulation/house_layout.gd")
const ObservationProjector = preload("res://observation/observation_projector.gd")

enum Motive { UNDERSTAND_CUE, KEEP_DISTANCE }
# These describe perceived cues, not the true cause of an event.
enum Cue { STARTLE, ANOMALOUS_EVIDENCE, STAGING_EVIDENCE, CHRONIC_PRESSURE, RELIEF, TELEPHONE_RING }
enum Temperature { COMFORTABLE, HOT, COLD }
enum RingAppraisal { UNEXPLAINED, ANOMALOUS, STAGED }

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
const _THERMAL_LIMIT := 3
const _RING_FAMILIARITY_LIMIT := 2
const _DEFAULT_STAY_MOTIVATION := 3
const _DISTRUST_WEIGHT := 2

var _clock: Scheduler
var _exit_id: StringName
var _actors: Dictionary[StringName, Dictionary] = {}
var _departed: Dictionary[StringName, Dictionary] = {}
var _temperatures: Dictionary[StringName, Temperature] = {}
var _telephone: Dictionary
var _last_ring: Dictionary = {}
var _observations: ObservationProjector


func _init(cast: Dictionary[StringName, Dictionary], clock: Scheduler, motives: Dictionary,
		trusted_contacts: Dictionary = {}, stay_motivations: Dictionary = {},
		exit_id: StringName = &"front", preparations: Dictionary = {},
		observations: ObservationProjector = null) -> void:
	_clock = clock
	_exit_id = exit_id
	_observations = observations if observations != null else ObservationProjector.new([], [])
	# Installed capabilities are supplied at setup; live commands cannot add them.
	for room: StringName in preparations.get("thermostat_rooms", []):
		if House.ROOMS.has(room):
			_temperatures[room] = Temperature.COMFORTABLE
	_telephone = preparations.get("telephone", {}).duplicate()
	for id: StringName in cast:
		_actors[id] = {
			"cell": cast[id].start_cell,
			"motive": motives.get(id, Motive.KEEP_DISTANCE),
			"stay_motivation": stay_motivations.get(id, _DEFAULT_STAY_MOTIVATION),
			"trusted_contacts": trusted_contacts.get(id, []).duplicate(),
			"pending_cue": null,
			"rest_next": cast[id].room_id == &"parlor",
			"activity": &"",
			"route": [] as Array[Vector3i],
			"memory": [],
			"fear": _NATURAL_BASELINE,
			"fear_tick": -1,
			"stress": _NATURAL_BASELINE,
			"effective_stress_baseline": _NATURAL_BASELINE,
			"thermal_baseline": _NATURAL_BASELINE,
			"thermal_load": _NATURAL_BASELINE,
			"synthetic_pressure": _NATURAL_BASELINE,
			"ring_familiarity": 0,
			"ring_appraisal": cast[id].get("ring_appraisal", RingAppraisal.UNEXPLAINED),
			"supernatural_belief": 0,
			"staging_suspicion": 0,
		}
	_clock.schedule_autonomous(_clock.current_tick() + 1, _step)


func camera_snapshot() -> Dictionary:
	return _observations._project_cameras(_clock.current_tick(), _actors)


func take_audible_events() -> Array[Dictionary]:
	return _observations._take_audible_events(_clock.current_tick())


func queue_temperature(room: StringName, setting: Temperature) -> int:
	return _clock.queue_live_trigger(
		func() -> bool: return _temperatures.has(room) and setting in Temperature.values(),
		func() -> void: _temperatures[room] = setting)


func queue_telephone_ring() -> int:
	return _clock.queue_live_trigger(_can_ring, _ring)


func _can_ring() -> bool:
	var cell: Variant = _telephone.get("cell")
	return (cell is Vector3i and House.is_walkable(cell)
			and _telephone.get("disconnected") == true and _telephone.get("ringer_prepared") == true)


func _ring() -> void:
	var cell: Vector3i = _telephone.cell
	var room := House.room_at(cell)
	# The headless acoustic fixture covers the source room only. This event is
	# an audible signal in the world even when no contestant is there to hear it.
	var tick := _clock.current_tick()
	_last_ring = {"kind": &"telephone_ring", "cell": cell, "room": room, "tick": tick}
	_observations._capture_sound(_last_ring, tick)
	var witnesses: Array[StringName] = []
	for id: StringName in _actors:
		if House.room_at(_actors[id].cell) == room:
			witnesses.append(id)
	perceive_event(cell, Cue.TELEPHONE_RING, witnesses)


# The #31 shared fixture explicitly assumes everyone still inside perceived this cue.
func present_disturbance(cell: Vector3i) -> bool:
	return perceive_event(cell, Cue.STARTLE, _actors.keys())


# Trusted simulation input: the caller supplies actual witnesses, not potential
# recipients or producer surveillance coverage. No player-facing command
# supplies witnesses or cue appraisals.
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


# A trusted simulation caller supplies a two-person contact opportunity, not an
# order to speak. This resolves private knowledge only, not surveillance access.
func consider_sharing_evidence(speaker_id: StringName, listener_id: StringName,
		cell: Vector3i, cue: Cue) -> bool:
	if speaker_id == listener_id or not _actors.has(speaker_id) or not _actors.has(listener_id):
		return false
	if cue != Cue.ANOMALOUS_EVIDENCE and cue != Cue.STAGING_EVIDENCE:
		return false
	var speaker: Dictionary = _actors[speaker_id]
	if listener_id not in speaker.trusted_contacts:
		return false
	for entry: Dictionary in speaker.memory:
		# This slice allows sharing retained first-hand evidence, not relaying hearsay.
		if entry.cell == cell and entry.cue == cue and not entry.has("reported_by"):
			_remember(_actors[listener_id], cell, cue, speaker_id)
			return true
	return false


func _remember(actor: Dictionary, cell: Vector3i, cue: Cue, reported_by: StringName = &"") -> void:
	var memory: Array = actor.memory
	if memory.size() == _MEMORY_LIMIT:
		memory.pop_front()
	var entry := {"tick": _clock.current_tick(), "cell": cell, "cue": cue}
	if reported_by != &"":
		entry["reported_by"] = reported_by
	memory.append(entry)
	match cue:
		Cue.STARTLE:
			var spike := _LOADED_STARTLE if actor.stress > _NATURAL_BASELINE else _UNLOADED_STARTLE
			_startle(actor, cell, spike)
		Cue.ANOMALOUS_EVIDENCE:
			actor.supernatural_belief = _EVIDENCE_SUPPORT
		Cue.STAGING_EVIDENCE:
			actor.staging_suspicion = _EVIDENCE_SUPPORT
		Cue.CHRONIC_PRESSURE:
			actor.synthetic_pressure = _PRESSURE_BASELINE
			_update_stress(actor)
		Cue.RELIEF:
			actor.synthetic_pressure = _NATURAL_BASELINE
			_update_stress(actor)
		Cue.TELEPHONE_RING:
			var spike := maxi(1, _UNLOADED_STARTLE + actor.stress - actor.ring_familiarity)
			_startle(actor, cell, spike)
			actor.ring_familiarity = mini(actor.ring_familiarity + 1, _RING_FAMILIARITY_LIMIT)
			match actor.ring_appraisal:
				RingAppraisal.ANOMALOUS:
					actor.supernatural_belief = _EVIDENCE_SUPPORT
				RingAppraisal.STAGED:
					actor.staging_suspicion = _EVIDENCE_SUPPORT


func _startle(actor: Dictionary, cell: Vector3i, spike: int) -> void:
	if spike >= actor.fear:
		actor.fear = spike
		actor.fear_tick = _clock.current_tick()
	# Only the latest perceived startle is pending at the next decision.
	actor.pending_cue = cell


func _update_stress(actor: Dictionary) -> void:
	actor.effective_stress_baseline = maxi(actor.synthetic_pressure, actor.thermal_baseline)
	actor.stress = maxi(actor.synthetic_pressure, actor.thermal_load)


func _update_condition(actor: Dictionary) -> void:
	# Sample the occupied room before this tick's movement, using its live setpoint.
	var room := House.room_at(actor.cell)
	var setting: Temperature = _temperatures.get(room, Temperature.COMFORTABLE)
	var uncomfortable := setting != Temperature.COMFORTABLE
	actor.thermal_baseline = _THERMAL_LIMIT if uncomfortable else _NATURAL_BASELINE
	actor.thermal_load = int(move_toward(actor.thermal_load, actor.thermal_baseline, 1))
	_update_stress(actor)
	if actor.fear > _NATURAL_BASELINE and actor.fear_tick < _clock.current_tick():
		actor.fear -= 1


func _step() -> void:
	# Snapshot the active IDs in cast order so arrivals can remove actors safely.
	for id: StringName in _actors.keys():
		var actor: Dictionary = _actors[id]
		_update_condition(actor)
		var route: Array[Vector3i] = actor.route
		if not route.is_empty():
			actor.cell = route.pop_front()
			actor["last_move_tick"] = _clock.current_tick()
		else:
			_choose(actor)
		if actor.activity == &"leave" and actor.route.is_empty():
			actor["departure"] = {
				"kind": &"voluntary_departure",
				"tick": _clock.current_tick(),
				"exit_id": _exit_id,
			}
			_departed[id] = actor
			_actors.erase(id)
	_clock.schedule_autonomous(_clock.current_tick() + 1, _step)


func _choose(actor: Dictionary) -> void:
	var start: Vector3i = actor.cell
	# Distrust can outweigh the reason to stay. Chronic pressure can tip a
	# close choice, but a startle alone still only prompts a cue reaction.
	var leave_pressure: int = actor.staging_suspicion * _DISTRUST_WEIGHT + actor.stress
	if actor.staging_suspicion > 0 and leave_pressure > actor.stay_motivation:
		var exit_route := House.route_to_exit(start, _exit_id)
		if not exit_route.is_empty():
			_begin(actor, &"leave", exit_route)
			return

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
