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
4. At release (P4), move the entries under the new version and write user-facing release notes.
5. Check that the docs are true: run the documented commands and follow the documented steps.
6. After incidents (P5), add a post-incident note to the runbook.

## Never
- Document planned behaviour as if it exists.
- Put secret values in docs.
