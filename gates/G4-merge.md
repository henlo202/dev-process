---
id: G4
---
# G4 · Merge approved

## Purpose
The Owner's decision to accept a change into the main branch. Applies to every
pull request in every tier.

## Checklist (copy into every PR description)
- [ ] CI is green: tests, lint, static analysis, security scans.
- [ ] Every conformance warning is fixed or covered by a waiver.
- [ ] Every requirement touched by this change has a passing test (see the traceability report).
- [ ] I read the reviewer summary, and every finding is fixed or answered.
- [ ] I skimmed the diff myself, with particular attention to tests that were changed or deleted.
- [ ] Docs are updated: user, technical, runbook, changelog.
- [ ] The tier is correct for this change.

## Decisions
- **Merge:** the merged PR with its ticked checklist is the gate record.
- **Request changes:** comment in the PR. The agents continue in P4.
- **Close:** abandon the change with a reason.

## Record
The merged pull request (description, checklist and review comments) is the
record. No separate file is needed. If you work without pull requests, create
`docs/gates/G4-<yyyy-mm-dd>-<task>.md` instead.

> **Note for solo work:** Many platforms do not let you approve your own pull
> request. Use the ticked checklist and the merge itself as the approval. Do not
> work around this by making an agent "approve" the PR.
