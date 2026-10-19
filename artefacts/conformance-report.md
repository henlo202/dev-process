---
id: conformance-report
---
# Conformance report (generated)

**What it is:** The output of `.process/check.py`. It lists where the project
deviates from the process for its tier.

## Severities
| Symbol | Level | Meaning |
|--------|-------|---------|
| ❌ | error | A required artefact is missing or invalid. The check still passes, but this should be fixed or waived. |
| ⚠️ | warning | Something is stale, incomplete or untraced. |
| ℹ️ | info | A suggestion or a recorded waiver. |

The checker **never fails the build** (see [PDR-0003](../governance/decisions/PDR-0003-warn-only-conformance.md)).
Every finding states what to fix, and links to the relevant process page.
