---
id: P7
---
# P7 · Operate & Learn

## Purpose
Run the software, learn from what happens in production and from how the
process felt, and feed both back into the next increment and into the process
itself.

## When
Continuously after a release. Hold a retrospective after every T3 release and
at least once a quarter for each active initiative.

## Steps

| # | Who | Step |
|---|-----|------|
| 1 | Owner / agents | Watch the signals defined in the runbook (errors, latency, usage) and handle incidents using the runbook. |
| 2 | Documenter agent | After any incident, add a short post-incident note to the runbook: what happened, the fix, and the follow-up. |
| 3 | Owner | Write a short [retrospective](../artefacts/retrospective.md): what worked, what didn't, and what to change. Agents can draft it from PR history. |
| 4 | Owner | Turn product learnings into new requirements or backlog items. Turn process learnings into a [process change proposal](../governance/change-process.md). |

## Exit criteria
- Retrospective findings are routed: to the product backlog, or to the process repository.
