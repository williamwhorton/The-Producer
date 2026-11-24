# Issue #16 — First Producer Actions and Shared Effect Model (DESIGN PROPOSAL)

**Status:** PROPOSED — for Creative Director review; **no new action or numerical psychology mechanic is approved by this document**  
**Scope:** A first tiny action vocabulary and common mechanics that can grow without bespoke psychology code for each new effect  
**Issue:** [#16 — Define producer actions and surveillance](https://github.com/williamwhorton/The-Producer/issues/16)  
**Dependencies:** Approved [ADR-0004](decisions/ADR-0004-producer-observation-boundary.md) (privacy/observation), [ADR-0005](decisions/ADR-0005-house-surveillance-and-communications.md) (house observation/attention), and [ADR-0006](decisions/ADR-0006-producer-preparation-and-practical-effects.md) (untimed budget-limited preparation, physically plausible effects, flat one-slot/night minor alterations and cast dossiers). [Issue #17](https://github.com/williamwhorton/The-Producer/issues/17) must choose actual simulation time control. [Issue #20](https://github.com/williamwhorton/The-Producer/issues/20) remains responsible for MVP scope.

## Objective

Prove that a few recognizable producer actions can create **different outcomes according to timing, location and the witnesses**, while using **one shared causal model**. Do not hand-author a fixed emotion, behavior or success score for each action. The producer **controls physical circumstances**, not contestant thoughts, guaranteed fear, scripted reactions or autonomous supernatural entities.

## Proposed tiny initial action vocabulary

| ID | Action | Category / in-fiction cause | Direct player control | Event delivered to world | Main distinct test |
| --- | --- | --- | --- | --- | --- |
| **P1** | **Squeaky floorboards** | Pre-contest passive modification of a particular area | Choose where to install during **untimed, budget-limited setup**; afterward it activates **when stepped on** | Localized creak; possible nearby/adjacent sound | Ambient/passive effect; context, source visibility and repeated habituation |
| **P2** | **Hidden speaker: knocking/footsteps** | Concealed speaker installed during setup | Select installed room and trigger sound **live**, at an opportune moment | Timed, source-ambiguous sound audible within a plausible area | Producer timing, audible range, witness source attribution and possible investigation |
| **P3** | **Controllable light flicker** | Pre-installed lighting control | Trigger an existing room's lighting disturbance **live** | Brief visible change in illumination in that room | Visual vs audible witnessing; ordinary explanation vs supernatural interpretation |
| **P4** | **Place a personally significant object** | Quick, nonstructural **overnight alteration** selected abstractly from a known contestant dossier hook | Pick the qualifying target and staged prop; **one nightly slot**; carries out unseen | A physical object appears in a plausible spot for later discovery | Delayed perception, personal relevance, consequences beyond fear, and no-hook contestant coverage |

**P4 variants are *content*, not separate mechanics:** A doll staged for someone whose **dossier documents doll phobia**; a deceased relative's photograph for someone with that **known** life event. **Some contestants have no known exploit in their dossier** and therefore do not receive a fabricated P4 hook. They can still be affected by P1–P3 and ordinary events. The available P4 options depend on the cast's known facts and plausible staging circumstances.

### Two bounded vertical-slice options

- **Option A — 3 actions (P1, P2, P4):** One passive audible action, one player-timed audible action, one delayed personal prop. Cheapest first implementation, but **does not test a visual-effect channel**.
- **Option B — 4 actions (P1–P4; RECOMMENDED):** Adds P3 to compare visual vs audible witnesses using **the same effect pipeline**. Slightly more prototype UI/world-effect work; better proof that the shared mechanics generalize.

**Recommendation is NOT approval of any individual action.** All four are candidate starting items. Their purchase prices, prop inventory, cooldowns, durations, audible/visible ranges, lighting intensity, number of nightly slots and difficulty scaling are not selected.

## One reusable action/effect specification (PROPOSED)

For each new action, document these fields. Physical-event generation is separate from witness psychology.

| Field | Meaning |
| --- | --- |
| **Identity / family** | Stable ID and whether this is a setup modification, live prepared trigger, or minor overnight staging |
| **Physical prerequisite / placement** | Which preinstalled device, adjusted structure or dossier-supported quick prop makes this possible, and where |
| **Budget / slot cost** | Setup budget for installed equipment; **one fixed slot per valid minor overnight alteration**. **No new numeric prices or variable effort points here** |
| **Eligibility / time** | When a player can select it; live trigger vs passive activation vs staged overnight result; a scene/room/target must support it |
| **Temporal profile (NEW PROPOSAL)** | Whether a condition is **chronic/ongoing**, **acute/episodic** or an acute event with lasting aftermath. This is **independent of** setup/live/overnight action category |
| **Duration, cessation and aftermath (NEW PROPOSAL)** | How long the physical condition remains and what persists when it stops (e.g., uncomfortable heat vs broken bulb vs remembered fright); no fixed balance numbers |
| **Habituation / repetition (NEW PROPOSAL)** | How cue familiarity and prior explanations change later reactions; distinguish reduced surprise from continuing discomfort and recovery |
| **Acute resistance interaction (CONFIRMED PRINCIPLE)** | Sustained chronic exposure lowers the affected contestant's resistance to subsequent acute effects; actual response remains autonomous. Mechanics for resistance and its recovery are OPEN |
| **World event** | Concrete change with **location, time, duration and perceivable cues** (sound, light, object placement). This occurs even if nobody notices |
| **Witness test** | Which contestants can plausibly see/hear/find it, considering location, sight/hearing, activity and later discovery. Others do **not** automatically learn |
| **Personal interpretation** | Contestant-specific appraisal of the cue based on prior evidence, traits, relationships, **known or private personal associations**, context and explanations |
| **Possible private effects** | Candidate changes to **momentary distress**, **belief that a haunting is real**, **suspicion of human staging**, and **salient memory**. Values/signs are **not** fixed by action identity |
| **Autonomous follow-up** | Individual may investigate, avoid, seek company, tell someone, rationalize, ignore or react otherwise; a producer choice does **not** choose the response |
| **Producer-facing evidence** | Show **the producer's own action, visible world changes, source-grounded movement/behavior, and attended dialogue only**; never reveal raw private numerical beliefs |
| **Repetition / persistence** | Cues and their memory may alter future reactions: repeated ordinary explanations can normalize **surprise**, but ongoing discomfort can remain; patterns may alter belief in ghosts or human staging, and later recovery can be gradual — **all proposed** |
| **Counterexamples / tests** | A no-witness event, different witnesses with different appraisals, repeated uses, missing prerequisite, no dossier hook, delayed discoveries and observation non-leakage |

## Temporal effect profiles, baseline stress and diminishing returns [NEW PROPOSAL — Creative Director exploration]

The Creative Director proposes a distinct classification of **chronic** and **acute** effects, with diminishing returns. **This is orthogonal to producer action categories:** a pre-contest installation can produce an ongoing condition, recurrent ambient cues or an acute remotely triggered event. A staged object can persist in the world but cause an acute **discovery** when a contestant first notices it.

| Candidate example | Temporal role | Physical effect | Proposed mechanics and limits |
| --- | --- | --- | --- |
| **Creaky floorboards (P1)** | **Chronic atmospheric source** emitting individual creaks when walked on | Repeated localized sound under actual footfalls | Ambience and uncertainty at first; **habituation to a recognizable, repeatedly explained cue** reduces its ability to startle. A new context or seemingly source-less sound may still matter |
| **Uncomfortably high or low temperature (NEW)** | **Sustained chronic discomfort** from preinstalled thermostat/controller | Room temperature remains uncomfortable until changed | **Baseline stress/discomfort accumulates or remains elevated** while exposure persists; adaptation may reduce *surprise* without eliminating heat/cold strain. Relief/recovery afterward is a distinct question |
| **Lightbulb popping (NEW)** | **Acute shock with lasting physical aftermath** | A prepared bulb suddenly pops; light is lost and the bulb is spent | Startle and uncertainty for witnesses; room may remain dim, altering subsequent conditions. **A spent bulb cannot simply pop again** without a plausible replacement/reset |
| **Unplugged house telephone ringing (NEW)** | **Acute, apparently impossible signal** | A plausible prepared battery-powered/internal ringer or hidden sound mechanism makes the **one shared house telephone** audibly ring despite visible disconnection | Surprise/uncertainty may affect nearby contestants. This is **a ringing event, not an actual phone call**, so does **not** imply remote speech, a transcript, or a new listening-focus source |
| **Placed doll / relative's photograph (P4)** | **Persistent staged object, acute discovery** | An object remains in the room; discovery occurs later | One-time personal salience upon finding it, possible lingering discomfort/memory; repeated exposure may change interpretation |

**Classification nuance:** A *chronic source* need not make noise continuously. Squeaky boards make **short sounds repeatedly**, collectively shaping ambience. Conversely, an *acute shock* can have durable material consequences (the bulb stays broken) or memory consequences. Do not make "chronic = loop continuously" and "acute = no aftereffects" engine assumptions.

### Proposed minimal psychological dynamics — not equations or approved values

1. **Background load:** a continuing condition (such as unpleasant heat or cold) can gradually raise or maintain baseline stress while experienced. Its contribution should **saturate** or otherwise be bounded rather than grow without limit. When the condition ends, recovery may take time.
2. **Immediate shock:** an acute cue produces a possible short-lived startle/distress response **only for perceiving witnesses**, scaled conceptually by surprise, plausibility, personal relevance, prior evidence and current context. It then decays, though memory and beliefs may persist.
3. **Habituation / diminishing returns:** reactions to a **familiar cue or explanation** can become smaller after repetition. This is **cue/context-specific**, not global immunity to fear or a universal per-click penalty. A fresh cue or changed context can still matter.
4. **Chronic-to-acute interaction (CONFIRMED principle):** chronic pressure **erodes a contestant's ability to resist an acute scare**. Given otherwise comparable circumstances, an exposed, worn-down contestant is more vulnerable to an acute disturbance than they would have been without that pressure. This is **the core strategic synergy** of the two types; exact resistance representation, exposure duration, magnitude and formulas remain OPEN. Contestants may still investigate, rationalize, seek relief or leave instead of becoming afraid.
5. **Separate appraisal from burden:** an occupant may become accustomed to floorboard creaks while remaining physiologically stressed by constant overheating. Similarly, a loud unexplained pop might frighten one person and convince another that the electrical system is unsafe rather than haunted.
6. **Consequences still need autonomous follow-up:** stress, beliefs, memory and possible behavior shifts are not producer-ordered. Chronic stress does **not** directly create a haunting-score payout without a separately approved supernatural progression rule.

**CONFIRMED strategic direction — balance chronic preparation and acute delivery:** the player is meant to **create sustained pressure to lower resilience**, then **recognize and exploit the right moment** for acute interventions. Chronic effects by themselves are not just weak versions of acute scares; they **prepare the psychological conditions in which an acute event can be more powerful**. Equally, triggering acute events with no chronic buildup may be less effective. The challenge is to choose a useful mix and sequence, not maximize one universal fear meter. The actual tradeoff is situational: chronic pressure takes exposure time and may cause contestants to seek relief, investigate, avoid a room or quit; acute effects require timely encounters and repeated use may habituate. These are potential consequences to model, **not predetermined penalties or a fixed optimal ratio**.

**Design recommendation [not selected]:** add a **temporal profile and per-contestant cue familiarity/ongoing exposure** to the proposed shared simulation pipeline, rather than separate scare-specific decay scripts. Use **at least one ongoing environmental condition** to test baseline load, **at least one repeatable cue** to test habituation, and **one discrete shock** to test decay and aftereffects.

### Starter-list implications [OPEN, no automatic scope increase]

The original P1–P4 are still **candidate actions**, not approved or replaced. The new temperature, popping bulb and unplugged-phone ring are **candidate examples** to compare—not three automatically added initial actions. **For the smallest convincing systems slice**, the Creative Director could keep P1 as the repeatable chronic atmosphere example, **substitute thermostat control for one live effect** to test sustained baseline stress, and use **either a popping bulb or a hidden-speaker/telephone sound** as an acute event, retaining dossier-based P4 to exercise deferred discovery. The precise 3–5 action shortlist should be chosen after this mechanical distinction is approved. These examples may also be represented as variants of existing equipment, where physically plausible.

**Physical-world guardrails:** a lightbulb that has popped should leave a changed fixture state until legitimately repaired; a ringing unplugged phone needs a plausible preinstalled standalone ringing device and must not invent actual phone conversation content. No permanent discomfort or endless repeating noise should generate unbounded stress in the absence of sensible attenuation.

### Proposed common simulation pipeline

```text
Producer Action or Prepared Passive Trigger
    -> Validate physical means, phase, location and slot/budget rules
    -> Create concrete WorldEvent(kind, location, time, cue tags, actor/source)
    -> For sustained conditions, evaluate individual exposure and recovery over time
    -> For perceptible cues, each contestant independently NOTICES or MISSES them
    -> Appraise observed events via context, personal relevance and cue familiarity
       (physical discomfort can persist even after cues cease to be surprising)
    -> Chronic exposure lowers resistance to later acute effects (CONFIRMED direction)
    -> Candidate private effects on baseline stress, momentary startle, haunting belief,
       staging suspicion, persistent memory (specific dimensions NOT APPROVED)
    -> Contestant's own goals/needs/relationships drive next actions
    -> Producer sees only permitted source-grounded observations and attended speech
```

**Critical gameplay distinction:** A produced effect **does not directly add “haunting points” merely because the button was clicked**. If distress, fear or sustained memories later contribute to supernatural persistence, that coupling needs a separate design decision. Nothing here overrides the established autonomy of genuinely supernatural entities. A passive effect or missed timed trigger can produce **zero noticed scares**. The proposed guaranteed-significant-consequence rule (A-11) remains undecided; it would have to apply to properly **offered** minor P4 choices without forcing an NPC emotion.

## Qualitative example behavior per action (PROPOSED, not fixed results)

### P1 — Squeaky floorboards (passive)

- **World:** A contestant stepping on prepared boards causes a local creak.
- **Perception:** The person causing it may think it mundane; a different person hearing unexplained footsteps from another room might appraise it as uncanny.
- **Possible effect:** Low direct fright, background tension or curiosity; repeated creaks may normalize, while an unexpectedly unoccupied-sounding room may prompt investigation.
- **Important:** Do **not** auto-trigger a ghostly squeak in a completely empty space without an actual step or another plausible mechanism.

### P2 — Hidden speaker sound (live)

- **World:** Producer triggers an installed knocking/footsteps sound from a chosen room.
- **Perception:** Nearby contestants may hear it; if a clearly visible mundane source explains it, the effect may be weak.
- **Possible effect:** Startle/distress; haunt-belief shift for an unexplained source; investigation may instead uncover indications of staging. Witness proximity, being alone and preceding events influence salience.
- **Important:** If nobody hears it, the producer triggered a sound but has **not** necessarily affected anyone. A sound is not guaranteed to cause fear.

### P3 — Light flicker (live)

- **World:** Existing room lighting flickers briefly.
- **Perception:** Occupants may see it; someone in another room should not automatically gain the same visual evidence.
- **Possible effect:** Startle, nervousness or doubt. One contestant may blame bad wiring; another may see a pattern of apparently supernatural disturbances.
- **Important:** This is not a forced “panic” effect or automatically a loss-of-control/visibility mechanic. Combining it with P2 for a stronger scare is a **future balance possibility**, not approved stacking math.

### P4 — Personalized object placement (overnight)

- **World:** An eligible dossier-derived doll/photo/other simple object is staged unseen and physically present for later discovery; consumes **one** of the approved flat nightly slots.
- **Perception:** The target or another contestant actually has to encounter the object, or credibly learn about it from someone who did. Possible discovery delay matters.
- **Possible effect:** Personal distress, grief, anger, investigation, avoidance, heightened haunting belief or suspicion of a cruel prank, depending on individual history and existing beliefs.
- **Important:** **No obligatory phobia per contestant**, no guaranteed specific reaction and no hard significant-impact promise until A-11 is separately decided. “Staging succeeds unseen” **does not mean** “a target is compelled to notice and fear it.”

## Minimal testable behavior scenarios

1. **Missing preparation:** P2/P3 cannot trigger in a room without the corresponding installed device; P1 cannot exist unless installed pre-contest. No “magic button”.
2. **Timing matters:** P2 while a contestant is nearby may affect them; the same sound played when everyone is away changes the world but leaves **no new witnessed personal event**. No action automatically reads a hidden fear value to tell the player whether it worked.
3. **Distinct perceptions:** A contestant sees P3 from within the room while another elsewhere misses it. Another contestant may later hear a witnessed claim, not receive the full private event retroactively.
4. **Same event, different appraisals:** One witness becomes more inclined toward ghosts, another toward human staging, a third investigates or ignores it. **The game chooses** using private evidence/personality.
5. **Overnight hook and no-hook:** A cast with a known doll phobia has a candidate targeted P4; a contestant without a known exploitable background has **no fabricated personal prop action**. Staging succeeds without stealth; discovery/reaction may be delayed.
6. **Repeat exposures:** A repeatedly explained floorboard creak may normalize; do not blindly add identical fright each time. Moving the trigger to an unexpected context may remain unsettling. Habituation is cue-specific, not global fear immunity.
7. **Persistent discomfort vs habituation:** In a thermostat test scenario, prolonged heat/cold sustains a bounded discomfort load even when occupants stop being surprised by the temperature. Restoring comfort begins recovery rather than immediately erasing all consequences.
8. **Acute shock and aftermath:** A prepared bulb popping creates a discrete witnessed event and a persistent broken/darkened fixture; it cannot be triggered indefinitely on the same bulb. An unplugged telephone ringing is a sound cue with plausible installed cause, **not an attended telephone call or authorized remote-side speech**.
9. **Chronic pressure weakens acute resistance [CONFIRMED principle]:** Replay the same acute noise with otherwise comparable context for a rested contestant and one exposed to sustained discomfort. The second should be more vulnerable to the acute disturbance; **do not** force the same emotional response or reveal hidden resilience in the player UI. Test the boundary where a contestant takes countermeasures, moves to a comfortable area or otherwise changes exposure. The exact attenuation, duration and recovery model is OPEN.
10. **Strategic balance:** A scenario with only chronic disturbances and one with only acute scares should play differently from a thoughtfully sequenced mix. Compare timing and contestant adaptation without assuming a fixed optimal action ratio or guaranteed haunted-house yield.
11. **Observation firewall:** The player sees installed devices and authorized house observations, but **does not see inner emotions, private memories, unobserved conversation text or unattended phone words**. Source-grounded observed speech remains available only when actually attended, under ADR-0005.
12. **Reproducibility:** A seeded simulation plus the same action schedule produces the same event/witness/behavior trace in headless developer tests. Actual GDScript implementation and passing test evidence belong to a later approved issue.

## Remaining Creative Director decisions

- **Approve/modify the starting action set:** **three vs four** (or replace a representative action). Which action is useful for demonstrating the earliest live timing challenge?
- **CONFIRMED strategic direction:** chronic exposure reduces resistance to acute events, and the producer's strategy involves **balancing and sequencing both classes**. **OPEN:** whether the initial implementation needs explicit resilience, threshold modifiers or another representation; what creates/relieves chronic pressure; which diminishing-returns rules apply; how to preserve autonomy and avoid a fixed optimum. Decide whether a thermostat, popped bulb or unplugged-phone ring should substitute for any P1–P4 example.
- **Approve/modify the shared pipeline:** particularly which **minimal private dimensions** to model first; whether baseline discomfort, momentary distress, haunting belief, staging suspicion and event memory need distinct representations from the outset.
- Decide **A-11**: guaranteed meaningful impact for offered P4 choices, or only a strong contextual likelihood; no forced fear behavior.
- Define the **first observable reactions** for prototype testing. Exact weights, cooldowns and effects on haunting persistence remain OPEN.
- Resource numbers, equipment purchase rules, the flat nightly **number**, nightly selection windows, general time controls (#17), prototype room/cast count (#20), UI presentation (#26) remain OPEN.

**This is a decision proposal, not implementation authorization.** Nothing in this document changes approved requirements, commits the player to a particular action menu, or claims executable tests passed.
