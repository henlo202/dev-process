---
id: P3
---
# P3 · Verify

## Purpose
Prove the increment does what it set out to do, by showing it working and by
automated evidence. Then decide whether to merge.

## When
For every pull request in every tier. The increment's [demo](../artefacts/demo.md)
is attached to the PR that completes the increment.

## Steps

| # | Who | Step |
|---|-----|------|
| 1 | CI | Run the automated tests, coverage, linting, static analysis, dependency scanning and secret scanning (see the [QA guide](../guides/quality-assurance.md)). |
| 2 | CI | Run the conformance checker, which produces the [conformance report](../artefacts/conformance-report.md) and [traceability report](../artefacts/traceability-report.md). It **warns** and never blocks. |
| 3 | Tester agent | Look for missing edge cases and untested acceptance criteria, and add tests where there are gaps. |
| 4 | Implementer agent | For the PR that completes the increment: record a [demo](../artefacts/demo.md) that shows each acceptance criterion working, as a terminal transcript, screenshots or a short recording. Link it from the increment brief and the PR. |
| 5 | Reviewer agent | Review the diff for correctness, security, maintainability and adherence to the increment brief. Produce a [reviewer summary](../artefacts/reviewer-summary.md) as a PR comment. |
| 6 | Owner | Hold gate [G2 · Merge approved](../gates/G2-merge.md). **Watch the demo first**, then read the reviewer summary and the reports. |

## Exit criteria
- CI is green. Any conformance warnings are fixed or waived.
- For the increment's final PR, the demo shows the outcome working.
- Every reviewer finding is fixed, or answered with a reason.
