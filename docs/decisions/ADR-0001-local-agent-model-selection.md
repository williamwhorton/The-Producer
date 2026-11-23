# ADR-0001 — Local AI-agent model selection

**Status:** Superseded on 2026-11-23 by [ADR-0003 — Cloud-first AI-agent development](ADR-0003-cloud-first-agent-development.md) (historical record retained)
**Date:** 2026-11-22
**Owner:** Creative Director
**Related issue:** [#2](https://github.com/williamwhorton/The-Producer/issues/2)
**Scope:** Development tooling only; this is not a choice of gameplay runtime or game engine.

## Context
The project uses OpenCode Desktop with locally hosted models in LM Studio on Bazzite (RTX 3080 Ti 12 GB VRAM, 64 GB RAM). The practical priority is reliable task completion, useful tools, correctness and maintainability; inference speed matters after those.

Initial experiments showed Gemma 4 12B QAT could produce concise code but suffered repeated tool-call loops, malformed tool attempts, and incomplete tasks. Qwen3.5 9B produced a mixed review with genuine and speculative findings. A larger Qwen3-Coder model completed an independent review but took ~42 minutes for a small utility and overstated unproven issues.

The developer model **gpt-oss-20b** completed the same Markdown checker assignment in ~12 minutes, with no reported loops or tool failures, and reported passing tests. Qwen3-Coder later reported **seven passing tests** and an overall approval, albeit with questionable high-priority findings. Evidence came from local sessions reported by the Creative Director and is not independently rerun as part of this ADR.

## Decision
Use **gpt-oss-20b as the preferred model for Developer, Reviewer, Architect, and Lead** for initial game work. Maintain separate project-local agent profiles, permissions, and **fresh sessions** for each role. Do **not** hard-code an LM Studio provider/model identifier until the actual locally available ID is confirmed; select the model in OpenCode per session.

Reserve **Qwen3-Coder-30B-A3B-Instruct** for optional second opinions when complexity, risk, or suspected shared blind spots warrant the cost. Do not assign Gemma or Qwen3.5 9B to the active default workflow.

## Alternatives
- **Gemma 4 12B QAT:** previously preferable code economy; rejected as default due to repeated tool reliability failures.
- **Qwen3.5 9B:** available and faster; its initial review had false positives and omitted known issues.
- **Qwen3-Coder-30B-A3B-Instruct:** completed a review using its own model family but was much slower; use selectively.
- **Dedicated reviewer model:** defer selection until observed problems justify renewed evaluation.

## Consequences and controls
- Simpler operation: one preferred local model, less switching/offload overhead.
- Limitation: same-model review can miss shared mistakes; a fresh session does not eliminate model-family correlation.
- Reviewer must inspect actual code, run permitted tests, present reproducible findings and distinguish defects from speculative concerns.
- Human approval remains mandatory for significant creative/architectural choices and merging PRs. Model review is not GitHub approval from another user.
- Keep benchmarks lightweight. Revisit the model roster only when recurring tool failures, missed defects, or disproportionate review time affect real development.
- Exact inference configuration, quantization and intervention counts were not consistently captured across experiments; do not claim a fully controlled comparison.

## Next milestone
Proceed to engine/simulation architecture investigation via Issue #4. Complete the administrative PR linked to Issue #2 before marking that issue done.
