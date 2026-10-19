---
id: plan
---
# Task plan

**What it is:** The ordered list of tasks for an increment. Each task is small,
verifiable and traceable to requirements.

## Task format
```markdown
### T-012: Export endpoint returns CSV
- **Requirements:** REQ-007 (AC-007.1, AC-007.2)
- **Depends on:** T-010
- **Touches:** api/export.py, tests/test_export.py, docs/user/export.md
- **Done when:** both ACs have passing tests; user doc updated
- **Status:** todo | doing | done
```

An issue tracker can replace this file. If it does, link the board from
`AGENTS.md`, and make sure issues still carry requirement IDs.
