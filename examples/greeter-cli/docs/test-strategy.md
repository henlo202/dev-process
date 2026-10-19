---
artefact: test-strategy
status: approved
version: 1.0.0
owner: Architect agent
updated: 2026-10-19
---
# greeter-cli: Test strategy

## 1. Test levels
| Level | Scope | Tooling | Runs |
|-------|-------|---------|------|
| Unit | `greeting()` | unittest | Every PR |
| CLI | `main(argv)`: output and exit codes | unittest | Every PR |

## 2. Requirement → level mapping
Behavioural requirements are tested at the CLI level. NFR-001 is tested by inspecting module imports.

## 3. Coverage targets
- Every must-have acceptance criterion: at least one automated test.

## 4. Non-functional testing
NFR-001 only.

## 5. Test data & environments
Literal names in tests. No environments needed.

## 6. Manual checks
| Check | Why not automated |
|-------|-------------------|
| AC-004.1 help text readability | Subjective |
