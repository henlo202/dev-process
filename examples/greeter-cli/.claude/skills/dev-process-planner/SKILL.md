---
name: dev-process-planner
description: Write an increment brief, with a single outcome, the requirement IDs in scope, vertical task slices S1..Sn and a demo plan, keeping within the increment size limit. Use when shaping a new increment (dev-process P1), splitting work, or when an increment looks too big.
---
# Planner (dev-process)

- **Phases:** P0 (rough order of the first increments), P1 Shape
- **Reads:** the brief, requirements in scope, design notes, spike reports, the previous increment's Learnings
- **Writes:** `docs/increments/INC-NNN-<slug>.md` (template: `increment.md` in this skill's folder, or `.process/templates/increment.md`)

## Steps
1. State the single outcome in one or two sentences the Owner can check in a demo.
2. List the requirement IDs in scope in the frontmatter `requirements:` list.
3. Slice the work vertically into tasks `S1, S2…`, each about half a day of agent work and naming its requirement IDs.
4. Put the riskiest slice first. In INC-001, build a walking skeleton.
5. Check the size limit in `.process/config.yaml` (`increment_limits`). If it is exceeded, propose a split.
6. Describe how the outcome will be demonstrated. The Demo section starts as a plan and is filled with evidence in P3.
7. Check every slice against the Definition of Ready: requirement IDs named, small, dependencies clear, no open questions.
8. Set the frontmatter `tier` and propose a `budget` (S, M or L, sized in agent steps in `economy.budgets`): roughly shaping and review, plus one step per slice, plus the demo, plus slack for retries. The Owner approves it at G1.
