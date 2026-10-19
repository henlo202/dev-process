---
id: P4
---
# P4 · Build

## Purpose
Implement tasks with tests first, keeping documentation current as part of the
same change.

## When
Every tier. A T1 change usually starts here.

## Steps (per task)

| # | Who | Step |
|---|-----|------|
| 1 | Implementer agent | Create a branch named after the task (e.g. `task/T-012-export-csv`). |
| 2 | Tester agent | Write failing tests from the task's acceptance criteria. Reference the requirement ID in each test name or a comment (e.g. `test_REQ_007_export_has_header`). |
| 3 | Implementer agent | Write the minimum code that makes the tests pass, then refactor. |
| 4 | Implementer agent | Run the full local test suite, linters and formatters before every commit. |
| 5 | Documenter agent | Update user docs, the architecture doc, the runbook and `CHANGELOG.md` (the "Unreleased" section) as needed. |
| 6 | Implementer agent | Check the [Definition of Done](../guides/definition-of-ready-done.md), then open a pull request using the G4 checklist. |

## Rules for agents
- Work within the [autonomy level](../guides/agent-autonomy.md) set in `AGENTS.md`. By default, agents may commit and open PRs, but never merge, deploy or approve gates.
- Never weaken or delete a test to make it pass. If a test is wrong, say so in the PR and link the requirement.
- Keep commits small and messages meaningful. Reference task and requirement IDs.
- Stop and ask the Owner when a task conflicts with requirements or the design.

## Exit criteria
- The PR is open, CI is green, and docs are updated in the same PR.
