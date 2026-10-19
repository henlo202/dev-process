# greeter-cli: worked example

A deliberately tiny project, taken through dev-process at tier **T2**. It shows
what every standard artefact looks like when filled in, and how tests trace to
requirements.

It was created with:
```bash
python tooling/scaffold.py examples/greeter-cli --name greeter-cli --tier T2
```

| Look at | To see |
|---------|--------|
| `docs/brief.md` | A filled-in brief, approved at G0 |
| `docs/requirements/core.md` | REQ/NFR IDs and Given/When/Then acceptance criteria |
| `tests/test_cli.py` | Tests named after requirement IDs (`test_REQ_001_...`) |
| `docs/gates/` | Gate records for G0 and G1 |
| `.process/config.yaml` | A waiver with a reason and an expiry date |
| `python .process/check.py` | A clean conformance and traceability report |

```bash
cd examples/greeter-cli
python -m unittest discover -s tests
PYTHONPATH=src python -m greeter Ada --lang sv
python .process/check.py
```
