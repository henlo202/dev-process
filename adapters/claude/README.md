# Adapter: Claude Code

Optional. Installed into a project with `tooling/scaffold.py --adapter claude`.

| File in the project | Purpose |
|---------------------|---------|
| `CLAUDE.md` | Imports `AGENTS.md`, so Claude Code reads the same instructions as every other agent |
| `.claude/skills/dev-process-*/` | Copies of the dev-process skills, discovered automatically |
| `.claude/agents/dev-process-*.md` | One subagent per role, so the orchestrator can delegate each step to a fresh context (reviews in particular) |
| `.claude/settings.json` | A `PreToolUse` hook running `.process/adapters/claude/pre_tool_use.sh`, which finds a working Python and runs `pre_tool_use.py` |

The hook calls the same `guard.py` as the git hooks. It refuses agent commands
that bypass hooks (`--no-verify`, `core.hooksPath`, the Owner override), merge
or approve pull requests, push to protected branches, or match the project's
`guardrails.agent_blocked_commands` patterns (for example, deploy commands).

If the project already has `.claude/settings.json`, the scaffolder leaves it
untouched and prints the hook entry to add by hand.
