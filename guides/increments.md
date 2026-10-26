# Increments & the loop

dev-process is a **loop**, not a sequence. After a one-off setup (P0), all work
is delivered in small increments, each going round the same loop:

```
P0 Initiate ─G0─►  ┌─► P1 Shape ─G1─► P2 Build ─► P3 Verify ─G2─► P4 Release ─G3─► P5 Learn ─┐
  (once)           │                                                                         │
                   └──────────────────────── next increment ◄──────────────────────────────────┘
```

T1 changes skip shaping and enter at P2.

## Why a loop
With AI agents, writing code is cheap and fast, while being wrong is still
expensive. The cheapest way to find out whether something is right is to build
a small piece of it and look at it. So:

- **Specify only the next increment.** The backlog beyond it stays rough.
- **Prefer evidence over documents.** Spikes answer questions, and demos prove outcomes (see [spikes](spikes.md) and the [demo](../artefacts/demo.md)).
- **Let documents grow.** Requirements, architecture and the test strategy are living documents, updated increment by increment and never frozen up front.
- **Learn every time round.** Each loop ends with a few lines of learnings that shape the next increment.

## What an increment is
One **demonstrable outcome**, small enough to shape, build, verify and release
in a few days. It is described by an [increment brief](../artefacts/increment.md)
(`docs/increments/INC-NNN-<slug>.md`).

Good increments are **vertical**: they cut through every layer needed for a user-visible result.

| Instead of… | Try… |
|---|---|
| "Build the database layer" | "A user can save one record and see it in the list" |
| "Design the full API" | "The export endpoint returns one CSV for the signed-in user" |
| "Set up infrastructure" | "A hello-world version is deployed and monitored" (a walking skeleton) |

## Size limit
An increment should stay within **all** of these:

| Limit | Default | Checked by |
|---|---|---|
| Requirements in scope | ≤ 5 | Conformance checker (`increment_limits.max_requirements`) |
| Task slices | ≤ 8, each about half a day of agent work | Conformance checker (`increment_limits.max_slices`) |
| Elapsed time from G1 to G2 | a few days | The Owner, at G2 |
| Outcomes | exactly one | The Owner, at G1 |

When an increment exceeds the limit, the checker **warns**: split it. If the
overrun is deliberate, accept it at G1 and add a waiver. The limits can be
tuned per project in `.process/config.yaml`.

Each increment also has an effort **budget** in agent steps (`budget: S | M | L`),
approved at G1. When it is used up, the orchestrator stops and asks the Owner.
See [resource economy](resource-economy.md#2-budgets-and-stop-loss).

## The first increments
- **INC-001** is usually a *walking skeleton*: the thinnest end-to-end slice that builds, tests, deploys and can be demonstrated. It proves the toolchain before any feature work.
- Shape the riskiest increment early. Learning that something is impossible is cheapest in week one.
