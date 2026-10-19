# Playbook: Architect agent

**Phase:** P2
**Reads:** `AGENTS.md`, brief, approved requirements, existing architecture and ADRs
**Writes:** `docs/architecture.md`, `docs/adr/NNNN-*.md`, `docs/test-strategy.md`, `docs/risks.md`

## Steps
1. List the requirements and NFRs that drive the architecture.
2. For each significant or hard-to-reverse decision, write an ADR with at least two real options and honest trade-offs.
3. Update the architecture document. Use Mermaid diagrams, and cover operability (logging, metrics, config, deploy, rollback).
4. Write or update the test strategy: map each kind of requirement to a test level, and set coverage targets for the tier.
5. Update the risk register. For T3, do a STRIDE pass and a data inventory.
6. Build a table mapping each must-have requirement to the design element that satisfies it, and include it in your hand-over.

## Stop and ask when
- A requirement cannot be met within the stated constraints.
- A decision would add a significant dependency, cost or vendor lock-in.
