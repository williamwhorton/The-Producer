# Season Outcomes and Reality-Show Continuity

**Status:** MIXED — includes confirmed creative objectives, proposals, and unresolved narrative questions. **Added:** 2026-11-21.

## The three competing outcomes

1. **Persistent haunting [CONFIRMED, primary].** The production's hidden objective is to make the location genuinely haunted. A successful haunting must continue after production departs; a transient scare or full energy meter is insufficient. Specific persistence test, duration, intensity and containment requirements are OPEN.
2. **Reality-show franchise viability [CONFIRMED objective].** The production must conclude the season in a way that permits a credible subsequent season at a different location. The show must remain publicly plausible. Exact trust/reputation/exposure mechanics are OPEN.
3. **A surviving contestant [PROPOSED].** Require at least one contestant to survive, possibly the public winner. This would create a meaningful restraint against overaggressive production and uncontrolled entities, but it is not approved as a hard win condition.

Keep these dimensions distinct in design discussion and test fixtures. Do not collapse them into a single kill count, energy meter or reputation score without approval. The degree to which objectives are hard gates versus grades remains OPEN.

## Contestant exits and the show's public narrative

**Confirmed problem:** Contestants have lives and relationships outside the production. A large number of unaccounted-for deaths or disappearances, especially repeated season after season, would undermine believability. Merely concealing a body inside the house does not explain a contestant's absence to viewers or the wider world.

**Design distinction [PROPOSED]:** Treat ordinary quitting or a normal publicly accounted-for elimination differently from death, disappearance, or an unresolved fate. Those outcomes should have different narrative and mechanical consequences. A contestant's actual fate may differ from what production or outsiders believe, but those distinctions must be explicitly modeled if adopted.

**Possible exploration paths, none approved:**
- A credible, visible system of ordinary exits and a public winner, with rare catastrophic incidents creating lasting scrutiny.
- A season structure in which apparent exits and actual fates differ, but inconsistencies can surface later and threaten future seasons.
- Supernatural interference with knowledge, memory, or testimony—but only if it has clear limitations and does not erase all consequences.

These are narrative hypotheses, not instructions for real-world concealment and not established mechanics. Do not canonize one without creative-director approval.

## Candidate outcome states [PROPOSED]

- **Full success:** a persistent haunting exists and the show remains viable (plus any survivor rule if approved).
- **Pyrrhic success:** a persistent haunting exists but the franchise is exposed, damaged or otherwise unable to continue.
- **Operational survival without haunting:** the production completes a plausible season but fails to seed a lasting haunting.
- **Catastrophic failure:** the haunting cannot be established and/or the operation collapses. Exact terminal logic is OPEN.

The game need not expose these exact labels or use binary thresholds. They are useful test cases for design reviews.

## Technical contracts to evaluate [PROPOSED]

- `HauntingPersistenceResult`: reports whether/how haunting continues in a simulated period after production intervention ends; separate from energy collected.
- `ContestantDisposition`: tracks actual outcome such as active, publicly exited, survived, deceased or missing, with no final taxonomy chosen.
- `PublicContinuityAssessment`: derives franchise viability from observable consequences and unresolved inconsistencies; no magic reputation scalar by default.
- `SeasonOutcome`: composes independent dimensions without assuming that a fatality quota is required.

## Required test scenarios once mechanics are approved

1. The house shows high activity during filming but stops afterward: should **not** count as persistent haunting.
2. The house remains haunted, but the franchise suffers severe public consequences: distinguish haunting success from operational failure.
3. Contestants can leave alive without being treated as unexplained disappearances.
4. Repeated unexplained absences cannot be ignored in later seasons.
5. An artifact-free season remains feasible.
6. A survivor gate is not introduced until explicitly approved.

## Open decisions for creative director

- How much activity and for how long must a site remain haunted to count?
- Must at least one contestant survive? Must that person be the publicly acknowledged winner?
- Do contestants need to die to make a house permanently haunted, or is death an accelerant rather than a universal necessity?
- Which contestants leave normally, and what public-facing information exists about contestants who die or vanish?
- What makes the show lose credibility, and do earlier seasons create lasting consequences?
- Do partial successes unlock future seasons or progression?