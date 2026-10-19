---
id: gate-record
---
# Gate record

**What it is:** A small file documenting one gate decision: what was reviewed,
the checklist, the decision and any conditions. It costs a minute today and
gives you an audit trail if compliance requirements arrive later.

**Where:** `docs/gates/<gate>-<date-or-version>.md`. For G4, the merged PR is the record.

## Rules
- Reference the exact versions (or commit) of the artefacts you reviewed.
- Write the conditions so that they can be checked.
- Never edit a gate record after the decision. Add a new one instead.
