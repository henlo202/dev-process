# Adoption & upgrades

## Adopting the process in a new project
```bash
git clone <dev-process repo> ~/dev-process
python ~/dev-process/tooling/scaffold.py path/to/project --name "My project" --tier T2
```
The scaffolder:
1. Creates `.process/` containing `config.yaml`, a snapshot of `process.yaml` and `check.py`
2. Creates `AGENTS.md`, `CHANGELOG.md` and the `docs/` artefacts required for the tier, from templates
3. Never overwrites existing files (it reports them as skipped)

Then run `python .process/check.py` and fill in the artefacts, starting with
`docs/brief.md` (phase P0).

## Adopting in an existing project
Run the scaffolder the same way. Existing files are kept, and the checker tells
you what is missing. Add waivers for anything you decide not to backfill.

## Upgrading a project
```bash
python ~/dev-process/tooling/scaffold.py path/to/project --upgrade
```
This refreshes `.process/process.yaml` and `.process/check.py`, and bumps
`process_version`. It never touches your artefacts. Read the CHANGELOG
"Upgrade" notes, run the checker, and fix or waive the new findings, all in a single PR.

## Deviating permanently
If a project genuinely does not need a rule (for example, a library has no runtime
to write a runbook for), record a [waiver](waivers.md) with a far expiry date and
a clear reason. If many projects need the same waiver, change the process instead.
