#!/usr/bin/env python3
"""Claude Code PreToolUse hook: refuse agent shell commands that break dev-process rules.

Installed by `tooling/scaffold.py --adapter claude` into .claude/settings.json.
It reuses .process/guardrails/guard.py, so the rules stay in one place. Exit
code 2 blocks the tool call, and the message on stderr is shown to the agent.
It enforces the autonomy "never" list (no bypassing hooks, no merging, no
pushes to protected branches) whatever guardrails.mode says.
"""
import json
import sys
from pathlib import Path

GUARD_DIR = Path(__file__).resolve().parents[2] / "guardrails"
sys.path.insert(0, str(GUARD_DIR))

import guard  # noqa: E402


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    if event.get("tool_name") != "Bash":
        return 0
    command = (event.get("tool_input") or {}).get("command", "")
    cfg = guard.load_config(guard.repo_root())
    problems = guard.check_command(command, cfg)
    if not problems:
        return 0
    print("Blocked by dev-process guardrails:", file=sys.stderr)
    for p in problems:
        print(f"  - {p}", file=sys.stderr)
    print("Work on a feature branch, open a PR, and leave merging and overrides to the Owner "
          "(see AGENTS.md and docs/standards.md).", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
