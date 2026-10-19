---
artefact: test-strategy
status: draft
version: 0.1.0
owner: Architect agent
updated: {{date}}
---
# {{project}}: Test strategy

## 1. Test levels
| Level | Scope | Tooling | Runs |
|-------|-------|---------|------|
| Unit | Single functions or classes | | Every commit / PR |
| Integration | Components with real dependencies | | Every PR |
| End-to-end | User journeys through the real interface | | Every PR / nightly |

## 2. Requirement → level mapping
<e.g. Business rules → unit; API contracts → integration; user journeys → e2e.>

## 3. Coverage targets
- Line coverage: ≥ 80 % (T2), ≥ 90 % on core modules (T3)
- Every must-have acceptance criterion: at least one automated test

## 4. Non-functional testing
<Performance, security scanning, accessibility.>

## 5. Test data & environments

## 6. Manual checks
| Check | Why not automated |
|-------|-------------------|
