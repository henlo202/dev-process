---
id: runbook
---
# Runbook

**What it is:** The operational documentation: how to deploy, configure,
monitor, troubleshoot and roll back the system. Written so that a future you
(or an agent) can act on it at 3 a.m.

## Contents
1. Service overview and dependencies
2. Deploy procedure (exact commands)
3. Rollback procedure (exact commands, tested for T3)
4. Configuration and secrets: where they live, never the values
5. Monitoring: dashboards, alerts, SLOs, and what each alert means
6. Common problems and fixes
7. Backup and restore
8. Post-incident notes

For libraries or tools with no runtime, most sections reduce to "release
procedure" and "how to yank a bad version". Record a waiver for the rest.
