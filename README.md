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

## Development with AI agents
The project uses **terminal-based OpenCode CLI on Bazzite** and a ChatGPT-connected **cloud coding model**. OpenCode's standard **Build** agent is the validated implementation path; independent read-only review, executable validation, and human acceptance remain required. Local LM Studio models are historical experiments, not the default. The production engine and language have **not** been selected.

See the [agent workflow](docs/agent-workflow.md), [cloud-first decision (ADR-0003)](docs/decisions/ADR-0003-cloud-first-agent-development.md), and [Lead orchestration options](docs/agent-orchestration.md). A **supervised single-issue CLI runner** is now available at [`tools/orchestrate.py`](tools/orchestrate.py), with instructions in the orchestration guide. Its unit tests pass; an actual Build → Reviewer run on the Creative Director's OpenCode 2.4.1 installation is still pending. **Board-driven dispatch is not yet implemented.**