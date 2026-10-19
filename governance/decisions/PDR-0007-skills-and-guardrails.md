# PDR-0007: Agent instructions as skills; rules enforced by guardrails

- **Status:** accepted
- **Date:** 2026-10-19

## Context
Agent instructions were plain Markdown "playbooks" that an agent only used if
pointed at them explicitly. The Agent Skills format (a folder with a `SKILL.md`
whose frontmatter holds a `name` and a "use when" `description`) lets agent
tools discover the right instructions automatically, and it is still plain
Markdown for every other tool.

Separately, all agent rules (coding standard, feature branches, no merging)
were advisory. Agents usually follow instructions, but they can skip, misread
or lose them, and nothing stopped a push to `main` or a bypassed hook.

## Options
1. Keep plain playbooks; rely on instructions and review.
2. Skills only: better discovery, but still advisory.
3. Skills for guidance **plus** guardrails for hard enforcement, layered: always-on rules (`AGENTS.md`), skills, then tooling.

## Decision
Option 3.
- Playbooks become **skills** in `agents/skills/<name>/SKILL.md`: seven role skills and four task skills, declared in `process.yaml` with their bundled templates. The format stays tool neutral; installing skills where a specific tool discovers them is an **adapter** (`scaffold.py --adapter claude`).
- A new initiative artefact, **engineering standards** (`docs/standards.md`), lists each rule *and where it is enforced*.
- **Guardrails** (`.process/guardrails/`): tool-neutral git hooks and a CI script backed by one `guard.py`, configured in `.process/config.yaml`. Hard blocking is opt-in per project (`mode: block`); new projects start in `warn`.
- Agent-tool adapters may add pre-execution hooks that refuse bypasses, merges and blocked commands, using the same rules.

PDR-0003 still applies: the **conformance checker** never blocks. Guardrails
are project tooling that the Owner chooses to make blocking.

## Consequences
- Agents get the right instructions without being told where to look (in tools that support skills).
- Rules the Owner cares most about become impossible to break by accident once `mode: block` is set and hooks are installed.
- Hooks must be installed in every clone (`git config core.hooksPath …`). `AGENTS.md` lists this as a setup step, and the checker reports when it is missing.
- Local hooks can be bypassed by a determined actor. Server-side branch protection, where the hosting plan allows it, is the strongest layer.
