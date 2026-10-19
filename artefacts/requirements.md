---
id: requirements
---
# Requirements specification

**What it is:** The authoritative list of what the system must do (functional
requirements, `REQ-nnn`) and how well (non-functional requirements, `NFR-nnn`). Each
requirement has testable acceptance criteria.

**Where:** `docs/requirements/`, one file per feature area (e.g. `export.md`).

## Format
```markdown
### REQ-007: Export data as CSV
- **Priority:** must
- **Status:** approved
- **Source:** brief §3, Owner 2026-10-19

A signed-in user can download their records as a CSV file.

**Acceptance criteria**
- AC-007.1: Given a user with 3 records, when they choose Export,
  then a CSV with a header row and 3 data rows is downloaded.
- AC-007.2: Given a user with no records, when they choose Export,
  then a CSV with only the header row is downloaded.
```

## Rules
- IDs are permanent. Never renumber or reuse them. Retire a requirement with `Status: retired`.
- Tests reference requirement IDs, so the checker can trace coverage.
- Approved requirements change only via a new version, noted in the file's change log.

See the [requirements guide](../guides/requirements.md).
