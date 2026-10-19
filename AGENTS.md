# AGENTS.md: dev-process (the process repository itself)

This repository *defines* the development process. It is not a project that
follows it in the normal way. Changes here follow
[governance/change-process.md](governance/change-process.md).

## Commands
```bash
pip install -r requirements.txt
python tooling/validate.py        # must pass before every commit
python site/build.py              # builds _site/; open _site/index.html
python tooling/scaffold.py /tmp/x --tier T3 && python /tmp/x/.process/check.py --project /tmp/x   # smoke test
python examples/greeter-cli/.process/check.py --project examples/greeter-cli
```

## Rules
- `process.yaml` holds the structure (relations between phases, gates, artefacts, roles and tiers); Markdown holds the prose. Never describe a relation only in prose.
- When you add a phase, gate, artefact or guide: add it to `process.yaml`, create its doc, and run `validate.py`.
- Changes to gates, required artefacts, tiers, autonomy or governance need a PDR in `governance/decisions/`.
- Bump `process.version` and add a `CHANGELOG.md` entry following `governance/versioning.md`.
- English only. Keep documents short; link instead of repeating.
- Agents may propose changes via PRs but never merge. Only the Owner merges.
- `tooling/check.py` must stay dependency-light (stdlib plus PyYAML) and must exit 0 unless `--strict` is given.
