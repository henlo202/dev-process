---
artefact: increment
increment: INC-002
status: done
requirements: [REQ-002, REQ-003, REQ-004]
owner: Planner agent
updated: 2026-10-19
---
# INC-002: Swedish greeting and input validation

## Outcome
`--lang sv` greets in Swedish, an empty name is rejected cleanly, and `--help` explains the tool.

## Requirements in scope
- REQ-002: Greet in Swedish
- REQ-003: Reject an empty name (added after INC-001's learnings)
- REQ-004: Helpful usage text (checked manually; waiver in `.process/config.yaml`)

## Design notes
- Greetings live in a `GREETINGS` dict keyed by language code, and argparse `choices` comes from its keys.
- Validation is in `greeting()`, which raises `ValueError`. The CLI maps that to exit code 2 and stderr, consistent with argparse's own usage errors.

## Spikes
- none

## Task slices
- [x] S1: `--lang sv` (REQ-002)
- [x] S2: empty and whitespace-only name rejected with exit code 2 (REQ-003)
- [x] S3: help text and the user reference doc (REQ-004)

## Demo
Terminal transcript against the real build (`PYTHONPATH=src`):
```
$ python -m greeter Ada --lang sv
Hej, Ada!
exit=0
$ python -m greeter "  "
greet: error: name must not be empty
exit=2
$ python -m greeter --help
usage: greet [-h] [--lang {en,sv}] name

Print a friendly greeting.

positional arguments:
  name            the name of the person to greet

options:
  -h, --help      show this help message and exit
  --lang {en,sv}  language of the greeting (default: en)
```

## Learnings
- Two increments were enough for v0.1.0. The next candidate is a third language, which would be a T2 increment.
