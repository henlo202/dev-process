---
id: reviewer-summary
---
# Reviewer summary

**What it is:** A structured critique written by the Reviewer agent before
every human gate. It is the main safeguard against rubber-stamping in a solo
process ([PDR-0002](../governance/decisions/PDR-0002-solo-owner-with-reviewer-agent.md)).

## Where
- G2: a comment on the pull request.
- Other gates: embedded in, or linked from, the gate record.

## Rules for the Reviewer agent
- Review the artefact against its inputs (e.g. the design against the requirements), not in isolation.
- Rank each finding by severity: blocker, major, minor, nit.
- Say explicitly what you did **not** check.
- Do not soften findings. The Owner decides what to accept.
- If possible, run the review in a fresh agent session, separate from the session that produced the work.
