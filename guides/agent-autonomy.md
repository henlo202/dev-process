# Agent autonomy levels

The autonomy level states what agents may do without asking. It is set in
`AGENTS.md`, by the Owner only.

| Level | Name | Agents may… | Typical use |
|-------|------|-------------|-------------|
| **A0** | Advise | Read, and suggest changes in chat | Unfamiliar or sensitive codebases |
| **A1** | Edit | A0 + edit files locally and run tests | Early in a new initiative |
| **A2** | Contribute *(default)* | A1 + create branches, commit, push branches, open PRs | Normal work |
| **A3** | Maintain | A2 + merge T1 PRs that have green CI and a clean reviewer summary | Mature projects with strong tests |

**Never at any level:** approve G0–G3 or G5, deploy to production, change
autonomy levels, add waivers, handle real secrets or production personal data.

A3 is the only level where an agent may close a gate (G4 for T1). Use it only
when the test suite is trustworthy. The Owner still reviews merged T1 changes
afterwards, at release (G5).

## Always ask first (A1–A3)
- Adding or upgrading dependencies (beyond patch versions)
- Changing CI, infrastructure, security or permission settings
- Changing an approved requirement or an accepted ADR
- Deleting or weakening tests
- Anything irreversible
