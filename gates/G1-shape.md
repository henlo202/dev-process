---
id: G1
---
# G1 · Shape approved

## Purpose
Agree on the outcome and the rough approach of one increment, before agents
build it. This gate is meant to be quick: it approves a small, concrete slice,
not a full specification.

## Before you decide
Read the increment brief and the reviewer summary. Where a spike was run, look
at what it showed. **A working prototype is better evidence than a paragraph.**

## Checklist (all tiers)
- [ ] The increment has one outcome that I can see demonstrated when it is done.
- [ ] It fits the [size limit](../guides/increments.md#size-limit), or I accept the overrun knowingly.
- [ ] Every requirement in scope has acceptance criteria that a test or the demo can show.
- [ ] Open questions were answered by spikes, or are recorded as assumptions I accept.
- [ ] Nothing contradicts the initiative brief's non-goals.
- [ ] Every finding in the reviewer summary has an answer.
- [ ] The [budget](../guides/resource-economy.md#2-budgets-and-stop-loss) (S/M/L) fits the work, and the tier is right (it sets the model classes).

## Design scrutiny (T3 only)
- [ ] Every hard-to-reverse decision has an ADR with real alternatives, ideally compared through a spike.
- [ ] The test strategy says how the risky parts will be proven.
- [ ] The risk register and threat model cover the change, including operability (logging, rollback).
- [ ] **Cooling-off:** I am approving no earlier than the day after the reviewer summary was produced.

## Decisions
- **Approved:** the increment's status becomes `in-progress`. Continue to P2.
- **Approved with conditions:** list the conditions, which the agents fix before building.
- **Rejected:** reshape the increment, or drop it.

## Record
Reply to the orchestrator with your decision (e.g. "approved"). It records it
verbatim with `python .process/status.py record-gate G1`, which refuses
unless this gate is pending. Or write the record yourself from the
[gate record template](../artefacts/gate-record.md).
