extends RefCounted
## Disposable decision rules, not approved contestant psychology or departure mechanics.

var _contestants: Array[Dictionary]
var _rng := RandomNumberGenerator.new()
var _tick := 0


func _init(seed_value: int, initial_contestants: Array[Dictionary]) -> void:
	_rng.seed = seed_value
	_contestants = initial_contestants.duplicate(true)


# Privileged domain output. The fixture's tip is a private exchange between contestants,
# not a producer order. Evaluating actors in fixture order keeps the raw trace ordered.
func step(private_tip: Dictionary = {}) -> Array[Dictionary]:
	_tick += 1
	var events: Array[Dictionary] = []
	if not private_tip.is_empty():
		var listener: Dictionary = _contestants[private_tip.listener_index]
		listener.beliefs.suspects_staging = true
		events.append({
			"tick": _tick, "kind": "private_conversation", "location": "pantry",
			"actor": private_tip.speaker, "listener": listener.id,
			"speech": "I think the disturbance was staged.",
		})

	for contestant in _contestants:
		# The decision to quit terminates this actor's fixture, not their story.
		if contestant.quit_attempted:
			continue
		var action: String
		var destination: String
		var reason: String
		if contestant.beliefs.suspects_staging and not contestant.motive_to_stay:
			action = "attempt_quit"
			destination = "exit_hall"
			reason = "distrust_outweighs_motive"
			contestant.quit_attempted = true
		elif contestant.perceives_danger:
			action = "avoid"
			destination = "common_room"
			reason = "perceived_danger"
		else:
			action = "investigate"
			# Seeded choice only breaks a tie between equivalent leads.
			destination = ["east_landing", "west_landing"][_rng.randi_range(0, 1)]
			reason = "follow_lead"
		events.append({
			"tick": _tick, "kind": "movement", "actor": contestant.id,
			"location": destination, "decision": action,
			"private": {
				"reason": reason, "beliefs": contestant.beliefs.duplicate(true),
				"perceives_danger": contestant.perceives_danger,
				"motive_to_stay": contestant.motive_to_stay,
			},
		})
	return events
