# The Producer

*A game about making haunted houses.*

**Status:** Preproduction · **Working title:** The Producer (final branding undecided) · **Design package:** v0.3.

An isometric psychological-horror management sandbox about running a reality show whose secret purpose is to create genuinely haunted locations. Contestants and supernatural entities act autonomously; you manipulate circumstances, manage imperfect information, and attempt to produce a permanent haunting without destroying the television franchise's credibility.

## For developers and AI agents
1. Read [AGENTS.md](AGENTS.md) before working.
2. Read [Game Vision](docs/vision.md), [Requirements](docs/requirements.md), and relevant [Systems](docs/systems/).
3. Separate CONFIRMED decisions from PROPOSED mechanics and OPEN questions.
4. Work from an approved GitHub issue on a branch; provide tests and an independent review before proposing a merge.

## Delivery roadmap
The [MVP-to-release delivery plan](docs/mvp-delivery-plan.md) maps GitHub issues from design decisions and prototypes to a playable, tested, distributable MVP. The [high-level roadmap](docs/roadmap.md) summarizes phases. Creative Director decision stories can be Ready alongside agent work; Ready does not settle unapproved mechanics.

## Design reference
- [Game design overview](docs/game-design.md)
- [Contestant psychology and observations](docs/systems/contestants-and-observation.md)
- [Supernatural systems](docs/systems/supernatural.md)
- [Seasons and artifacts](docs/systems/seasons-and-artifacts.md)
- [Season outcomes and continuity](docs/systems/season-outcomes-and-continuity.md)
- [Technical architecture constraints](docs/technical-architecture.md)
- [Roadmap](docs/roadmap.md)
- [Issue types, field visibility and priority conventions](docs/project-board-setup.md)
- [Open decisions](docs/open-questions.md)
- [ADR template](docs/decisions/ADR-template.md)

## Local development
OpenCode + LM Studio on Bazzite. **gpt-oss-20b** is the provisional preferred model for Developer, Reviewer, Architect, and Lead, each in a separate task-scoped session. Qwen3-Coder is optional for second opinions; model selection is manual and separate from the agent profile. The engine and language have **not** been selected. See [agent workflow](docs/agent-workflow.md) and [agent model decision (ADR-0001)](docs/decisions/ADR-0001-local-agent-model-selection.md).