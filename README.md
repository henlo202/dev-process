# dev-process

A standard, **tool-neutral** process for **AI-agentic software development**.
One human Owner, several AI agent roles, and human approval at defined gates.

- **Machine-readable:** [`process.yaml`](process.yaml) (validated by [JSON Schema](schema/process.schema.json)) plus Markdown with frontmatter
- **Human-navigable:** a generated HTML site (`python site/build.py`, output in `_site/`). Every CI run also attaches it as the `site` artifact. Publishing to GitHub Pages is optional: set the repository variable `PAGES_ENABLED=true` and set the Pages source to "GitHub Actions".
- **Enforced gently:** a conformance checker that warns and never blocks

## The process at a glance

The process is a **loop**. After a one-off setup, every change is a small
**increment**: one demonstrable outcome, shaped, built, verified, released and
learned from in a few days.

```
P0 Initiate ─G0─►  ┌─► P1 Shape ─G1─► P2 Build ─► P3 Verify ─G2─► P4 Release ─G3─► P5 Learn ─┐
  (once)           │                                                                         │
                   └──────────────────────── next increment ◄──────────────────────────────────┘
```

- **Shape, don't specify:** detail only the next increment, and settle open questions with throwaway [spikes](guides/spikes.md) rather than long documents.
- **Gate on outcomes:** the Owner approves merges after watching a [demo](artefacts/demo.md) of the increment working, backed by automated tests.
- **Stay small:** a [size limit](guides/increments.md#size-limit) per increment, checked automatically.
- **Enforce what matters:** coding standards, branching and "never" rules are enforced by [guardrails](guides/guardrails.md), not just written down.
- **Scale by risk:** T1 Trivial changes skip shaping, and T3 Major increments add design scrutiny at G1. See [risk tiers](guides/risk-tiers.md).
- **Spend wisely:** each step runs on the smallest suitable model class (`deep`, `standard`, `fast`), each increment has a budget, and agents stop instead of looping. See [resource economy](guides/resource-economy.md).

| Folder | Contents |
|--------|----------|
| [`phases/`](phases/) | P0 and the loop P1–P5: purpose, steps (who does what), exit criteria |
| [`gates/`](gates/) | G0–G3: human approval checklists |
| [`artefacts/`](artefacts/) | The standard artefacts, plus [`templates/`](artefacts/templates/) |
| [`roles/`](roles/roles.md) | The Owner and the agent roles |
| [`agents/`](agents/README.md) | Agent **skills** (`SKILL.md` format): one per role, plus task skills |
| [`adapters/`](adapters/claude/README.md) | Optional agent-tool integrations (Claude Code) |
| [`guides/`](guides/) | Increments, spikes, requirements, QA, documentation, security, tiers, autonomy, resource economy, glossary |
| [`governance/`](governance/ownership.md) | How the process itself is owned, changed, versioned and adopted |
| [`tooling/`](tooling/) | `scaffold.py`, `check.py` (conformance), `guardrails/` (enforcement), `validate.py`, CI snippets |
| [`site/`](site/) | HTML site generator |
| [`examples/`](examples/) | A worked example project |

## Quick start

```bash
pip install -r requirements.txt

# Adopt the process in a project (with blocking guardrails and Claude Code integration)
python tooling/scaffold.py ../my-project --name "My project" --tier T2 \
    --guardrails block --adapter claude --github --install-hooks
cd ../my-project && python .process/check.py

# Work on the process itself
python tooling/validate.py      # validate structure, links and versions
python site/build.py            # build the HTML site into _site/
```

## Using it day to day
Open your agent tool in the project and say **"continue"**. The
[orchestrator](guides/orchestration.md) asks `python .process/status.py` what
comes next, runs it, and stops only when you need to decide at a gate. You
state outcomes ("next, users should export CSV") and reply to gates
("approved"); everything in between runs on its own.

To save quota, run your main session on a mid-tier model: the orchestrator
delegates design and T3 reviews to subagents on stronger models, and mechanical
work to cheaper ones (`economy.models` in `.process/config.yaml`).

## Using it with agents
Point any agent at the project's `AGENTS.md`. Agent instructions are **skills**
in `.process/skills/`, which tools that support the format discover
automatically. Rules that must hold are enforced by **guardrails** (git hooks,
CI, optional agent-tool hooks) rather than left to instructions. See
[agents/README.md](agents/README.md) and [guides/guardrails.md](guides/guardrails.md).

## Governance
The Owner owns and approves all changes. Changes follow the
[change process](governance/change-process.md) and [semantic versioning](governance/versioning.md).
Projects pin a version and [upgrade](governance/adoption.md) deliberately.
