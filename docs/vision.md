# Game Vision — The Producer

**Status:** Mixed: explicit decisions and exploratory design. **Version:** 0.2

## High concept [CONFIRMED]
A reality television competition places contestants in a supposedly haunted house. They may quit at any time; the last contestant remaining wins. Secretly, the organizers seek to create a genuinely haunted location by cultivating psychic energy through fear and killing contestants at moments of extreme terror. The player acts as the producer, manipulating the conditions of the competition while hiding the underlying operation.

## Identity [CONFIRMED]
- Primary perspective: **The Producer**, not the contestant survival game.
- Genre direction: isometric/dollhouse-view, systems-driven horror management sandbox.
- Tone: genuine psychological/supernatural horror with tonal shifts and organic comic relief; not primarily parody.
- Structure: independent reality-show seasons in varied locations with new casts and some optional persistent progression.
- Contestants are autonomous and can leave; the player must manage fear, exposure and retention.
- Supernatural activity becomes increasingly autonomous and can threaten the player's goals.
- The player has incomplete, observational knowledge of contestants' beliefs and intentions.
- Contestants can interact with and resist supernatural forces, including avoidance, investigation, exorcism/banishment and potential elimination.
- Artifacts from prior hauntings may seed later seasons; they are interesting options, never mandatory.
- The primary goal of a season is to establish a **real, persistent haunting** that continues after production departs [CONFIRMED].
- The reality show must retain enough public credibility to support another season [CONFIRMED goal; mechanical measurement OPEN].
- Requiring at least one surviving contestant is a favored possibility, **not yet a final rule** [PROPOSED].
- The public-facing fate of contestants who leave, die, or disappear must be narratively credible; the mechanism is [OPEN].

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
- No final title, engine, art pipeline, monetization or target platforms selected [OPEN].

## Season outcomes and stakes
- **Persistent haunting [CONFIRMED objective]:** mere energy accumulation is not sufficient; the location must remain haunted independently of the production's ongoing intervention. The precise test for persistence is OPEN.
- **Franchise continuity [CONFIRMED objective]:** the production must preserve the show as a plausible enterprise capable of returning for another season. Exact reputation/exposure mechanics are OPEN.
- **Survivor requirement [PROPOSED]:** at least one contestant may have to survive and perhaps serve as the public winner. Do not implement this as a mandatory rule without approval.
- **Credible contestant accounting [CONFIRMED narrative constraint]:** contestant deaths and unexplained absences must have meaningful, believable consequences. How exits and deaths are represented publicly remains OPEN.

See `systems/season-outcomes-and-continuity.md` for the system contract and unresolved choices.

## Success criteria [PROPOSED]
Players can form hypotheses about contestants and entities, execute meaningful plans, respond to unintended consequences, and tell distinct stories about different seasons. The core loop remains interesting with placeholder art and without an artifact loadout.