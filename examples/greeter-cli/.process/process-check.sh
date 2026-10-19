#!/usr/bin/env sh
# Run the dev-process conformance check in any CI system.
# Always exits 0: the check warns, it never blocks (PDR-0003).
# The report is printed and written to process-report.md. If the CI system
# offers a job-summary file (e.g. GITHUB_STEP_SUMMARY), the report is appended there.
set -u
cd "$(dirname "$0")/.." || exit 0
. .process/guardrails/find-python.sh
if ! dev_process_find_python; then
  echo "dev-process check: no working Python 3.9+ found (tried python3, python, py -3); skipping." >&2
  exit 0
fi

if ! dev_process_python -c "import yaml" 2>/dev/null; then
  dev_process_python -m pip install --quiet pyyaml 2>/dev/null || pip install --quiet pyyaml 2>/dev/null || true
fi

dev_process_python .process/check.py --output process-report.md || true

if [ -n "${GITHUB_STEP_SUMMARY:-}" ] && [ -f process-report.md ]; then
  cat process-report.md >> "$GITHUB_STEP_SUMMARY"
fi
exit 0
