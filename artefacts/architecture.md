---
id: architecture
---
# Architecture document

**What it is:** The technical documentation of the system: a lightweight
arc42/C4-style description that is kept current, not written once.

## Contents
1. Context: the system, its users and external systems (C4 level 1)
2. Building blocks: containers and components, and their responsibilities (C4 levels 2–3)
3. Data: the main entities, storage, retention
4. Runtime view: the key flows, as sequence diagrams for the non-obvious ones
5. Deployment: environments, infrastructure, configuration
6. Cross-cutting concerns: security, logging, error handling, observability
7. Quality attributes: how each NFR is met
8. Links to ADRs

## Rules
- Diagrams as text (Mermaid or PlantUML), so agents can read and update them.
- Update the document in the same PR as the change that makes it outdated.
