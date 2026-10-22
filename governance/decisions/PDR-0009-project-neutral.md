# PDR-0009: The process is project neutral

- **Status:** accepted
- **Date:** 2026-10-22

## Context
Process changes are often found while working on a project that uses the
process: a checker bug shows up on that project's documents, and an agent in
that project's session fixes it here. In 0.5.0 such a fix copied the project's
real commands into code comments, a test fixture and the changelog. Nothing
caught it: the reviewer had no rule to check against, and the repository is
public, so project details leaked.

## Options
1. Rely on the Owner noticing in review.
2. A written rule only (governance, `AGENTS.md`, review step).
3. A written rule plus a mechanical check against a private list of project terms.

## Decision
Option 3.
- **Rule.** Nothing in this repository may name or describe a consuming
  project: no project names, domain terms, commands, file paths, requirement
  IDs, people or data. Examples are invented and generic (`mytool`,
  `greeter-cli`). When a change is found in a project, the proposal describes
  the problem in neutral terms and rewrites every example before it lands here.
- **Where it is stated:** [ownership principles](../ownership.md), the
  [change process](../change-process.md) (draft and review steps), this
  repository's `AGENTS.md`, and the project `AGENTS.md` template, so agents in a
  consuming project see the rule before proposing a process change.
- **Check.** `tooling/validate.py` fails if any term from a private list
  appears in the repository. The list is never committed: it is read from
  `.private-terms` (git-ignored, one term per line) and from the
  `DEV_PROCESS_PRIVATE_TERMS` environment variable (comma-separated), so it can
  also be supplied to CI as a secret.

## Consequences
- Agents and the reviewer have an explicit rule; a leak becomes a review finding.
- The check only knows the terms the Owner lists, so the review step stays necessary.
- Text already in git history is not removed by this decision.
