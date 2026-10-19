# Running the process day to day

You should not have to drive the process step by step. In daily use you do two
things: **say what you want next**, and **make gate decisions**. An
orchestrating agent does everything in between.

## How it works
1. **The repository is the state.** `python .process/status.py` reads the gate records, increment briefs, reviews, `CHANGELOG.md`, and git branches and tags, and prints the current phase and the next step. Because nothing depends on an agent's memory, any session, today or next month, resumes exactly where things stand.
2. **The orchestrator runs the loop.** The `dev-process-orchestrator` skill asks `status.py` for the next step, carries it out with the right skill (or a subagent), and asks again. It keeps going until the next step belongs to the Owner.
3. **It stops only at gates**, with a short decision brief: what is being decided, the evidence, the reviewer's verdict, its recommendation, and how to reply.
4. **You reply in plain words.** The orchestrator records your decision verbatim (`status.py record-gate`) and carries on.

## A typical conversation

| You say | The orchestrator does | Then stops at |
|---|---|---|
| "Continue" (in a new project) | P0: the brief, `AGENTS.md`, standards, a reviewer summary | **G0**: "Go?" |
| "Approved. First I want users to export their data as CSV." | Creates INC-001 and shapes it: requirements, spikes, brief, size check, review | **G1**: "Approve the shape of INC-001?" |
| "Approved." | Records G1, then builds every slice (tests, code, docs, PRs) and records the demo | **G2**: "PR #12 is ready, here is the demo. Merge when happy." |
| *(you merge)* "Continue." | Sees the merge, marks the increment done, prepares the release and its review | **G3**: "Release 0.2.0?" |
| "Ship it." | Records G3, tags v0.2.0, deploys per the runbook, drafts the Learnings | "What outcome do you want next?" |

"Continue", "what's next" or `/dev-process-orchestrator` (in tools that expose
skills as commands) picks up from wherever the project is.

## Subagents
In tools with subagents (Claude Code: `scaffold.py --adapter claude` creates
`.claude/agents/dev-process-<role>.md`), the orchestrator delegates each step to
the matching role subagent. This keeps the main conversation small during long
builds, and runs every review in a fresh context, as the reviewer rules require.

## What still needs you
- **Starting a session.** Open your agent tool and say "continue". Unattended triggers (schedules, issue labels) may come later.
- **Gate decisions and merges.** By design. The orchestrator never approves, merges or releases on its own.
- **Unblocking.** When a step is blocked (a conflicting requirement, a guardrail refusal it cannot fix properly), the orchestrator stops and asks.

## Checking the state yourself
```bash
python .process/status.py            # human-readable
python .process/status.py --json     # for tools
```
