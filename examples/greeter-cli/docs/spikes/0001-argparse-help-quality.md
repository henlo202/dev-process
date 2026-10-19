---
artefact: spike-report
status: done
updated: 2026-10-19
---
# Spike 0001: Is argparse's help output good enough?

- **Time-box:** 30 minutes of agent work
- **Branch:** spike/argparse-help (never merged, deleted)
- **Increment:** INC-001

## Question
NFR-001 forbids dependencies, which rules out click. Would argparse's
auto-generated help be clear enough for REQ-004, or would we need hand-written
help text?

## What was built or measured
A ten-line throwaway CLI with one positional argument and one `choices` option.
We ran `--help` and compared the output with a click equivalent.

## Findings
argparse's help is plainer, but it lists the arguments, choices and default
clearly once each argument has a `help=` string. No hand-written help is needed.

## Decision supported
Use argparse ([ADR-0001](../adr/0001-use-argparse.md)), and add `help=` strings to every argument.
