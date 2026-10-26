---
name: dev-process-tester
description: Derive automated tests from acceptance criteria, name them after requirement IDs, and find coverage gaps using the traceability report. Use when writing tests, reproducing a bug, or checking that an increment's requirements are proven (dev-process P2 and P3).
---
# Tester (dev-process)

- **Phases:** P2 Build, P3 Verify
- **Reads:** requirements and ACs, `docs/test-strategy.md`, `docs/standards.md`, the diff
- **Writes:** tests

## Steps
1. For each AC, write at least one test at the level the test strategy names, with the requirement ID in its name or a comment (`test_REQ_007_...`).
2. Add edge cases: empty, maximum, invalid, concurrent, a failing dependency, permissions.
3. For bugs, write a failing reproduction test first.
4. In P3, run `python .process/check.py` and read the traceability section. Add tests for requirements in scope that have none.
5. Report what could not be automated, and why.
6. While iterating, run only the affected tests and show only the failures; run the full suite once at the end.

## Never
- Count spike results as test coverage.
- Mock the unit under test, or assert on implementation details when behaviour can be asserted.
