---
id: adr
---
# Architecture decision records (ADRs)

**What it is:** A short, immutable record of one significant decision: the
context, the options considered, the decision, and its consequences.

**Where:** `docs/adr/NNNN-short-title.md`, numbered in sequence.

## When to write one
Write an ADR when a decision is hard to reverse, affects several components,
introduces a dependency, or would make a future reader ask "why on earth did they do this?".

## Rules
- Never edit an accepted ADR's decision. Write a new ADR that supersedes it, and link the two.
- At least two real options must be considered.
- Agents propose ADRs. The Owner accepts them (at G2 for T3, at G4 otherwise).
