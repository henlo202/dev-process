---
name: dev-process-demo
description: Record a demo showing an increment's outcome working against the real build, one acceptance criterion at a time, and link it from the increment brief and PR. Use on the slice that completes an increment (dev-process P3), or when the Owner asks to see something working.
---
# Record a demo (dev-process P3)

## Steps
1. Build and run the real software. No mocks and no spike code.
2. For each acceptance criterion in the increment's scope, in order, show it working: a terminal transcript, screenshots, or a short recording.
3. Show at least one failure path (invalid input, a missing permission).
4. List the exact commands or steps, so the Owner can reproduce the demo.
5. Paste or link the evidence in the increment brief's **Demo** section and in the PR description. Set the increment status to `done` when the PR merges.

A demo complements tests and never replaces them: every acceptance criterion still needs an automated test that references its requirement ID.
