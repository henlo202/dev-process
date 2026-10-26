# Changelog

All notable changes to dev-process are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the process uses
[Semantic Versioning](https://semver.org/) as described in
[governance/versioning.md](governance/versioning.md).

## [Unreleased]

## [0.6.0] - 2026-10-26
**Resource economy** ([PDR-0010](governance/decisions/PDR-0010-resource-economy.md)): each step runs on the smallest suitable model, increments have a budget, agents stop instead of looping, and context stays small. The process stays tool- and model-neutral.

### Added
- **Model classes** `deep`, `standard` and `fast` in `process.yaml` (`model_classes`). Each agent role and task skill has a default class (`model_class`), with per-tier overrides (`tier_model_class`): the architect is `deep`; the analyst and reviewer become `deep` at T3; the implementer and tester drop to `fast` at T1; the documenter is `fast`; the rest are `standard`.
- **`economy` section** in `.process/config.yaml`: `models` (class → model and effort), `budgets` (agent steps for S/M/L), `max_attempts`, `agents_md_max_lines`.
- **`status.py`** names `model_class`, `model` and `effort` for every agent step, and shows the increment's budget.
- **Budgets and stop-loss:** increment frontmatter `budget`, `spent` and `escalations`. `status.py log-step` counts steps and records escalations. When the budget is used up, the next step is the Owner's. `status.py set-budget` changes a budget on the Owner's verbatim word.
- **Conformance checks** (warn only): `economy-not-configured`, `models-not-configured`, `budget-missing`, `budget-invalid`, `budget-exceeded`, `agents-context-too-long`.
- **Claude Code adapter:** maps the classes to `opus`, `sonnet` and `haiku`, writes `model` and `effort` into each subagent from its role's class, and makes the `standard` model the main session's default in `.claude/settings.json` (an existing `model` setting is kept).
- Guide: [Resource economy](guides/resource-economy.md). Glossary entries for agent step, budget, escalation and model class.
- The site shows model classes on each skill page and on the Roles page.
- Tests for model-class resolution, budgets, `log-step` and `set-budget`.
- **Project neutrality** ([PDR-0009](governance/decisions/PDR-0009-project-neutral.md)): the process must not name or describe any project that uses it. The rule is in the ownership principles, the change process (draft and review steps), `AGENTS.md` and the project `AGENTS.md` template.
- `tooling/validate.py` fails when a term from a private list (`.private-terms`, git-ignored, or `DEV_PROCESS_PRIVATE_TERMS`) appears in the repository.

### Changed
- **G2 for T1:** the reviewer summary is now evidence for T2/T3 only. T1 changes rest on CI and the Owner's merge.
- Orchestrator skill: compact step briefs, step counting, one escalation then a "stuck" brief, batched questions, and a fresh session after each gate.
- Skills: proportional tests (implementer, tester), proportional reviews (reviewer), edit-don't-regenerate and the Learnings resource line (documenter), budget proposal (planner, shaping), spike time-boxes in agent steps.
- Subagents reply in at most 15 lines and stop after `max_attempts`.
- G1 checklist: the budget and tier fit the work. The risk tiers table gains reviews, models and budget rows.
- Templates: `AGENTS.md` gains a resource-economy bullet; the increment brief gains `tier`, `budget`, `spent`, `escalations` and a resource line in Learnings; `process-config.yaml` gains `economy`.
- Subagent descriptions keep non-ASCII characters readable.
- Code comments, a test fixture and the 0.5.0 changelog entry used commands from a consuming project as examples; they now use neutral ones (`mytool --user <name or id> list`). No behaviour change.

### Upgrade (from 0.5.0)
1. Run `python <dev-process>/tooling/scaffold.py <project> --upgrade`. It adds the `economy` section to `.process/config.yaml` (filled in for Claude Code if that adapter is installed) and regenerates subagents with their models.
2. If you do not use the Claude adapter, map `economy.models` to your tool's models.
3. Add the resource-economy bullet from `.process/templates/AGENTS.md` to your `AGENTS.md`.
4. Add `tier` and `budget` (and `spent: 0`) to increments that are not yet `done`.
5. Run your main agent session on your `standard` model (with the Claude adapter, the upgrade sets this unless `.claude/settings.json` already names a model).
6. Run `python .process/check.py` and `python .process/status.py`.

## [0.5.0] - 2026-10-19
Guardrails now work on **Windows**, and projects can use their own **requirement ID prefixes**.

### Added
- `requirement_id_prefixes` in `.process/config.yaml` (default `[REQ, NFR]`): the prefixes the checker recognises as requirement IDs, for example one per area (`[SYS, API, UI]`). Requirement headings, test references and increment `requirements:` lists all use them. An invalid value is reported as `config-invalid:requirement_id_prefixes` and the default is used.
- `.process/guardrails/find-python.sh`: shared Python discovery for every shell entry point. It tries `python3`, `python` and `py -3` by running them, and prefers one that can import PyYAML.
- `.process/adapters/claude/pre_tool_use.sh`: the Claude Code hook entry point. It blocks (exit 2) when no Python works, instead of silently allowing.
- Tests: Python discovery (broken `python3` stub, PyYAML preference, no Python at all), the Claude entry point, the settings upgrade, and requirement ID prefixes (`tooling/tests/test_check.py`).

### Fixed
- Git hooks, CI scripts and the Claude Code hook called `python3` directly. On Windows that is often the Microsoft Store alias, which does not run Python, so every commit was refused and the Claude hook never checked anything.
- When the first Python on PATH had no PyYAML, the guardrails fell back to their defaults (warn mode) even in `block` projects; a Python with PyYAML is now preferred.
- Text in inline code (for example `` `--user <name or id>` ``) was reported as an unfilled template placeholder; inline code is now skipped like fenced code, in `check.py` and `status.py`.
- The tools crashed on Windows when printing ✔, ✖ or ❌ to a non-UTF-8 console or pipe; their output is now UTF-8.

### Changed
- The Claude adapter's `settings.json` runs `sh "$CLAUDE_PROJECT_DIR/.process/adapters/claude/pre_tool_use.sh"`. `scaffold.py --upgrade` rewrites the old `python3 …/pre_tool_use.py` command in an existing `.claude/settings.json` and keeps every other hook.
- The increment `requirements` frontmatter pattern accepts any configured prefix (`^[A-Z][A-Z0-9]*-\d+$`).

### Upgrade (from 0.4.0)
1. Run `python <dev-process>/tooling/scaffold.py <project> --upgrade` (add `--adapter claude` if you use it). This refreshes the hooks, CI scripts and adapter, and updates the Claude hook command if it is the old one.
2. If your project uses requirement IDs other than `REQ-`/`NFR-`, add `requirement_id_prefixes: [..]` to `.process/config.yaml` and run `python .process/check.py`.
3. Make sure a Python 3.9+ with PyYAML is reachable as `python3`, `python` or `py -3` (`pip install pyyaml`). Otherwise the guardrails warn instead of block.

## [0.4.0] - 2026-10-19
The process now **runs itself between gates** ([PDR-0008](governance/decisions/PDR-0008-orchestration.md)). In daily use the Owner states outcomes and makes gate decisions; an orchestrator does everything in between.

### Added
- **`status.py`** (`.process/status.py`): derives the current phase and next step from the repository alone (gate records, increment status and ticked slices, `docs/reviews/`, `CHANGELOG.md`, git branches and tags). It has `--json` output for agents, and `--fetch` to see merges.
- **`status.py record-gate`**: records an Owner decision stated in conversation, verbatim (`recorded_by: agent`, `owner_statement`). It refuses unless that gate is pending. It sets the increment's status after G1.
- **Orchestrator** role and skill (`dev-process-orchestrator`): loops on `status.py`, delegates each step to the right skill or subagent, sends reviews to a fresh context, and stops only at gates with a decision brief.
- **Claude Code subagents**: `--adapter claude` now also creates `.claude/agents/dev-process-<role>.md` for each role.
- Guide: [Running the process day to day](guides/orchestration.md).
- Reviewer summaries for G0, G1 and G3 are stored in `docs/reviews/`; the template gains frontmatter.
- Gate-record frontmatter fields `release`, `recorded_by` and `owner_statement`.
- Tests: a full-loop lifecycle test of `status.py` (P0 → G0 → shape → G1 → slices → demo → merge → release → tag → learnings).

### Changed
- `AGENTS.md` template: "How work starts" points agents to the orchestrator.
- Skills: the reviewer writes to `docs/reviews/`; shaping sets `in-review`; the implementer ticks slices; the documenter tags after G3.
- New projects start with an empty Unreleased section in `CHANGELOG.md`.
- The increment template's slice placeholder is now detectable by the placeholder check.

### Upgrade (from 0.3.0)
1. Run `python <dev-process>/tooling/scaffold.py <project> --upgrade` (with `--adapter claude` if you use it, to get subagents).
2. Add the "How work starts" bullet from `.process/templates/AGENTS.md` to your `AGENTS.md`.
3. Move existing reviewer summaries for G0, G1 and G3 (if you kept any) to `docs/reviews/<gate>-<key>.md`.
4. Run `python .process/status.py` to check that it reads your project correctly, then say "continue" to your agent.

## [0.3.0] - 2026-10-19
Agent instructions are now **skills**, and rules can be **enforced** by guardrails ([PDR-0007](governance/decisions/PDR-0007-skills-and-guardrails.md)).

### Added
- **Skills** in Agent Skills format (`agents/skills/<name>/SKILL.md`): role skills for the analyst, architect, planner, implementer, tester, reviewer and documenter; task skills for shaping an increment, spikes, demos and the conformance check. Declared in `process.yaml` (`skills:`) with bundled templates, and validated by `validate.py`.
- **Engineering standards** artefact (`docs/standards.md`, required for T2/T3): each rule, with where it is enforced.
- **Guardrails** (`tooling/guardrails/` → `.process/guardrails/`): `guard.py` with `commit-msg`, `pre-commit` and `pre-push` git hooks (no commits or pushes to protected branches, branch naming, commit convention, lint command) and a CI script. Configured in the `guardrails` section of `.process/config.yaml`; `mode: warn` by default, `block` opt-in.
- **Claude Code adapter** (`adapters/claude/`, `scaffold.py --adapter claude`): `CLAUDE.md` importing `AGENTS.md`, skills in `.claude/skills/`, and a `PreToolUse` hook refusing bypasses (`--no-verify`, `core.hooksPath`, the Owner override), PR merges or approvals, pushes to protected branches and project-blocked commands.
- Guide: [Guardrails](guides/guardrails.md).
- Checker rules: `guardrails-not-configured`, `lint-not-configured`, `guardrails-warn-mode` (info), `hooks-not-installed` (info).
- Scaffolder options: `--guardrails warn|block`, `--adapter claude`, `--install-hooks`. The GitHub workflow template gains a `guardrails` job.

### Changed
- `.process/playbooks/` is replaced by `.process/skills/`.
- The `AGENTS.md` template has a setup step for hooks, a link to the standards, and the bypass ban.
- Agent autonomy: bypassing a guardrail is on the "never" list at every level.

### Upgrade (from 0.2.0)
1. Run `python <dev-process>/tooling/scaffold.py <project> --upgrade --install-hooks` (add `--adapter claude` if you use Claude Code). This replaces `.process/playbooks/` with `.process/skills/` and adds a `guardrails` section (mode `warn`) to `.process/config.yaml`.
2. Create `docs/standards.md` from `.process/templates/standards.md`.
3. Set `guardrails.lint_command`, then switch to `mode: block` when ready.
4. Update `AGENTS.md` from `.process/templates/AGENTS.md` (Setup, Process and Rules sections).
5. If you use `--github`, add the `guardrails` job from `tooling/ci/github-actions-process-check.yml` to your workflow.

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
