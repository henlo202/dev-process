# Playbook: Reviewer agent

**When:** before every gate (G0–G3)
**Reads:** the artefact under review **and its inputs** (e.g. code vs requirements, design vs NFRs)
**Writes:** a reviewer summary (template: `.process/templates/reviewer-summary.md`)

Run in a fresh session, separate from the one that produced the work, if your tool allows.

## What to check, by gate
| Gate | Focus |
|------|-------|
| G0 | Problem clarity, measurable success, non-goals, tier justification |
| G1 | One clear outcome; size limit; testable ACs; missing NFRs; open questions that should have been spiked; scope creep against the brief. **T3:** ADR quality (real alternatives, spike evidence?), operability, security threats, test strategy gaps |
| G2 | Does the demo actually show every AC in scope? Correctness; tests that really prove the ACs; weakened or deleted tests; spike code leaking in; security; docs updated; tier still correct |
| G3 | Version, changelog accuracy, rollback path, migrations, user docs vs behaviour |

## Rules
- Rank each finding as blocker, major, minor or nit.
- Be specific: file, line or section, and a suggested fix.
- State what you did **not** check.
- Do not approve. End with "ready / ready with fixes / not ready" as advice to the Owner.
