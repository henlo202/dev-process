---
id: P0
---
# P0 · Initiate

## Purpose
Decide whether an initiative is worth doing, frame it, and set the project up
so that agents can work in it from day one. This is the only phase outside the
[increment loop](../guides/increments.md).

## When
Once per initiative, before the first increment. Re-run it if the initiative's
goal changes fundamentally.

## Steps

| # | Who | Step |
|---|-----|------|
| 1 | Owner | Describe the idea in a few sentences: problem, who it is for, why now. |
| 2 | Analyst agent | Draft the [initiative brief](../artefacts/brief.md). Ask clarifying questions rather than guess. |
| 3 | Analyst agent | Propose the initiative's highest expected [risk tier](../guides/risk-tiers.md), with a short justification. |
| 4 | Owner | Run the scaffolder (`tooling/scaffold.py`) to create the project skeleton, [`AGENTS.md`](../artefacts/agents-context.md) and [`.process/config.yaml`](../artefacts/process-config.md). |
| 5 | Architect agent | Sketch a first [architecture](../artefacts/architecture.md) and [test strategy](../artefacts/test-strategy.md): just enough to start. Optionally run a [spike](../guides/spikes.md) to test the riskiest assumption. Both documents grow increment by increment. |
| 6 | Planner agent | Propose a rough ordering of the first two or three increments, as a list in the brief. Not a plan for the whole initiative. |
| 7 | Reviewer agent | Write a [reviewer summary](../artefacts/reviewer-summary.md): unclear scope, missing success criteria, hidden risks. |
| 8 | Owner | Hold gate [G0 · Go / No-go](../gates/G0-go-no-go.md). |

## Exit criteria
- The brief states the problem, users, scope, non-goals and measurable success criteria.
- A tier is chosen and recorded in `.process/config.yaml`.
- The first increment is identified.

## Pitfalls
- **Big design up front.** P0 is for direction, not for specifying the whole system. Detail arrives one increment at a time.
- **Skipping non-goals.** Agents will happily expand scope; explicit non-goals are your main defence.
