---
id: gate-record
---
# Gate record

**What it is:** A small file documenting one gate decision: what was reviewed,
the checklist, the decision and any conditions. It costs a minute today and
gives you an audit trail if compliance requirements arrive later.

**Where:** `docs/gates/<gate>-<increment-date-or-version>.md`. For G2, the merged PR is the record.

## Rules
- Reference the exact versions (or commit) of the artefacts you reviewed.
- Write the conditions so that they can be checked.
- Never edit a gate record after the decision. Add a new one instead.
- Records written by an agent (`recorded_by: agent`) must quote the Owner's decision verbatim in `owner_statement`. Agents use `.process/status.py record-gate`, and never record a decision the Owner did not state.
