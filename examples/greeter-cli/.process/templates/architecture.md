---
artefact: architecture
status: draft
version: 0.1.0
owner: Architect agent
updated: {{date}}
---
# {{project}}: Architecture

## 1. Context
```mermaid
flowchart LR
  user([User]) --> system[{{project}}]
  system --> ext[(External system)]
```

## 2. Building blocks
| Component | Responsibility | Technology |
|-----------|----------------|------------|
| | | |

## 3. Data
<Main entities, storage, retention.>

## 4. Runtime view
<Key flows; sequence diagrams for non-obvious ones.>

## 5. Deployment
<Environments, infrastructure, configuration.>

## 6. Cross-cutting concerns
- **Security:**
- **Logging & observability:**
- **Error handling:**

## 7. Quality attributes
| NFR | How it is met |
|-----|---------------|
| | |

## 8. Decisions
See `docs/adr/`.
