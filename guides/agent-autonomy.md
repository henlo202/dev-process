# Agent autonomy levels

The autonomy level states what agents may do without asking. It is set in
`AGENTS.md`, by the Owner only.

| Level | Name | Agents may… | Typical use |
|-------|------|-------------|-------------|
| **A0** | Advise | Read, and suggest changes in chat | Unfamiliar or sensitive codebases |
| **A1** | Edit | A0 + edit files locally and run tests | Early in a new initiative |
| **A2** | Contribute *(default)* | A1 + create branches, commit, push branches, open PRs, run time-boxed spikes | Normal work |
| **A3** | Maintain | A2 + merge T1 PRs that have green CI and a clean reviewer summary | Mature projects with strong tests |

**Never at any level:** approve G0, G1 or G3, merge spike code, bypass a guardrail (`--no-verify`, changing `core.hooksPath`, the Owner override), deploy to production, change
autonomy levels, add waivers, handle real secrets or production personal data.

A3 is the only level where an agent may close a gate (G2 for T1). Use it only
when the test suite is trustworthy. The Owner still reviews merged T1 changes
afterwards, at release (G3).

## Recording decisions
At every level, an agent may **record** a gate decision that the Owner has explicitly stated, quoting it verbatim (`.process/status.py record-gate`). Recording is not approving. See [PDR-0008](../governance/decisions/PDR-0008-orchestration.md).

## Enforcement
Autonomy levels are guidance in `AGENTS.md`. The "never" list is also enforced
by [guardrails](guardrails.md) where possible: git hooks block pushes to protected branches, and
agent-tool adapters refuse bypasses, merges and blocked commands before they run.

## Always ask first (A1–A3)
- Adding or upgrading dependencies (beyond patch versions)
- Changing CI, infrastructure, security or permission settings
- Changing an approved requirement or an accepted ADR
- Deleting or weakening tests
- Anything irreversible
