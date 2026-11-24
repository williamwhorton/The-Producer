# Issue #16 — Five Starter Producer Actions and Shared Effect Mechanics

**Status:** PROPOSED STARTING LIST — Creative Director review pending. **Approved principle:** chronic pressure reduces contestants' resistance to acute scares, making their balance and sequencing a core player strategy (S-07). No starter action or balance formula has been individually approved here.  
**Issue:** [#16](https://github.com/williamwhorton/The-Producer/issues/16)  
**Dependencies:** [ADR-0004](decisions/ADR-0004-producer-observation-boundary.md) private/observable boundary; [ADR-0005](decisions/ADR-0005-house-surveillance-and-communications.md) house surveillance, speech and phone; [ADR-0006](decisions/ADR-0006-producer-preparation-and-practical-effects.md) untimed budgeted setup, live prepared effects, unseen overnight changes and compact contestant dossiers. [#17](https://github.com/williamwhorton/The-Producer/issues/17) controls timing/pause; [#20](https://github.com/williamwhorton/The-Producer/issues/20) controls MVP scope.

## Goal

Prove that **a small set of practical effects** drives a common simulation pipeline, instead of attaching pre-scripted fear responses to scare buttons. **All proposed effects operate on the environment.** Contestants independently perceive, interpret, remember and respond to events. An unheard or unseen effect does not automatically grant fear or supernatural progress.

The Creative Director confirmed that **chronic effects erode resistance to acute effects** (S-07); balancing chronic pressure and acute event timing is a central strategy. Exact exposure/decay/resilience numbers, habituation formulas, budget costs and first tool selection remain undecided.

## Recommended initial five actions [PROPOSED — awaiting Creative Director approval]

| ID | Action | Type / activation | Direct effect in world | What it tests |
| --- | --- | --- | --- | --- |
| **P1** | **Creaky floorboards** | **Chronic ambience** — modify selected boards during untimed pre-contest setup; each actual step causes a creak | Repeated localized sounds with plausible footstep sources | **Familiarity/habituation** to a repeated cue, ambient unease, partial hearing and source explanation |
| **P2** | **Remote temperature control** | **Chronic discomfort** — install/prep a thermostat before arrival; during play make an eligible room uncomfortably hot or cold | Sustained temperature state while the setting persists | **Baseline physical stress** and reduced acute resistance despite becoming familiar with the condition; later relief/recovery |
| **P3** | **Unplugged telephone rings** | **Acute auditory anomaly** — prearrange a plausible separate ring/battery/speaker mechanism; player triggers the **single house telephone** ringing even while visibly disconnected | A localized, apparently impossible ring heard by those in range | Startle and **haunting vs staged-prank interpretation**, timing and possible cue-specific habituation on repetition |
| **P4** | **Lightbulb pops** | **Acute visual/auditory shock** — arrange a one-use/otherwise finite plausible prepared mechanism before contestants arrive; trigger live | Sudden pop/flash and **spent bulb**, leaving changed illumination until legitimately fixed | Immediate response vs lasting environmental aftermath, limited one-use availability, visual + audible witness differences |
| **P5** | **Place a personally significant object** | **Overnight staging; acute discovery** — select a quick nonstructural doll/photo/prop derived from a known contestant-dossier hook | Physical prop appears **unseen**, remains until moved/removed, can be discovered later | **Delayed discovery**, personally relevant interpretation, and a special one-slot/night action |

**Why these five?** P1 tests an atmospheric cue that eventually becomes familiar; P2 tests **sustained discomfort** that can still wear a person down after novelty fades. P3 tests repeatable-looking acute sound and anomalous source interpretation; P4 tests a discrete shock with an **irreversible-until-repaired physical consequence** and visible changes. P5 tests the preapproved **separate overnight action economy** and personal relevance. Together they cover **chronic atmosphere + chronic load + acute sound + acute physical shock + personalized delayed discovery** without a larger inventory.

**Deliberately deferred, not discarded:** generic hidden-speaker knocking/footsteps, controllable lighting flickers, rattling windows, piano effects, projection-based figures and other props. The earlier draft PR #87 list of four candidates (floorboards, hidden speaker, light flicker, personalized object) is **superseded by this recommended five-item shortlist** for review. Neither the former nor this replacement was automatically approved. Generic speakers and flickering lights can be added later using the same event template; never silently include them in the starter kit.

**Physical integrity:** The ringing phone is **not an actual incoming call**. It does **not** create a second telephone, remote-side speech or a transcript under ADR-0005. A prepared audible signal is distinct from authorized attended live speech. A popped bulb stays spent and a darkened room remains dark until a plausible repair/replacement; **do not repeatedly pop an intact bulb from nothing**. P1 sounds are caused by actual footsteps; P5 cannot install complex electronics or structural modifications overnight.

**Personalization:** Dossiers exist for all contestants, but **some have no known exploitable hook**. Only a known dossier fact may generate the personalized P5 option; no mandatory personal scare for everyone. The stronger A-11 proposal that every *offered* personalized intervention has a guaranteed significant consequence remains **PROPOSED**; its immediate impact or discovery and reaction are not predetermined.

## Reusable effect template [PROPOSED]

Each future action can be described using one common specification, without hand-authoring a fear change or preferred follow-up:

| Field | Contract to document |
| --- | --- |
| **ID / family** | Stable action ID; **setup/passive**, **live prepared trigger**, or **overnight nonstructural staging** |
| **Temporal profile** | Chronic repeating cue, chronic sustained condition, acute event, or persistent prop with acute discovery; **independent of the action family** |
| **Physical prerequisites** | Prepared device, adjusted fixture or a known dossier prop, including location and reasonable visibility/hearing boundaries |
| **Costs and eligibility** | Setup purchases constrained by **approved budget**; P5 costs **one of a flat number of nightly slots**. Specific prices, other cooldowns and actual quota OPEN |
| **Activation, termination, aftermath** | Step/contact, remote cue, sustained setpoint, one-use failure, overnight placement; when and how it ends and what persists |
| **World event / condition** | What physically happened, where, when, visible/audible properties and duration, **even if nobody notices** |
| **Per-contestant exposure / perception** | Individual conditions and hearing/vision/discovery; never broadcast a witness event to every NPC |
| **Cue familiarity / chronic pressure** | Potential repeated-cue habituation (PROPOSED), ongoing exposure/discomfort and **approved direction that chronic pressure reduces resistance to a later acute event** |
| **Private appraisal / outcomes** | Personal trigger and prior evidence/context affect distress, haunting belief, suspicion of staging, remembered events and autonomous goals. Specific variables and rates OPEN |
| **Observable feedback** | Producer's known actions plus **authorized** events and observations; never a raw private mental-state inspector, instant omniscient fear bar or unattended speech transcript |
| **Test cases** | Missing preparation, no witnesses, contrasting appraisals, repetition, chronic → acute vulnerability, physical aftermath, appropriate source-grounding |

### Common causal pipeline

```text
Producer prepares physical means or places a valid overnight action
    -> World condition changes (possibly sustained) or a concrete event happens
    -> Each contestant experiences physical exposure and/or notices a perceptible cue
    -> Chronic exposure weakens that contestant's resistance to acute shocks
       [CONFIRMED STRATEGIC DIRECTION; numerical representation OPEN]
    -> Witness appraises new cue through history, current context and familiarity
    -> Private distress/beliefs/memories may change (PROPOSED state design)
    -> Contestant autonomously investigates, avoids, talks, seeks relief, stays or leaves
    -> Producer sees only source-authorized house evidence and attended speech
```

**Not all physical conditions are discrete observed scares.** A hot room can continue causing discomfort even if an occupant has stopped finding it surprising. Conversely, an unexplained ringing sound can cause immediate shock but no continuing discomfort. One-off changes may leave durable environmental states or strong memories.

## Chronic/acute interaction [CONFIRMED STRATEGY; detailed mechanics OPEN]

1. **Chronic preparation:** Sustained discomfort or recurrent oppressive cues can wear down an exposed contestant's ability to resist an acute event. The player invests in conditions that make later interventions more consequential. **P2** is the clearest baseline-stress test, while **P1** tests repeated ambience.
2. **Acute opportunity:** The player times **P3/P4** when a vulnerable witness is plausibly nearby. Given otherwise comparable circumstances, a contestant already under chronic pressure is **more susceptible** to a sudden event. Their *actual* reaction still depends on their autonomy, past evidence and personal interpretation.
3. **Diminishing returns [PROPOSED DETAIL]:** Repeated recognizable creaks or the same anomalous ring may become less startling **for that cue**. This is not blanket immunity to different scares. A persistently hot/cold environment can remain uncomfortable after it stops surprising the contestant.
4. **Consequences / counterplay:** Contestants may seek comfortable rooms, repair a light, investigate a phone, provide mundane explanations or leave. Removing a chronic condition may permit **recovery over time** (amount/rate OPEN). A too-strong chronic tactic may drive people to quit before acute scares can exploit their vulnerability—**a candidate emergent consequence, not a fixed rule or penalty**.
5. **No universal optimal ratio:** The producer's challenge is **balance and sequence**, not fill a numerical chronic meter then execute a guaranteed kill/scare combo. There is no approved stacking multiplier, susceptibility equation, minimum exposure duration, fear threshold, instant haunting yield or automatic action success.

## Minimal headless validation scenarios [PROPOSED TESTS, no implementation]

1. **Missing means:** No prepped board = no P1 creak; no thermostat control = no P2; no ringing mechanism = no P3; no prepared bulb mechanism or spent bulb = no P4 retrigger; no dossier hook = no corresponding P5 personalized choice. The producer is not omnipotent.
2. **Low-load/high-load comparison:** Recreate an otherwise identical witnessed P3/P4 event with and without earlier P2 chronic exposure. The prior-exposure contestant shows **greater susceptibility** to the acute event (confirmed principle) without scripting a guaranteed emotion or identical behavior.
3. **Chronic vs habituation:** Repeated floor creaks become more familiar or less surprising under a possible habituation implementation. A room staying too cold can remain physically uncomfortable despite cue familiarity; stress contributions must not grow unbounded.
4. **Perception and timing:** A ringing sound with no nearby listener has no automatically observed psychological effect. A bulb pop in one room can be seen by an occupant and missed visually by someone elsewhere.
5. **World aftermath:** P4 changes the bulb/lighting state until repaired; P3 produces a *ring sound*, not incoming call text, new listening focus or a fake remote participant.
6. **Personalized discovery:** The cast contains a contestant with a dossier-specified hook and one with none. P5 shows the former's plausible prop option; it never invents a new trauma for the latter. The producer stages the object unseen, but discovery and interpretation remain independent.
7. **Different appraisals:** Two witnesses of the same P3 event can lean toward a genuine haunting vs a contrived staging; a contestant may investigate or ignore it. No producer-side “force panic” effect.
8. **Recovery and sequencing:** Allow a contestant to escape chronic P2 exposure, recover gradually if a recovery model is adopted, and later encounter P3/P4. Compare sequences without hard-coding that the combined strategy always wins.
9. **Source firewall:** Dossier facts are known producer research, but actual contestant distress, resilience, beliefs and plans remain private. In-house attended speech is rereadable only when listened to; nothing in the ringing effect fabricates a dialogue record.
10. **Reproducibility:** The same seeded world + action schedule has the same event/witness/behavior traces in developer tests. No Godot code or tests are included in this proposal.

## Decisions remaining

- **Creative Director:** approve or adjust the recommended **five-item shortlist**. The action names, inclusion and exclusions are not settled by writing this document.
- **Core private state:** choose a minimal baseline chronic-load/resilience representation, momentary acute distress, belief/suspicion and memory design. Quantitative details OPEN.
- **S-08:** select a concrete bounded stress, recovery and cue-specific habituation design. This is currently PROPOSED.
- **A-11:** decide whether *offered* dossier-targeted P5 options should guarantee a significant consequence at some future time, versus simply being likely relevant.
- **Other:** preparation prices, equipment availability, bulb reset/repair timing, ring repeatability, eligible nighttime windows, numerical flat nightly quota, general pause/time (#17), specific UI (#26), number of rooms/contestants (#20) and how psychological outcomes influence long-term haunting remain OPEN.

**Design proposal only.** The previously approved rules for producer staging, contestant autonomy and observation remain intact. **No gameplay implementation or executable evidence is claimed.**
