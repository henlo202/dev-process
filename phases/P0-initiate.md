---
id: P0
---
# P0 · Initiate

## Purpose
Decide whether an initiative is worth doing, frame what it is, and set up the
project so that agents can work in it from day one.

## When
Once per initiative, before any other work. Re-run it if the initiative's goal
changes fundamentally.

## Steps

| # | Who | Step |
|---|-----|------|
| 1 | Owner | Describe the idea in a few sentences: problem, who it is for, why now. |
| 2 | Analyst agent | Draft the [initiative brief](../artefacts/brief.md) from the Owner's description. Ask clarifying questions rather than guess. |
| 3 | Analyst agent | Propose a **risk tier** for the initiative (see [risk tiers](../guides/risk-tiers.md)) with a one-paragraph justification. |
| 4 | Owner | Run the scaffolder (`tooling/scaffold.py`) to create the project skeleton, [`AGENTS.md`](../artefacts/agents-context.md) and [`.process/config.yaml`](../artefacts/process-config.md). |
| 5 | Reviewer agent | Write a [reviewer summary](../artefacts/reviewer-summary.md) of the brief: unclear scope, missing success criteria, hidden risks. |
| 6 | Owner | Hold gate [G0 · Go / No-go](../gates/G0-go-no-go.md). |

## Exit criteria
- The brief states the problem, users, scope, non-goals and measurable success criteria.
- A tier is chosen and recorded in `.process/config.yaml`.
- The project repository exists and passes the conformance check (warnings are acceptable).

## Pitfalls
- **Skipping non-goals.** Agents will happily expand scope; explicit non-goals are your main defence.
- **Solution-first briefs.** The brief describes the problem. Technology choices belong in P2.
