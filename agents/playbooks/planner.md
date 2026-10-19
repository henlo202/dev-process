# Playbook: Planner agent

**Phases:** P0 (rough ordering of the first increments), P1 · Shape (increment brief)
**Reads:** brief, requirements in scope, design notes, spike reports, learnings from the previous increment
**Writes:** `docs/increments/INC-NNN-<slug>.md` (template: `.process/templates/increment.md`)

## Steps
1. State the increment's single outcome in one or two sentences the Owner can check in a demo.
2. List the requirement IDs in scope in the frontmatter `requirements:` list.
3. Slice the work vertically into tasks `S1, S2…`, each about half a day of agent work, and each naming its requirement IDs.
4. Put the riskiest slice first. In INC-001, build a walking skeleton.
5. Check the [size limit](../../guides/increments.md#size-limit). If it is exceeded, propose a split instead of a bigger increment.
6. Describe how the outcome will be demonstrated (the Demo section starts as a plan and is filled with evidence at P3).
7. Check every slice against the Definition of Ready.
