---
id: P3
---
# P3 · Plan

## Purpose
Break the work into small, independently verifiable tasks that an agent can
complete in one focused session, each traceable to requirements.

## When
For T3 increments, with gate G3. For T2, a lightweight plan (an issue list or a
short task list in the PR description) is enough, with no gate.

## Steps

| # | Who | Step |
|---|-----|------|
| 1 | Planner agent | Split the work into tasks. Each task names its requirement IDs, acceptance criteria and the files or modules it touches. |
| 2 | Planner agent | Order tasks by dependency and risk: highest-risk and walking-skeleton tasks first. |
| 3 | Planner agent | Check each task against the [Definition of Ready](../guides/definition-of-ready-done.md). |
| 4 | Planner agent | Write the [task plan](../artefacts/plan.md). |
| 5 | Reviewer agent | Check for gaps (requirements with no task), oversized tasks and hidden dependencies. Produce a [reviewer summary](../artefacts/reviewer-summary.md). |
| 6 | Owner | Hold gate [G3 · Plan approved](../gates/G3-plan.md) (T3). |

## Exit criteria
- Every in-scope requirement maps to at least one task.
- No task is estimated above roughly half a day of agent work; larger tasks are split.
- Every task meets the Definition of Ready.

## Pitfalls
- **Horizontal slicing.** "Build the database layer" is hard to verify. Prefer vertical slices that deliver testable behaviour.
