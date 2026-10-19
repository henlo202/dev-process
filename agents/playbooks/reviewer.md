# Playbook: Reviewer agent

**When:** before every gate (G0–G5)
**Reads:** the artefact under review **and its inputs** (e.g. code vs requirements, design vs NFRs)
**Writes:** a reviewer summary (template: `.process/templates/reviewer-summary.md`)

Run in a fresh session, separate from the one that produced the work, if your tool allows.

## What to check, by gate
| Gate | Focus |
|------|-------|
| G0 | Problem clarity, measurable success, non-goals, tier justification |
| G1 | Ambiguity, testability, conflicts, missing NFRs, scope creep against the brief |
| G2 | Requirements coverage, ADR quality (real alternatives?), operability, security threats, test strategy gaps |
| G3 | Requirements with no task, oversized tasks, hidden dependencies, risky ordering |
| G4 | Correctness, tests that actually prove the ACs, weakened or deleted tests, security, docs updated, design adherence, tier still correct |
| G5 | Version, changelog accuracy, rollback path, migrations, user docs vs behaviour |

## Rules
- Rank each finding as blocker, major, minor or nit.
- Be specific: file, line or section, and a suggested fix.
- State what you did **not** check.
- Do not approve. End with "ready / ready with fixes / not ready" as advice to the Owner.
