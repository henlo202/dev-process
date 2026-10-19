# CLAUDE.md

This project's agent instructions live in `AGENTS.md` (the tool-neutral
convention). It is imported here so that Claude Code loads it:

@AGENTS.md

dev-process skills are installed in `.claude/skills/`, role subagents in
`.claude/agents/`, and guardrail hooks in
`.claude/settings.json`. Do not edit those copies; they are refreshed by
`scaffold.py --upgrade` from `.process/`.
