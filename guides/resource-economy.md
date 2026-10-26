# Resource economy

AI agents cost money and quota. This guide sets rules so that each step uses
**the smallest model that does the job well**, increments have a **budget**,
agents **stop instead of looping**, and context stays **small**. It is tool- and
model-neutral: the process names abstract model classes, and each project maps
them to real models ([PDR-0009](../governance/decisions/PDR-0009-resource-economy.md)).

Waste tends to come from four sources, in roughly this order:
1. The main session runs on the most capable model all the time.
2. Context grows: long sessions, whole files pasted in, subagents returning transcripts.
3. Agents retry failing steps without limit.
4. The wrong model class for the task (too big, or too small and then redone).

## 1. Model classes

| Class | Use for | Effort |
|-------|---------|--------|
| `deep` | Design choices, trade-offs, judging risk, hard debugging, T3 reviews | high |
| `standard` | Code, tests, requirements and reviews against a clear brief | medium |
| `fast` | Mechanical work: doc edits, changelogs, formatting, summaries, running scripts | low |

Every agent role and task skill has a **default class**, and some have an
override for T1 or T3 work. Both are defined in `process.yaml` and shown on each
skill's page. In short: the architect works on `deep`; the analyst and reviewer
move to `deep` at T3; the implementer and tester drop to `fast` at T1; the
documenter works on `fast`; the rest work on `standard`.

The **orchestrator** is `standard`. It runs in your main session, which most tools
cannot switch per step, and a `fast` model is unreliable at following the whole
loop and writing gate briefs. So the main session should run on your `standard`
model, and delegate `deep` work to subagents.

### Mapping classes to models
In `.process/config.yaml`:
```yaml
economy:
  models:
    deep:     {model: opus,   effort: high}
    standard: {model: sonnet, effort: medium}
    fast:     {model: haiku,  effort: low}
```
Use whatever names your tool accepts. `scaffold.py --adapter claude` fills these
in for Claude Code. When a class is not mapped, the conformance checker warns
(`models-not-configured`).

### Which class a step uses
`python .process/status.py` names it for every agent step (`model_class`,
`model` and `effort` in `--json`). The class comes from the step's skill (or
its role), adjusted for the increment's `tier`, or the project tier when the
increment has none. If your tool lets you choose the model when delegating, pass
`model`; otherwise the subagent's own setting applies.

### Escalation
- A step starts at its class. After `economy.max_attempts` failed attempts (default 2), the agent may move **one class up**, and records why: `status.py log-step INC-004 --escalated "S3 to deep: race in the exporter"`.
- Going above `deep`, or escalating again on the same step, means stopping and asking the Owner.
- The other way round: when work turns out to be mechanical, use a lower class.

## 2. Budgets and stop-loss
- Each increment has a **budget**: `budget: S | M | L` (or a number) in its frontmatter. It is set while shaping and approved at G1 with the rest of the shape.
- The budget is counted in **agent steps**. One agent step is one delegated unit of work, such as shaping, a review, a slice or a demo. A failed attempt counts as a step. Default sizes are S = 10, M = 20 and L = 35 steps (`economy.budgets`).
- The orchestrator counts each step with `status.py log-step <INC>`, committed with the step's result.
- **When the budget is used up**, `status.py` makes the next step the Owner's: extend the budget, cut scope or stop. Only the Owner extends a budget: `status.py set-budget INC-004 L --statement "<the Owner's words>"`.
- **Stop-loss within a step:** when a step fails `max_attempts` times even after escalating, the agent stops and writes a short "stuck" brief: what was tried, what failed, and its best guess. It does not try again.
- Spikes are budgeted in steps too, and end with a report even when the question is still open.

## 3. Context economy
- **Scripts before models.** If `status.py`, `check.py`, the guardrails, a linter or the test runner can answer something, do not ask a model.
- **Compact handoffs.** The orchestrator gives a subagent a short step brief: the goal, the files to read, and when the step is done. It does not pass on its own history. Subagents reply in at most about 15 lines, plus links to what they changed, never transcripts or file contents.
- **Gates are where sessions end.** Start a fresh session (or compact) after every gate decision. The repository is the state, so nothing is lost.
- **Keep always-loaded context small.** `AGENTS.md` stays under `economy.agents_md_max_lines` (default 150; the checker warns with `agents-context-too-long`). Details go into linked docs and skills, which load only when needed.
- **Read on demand.** Search instead of reading whole large files. Do not re-read files that have not changed. Trim long command output (for example, only the failing tests).
- **Proportional test runs.** Run the affected tests while building a slice, and the full suite before the demo and PR.
- **Edit, don't regenerate.** Change docs and code with targeted edits, not by rewriting whole files.
- **Batch questions.** Collect open questions and bring them to the Owner at the next stop, rather than stopping for each one.
- **Proportional reviews.** T1 changes get no separate review step (CI and the Owner's merge are enough); T2 gets one `standard` review; T3 gets a `deep` review, preferably by a different model than the author.

## 4. Measure and learn
- Each increment's frontmatter keeps `spent` and `escalations`.
- At P5 the Learnings end with one resource line, for example: "Resource use: 14 of 20 steps (M), 1 escalation (S3 to deep), most cost: flaky test."
- When the same cost keeps appearing, fix the cause: a better `AGENTS.md`, a sharper skill, a test helper, or a process change.

## Conformance checks
| Rule | Meaning |
|------|---------|
| `economy-not-configured` | No `economy` section in `.process/config.yaml` |
| `models-not-configured` | A model class is not mapped to a model |
| `budget-missing:<INC>` | An increment being shaped or built has no budget (T2/T3) |
| `budget-invalid:<INC>` | The budget is not a known size or a number |
| `budget-exceeded:<INC>` | `spent` is over the budget |
| `agents-context-too-long` | `AGENTS.md` is over its line limit |

Like every check, these warn and never block ([PDR-0003](../governance/decisions/PDR-0003-warn-only-conformance.md)).
