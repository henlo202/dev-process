# Quality assurance & automated testing

Quality is proven by automated evidence, not by assertions from agents.
An agent saying "all tests pass" is not evidence; a green CI run is.

## Layers of defence

| Layer | What | When |
|-------|------|------|
| 1. Test-first development | Tests derived from acceptance criteria before code | P2 |
| 2. Automated test suite | Unit, integration and end-to-end tests, per the test strategy | Every commit and PR |
| 3. Static checks | Formatter, linter, type checker | Every commit and PR |
| 4. Security checks | Dependency vulnerability scan, secret scan, SAST | Every PR |
| 5. Conformance & traceability | `.process/check.py` | Every PR |
| 6. Agent review | Reviewer agent critique in a fresh session | Every PR, every gate |
| 7. Demo | The increment's outcome shown working against the real build | P3, final PR of an increment |
| 8. Human gate | The Owner watches the demo, reads the summary, skims the diff, ticks the checklist | G2 |

## Default targets

| | T1 | T2 | T3 |
|---|---|---|---|
| Line coverage on changed code | no drop | ≥ 80 % | ≥ 90 % on core modules |
| Must-have ACs with automated tests | n/a | 100 % | 100 % |
| End-to-end tests for main journeys | n/a | recommended | required |
| Mutation testing | n/a | n/a | recommended on core logic |

Projects may change these in their test strategy. Changes are reviewed at G1 for T3 increments.

## Agent-specific rules
- **Never weaken tests to pass.** Any change that deletes tests, skips them or loosens assertions must be called out in the PR description. The Owner checks this specifically at G2.
- **Spikes are not tests.** Evidence from a spike informs decisions; it never counts as test coverage.
- **No mocking of the thing under test.** Mocks are for external boundaries.
- **Reproduce before you fix.** For bugs, write a failing test that reproduces the bug first.
- **Flaky tests are bugs.** Quarantine them with an issue; never re-run until green and then ignore them.

## If the product itself uses AI
Add **evals** as a test level: a versioned dataset of inputs with expected
properties of the outputs, scored automatically and tracked over time. Treat a drop
in an eval score like a failing test.

## CI as the source of truth
The project's CI must run the same commands that are listed in `AGENTS.md`.
The conformance check runs in CI too, but never fails the build.
