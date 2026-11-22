# The Producer

*A game about making haunted houses.*

**Status:** Preproduction · **Working title:** The Producer (final branding undecided) · **Design package:** v0.3.

An isometric psychological-horror management sandbox about running a reality show whose secret purpose is to create genuinely haunted locations. Contestants and supernatural entities act autonomously; you manipulate circumstances, manage imperfect information, and attempt to produce a permanent haunting without destroying the television franchise's credibility.

## For developers and AI agents
1. Read [AGENTS.md](AGENTS.md) before working.
2. Read [Game Vision](docs/vision.md), [Requirements](docs/requirements.md), and relevant [Systems](docs/systems/).
3. Separate CONFIRMED decisions from PROPOSED mechanics and OPEN questions.
4. Work from an approved GitHub issue on a branch; provide tests and an independent review before proposing a merge.

## Design reference
- [Game design overview](docs/game-design.md)
- [Contestant psychology and observations](docs/systems/contestants-and-observation.md)
- [Supernatural systems](docs/systems/supernatural.md)
- [Seasons and artifacts](docs/systems/seasons-and-artifacts.md)
- [Season outcomes and continuity](docs/systems/season-outcomes-and-continuity.md)
- [Technical architecture constraints](docs/technical-architecture.md)
- [Roadmap](docs/roadmap.md)
- [Open decisions](docs/open-questions.md)
- [ADR template](docs/decisions/ADR-template.md)

## Local development
OpenCode + LM Studio on Bazzite. Provisional agent roles: Gemma 4 12B QAT for architecture/implementation; Qwen3.5 9B for independent review. Model assignments are provisional and must be selected/verified in each desktop session. The engine and language have **not** been selected. See [agent workflow](docs/agent-workflow.md).