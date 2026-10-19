---
id: G0
---
# G0 · Go / No-go

## Purpose
Commit, or decline to commit, time to an initiative, based on a clear brief.

## Before you decide
Read the brief and the reviewer summary. Agents prepare everything else; this
decision is yours alone.

## Checklist
- [ ] The problem and target users are clear enough that I could explain them in two sentences.
- [ ] Success criteria are measurable, and I will know when the initiative is done.
- [ ] Non-goals are listed.
- [ ] The risk tier is chosen and justified.
- [ ] The first increment is small and clear enough to shape next.
- [ ] Every finding in the reviewer summary has an answer.
- [ ] I am willing to spend the time this will take, now.

## Decisions
- **Approved:** continue to the first increment (P1).
- **Approved with conditions:** continue, with the conditions written in the gate record.
- **Rejected:** archive the brief with the reason. A rejected brief is still useful history.

## Record
Reply to the orchestrator with your decision (e.g. "approved"). It records it
verbatim with `python .process/status.py record-gate G0`, which refuses
unless this gate is pending. Or write the record yourself from the
[gate record template](../artefacts/gate-record.md).
