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

## Original story seed [SOURCE MATERIAL — MECHANICS PROPOSED]

The Creative Director's earlier fiction notes inspired the approved deceptive-competition premise. The following are **candidate scenario elements**, not rules authorized for implementation:

- A large, aging allegedly haunted house; a residential contest advertised for **30 days**, promising **$250,000 plus a share of the deed** to each contestant (exact duration and rewards are illustrative).
- A nighttime rule that contestants stay in their own rooms from **8 PM to 6 AM**, with mysterious **“removal”** for violations. Contestants learn of removals through next-day notes, suspicious sounds and partial witnesses rather than clear explanations.
- Increasing disturbances designed to lure contestants out or prevent them from retreating, as tension grows between the perceived contest and the hidden operation.
- Daytime visits to a nearby town, stories spread by contestants, and possible planted locals supporting the property's reputation.
- A final survivor discovering the conspiracy, potentially exploiting it; a framing or post-contest tragedy is another **story possibility**, not a required conclusion. Found documents or a contestant diary remain possible narrative presentation devices.

**Do not canonize:** mandatory mass death, a survivor/winner, scripted removal events, fixed hours, a death-to-psychic-energy formula, fixed day count, specific rewards or a predetermined ending. Contestants retain autonomous choices and credible external relationships; actual and apparent fates cannot be waved away. Preserve the narrative seed for later review under #7, #17, #20 and #24.

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