# Contestants, Knowledge and Observation

## Goals [CONFIRMED]
Contestants act independently and can infer, investigate, collaborate, conceal information, flee, resist and confront supernatural threats. The producer cannot read their minds.

## Candidate private model [PROPOSED]
Identity/traits; motives for staying; perceived safety; fear/stress; beliefs about haunting vs production wrongdoing; trust by person; memory of witnessed events; goals/plans; evidence held; knowledge of defensive methods. Do not collapse these into a single omniscient suspicion score.

## Candidate behavior cycle [PROPOSED]
Perceive local events -> update memories/beliefs -> evaluate needs/goals/relationships -> choose action -> emit observable events. Actions include socializing, seeking reassurance, investigating, confronting, cooperating, avoiding, quitting and ritual preparation.

## Observation boundary [REQUIRED design invariant]
`PrivateContestantState` must never be directly serialized to normal player-facing views. An `ObservationService` receives events through camera/audio/staff/other grounded channels, producing observations with source, timestamp, visibility and uncertainty. A `PerceptionEstimator` may summarize evidence into uncertain ranges or qualitative assessments. Hidden private conversations cannot be reported verbatim without a valid source.

## Illustrative example
A contestant avoids a hallway. The producer sees the avoidance, but does not know whether it stems from fear, suspicion, interpersonal conflict or coincidence. Further observations can strengthen or weaken hypotheses.

## Test scenarios
- Two contestants share evidence privately; production cameras cannot observe content; producer UI receives no private belief update.
- A contestant investigates an apparition and revises their theory without automatically informing other contestants.
- Fearful contestant may remain due to a strong personal motive; low-fear contestant may quit for another reason.
- Contestants form a defensive alliance and attempt a banishment without producer scripting.
- Debug-only trace explains decisions without leaking to release UI.

## Open decisions
Granularity of motives and relationships; sensors and camera coverage; confidence display; player-directed interviews; procedural vs authored dialogue; quitting thresholds; availability of occult knowledge.