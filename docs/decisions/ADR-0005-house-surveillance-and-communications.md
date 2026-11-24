# ADR-0005 — House surveillance, conversations, and communications

**Status:** APPROVED — partial Creative Director decision under Issue #16; producer **observation only** (2026-11-23, America/New_York). The rest of #16's producer actions and mechanics remain OPEN.  
**Date:** 2026-11-23  
**Owner:** Creative Director (decision); Architect/Lead (documentation)  
**Issue:** [#16 — Producer actions and surveillance](https://github.com/williamwhorton/The-Producer/issues/16)  
**Requirements:** G-01, G-02, G-03, G-06; O-01–O-04 (new approved observation requirements); T-03 / [ADR-0004](ADR-0004-producer-observation-boundary.md).

## Context

The game is viewed through a fixed-angle house/dollhouse presentation, while [ADR-0004](ADR-0004-producer-observation-boundary.md) prohibits revealing private contestant/world state without a legitimate source. The Creative Director has now selected **hidden house surveillance** as the in-world explanation for the producer's ability to see the house. This decision reduces the need for camera-coverage puzzles, but does not make the producer omniscient about minds, off-site actions, unsaid intentions, or the supernatural.

## Options and tradeoffs

**A. Sparse/positionable cameras:** makes sensor management a gameplay system and creates blind spots, but contradicts the Creative Director's stated goal that the player can see *all rooms*, adds setup/maintenance complexity, and risks obscuring the basic house gameplay.

**B. Established hidden surveillance with complete room visibility (APPROVED):** supports an intuitive always-visible dollhouse, lets players attend to behavior rather than camera placement, and maintains a diegetic basis for in-house observations. The tradeoff is fewer in-house secrets and potentially greater event/UI information volume; meaningful uncertainty instead comes from motivations, interpretation, off-site events, unreliable statements and any *separately approved* interference.

**Implementation constraint:** the dollhouse view can represent a composite surveillance perspective. It need **not** reproduce literal camera angles, sight cones or feed mosaics. No camera-placement gameplay, switchable feed mechanic, surveillance failure or signal interference has been approved.

## Approved decisions — observation slice of #16

1. **All rooms are visible.** Hidden cameras let the producer/player see what is physically happening in **every room of the house**. This justifies the overall dollhouse view. It does **not** expose private contestant thoughts, motives, beliefs or hidden causes of events. Exact treatment of hallways, stairs, exterior/property grounds, sightline occlusion and supernatural camera interference is **not specified** by this approval; do not make those a source of arbitrary blind spots in confirmed rooms.
2. **Audible environmental events.** The producer can hear relevant sounds originating in the house, including (for example) doors opening or shutting. This is perceptible sound/event feedback, not hidden psychological truth. Exact sound mix, distance, indicators and whether all sounds reach the player at every zoom level are **OPEN**.
3. **Conversation bubbles with on-demand text.** When contestants speak to each other in the surveilled house, a visible conversation bubble indicates the interaction. **The player clicks the bubble to reveal the text/details of what is said.** Speech is made accessible by the house's surveillance/audio setup, not by inspecting `PrivateContestantState`. The player does **not** see the text by default merely because a conversation started. The content can be mistaken, deceptive, partial, or otherwise different from the speaker's private belief. Specific transcript completeness, retention, interruptions, click range, player time-pausing and dialogue UX are **OPEN**.
4. **One shared house telephone; cell phones prohibited.** Contestants have access to **one house phone**; competition rules **do not allow cell phones**. Phone use is another visible/clickable interaction: a bubble appears and clicking it gives text/details for the observed telephone interaction rather than automatically exposing the contents. Whether the producer hears both ends of calls, how the phone is monitored, call logs, calls to the outside world, and enforcement or possible violations of the no-cell-phone rule remain **OPEN**. Do not treat a ban as a guarantee no one could ever secretly obtain a phone.

These approvals define a **baseline observation experience**, not a finalized actor AI system, sound production plan, conversation mechanic, phone interception rule, full transcript storage, UI art style, or simulation pacing model.

## Compatibility with ADR-0004 (APPROVED)

The producer's source for visible house actions is the **established camera coverage**; for conversations, audible events and telephone interactions, it is the **authorized house surveillance/communications channel**. The observation projector emits detached, content-allowlisted records/available dialogue, not references to mutable simulation objects.

**Two boundaries must not be confused:**

- **Access to speech:** the producer can click an in-house conversation bubble to inspect **what contestants actually said**, as captured in the house. This is a legitimate observed event, even when contestants hoped it would be private. It supersedes the *illustrative* “unmonitored pantry conversation” example **for rooms in the newly confirmed complete-coverage house**; that scenario still tests the default-deny rule in an explicitly *unmonitored off-site or synthetic* environment.
- **Access to inner thoughts:** hearing “I'm fine” does **not** tell the producer whether a contestant is truly calm. Spoken intentions, phone calls, and reports aren't guaranteed truths about a participant's current plan, actual belief or later actions.

Outside the house, e.g. town visits portrayed as proposed illustrated event vignettes, no automatic access to conversations is granted. Those need separately grounded sources. The renderer cannot cheat by accessing raw NPC data; it receives authorized snapshots and interaction metadata from the application/observation boundary.

## Minimal possible view/event examples (illustrative, NOT schema)

- **House visual:** `seen_in_room(contestant_id, room_id, tick, source=house_cameras)` may support the dollhouse actor display. The actual implementation may be a state snapshot rather than an event log.
- **House sound:** `door_sound(door_id, event_time, source=house_audio)` may produce audible feedback. Do not infer unseen intentions or the precise hidden cause.
- **Conversation:** `conversation_indicator(conversation_id, participants?, room_id, source=house_audio)` is presented as a clickable bubble; `get_observed_dialogue(conversation_id)` may retrieve only the captured spoken text, subject to any *later approved* timing/retention rule. It is not a query for NPC memories or intentions.
- **Telephone:** `phone_in_use(phone_id, caller?, source=house_phone)` can render a clickable bubble; `get_observed_phone_dialogue(call_id)` exposes only what the chosen phone-observation rules permit, **not yet defined as both parties' full conversation**.

These names are placeholders. World renderer/UI must not receive private world objects or invent extra observed content.

## Proposed checks for later implementation

1. With synthetic coverage of every test room, visible in-house occupants appear in authorized player-view records at the correct location, without raw beliefs or plans.
2. Door opening/shutting generates an audible/visible-sound cue with plausible source; an unobserved *off-site* door does not automatically produce one.
3. In-house speech creates a bubble. The player-view has no full dialogue in its default rendered text; clicking requests the captured spoken text without exposing the speaker's private truth.
4. Phone use generates a phone interaction indicator; its on-click detail is limited to the **separately defined monitored portion** of the call.
5. No second house telephone or ordinary contestant cell-phone use exists under default scenario constraints; do not assume enforcement/contraband behavior is finalized.
6. Attempts to access private state via the bubble's ID, actor/node reference, a phone UI callback or a transcript endpoint fail; the same independent observation service feeds UI and renderer.
7. A purely private thought or off-site conversation remains hidden unless the producer has a valid separate source.
8. The approved 3D dollhouse view works without implementing camera devices, a camera placement minigame or literal camera feed screens.

This ADR is a **human-approved design record, not proof** that the current Godot prototype implements any of these rules. No gameplay implementation or automated test was run for the documentation decision.

## Unresolved next decisions

- Which **producer actions/interventions** are selectable, how they are prepared, and what the contestant simulation decides independently (**remaining #16 acceptance criteria**).
- Full in-house audio/transcript availability vs practical UI filtering; live-only versus replayable logs; whether inspection pauses time (**#17 / #26**).
- What part of a telephone call can be heard, how calls are triggered, whether the producer can interfere with them, and whether contestants could violate the phone ban (**#16 / #7**).
- Sound alerts, accessibility alternatives (captions), on-screen density and spatial audio (**#26 / #21 / #22**).
- How cameras cover hallways, outdoor areas, and whether there can be in-world sabotage or supernatural disruption (**#16 if proposed later**).

**Approval reference:** Creative Director explicitly set these house-view, sound, speech bubble, single-phone and no-cell-phone rules in the discussion of Issue #16 on 2026-11-23 ET. Approval applies **only** to these listed observations. **Issue #16 stays open** pending actions/interventions and remaining decisions.
