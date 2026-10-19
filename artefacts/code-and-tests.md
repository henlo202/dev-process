---
id: [code, tests]
---
# Source code & automated tests

**What it is:** The implementation, and the automated tests that prove it
meets its requirements.

## Rules
- Tests are written before or together with the code, never afterwards as an afterthought.
- Each test that proves an acceptance criterion names the requirement ID in its name or a comment, e.g. `test_REQ_007_empty_export_has_header` or `// REQ-007 AC-007.2`.
- Deleting or weakening a test needs a reason in the PR description.
- Tests live in the folders listed under `test_paths` in `.process/config.yaml`.

See the [QA guide](../guides/quality-assurance.md).
- Spike code is never merged. Production code is rebuilt test-first, using what the spike taught.
