---
id: agents-context
---
# Agent context file (`AGENTS.md`)

**What it is:** The single entry point any AI coding agent reads before working
in the project. It uses the open, tool-neutral `AGENTS.md` convention. Tool-specific
files (for example `CLAUDE.md` or `.cursor/rules`) should contain only a pointer
to `AGENTS.md`.

## Contents
1. What the project is (a one-paragraph summary, plus a link to the brief)
2. That the project follows dev-process, which version, and its current tier
3. How to build, test, lint and run the project locally (exact commands)
4. Repository map: where code, tests and docs live
5. Coding conventions and the definition of done
6. **Autonomy level**: what agents may and may not do without asking
7. Where the artefacts are, and the rule to keep them current

## Rules
- Exact commands only. If a command in `AGENTS.md` fails, fixing `AGENTS.md` is part of the task.
- Keep it under about 200 lines. Link to detail instead of copying it.
