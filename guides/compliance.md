# Compliance profiles (future)

dev-process currently has **no compliance requirements**. It is, however,
designed so that a compliance regime (e.g. ISO 27001, SOC 2, GDPR-heavy work,
or sector rules) can be added later without redesigning it.

## What is already in place
- **Gate records** in `docs/gates/`: who approved what, when, and against which artefact versions.
- **Traceability** from requirements to tests to releases.
- **Versioned process** pinned per project, so you can show which rules applied at the time.
- **Waivers** that are explicit, have a reason and expire, so deviations are documented.
- **Risk register and threat model** for T3 work.

## How a profile would be added
A compliance profile is an overlay, selected per project in `.process/config.yaml`:

```yaml
profiles: [iso27001]
```

A profile may:
1. Add checklist items to existing gates
2. Add required artefacts (e.g. access review, DPIA)
3. Raise default tiers for certain kinds of change
4. Make specific conformance rules strict (blocking) for that project only

Adding the first profile is a **major** process change (see [versioning](../governance/versioning.md)),
made through the [change process](../governance/change-process.md).
