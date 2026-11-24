# Development Roadmap and Vertical Slice

> **MVP-to-release tracking:** [MVP delivery and dependency plan](mvp-delivery-plan.md) is the living work-item map, including Creative Director decisions, agent implementation, public-release readiness, and GitHub issue references. This roadmap describes development phases at a higher level; it is **not** the complete MVP backlog.
>
> **Distinction:** The Phase 3 vertical slice is a proof of the player loop. The MVP additionally requires the approved minimum multi-season experience, content, onboarding, save/resume, reliability, accessibility, offline distribution and release acceptance. See Issue #20 for the **unresolved** exact product scope.


## Phase 0 — Local agent reliability
- Verify LM Studio local API and exact model IDs/quantization/context settings on Bazzite (RTX 3080 Ti 12 GB VRAM, 64 GB RAM).
- Evaluate OpenCode + LM Studio with one agent first; measure tool reliability before introducing delegated roles.
- Benchmark Qwen and Gemma models on identical implementation, bug-fix, review and handoff tasks. Do not assume model-role rankings.
- Run agents sequentially initially to avoid VRAM contention. Confirm model switching/unloading behavior rather than assuming it.

## Phase 1 — Approve design boundaries
Review vision, unresolved questions, requirements and technical evaluation criteria. Record approvals in ADRs/issues. No engine choice yet.

## Phase 2 — Engine spikes
Implement small, throwaway proofs for headless simulation, isometric view, event observation, save/load and testing. Select engine based on measured results and human approval.

## Phase 3 — Vertical slice [PROPOSED scope]
- One house with roughly 5–7 rooms; four differentiated contestants.
- Pausable time, a handful of staged scares, observation-based player interface.
- Fear, beliefs/suspicion, basic social information exchange and voluntary quitting.
- One autonomous supernatural entity that may act against producer goals.
- At least one contestant countermeasure (avoidance or attempted banishment).
- One possible autonomous entity, a binary persistent-haunting outcome report, and save/load. No survival or operational-viability gate.
- Headless simulation and QA inspector.
These are sizing suggestions, not approved feature counts.

## Phase 4 — Expand systems
Distinct houses, cast variation, deeper autonomy, artifact generation/inheritance, pacing and narrative content.

## Phase 5 — Stabilization
Performance, accessibility, balance, regression testing, content polish, packaging and external playtesting.

## First candidate GitHub issues
1. Approve vision and design invariants.
2. Define observable vs private contestant data contract.
3. Establish local model benchmark harness.
4. Compare engine prototypes.
5. Implement seeded contestant decision test harness.
6. Implement one supernatural entity and one contestant response scenario.
7. Validate artifact-free season completion feasibility.
8. Prototype post-operation haunting persistence evaluation; no operational-viability subsystem or death quota.

## Evidence standard
Each milestone requires executable proof, recorded tests, reproducible instructions, known risks and a human approval decision where relevant.