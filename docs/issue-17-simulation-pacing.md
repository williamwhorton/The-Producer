# Issue #17 — Simulation pacing and player time controls

Status: Creative Director approved qualitative direction (issue discussion); numerical tuning and implementation remain open.

## Alternatives considered

- Pausable real-time: contestants act independently while the producer observes and triggers effects; pause to plan, then resume. Organic timing and competing attention, without requiring fast interface operation.
- Discrete turns: review positions, choose a telephone trigger, advance a turn and observe reactions. Easier planning but artificial behavioral rhythm.
- Hybrid: contestants move continuously until designated decision periods interrupt play. Structured opportunities but disruptive transitions and additional complexity.

## Decision

Use pausable real-time with unrestricted tactical pause and normal, fast and very fast running speeds. Exact multipliers and tick duration are open. Speed changes wall-clock progression, not simulation rules. No automatic event-based pause, slowdown or significance alerts. The player notices events through source-authorized surveillance and communications; ordinary speech bubbles indicate activity, not importance. Direct communications may naturally attract attention. Off-site vignette presentation remains a UI question; no omniscient event feed.

While paused, observe existing state, inspect dossiers and attended history, change listening focus and queue/cancel live interventions. No autonomous movement, decisions, new speech, psychological progression or recovery occurs. Missed information cannot be recovered. Manual live triggers execute during running time or on the next eligible update after resume; validate prerequisites and resources at execution, resolve competing commands consistently. No future-time or conditional scheduling. Passive prepared effects remain autonomous.

Day and night are fully simulated. Curfew is a contest rule, not a movement restriction; contestants may violate it. Overnight minor alterations are available only while paused during curfew, directly through the normal interface, with no separate planning phase. Valid alterations execute unseen, one slot each from the fixed nightly allowance, across multiple pauses. No stealth checks. Live triggers retain normal rules. Pre-contest preparation remains untimed.

## Creative direction

The producer is a participant in the horror, not omniscient. Genuine supernatural activity should create uncertainty and threaten perceived control. Rare contextual producer-directed intrusions, contestant recognition or deception, equipment/interface interference and fourth-wall breaks are possible future capabilities, not vertical-slice commitments. They must be surprising, varied, neither guaranteed nor reliable strategic mechanics, and should not be advertised in advance. Preserve trust in actual software and persistence. Continuous real-time/restricted pause, timed or conditional triggers and opportunity-based overnight staging are deferred candidates.

## Technical implications and validation

Keep simulation updates separate from rendering and observation. For proposed T-01, test seeded runs with identical initial state and ordered simulation-time commands at different render speeds; pause duration must not change outcomes. AI decisions must not advance while paused; asynchronous results must be applied at controlled simulation boundaries, with reproducible fixtures or recorded decisions for tests. Do not promise deterministic external model inference.

Vertical-slice acceptance scenarios:
1. Observe two concurrent conversations; pause, change focus, resume; no new or retroactive speech while paused.
2. Queue and cancel triggers; resume and validate physical prerequisites and resources; verify consistent command ordering.
3. Compare seeded runs at different speeds and pause durations with equivalent commands.
4. Observe a contestant packing or an unexplained event without automatic notification, pause or slowdown.
5. During curfew, pause and stage valid changes across multiple pauses; enforce nightly allowance and reject staging outside curfew or while running.
6. A contestant violates curfew without blocking valid unseen staging; ordinary nighttime activity and live effects continue.
7. Verify observation projection does not expose private state or label unexplained events as supernatural without evidence.

Affected requirements: O-05/O-06/O-07, A-03/A-05/A-08/A-10, T-01/T-03; observation and action ADRs 0004–0006 remain applicable. Exact season length, curfew hours, slot count, reset/carryover details, reaction windows, speed multipliers and implementation architecture details remain open.
