---
id: P5
---
# P5 · Verify

## Purpose
Prove the change does what the requirements say, nothing broke, and the
process was followed. Then decide whether to merge.

## When
For every pull request, in every tier.

## Steps

| # | Who | Step |
|---|-----|------|
| 1 | CI | Run the automated test suite, coverage, linting, static analysis, dependency and secret scanning (see [QA guide](../guides/quality-assurance.md)). |
| 2 | CI | Run the conformance checker. It produces the [conformance report](../artefacts/conformance-report.md) and [traceability report](../artefacts/traceability-report.md). It **warns** and never blocks. |
| 3 | Tester agent | Look for missing edge cases and untested acceptance criteria. Add tests where gaps exist. |
| 4 | Reviewer agent | Review the diff for correctness, security, maintainability and adherence to the design. Produce a [reviewer summary](../artefacts/reviewer-summary.md) as a PR comment. |
| 5 | Owner | Hold gate [G4 · Merge approved](../gates/G4-merge.md): read the reviewer summary and the reports, tick the PR checklist, and merge. |

## Exit criteria
- CI is green. Any conformance warnings are fixed or waived.
- Every requirement touched by the change is covered by a passing test.
- Every reviewer finding is fixed, or answered with a reason.
