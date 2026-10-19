---
name: dev-process-architect
description: Decide how an increment will be built, writing design notes, ADRs, architecture and test-strategy updates and, for T3, the threat model. Use when shaping an increment (dev-process P1), when a technical decision is hard to reverse, or when asked to design or compare approaches.
---
# Architect (dev-process)

- **Phases:** P0 (first sketch), P1 Shape
- **Reads:** `AGENTS.md`, the brief, the increment brief, requirements in scope, `docs/architecture.md`, `docs/adr/`, `docs/standards.md`
- **Writes:** design notes in the increment brief, `docs/architecture.md`, `docs/adr/NNNN-*.md`, `docs/test-strategy.md`, `docs/risks.md`

## Steps
1. List the requirements and NFRs that shape this increment's design.
2. Write a few bullet points of design notes in the increment brief. Design only what this increment needs.
3. When a question is open or hard to reverse, prefer a spike (skill `dev-process-spike`) over a written argument.
4. Write an ADR for each hard-to-reverse decision, with real alternatives and any spike evidence (`.process/templates/adr.md`).
5. Update `docs/architecture.md` only where this increment changes it (Mermaid diagrams; logging, config, deploy, rollback).
6. If the increment introduces a new language, tool or convention, propose an update to `docs/standards.md`, **with how it will be enforced**.
7. For T3: update `docs/risks.md`, including a STRIDE pass over what changes.

## Stop and ask when
- A requirement cannot be met within the constraints.
- A decision adds a significant dependency, cost or lock-in.
