---
artefact: increment
increment: INC-001
status: draft
requirements: []
tier: {{tier}}
budget: M                # S | M | L or a number of agent steps; set while shaping, approved at G1
spent: 0                 # agent steps used; updated by .process/status.py log-step
escalations: []
owner: Planner agent
updated: {{date}}
---
# INC-001: <increment title>

## Outcome
<One or two sentences: what the Owner will see working when this is done.>

## Requirements in scope
<!-- IDs only; the requirements live in docs/requirements/. Keep within the size limit. -->
-

## Design notes
<A few bullet points on how it will be built. Link ADRs for hard-to-reverse decisions.>

## Spikes
<!-- Link spike reports, or write "none". -->
- none

## Task slices
<!-- Vertical slices, each about half a day of agent work. -->
- [ ] S1: <slice description> (REQ-)

## Demo
<!-- Filled in at P3: link or paste the evidence that each acceptance criterion works. -->

## Learnings
<!-- Filled in at P5: two or three lines. Route actions to the next increment, AGENTS.md or a process change.
     End with one resource line, e.g. "Resource use: 14 of 20 steps (M), 1 escalation (S3 to deep), most cost: flaky test." -->
