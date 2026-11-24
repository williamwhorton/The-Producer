# Operation Outcomes, Contestant Fates and Continuity

**Status:** MIXED — approved v0.3 premise (Issue #1, Creative Director, 2026-11-23 ET); exact mechanics remain proposed/open.

## Distinct outcome dimensions

1. **Persistent haunting [CONFIRMED, primary].** The secret producer operation aims to make its property genuinely haunted. The haunting must continue after the operation ends; a momentary scare or a full psychic-energy meter alone is insufficient. The persistence duration, intensity, testing and whether death is required remain OPEN.
2. **Operational viability and exposure [CONFIRMED direction; rules OPEN].** The organization may attempt additional deceptive competitions at other locations. Contestant fates, local rumors and external scrutiny must have consequences. **A legitimate TV franchise, actual public show or guaranteed next season is not required.** Conditions for successfully operating again, escaping accountability or failing are OPEN.
3. **Contestant survival, killing and winning [OPEN].** The Creative Director is exploring an increasingly sinister contest, potentially ending in deaths, but has **not** approved an all-contestants-must-die condition or a mandatory survivor/winner. Whether contestants may withdraw safely, are trapped, or can escape is unresolved.

Keep these dimensions distinct in proposed scenarios and tests. Do not collapse them into a body count, one energy meter or a single reputation score without a separate approved decision.

## Deception, rule enforcement and contestant knowledge

**Approved narrative frame:** The contestants believe an elaborate residential prize contest is legitimate, while the producer has designed it to cultivate fear and ultimately create a persistent haunting. **The contest's purported public purpose is a lure, not an actually confirmed TV broadcast.**

**Original story seed — illustrative, NOT approved gameplay:** contestants live in a large old house for thirty days; each is promised $250,000 and a share of the deed; they are instructed to stay in individual rooms overnight from 8 PM–6 AM. The meaning of **“removal”** for breaking the rules is hidden from the cast. Next-day notes, footsteps and partial witnesses create uncertainty; incidents may entice contestants into corridors. Contestants might go into town during daylight and encounter planted locals, helping build the house's reputation. Diary/found-document presentation, a final witness and possible framed deaths are narrative candidates, not scripted endpoints.

**Confirmed stakes:** Contestants and outsiders have relationships and memories. A pattern of missing people, unexplained deaths, false assurances or contradictory accounts cannot become consequence-free. Do not assume that removing evidence, supernatural memory alteration or arbitrary off-screen explanations automatically resolve these stakes.

**Proposed distinctions:** Voluntary quit; attempted escape; rule-related “removal”; survival; death; disappearance; discovery/exposure; external suspicion. The player's access to individual fears, private knowledge and fate reports remains mediated by Issue #3's unapproved observation contract.

## Candidate outcomes [PROPOSED]

- **Full operational success:** a persistent haunting is established, and the organization remains able to pursue future operations under still-to-be-defined constraints.
- **Pyrrhic success:** a genuine haunting exists, but the operation is exposed, collapses or suffers other lasting consequences.
- **Failure to seed the house:** the operation ends without a persistent haunting, regardless of what contestants experienced.
- **Uncontrolled supernatural outcome:** supernatural forces exceed the producer's control, potentially harming all sides, with specific scoring and end conditions OPEN.
- **Escape or investigation outcome:** a contestant survives or uncovers the deception, changing what outsiders know and what the producer can do next.

These are *examples*, not the approved victory table or a commitment to preserve every outcome. Neither a mandatory surviving public winner nor a requirement to kill everyone is approved.

## Technical contracts to evaluate [PROPOSED]

- `HauntingPersistenceResult`: verifies that haunting persists after producer interventions stop rather than equating it with energy collected.
- `ContestantDisposition`: distinguishes actual outcomes from public, institutional and producer-held beliefs; the exact taxonomy remains open.
- `OperationContinuityAssessment`: explores whether the organization can credibly attempt another location given real consequences and outside knowledge. This **replaces the former `PublicContinuityAssessment` TV-franchise framing**, without approving a data shape.
- `OperationOutcome`: combines separable dimensions only after the Creative Director decides outcome rules.

## Later verification scenarios (no implementation until mechanics are approved)

1. The house exhibits paranormal activity during the operation but falls silent afterward; this is **not** persistent haunting.
2. A haunting endures, but evidence or witnesses threaten future operations; evaluate haunting and operational viability independently.
3. Someone tries to quit or escape; distinguish the attempt, the person's actual fate, and what the producer and other contestants know.
4. Repeated unexplained disappearances cannot be ignored merely because the contest was staged.
5. A chapter can begin without inherited haunted artifacts.
6. No unconditional death quota, compulsory victim, survivor/winner gate, or mandatory television audience appears without explicit approval.

## Open creative decisions

- Exact rules and effect of nighttime confinement; whether a daytime contestant can freely quit; what “removal” means.
- Whether everyone must die, anyone must survive, or deaths are simply one route to lasting haunting.
- The haunted location's persistence threshold, assessment and any partial success.
- Whether there is a public contest, a staged broadcast façade, or solely an elaborate private lure (none requires a genuine reality-TV business).
- Whether reputation-building involves witnesses and nearby towns, planted rumors, property ownership, or some other mechanism.
- How a new operation starts despite prior incidents; consequences for cast families, townspeople and investigators.
- Whether the original thirty-day period, financial/deed prize, documented testimony and final-survivor twists make good gameplay/story devices.

**Owner of the next decisions:** Issue [#7](https://github.com/williamwhorton/The-Producer/issues/7) and related creative review, not this baseline vision acceptance.
