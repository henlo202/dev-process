---
id: G2
---
# G2 · Merge approved

## Purpose
The Owner's decision to accept a change into the main branch. Applies to every
pull request in every tier. For the PR that completes an increment, the
decision rests first on the **demo**: you see the outcome working.

## Checklist (copy into every PR description)
- [ ] **Demo:** I watched the demo, and it shows every acceptance criterion in scope working. (This applies to the final PR of an increment; T1 changes show the before and after.)
- [ ] CI is green: tests, lint, static analysis, security scans.
- [ ] Every conformance warning is fixed or covered by a waiver.
- [ ] Every requirement touched by this change has a passing test (see the traceability report).
- [ ] I read the reviewer summary, and every finding is fixed or answered.
- [ ] I skimmed the diff myself, with particular attention to tests that were changed or deleted.
- [ ] No spike code was merged.
- [ ] Docs are updated: user, technical, runbook, changelog.
- [ ] The tier is correct for this change.

## Decisions
- **Merge:** the merged PR with its ticked checklist is the gate record.
- **Request changes:** comment in the PR. The agents continue in P2.
- **Close:** abandon the change with a reason.

## Record
The merged pull request (description, checklist, demo link and review comments)
is the record. No separate file is needed. If you work without pull requests,
create `docs/gates/G2-<yyyy-mm-dd>-<task>.md` instead.

> **Note for solo work:** Many platforms do not let you approve your own pull
> request. Use the ticked checklist and the merge itself as the approval. Do not
> work around this by making an agent "approve" the PR.
