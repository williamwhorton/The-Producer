# ADR-0004 — Private simulation state and producer observation boundary

**Status:** APPROVED — Creative Director, 2026-11-23 (America/New_York); architecture boundary only, not a game-system implementation  
**Date:** 2026-11-23  
**Owner:** Architect (proposal); Creative Director (decision)  
**Issue:** [#3 — Private state / observation boundary](https://github.com/williamwhorton/The-Producer/issues/3)  
**Requirements:** G-02, G-06 (CONFIRMED); S-01, S-02, S-04, T-02 (PROPOSED); T-03 (approved separation principle under ADR-0002)  
**Dependencies:** [ADR-0002](ADR-0002-engine-and-presentation-approach.md), approved [vision v0.3](../vision.md). Related open decisions: [#16 producer powers/surveillance](https://github.com/williamwhorton/The-Producer/issues/16), [#17 pacing](https://github.com/williamwhorton/The-Producer/issues/17), [#26 UI workflow](https://github.com/williamwhorton/The-Producer/issues/26), [#7 contestant fates](https://github.com/williamwhorton/The-Producer/issues/7).

## Approved decision and scope

The Creative Director approves the **architectural contract** that private contestant/world state is never returned directly to producer-facing gameplay presentation. Instead, an explicit **source-mediated observation projection** creates fresh, allowlisted, attributable records of what the producer could plausibly learn. The producer may infer hidden motives from evidence; the system must not quietly disclose exact beliefs, plans or knowledge.

The Creative Director has already approved *imperfect information* (G-06) and separation of game logic from presentation (T-03). **The exact cameras, surveillance privileges, player-facing uncertainty displays, event-popup behavior, off-site interactions and contestant psychology remain separate, unapproved decisions.** This approval establishes information flow, not those mechanics.

### Three distinct kinds of knowledge

| Kind | Examples | May go to ordinary player UI? |
| --- | --- | --- |
| **Private world state / facts** | Contestant's true intent to escape, exact fear, private memory, who actually caused a noise, hidden ritual plan, internal supernatural drive | **No**, not simply because the simulation stores it |
| **Captured evidence** | Observed door crossing from a permitted camera; staff report; recording; visible footprint; testimony from an authorized informant | **Only after** applying source access, timing, coverage and content restrictions |
| **Producer-facing observation / possible estimate** | “Contestant A was seen entering the pantry at 19:00 (hall camera)”; “Staff member reports B intends to leave (unverified claim)” | **Yes**, if backed by authorized evidence, with provenance; guesses must be distinct from facts |

Even the producer's role in the deception does not grant omniscience about **contestants**, **supernatural entities**, or unobserved town events. Known production actions or assets are an intentional exception **only when the game rules establish that producer knowledge**. The boundary need not hide the player's own authorized orders.

## Alternatives evaluated

### A. Shared simulation event log, filtered when displayed

The simulation publishes one canonical event list; every HUD, 2D/3D renderer, modal or report decides which fields to show.

- **Advantages:** very little initial infrastructure, easy deterministic debugging.
- **Risks:** an innocent UI path can bypass a filter and expose a private event; source semantics get duplicated across windows, overlays, saves and future town vignettes; refactoring can reintroduce hidden fields. Rejected as the **ordinary player-facing contract**. A complete privileged event log can remain useful for headless tests/development tools only.

### B. Source-mediated projection into a minimal, immutable-by-convention player view (**approved**)

The simulation owns private entities and raw events. A small **observation projector** considers which legitimate observer/device/report could have captured **which portion** of an event at that time; it returns newly constructed allowlisted data. The world renderer, HUD and optional narrative modal consume **only** those player-view records. Estimation is a later, separate derived layer.

- **Advantages:** one audit point; consistent boundaries for isometric/3D rendering, UI, saved reports and off-site vignettes; raw beliefs/intent cannot leak by merely serializing a world event; straightforward negative headless tests.
- **Costs:** must represent data provenance and observation coverage; UI may need a deliberate `unknown` state and cannot assume every simulation event is displayable.
- **Approved direction:** use this **boundary**, without introducing a general-purpose message bus, security framework, external service or unapproved gameplay sensors.

## Proposed minimal conceptual data flow

```text
[private WorldState + actions]
           |
           v
[raw WorldEvents: exact, debug/test only]
           |
           v
[ObservationProjector]
   + authorized capture sources/coverage/timing
   + content allowlist + provenance + access rules
           |
           v
[public Observation records] ----> [optional evidence-derived estimates]
           |                                  |
           +-----------------+----------------+
                             |
                    [PlayerView / application]
                          /          \
                 [world renderer]  [HUD / event vignette]
                                  |
                     [optional ProducerActionIntent]
                                  |
                          [application validation]
                                  |
                        [simulation input]
```

**Invariant:** no ordinary player-facing renderer, HUD, dialogue, vignette, save/report export or public callback is handed a `WorldState`, private `WorldEvent` or mutable reference to the underlying contestant dictionaries. The world renderer's 3D scene must not become a shortcut around observed positions or knowledge: source coverage for what the producer can see is itself still an open design question (#16). The renderer can be replaced independently (#4/ADR-0002).

### Candidate interfaces — sketches, NOT final field names

Use plain typed GDScript values or small `RefCounted` classes as needed; a service process, network protocol or database is unnecessary:

- **`WorldState.step(input) -> events`** (*domain-internal*). Applies deterministic contestant/entity behavior; exact private state, causal data and RNG/event order remain accessible only to simulation and privileged tests.
- **`ObservationProjector.project(raw_event, capture_context) -> 0..N observations`** (*the single public-boundary mapping*). `capture_context` is provided by rules/authorized sources, not automatically inferred from the existence of the event. When coverage/access/source validity is unknown or absent, default to **no observation**. It may emit a partial account, not the entire event.
- **`Observation`** (*public view value*). Candidate minimum: stable event/observation ID, in-world occurrence time/tick, delivery/receipt time if different, authorized **source identity/type**, only observed/claimed content and relevant entity IDs. Mark **claims** as claims (e.g., “a witness says X”), not verified hidden truth. Uncertainty/freshness can be added if approved, without creating a mandatory fear percentage.
- **`PlayerViewSnapshot` / `get_observations(since_id)`** (*read-only for world renderer, HUD, reports and text vignettes*). Return detached data with no raw object references or secret fields; do not allow a UI helper to request hidden state by passing an arbitrary entity ID.
- **`ProducerActionIntent`** (*candidate input boundary*). A UI choice expresses an intended producer action by an allowed action ID and public parameters; the application/simulation validates feasibility and applies consequences. A vignette's choice must **not** mutate private world state directly. The repertoire of producer actions is **Issue #16**, not decided here.
- **`PrivateDebugTrace`** (*separate privileged test/development path*). Exact world state/events available only to headless tests and explicitly enabled development diagnostics. Do not include it in production player-view snapshots, ordinary logs, serialized observations or release HUDs.

These are *contracts and example names*, not an enforced schema or permission/security boundary against malicious scripts. GDScript underscore prefixes do **not** make a value truly private. Enforce through narrow APIs, **copying/projection**, code review and tests.

### Data/safety rules to keep the boundary meaningful

1. **Default-deny player observation:** a world event with no valid authorized source yields **no** producer observation, even when the simulation knows exactly what happened.
2. **Only observed properties escape:** a hallway camera could show who entered a door; it does not transmit private motives, speech beyond microphone range or event metadata with nested `private` fields.
3. **Source-grounded claims aren't privileged truth:** a planted local, crew report or contestant testimony can be mistaken, misleading or delayed. Where appropriate, report “X claims Y,” rather than “Y is true.” **Exact reliability, confidence and estimate UI are undecided**.
4. **Time and identity:** observations identify *when information was obtained* and a grounded source; a late report must not magically update earlier player decisions. Temporal semantics and pause rules remain #17.
5. **No shared mutable references:** construct new scalar/approved-content structures. Mutating an observation must not mutate `WorldState`, and subsequent reads must not expose secrets.
6. **Debug is not a player channel:** deterministic internal traces are vital for tests, but no routine HUD, renderer, save/report or release log can query them. If a privileged inspector is ever authorized, gate it explicitly and test its absence in a release build.
7. **No total-information vignette:** off-site narrative windows only show events that reach the producer through an allowed channel. “A contestant secretly spoke with a shopkeeper” is **not** an automatic producer popup unless a staff report, recording, returned testimony or similar authorized evidence exists. A later discovered document can surface past events **at discovery time**, not retroactively to the earlier UI.
8. **Separate simulation results from visual disclosure:** hidden but simulated NPC movements and events must not accidentally appear in a 3D/2D renderer's visible view model. #16 decides camera/surveillance/abstract dollhouse visibility; this ADR does not pre-approve omniscient dollhouse vision.

## Required Issue #3 example: an unwatched conversation

**Illustrative test only, not new authorized mechanics.**

At 19:00, **Contestant A tells Contestant B in an unmonitored pantry**: “I'm going to look for a way out.” The simulation changes B's knowledge and may affect later plans. There is no mic or staff presence in that room. A hallway camera (if such coverage is later approved) might show A and B going in, but nothing of the words exchanged.

| Step | Private truth | Permitted producer-facing record |
| --- | --- | --- |
| 19:00: conversation inside pantry | A plans escape; B has been told | **No transcript; no “A intends escape” fact** |
| 18:59: two people entered pantry, if hallway is covered | A and B passed camera | “A and B seen entering pantry, hall camera, 18:59” (only when source actually covers it) |
| Next morning: C tells a crew member that B mentioned leaving | C makes a report, potentially mistaken | “Crew member reports C claimed B discussed leaving” with receipt time, **not** direct proof of the original plan |
| No source at all | Simulation still resolves the plan | No player observation and no corresponding town/house vignette |

This demonstrates why simply filtering **fields** from a global event is insufficient: **whether the event may be known at all** depends on an independently justified observation source.

## Proposed tests for Issue #5 / subsequent implementation

`godot --headless --path <approved-game-project> --script <test-path>` is an eventual command shape, **not an executed command or approved production path**. Start with a disposable in-process fixture and independent negative tests:

| Test | Expected evidence |
| --- | --- |
| Two seeded runs, same world inputs and capture conditions | Same raw events in privileged harness and same ordered public observations; distinct seeds need not guarantee a specific observed difference |
| Unmonitored private conversation | Changes private knowledge, emits **no** speech/content observation |
| Hall camera observes only door crossing | Reports seen participants/time/location, **not** private intent, plan, fear or audio |
| Unobserved supernatural action | No automatic event popup, exact source/cause or public NPC-knowledge update |
| Misleading/delayed testimony | Public record identifies an **unverified claim** and source/receipt time, not canonical truth |
| Missing, disabled or invalid source | Fail closed; no event or partial private payload to player |
| Nested private data in otherwise observable event | Public serialization contains only allowed fields; recursively forbidden keys/secret references absent |
| Returned view is mutated by caller | World/private trace unchanged; next public read unchanged |
| World renderer/HUD and illustrated event modal | Same authorized player view; no bypass through scene state, modal callbacks, convenience APIs or ordinary logs |
| Headless debug vs shipping mode | Privileged debug can inspect exact truth in tests; production-facing interfaces/exports cannot access a hidden-state inspector |

For the first production proof, **do not** assume exact cameras, remote listeners, automatic fear scoring or any particular UI confidence number. Test the information contract with **synthetic sources** only; a full sensor system and gameplay psychology are outside #3.

## Creative Director decision and outstanding details

**Approved 2026-11-23 (ET):**

1. Private world truth is separated from a **single source-grounded, allowlisted observation projection**. All ordinary player-facing surfaces—including 2D/3D world rendering, UI/HUD, reports and optional illustrated off-site vignettes—consume authorized, detached view data, not raw hidden state.
2. **Unknown or unmonitored details remain withheld.** Indirect testimony and observations are identified as reports or claims, not silently promoted into verified facts; the producer is not omniscient about contestant or supernatural intent.
3. **Explicitly deferred:** approved camera/microphone/crew/town sources, source access rules and any producer knowledge exceptions, presentation of uncertainty or freshness, precise timestamps, player actions, modal pause semantics, exact interface/schema, and contestant behavior variables. These remain #16/#17/#26 and later decisions.

**Approval authority:** Creative Director, in conversation on 2026-11-23 (America/New_York). This approval is **for the information boundary only**. It does not adopt the illustrative sensor system, dictate specific numeric mechanics, authorize production code outside independently approved tasks, or imply that the PR was merged.

## Consequences and follow-up

- Keeps G-06 meaningful while supporting G-02 emergent autonomous behavior and the deceptive competition's misinformation.
- Makes swapping 2D/3D rendering (ADR-0002) less disruptive because both consume authorized view data rather than world internals.
- Simplifies source attribution in optional still-image/text town vignettes and permits private activity to affect later visible events without instant omniscient notifications.
- Imposes some boilerplate for observation projection and fixture tests; this is preferable to scattering privacy filters across all UI components.
- **Issue #5's architectural prerequisites are satisfied by the Creative Director's approval of this boundary and the previously approved engine direction.** Move #5 into implementation only after the ADR is merged/recorded and the normal issue/task authorization is confirmed; a small seeded contestant-decision harness is the intended scope, not a full AI psychology, actual surveillance equipment or producer gameplay system.
- Detailed sensor/reporter privileges need #16; pacing #17; illustrated UI proof #26; contestant-exit outcomes #7; MVP size and content #20. If the human changes any of these in ways that affect source attribution, update this ADR rather than silently weakening G-06.

**Existing feasibility evidence, not proof of this contract:** [Issue #15 headless prototype](../../spikes/issue-4-simulation/README.md) showed deterministic 100-tick repeatability and a copy-only observation projection. It did **not** implement capture coverage, uncertain testimony, production UI, delayed reports or a release-build boundary.
