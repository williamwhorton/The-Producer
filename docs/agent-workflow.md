# Local AI-agent workflow

**Status:** Initial, manually coordinated and subject to validation.

## Environment
- Bazzite Linux; LM Studio provides the local OpenAI-compatible endpoint.
- OpenCode Desktop is installed as Flatpak. Project agents live in `.opencode/agents/` within the checked-out repository. Verify that Desktop discovers them.
- Never commit host-specific paths, tokens, model weights or credentials.
- The selected model is separate from the agent profile unless an exact `provider/model` ID is explicitly set. Model IDs are intentionally not hard-coded.

## Provisional assignments
- `producer-developer` — Gemma 4 12B QAT, implementation and tests.
- `producer-reviewer` — Qwen3.5 9B, independent QA.
- `producer-architect` — architecture and engine comparisons.
- `producer-lead` — requirements, issue breakdown and handoffs.

## Issue intake and triage
Follow [GitHub issue types, fields and priority conventions](project-board-setup.md).

- Issue Types: **Feature**, **Bug**, **Task**, **Spike**, **Design Decision**. Types affect expected deliverables; Workstream is a separate domain classification.
- Priority: **Urgent / High / Medium / Low**, not P0/P1/P2. A High-priority issue can still be Blocked.
- Before starting an issue, check its **Type, Status, dependencies and Human Approval Required** field, plus approval evidence in the issue/ADR. A missing or incorrectly set field never overrides the Creative Director's approval authority.
- Handle **Spikes** as evidence gathering; handle **Design Decisions** as proposed choices requiring recorded human approval. Do not treat a promising prototype or a proposed decision as authorization for production code.
- Do not infer arbitrary effort values, due dates, approvals or requirement changes. Use issue fields where available and report any missing decision instead.

## Manual development cycle
1. Human approves bounded GitHub issue and acceptance criteria.
2. Developer uses a fresh session on a feature branch; reads relevant docs, implements and executes tests.
3. Developer reports exact checks, results, commit and limitations.
4. Reviewer independently examines actual code/diff against requirements in a fresh session; no modifications during review.
5. Developer addresses substantiated findings and reruns checks.
6. Human reviews the PR; no automatic merge while workflow is being validated.

## Gemma-specific reliability
Gemma previously confused restricted JavaScript `execute` with dedicated file/shell tools. The developer profile explicitly instructs direct `read`, `glob`, `grep`, `shell`, and `write`/`edit` usage. Never use Node.js `require("fs")` for filesystem access. Confirm stability over longer tasks.

## Context and safety
- Use one active model workload at a time until VRAM/model switching is validated.
- Keep durable context in versioned docs, issues, ADRs, tests and PRs, not long conversations.
- Never turn an illustrative mechanic into an approved requirement.
- Do not silently add dependencies, publish releases, merge into main, or use paid cloud services.
- Independent testing is required; self-authored green tests alone are not acceptance evidence.
