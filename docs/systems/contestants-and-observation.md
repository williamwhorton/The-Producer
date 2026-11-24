# Contestants, Knowledge and Observation

**Approved architectural boundary:** [ADR-0004 — Private state and producer observations](../decisions/ADR-0004-producer-observation-boundary.md) (Issue #3; Creative Director approval, 2026-11-23 ET). **Approved house observation baseline:** [ADR-0005 — Hidden cameras, conversation bubbles and one house telephone](../decisions/ADR-0005-house-surveillance-and-communications.md) (Issue #16). Exact dialogue history, call monitoring scope, uncertainty displays, observation schema and producer interventions remain OPEN.

## Goals [CONFIRMED]
Contestants act independently and can infer, investigate, collaborate, conceal information, flee, resist and confront supernatural threats. The producer cannot read their minds.

## Cast-specific personal triggers and producer background [CONFIRMED direction; sourcing OPEN]

Each contestant has **at least one meaningful fear or personal history/association** connected to an object, person, memory or idea. **Available overnight minor-intervention options are derived from those personalized hooks** (e.g., a doll-phobic contestant can be targeted with a doll; someone with a deceased relative may encounter that person's photograph). An option must still be a physically plausible quick nonstructural stage change.

**Producer-facing context must come from a legitimate source.** Casting interviews, vetting or background research could explain knowledge of some historical or personal facts, but the exact source, completeness and dossier/UI are OPEN. Showing a background fact to the producer is **not** the same as showing raw current fear, memories, beliefs or plans from `PrivateContestantState`. ADR-0004 still requires allowlisted source-grounded player views.

Targeting a contestant's known trigger does **not** automatically dictate their action or emotional state. The harder **guaranteed significant consequence** for each offered option remains PROPOSED under A-11; the personal association is now CONFIRMED as the source of candidate interventions (A-12).

## Candidate private model [PROPOSED]
Identity/traits; motives for staying; perceived safety; fear/stress; beliefs about haunting vs production wrongdoing; trust by person; memory of witnessed events; goals/plans; evidence held; knowledge of defensive methods. Do not collapse these into a single omniscient suspicion score.

## Candidate behavior cycle [PROPOSED]
Perceive local events -> update memories/beliefs -> evaluate needs/goals/relationships -> choose action -> emit observable events. Actions include socializing, seeking reassurance, investigating, confronting, cooperating, avoiding, quitting and ritual preparation.

## Observation boundary [REQUIRED design invariant]
`PrivateContestantState` must never be directly serialized to normal player-facing views. Approved [ADR-0004](../decisions/ADR-0004-producer-observation-boundary.md) rejects per-UI direct filtering of world truth in favor of a single **source-mediated observation projector**. The projector creates detached, allowlisted evidence from legitimate sources. **House-wide room cameras and in-house audible/conversation/telephone interactions are now approved sources** (#16/ADR-0005); external testimony and any additional surveillance sources require separate approval. Coverage *outside the rooms* and details of telephone monitoring remain OPEN. Any optional estimate must derive from evidence and must not masquerade as direct access to hidden fear, knowledge, intent or the canonical truth. Hidden private conversations cannot be reported verbatim without an eligible source.

## In-house monitoring and clickable dialogue [CONFIRMED baseline; details OPEN]

The producer can see activity in **every house room** through hidden cameras and can hear relevant house sounds (e.g. opening/closing doors). In-house **conversation bubbles** signal observable speech; clicking a bubble reveals its captured text/details on demand. One shared **house telephone** is available; **cell phones are prohibited**, and using the house phone similarly displays an inspectable bubble. Do not automatically display dialogue text, force speech to reveal a contestant's genuine thoughts, or grant access to the unmonitored remote side of a call without another decision. Exact transcript history, audio presentation and click behavior are UI/pacing decisions (#17/#26).

The producer need not position cameras: this is a **diegetic justification for the all-room dollhouse view**. Internal actors and events still come through the ADR-0004 observation boundary rather than raw simulation state. Interior conversation is **not** considered unmonitored by default under the newly approved house coverage; preserve unmonitored-event privacy tests using off-site or synthetic no-source situations.

## Off-site event vignette implications [PROPOSED]

An external event in a town can exist in the simulation without being automatically shown to the producer. A still-image/text narrative popup is an **UI presentation of source-grounded evidence**, not an omniscient feed from world state. For example, an unmonitored conversation with a shopkeeper is not immediately revealed; a later report from an actual witness or authorized plant could yield a vignette that distinguishes what the witness **claims** from what occurred privately. The pause/resume rules and possible player choices are pending #17/#26, and the precise sources are pending #16.

## Illustrative example
A contestant avoids a hallway. The producer sees the avoidance, but does not know whether it stems from fear, suspicion, interpersonal conflict or coincidence. Further observations can strengthen or weaken hypotheses.

## Test scenarios
- In a **synthetic unmonitored fixture or off-site conversation**, two contestants share evidence privately; without an authorized source the producer receives no report. Under the approved all-room house surveillance, **spoken dialogue inside a room is observable through its conversation bubble**, but the transcript does not expose private belief/intent that was not spoken. Source access must still fail closed outside covered spaces.
- A contestant investigates an apparition and revises their theory without automatically informing other contestants.
- Fearful contestant may remain due to a strong personal motive; low-fear contestant may quit for another reason.
- Contestants form a defensive alliance and attempt a banishment without producer scripting.
- Debug-only trace explains decisions without leaking to release UI.

## Open decisions
Granularity of motives and relationships; sensors and camera coverage; confidence display; player-directed interviews; procedural vs authored dialogue; quitting thresholds; availability of occult knowledge.