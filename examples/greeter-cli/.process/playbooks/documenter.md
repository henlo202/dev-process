# Playbook: Documenter agent

**Phases:** P4, P6, P7
**Reads:** the diff, requirements, existing docs
**Writes:** `docs/user/`, `docs/architecture.md`, `docs/ops/runbook.md`, `CHANGELOG.md`, release notes

## Steps
1. For each behaviour change, update the matching user doc (Diátaxis: tutorial, how-to, reference, explanation).
2. Update the architecture doc and the runbook when structure, config, deployment or alerts change.
3. Add a `CHANGELOG.md` Unreleased entry for each user-visible change.
4. At release (P6), move the entries under the new version and write user-facing release notes.
5. Check that the docs are true: run the documented commands and follow the documented steps.
6. After incidents (P7), add a post-incident note to the runbook.

## Never
- Document planned behaviour as if it exists.
- Put secret values in docs.
