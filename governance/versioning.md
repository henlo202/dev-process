# Versioning

The process uses [Semantic Versioning](https://semver.org). The current version is
`process.version` in `process.yaml`, and each release is tagged `vX.Y.Z`.

| Bump | When | Example |
|------|------|---------|
| **Major** | A project that conformed may no longer conform | New required artefact, new gate, stricter tier rules, first compliance profile |
| **Minor** | New guidance or optional capabilities; existing projects still conform | New guide, new optional template, new checker warning type |
| **Patch** | Wording, typos, clarifications, bug fixes in tooling | Fixing a broken link |

## Pre-1.0
Versions `0.x` are pre-pilot. Breaking changes may happen in minor bumps. The
process becomes `1.0.0` after the first full pilot initiative and its retrospective.

## Pinning
Every project pins a version in `.process/config.yaml`, and keeps a snapshot in
`.process/process.yaml`. A process release never changes a project silently.
See [adoption](adoption.md).

## Upgrade notes
Every major release (and every minor release before 1.0) has an "Upgrade" section in
`CHANGELOG.md`, listing what projects must change.
