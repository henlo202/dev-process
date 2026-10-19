# AGENTS.md: {{project}}

> Read this file before doing any work in this repository.

## About
<One paragraph. Details are in docs/brief.md.>

## Process
This project follows **dev-process v{{process_version}}**, a standard process for
AI-agentic development. The current tier is **{{tier}}**.

- Process configuration: `.process/config.yaml`
- Conformance check: `python .process/check.py` (it warns and never blocks)
- Role playbooks: `.process/playbooks/` (analyst, architect, planner,
  implementer, tester, reviewer, documenter)
- Artefact templates: `.process/templates/`
- Before starting any task, find out which phase you are in (P0–P7) and follow
  that phase's steps. Produce the artefacts the phase lists.
- Human gates (G0–G5) are approved only by the Owner. **Never** approve a
  gate, merge a pull request or deploy on your own.

## Commands
```bash
# install:
# test:
# lint:
# run:
```

## Repository map
| Path | Contents |
|------|----------|
| `docs/brief.md` | Initiative brief |
| `docs/requirements/` | Requirements (REQ-/NFR- IDs) |
| `docs/architecture.md` | Architecture |
| `docs/adr/` | Architecture decision records |
| `docs/test-strategy.md` | Test strategy |
| `docs/ops/runbook.md` | Runbook |
| `docs/user/` | User documentation (Diátaxis) |
| `docs/gates/` | Gate records |

## Autonomy level: A2 (default)
Allowed without asking: read anything; create branches; edit code, tests and
docs; run tests and linters; commit; open pull requests.

Ask first: adding dependencies; changing CI, infrastructure or security
settings; changing an approved requirement or an accepted ADR; deleting or
weakening tests.

Never: merge, approve gates, deploy to production, handle real secrets or
personal data, force-push to the main branch.

## Rules
- Write tests first, and reference requirement IDs in test names or comments.
- Update the relevant docs and `CHANGELOG.md` (Unreleased) in the same change.
- All artefacts are written in English.
- If this file is wrong or out of date, fix it as part of your task.
- When requirements, design and the task conflict, stop and ask.
