# Open Questions and Decision Queue

## Priority A — Must resolve before vertical slice implementation
1. **Operation outcome (partly resolved):** The primary objective is a genuine haunting that remains active after the operation ends. The ability to stage further deceptive competitions must reckon with exposure and contestant fates, **not** legitimate TV-franchise continuity. OPEN: persistence test and threshold, survivor/death requirements, operational viability, partial success/failure states.
2. **Player action scope:** Which production tools are direct controls, which require preparation, and which supernatural actions are only influences?
3. **Simulation pacing and proposed confinement rule:** Pausable real-time vs turn/tick-based, possible day/night phases, a candidate **8 PM–6 AM room confinement rule** and illustrative **30-day contest** from the story notes. None of the numeric rules are approved.
4. **Observation architecture + house baseline APPROVED:** ADR-0004 [source-grounded projection](decisions/ADR-0004-producer-observation-boundary.md) remains required; ADR-0005 [full room surveillance and communications](decisions/ADR-0005-house-surveillance-and-communications.md) under #16 now confirms hidden cameras in all house rooms, audible environmental events, click-to-read conversation bubbles, **one house phone**, and **no contestant cell phones allowed**. **Further approved attention direction:** choose which simultaneous conversation to follow; only attended speech is readable, with no automatic unselected-history catch-up or bubble-triggered pause. **Further approved details:** phone calls and conversations use the **same exclusive listening focus**; only witnessed, source-permitted speech becomes a **persistent rereadable text record**, while unattended speech is lost. Ordinary surveillance footage/audio **cannot be replayed**. Video recording is a **future mechanic candidate, not approved**. Still OPEN: cameras outside rooms, live text/archive UX, manual/global pause controls (#17), telephone remote-side content, optional estimate/confidence UI and unapproved producer powers. Off-site knowledge still needs a valid source.
5. **Contestant resistance:** What knowledge/resources allow exorcism or neutralization, and how do contestants discover them?
6. **Deceptive competition CONFIRMED; participant fates OPEN:** The prize/residential contest is a lure for the hidden haunting operation (Creative Director approval, #1). Does a voluntary quitter escape safely? What distinguishes rule-violation “removal,” attempted escape, actual disappearance and murder? How do contestants, nearby townspeople, families and investigators interpret events? How can repeat operations avoid becoming implausibly consequence-free? Resolve specific rules under #7; **no real television show or standard public winner is required**.
7. **Engine and presentation (provisionally decided):** ADR-0002 approves Godot 4 + GDScript, beginning with fixed-angle 3D orthographic. **Open validation:** preserve the appealing clean/comic-like 2D aesthetic in stylized 3D using cheap assets, test lighting/shadows and room readability, and retain 2D as a fallback before major art spending. Do not interpret this as a final art-direction choice.

## Producer-observation presentation still to decide (#16 / #17 / #26)

- All-room cameras justify the dollhouse view; no camera placement or blind-spot game loop is approved. Does any indoor space outside the rooms, or any exterior space, have additional coverage?
- **Confirmed:** clicking/selecting a conversation is a time-sensitive listening decision; simultaneous unattended dialogue is missed, and opening it does not automatically pause the simulation or provide an all-conversation transcript. **CONFIRMED:** actively attended speech from house conversations **and** source-authorized phone call content is retained as text and can be reread at any time. **Only one stream can be focused on at once**. Unattended conversation cannot be retrieved and no ordinary audio/video replay is available. Video recording remains **PROPOSED for the future**. Exact behavior for interrupted/focus-switched excerpts and archive UI belongs to #26; general/manual pause to #17, accessible captions to #26/#21.
- What portion of a house-phone call can be heard, particularly the remote side? Are there consequences or exceptions if someone violates the ban on cell phones?
- These approved sources must flow through the ADR-0004 observation projection; the house-wide surveillance makes its earlier **hypothetical unmonitored pantry** example noncanonical for the main house. Unmonitored off-site/private-thought cases still need negative leakage tests.

## Story-seed details to test later (not confirmed mechanics)

- Proposed recruitment: a substantial cash prize and shared house ownership; illustrative notes specify $250,000 and a deed share.
- Proposed removal: overnight-rule violations may cause mysterious “removal,” discovered through notes or incomplete witnesses; **never equate removal with mandatory death without approval**.
- Proposed outside-world element: contestants visit town during the day and help generate local haunted-house folklore; some townspeople may be plants. **Presentation candidate:** pause-and-resolve static-image/text vignettes (Paradox-style event windows or *Rogue Trader* narrative interludes), with player choices when meaningful and information-only events otherwise. No fully explorable town is assumed.
- Proposed dramatic endpoints: a contestant uncovers the operation or is implicated in others' fates; diary/found-document framing is optional. No authored ending, required survivor, everyone-dies result, or murder threshold has been approved.

**Off-site event presentation still OPEN:** Should narrated town events pause simulation time, and when should they be shown? Who sees the underlying event, which choices can the producer genuinely make, and what information is properly available through witnesses/staff/letters? Keep this at the UI/observation interface rather than embedding it into world rendering; evaluate under #26/#17/#3.

## Priority B — Important after initial prototype
8. What creates a new supernatural entity and determines its drives?
9. What does it mean for the *house itself* to awaken?
10. How are contestants authored or generated, and how do their reasons for staying vary?
11. How do producers learn about private conspiracies without omniscience?
12. Are seasons procedurally generated, curated, or hybrid?
13. How are artifacts created, acquired, carried and balanced?
14. What persists between seasons beyond artifacts?
15. What constitutes irreversible failure, and can a season end in partial success?
16. Is a death necessary for a persistent haunting, an efficient accelerator, or one of several routes? How can this preserve narrative stakes and player choice?

## Priority C — Production decisions
17. Target operating systems, distribution, accessibility and performance targets.
18. **Art direction and animation scope:** reference *Darkest Dungeon* and *Cult of the Lamb* for graphic, expressive, readable horror (not copied assets). Test stylized 3D with selective shadows/ink-like edges, ordinary-to-ominous lighting contrast, zoom-scale legibility and stable outlines. Avoid both alienating photorealism and overly glib/cute horror; decide specific assets, shaders, animation, UI style and production budget under #22.
19. Audio approach, soundtrack and voice acting.
20. Content boundaries, rating and presentation of death/violence.
21. Localization and modding.

## Decision procedure
For each decision: record options, tradeoffs, recommendation, evidence, approval, date and affected requirement IDs in an ADR. Agents may propose, but the human creative director approves material creative changes.