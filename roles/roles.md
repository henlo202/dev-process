# Roles

dev-process assumes **one human, the Owner**, working with several AI agent
roles. A "role" is a hat, not necessarily a separate tool or model: one agent
session can play several roles. The exception is the **Reviewer**, which should
run in a separate, fresh session where possible, so that it does not mark its
own homework.

## Human

### Owner
- Sets direction and priorities. Writes or approves the brief.
- Approves **every** gate (G0–G3). This cannot be delegated to an agent. The orchestrator may *record* a decision the Owner has stated, verbatim ([PDR-0008](../governance/decisions/PDR-0008-orchestration.md)).
- In day-to-day use, only states outcomes and makes gate decisions. The [orchestrator](../guides/orchestration.md) runs everything in between.
- Owns `AGENTS.md`, the autonomy level and all waivers.
- Owns the process itself (see [governance](../governance/ownership.md)).

## Agents

| Role | Main phases | Produces | Must not |
|------|-------------|----------|----------|
| **Orchestrator** | all | Runs the loop: asks `.process/status.py` for the next step, delegates it, records the Owner's stated gate decisions | Approve, merge or release; record a decision the Owner did not state |
| **Analyst** | P0, P1 | Brief draft, requirements for the next increment, acceptance criteria | Invent requirements without a source |
| **Architect** | P0, P1 | Design notes, ADRs, design spikes, test strategy, risk register | Accept its own ADRs |
| **Planner** | P0, P1 | Increment brief, slices, size check | Let an increment exceed the size limit silently |
| **Implementer** | P1, P2, P3 | Spikes, code, commits, pull requests, demos | Merge, deploy, weaken tests, merge spike code |
| **Tester** | P2, P3 | Tests from acceptance criteria, gap analysis | Delete failing tests to go green |
| **Reviewer** | before every gate | Reviewer summaries | Soften findings; review in the same session that did the work |
| **Documenter** | P2, P4, P5 | User docs, runbook, changelog, release notes | Document behaviour that is not implemented |

Each agent role has a matching skill, `dev-process-<role>` (see [agent skills](../agents/README.md)),
which any agent can load to play that role. Each role also has a default
[model class](../guides/resource-economy.md) (`deep`, `standard` or `fast`), set in
`process.yaml` and shown in the "Model classes" panel of the HTML site and on each skill's page.

## Who decides what

| Decision | Owner | Agents |
|----------|:-----:|:------:|
| Start or stop an initiative | ✅ decides | draft brief |
| Increment scope, requirements and approach (shape) | ✅ approves | propose, spike |
| Hard-to-reverse decisions (ADRs) | ✅ approves | propose |
| Code changes | ✅ merges | write |
| Release | ✅ approves | prepare |
| Autonomy level and waivers | ✅ decides | n/a |
| Process changes | ✅ approves | may propose |
