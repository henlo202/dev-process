---
id: spike-report
---
# Spike report

**What it is:** A short record of a time-boxed experiment: the question, what
was built or measured, what was found, and the decision it supports. The spike
code itself is thrown away; the report keeps what was learned.

**Where:** `docs/spikes/NNNN-<slug>.md`. Spike code lives on a `spike/<slug>` branch that is **never merged**.

## Rules
- One question per spike, with the time-box stated up front.
- Record negative results too. They stop the same idea from being tried again.
- Link the report from the increment brief, and from any ADR that relied on it.

See the [spikes guide](../guides/spikes.md).
