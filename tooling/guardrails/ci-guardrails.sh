#!/usr/bin/env sh
# Run dev-process guardrails in CI: lint/format and commit messages since BASE.
# Exits 1 on violations when guardrails.mode is "block" (hard enforcement),
# unlike .process/process-check.sh, which always exits 0.
# Usage: sh .process/guardrails/ci-guardrails.sh [BASE_REF]
cd "$(dirname "$0")/../.." || exit 1
. .process/guardrails/find-python.sh
if ! dev_process_find_python; then
  echo "dev-process guardrails: no working Python 3.9+ found (tried python3, python, py -3)." >&2
  exit 1
fi
dev_process_python -c "import yaml" 2>/dev/null || dev_process_python -m pip install --quiet pyyaml
if [ -n "${1:-}" ]; then
  dev_process_python .process/guardrails/guard.py ci --base "$1"
  exit $?
fi
dev_process_python .process/guardrails/guard.py ci
