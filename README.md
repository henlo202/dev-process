# dev-process

A standard, **tool-neutral** process for **AI-agentic software development**.
One human Owner, several AI agent roles, and human approval at defined gates.

- **Machine-readable:** [`process.yaml`](process.yaml) (validated by [JSON Schema](schema/process.schema.json)) plus Markdown with frontmatter
- **Human-navigable:** a generated HTML site (`python site/build.py`, output in `_site/`). Every CI run also attaches it as the `site` artifact. Publishing to GitHub Pages is optional: set the repository variable `PAGES_ENABLED=true` and set the Pages source to "GitHub Actions".
- **Enforced gently:** a conformance checker that warns and never blocks

## The process at a glance

```
 P0 Initiate ─G0─► P1 Requirements ─G1─► P2 Design ─G2─► P3 Plan ─G3─► P4 Build ─► P5 Verify ─G4─► P6 Release ─G5─► P7 Operate & Learn
 (once)                                                                    ▲                                              │
                                                                           └──────────── next increment ◄─────────────────┘
```

How much of the process applies is set by the **risk tier**: T1 Trivial, T2 Standard or T3 Major. See [guides/risk-tiers.md](guides/risk-tiers.md).

| Folder | Contents |
|--------|----------|
| [`phases/`](phases/) | P0–P7: purpose, steps (who does what), exit criteria |
| [`gates/`](gates/) | G0–G5: human approval checklists |
| [`artefacts/`](artefacts/) | The standard artefacts, plus [`templates/`](artefacts/templates/) |
| [`roles/`](roles/roles.md) | The Owner and the agent roles |
| [`agents/`](agents/README.md) | Tool-neutral playbooks for each agent role |
| [`guides/`](guides/) | Requirements, QA, documentation, security, tiers, autonomy, glossary |
| [`governance/`](governance/ownership.md) | How the process itself is owned, changed, versioned and adopted |
| [`tooling/`](tooling/) | `scaffold.py`, `check.py` (conformance), `validate.py`, CI snippets |
| [`site/`](site/) | HTML site generator |
| [`examples/`](examples/) | A worked example project |

## Quick start

```bash
pip install -r requirements.txt

# Adopt the process in a project
python tooling/scaffold.py ../my-project --name "My project" --tier T2 --github
cd ../my-project && python .process/check.py

# Work on the process itself
python tooling/validate.py      # validate structure, links and versions
python site/build.py            # build the HTML site into _site/
```

## Using it with agents
Point any agent at the project's `AGENTS.md`. It links to the role playbooks in
`.process/playbooks/`. See [agents/README.md](agents/README.md).

## Governance
The Owner owns and approves all changes. Changes follow the
[change process](governance/change-process.md) and [semantic versioning](governance/versioning.md).
Projects pin a version and [upgrade](governance/adoption.md) deliberately.
