extends RefCounted
## The only public-data mapping. Inputs besides the raw events are trusted, synthetic
## capture fixtures supplied outside the simulation, not production sensor rules.


static func project(tick: int, events: Array[Dictionary], captures: Array[Dictionary]) -> Array[Dictionary]:
	var observations: Array[Dictionary] = []
	for capture in captures:
		if not is_same(capture.get("authorized"), true) or not is_same(capture.get("active"), true):
			continue
		if not _has_text(capture.get("source")) or not is_same(capture.get("tick"), tick):
			continue
		var source: String = capture.source
		match capture.get("kind"):
			"sighting":
				if not _has_text(capture.get("location")):
					continue
				for event in events:
					if (event.get("kind") == "movement" and event.get("tick") == tick
							and event.get("location") == capture.location and _has_text(event.get("actor"))):
						observations.append({
							"kind": "sighting", "tick": tick, "source": source,
							"actor": String(event.actor), "location": String(capture.location),
						})
			"testimony":
				# A delivered claim comes from the source, never from the privileged trace.
				if _has_text(capture.get("claim")):
					observations.append({
						"kind": "unverified_claim", "tick": tick, "source": source,
						"claim": String(capture.claim),
					})
	return observations


static func _has_text(value: Variant) -> bool:
	return value is String and not value.strip_edges().is_empty()
