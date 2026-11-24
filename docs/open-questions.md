# Open Questions and Decision Queue

## Priority A — Must resolve before vertical slice implementation
1. **Season victory (partly resolved):** The primary objective is a genuine haunting that remains active after production leaves; the reality show must remain credible enough to continue. OPEN: measurable persistence criterion, thresholds, whether a living survivor is mandatory, and partial success/failure states.
2. **Player action scope:** Which production tools are direct controls, which require preparation, and which supernatural actions are only influences?
3. **Simulation pacing:** Pausable real-time vs turn/tick-based; desired season duration.
4. **Observation:** What surveillance can the production plausibly access? How are confidence and stale estimates displayed?
5. **Contestant resistance:** What knowledge/resources allow exorcism or neutralization, and how do contestants discover them?
6. **Contestant fates, public plausibility and possible deception:** How do normal quits, eliminations, deaths and absences appear to contestants, viewers (if any), families and authorities? How can seasons continue plausibly? **Alternative to explore:** what if the ostensible reality show is partly or entirely a lie told to contestants, rather than a genuine television franchise? This is not approved as a premise change; G-01 stays confirmed pending a separate decision. **Not a blocker** for the provisional engine choice, observation-boundary design or a narrow technical skeleton; resolve before implementing related narratives, exits or season-continuity systems.
7. **Engine and presentation (provisionally decided):** ADR-0002 approves Godot 4 + GDScript, beginning with fixed-angle 3D orthographic. **Open validation:** preserve the appealing clean/comic-like 2D aesthetic in stylized 3D using cheap assets, test lighting/shadows and room readability, and retain 2D as a fallback before major art spending. Do not interpret this as a final art-direction choice.

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
18. Art direction and animation scope.
19. Audio approach, soundtrack and voice acting.
20. Content boundaries, rating and presentation of death/violence.
21. Localization and modding.

## Decision procedure
For each decision: record options, tradeoffs, recommendation, evidence, approval, date and affected requirement IDs in an ADR. Agents may propose, but the human creative director approves material creative changes.