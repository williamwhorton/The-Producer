# Game Vision — The Producer

**Status:** v0.3 foundational premise approved by Creative Director (2026-11-23 ET); detailed mechanics and outcomes remain proposed/open. **Version:** 0.3

## High concept [CONFIRMED]
A deceptive residential competition lures contestants into a supposedly haunted house with promises of substantial rewards. They believe they are entering a legitimate contest; the player, acting as the producer of the *operation*, knows its real purpose is to manufacture fear and psychological trauma in order to establish a genuine, persistent haunting. Contestants think, investigate, cooperate, resist and act autonomously as staged disturbances give way to supernatural forces that can become independent and dangerous. Whether the contest is filmed, broadcast or publicly presented as a reality show is **not a requirement**. The exact rules, reward, number of days, need for deaths, survival/winning conditions and methods of ending or escaping the contest are **OPEN or PROPOSED**, not established by this premise.

## Identity [CONFIRMED]
- Primary perspective: **The Producer**, not the contestant survival game.
- Genre direction: isometric/dollhouse-view, systems-driven horror management sandbox.
- Tone: genuine psychological/supernatural horror with tonal shifts and organic comic relief; not primarily parody.
- Structure: distinct residential operations/chapters at different locations with different casts; optional inherited progression. How later operations are justified, concealed and sustained remains OPEN.
- Contestants are autonomous and may attempt to quit, escape or resist; their ability to leave safely, and the distinction between voluntary departure, forced removal and disappearance, are OPEN mechanics.
- Supernatural activity becomes increasingly autonomous and can threaten the player's goals.
- The player has incomplete, observational knowledge of contestants' beliefs and intentions.
- Contestants can interact with and resist supernatural forces, including avoidance, investigation, exorcism/banishment and potential elimination.
- Artifacts from prior hauntings may seed later seasons; they are interesting options, never mandatory.
- The primary goal of a season is to establish a **real, persistent haunting** that continues after production departs [CONFIRMED].
- The operation must contend with outside scrutiny and the credibility of contestant fates; maintaining the possibility of future operations is a high-level goal, but **not** the survival of a genuine TV franchise [CONFIRMED direction; exact rules OPEN].
- Requiring at least one surviving contestant is a favored possibility, **not yet a final rule** [PROPOSED].
- The public-facing fate of contestants who leave, die, or disappear must be narratively credible; the mechanism is [OPEN].

## House surveillance and communications [CONFIRMED — OBSERVATION BASELINE, #16]

- **Complete room visibility:** Hidden cameras justify the producer's dollhouse view of **every room in the house**. This reveals observable actions and movement, **not** private thoughts, precise fear, intentions or hidden supernatural causes. Hallways/exterior coverage and possible interference have not been separately decided.
- **House sounds:** The producer hears relevant noises such as doors opening and closing. Sound-mixing, alerts and accessibility presentation remain OPEN.
- **Selective live speech observation:** People talking inside the house show **conversation bubbles**. Clicking/focusing one allows the player to **follow its speech as text while listening**. When multiple conversations happen at once, the producer must **choose where to pay attention**. Unselected speech is **missed**, not offered later in an automatic transcript/catch-up. Focusing a conversation does **not** automatically pause time. Private beliefs remain unknown, and people may lie. **Only attended-to dialogue is saved as rereadable text**, available at any later time. House-phone calls compete for the same listening attention and their observed words can also be saved. **Surveillance footage/audio cannot be replayed**, and the player cannot recover unattended speech. General manual pause/speed and exact dialogue UX remain OPEN.
- **One house telephone:** The competition has **one shared house phone**; **cell phones are not allowed**. Telephone use likewise has a clickable bubble for text/details; **following a call consumes the producer's one live conversation focus**, and only its actually heard, source-authorized speech is preserved in the text history. The precise amount of a call that surveillance makes available (including the remote speaker) and whether the ban can be evaded remain OPEN.
- **Recording as an expansion option [PROPOSED]:** The producer **cannot replay surveillance video or audio** in the initial design. A future limited **video-recording mechanic** may be explored separately; its existence, cost and availability are not approved.

These choices are documented in [ADR-0005](decisions/ADR-0005-house-surveillance-and-communications.md) and refine the approved [ADR-0004](decisions/ADR-0004-producer-observation-boundary.md) source-grounded observation contract: house cameras/audio are real producer-authorized sources; unseen events outside the house and private internal states are not automatically knowable. **This approves observations, not player intervention powers or specific implementation.**

