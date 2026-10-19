# PDR-0006: Restructure the process as an increment loop

- **Status:** accepted
- **Date:** 2026-10-19
- **Supersedes:** the phase and gate structure of v0.1.0. It updates the gate numbers referenced in PDR-0002.

## Context
v0.1.0 had eight sequential phases (requirements → design → plan → build →
verify → release → operate) with up to five sign-offs. Although it was meant to
be iterative, it read like a waterfall with agents in place of people, and agents
follow documents literally. It also ignored the main thing AI agents change:
building a throwaway version is now often cheaper than writing a careful
specification, so learning by building should come before specifying in detail.

## Options
1. Keep the structure, and add text saying "iterate".
2. Restructure around a short increment loop, with spikes, outcome-based gates and a size limit.
3. Drop the gates in favour of continuous flow with the Owner reviewing afterwards.

## Decision
Option 2:
1. **Loop.** P0 Initiate (once), then the loop P1 Shape → P2 Build → P3 Verify → P4 Release → P5 Learn, repeated for every increment. T1 changes enter at P2.
2. **Shape.** Requirements, design and planning merge into one phase, P1 Shape, with one gate, G1 Shape approved. T3 increments add a design-scrutiny section and the cooling-off period to G1, rather than a separate gate.
3. **Spikes.** Time-boxed, throwaway experiments on `spike/*` branches, recorded in spike reports and never merged. They are the preferred way to settle open questions.
4. **Outcome-based gates.** The final PR of each increment carries a demo, and the Owner watches it first at G2 Merge approved. Automated tests are still required.
5. **Size limit.** One outcome, at most 5 requirements and 8 slices per increment by default, with warnings from the conformance checker.

The gates are renumbered G0 Go/No-go, G1 Shape, G2 Merge, G3 Release. The task
plan artefact is replaced by the increment brief.

## Consequences
- Fewer gates for T3 (four instead of six) and the same number for T2 (three, plus G0), each smaller and backed by evidence.
- More artefact files (one increment brief per increment, plus spike reports), each short.
- Projects on v0.1.0 must migrate: see the Upgrade notes for v0.2.0 in `CHANGELOG.md`.
