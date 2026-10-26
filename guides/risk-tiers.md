# Risk tiers

Tiers scale the process to the risk of the work. Without them, the process is
either too heavy for a typo fix or too light for a data migration.

Each increment (or T1 change) gets a tier. P0 and G0 run once per initiative, whatever the tier. The project's `.process/config.yaml` records the
**highest** tier currently expected, and that decides which initiative-level
artefacts must exist.

## Choosing a tier

| | T1 · Trivial | T2 · Standard | T3 · Major |
|---|---|---|---|
| **Examples** | Bug fix, copy change, dependency patch bump, config tweak | New feature, notable behaviour change, new integration | New initiative, new architecture, auth/security changes, data migrations, public API changes, anything hard to reverse |
| **Loop** | P2 → P3 → P4 | P1 → P2 → P3 → P4 → P5 | P1 → P2 → P3 → P4 → P5 |
| **Gates** | G2, G3 | G1, G2, G3 | G1 (with design scrutiny), G2, G3 |
| **Increment brief** | none | required | required |
| **Design** | none | Design notes in the increment brief, plus an ADR if needed | Design notes, ADRs, threat model, reviewed in depth at G1 |
| **Spikes** | rarely | when a question is open | expected for hard-to-reverse decisions |
| **Cooling-off** | none | none | G1: approve the next day at the earliest |
| **Reviews** | none: CI and your merge | one `standard` review per gate | `deep` reviews, ideally by a different model than the author |
| **Models** | mostly `fast` | mostly `standard`; architect `deep` | `deep` for design and review |
| **Budget** | none | per increment (S/M/L) | per increment (S/M/L) |

When unsure, pick the higher tier. An agent may **propose** a tier, but only the
Owner decides it.

## Escalation
If a T1 or T2 change turns out to touch something on the T3 list, stop and
re-tier it. The Implementer agent must flag this rather than continue.

Model classes and budgets per tier are explained in the [resource economy guide](resource-economy.md).
