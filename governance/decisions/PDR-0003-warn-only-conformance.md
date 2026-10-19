# PDR-0003: Conformance checks warn and never block

- **Status:** accepted
- **Date:** 2026-10-19

## Context
A blocking checker makes the process feel like bureaucracy and pushes people to
fake artefacts. A silent process drifts.

## Decision
The conformance checker always exits with status 0. It produces a clear report
with severities (❌ error, ⚠️ warning, ℹ️ info), explains each finding, and links
to the relevant rule. The Owner reviews it at G4.

A future compliance profile may make selected rules blocking for specific
projects (see `guides/compliance.md`).

## Consequences
- Deviations are always visible, and decisions stay with the Owner.
- It relies on discipline at G4, supported by the checklist item "conformance warnings fixed or waived".
