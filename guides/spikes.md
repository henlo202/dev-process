# Spikes: build to learn

A **spike** is a time-boxed, throwaway experiment that answers one question by
building, rather than by writing. With agents, a prototype often costs less
than a careful written argument, and it gives a far more reliable answer.

## When to spike
- Two design options are being debated. Build both and compare them.
- A library, API or service might not do what we need. Try it.
- Performance or feasibility is uncertain. Measure it.
- The Owner can't judge a UX or behaviour from a description. Show a rough version.
- A requirement is unclear. A prototype makes the question concrete.

## Rules
1. **One question, one time-box.** Write both down before starting (for example, "Can SQLite handle 1M rows with sub-100 ms queries? 2 hours.").
2. **A separate branch:** `spike/<slug>`. Spike code is **never merged**. Production code is rebuilt test-first, using what the spike taught.
3. **Record the result** in a [spike report](../artefacts/spike-report.md), including negative results.
4. **Feed the decision forward:** into the increment brief, an ADR, or a requirement.
5. **Stop at the time-box.** If the question is still open, report what was learned and let the Owner decide whether to extend it.

## Where spikes happen
- In **P0**, to test the riskiest assumption behind the whole initiative.
- In **P1 · Shape**, to settle open questions before G1. This is the main use.
- In **P2 · Build**, when a new unknown appears. Spike briefly, and go back to the Owner if the scope changes.

## Autonomy
Spikes fall under the project's [autonomy level](agent-autonomy.md). At A2 and
above, agents may create spike branches and run spikes without asking, as long
as the spike stays inside its time-box and touches no shared infrastructure,
real data or secrets.
