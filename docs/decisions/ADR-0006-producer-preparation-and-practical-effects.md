# ADR-0006 — Producer preparation and practical scare interventions

**Status:** APPROVED — high-level Creative Director direction; **specific effect implementations and the nightly-access mechanic remain PROPOSED/OPEN** (2026-11-23, America/New_York)  
**Date:** 2026-11-23  
**Owner:** Creative Director (creative direction); Architect/Lead (design proposal)  
**Issue:** [#16 — Producer actions and surveillance](https://github.com/williamwhorton/The-Producer/issues/16)  
**Related decisions:** [v0.3 vision](../vision.md), [ADR-0004](ADR-0004-producer-observation-boundary.md), [ADR-0005](ADR-0005-house-surveillance-and-communications.md). Supernatural behavior remains under #6 and related work.

## Creative Director's direction — APPROVED principles

The player should have a **broad, physically plausible repertoire**, not be constrained to an exhaustive prewritten list of individual scare buttons. The **producer has prior access to the house** and can arrange its condition and install devices **before contestants arrive**. During the contest, available preinstalled mechanisms can be triggered to manufacture apparent hauntings. Disturbances must have a **plausible in-fiction cause**: a prepared prop, concealed actor, installed device, mechanical action, timed alteration, or later a genuinely supernatural cause. This is a *fictional game-design plausibility standard*, **not** a mandate to realistically engineer each prop or teach real-world fabrication.

### Three distinct action times and agency types

1. **Preparation / pre-contest setup [APPROVED as category]:** The producer selects physical arrangements, props and installed devices in advance. Examples offered by the Creative Director: **squeaky floorboards**, **creepy dolls**, **remotely controlled thermostat**. **Budget is now an APPROVED constraint** on preparation, although exact prices, currency, replenishment and balance remain OPEN. Whether equipment is additionally constrained by a limited selection, availability or progression is **PROPOSED**; placement restrictions, visible clues and repositioning are OPEN.
2. **Triggered effects during the contest [APPROVED as category]:** A producer-available prepared effect can be activated when circumstances warrant. Creative Director examples: **sound effects via hidden speakers**, **rattling windows**, **an unoccupied piano playing**, **flickering lights**; temperature changes via a prepared thermostat are also plausible. These are **examples to explore**, not a fully approved set of devices or individually specified rules. Nothing happens “by magic” simply because the player clicks a room.
3. **Limited covert alterations during the contest [PROPOSED method, not approved mechanic]:** The producer **might be able to enter the house unseen at some point each night** to make minor physical changes. A **bloody knife appearing overnight on a table** is a potential staged-prop example. This can create evidence and uncertainty without requiring a remote-controlled device for every surprise. **Not decided:** whether entry is always possible, its timing/window, risk of discovery, where the producer can go, how alterations are constrained, whether crew/agents can substitute, or whether time must elapse. Do not assume guaranteed safe night access or a nightly free-action allowance.

**Further candidate:** a **holographic/projection-based ghost** may be a manufactured visual effect if a plausible installation/setup and appropriate visual scope are eventually approved. It is **PROPOSED**, not a core mechanic, guaranteed technology, real ghost, or justification for unbounded on-demand apparitions.

**Crucial distinction:** player-operated practical effects are **different from autonomous supernatural phenomena**. Paranormal entities and manifestations may eventually operate independently or disobey the producer (G-05). Do not model every genuine manifestation as a remotely commanded practical-effect device.

## Alternative initial action designs (not chosen as complete gameplay rules)

### A. Preset fixed scare menu

Player chooses a named scare anywhere at any time, e.g. “rattle windows.”

- **Pros:** easy to build, explain and prototype.
- **Cons:** without setup/physical context, turns the producer into an omnipotent ghost; undermines the fiction of a prepared house; weakens strategic choice over preparation and suspicion.
- **Use only if** an actual staged device or valid means of action exists in that location, rather than offering universal room spells.

### B. Fully simulated construction and engineering system

Player individually assembles motors, cables, props, speakers, actuators, power routing, etc., and manually schedules all movements.

- **Pros:** maximizes systemic combinatorics.
- **Cons:** expensive, distracts from horror management into an engineering game, and demands exact physical simulation unsupported by current scope. **Not recommended**.

### C. Prepared capabilities + context-appropriate effect actions (**RECOMMENDED for first design/prototype**)

Before the contest, select a **small number of physically plausible house preparations**; during the contest, trigger effects that those preparations authorize. If a later **covert alteration** method is approved, add a separate action category with distinct fiction and consequences. The simulation decides what contestants notice, believe and do; the player does **not** directly set their emotional state or supernatural entity actions.

- **Pros:** grounded fiction and meaningful setup; game-design room to expand effects without exhaustive item lists or simulating wiring; prepares genuine producer-versus-contestant interplay.
- **Costs:** needs a lightweight capability/location model and explanation of why an intervention is possible. Trigger frequency, setup timing, discovery and resource costs must be balanced later.
- **Status:** **recommended implementation approach, not yet selected as an exact interface, action economy or MVP effect list**.

## Challenge hierarchy and *Orcs Must Die!* reference — newly approved direction

**Creative Director's priority:** For **earlier levels and/or lower difficulty settings**, the **primary challenge should be timing**—recognizing a useful opportunity and triggering a prepared disturbance at the right moment, while contestants continue acting autonomously. The player is observing a social situation, not simply optimizing a damage output or purchasing a perfect trap network.

**Budget is CONFIRMED as a constraint** on preparation: the producer cannot buy/install every potential effect without tradeoffs. **Available equipment may also be constrained [PROPOSED]**—for example by selectable kit, available stock or eventual unlocks; which model is suitable remains OPEN.

The Creative Director cited *Orcs Must Die!* as a **structural design reference**: prepare/place a finite selection of capabilities before live action, then actively use those preparations when circumstances warrant. **Do not import** its wave-defense goal, lethal traps, fixed enemy paths, economy/reward loop, combat, number of loadout slots or escalating waves as approved rules. Here the challenge arises from **human behavior, opportunity windows and competing producer attention**. The *preparation → live timing → consequences* structure is the useful inspiration.

**Design recommendation to test, not a further approved mechanic:** make a low-difficulty scenario forgiving about the number and breadth of prepared tools, while still requiring a good trigger moment (e.g., when a susceptible contestant is nearby, alone, or has just noticed an earlier disturbance). Use a **small clear budget** and possibly limited gear/loadout variety, but avoid making optimization of money/equipment the dominant difficulty at the beginning. Higher difficulties could add tighter budget/stock, more competing conversational or scare opportunities, and stronger contestant counterplay; exact difficulty scaling and timers are OPEN.

**Timing does not necessarily mean twitch-speed clicking.** The precise simulation rate, optional manual pausing, cooldowns, action latency and effect windows remain to be decided under [Issue #17](https://github.com/williamwhorton/The-Producer/issues/17). Design should protect the **meaningful sequencing and attention** challenge without assuming a particular clock model. Once the user selects a scare, its effects must remain dependent on autonomous contestants and the room context rather than guaranteed reactions.

### Early-scenario sketch [ILLUSTRATIVE — not approved content]

- **Prepare:** With a constrained setup budget, put a hidden sound effect in one room and a suspicious household prop in another; equipment availability may constrain choices but is **not yet a mandatory mechanic**.
- **Observe:** Through the all-room surveillance view, notice a contestant approaching the sound-enabled room while someone elsewhere starts a potentially significant conversation.
- **Choose:** Trigger the sound *now*, or keep attention on the conversation and risk losing the scare opportunity. Each option has an opportunity cost.
- **Resolve:** The contestant may investigate, shrug, tell someone, become frightened or even discover staging. The producer cannot select which of these happens.

The central failure mode to avoid is turning early levels into “you needed a better loadout” rather than “you chose the wrong moment.” A very strict budget, scarce kit, cooldown or prewritten wave would need separate evidence and approval.

## A minimal possible conceptual flow (for later #16 selection)

```text
[Pre-contest access]
   -> select plausible house preparations
   -> scenario capabilities (room/device/prop; exact model open)
[Producer observes through approved hidden surveillance]
   -> choose an available prepared effect
   -> game checks whether preparation/context supports that effect
   -> effect occurs in world simulation
   -> contestants notice or miss it and react autonomously
   -> effect/evidence may be investigated and interpreted
[Later: independent supernatural forces may manifest, not as direct player commands]
```

**Example:** If an appropriate hidden sound setup is approved and installed in a room, the player could trigger a disturbing sound there. A contestant might flee, investigate the apparent source, ignore it, or persuade others that it was staged. The producer's selected **effect** is direct control; a contestant's **reaction/belief** is not.

**Overnight alteration example [PROPOSED ONLY]:** a staged object is discovered the next morning after a covert change. How the alteration is performed and what makes it possible or risky remain open.

## Boundaries and future tests

- A nonexistent or unprepared **mundane** effect may not be triggered just because the player selected a room; a preexisting or later-approved supernatural means is distinct.
- Preparations affect available choices but **do not** automatically command contestants; decision tests should demonstrate multiple plausible reactions.
- Contestants can notice a physical sign of staging and interpret it. Exact evidence, detection thresholds and consequences are open.
- The producer cannot invent unobserved inner state from an intervention result. **Observation remains routed through ADR-0004 and ADR-0005**; the approved house surveillance can show visible changes without revealing the cause to contestants or their internal conclusions.
- Any later covert entry/prop placement needs an approved route, timing and risk model; **none is authorized merely by this ADR**.
- **Budget as a preparation constraint and timing as the principal early/lower-difficulty challenge are approved design directions**, but exact costs, gear restrictions, severity, cooldowns, difficulty scaling, initial effects, asset fidelity, implementation, scenario generation, time controls and player tool UX are NOT approved. No implementation test was executed for this design decision.

## Decisions still needed in #16

1. Select the **first tiny action vocabulary** for a vertical slice: what prepared features and triggered interventions make the essential observe → stage → react → adapt loop legible?
2. Is **covert nightly entry** an actual player tool? If so, who enters, what can change, when, and with what consequences?
3. **Budget limits setup [CONFIRMED]**; choose a simple budget model and numeric costs later. Decide whether **equipment stock/loadouts are constrained [PROPOSED]**, and what room/device limits, suspicion, access, cooldowns and feasibility/availability UI are necessary. **Keep early/lower-difficulty balance timing-first [CONFIRMED direction].**
4. May contestants discover/disarm/counter staged effects, and how should this affect continuing operations?
5. How should sound/lighting/effect controls interact with player focus, live dialogue, the proposed house timetable and real supernatural autonomy?

**Recorded scope:** The Creative Director approved the **physical-plausibility and pre-contest preparation direction**, **budget-limited setup**, and **timing-first challenge at early/lower difficulties**, supplying *Orcs Must Die!* as a structural reference. **Equipment availability limits remain a possibility**, not a confirmed rule. The Director supplied example effects and suggested (but did not yet finalize) **covert nighttime changes** and **holographic ghosts**. The specific catalogue of interventions is **deliberately non-exhaustive**. Issue #16 remains **OPEN/In Progress**; no producer gameplay system or detailed mechanic is authorized by this documentation.
