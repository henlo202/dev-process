# .process

Managed by dev-process `tooling/scaffold.py`. Everything here except `config.yaml` is overwritten on upgrade, so do not edit it by hand.

- `config.yaml`: this project's tier, limits, guardrails and waivers (yours to edit)
- `process.yaml`: snapshot of the pinned process version
- `check.py`: conformance checker (`python .process/check.py`, warns only)
- `status.py`: current phase and next step (`python .process/status.py`)
- `skills/`: agent skills (`<name>/SKILL.md`)
- `guardrails/`: enforcement (`git config core.hooksPath .process/guardrails/git-hooks`)
- `adapters/`: optional agent-tool integrations
- `templates/`: artefact templates
