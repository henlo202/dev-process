---
name: dev-process-reviewer
description: Critically review an artefact or pull request against its inputs before a dev-process human gate (G0-G3) and write a reviewer summary with ranked findings. Use before any gate decision, when asked to review a PR, increment brief, ADR or release, or for a second opinion.
---
# Reviewer (dev-process)

- **When:** before every gate (G0–G3). Run in a fresh session, separate from the one that did the work, if your tool allows.
- **Reads:** the artefact under review **and its inputs** (code against requirements, design against NFRs), plus `docs/standards.md`
- **Writes:** a reviewer summary (template: `reviewer-summary.md` in this skill's folder, or `.process/templates/reviewer-summary.md`)

## Focus per gate
| Gate | Focus |
|------|-------|
| G0 | Problem clarity, measurable success, non-goals, tier justification |
| G1 | One clear outcome; size limit; testable ACs; missing NFRs; questions that should have been spiked. **T3:** ADR quality, operability, security threats, test strategy gaps |
| G2 | Does the demo show every AC in scope? Correctness; tests that really prove the ACs; weakened or deleted tests; spike code; **standards compliance**; security; docs; tier |
| G3 | Version, changelog accuracy, rollback path, migrations, user docs vs behaviour |

## Rules
- Rank each finding as blocker, major, minor or nit. Be specific about the file, line and fix.
- Check the standards in `docs/standards.md` that tooling does **not** enforce (naming, structure, error handling).
- State what you did **not** check.
- Do not approve. End with "ready / ready with fixes / not ready" as advice to the Owner.
