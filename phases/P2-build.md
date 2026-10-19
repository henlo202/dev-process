---
id: P2
---
# P2 · Build

## Purpose
Implement the increment's task slices with tests first, keeping documentation
current as part of the same change.

## When
In every tier. A T1 change starts here, without an increment brief.

## Steps (per task slice)

| # | Who | Step |
|---|-----|------|
| 1 | Implementer agent | Create a branch named after the task (e.g. `task/INC-004-S2-export-csv`). |
| 2 | Tester agent | Write failing tests from the acceptance criteria. Reference the requirement ID in each test name or a comment (e.g. `test_REQ_007_export_has_header`). |
| 3 | Implementer agent | Write the minimum code that makes the tests pass, then refactor. |
| 4 | Implementer agent | Run the full local test suite, linters and formatters before every commit. |
| 5 | Documenter agent | Update user docs, the architecture doc, the runbook and the `CHANGELOG.md` Unreleased section as needed. |
| 6 | Implementer agent | Check the [Definition of Done](../guides/definition-of-ready-done.md), then open a pull request using the G2 checklist. |

If a new open question appears mid-build, run a short [spike](../guides/spikes.md)
instead of guessing. If the answer changes the increment's scope, go back to
the Owner.

## Rules for agents
- Work within the [autonomy level](../guides/agent-autonomy.md) set in `AGENTS.md`. By default, agents may commit and open PRs, but never merge, deploy or approve gates.
- Never weaken or delete a test to make it pass. If a test is wrong, say so in the PR and link the requirement.
- Never merge spike code. Rebuild it properly, test-first.
- Stop and ask the Owner when a task conflicts with the increment brief or the design.

## Exit criteria
- PRs are open, CI is green, and docs are updated in the same PRs.
