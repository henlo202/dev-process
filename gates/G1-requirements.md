---
id: G1
---
# G1 · Requirements approved

## Purpose
Freeze an agreed, testable description of *what* will be built in this
increment, before agents spend effort on *how*.

## Checklist
- [ ] Every in-scope requirement has an ID, priority and acceptance criteria.
- [ ] Every acceptance criterion can be checked by an automated test, or is marked `manual` with a reason.
- [ ] Non-functional requirements are considered: security, performance, accessibility, operability, privacy.
- [ ] Nothing in the requirements contradicts the brief's non-goals.
- [ ] Every finding in the reviewer summary has an answer.
- [ ] I read the requirements myself, not only the summary.

## Decisions
- **Approved:** the requirements' `status` becomes `approved`. Continue to P2.
- **Approved with conditions:** list the conditions. The Analyst agent fixes them before P2 starts.
- **Rejected:** go back to P1 with notes.

## Record
Create `docs/gates/G1-<yyyy-mm-dd>.md` from the [gate record template](../artefacts/gate-record.md).
