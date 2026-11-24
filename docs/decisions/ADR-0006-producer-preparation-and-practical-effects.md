# ADR-0006 — Producer preparation and practical scare interventions

**Status:** APPROVED — high-level Creative Director direction; **specific effect implementations and the nightly-access mechanic remain PROPOSED/OPEN** (2026-11-23, America/New_York)  
**Date:** 2026-11-23  
**Owner:** Creative Director (creative direction); Architect/Lead (design proposal)  
**Issue:** [#16 — Producer actions and surveillance](https://github.com/williamwhorton/The-Producer/issues/16)  
**Related decisions:** [v0.3 vision](../vision.md), [ADR-0004](ADR-0004-producer-observation-boundary.md), [ADR-0005](ADR-0005-house-surveillance-and-communications.md). Supernatural behavior remains under #6 and related work.

## Creative Director's direction — APPROVED principles

The player should have a **broad, physically plausible repertoire**, not be constrained to an exhaustive prewritten list of individual scare buttons. The **producer has prior access to the house** and can arrange its condition and install devices **before contestants arrive**. During the contest, available preinstalled mechanisms can be triggered to manufacture apparent hauntings. Disturbances must have a **plausible in-fiction cause**: a prepared prop, concealed actor, installed device, mechanical action, timed alteration, or later a genuinely supernatural cause. This is a *fictional game-design plausibility standard*, **not** a mandate to realistically engineer each prop or teach real-world fabrication.

### Three distinct action times and agency types

1. **Preparation / pre-contest setup [APPROVED as category]:** The producer selects physical arrangements, props and installed devices in advance. Examples offered by the Creative Director: **squeaky floorboards**, **creepy dolls**, **remotely controlled thermostat**. Whether these are selected from inventory, installed into rooms, require budget, create visible clues or may be repositioned is **OPEN**.
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
- Budget/resource limits, exact initial effects, asset fidelity, implementation, scenario generation, pacing and player tool UX are **not approved**. No implementation test was executed for this design decision.

## Decisions still needed in #16

1. Select the **first tiny action vocabulary** for a vertical slice: what prepared features and triggered interventions make the essential observe → stage → react → adapt loop legible?
2. Is **covert nightly entry** an actual player tool? If so, who enters, what can change, when, and with what consequences?
3. What are the **setup constraints and opportunity costs** (e.g., budgets, room/device limits, suspicion, access, cooldowns) and the feasibility/availability UI?
4. May contestants discover/disarm/counter staged effects, and how should this affect continuing operations?
5. How should sound/lighting/effect controls interact with player focus, live dialogue, the proposed house timetable and real supernatural autonomy?

**Recorded scope:** The Creative Director approved the **physical-plausibility and pre-contest preparation direction**, supplied example effects, and suggested (but did not yet finalize) **covert nighttime changes** and **holographic ghosts**. The specific catalogue of interventions is **deliberately non-exhaustive**. Issue #16 remains **OPEN/In Progress**; no producer gameplay system or detailed mechanic is authorized by this documentation.
