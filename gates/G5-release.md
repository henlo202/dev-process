---
id: G5
---
# G5 · Release approved

## Purpose
Decide that a set of merged changes is ready for users.

## Checklist
- [ ] The version number follows the project's versioning scheme.
- [ ] The changelog and release notes are accurate and written for users.
- [ ] The runbook covers deploy, rollback and any new configuration or alerts.
- [ ] Data migrations, if any, are reversible or backed up.
- [ ] The user documentation matches the released behaviour.
- [ ] For T3: the rollback procedure was tested.
- [ ] Every finding in the reviewer summary has an answer.

## Decisions
Approved (tag and deploy) / Approved with conditions / Rejected.

## Record
Create `docs/gates/G5-<version>.md` from the [gate record template](../artefacts/gate-record.md).
For T1-only releases, an annotated git tag whose message contains the
ticked checklist is enough.
