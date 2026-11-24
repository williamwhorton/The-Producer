# Game Design Overview

## Player role and fantasy [CONFIRMED]
The player orchestrates a deceptive residential prize competition whose concealed purpose is to create an authentic, persistent haunting. The contestants believe they have entered a legitimate contest, but the producer manipulates fear and supernatural conditions behind the scenes. Contestants are autonomous and may attempt to quit, escape, investigate or resist. No genuine television broadcast, public winner, fixed number of days or mandatory body count is required by the approved premise (Issue #1 v0.3).

## Primary loop [PROPOSED]
Observe partial evidence -> plan production interventions -> stage scares/manipulations -> watch autonomous contestant and entity responses -> assess fear, suspicion, retention and psychic yield -> adapt/contain consequences -> invest in supernatural development.

## Producer action families [CONFIRMED direction; exact toolkit OPEN]

- **Untimed pre-contest house preparation:** the producer can take **as long as desired before the start** to plan, install equipment, perform structural alterations and arrange props, **within budget**. Deliberately squeaky floorboards or new hidden sound devices must be prepared here and cannot be casually added after contestants arrive. Candidate examples include squeaky floorboards, creepy dolls, a remote thermostat and hidden speakers.
- **During-contest prepared effects:** the producer can trigger **physically supported** disturbances—for example, unsettling sound effects, flickering lights, window rattles or an empty-room piano playing—**provided an appropriate practical means exists**. The mechanism, effect catalogue and action budget are not yet approved. The producer chooses the intervention; contestants choose their response.
- **Small nonstructural interventions during play [CONFIRMED category]:** quick, prank-like alterations such as relocating a doll or staging a bloody-looking knife to appear on a table overnight can occur **while the contest is underway**. They are **separate** from live triggers of installed effects and cannot perform structural work, install complicated devices or remodel rooms. **APPROVED:** select a permitted change from an **abstract/menu action**, then assume it is **successfully carried out unseen**. No stealth gameplay, navigation or chance of being caught placing the prop. **CONFIRMED:** a **flat number of selections per night**, one slot per valid change, with candidate changes balanced for **roughly equal intended effectiveness**. The **numeric limit**, slot expiration/carryover and eligibility windows are OPEN. No separate time/effort points or automatic suspicion penalty limits action capacity. **Comparable intended effect is not identical NPC reaction**; contestants may investigate the result afterward. **PROPOSED refinement:** only offer minor alterations that will **significantly affect at least one contestant**, while leaving the nature of the impact (fear, curiosity, suspicion, investigation or other behavior) to autonomous simulation. Defining significance and guaranteeing a later discovery without scripting NPCs remain OPEN.
- **Further optional effects [PROPOSED]:** projected/holographic apparitions, subject to feasible fiction and an approved small art/effect scope. These are **manufactured illusions**, separate from genuinely autonomous supernatural manifestations.

**Timing should be the primary challenge in early levels/lower difficulties [CONFIRMED direction]**: decide *when* to trigger a prepared effect, taking account of contestant location, behavior and competing observation opportunities. **Budget limits pre-contest setup [CONFIRMED]**, while **limited available equipment/loadouts [PROPOSED]** could add a secondary constraint. The reference is the *Orcs Must Die!* **prepare/position → active intervention** structure, **not** mandatory waves, combat or trap damage. Exact currencies, costs, reaction windows and difficulty scaling are OPEN. A small **prepared-capability + context-sensitive action** model is the recommended starting point, instead of either a magic scare menu or detailed cable-and-motor construction simulation. The Creative Director has approved the physical-plausibility/preparation direction, **not an exhaustive inventory, full mechanic or resource economy**. See [ADR-0006](decisions/ADR-0006-producer-preparation-and-practical-effects.md).

## Pre-researched contestant dossiers and personalized alterations [CONFIRMED direction]

The producer **personally selected and researched the cast before the competition**. The player starts with a **brief baseball-card-style dossier for every contestant**: photo, age, sex, occupation and an extremely short background, including an exploitable phobia or emotionally significant personal history/event **only if known**. **Some contestants have no known exploitable trigger**; they still have dossiers and can react to environmental scares or supernatural events. An elaborate stat card, live mind reading or mandatory player-led research is not the approved starting system.

**Personalized nighttime alteration options derive from known hooks in these dossiers**, e.g., a doll staged for a contestant afraid of dolls, or an unexpected photograph of a deceased relative for someone affected by that death. **Not every contestant needs a personalized action.** Each option must be physically plausible as a quick, nonstructural intervention, executed unseen at one flat nightly slot. NPC responses remain autonomous, and the idea that every *offered* choice causes a guaranteed significant effect remains **PROPOSED (A-11)**.

The dossier is an authorized **pre-contest research source** for known biographical facts; it cannot reveal a contestant's present private emotions, thoughts or plans (ADR-0004). **Future-only PROPOSAL:** cast selection and background research become strategic mechanics. The initial game **already has a selected roster and the prepared dossiers**, without requiring a recruitment or research phase. See A-12–A-14 and ADR-0006.

## Tension model [PROPOSED]
- Fear may contribute to haunting formation, but may also trigger attempted withdrawal/escape, panic, investigation or defensive cooperation. Whether deaths or a minimum fear threshold are required remains OPEN.
- Suspicion of **production wrongdoing** is distinct from belief in a **real haunting**.
- The producer can plan and stage mundane effects; emerging supernatural entities may act without permission.
- Contestants can thwart, avoid or neutralize supernatural assets.
- Greater supernatural power increases capability and loss-of-control risk.

## Time and pacing [OPEN/PROPOSED]
A pausable real-time simulation with adjustable speed is a candidate, not a commitment. Ordinary activities, interpersonal friction and downtime are essential to tonal contrast. Avoid constant scares.

## Seasons [CONFIRMED]
Each season has a distinct house, cast and scenario. Example settings: rural farmhouse, suburban mansion, urban high-rise penthouse. They create different sightlines, surveillance constraints, isolation, public exposure and logistical options. Contestants differ in resilience, skepticism, social influence and reasons to stay.

## Cross-season progression [CONFIRMED concept; PROPOSED implementation]
Some skills, tools, occult knowledge or artifacts may carry over. Haunted objects can be recovered and brought to a new site to seed activity or offer specialized powers. They must remain optional and context-sensitive; horizontal variety is preferable to mandatory power creep. Artifact creation rules, inventory size, drawbacks and acquisition are OPEN.

## Supernatural progression [PROPOSED]
Manufactured horror -> early genuine manifestations -> autonomous entities and environmental influence -> potentially powerful independent haunting. These are conceptual stages, not a fixed unlock tree.

## Contestant agency [CONFIRMED]
Contestants can form private beliefs and alliances, share or withhold information, investigate, flee, cooperate, defend themselves, and attempt to exorcise/banish or neutralize supernatural threats. Success must not depend solely on scripted scenes.

## House observation and communications [CONFIRMED baseline from #16]

Hidden cameras grant full visibility into **every house room**, providing an in-world explanation for the fixed-angle dollhouse display. The producer can hear noises such as doors opening/closing. When contestants speak, an **on-screen conversation bubble** appears; the player must **click** it to see the text/details of the spoken exchange. Speech is not automatically printed and need not truthfully reflect a contestant's private belief.

The house has **one shared telephone**; cell phones are **not allowed** in the contest. Telephone use has a similar inspectable bubble. **Conversation listening is selective and live:** when two contestants/groups are talking, the producer must decide which conversation to follow and **cannot retrieve a transcript of an unattended conversation afterward**. Focusing a bubble does not automatically pause the simulation. **Attended-only text history is approved:** the player can reread at any time the words actually followed, including the observed portion of phone calls. The single listening focus is **shared between house conversations and the phone**; attending one means missing simultaneous speech elsewhere. **Surveillance video/audio cannot be replayed**, and no auto-generated all-conversation history exists. Adding video recording could be a future mechanic but is **not approved**. Exact phone remote-side coverage, manual/global pause options, archive UI and possible ban violations remain undecided. Do not add camera placement, feed-selection micromanagement or blind spots as mandatory gameplay from this baseline. [ADR-0005](decisions/ADR-0005-house-surveillance-and-communications.md) documents the partial approval.

The approved ADR-0004 observation projector remains in effect; **complete room visibility does not equal omniscience about minds or off-site events**.

## Off-site events as narrative vignettes [PROPOSED]

Instead of building a navigable 3D town, consider **self-contained still-image-and-text event dialogs** for town visits and other off-site developments, modeled on Paradox event pop-ups and *Rogue Trader*-style choice interludes. A short description and static illustration communicate context; the event may provide **a meaningful player choice or simply convey information**. It may pause the game while the player reads or resolves it, but pause/trigger rules belong to the separate pacing decision (#17).

Example possibilities, **not confirmed scripted events**: a contestant talks to a suspiciously well-informed shopkeeper; a local newspaper prints a rumor about the estate; a contestant returns with an ambiguous account of an interaction downtown; a planted local reports whether the house's reputation is spreading. These should remain grounded in believable channels of knowledge.

Architectural intent: game systems produce the event and determine consequences; the observation/application layer decides what the producer can legitimately learn and which interventions are offered; a UI modal renders the text/image and any choices. Neither a free-roaming town nor renderer-specific 3D nodes are prerequisites. The exact off-site mechanics, choices, art cost, real-time pause semantics and information-leakage restrictions must be tested/approved under #26, #17, #3 and #20. **No new mechanic is approved by Issue #1.**

## Information interface [CONFIRMED principle; PROPOSED details]
Player-facing estimates of stress/fear/suspicion may exist, but should be uncertain, sourced and observational. The player should infer conspiracy from actions and evidence. Private conversations outside surveillance should not magically appear in production reports.

## Outcomes and season resolution [MIXED]
**Primary win objective [CONFIRMED]:** create a genuine haunting that persists after the deceptive operation ends and its organizers depart. The persistence threshold, verification method, death requirements and allowable degrees of success remain OPEN.

**Continuity/exposure direction [CONFIRMED]:** attempts to run future deceptive contests cannot ignore contestant fates, local rumor, witnesses, family concerns or external investigation. How the organization endures, conceals or fails after an operation remains OPEN; **no credible broadcast TV franchise is required**.

**Survivors, deaths and winners [OPEN]:** whether anyone must survive, contestants must all die, a participant wins a promised prize, or death is necessary for haunting success are not approved gameplay rules.

**Departures, “removal,” deaths and witnesses [OPEN]:** distinguish voluntary withdrawals and escapes from enforced rule-related removals, deaths and unresolved disappearances; do not assume every removal is death. Contestants and people outside the house have differing partial knowledge; no universal cover-up, death quota or psychic-energy conversion rule is approved. **Original story seed [PROPOSED]:** 30-day stay, 8 PM–6 AM room restriction, large cash/house reward, frightening unexplained removals, and daytime town rumors (see `vision.md`).

Track haunted-location outcome and **operation-continuity/exposure** separately, allowing partial successes and consequential failures. See `systems/season-outcomes-and-continuity.md`.