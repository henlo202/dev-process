---
artefact: gate-record
gate: G1               # G0 | G1 | G2 | G3
increment: INC-001     # G1 only: the increment being approved (delete for other gates)
decision: approved     # approved | approved-with-conditions | rejected
tier: {{tier}}
status: approved
updated: {{date}}
---
# Gate G1: <name>, <increment or version>

**Approver:** Owner
**Process version:** {{process_version}}
**Reviewed artefacts:**
- docs/requirements/<file>.md @ v0.1.0 (commit <sha>)

**Reviewer summary:** <link or paste>

## Checklist
<!-- Paste the gate's checklist from dev-process and tick it. -->
- [ ]

## Conditions
<!-- Only for approved-with-conditions. Each condition must be checkable. -->

## Notes
