# ADR-0003 — Cloud-first AI-agent development

**Status:** Approved (Creative Director)
**Date:** 2026-11-23
**Owner:** Creative Director
**Supersedes:** [ADR-0001 — Local AI-agent model selection](ADR-0001-local-agent-model-selection.md)
**Related work:** [Issue #13](https://github.com/williamwhorton/The-Producer/issues/13), [Issue #4](https://github.com/williamwhorton/The-Producer/issues/4)
**Scope:** AI tools used **to develop** The Producer; **not** the shipped game's inference/runtime architecture or the pending engine decision.

## Context

ADR-0001 provisionally chose local models (via LM Studio/OpenCode) for development and review on a Bazzite machine with RTX 3080 Ti 12 GB VRAM and 64 GB RAM. That choice was economical in API charges but did not reliably produce working Godot UI artifacts. During the Issue #13 2D prototype work, the local development setup repeatedly failed to generate an independently launchable, visibly correct main scene despite reading Godot errors and receiving substantial human debugging help. Local reviews sometimes invented requirements (WASD control, supernatural behavior) and missed real defects (e.g., grid/scene issues).

On 2026-11-23 the Creative Director ran a small, intentionally isolated comparison using **OpenCode standard Build** with a **cloud coding model accessed through ChatGPT sign-in**. The reported result was a runnable minimal Godot project with visible labeled markers, independently inspected, completed in approximately **two minutes** without developer intervention beyond normal tool approvals.

Both the model and agent profile changed, and the two efforts were not a controlled benchmark. The successful test supports choosing the demonstrated workflow as a practical default; it does not prove large-feature autonomy or attribute all gains to the model alone.

## Decision

1. Adopt **cloud-first AI assistance** for routine implementation, planning, architecture analysis and review. Local LM Studio inference is not a required dependency or preferred default.
2. Default to **OpenCode's standard Build role with a ChatGPT-connected cloud coding model** for implementation and self-debugging. Model names may vary with plan availability; verify the selected provider and model at each session start rather than hard-coding a model ID.
3. Keep the Lead, Architect and Reviewer roles conceptually separate. Use **fresh task-scoped sessions** and read-only reviewer permissions. Same-model independent review is acceptable when grounded in the original requirements, actual diff and test evidence; no cross-model requirement.
4. Make **executable self-verification** a gate before review: run relevant CLI checks, make the project independently launchable, and verify GUI observations where possible. If visual inspection is unavailable, disclose that limit and require a human check; never assert visual success from scene definitions alone.
5. Use **the existing ChatGPT subscription allowance** first. Do not introduce pay-as-you-go APIs, additional subscriptions, automatic recharges or charges without explicit Creative Director approval.
6. Preserve human authority over scope, major technical choices, visual acceptance, PR merges and all game-design decisions. The engine evaluation under Issue #4 remains open; do not infer approval of any production engine, service, protocol or in-game cloud model.

## Alternatives considered

- **Continue fully local:** zero added model API charges, but repeated Godot implementation/debugging failures required disproportionate human time.
- **Use local models for routine review and cloud only for emergency debugging:** feasible later, but not the current default because review reliability and handoff overhead are unproven.
- **Use direct paid cloud APIs immediately:** unnecessary while the existing ChatGPT-connected setup works; may be reconsidered with a measured cost cap and explicit approval.
- **Abandon agent role separation:** not needed. Maintain independent issue checks, fresh review sessions and human approval, while using the known-working Build implementation path.

## Consequences and follow-up

- Lower operational complexity: no routine loading/offloading, prompt-template troubleshooting or context contention from local reviewer/developer models.
- Cost is controlled initially by existing subscription access, but plan usage limits are real. Subscription access is **not** equivalent to unlimited API credit. Unexpected billing or provider changes are stop-and-escalate events.
- Small Godot smoke-test success is only a baseline. For Issue #13 resume from an isolated, clean development branch and test bounded functional milestones; preserve the existing incomplete PR #70 until explicitly resolved. Record actual launch/test output, visible behavior, elapsed time, human intervention and unmet criteria. Do not merge on self-reported success alone.
- The repository's custom `producer-developer` and `producer-reviewer` profiles remain available but are not validated substitutes for OpenCode Build. Verify permissions and tool availability before using them.
- Any requirements concerning cloud inference or external service use **inside the shipped game** remain separately governed; this ADR authorizes cloud **development tools only**.
- Revisit the decision if the cloud workflow fails repeatedly at real project tasks, plan limits impede delivery, or measured per-deliverable cost becomes unacceptable. Preserve ADR-0001 as historical evidence rather than rewriting its earlier rationale.
