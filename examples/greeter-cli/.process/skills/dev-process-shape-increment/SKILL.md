---
name: dev-process-shape-increment
description: Shape the next increment end to end, covering outcome, requirements, design notes, spikes and the increment brief, ready for the Owner's G1 decision. Use when the Owner says what they want next ("next I want users to export CSV"), at the start of every T2/T3 increment.
---
# Shape an increment (dev-process P1)

Combines the analyst, architect and planner roles for one increment. The result
is a reviewed increment brief, ready for gate G1.

## Steps
1. **Outcome:** restate the Owner's goal as one demonstrable outcome. Read the previous increment's Learnings.
2. **Requirements:** add or update only the requirements this outcome needs (skill `dev-process-analyst`).
3. **Open questions:** settle each one that a document cannot settle with a spike (skill `dev-process-spike`), or record it as an assumption.
4. **Design notes:** a few bullet points, plus an ADR if a decision is hard to reverse (skill `dev-process-architect`).
5. **Brief:** write `docs/increments/INC-NNN-<slug>.md` from `increment.md` in this skill's folder: frontmatter with `increment` and `requirements`, outcome, slices, demo plan.
6. **Size check:** run `python .process/check.py`, and split the increment if it reports `increment-too-large`.
7. **Mark it ready:** set the increment's `status` to `in-review`.
8. **Review:** produce `docs/reviews/G1-<INC>.md` (skill `dev-process-reviewer`, in a fresh session or subagent).
9. **Hand over:** tell the Owner the increment is ready for G1, with the brief, the summary and the spike results. Do not approve it yourself.
