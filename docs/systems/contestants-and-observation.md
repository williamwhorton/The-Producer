# Contestants, Knowledge and Observation

**Proposed implementation boundary:** [ADR-0004 — Private state and producer observations](../decisions/ADR-0004-producer-observation-boundary.md) (Issue #3). **Not yet Creative Director-approved.** G-06's imperfect-knowledge principle is already confirmed; exact surveillance, uncertainty displays and interfaces are not.

## Goals [CONFIRMED]
Contestants act independently and can infer, investigate, collaborate, conceal information, flee, resist and confront supernatural threats. The producer cannot read their minds.

## Candidate private model [PROPOSED]
Identity/traits; motives for staying; perceived safety; fear/stress; beliefs about haunting vs production wrongdoing; trust by person; memory of witnessed events; goals/plans; evidence held; knowledge of defensive methods. Do not collapse these into a single omniscient suspicion score.

## Candidate behavior cycle [PROPOSED]
Perceive local events -> update memories/beliefs -> evaluate needs/goals/relationships -> choose action -> emit observable events. Actions include socializing, seeking reassurance, investigating, confronting, cooperating, avoiding, quitting and ritual preparation.

## Observation boundary [REQUIRED design invariant]
`PrivateContestantState` must never be directly serialized to normal player-facing views. The [ADR-0004 proposal](../decisions/ADR-0004-producer-observation-boundary.md) compares direct filtering against a single **source-mediated observation projector**. The projector would create detached, allowlisted evidence only when a real authorized capture source (potentially a camera, crew report, testimony or other approved channel) explains why the producer knows it. The exact source inventory and observation contents remain **unapproved** under #16. Any optional estimate must derive from evidence and must not masquerade as direct access to hidden fear, knowledge, intent or the canonical truth. Hidden private conversations cannot be reported verbatim without an eligible source.

## Off-site event vignette implications [PROPOSED]

An external event in a town can exist in the simulation without being automatically shown to the producer. A still-image/text narrative popup is an **UI presentation of source-grounded evidence**, not an omniscient feed from world state. For example, an unmonitored conversation with a shopkeeper is not immediately revealed; a later report from an actual witness or authorized plant could yield a vignette that distinguishes what the witness **claims** from what occurred privately. The pause/resume rules and possible player choices are pending #17/#26, and the precise sources are pending #16.

## Illustrative example
A contestant avoids a hallway. The producer sees the avoidance, but does not know whether it stems from fear, suspicion, interpersonal conflict or coincidence. Further observations can strengthen or weaken hypotheses.

## Test scenarios
- Two contestants share evidence privately; production cameras cannot observe content; producer UI receives no private belief update. Source access must fail closed, and a camera observing doorway traffic cannot emit private speech or intent.
- A contestant investigates an apparition and revises their theory without automatically informing other contestants.
- Fearful contestant may remain due to a strong personal motive; low-fear contestant may quit for another reason.
- Contestants form a defensive alliance and attempt a banishment without producer scripting.
- Debug-only trace explains decisions without leaking to release UI.

## Open decisions
Granularity of motives and relationships; sensors and camera coverage; confidence display; player-directed interviews; procedural vs authored dialogue; quitting thresholds; availability of occult knowledge.