# Requirements Register

`CONFIRMED` means design direction explicitly stated; it does **not** mean detailed numeric mechanics are finalized.

| ID | Status | Requirement | Verification direction |
|---|---|---|---|
| G-01 | CONFIRMED | Player operates reality-show production concealing a haunting-creation objective. | Vision/design review |
| G-02 | CONFIRMED | Contestants are autonomous and may voluntarily quit. | Simulation tests for decisions and exits |
| G-03 | CONFIRMED | Isometric/dollhouse presentation. | Visual prototype review |
| G-04 | CONFIRMED | Horror is primary; humor is organic tonal contrast. | Narrative/art direction review |
| G-05 | CONFIRMED | Supernatural forces develop independent behavior that can conflict with producer goals. | Autonomous-event scenarios |
| G-06 | CONFIRMED | Player has imperfect information about contestant attitudes, knowledge and plans. | UI/data-access tests |
| G-07 | CONFIRMED | Contestants can avoid, investigate, defend against, banish/exorcise, and potentially neutralize supernatural entities. | Behavioral scenario tests |
| G-08 | CONFIRMED | Seasons vary in location, cast and constraints. | Data-driven scenario tests |
| G-09 | CONFIRMED | Cross-season artifacts are optional, not required for successful play. | Artifact-free season feasibility tests |
| G-10 | CONFIRMED | New seasons may inherit selected capabilities, knowledge or artifacts. | Persistence/season-transition tests |
| G-11 | CONFIRMED | The primary season objective is to create a genuine haunting that persists after production departs. | Headless post-season persistence scenario, exact criterion TBD |
| G-12 | CONFIRMED | Preserving the reality show's ability to plausibly continue into further seasons is a required season objective. | Season resolution checks, exact credibility model TBD |
| G-13 | PROPOSED | At least one contestant must survive a season; survivor may be the public winner. | Scenario validation if approved |
| G-14 | CONFIRMED | Deaths and unexplained contestant disappearances cannot be consequence-free or waved away without credible in-world accounting. | Narrative/system review of contestant outcomes |
| S-01 | PROPOSED | Contestants have private beliefs, memory, motives, relationships and observable behaviors. | State transition tests |
| S-02 | PROPOSED | Fear and suspicion of producer wrongdoing are modeled separately. | Counterexample scenarios |
| S-03 | PROPOSED | Supernatural entities have consistent drives and bounded agency rather than arbitrary random actions. | Seeded reproducibility and causal trace |
| S-04 | PROPOSED | Observations are derived from sensors/events and can be uncertain or stale. | Non-leakage tests |
| S-05 | PROPOSED | Track supernatural persistence independently from momentary activity or energy yield. | Stop production intervention and evaluate continued haunting |
| S-06 | PROPOSED | Track each contestant's actual fate and separately what is publicly known or believed. | Divergence and season-continuity scenario tests |
| T-01 | PROPOSED | Simulation can run headlessly with seeded randomness. | Repeatability tests |
| T-02 | PROPOSED | Debug inspector reveals hidden state only in developer/test modes. | Release-build access tests |
| T-03 | PROPOSED | Game logic is separated from presentation and campaign persistence. | Architecture review |
| T-04 | PROPOSED | Core gameplay does not require paid cloud model APIs. | Offline smoke test |
| P-01 | OPEN | Engine, language and 2D-isometric vs 3D-orthographic implementation. | Comparative prototype |
| P-02 | OPEN | Exact persistence threshold, whether a survivor is mandatory, and season scoring/partial-success criteria. | Creative director decision |
| P-04 | OPEN | Feasible fiction/gameplay treatment of contestant deaths, show eliminations, and missing contestants across seasons. | Narrative and systems exploration, human approval |
| P-03 | OPEN | Initial platform(s), accessibility targets and performance budgets. | Creative director decision |

## Requirement change control
Changes to CONFIRMED direction require human approval. PROPOSED items become approved only through a recorded decision. Every implemented issue should cite applicable IDs and include verification evidence.