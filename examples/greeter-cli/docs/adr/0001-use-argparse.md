---
artefact: adr
status: approved
updated: 2026-10-19
---
# ADR-0001: Use argparse for the command line

## Context
NFR-001 forbids third-party dependencies. The CLI is tiny.

## Options considered
1. **argparse** (standard library): no dependency, and good enough help output. It is more verbose to write.
2. **click**: nicer API, but a third-party dependency that violates NFR-001.

## Decision
argparse.

## Consequences
Help text is less polished (REQ-004 is checked manually). Revisit if the CLI grows sub-commands.

## Links
- Requirements: NFR-001, REQ-004
- Evidence: [spike 0001](../spikes/0001-argparse-help-quality.md)
