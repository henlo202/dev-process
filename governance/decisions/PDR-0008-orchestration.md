# PDR-0008: An orchestrator runs the loop; agents may record the Owner's stated decisions

- **Status:** accepted
- **Date:** 2026-10-19

## Context
v0.3.0 defined phases, skills and gates, but nothing ran them in order. The
Owner had to start each step with a prompt. This also made the process depend
on the Owner remembering where each project stood.

## Options
1. Leave orchestration to the Owner's prompts.
2. An orchestrating agent that keeps its own memory of progress.
3. Deterministic state derived from the repository (`status.py`), plus an orchestrator skill that loops on it and stops at gates.

## Decision
Option 3.
- `.process/status.py` derives the phase and the next step from repository artefacts only: gate records, increment briefs (status and ticked slices), reviews in `docs/reviews/`, `CHANGELOG.md`, and git branches and tags.
- A new **Orchestrator** agent role and skill run the loop, delegating to role skills or subagents, and stop whenever the next step belongs to the Owner.
- **Recording decisions:** when the Owner states a gate decision in conversation, an agent may write the gate record via `status.py record-gate`, quoting the Owner verbatim (`recorded_by: agent`, `owner_statement`). The command refuses unless that gate is pending. The decision itself remains the Owner's alone. G2 is still recorded only by the Owner merging.
- Reviewer summaries for G0, G1 and G3 are stored in `docs/reviews/`, so readiness for a gate is visible in the repository.

## Consequences
- In daily use the Owner states outcomes and makes decisions; everything in between runs without prompting.
- Sessions can stop and resume at any time.
- An agent could misreport an Owner statement. Mitigations: verbatim quotes in versioned files, the refusal unless the gate is pending, and the rule that ambiguous replies are not approvals. A future compliance profile may require Owner-signed records instead.
