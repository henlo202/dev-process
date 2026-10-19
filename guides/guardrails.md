# Guardrails: making rules stick

Agent instructions (`AGENTS.md`, skills) are **guidance**. An agent usually
follows them, but can skip, misread or lose them during a long session. Rules
that must never be broken need **enforcement**: tooling that checks or blocks,
whatever the agent decides.

## Three layers

| Layer | What | Applies | Strength |
|-------|------|---------|----------|
| 1. Always-on rules | `AGENTS.md`, loaded at the start of every session | every task | advisory |
| 2. Skills | `.process/skills/*/SKILL.md`, loaded when a task matches | relevant tasks | advisory |
| 3. Guardrails | git hooks, CI, agent-tool hooks, server-side protection | every action | **hard** (in `block` mode) |

**Rule of thumb:** anything that must never be violated belongs in layer 3.
Layers 1 and 2 explain the rule and how to comply with it. Each rule in
[engineering standards](../artefacts/standards.md) names its layer-3 enforcement.

## What dev-process provides (tool neutral)

| Guardrail | Enforces | How |
|-----------|----------|-----|
| `pre-commit` hook | No commits on protected branches; lint/format clean | `.process/guardrails/guard.py pre-commit` |
| `commit-msg` hook | Commit message convention | `guard.py commit-msg` |
| `pre-push` hook | No pushes to protected branches; branch naming | `guard.py pre-push` |
| CI step | Lint/format, plus commit messages in the PR | `.process/guardrails/ci-guardrails.sh <base>` |

The hooks, CI scripts and adapters find Python with `.process/guardrails/find-python.sh`:
they try `python3`, `python` and `py -3` by running them (so the Windows Store alias is skipped)
and prefer one that has PyYAML. Without PyYAML the guardrails can only use their defaults (warn mode).

Install the hooks in every clone, including every fresh agent container:

```bash
git config core.hooksPath .process/guardrails/git-hooks
```

`AGENTS.md` lists this as a setup command, so agents run it themselves.

### Configuration (`.process/config.yaml`)
```yaml
guardrails:
  mode: block                 # block | warn (warn prints, never refuses)
  protected_branches: [main, master]
  branch_pattern: '^(task|fix|spike|docs|chore|release)/[A-Za-z0-9._/-]+$'
  commit_pattern: '^(feat|fix|docs|test|refactor|perf|build|ci|chore|style|revert|spike)(\([^)]+\))?!?: .+'
  lint_command: "ruff check . && ruff format --check ."
  agent_blocked_commands: ['\bkubectl\s+apply\b', '\bterraform\s+apply\b']
```

Guardrails are **opt-in to block**: new projects start in `warn` mode, and the
Owner switches to `block` (`scaffold.py --guardrails block`). This is separate
from the conformance checker, which always only warns ([PDR-0003](../governance/decisions/PDR-0003-warn-only-conformance.md)).

## Agent-tool adapters (optional)
Git hooks can be bypassed (`git commit --no-verify`, or by changing `core.hooksPath`).
An agent-tool adapter closes that gap by refusing such commands before they run.
The Claude Code adapter (`scaffold.py --adapter claude`) installs a `PreToolUse`
hook that uses the same `guard.py` rules, and also refuses `gh pr merge`, PR
approvals, pushes to protected branches, the Owner override, and any
`agent_blocked_commands`. Adapters for other tools follow the same pattern.

## Server-side protection (recommended where available)
Hosting platforms can block pushes to `main` and require pull requests with
passing CI (on GitHub: branch protection or rulesets). This is the strongest
layer, because nothing local can bypass it. Availability depends on your plan
for private repositories. If you have it, turn it on. If not, the hooks and the
adapter are your enforcement.

## Escape hatch (Owner only)
For a single deliberate exception, the Owner can run a command with
`DEV_PROCESS_OWNER_OVERRIDE=1`. The guardrail prints what it allowed. Agents
must never use it: the adapter refuses it, and the autonomy guide forbids it.
