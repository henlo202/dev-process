# PDR-0002: A single human Owner approves gates, supported by a Reviewer agent

- **Status:** accepted (gate numbers updated by [PDR-0006](PDR-0006-increment-loop.md): the cooling-off now applies to G1 for T3, and agent merges at A3 to G2 for T1)
- **Date:** 2026-10-19

## Context
All initiatives are run by one person. There is no second human to review.
Self-approval invites rubber-stamping, especially when agents produce large
volumes of plausible-looking work.

## Options
1. Gates approved by the Owner on their own.
2. Gates approved by the Owner after a structured critique from a separate Reviewer agent, using concrete checklists and, for T3, a cooling-off period.
3. Agents approve some gates autonomously.

## Decision
Option 2. Every gate requires a reviewer summary and a ticked checklist. G2 for T3
has a one-day cooling-off period. Agents may close G4 for T1 only at autonomy level A3.

## Consequences
- Slightly slower gates, with much better scrutiny.
- If a team grows later, roles can be split without restructuring the process.
