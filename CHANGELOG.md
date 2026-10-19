# Changelog

All notable changes to dev-process are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the process uses
[Semantic Versioning](https://semver.org/) as described in
[governance/versioning.md](governance/versioning.md).

## [Unreleased]

## [0.2.0] - 2026-10-19
The process is now a **loop of small increments** instead of a sequence of phases ([PDR-0006](governance/decisions/PDR-0006-increment-loop.md)).

### Changed
- Phases: P0 Initiate (once), then the loop P1 Shape → P2 Build → P3 Verify → P4 Release → P5 Learn. The former Requirements, Design and Plan phases are merged into **P1 Shape**.
- Gates: G0 Go/No-go, **G1 Shape approved** (with a design-scrutiny section and cooling-off for T3), G2 Merge approved, G3 Release approved.
- G2 Merge is outcome-based: the Owner watches the increment's **demo** first.
- Requirements are detailed only for the next increment. The architecture and test strategy start as a sketch in P0 and grow.
- Roles, playbooks, guides, templates and the PR checklist are updated to match.
- CI: publishing to GitHub Pages is now optional (repository variable `PAGES_ENABLED`). The built site is always attached to each run as the `site` artifact.

### Added
- Artefacts: **increment brief** (`docs/increments/`), **spike report** (`docs/spikes/`) and **increment demo**.
- Guides: [Increments & the loop](guides/increments.md) (including the size limit) and [Spikes](guides/spikes.md).
- Checker rules: `increment-too-large`, `demo-missing`, `duplicate-increment`, and `gate-record-missing:G1:<INC>` for each increment.
- The `increment_limits` setting in `.process/config.yaml` (defaults: 5 requirements, 8 slices).
- Statuses `in-progress` and `done` in artefact frontmatter.

### Removed
- The task plan artefact (`docs/plan.md`), replaced by increment briefs.
- The separate Design and Plan gates.

### Upgrade (from 0.1.0)
1. Run `python <dev-process>/tooling/scaffold.py <project> --upgrade`.
2. Rename any gate records: G4 → G2, G5 → G3. Former G2/G3 (Design/Plan) records stay as history.
3. Move any open work from `docs/plan.md` into an increment brief (`docs/increments/INC-001-*.md`), then delete `docs/plan.md`.
4. Add `increment: INC-nnn` to the frontmatter of G1 gate records.
5. Add `increment_limits` to `.process/config.yaml` if you want limits other than the defaults.
6. Update `AGENTS.md` from `.process/templates/AGENTS.md` (Process section).

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
