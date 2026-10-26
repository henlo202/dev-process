# Adapter: Claude Code

Optional. Installed into a project with `tooling/scaffold.py --adapter claude`.

| File in the project | Purpose |
|---------------------|---------|
| `CLAUDE.md` | Imports `AGENTS.md`, so Claude Code reads the same instructions as every other agent |
| `.claude/skills/dev-process-*/` | Copies of the dev-process skills, discovered automatically |
| `.claude/agents/dev-process-*.md` | One subagent per role, so the orchestrator can delegate each step to a fresh context (reviews in particular). Each gets `model` and `effort` from its role's model class |
| `.claude/settings.json` | A `PreToolUse` hook running `.process/adapters/claude/pre_tool_use.sh`, which finds a working Python and runs `pre_tool_use.py` |

The hook calls the same `guard.py` as the git hooks. It refuses agent commands
that bypass hooks (`--no-verify`, `core.hooksPath`, the Owner override), merge
or approve pull requests, push to protected branches, or match the project's
`guardrails.agent_blocked_commands` patterns (for example, deploy commands).

If the project already has `.claude/settings.json`, the scaffolder leaves it
untouched and prints the hook entry to add by hand.

## Models
`--adapter claude` maps the [model classes](../../guides/resource-economy.md) in
`.process/config.yaml` to Claude Code aliases: `deep: opus`, `standard: sonnet`,
`fast: haiku`. Change them there (any alias or full model ID works), then run
`scaffold.py --upgrade` to regenerate the subagents.

- Each subagent's `model` and `effort` come from its role's class at the project tier. For example, at T3 the reviewer runs on `opus`.
- The main session (where the orchestrator runs) defaults to the `standard` model: the scaffolder adds `"model": "sonnet"` to `.claude/settings.json`. An existing `model` there is kept. Switch with `/model opus` for a hard conversation, or set your own default in `.claude/settings.local.json`.
- When delegating, the orchestrator can pass the step's `model` from `status.py` to override the subagent default, for example for an escalation.
- Optional: a `maxTurns` line in a subagent file puts a hard limit on runaway subagents.
