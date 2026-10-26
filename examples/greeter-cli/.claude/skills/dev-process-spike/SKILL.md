---
name: dev-process-spike
description: Run a time-boxed, throwaway spike to answer one open question by building instead of writing, and record a spike report. Use when two design options are being debated, when feasibility, performance or an API is uncertain, or when the Owner needs to see a rough version before deciding. Spike code is never merged.
---
# Run a spike (dev-process)

## Steps
1. Write down **one question** and a **time-box**, in hours or agent steps, before starting (e.g. "Can SQLite serve 1M rows under 100 ms? 3 agent steps.").
2. Create a `spike/<slug>` branch. Take shortcuts freely: no tests, no polish.
3. Build or measure the smallest thing that answers the question. Compare options side by side when there are several.
4. Stop at the time-box, even if the question is still open.
5. On a normal branch, write `docs/spikes/NNNN-<slug>.md` from `spike-report.md` in this skill's folder. Record findings with numbers and the commands to reproduce them, **including negative results**.
6. Link the report from the increment brief, and from any ADR it supports.

## Never
- Merge or cherry-pick spike code. Production code is rebuilt test-first.
- Use real data, secrets or shared infrastructure.
