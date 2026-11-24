# ADR-0006 — Producer preparation and practical scare interventions

**Status:** APPROVED — high-level Creative Director direction, including **unseen execution and flat per-night minor-action slots**; numeric quota/timing and specific effect set remain OPEN (2026-11-23, America/New_York)  
**Date:** 2026-11-23  
**Owner:** Creative Director (creative direction); Architect/Lead (design proposal)  
**Issue:** [#16 — Producer actions and surveillance](https://github.com/williamwhorton/The-Producer/issues/16)  
**Related decisions:** [v0.3 vision](../vision.md), [ADR-0004](ADR-0004-producer-observation-boundary.md), [ADR-0005](ADR-0005-house-surveillance-and-communications.md). Supernatural behavior remains under #6 and related work.

## Creative Director's direction — APPROVED principles

The player should have a **broad, physically plausible repertoire**, not be constrained to an exhaustive prewritten list of individual scare buttons. The **producer has prior access to the house** and can arrange its condition and install devices **before contestants arrive**. During the contest, available preinstalled mechanisms can be triggered to manufacture apparent hauntings. Disturbances must have a **plausible in-fiction cause**: a prepared prop, concealed actor, installed device, mechanical action, timed alteration, or later a genuinely supernatural cause. This is a *fictional game-design plausibility standard*, **not** a mandate to realistically engineer each prop or teach real-world fabrication.

### Three distinct action times and agency types

1. **Preparation / pre-contest setup [APPROVED as category]:** The producer has **unlimited setup/planning time before contestants arrive**; there is no setup countdown. The producer chooses physical arrangements, props and devices in advance. **Structural or complex installation, such as deliberately squeaky floorboards, belongs to this phase only**, not the running contest. Untimed setup is **still budget-limited**. Examples offered by the Creative Director: **squeaky floorboards**, **creepy dolls**, **remotely controlled thermostat**. **Budget is now an APPROVED constraint** on preparation, although exact prices, currency, replenishment and balance remain OPEN. Whether equipment is additionally constrained by a limited selection, availability or progression is **PROPOSED**; placement restrictions, visible clues and repositioning are OPEN.
2. **Triggered effects during the contest [APPROVED as category]:** Previously installed or prepared effects can be activated while play is underway, when circumstances warrant. Triggering an effect does **not** install a new device or perform structural work. Creative Director examples: **sound effects via hidden speakers**, **rattling windows**, **an unoccupied piano playing**, **flickering lights**; temperature changes via a prepared thermostat are also plausible. These are **examples to explore**, not a fully approved set of devices or individually specified rules. Nothing happens “by magic” simply because the player clicks a room.
3. **Small alterations during play [APPROVED category and flat nightly slots; count/windows OPEN]:** The producer can stage **minor, quick, nonstructural, prank-like changes** while the contest is running, such as a **bloody knife appearing on a table overnight** or a moved prop. Changes in this category should be plausibly achievable quickly by **one person**, not require structural renovation or complicated equipment installation. **APPROVED:** a valid selection is **executed unseen by assumption**, with **no stealth sequence or chance of being caught during the alteration**. The producer's prior access, preparation and clandestine competence are sufficient in-fiction. **APPROVED nightly limit:** a fixed **number of minor selections per night**, with **each qualifying alteration consuming one slot**. For balancing purposes, the candidate alterations should have **comparable intended effectiveness** rather than different time, effort or action-point costs. The **numeric limit**, eligible nighttime window, rollover of unused slots and exact effect balance remain OPEN. There is no need to simulate who walked where.

**Further candidate:** a **holographic/projection-based ghost** may be a manufactured visual effect if a plausible installation/setup and appropriate visual scope are eventually approved. It is **PROPOSED**, not a core mechanic, guaranteed technology, real ghost, or justification for unbounded on-demand apparitions.

**Crucial distinction:** player-operated practical effects are **different from autonomous supernatural phenomena**. Paranormal entities and manifestations may eventually operate independently or disobey the producer (G-05). Do not model every genuine manifestation as a remotely commanded practical-effect device.

## Three phases and their limits [CONFIRMED direction; fixed nightly quota approved, numeric value open]

| Phase | What the player does | Example | Limits |
| --- | --- | --- | --- |
| **Before start** | Prepare and alter house; select equipment; complete structural work at leisure | Make floorboards squeak, install speakers/thermostats | **No time limit [CONFIRMED]**; **budget-limited [CONFIRMED]**; gear availability only PROPOSED |
| **During contest (live)** | Choose **when** to activate a previously installed or prepared effect | Play sound, rattle windows, flicker controllable lights | Prepared mechanism needed; exact uses, costs and cooldowns OPEN |
| **During contest (small alteration, possibly nightly)** | Select a quick, nonstructural change, staged for occupants to discover | Move a doll, place a bloody-looking prop on a table | **Nonstructural scope and unseen staging [CONFIRMED]**; **fixed count per night [CONFIRMED]**, one slot per change; number/windows OPEN |

The initial phase **has no player time pressure**, but is not unlimited in money or kit. Once contestants arrive, floorboards and complex devices cannot simply be installed as a minor nighttime prank. These alterations form a distinct action type from remote activation of an effect.

**Approved execution model:** the player **selects a qualifying minor alteration from a menu/abstract action**, and it **happens unseen**. Do **not** build a stealth minigame, security patrol challenge, entry-detection probability or roll to see whether the producer is caught placing the object. The in-fiction justification is the producer's skill and prior preparation; it does not require detailed explanation or simulation. Contestants may still discover and investigate the **result** after the fact—this is separate from catching anyone in the act.

**APPROVED:** a **fixed nightly count** of these minor alterations; **each eligible change costs one selection**. No separate time/effort points or automatic escalating suspicion cost for using several. The number of slots and exact nighttime selection windows are **OPEN** (#16/#17/#7).

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

Before the contest, select a **small number of physically plausible house preparations**; during the contest, trigger effects that those preparations authorize. Keep the quick, nonstructural alteration category **separate** from prepared effect triggers. Valid changes are **abstracted and executed unseen without stealth checks**; there is an approved **flat number of one-slot changes per night**. The exact quota and when results appear remain undecided. The simulation decides what contestants notice, believe and do; the player does **not** directly set their emotional state or supernatural entity actions.

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
[Untimed pre-contest planning, constrained by budget]
   -> select plausible house preparations
   -> scenario capabilities (room/device/prop; exact model open)
[Producer observes through approved hidden surveillance]
   -> choose an available prepared effect
   -> game checks whether preparation/context supports that effect
   -> effect occurs in world simulation
   -> contestants notice or miss it and react autonomously
   -> effect/evidence may be investigated and interpreted
[Separate minor nonstructural changes during play; flat nightly slots APPROVED]
   -> potential staged discovery of quick prop changes
[Later: independent supernatural forces may manifest, not as direct player commands]
```

**Example:** If an appropriate hidden sound setup is approved and installed in a room, the player could trigger a disturbing sound there. A contestant might flee, investigate the apparent source, ignore it, or persuade others that it was staged. The producer's selected **effect** is direct control; a contestant's **reaction/belief** is not.

**Overnight alteration example [CONFIRMED category and unseen execution]:** the player selects a permitted minor prop placement. The prop appears as staged; the player is **never caught placing it**. Contestants may observe it later and react autonomously. The **numeric nightly allowance**, eligible windows and exact aftereffects remain OPEN; each qualifying alteration uses **one slot**.

## Boundaries and future tests

- A nonexistent or unprepared **mundane** effect may not be triggered just because the player selected a room; a preexisting or later-approved supernatural means is distinct.
- Preparations affect available choices but **do not** automatically command contestants; decision tests should demonstrate multiple plausible reactions.
- Contestants can notice a staged object or physical evidence **after** the alteration and interpret it autonomously. That is **not** witnessing the producer's action. Exact evidence/inference rules and consequences remain OPEN.
- The producer cannot invent unobserved inner state from an intervention result. **Observation remains routed through ADR-0004 and ADR-0005**; the approved house surveillance can show visible changes without revealing the cause to contestants or their internal conclusions.
- Quick nonstructural staging is a **confirmed intervention category**; **valid selected changes are carried out unseen as a design assumption**. No stealth interface or caught-in-the-act failure roll. This does **not** approve unlimited selections or structural changes during the contest: **each eligible alteration uses one of a fixed number of nightly slots**. Structural/setup work cannot be treated as a quick alteration.
- **Budget as a preparation constraint and timing as the principal early/lower-difficulty challenge are approved design directions**, but exact costs, gear restrictions, severity, cooldowns, difficulty scaling, initial effects, asset fidelity, implementation, scenario generation, time controls and player tool UX are NOT approved. No implementation test was executed for this design decision.

## Nightly minor-alteration limits — option 2 APPROVED; alternatives retained for rationale

The Creative Director evaluated **three ways** to constrain quick, nonstructural overnight alterations and **selected option 2: a flat per-night count**. All assume the previously approved rule: **valid selected staging is carried out unseen**, without stealth minigames or caught-in-the-act checks. A contestant's **later interpretation** of the staged result is distinct from detecting the producer performing the act.

| Candidate | What limits action | Benefit | Problem / design risk |
| --- | --- | --- | --- |
| **1. Escalating suspicion / soft cap** | No simple hard quota; many or conspicuous **discoveries in proximity** might provoke skepticism about staging | Emergent risk/reward tied to effects on contestants, potentially supports higher skill levels | Counting incidents alone is insufficient: frequent apparent hauntings can also increase **belief in genuine ghosts**, not automatically suspicion of producer wrongdoing; must respond to patterns, explanations and contestant beliefs |
| **2. Flat per-night count** | A limited number of qualifying changes each night | Very clear, cheap to prototype and balance; keeps early challenge about **which** intervention to select and **when** to use live effects | Treats all prank-like changes as equivalent; arbitrary limit might feel artificial |
| **3. Per-action time/effort cost** | A finite **abstract nightly effort allowance**, with larger changes consuming more | Physically plausible differences between small and elaborate interventions; room for loadout variety | Adds bookkeeping and balancing; risks displacing the game's early **live timing** focus; do not translate into stealth traversal or real-time countdown by default |

**Creative Director decision — option 2 CONFIRMED:** Use a **flat number of allowable minor changes per night**. **Each qualifying change uses exactly one slot**, and available alterations should be balanced around **comparable intended effectiveness**, rather than distinguished by abstract setup time/effort prices. The quota's **numeric value is OPEN**; other potential rules (e.g., whether unused selections carry over) are not decided. Equal balancing weight is a **game-design abstraction**—it does **not** force identical fear, belief, suspicion or other results from different autonomous contestants and contexts. A doll moved in an already tense room may be interpreted differently from the same alteration in a calm one.

**Reasons for rejecting the other proposals as the nightly capacity rule:** A suspicion-based soft cap requires a substantially more sophisticated **believability/inference model** and risks conflating stronger apparent haunting with suspicion that it is fake; an abstract time/effort budget is **just as arbitrary** when the actual clandestine time available is difficult to model accurately. Neither is approved as the capacity limiter. Independent, context-grounded contestant suspicion **afterward** remains possible through future systems, not a fixed tax based on how many slots were used.

**Critical distinction:** fear, belief in a real haunting, and suspicion of human staging need not move together (G-06; candidate S-02). A cluster of apparent disturbances could make one contestant more convinced of ghosts, and another suspicious of a prank. The producer still succeeds at performing allowed staging unseen. **The flat quota and one-slot cost are approved; the numeric quota, eligibility windows and difficulty scaling are not.** No abstract time budget, suspicion-as-action-cost formula, or forced equal contestant outcomes is approved.

## Preselected contestants and compact research dossiers [CONFIRMED direction]

**The producer personally selected the contestants and conducted background research before the competition began.** The player receives a **brief dossier for every contestant**, comparable to a **baseball card**, containing:
- **Photo** and identifying name
- **Age**
- **Sex**
- **Occupation**
- **Extremely brief background** (one or a few short statements), including **an exploitable fear or significant personal event when one is known**

**IMPORTANT REVISION:** **Not all contestants have a known exploitable fear, personal trauma or trigger**. Their dossier is still present and may simply contain ordinary background with **no known exploitable hook**. This explicitly **supersedes** the earlier direction that every contestant must have at least one personal trigger. Do not invent an exploitable trauma to fill each card. A contestant with no known hook can still be frightened, affected by the environment, investigate, cooperate or react to supernatural events autonomously.

For the initial game, casting selection and research are **backstory and starting information**, **not gameplay systems the player must perform**. **Future option, PROPOSED:** allow the player to choose/recruit the contestants and research their vulnerabilities, giving casting strategic consequences in an expanded version. No recruiting process, research minigame, hidden-dossier unlock system, candidate pool or recruitment budget is approved now.

### Dossier-driven overnight options

Available **personalized** minor-alteration choices derive from **known exploitable fears or meaningful events in the cast's dossiers**, when present—not from a universal pool of generic scary props. Creative Director examples:
- **Fear of dolls:** arrange for a doll to appear somewhere unusual for that particular contestant.
- **Death of a family member:** leave a photograph of that family member somewhere unexpected.

Dossiers are a **legitimate pre-contest research source available to the producer** for known biographical details. Under ADR-0004 they are **not** an omniscient readout of current hidden fear, intent, truthfulness, beliefs or mental state. Their completeness/accuracy beyond the supplied short facts remains undecided, but the basic cards are confirmed. The exact format, portrait art, ordering, whether names/locations link to the surveillance view and how to handle a cast with few/no disclosed hooks remain open.

Any overnight selection must still be a **plausible quick, nonstructural change**, use **one of the fixed nightly slots**, and occur **unseen**. A contestant without a hook in their dossier does **not** receive a fabricated personalized option just to guarantee one per person. Likewise, an elaborate personal effect requiring equipment belongs in **untimed pre-contest preparation** rather than a free nighttime installation.

**NPC autonomy remains mandatory:** a meaningful photograph may cause grief, anger, curiosity, skepticism or other consequences; a doll could provoke fear, investigation or avoidance. **The stronger guarantee that every offered option significantly affects at least one contestant remains PROPOSED (A-11)**. Personal relevance makes an effect plausible; it does not establish a fixed guaranteed fear amount or forced response.

### Possible guaranteed meaningful consequence — Creative Director suggestion [PROPOSED]

Because **each overnight alteration uses one of a small, fixed number of slots**, the Creative Director raised the possibility that **every offered option is guaranteed to have a significant effect on at least one contestant**. This is a **proposal**, not an approved NPC-outcome rule or tuning threshold.

**Recommended reading of “significant” (PROPOSED):** ensure each available choice has a **meaningful consequence for at least one contestant** when it resolves, such as consequential fear, curiosity/investigation, suspicion, changed intentions or changed behavior. **Do not guarantee a specific emotion, belief, reaction, fear gain or haunting-energy payout.** NPC reactions remain autonomous, and the player should not automatically receive private mental-state details that ADR-0004 would prohibit. The consequence could be legible through later behavior, dialogue or properly sourced observation rather than a numerical UI promise.

**Potential implementation approach [PROPOSED]:** make the **menu of eligible alterations context-aware**: only offer an action in the circumstances where at least one contestant can meaningfully encounter or be affected by the result, or design the staged event to reliably elicit a meaningful *but variable* reaction. A mere ornamental prop that no one encounters should not consume one of the scarce action slots **if a hard impact guarantee is adopted**. This may require balancing, scenario authoring, targeting rules or validation rather than forcing NPC psychology.

**Unresolved:** How to define/test a “significant effect” without covertly scripting contestant choices or exposing hidden state; whether the promise must be immediate or may be fulfilled upon later discovery; what happens when contestants leave or circumstances change after the nightly choice; and whether all eligible options are guaranteed or merely strongly likely to matter. **Known dossier-based personal hooks are CONFIRMED as the source of personalized options when available; not every contestant has one, and guaranteed impact is still PROPOSED.** No numerical magnitude or hard-gating implementation is approved.

## Decisions still needed in #16

1. Select the **first tiny action vocabulary** for a vertical slice: what prepared features and triggered interventions make the essential observe → stage → react → adapt loop legible?
2. **Quick nonstructural changes, assured unseen abstract execution, and a flat number of one-slot selections per night are confirmed.** The **number** of nightly slots, eligible windows, specific options, and whether unused slots expire remain OPEN. **PROPOSED:** guarantee that each offered nightly choice causes a significant but non-predetermined consequence to at least one contestant; define significant, context eligibility and interaction with autonomy before approving. Do not design stealth navigation, exposure rolls, effort prices or automatic suspicion penalties.
3. **Budget limits setup [CONFIRMED]**; choose a simple budget model and numeric costs later. Decide whether **equipment stock/loadouts are constrained [PROPOSED]**, and what room/device limits, suspicion, access, cooldowns and feasibility/availability UI are necessary. **Keep early/lower-difficulty balance timing-first [CONFIRMED direction].**
4. May contestants discover/disarm/counter staged effects, and how should this affect continuing operations?
5. How should sound/lighting/effect controls interact with player focus, live dialogue, the proposed house timetable and real supernatural autonomy?

**Recorded scope:** The Creative Director approved **untimed, budget-limited pre-contest preparation**, **timing-first challenge at early/lower difficulties**, and the separate category of **quick nonstructural changes during play, selected abstractly and executed unseen**, supplying *Orcs Must Die!* as a structural reference. **Equipment availability limits remain a possibility**, not a confirmed rule. The Director approved a **fixed per-night count with equal one-slot costs and roughly equivalent intended value** for qualifying minor alterations. The **numeric count**, selection windows and holographic ghosts remain OPEN/PROPOSED as applicable. The specific catalogue of interventions is **deliberately non-exhaustive**. Issue #16 remains **OPEN/In Progress**; no producer gameplay system or detailed mechanic is authorized by this documentation.
