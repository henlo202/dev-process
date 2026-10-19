---
artefact: standards
status: approved
version: 1.0.0
owner: Owner
updated: 2026-10-19
---
# greeter-cli: Engineering standards

Each rule says where it is enforced. Unenforced rules are checked by the Reviewer agent at G2.

## Code
| Rule | Why | Enforced by |
|------|-----|-------------|
| Python 3.9+, standard library only at runtime (NFR-001) | No install friction | `test_NFR_001_standard_library_only` in CI |
| Lint-clean with ruff (rules E, F, W, I, B, UP; config in `ruff.toml`) | Catches bugs and keeps imports tidy | pre-commit hook + CI (`guardrails.lint_command`) |
| Formatted with `ruff format` (line length 100) | No style debates in review | pre-commit hook + CI |
| Pure logic in `greeter.core`; I/O and exit codes only in `greeter.cli` | Testability | Reviewer at G2 |

## Branches & commits
| Rule | Why | Enforced by |
|------|-----|-------------|
| Never commit or push to `main`; all changes arrive by pull request | Every change passes gate G2 | pre-commit + pre-push hooks; Claude Code adapter |
| Branch names: `task/<INC>-<S>-<slug>`, `fix/`, `spike/`, `docs/`, `chore/`, `release/` | Traceability | pre-push hook |
| Conventional Commits, with requirement IDs where relevant: `feat: Swedish greeting (REQ-002)` | Readable history; changelog | commit-msg hook + CI |

## Dependencies
| Rule | Why | Enforced by |
|------|-----|-------------|
| No runtime dependencies. Dev tools (ruff) are allowed with the Owner's OK | NFR-001 | NFR-001 test; Reviewer at G2 |

## Tests
| Rule | Why | Enforced by |
|------|-----|-------------|
| Tests are named after requirement IDs (`test_REQ_001_...`) | Traceability | Conformance check (warns) |
| Tests are never weakened or deleted silently | Trust in green CI | Reviewer at G2; G2 checklist |
