# PDR-0004: Markdown + YAML as the single source; HTML is generated

- **Status:** accepted
- **Date:** 2026-10-19

## Context
The process must be readable by machines (agents, CI) and navigable by humans.
Maintaining two hand-written versions guarantees drift.

## Decision
- `process.yaml` (validated by JSON Schema) holds the structure: phases, gates, artefacts, roles, tiers and their relations.
- Markdown files hold the prose.
- `site/build.py` generates a static HTML site, adding cross-links (e.g. "artefact X is produced in P2 and checked at G2").
- Dependencies are limited to PyYAML and Markdown (plus jsonschema for validation).

## Consequences
- One edit updates both audiences.
- Structural relations must be changed in `process.yaml`, not in prose.
