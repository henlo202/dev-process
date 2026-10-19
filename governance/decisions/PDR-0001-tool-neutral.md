# PDR-0001: The process is tool neutral

- **Status:** accepted
- **Date:** 2026-10-19

## Context
AI agent tooling changes fast. Binding the process to one product risks having
to rewrite it, and excludes using different agents for different roles (for example, a
different model as Reviewer).

## Options
1. Build around one tool's native features (skills, rules, hooks).
2. Keep the core neutral (Markdown, YAML, `AGENTS.md`, plain scripts), with optional thin adapters.

## Decision
Option 2. The core uses only Markdown, YAML, JSON Schema and dependency-light
Python. `AGENTS.md` is the agent entry point. Tool-specific integrations live in
`adapters/` (to be added) and only point to the neutral content.

## Consequences
- The process works with any agent that can read files and run commands.
- Some tool conveniences (auto-loaded skills, hooks) need an adapter to be used.
