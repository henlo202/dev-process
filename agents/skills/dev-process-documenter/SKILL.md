---
name: dev-process-documenter
description: Keep user docs (Diátaxis), architecture, runbook, changelog and release notes in line with the code. Use after behaviour changes (dev-process P2), when preparing a release (P4), after incidents (P5), or when asked to write or fix documentation.
---
# Documenter (dev-process)

- **Phases:** P2 Build, P4 Release, P5 Learn
- **Reads:** the diff, requirements, existing docs
- **Writes:** `docs/user/`, `docs/architecture.md`, `docs/ops/runbook.md`, `CHANGELOG.md`, release notes

## Steps
1. For each behaviour change, update the matching user doc: a tutorial, how-to, reference or explanation page.
2. Update the architecture doc and the runbook when structure, config, deployment or alerts change.
3. Add a `CHANGELOG.md` Unreleased entry for each user-visible change.
4. At release (P4), move the entries under a new `## [X.Y.Z] - date` heading and write user-facing release notes. After the Owner approves G3, create the annotated tag `vX.Y.Z` and follow the runbook's deploy steps.
5. Check that the docs are true: run the documented commands and follow the documented steps.
6. After incidents (P5), add a post-incident note to the runbook.
7. At P5, end the increment's Learnings with a resource line from its `budget`, `spent` and `escalations`, e.g. "Resource use: 14 of 20 steps (M), 1 escalation (S3 to deep), most cost: flaky test."

Edit docs in place with targeted changes; never regenerate a whole document to change part of it.

## Never
- Document planned behaviour as if it exists.
- Put secret values in docs.
