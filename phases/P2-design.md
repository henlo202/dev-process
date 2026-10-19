---
id: P2
---
# P2 · Design

## Purpose
Decide *how* the requirements will be met, record the important decisions and
their reasons, and decide *how quality will be proven*.

## When
For T3 increments in full, with gate G2. For T2 increments, update the
architecture document and add an ADR only if a significant decision is made;
there is no separate gate, and the changes are reviewed at G4.

## Steps

| # | Who | Step |
|---|-----|------|
| 1 | Architect agent | Propose a design that satisfies the approved requirements. Offer alternatives for any decision that is hard to reverse. |
| 2 | Architect agent | Update the [architecture document](../artefacts/architecture.md) (context, building blocks, data, deployment, cross-cutting concerns). |
| 3 | Architect agent | Write an [ADR](../artefacts/adr.md) for each significant decision: context, options, decision, consequences. |
| 4 | Architect agent | Write or update the [test strategy](../artefacts/test-strategy.md): which test levels prove which requirements, coverage targets, tooling. |
| 5 | Architect agent | Update the [risk register & threat model](../artefacts/risk-register.md). |
| 6 | Reviewer agent | Review the design against the requirements and NFRs, and challenge every ADR. Produce a [reviewer summary](../artefacts/reviewer-summary.md). |
| 7 | Owner | Hold gate [G2 · Design approved](../gates/G2-design.md) (T3). |

## Exit criteria
- Every must-have requirement is addressed by some part of the design.
- Every hard-to-reverse decision has an ADR with at least two options considered.
- The test strategy names the test level for every requirement.
- Security threats are listed with mitigations or explicit acceptance.

## Pitfalls
- **Design by default.** Agents tend to reach for familiar stacks. Make them justify choices against the NFRs.
- **Over-design.** Design only what the current requirements need, and record future ideas as ADR "consequences" or backlog items.
