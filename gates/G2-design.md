---
id: G2
---
# G2 · Design approved

## Purpose
Approve the approach and the hard-to-reverse decisions before implementation
starts. Applies to T3. For T2, design changes are reviewed at G4.

## Checklist
- [ ] Every must-have requirement is addressed by the design.
- [ ] Every hard-to-reverse decision has an ADR, with alternatives considered.
- [ ] The test strategy says how each requirement will be proven.
- [ ] The risk register lists security and operational threats, with mitigations.
- [ ] Operability is designed in: logging, metrics, configuration, deployment, rollback.
- [ ] Every finding in the reviewer summary has an answer.

## Cooling-off (solo safeguard)
For T3, approve no earlier than the day after the reviewer summary was
produced. Re-read the ADRs with fresh eyes before signing.

## Decisions
Approved / Approved with conditions / Rejected (back to P2).

## Record
Create `docs/gates/G2-<yyyy-mm-dd>.md` from the [gate record template](../artefacts/gate-record.md).
