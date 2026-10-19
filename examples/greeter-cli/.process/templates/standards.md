---
artefact: standards
status: draft
version: 0.1.0
owner: Owner
updated: {{date}}
---
# {{project}}: Engineering standards

Each rule says where it is enforced. Unenforced rules are checked by the Reviewer agent at G2.

## Code
| Rule | Why | Enforced by |
|------|-----|-------------|
| <Coding standard or style guide, e.g. PEP 8 via ruff> | Consistent, reviewable code | pre-commit hook + CI (`guardrails.lint_command`) |
| <Formatter, e.g. ruff format> | No style debates in review | pre-commit hook + CI |

## Branches & commits
| Rule | Why | Enforced by |
|------|-----|-------------|
| Never commit or push to `main`/`master`; all changes arrive by pull request | Every change passes gate G2 | pre-commit + pre-push hooks; agent adapter; branch protection where available |
| Branch names: `task/<INC>-<S>-<slug>`, `fix/<slug>`, `spike/<slug>`, `docs/<slug>`, `chore/<slug>`, `release/<version>` | Traceability | pre-push hook (`guardrails.branch_pattern`) |
| Commit messages: Conventional Commits, e.g. `feat: export CSV (REQ-007)` | Readable history; changelog | commit-msg hook + CI (`guardrails.commit_pattern`) |

## Dependencies
| Rule | Why | Enforced by |
|------|-----|-------------|
| New or upgraded (non-patch) dependencies need the Owner's OK | Supply-chain risk | Autonomy level; Reviewer at G2 |

## Tests
| Rule | Why | Enforced by |
|------|-----|-------------|
| Tests reference requirement IDs (`test_REQ_007_...`) | Traceability | Conformance check (warns) |
| Tests are never weakened or deleted silently | Trust in green CI | Reviewer at G2; G2 checklist |
