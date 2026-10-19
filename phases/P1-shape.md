---
id: P1
---
# P1 · Shape

## Purpose
Decide **what** the next increment delivers and **roughly how**, in one short
step. Where an answer is uncertain, build something to find out instead of
writing more.

## When
At the start of every T2 and T3 [increment](../guides/increments.md). T1 changes
skip shaping and go straight to [P2 · Build](P2-build.md).

## Steps

| # | Who | Step |
|---|-----|------|
| 1 | Owner | State the outcome you want from this increment in one or two sentences. Include learnings from the last [retrospective](../artefacts/retrospective.md). |
| 2 | Analyst agent | Write or update the [requirements](../artefacts/requirements.md) in scope, with Given/When/Then acceptance criteria. Only the requirements for this increment; the rest of the backlog stays rough. |
| 3 | Architect agent | Note how the increment will be built, as a few bullet points in the increment brief. Update the [architecture](../artefacts/architecture.md) only where it changes. Write an [ADR](../artefacts/adr.md) for any decision that is hard to reverse. |
| 4 | Architect / Implementer agent | For every open question that a document cannot settle, run a time-boxed [spike](../guides/spikes.md): build a throwaway prototype, try both options, measure. Record the result in a [spike report](../artefacts/spike-report.md). |
| 5 | Planner agent | Write the [increment brief](../artefacts/increment.md): the outcome, the requirements in scope, design notes, spike results, the vertical task slices, and how the result will be demonstrated. Check it against the [size limit](../guides/increments.md#size-limit). |
| 6 | Reviewer agent | Review the brief against the initiative brief, the requirements and the architecture. Produce a [reviewer summary](../artefacts/reviewer-summary.md). For T3, also review the design in depth. |
| 7 | Owner | Hold gate [G1 · Shape approved](../gates/G1-shape.md). |

## Exit criteria
- The increment has one demonstrable outcome and fits the size limit.
- Every requirement in scope has testable acceptance criteria.
- Open questions are answered by spikes, or recorded as explicit assumptions.
- For T3: the design decisions are recorded in ADRs, and the risk register and threat model are updated.

## Pitfalls
- **Shaping the whole backlog.** Shape one increment at a time. Later increments will look different once you have learned from this one.
- **Arguing on paper.** If two options are debated for more than a few minutes, spike both.
- **Requirements as tasks.** "Add a button" is a task; "A user can export their data as CSV" is a requirement.
