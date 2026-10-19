# Changing the process

The process changes the same way software does: proposal, review, decision,
release.

## Flow

```
Proposal ─► Draft PR ─► Reviewer agent summary ─► Owner decision ─► Merge ─► Release (version tag)
   │                                                     │
   └ issue, retrospective action                         └ reject: close with reason
     or recurring checker warning
```

1. **Propose.** Open an issue (or a draft PR) stating the problem, with evidence such as a retrospective, a repeated waiver or a confusing step.
2. **Draft.** Change the Markdown and `process.yaml` together. For any change that alters a gate, a required artefact, a tier rule or governance itself, add a **process decision record (PDR)** in `governance/decisions/`.
3. **Validate.** CI runs `tooling/validate.py` (schema, cross-references, links) and builds the site.
4. **Review.** A Reviewer agent summarises the impact: which projects are affected, and whether the change is major, minor or patch.
5. **Decide.** The Owner merges or closes the PR.
6. **Release.** Update `CHANGELOG.md`, bump `process.version` per [versioning](versioning.md), and tag `vX.Y.Z`.

## What needs a PDR
- Adding or removing a phase, gate or required artefact
- Changing tier rules or autonomy levels
- Changing governance (this section)
- Any decision you might later wonder about

Typos and clarifications need no PDR.

## Signals that the process needs to change
- The same waiver appears in several projects, so the rule is probably wrong.
- A gate is regularly approved without reading, so it is too heavy or in the wrong place.
- Agents repeatedly misunderstand a step, so the skill is unclear.
- A retrospective action is routed to "process change".
