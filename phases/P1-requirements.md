---
id: P1
---
# P1 · Requirements

## Purpose
Turn the brief into requirements that are specific, uniquely identified and
testable, so that every later step (design, tasks, tests, docs) can trace back
to them.

## When
For every T2 and T3 increment. For T1 changes, skip this phase but still
reference an existing requirement ID if one applies.

## Steps

| # | Who | Step |
|---|-----|------|
| 1 | Analyst agent | Read the brief and existing requirements. List open questions and ask the Owner before writing. |
| 2 | Analyst agent | Write or update [requirements](../artefacts/requirements.md): functional (`REQ-nnn`) and non-functional (`NFR-nnn`), each with acceptance criteria in Given/When/Then form. |
| 3 | Analyst agent | Mark each requirement's priority (must / should / could) and status. Never renumber or reuse IDs. |
| 4 | Reviewer agent | Review for ambiguity, untestable wording, conflicts, missing NFRs (performance, security, accessibility, operability). Produce a [reviewer summary](../artefacts/reviewer-summary.md). |
| 5 | Analyst agent | Resolve or explicitly defer every reviewer finding. |
| 6 | Owner | Hold gate [G1 · Requirements approved](../gates/G1-requirements.md). |

## Exit criteria
- Every requirement in scope has an ID, priority and at least one acceptance criterion.
- Every acceptance criterion is observable by an automated test, or explicitly marked `manual` with a reason.
- Open questions are answered or recorded as assumptions.

## Pitfalls
- **Requirements as tasks.** "Add a button" is a task; "A user can export their data as CSV" is a requirement.
- **Silent edits after approval.** Changing an approved requirement means bumping its version and noting it in the change log section of the requirements file.

See the [requirements guide](../guides/requirements.md) for format and traceability rules.
