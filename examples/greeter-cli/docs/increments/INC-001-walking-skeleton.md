---
artefact: increment
increment: INC-001
status: done
requirements: [REQ-001, NFR-001]
owner: Planner agent
updated: 2026-10-19
---
# INC-001: Walking skeleton (greet in English)

## Outcome
`python -m greeter Ada` prints "Hello, Ada!". It is installable with no dependencies, tested in CI and documented.

## Requirements in scope
- REQ-001: Greet a person by name
- NFR-001: No third-party dependencies

## Design notes
- `greeter.core.greeting()` is a pure function, and `greeter.cli.main(argv)` does the I/O and exit codes.
- argparse rather than click: see [ADR-0001](../adr/0001-use-argparse.md), backed by [spike 0001](../spikes/0001-argparse-help-quality.md).

## Spikes
- [0001: Is argparse's help output good enough?](../spikes/0001-argparse-help-quality.md)

## Task slices
- [x] S1: core `greeting()` and the English CLI path (REQ-001)
- [x] S2: test that the code imports only the standard library (NFR-001)
- [x] S3: AGENTS.md commands, user reference doc, runbook

## Demo
Terminal transcript against the real build (`PYTHONPATH=src`):
```
$ python -m greeter Ada
Hello, Ada!
exit=0
```
NFR-001: `test_NFR_001_standard_library_only` passes in CI.

## Learnings
- The walking skeleton took less than an hour, so the next increment can carry more scope.
- Empty input was not covered by any requirement. It was added as REQ-003 when INC-002 was shaped.
