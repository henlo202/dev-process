---
artefact: runbook
status: approved
version: 1.0.0
owner: Documenter agent
updated: 2026-10-19
---
# greeter-cli: Runbook

## 1. Overview & dependencies
A command-line tool with no runtime service and no dependencies beyond Python 3.9+.

## 2. Deploy (release)
```bash
python -m unittest discover -s tests
git tag -a v0.1.0 -m "Release v0.1.0 (G5 checklist in tag message)"
git push origin v0.1.0
```

## 3. Rollback
```bash
# Users pin the previous tag:
git checkout v0.0.9
```

## 4. Configuration & secrets
None.

## 5. Monitoring & alerts
Not applicable: there is no running service. Issues are reported via the issue tracker.

## 6. Common problems
| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError: greeter` | Run from the project root, or set `PYTHONPATH=src` |

## 7. Backup & restore
Not applicable: the tool keeps no state.

## 8. Post-incident notes
None yet.
