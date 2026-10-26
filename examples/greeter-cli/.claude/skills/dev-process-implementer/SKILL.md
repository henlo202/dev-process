---
name: dev-process-implementer
description: Implement a task slice test-first on a feature branch, following the project's engineering standards, and open a pull request with the G2 merge checklist. Use for any coding task in a dev-process project (phase P2 Build), including T1 bug fixes.
---
# Implementer (dev-process)

- **Phases:** P2 Build, P3 Verify (demo)
- **Reads:** `AGENTS.md`, `docs/standards.md`, the increment brief, the requirements and ACs, the architecture, relevant ADRs
- **Writes:** code, tests (with the tester), a pull request

## Rules (always)
- **Standards:** write code according to `docs/standards.md`. Run the project's lint/format command (`guardrails.lint_command` in `.process/config.yaml`, also listed in `AGENTS.md`) before every commit, and fix what it reports. Never disable a lint rule without asking.
- **Branches:** work only on a feature branch named per `docs/standards.md` (default `task/<INC>-<S>-<slug>`). Never commit or push to `main`/`master`.
- **Commits:** follow the commit convention in `docs/standards.md` (default Conventional Commits, e.g. `feat: export CSV (REQ-007)`).
- **Guardrails:** git hooks in `.process/guardrails/` enforce these rules. If a hook rejects something, fix the cause. **Never** bypass a hook (`--no-verify`, changing `core.hooksPath`, owner-override variables).
- **Tests:** never weaken, skip or delete a test to make it pass without saying so in the PR.
- **Economy:** run the affected tests while working and the full suite once before the PR; make targeted edits instead of rewriting files; search instead of reading whole large files. After `economy.max_attempts` failed attempts at the same problem, stop and report (or escalate one model class, recorded with `status.py log-step --escalated`), never keep retrying.

## Steps
1. Make sure the hooks are installed: `git config core.hooksPath .process/guardrails/git-hooks`.
2. Create the branch, e.g. `git switch -c task/INC-004-S2-export-csv`.
3. Write failing tests for each AC first, with the requirement ID in the test name or a comment.
4. Implement the minimum code to pass, then refactor.
5. Run the full test suite (once, at the end of the slice) and the lint command. Commit in small steps.
6. Update the docs and the `CHANGELOG.md` Unreleased section (or hand over to the documenter).
7. Run `python .process/check.py` and fix any new findings.
8. Tick the slice (`- [x] S2: …`) in the increment brief, in the same PR. `.process/status.py` uses the ticks to pick the next slice.
9. Open a PR with the increment and slice IDs, the requirement IDs, a summary, any tests changed or deleted, and the G2 checklist.
10. On the slice that completes the increment, record the demo (skill `dev-process-demo`).

## Never
Merge, deploy, bypass hooks, merge spike code, add dependencies or change CI without asking.

## Stop and ask when
The task conflicts with the increment brief, the design or the standards, or turns out to belong to a higher tier.
