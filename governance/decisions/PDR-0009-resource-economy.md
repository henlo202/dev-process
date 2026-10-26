# PDR-0009: Resource economy: model classes, budgets and stop-loss

- **Status:** accepted
- **Date:** 2026-10-26

## Context
Using the process with an AI agent tool often ran out of quota. Every step ran
on the same model, usually the most capable one, whatever the task. Sessions and
context grew without limit, and nothing stopped an agent that kept retrying a
failing step. The process had no rules on resource use at all.

## Options
1. Leave model choice and cost to each project.
2. Name concrete models in the process.
3. Abstract **model classes** (`deep`, `standard`, `fast`) in the process, mapped to concrete models per project, plus per-increment budgets and stop-loss rules.

## Decision
Option 3 ([resource economy guide](../../guides/resource-economy.md)).
- `process.yaml` defines the model classes. Each agent role and task skill has a default class, with optional per-tier overrides (`tier_model_class`).
- Projects map classes to models in `.process/config.yaml` (`economy.models`). Adapters may fill in defaults.
- `status.py` names the model class, model and effort for every agent step.
- **Escalation:** after `economy.max_attempts` failed attempts at one step, an agent may move up one class and must record why. Anything beyond that needs the Owner.
- **Budgets:** each increment has a budget in agent steps (`budget`, `spent`), set while shaping and approved at G1. When it is used up, the next step goes to the Owner. Only the Owner extends a budget (`status.py set-budget`, quoting the Owner verbatim, as with PDR-0008).
- **Context rules:** compact handoffs, sessions end at gates, a line limit for `AGENTS.md`, proportional tests and reviews.
- **Reviews:** T1 changes get no separate review step; G2 for T1 rests on CI and the Owner's merge.
- New warn-only checks report missing mappings and budgets, overruns and an overlong `AGENTS.md`.

## Consequences
- Most steps run on cheaper models, and runaway work is stopped at a known limit.
- "Agent steps" are a rough measure, chosen because every tool can count them. Real token costs differ per step. The Learnings resource line and retrospectives are where budgets get recalibrated.
- A `fast` model may produce weaker results on some steps. Escalation and the Owner's gates catch this. When a class keeps escalating, change its default in a later process version.
- The budget adds a small bookkeeping step (`log-step`) after each agent step.
