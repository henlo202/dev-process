# .process

Managed by dev-process `tooling/scaffold.py`. Everything here except `config.yaml` is overwritten on upgrade, so do not edit it by hand.

- `config.yaml`: this project's tier, test paths and waivers (yours to edit)
- `process.yaml`: snapshot of the pinned process version
- `check.py`: conformance checker (`python .process/check.py`)
- `playbooks/`: agent role playbooks
- `templates/`: artefact templates
