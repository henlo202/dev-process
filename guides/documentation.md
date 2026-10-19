# Documentation

Documentation is written as code: it lives in the repository, is reviewed in
the same pull requests as the code, and is kept current by agents as part of
the Definition of Done.

## Three audiences, three artefacts

| Type | Audience | Artefacts | Framework |
|------|----------|-----------|-----------|
| **Technical** | Developers and agents working on the system | [Architecture](../artefacts/architecture.md), [ADRs](../artefacts/adr.md), `AGENTS.md`, code comments | arc42 / C4 (lightweight) |
| **Operational** | Whoever runs the system | [Runbook](../artefacts/runbook.md) | Runbook template |
| **User** | People using the software | [User docs](../artefacts/user-docs.md), release notes | Diátaxis |

## Rules
1. **Same PR rule.** A change that makes a doc wrong updates that doc in the same PR.
2. **Diagrams as text.** Use Mermaid or PlantUML, so agents can read and edit them.
3. **Exact commands.** Operational and `AGENTS.md` instructions use copy-pasteable commands, which agents should actually run to check them.
4. **No speculative docs.** Document what exists. Plans go in requirements, the plan or ADRs.
5. **English only.**

## Keeping docs honest
- The Documenter agent checks docs against the actual behaviour (run the commands, open the UI) at P6.
- The Reviewer agent flags code changes with no matching doc change.
- The conformance checker warns when required doc artefacts are missing for the tier, or when their frontmatter is invalid.
