# Contestants, Knowledge and Observation

**Approved architectural boundary:** [ADR-0004 — Private state and producer observations](../decisions/ADR-0004-producer-observation-boundary.md) (Issue #3; Creative Director approval, 2026-11-23 ET). **Approved house observation baseline:** [ADR-0005 — Hidden cameras, conversation bubbles and one house telephone](../decisions/ADR-0005-house-surveillance-and-communications.md) (Issue #16). Exact dialogue history, call monitoring scope, uncertainty displays, observation schema and producer interventions remain OPEN.

## Goals [CONFIRMED]
Contestants act independently and can infer, investigate, collaborate, conceal information, flee, resist and confront supernatural threats. The producer cannot read their minds.

## Brief researched dossiers and optional personal vulnerabilities [CONFIRMED]

The producer has **already selected and researched the contestants**. Every contestant has a compact, producer-facing **baseball-card-style dossier** containing a **photo, age, sex, occupation and an extremely brief background**. It mentions a **known exploitable phobia, emotionally significant event or personal association when applicable**. **Some contestants have no known exploitable vulnerability**; their dossiers remain valid. Identifying names are a practical UI detail; no large set of numerical psychology meters is required.

**Authorized source:** the dossier records **producer-gathered pre-contest biographical research**. Those known facts can be exposed to the player without revealing the contestant's **private current fear/stress, intentions, plans, beliefs or internal memory state** from `PrivateContestantState`. ADR-0004's allowlisted, source-mediated observation boundary continues to govern the ongoing house. Completeness/accuracy of dossiers beyond the brief furnished background remains OPEN.

**Intervention eligibility:** personalized overnight options arise from **known dossier hooks where present** (e.g., a doll for someone afraid of dolls; a deceased relative's photograph for someone affected by that loss). **Do not fabricate a hook for every contestant** or require a special nightly action for those without one. Any chosen change must remain quick and nonstructural, using one of the fixed nightly slots and staged unseen. Reactions remain autonomous. Guaranteed significant impact of an *offered* option is still PROPOSED (A-11).

**Future-only option [PROPOSED]:** let the player select/recruit contestants and perform background research. For the initial game, the casting and research have already taken place offscreen.

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