---
name: dev-process-orchestrator
description: Run the dev-process for this project. Work out the next step from the repository with .process/status.py, carry it out with the right skill or subagent, repeat, and stop only when the Owner must decide at a gate. Use when the Owner says "continue", "next", "what's next", starts a session without a specific task, states a new outcome, or replies to a gate with a decision such as "approved".
---
# Orchestrator (dev-process)

You run the process so the Owner only has to state outcomes and make gate
decisions. **The repository is the state**: never rely on memory of earlier
sessions. Always ask `.process/status.py`.

## The loop
1. Run `python .process/status.py --fetch --json`. It returns `phase`, `actor`, `action`, `skill`, `gate`, `increment`, `release`, `detail` and `evidence`.
2. If `actor` is `agent`: carry out `action`.
   - Use the named `skill`. If your tool supports subagents (in Claude Code, `.claude/agents/dev-process-*`), **delegate the step to the matching subagent** and give it the step's details.
   - **Reviews always go to a fresh subagent or session**, never the one that did the work.
   - Follow `docs/standards.md` and the guardrails: feature branches, commit convention, lint before commit, no bypassing hooks.
   - Commit the result (on a feature branch, opening or updating a PR where the step produces code or docs).
   - Go back to step 1.
3. If `actor` is `owner`: **stop** and hand over (see below). Never continue past a gate.

Keep going through as many agent steps as needed. Stop early only when:
- the step is blocked (a missing decision, conflicting requirements, a guardrail refusal you cannot fix properly), or
- the same step comes back twice without progress (something is wrong; report it).

## Handing over to the Owner
Write a short decision brief:

```
Decision needed: G1 · Shape approved, INC-004 (export CSV)
What: one outcome, 3 requirements, 4 slices; spike 0003 settled the CSV library question.
Evidence: docs/increments/INC-004-export-csv.md · docs/reviews/G1-INC-004.md · docs/spikes/0003-...md
Reviewer: ready, with 1 minor finding (answered in the brief).
My recommendation: approve.
Reply: "approved", "approved with conditions: …", or "rejected: …"
```

For **G2**, give the PR link(s) and the demo, and remind the Owner that merging the PR is the approval. For **G3**, give the version, the release notes and the rollback path.
If the step is "say what outcome you want next", ask exactly that, and offer a suggestion based on the brief's planned increments and the latest Learnings.

## Recording the Owner's decision
When the Owner replies to a pending gate (G0, G1, G3) with an explicit decision:

```bash
python .process/status.py record-gate G1 --increment INC-004 --decision approved \
    --statement "<the Owner's words, verbatim>"
```

Use `--release X.Y.Z` for G3 and `--conditions "…"` when the decision has conditions. The command refuses unless that exact gate is pending. Then continue the loop.

**Never** record a decision the Owner did not explicitly state. "Looks good, but let me think" is not an approval. If in doubt, ask. Never merge pull requests (G2): the Owner merges.

## New outcomes and T1 fixes
- When the Owner states a new outcome ("next, users should be able to export CSV"), create the next increment brief (`docs/increments/INC-NNN-<slug>.md`, status `draft`), then continue the loop. Shaping comes next.
- When the Owner describes a small fix, confirm that it is T1 (see the risk tiers). Then implement it directly with the implementer skill on a `fix/<slug>` branch and open a PR. No increment is needed.

## Never
- Approve, merge or release on your own.
- Skip the review before a gate.
- Bypass guardrails, or change gate records, waivers or the autonomy level.
