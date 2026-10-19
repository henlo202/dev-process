# Changelog

All notable changes to dev-process are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the process uses
[Semantic Versioning](https://semver.org/) as described in
[governance/versioning.md](governance/versioning.md).

## [Unreleased]
### Changed
- CI: publishing to GitHub Pages is now optional (repository variable `PAGES_ENABLED`). The built site is always attached to each run as the `site` artifact.

## [0.1.0] - 2026-10-19
### Added
- Initial MVP: phases P0–P7, gates G0–G5, 20 artefact definitions with templates, risk tiers T1–T3.
- Roles (one human Owner plus seven agent roles) and tool-neutral agent playbooks.
- Guides: requirements, QA & testing, documentation, security, Definition of Ready/Done, agent autonomy, compliance (future), glossary.
- Governance: ownership, change process, versioning, adoption, waivers, review cadence, PDR-0001 to PDR-0005.
- Tooling: `scaffold.py`, a warn-only `check.py` with traceability, `validate.py`, and CI snippets.
- A generated HTML site.
- Worked example: `examples/greeter-cli`.

### Upgrade
- First release. Adopt with `tooling/scaffold.py`.
