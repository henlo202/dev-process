---
id: standards
---
# Engineering standards

**What it is:** The project's rules for *how* code is written and delivered:
the coding standard, branching, commit messages, dependencies, testing
conventions. **Every rule names where it is enforced.** A rule with no
enforcement is guidance only, and the Reviewer agent checks it at G2.

**Where:** `docs/standards.md`. It is created in P0, and updated when an
increment introduces a new language, tool or convention.

## Format
| Rule | Why | Enforced by |
|------|-----|-------------|
| Code is formatted and lint-clean with `ruff` | Consistent, reviewable diffs | pre-commit hook + CI (`guardrails.lint_command`) |
| Work happens on `task/<INC>-<S>-<slug>` branches, never on `main` | Every change passes G2 | pre-push hook; agent adapter; server-side branch protection if available |
| Commit messages follow Conventional Commits | Readable history, changelog | commit-msg hook + CI |
| New dependencies need the Owner's OK | Supply-chain risk | Agent autonomy level; Reviewer at G2 |

## Rules
- Prefer rules a tool can check. Put the tool configuration (linter config, formatter config) in the repository, and make `guardrails.lint_command` run it.
- Keep it short. Link to an external style guide rather than copying it.
- Changes to standards are made by the Owner, typically during shaping (proposed by the architect skill).

See the [guardrails guide](../guides/guardrails.md).
