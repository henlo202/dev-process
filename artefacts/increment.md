---
id: increment
---
# Increment brief

**What it is:** A one-page description of one increment: the outcome it
delivers, the requirements in scope, short design notes, spike results, the
task slices, how it will be demonstrated, and afterwards what was learned. It
replaces separate requirements, design and plan sign-offs for each increment.

**Where:** `docs/increments/INC-NNN-<slug>.md`, one file per increment.

## Lifecycle
`draft` (shaping) → `approved` (G1 passed) → `in-progress` → `done` (demo recorded, merged) → Learnings filled in at P5.

## Frontmatter
```yaml
artefact: increment
increment: INC-004
status: draft            # draft | approved | in-progress | done | superseded
requirements: [REQ-007, REQ-008]   # in scope; checked against the size limit
tier: T2                 # sets the model classes for its steps
budget: M                # S | M | L or a number of agent steps; approved at G1
spent: 7                 # agent steps used (status.py log-step)
escalations: ["S3 to deep: race in the exporter"]
updated: 2026-10-19
```

## Rules
- One outcome per increment, demonstrable to the Owner.
- Respect the [size limit](../guides/increments.md#size-limit). The conformance checker warns when an increment lists too many requirements or tasks.
- Requirements themselves live in `docs/requirements/`. The brief only references them by ID.
- When the increment is `done`, the **Demo** section must link to the evidence.
- It has a [budget](../guides/resource-economy.md#2-budgets-and-stop-loss). Only the Owner changes it.
