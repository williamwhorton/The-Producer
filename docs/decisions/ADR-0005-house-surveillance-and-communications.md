# ADR-0005 — House surveillance, conversations, and communications

**Status:** APPROVED — partial Creative Director decision under Issue #16; producer **observation only** (2026-11-23, America/New_York). The rest of #16's producer actions and mechanics remain OPEN.  
**Date:** 2026-11-23  
**Owner:** Creative Director (decision); Architect/Lead (documentation)  
**Issue:** [#16 — Producer actions and surveillance](https://github.com/williamwhorton/The-Producer/issues/16)  
**Requirements:** G-01, G-02, G-03, G-06; O-01–O-07 (approved observation requirements); T-03 / [ADR-0004](ADR-0004-producer-observation-boundary.md).

## Context

The game is viewed through a fixed-angle house/dollhouse presentation, while [ADR-0004](ADR-0004-producer-observation-boundary.md) prohibits revealing private contestant/world state without a legitimate source. The Creative Director has now selected **hidden house surveillance** as the in-world explanation for the producer's ability to see the house. This decision reduces the need for camera-coverage puzzles, but does not make the producer omniscient about minds, off-site actions, unsaid intentions, or the supernatural.

## Options and tradeoffs

**A. Sparse/positionable cameras:** makes sensor management a gameplay system and creates blind spots, but contradicts the Creative Director's stated goal that the player can see *all rooms*, adds setup/maintenance complexity, and risks obscuring the basic house gameplay.

**B. Established hidden surveillance with complete room visibility (APPROVED):** supports an intuitive always-visible dollhouse, lets players attend to behavior rather than camera placement, and maintains a diegetic basis for in-house observations. The tradeoff is fewer in-house secrets and potentially greater event/UI information volume; meaningful uncertainty instead comes from motivations, interpretation, off-site events, unreliable statements and any *separately approved* interference.

**Implementation constraint:** the dollhouse view can represent a composite surveillance perspective. It need **not** reproduce literal camera angles, sight cones or feed mosaics. No camera-placement gameplay, switchable feed mechanic, surveillance failure or signal interference has been approved.

## Approved decisions — observation slice of #16

1. **All rooms are visible.** Hidden cameras let the producer/player see what is physically happening in **every room of the house**. This justifies the overall dollhouse view. It does **not** expose private contestant thoughts, motives, beliefs or hidden causes of events. Exact treatment of hallways, stairs, exterior/property grounds, sightline occlusion and supernatural camera interference is **not specified** by this approval; do not make those a source of arbitrary blind spots in confirmed rooms.
2. **Audible environmental events.** The producer can hear relevant sounds originating in the house, including (for example) doors opening or shutting. This is perceptible sound/event feedback, not hidden psychological truth. Exact sound mix, distance, indicators and whether all sounds reach the player at every zoom level are **OPEN**.
3. **Conversation bubbles with on-demand text.** When contestants speak to each other in the surveilled house, a visible conversation bubble indicates the interaction. **The player clicks the bubble to reveal the text/details of what is said.** Speech is made accessible by the house's surveillance/audio setup, not by inspecting `PrivateContestantState`. The player does **not** see the text by default merely because a conversation started. The content can be mistaken, deceptive, partial, or otherwise different from the speaker's private belief. **Follow-up approved direction:** listening is **selective and live**. With multiple conversations ongoing, the producer chooses which bubble to focus on; **unattended dialogue is missed** rather than silently transcribed into a universal readable backlog. Opening/focusing a bubble does **not automatically pause time** or make other conversations available for catch-up. Exactly how to display text as it is spoken, how focus changes, and whether the player has separate manual time controls remain OPEN (#17/#26). **Approved follow-up:** dialogue portions the player actually attends to (including the observable portion of a house-phone call) **are saved as text and remain readable at any later time**. All other speech remains unrecorded in player-accessible history. Surveillance video and uncaptured audio **cannot be replayed**; video recording is a possible **future feature, not part of this baseline**. The precise UI display, storage implementation, focus-switch boundaries and any separate manual time controls remain OPEN.
4. **One shared house telephone; cell phones prohibited.** Contestants have access to **one house phone**; competition rules **do not allow cell phones**. Phone use is another visible/clickable interaction: a bubble appears and clicking it gives text/details for the observed telephone interaction rather than automatically exposing the contents. Whether the producer hears both ends of calls, how the phone is monitored, **call metadata logs (as distinct from the approved attended-only dialogue text)**, calls to the outside world, and enforcement or possible violations of the no-cell-phone rule remain **OPEN**. Do not treat a ban as a guarantee no one could ever secretly obtain a phone.

These approvals define a **baseline observation experience**, not a finalized actor AI system, sound production plan, conversation mechanic, phone interception rule, full transcript storage, UI art style, or simulation pacing model.

## Attention as a gameplay constraint — approved live focus, attended-only text history

The Creative Director selected **live attention management** as part of the challenge: the house can have several simultaneous, visible conversation bubbles, but the player cannot inspect every concurrent exchange simply by opening a pause menu or an automatic transcript archive. **Choosing a bubble means choosing to listen**; only dialogue within the selected interaction and the time the player actively attends to it is disclosed as text. A simultaneous, unselected conversation remains visible as an event and its participants' physical behavior remains visible in the dollhouse, but **its words are not retroactively available to the player** through a catch-up query.

This is **not** the same as an environmental microphone failing: the house's surveillance supplies an authorized speech source; the *player's selection* determines which of the otherwise captured streams becomes an **attended, player-readable** interaction. Access to a specific on-click dialogue excerpt must be mediated by the authorized observation/application layer and focus/temporal state, not by a UI reading the complete simulation conversation log.

**Approved:** retain **only spoken dialogue the player actually listened to** as a persistent, player-readable **text history**, including the available portion of an attended house-phone call. This history may be read **at any later time**. Unselected speech is never retroactively reconstructed from the house's theoretical camera/audio coverage, a debug event log, or any later rewind. A player changing focus mid-conversation should only capture the portions witnessed during each focus interval; the exact timestamp granularity and presentation remain for #26. Phone focus and house conversation focus **compete for the same single listening attention**—the producer cannot read two live conversation streams simultaneously. The **remote end of a telephone call remains accessible only to whatever extent separate phone monitoring rules eventually approve**.

**Approved:** ordinary surveillance **cannot be replayed**—no video rewind, replayed live audio, or automatic retroactive dialogue. **Possible future mechanic, NOT approved now:** recording surveillance video as a limited or separately acquired producer capability. Whether reading saved dialogue requires pausing by manual choice or appears in a non-pausing panel is a #17/#26 interaction decision; opening a live bubble does not automatically pause the world.

The time cost is intentionally meaningful: selecting a bubble **does not automatically freeze the world** or create a special pause to review every missed conversation. This does **not** decide the game's separate general pause/simulation-speed model under #17. Do not use a universal transcript backlog to defeat the intended observation challenge.

## Compatibility with ADR-0004 (APPROVED)

The producer's source for visible house actions is the **established camera coverage**; for conversations, audible events and telephone interactions, it is the **authorized house surveillance/communications channel**. The observation projector emits detached, content-allowlisted records/available dialogue, not references to mutable simulation objects.

**Two boundaries must not be confused:**

- **Access to speech:** the producer can click an in-house conversation bubble to inspect **what contestants actually said**, as captured in the house. This is a legitimate observed event, even when contestants hoped it would be private. It supersedes the *illustrative* “unmonitored pantry conversation” example **for rooms in the newly confirmed complete-coverage house**; that scenario still tests the default-deny rule in an explicitly *unmonitored off-site or synthetic* environment.
- **Access to inner thoughts:** hearing “I'm fine” does **not** tell the producer whether a contestant is truly calm. Spoken intentions, phone calls, and reports aren't guaranteed truths about a participant's current plan, actual belief or later actions.

Outside the house, e.g. town visits portrayed as proposed illustrated event vignettes, no automatic access to conversations is granted. Those need separately grounded sources. The renderer cannot cheat by accessing raw NPC data; it receives authorized snapshots and interaction metadata from the application/observation boundary.

## Minimal possible view/event examples (illustrative, NOT schema)

- **House visual:** `seen_in_room(contestant_id, room_id, tick, source=house_cameras)` may support the dollhouse actor display. The actual implementation may be a state snapshot rather than an event log.
- **House sound:** `door_sound(door_id, event_time, source=house_audio)` may produce audible feedback. Do not infer unseen intentions or the precise hidden cause.
- **Conversation and telephone:** `conversation_indicator(conversation_id, participants?, room_id, source=house_audio)` or a house-phone bubble advertises a live stream. `focus_audio_stream(stream_id, time)` represents the **one active speech/call focus at a time**; `get_live_attended_dialogue(stream_id)` only gives authorized words heard while focused. Approved attended text **is preserved in an attended-only readable history**, available later; neither query may retrieve unselected speech or replay surveillance video/audio. These are conceptual names only, not approved API signatures or NPC-memory queries.
- **Telephone:** `phone_in_use(phone_id, caller?, source=house_phone)` can render a clickable bubble; `get_observed_phone_dialogue(call_id)` exposes only what the chosen phone-observation rules permit, **not yet defined as both parties' full conversation**.

These names are placeholders. World renderer/UI must not receive private world objects or invent extra observed content.

## Proposed checks for later implementation

1. With synthetic coverage of every test room, visible in-house occupants appear in authorized player-view records at the correct location, without raw beliefs or plans.
2. Door opening/shutting generates an audible/visible-sound cue with plausible source; an unobserved *off-site* door does not automatically produce one.
3. In-house speech creates a bubble. The player-view has no full dialogue in its default rendered text; focusing/clicking reveals **only the spoken text during the active focus window**, without revealing the speaker's private truth; no automatic pause starts.
4. Phone use generates a phone interaction indicator and **competes for the same exclusive listening focus** as other speech bubbles. Its on-click text and later attended-only text history are limited to the **separately defined monitored portion** of the call; do not grant the producer the remote side automatically.
5. No second house telephone or ordinary contestant cell-phone use exists under default scenario constraints; do not assume enforcement/contraband behavior is finalized.
6. Attempts to access private state or **unattended transcript content** via a bubble ID, arbitrary time range, actor/node reference, a phone callback or transcript endpoint fail; the observation/application boundary enforces focus/time restrictions for ordinary player views.
7. With **two simultaneous in-house conversations**, selecting A yields only A's words during the actual focus interval; B's speech is never player-retrievable (even if a raw/debug trace contains it). **Attended A text is saved and can be reread at any later time**.
8. With a **house phone call concurrent with an in-room conversation**, selecting the phone excludes the other conversation from readable records during that interval, and vice versa. No speculative remote-party transcript may leak.
9. Attempting to replay **unrecorded surveillance video/audio** or obtain a retroactive total transcript fails; a future video-recording system must receive separate explicit mechanic approval.
10. A purely private thought or off-site conversation remains hidden unless the producer has a valid separate source.
8. The approved 3D dollhouse view works without implementing camera devices, a camera placement minigame or literal camera feed screens.

This ADR is a **human-approved design record, not proof** that the current Godot prototype implements any of these rules. No gameplay implementation or automated test was run for the documentation decision.

## Unresolved next decisions

- Which **producer actions/interventions** are selectable, how they are prepared, and what the contestant simulation decides independently (**remaining #16 acceptance criteria**).
- Exact live text presentation, focus switching/interruptions, archive UX, what counts as actually witnessed, and accessibility equivalents. The **attended-only persistent text history and single shared focus across speech + phone are approved**. No surveillance replay is available at baseline; video recording is only a later mechanic candidate. Focus does not itself auto-pause; separate manual pause/speed rules remain #17/#26.
- What part of a telephone call can be heard, how calls are triggered, whether the producer can interfere with them, and whether contestants could violate the phone ban (**#16 / #7**).
- Sound alerts, accessibility alternatives (captions), on-screen density and spatial audio (**#26 / #21 / #22**).
- How cameras cover hallways, outdoor areas, and whether there can be in-world sabotage or supernatural disruption (**#16 if proposed later**).

**Approval reference:** Creative Director explicitly set these house-view, sound, speech bubble, single-phone and no-cell-phone rules, then approved **selective real-time attention without automatic catch-up/pause** and, subsequently, **shared phone/conversation focus, permanently rereadable attended-only text, and no baseline surveillance replay**, in the discussion of Issue #16 on 2026-11-23 ET. **Surveillance video recording is only a future candidate.** Approval applies **only** to these listed observations. **Issue #16 stays open** pending actions/interventions and remaining decisions.
