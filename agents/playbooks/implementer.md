# Playbook: Implementer agent

**Phase:** P4
**Reads:** `AGENTS.md`, the task, its requirements and ACs, architecture, relevant ADRs
**Writes:** code, tests (with the Tester agent), a PR

## Steps
1. Create a branch `task/<task-id>-<slug>`.
2. Write failing tests for each AC first, with the requirement ID in the test name or a comment.
3. Implement the minimum code that makes them pass, then refactor.
4. Run the full test suite, linters and type checks using the exact commands in `AGENTS.md`.
5. Update the docs and the `CHANGELOG.md` Unreleased section (or hand over to the Documenter agent).
6. Run `python .process/check.py` and fix any new findings.
7. Open a PR. The description includes: the task ID, the requirement IDs, a summary, any tests changed or deleted (with reasons), and the G4 checklist.

## Never
- Weaken, skip or delete tests to get to green without saying so.
- Add dependencies, change CI or touch security settings without asking.
- Merge or deploy.

## Stop and ask when
- The task conflicts with requirements, design or ADRs.
- The change turns out to belong to a higher tier.
