# Roles

dev-process assumes **one human, the Owner**, working with several AI agent
roles. A "role" is a hat, not necessarily a separate tool or model: one agent
session can play several roles. The exception is the **Reviewer**, which should
run in a separate, fresh session where possible, so that it does not mark its
own homework.

## Human

### Owner
- Sets direction and priorities. Writes or approves the brief.
- Approves **every** gate (G0–G5). This cannot be delegated to an agent.
- Owns `AGENTS.md`, the autonomy level and all waivers.
- Owns the process itself (see [governance](../governance/ownership.md)).

## Agents

| Role | Main phases | Produces | Must not |
|------|-------------|----------|----------|
| **Analyst** | P0, P1 | Brief draft, requirements, acceptance criteria | Invent requirements without a source |
| **Architect** | P2 | Architecture doc, ADRs, test strategy, risk register | Accept its own ADRs |
| **Planner** | P3 | Task plan | Create tasks without requirement links |
| **Implementer** | P4 | Code, commits, pull requests | Merge, deploy, weaken tests |
| **Tester** | P4, P5 | Tests from acceptance criteria, gap analysis | Delete failing tests to go green |
| **Reviewer** | before every gate | Reviewer summaries | Soften findings; review in the same session that did the work |
| **Documenter** | P4, P6, P7 | User docs, runbook, changelog, release notes | Document behaviour that is not implemented |

## Who decides what

| Decision | Owner | Agents |
|----------|:-----:|:------:|
| Start or stop an initiative | ✅ decides | draft brief |
| Requirements content | ✅ approves | propose |
| Architecture and ADRs | ✅ approves | propose |
| Task breakdown | ✅ approves (T3) | propose |
| Code changes | ✅ merges | write |
| Release | ✅ approves | prepare |
| Autonomy level and waivers | ✅ decides | n/a |
| Process changes | ✅ approves | may propose |
