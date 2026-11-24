# Requirements Register

`CONFIRMED` means design direction explicitly stated; it does **not** mean detailed numeric mechanics are finalized.

| ID | Status | Requirement | Verification direction |
|---|---|---|---|
| G-01 | CONFIRMED — REVISED (#1) | Player orchestrates a deceptive residential prize competition whose concealed purpose is to create a genuine, persistent haunting; a real televised show is not required. | Approved v0.3 vision; design review |
| G-02 | CONFIRMED | Contestants act autonomously and can decide to quit, attempt to leave/escape, investigate or resist; whether they can safely leave is not automatically guaranteed by the contest's claims. | Simulation tests for autonomous decisions and attempted exits; detailed exits OPEN |
| G-03 | CONFIRMED | Isometric/dollhouse presentation. | Visual prototype review |
| G-04 | CONFIRMED | Horror is primary; humor is organic tonal contrast. | Narrative/art direction review |
| G-05 | CONFIRMED | Supernatural forces develop independent behavior that can conflict with producer goals. | Autonomous-event scenarios |
| G-06 | CONFIRMED | Player has imperfect information about contestants' inner attitudes, knowledge and plans, despite complete camera visibility of the house and clickable observed conversations. | UI/data-access and speech-vs-belief leakage tests |
| G-07 | CONFIRMED | Contestants can avoid, investigate, defend against, banish/exorcise, and potentially neutralize supernatural entities. | Behavioral scenario tests |
| G-08 | CONFIRMED | Distinct operations/chapters may take place at different locations with varying casts and constraints; no real TV seasons are required. | Data-driven scenario tests |
| G-09 | CONFIRMED | Cross-season artifacts are optional, not required for successful play. | Artifact-free season feasibility tests |
| G-10 | CONFIRMED | New seasons may inherit selected capabilities, knowledge or artifacts. | Persistence/season-transition tests |
| G-11 | CONFIRMED | The primary season objective is to create a genuine haunting that persists after production departs. | Headless post-season persistence scenario, exact criterion TBD |
| G-12 | CONFIRMED — REVISED (#1) | Operating again in future locations must reckon with external exposure, contestant fates and the organization's ability to continue; TV-franchise credibility is not a requirement. Exact viability mechanics remain OPEN. | Multi-operation continuity/narrative checks once approved |
| G-13 | OPEN | Whether a contestant must survive, win, or whether all must die is undecided; no survivor gate or mandatory death quota is approved. | Decide under #7/P-02 before scenario validation |
| G-14 | CONFIRMED | Departures, enforced removals, deaths and unexplained disappearances have credible consequences for contestants and the wider world; no convenient universal cover-up is assumed. | Narrative/system review of contestants, witnesses and external scrutiny |
| O-01 | CONFIRMED (#16, ADR-0005) | Hidden cameras give the producer full observational visibility into all rooms of the house, supplying the diegetic basis for the dollhouse view; this does not reveal private thoughts or unobserved off-site activity. | Authorized house view covers all test rooms, never private-state fields |
| O-02 | CONFIRMED (#16, ADR-0005) | The producer can hear relevant house sounds, including door opening and closing. | House auditory events, no unauthorized off-site sound |
| O-03 | CONFIRMED (#16, ADR-0005) | In-house conversations display bubbles that the player clicks to read speech details; dialogue text is not shown automatically, and speech is not the same as private beliefs. | Visible indicator, on-click observed text, no hidden-belief leak |
| O-04 | CONFIRMED (#16, ADR-0005) | Contestants have one shared house phone and are not allowed cell phones; phone-use bubbles can be clicked for text/details. Exact remote-side availability, logs and ban enforcement are OPEN. | One phone in default scenario; phone indicator + source-limited click details |
| S-01 | PROPOSED | Contestants have private beliefs, memory, motives, relationships and observable behaviors. | State transition tests |
| S-02 | PROPOSED | Fear and suspicion of producer wrongdoing are modeled separately. | Counterexample scenarios |
| S-03 | PROPOSED | Supernatural entities have consistent drives and bounded agency rather than arbitrary random actions. | Seeded reproducibility and causal trace |
| S-04 | PROPOSED | Observations are derived from sensors/events and can be uncertain or stale. | Non-leakage tests |
| S-05 | PROPOSED | Track supernatural persistence independently from momentary activity or energy yield. | Stop production intervention and evaluate continued haunting |
| S-06 | PROPOSED | Track each contestant's actual fate and separately what is publicly known or believed. | Divergence and season-continuity scenario tests |
| T-01 | PROPOSED | Simulation can run headlessly with seeded randomness. | Repeatability tests |
| T-02 | PROPOSED | Debug inspector reveals hidden state only in developer/test modes. | Release-build access tests |
| T-03 | APPROVED (BOUNDARY PRINCIPLE) | Keep simulation/game rules, authorized observation/application data, replaceable world rendering, player UI/HUD, and campaign persistence distinct. Detailed interfaces and save formats remain open. | ADR-0002; architecture review and integration tests |
| T-04 | PROPOSED | Core gameplay does not require paid cloud model APIs. | Offline smoke test |
| P-01 | APPROVED — PROVISIONAL | Godot 4 + GDScript, initially fixed-angle 3D orthographic, with 2D isometric retained as a pre-art-investment fallback; stylized/comic-like appearance and lighting to validate. | ADR-0002; native GUI and renderer-independence acceptance |
| P-02 | OPEN | Exact persistence threshold, whether a survivor is mandatory, and season scoring/partial-success criteria. | Creative director decision |
| P-04 | OPEN | Meaning of contest “removal,” quit/escape outcomes, death/disappearance accounting, town reputation and concealment of repeated deceptive operations. | Narrative and systems exploration under #7, human approval |
| P-03 | OPEN | Initial platform(s), accessibility targets and performance budgets. | Creative director decision |

**Approved premise revision (Creative Director, 2026-11-23 ET; Issue #1):** the contest is a deception used to attract and manipulate occupants; the player's production is the secret haunting operation, not necessarily a genuine television show. This supersedes the former TV-franchise interpretation of G-01/G-12 without altering the provisional Godot/renderer decision in ADR-0002. **Original story specifics remain proposed:** a 30-day stay, 8 PM–6 AM room confinement, $250,000 plus shared ownership, mysterious “removal,” staged townspeople, fabricated notes/diary and possible last-person outcomes. These are not implementation mandates. See `docs/vision.md` for source details. Contestant exits, whether death is necessary or universal, exact haunting-persistence threshold, and continued-operation mechanics remain OPEN.

## Requirement change control
Changes to CONFIRMED direction require human approval. PROPOSED items become approved only through a recorded decision. Every implemented issue should cite applicable IDs and include verification evidence.