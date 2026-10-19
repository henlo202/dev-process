---
id: P4
---
# P4 · Release

## Purpose
Ship merged increments to users safely, with release notes and a plan for when
things go wrong.

## When
Whenever you release. Release often: ideally after every increment, but
several increments can share one release.

## Steps

| # | Who | Step |
|---|-----|------|
| 1 | Documenter agent | Move the Unreleased entries in `CHANGELOG.md` under a new version, and draft release notes written for users. |
| 2 | Documenter agent | Check that the [runbook](../artefacts/runbook.md) covers deploy, rollback, configuration and any new alerts. |
| 3 | Documenter agent | Check that the [user documentation](../artefacts/user-docs.md) matches the released behaviour. |
| 4 | Reviewer agent | Check release readiness: version number, migrations, rollback path, known issues. Produce a [reviewer summary](../artefacts/reviewer-summary.md). |
| 5 | Owner | Hold gate [G3 · Release approved](../gates/G3-release.md), then tag and deploy (or tell the agent to do so). |

## Exit criteria
- A version tag exists. The changelog and release notes are published.
- The rollback procedure is documented, and was tested for T3 releases.
