# Definition of Ready & Definition of Done

Short, checkable lists that agents can apply to themselves.

## Definition of Ready (a task may start when…)
- [ ] It belongs to an approved increment (or is a T1 change), and references the requirement IDs and acceptance criteria it addresses.
- [ ] It is small enough to finish in one focused agent session (≈ ½ day).
- [ ] Its dependencies are done, or not blocking.
- [ ] The files or modules it touches are named.
- [ ] Its tier is known.
- [ ] There are no open questions: they were settled by a spike, or recorded as explicit assumptions.

## Definition of Done (a task is done when…)
- [ ] Every acceptance criterion it addresses has a passing automated test that references the requirement ID.
- [ ] The full test suite, linters and type checks pass locally and in CI.
- [ ] No tests were deleted, skipped or weakened, or the PR explains why.
- [ ] Docs are updated (user, technical, runbook) where behaviour changed.
- [ ] `CHANGELOG.md` has an Unreleased entry for any user-visible change.
- [ ] The conformance check shows no new errors.
- [ ] No spike code is included.
- [ ] A PR is open with the G2 checklist and a reviewer summary.
- [ ] For the slice that completes an increment, the demo is recorded and linked.
