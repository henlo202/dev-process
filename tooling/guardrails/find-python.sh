# dev-process: find a working Python 3.9+ for the shell entry points.
# Sourced (not executed) by the git hooks, the CI scripts and agent adapters.
#
# dev_process_find_python  sets DEV_PROCESS_PY (and DEV_PROCESS_PY_ARG for the
#                          Windows launcher "py -3"); returns 1 if none works.
# dev_process_python ARGS  runs the Python that was found.
#
# Candidates (python3, python, py -3) are tried by running them, not by looking
# them up on PATH, because some systems have commands that exist but do not run
# Python (for example the Microsoft Store alias for python3 on Windows). A
# Python that can import PyYAML is preferred, because without it the guardrails
# can only read their defaults (warn mode).
dev_process_find_python() {
  DEV_PROCESS_PY=""
  DEV_PROCESS_PY_ARG=""
  _dp_first=""
  _dp_first_arg=""
  for _dp_candidate in python3 python py; do
    _dp_arg=""
    [ "$_dp_candidate" = py ] && _dp_arg=-3
    if "$_dp_candidate" ${_dp_arg:+"$_dp_arg"} -c 'import sys; sys.exit(sys.version_info < (3, 9))' </dev/null >/dev/null 2>&1; then
      if "$_dp_candidate" ${_dp_arg:+"$_dp_arg"} -c 'import yaml' </dev/null >/dev/null 2>&1; then
        DEV_PROCESS_PY=$_dp_candidate
        DEV_PROCESS_PY_ARG=$_dp_arg
        return 0
      fi
      if [ -z "$_dp_first" ]; then
        _dp_first=$_dp_candidate
        _dp_first_arg=$_dp_arg
      fi
    fi
  done
  if [ -n "$_dp_first" ]; then
    DEV_PROCESS_PY=$_dp_first
    DEV_PROCESS_PY_ARG=$_dp_first_arg
    return 0
  fi
  return 1
}

dev_process_python() {
  "$DEV_PROCESS_PY" ${DEV_PROCESS_PY_ARG:+"$DEV_PROCESS_PY_ARG"} "$@"
}
