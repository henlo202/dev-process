#!/bin/sh
# Claude Code PreToolUse entry point (see settings.json): find a working
# Python, then run pre_tool_use.py, which reads the tool call from stdin.
# Exit code 2 blocks the tool call. Without a working Python the hook cannot
# check anything, so it blocks rather than silently allowing.
PROCESS_DIR="${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../../..}/.process"
. "$PROCESS_DIR/guardrails/find-python.sh"
if ! dev_process_find_python; then
  echo "Blocked by dev-process guardrails: no working Python 3.9+ found (tried python3, python, py -3)." >&2
  exit 2
fi
dev_process_python "$PROCESS_DIR/adapters/claude/pre_tool_use.py"
