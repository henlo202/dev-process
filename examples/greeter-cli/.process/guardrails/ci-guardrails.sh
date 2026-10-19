#!/usr/bin/env sh
# Run dev-process guardrails in CI: lint/format and commit messages since BASE.
# Exits 1 on violations when guardrails.mode is "block" (hard enforcement),
# unlike .process/process-check.sh, which always exits 0.
# Usage: sh .process/guardrails/ci-guardrails.sh [BASE_REF]
cd "$(dirname "$0")/../.." || exit 1
python3 -c "import yaml" 2>/dev/null || python3 -m pip install --quiet pyyaml
if [ -n "${1:-}" ]; then
  exec python3 .process/guardrails/guard.py ci --base "$1"
fi
exec python3 .process/guardrails/guard.py ci
