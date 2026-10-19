---
name: dev-process-conformance-check
description: Run the dev-process conformance and traceability check, explain the findings, and fix them or propose waivers. Use before opening a pull request, before any gate, after a process upgrade, or when asked whether the project follows the process.
---
# Conformance check (dev-process)

## Steps
1. Run `python .process/check.py`. It never fails the build; it reports ❌ errors, ⚠️ warnings and ℹ️ info.
2. Fix what you can, in this order: missing required artefacts, invalid frontmatter, untested approved requirements, increment size or demo problems, placeholders.
3. For findings that should not be fixed, **propose** a waiver to the Owner, with the rule ID, a reason and an expiry date. Only the Owner adds waivers to `.process/config.yaml`.
4. Summarise for the Owner: what you fixed, what remains, and what you propose to waive.
