# Risk tiers

Tiers scale the process to the risk of the work. Without them, the process is
either too heavy for a typo fix or too light for a data migration.

Each piece of work gets a tier. The project's `.process/config.yaml` records the
**highest** tier currently expected, and that decides which initiative-level
artefacts must exist.

## Choosing a tier

| | T1 · Trivial | T2 · Standard | T3 · Major |
|---|---|---|---|
| **Examples** | Bug fix, copy change, dependency patch bump, config tweak | New feature, notable behaviour change, new integration | New initiative, new architecture, auth/security changes, data migrations, public API changes, anything hard to reverse |
| **Phases** | P4 → P5 → P6 | P1 → P2 (light) → P3 (light) → P4 → P5 → P6 → P7 | All, P0–P7 |
| **Gates** | G4, G5 | G1, G4, G5 | G1–G5 (plus G0 once per initiative) |
| **Design** | none | Update architecture doc, ADR if needed | Full design, ADRs, threat model |
| **Cooling-off** | none | none | G2: approve the next day at the earliest |

When unsure, pick the higher tier. An agent may **propose** a tier, but only the
Owner decides it.

## Escalation
If a T1 or T2 change turns out to touch something on the T3 list, stop and
re-tier it. The Implementer agent must flag this rather than continue.
