# Playbook: Tester agent

**Phases:** P2 (Build), P3 (Verify)
**Reads:** requirements and ACs, test strategy, the diff
**Writes:** tests

## Steps
1. For each AC, write at least one test at the level the test strategy says, and name the requirement ID in it.
2. Add edge cases: empty, maximum, invalid, concurrent, failure of dependencies, permissions.
3. For bugs, write a failing reproduction test first.
4. In P3, read the traceability report, and add tests for any requirement in scope that has no test.
5. Report what you could not test automatically, and why.

## Never
- Count spike results as test coverage.
- Mock the unit under test.
- Assert on implementation details when behaviour can be asserted instead.
