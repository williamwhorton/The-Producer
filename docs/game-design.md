# Game Design Overview

## Player role and fantasy [CONFIRMED]
The player orchestrates a deceptive residential prize competition whose concealed purpose is to create an authentic, persistent haunting. The contestants believe they have entered a legitimate contest, but the producer manipulates fear and supernatural conditions behind the scenes. Contestants are autonomous and may attempt to quit, escape, investigate or resist. No genuine television broadcast, public winner, fixed number of days or mandatory body count is required by the approved premise (Issue #1 v0.3).

## Primary loop [PROPOSED]
Observe partial evidence -> plan production interventions -> stage scares/manipulations -> watch autonomous contestant and entity responses -> assess fear, suspicion, retention and psychic yield -> adapt/contain consequences -> invest in supernatural development.

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

The house has **one shared telephone**; cell phones are **not allowed** in the contest. Telephone use has a similar inspectable bubble. How much of a call can be monitored, whether conversation/phone history is retained, whether opening a bubble pauses play and whether contestants can violate the phone ban are still undecided. Do not add camera placement, feed-selection micromanagement or blind spots as mandatory gameplay from this baseline. [ADR-0005](decisions/ADR-0005-house-surveillance-and-communications.md) documents the partial approval.

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