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
- Work happens in small **increments** (`docs/increments/`), each looping
  through P1 Shape → P2 Build → P3 Verify → P4 Release → P5 Learn. Before
  starting, find out which increment and phase you are in, and follow that
  phase's steps. T1 changes start at P2.
- When a question cannot be settled on paper, run a time-boxed **spike** on a
  `spike/*` branch, and record a spike report. Spike code is never merged.
- Human gates (G0–G3) are approved only by the Owner. **Never** approve a
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
| `docs/increments/` | Increment briefs (INC- IDs): outcome, scope, slices, demo |
| `docs/requirements/` | Requirements (REQ-/NFR- IDs) |
| `docs/spikes/` | Spike reports |
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