## Producer preparations and practical disturbances [CONFIRMED DIRECTION; MECHANICS OPEN — #16]

The producer has **unlimited setup/planning time before contestants arrive** to **prepare the environment, make structural changes or install devices** for later effects, **within the confirmed budget limit**. After the contest begins, structural work (e.g. installing squeaky floorboards) is no longer an ordinary available action. Manufactured scares must be plausible within the game's fiction, arising from prepared physical mechanisms, props, deliberate alterations or other justified methods; they are not unexplained *player-created magic*. The repertoire is intentionally **not an exhaustive fixed list**.

**Examples for future design, not individually approved actions:** squeaky floorboards, creepy dolls, remotely controllable thermostat, hidden-speaker noises, window-rattling effects, an unoccupied piano playing, and flickering lights. A seemingly inexplicable **bloody knife appearing on a table overnight** is an example of a staged change. **Holographic/projection-based ghosts** are an optional, more advanced *candidate*, not a confirmed device.

**Difficulty emphasis [CONFIRMED DIRECTION]:** At earlier levels or lower difficulties, the primary gameplay challenge is *timing*—choosing the moment to trigger a credible prepared scare while contestants are acting independently. **Pre-contest setup is budget-limited [CONFIRMED]**; restrictions on which equipment is available are **PROPOSED**, not fixed. *Orcs Must Die!* is a structural reference for selecting/placing capabilities before play and using them during active events—not for importing enemy waves, combat or trap-based victory conditions. Detailed costs, initial gear, cooldowns and actual pacing remain OPEN (#16/#17).

**Quick during-contest changes [CONFIRMED CATEGORY; QUOTA PROPOSED]:** The producer can stage **small, quick, nonstructural prank-like alterations** during the contest (for example, a bloody-looking knife appears on a table overnight). These are different from **activating an already installed device**, and cannot substitute for major pre-contest setup. The idea of selecting **a limited number per night** is a **proposal**, not yet a fixed rule. **APPROVED:** the player selects a permitted minor change through an **abstract/menu action**, and it **happens unseen** because the producer is assumed skilled and prepared. No stealth gameplay or probability of being caught during placement. Contestants may still investigate the **result** afterward; eligible nights, quotas and consequences remain OPEN. The three-phase distinction is documented in [ADR-0006](decisions/ADR-0006-producer-preparation-and-practical-effects.md). Reactions remain autonomous.

## Original story seed [SOURCE MATERIAL — MECHANICS PROPOSED]

The Creative Director's earlier fiction notes inspired the approved deceptive-competition premise. The following are **candidate scenario elements**, not rules authorized for implementation:

- A large, aging allegedly haunted house; a residential contest advertised for **30 days**, promising **$250,000 plus a share of the deed** to each contestant (exact duration and rewards are illustrative).
- A nighttime rule that contestants stay in their own rooms from **8 PM to 6 AM**, with mysterious **“removal”** for violations. Contestants learn of removals through next-day notes, suspicious sounds and partial witnesses rather than clear explanations.
- Increasing disturbances designed to lure contestants out or prevent them from retreating, as tension grows between the perceived contest and the hidden operation.
- Daytime visits to a nearby town, stories spread by contestants, and possible planted locals supporting the property's reputation.
- A final survivor discovering the conspiracy, potentially exploiting it; a framing or post-contest tragedy is another **story possibility**, not a required conclusion. Found documents or a contestant diary remain possible narrative presentation devices.

**Do not canonize:** mandatory mass death, a survivor/winner, scripted removal events, fixed hours, a death-to-psychic-energy formula, fixed day count, specific rewards or a predetermined ending. Contestants retain autonomous choices and credible external relationships; actual and apparent fates cannot be waved away. Preserve the narrative seed for later review under #7, #17, #20 and #24.

## Off-site encounters and narrative interludes [PRESENTATION PROPOSAL]

Interactions in the surrounding town, encounters with planted locals, rumors, interviews, recovered notes or other events away from the explorable house **could be presented as pause-and-resolve text-and-still-image vignettes**, rather than requiring a simulated or fully rendered town. Reference formats are event windows in Paradox strategy games and the choice-driven narrative interludes in *Warhammer 40,000: Rogue Trader*; these are examples of a format, not content to copy.

A vignette might show one illustrative image, a brief account of a situation, and **zero or more choices** for the producer when there is an actual decision to make. Some events may be informational only. This could reduce environment/animation costs while giving townspeople, local folklore and the house's reputation narrative presence.

**Not yet decided:** what off-site activities contestants can do; who triggers and observes the event; whether player input always pauses game time, whether off-site actions have ongoing simulation effects, and whether a vignette can reveal information the producer did not plausibly obtain. The future design must honor G-06 and Issue #3's observation boundary: a contestant's private off-site experience must not become an omniscient player report without a grounded source. This event-window concept belongs to **UI/application presentation**, not the 2D/3D world renderer or core game rules; defer detailed selection and testing to #26/#17 and MVP scope #20.

## Visual and tonal reference direction [CREATIVE DIRECTION; detailed style OPEN]

- **References:** *Darkest Dungeon* and *Cult of the Lamb* as broad examples of strong graphic silhouettes, stylized surfaces, controlled lighting and horror contrasted with appealing, readable imagery. Do not copy their assets, character designs or compositions.
- **Rendering preference:** start with fixed-angle 3D orthographic (provisional ADR-0002), aiming to keep the 2D spike's clean, comic-like quality while gaining atmospheric light and shadow; preserve a 2D fallback before major art investment. Specific shaders, palette, models and rendering techniques are not selected.
- **Emotional balance:** stylization gives the player enough imaginative distance to inhabit a morally troubling producer role, but the experience must remain **psychological/supernatural horror**, not a cheerful joke about contestants' suffering. Resist both unrelenting graphic realism and excessively cute or flippant presentation.
- **Validation:** cheaply test a familiar/ordinary room and a threatening version of that same room, including lighting, graphic outlines, zoom-scale legibility and visible character/room information. Avoid committing expensive art resources until that direction is reviewed. Final art/audio/content boundaries belong to [Issue #22](https://github.com/williamwhorton/The-Producer/issues/22).

## Experience pillars
1. **Manipulation, not omnipotence [CONFIRMED]:** create circumstances; people and entities decide how to respond.
2. **Horror through contrast [CONFIRMED]:** normal social life and occasional humor amplify genuine dread.
3. **Competing autonomous agendas [CONFIRMED]:** producer, contestants and supernatural entities have conflicting aims.
4. **Imperfect observation [CONFIRMED]:** infer motives from observable conduct, not thought bubbles.
5. **Distinct seasons [CONFIRMED]:** varied locations, casts and challenges; optional cross-season inheritance.
6. **Emergent, legible causality [PROPOSED]:** outcomes surprise but are explainable in retrospect.

## Boundaries
- No requirement for LLM-driven NPCs. Prefer testable simulated behavior unless proven otherwise [PROPOSED].
- Do not make inherited artifacts prerequisites for success [CONFIRMED].
- Do not reveal exact hidden contestant state through normal player UI [CONFIRMED].
- The engine/rendering direction is **provisionally approved** in ADR-0002; no final title, detailed art pipeline, monetization or target platforms have been selected [OPEN].

## Season outcomes and stakes
- **Persistent haunting [CONFIRMED objective]:** mere energy accumulation is not sufficient; the location must remain haunted independently of the production's ongoing intervention. The precise test for persistence is OPEN.
- **Operational continuity [CONFIRMED direction]:** the producer must contend with public suspicion, exposed wrongdoing and lasting consequences when attempting future competitions at new sites; the precise conditions for carrying on are OPEN. A legitimate TV franchise is **not** required.
- **Survivor and death requirements [OPEN]:** whether everyone must die, anyone must survive, someone wins, or a successful haunting can arise without deaths are all unsettled. Do not implement a mandatory kill count or survivor gate.
- **Credible contestant accounting [CONFIRMED narrative constraint]:** voluntary exits, enforced removals, deaths and unexplained absences must have meaningful consequences for witnesses, families, townspeople and/or investigators. Who knows what, and how it affects future operations, is OPEN.

See `systems/season-outcomes-and-continuity.md` for the system contract and unresolved choices.

## Success criteria [PROPOSED]
Players can form hypotheses about contestants and entities, execute meaningful plans, respond to unintended consequences, and tell distinct stories about different seasons. The core loop remains interesting with placeholder art and without an artifact loadout.