# greeter-cli: worked example

A deliberately tiny project, taken through dev-process at tier **T2** in two
increments. It shows what every standard artefact looks like when filled in, how
an increment goes round the loop, and how tests trace to requirements.

It was created with:
```bash
python tooling/scaffold.py examples/greeter-cli --name greeter-cli --tier T2
```

| Look at | To see |
|---------|--------|
| `docs/brief.md` | A filled-in brief, approved at G0 |
| `docs/increments/` | Two increment briefs, each with its outcome, slices, real demo transcript and learnings |
| `docs/spikes/0001-*.md` | A spike that settled a design question (it backs ADR-0001) |
| `docs/requirements/core.md` | REQ/NFR IDs and Given/When/Then acceptance criteria |
| `tests/test_cli.py` | Tests named after requirement IDs (`test_REQ_001_...`) |
| `docs/gates/` | Gate records for G0, and for G1 of each increment |
| `docs/standards.md` | Engineering standards, each naming its enforcement |
| `.process/config.yaml` | Guardrails in `block` mode with a ruff lint command, and a waiver with a reason and an expiry date |
| `CLAUDE.md`, `.claude/` | The Claude Code adapter: skills plus a hook that refuses bypasses and merges |
| `python .process/check.py` | A clean conformance and traceability report |
| `python .process/status.py` | Where the project stands: both increments are done, so the next step is preparing a release |
| `.claude/agents/` | Role subagents the orchestrator delegates to |

```bash
cd examples/greeter-cli
python -m unittest discover -s tests
PYTHONPATH=src python -m greeter Ada --lang sv
python .process/check.py
```
