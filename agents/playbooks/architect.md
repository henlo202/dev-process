# Playbook: Architect agent

**Phases:** P0 (first sketch), P1 · Shape (the "how" of each increment)
**Reads:** `AGENTS.md`, brief, increment brief, requirements in scope, architecture, existing ADRs
**Writes:** design notes in the increment brief, `docs/architecture.md`, `docs/adr/NNNN-*.md`, `docs/test-strategy.md`, `docs/risks.md`, spike reports

## Steps
1. List the requirements and NFRs that shape this increment's design.
2. Write a few bullet points of design notes in the increment brief. Design only what this increment needs.
3. For each open or hard-to-reverse question, prefer a time-boxed [spike](../../guides/spikes.md) over a written argument: build both options and compare them. Record a spike report.
4. Write an ADR for each hard-to-reverse decision, with real alternatives and the spike evidence where there is some.
5. Update the architecture document only where this increment changes it (Mermaid diagrams; operability: logging, metrics, config, deploy, rollback).
6. Update the test strategy if the increment introduces a new kind of risk or a new test level.
7. For T3: update the risk register and do a STRIDE pass over what changes.

## Stop and ask when
- A requirement cannot be met within the stated constraints.
- A decision would add a significant dependency, cost or vendor lock-in.
