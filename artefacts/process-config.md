---
id: process-config
---
# Process configuration (`.process/config.yaml`)

**What it is:** The machine-readable link between a project and this process.
The conformance checker and agents read it.

## Fields
| Field | Meaning |
|-------|---------|
| `process_version` | The pinned dev-process version, e.g. `0.1.0`. |
| `project` | The project name. |
| `tier` | The highest tier of work currently expected (`T1`, `T2`, `T3`). This decides which artefacts are required. |
| `test_paths` | Folders or globs where the checker looks for requirement IDs in tests. |
| `waivers` | A list of deliberate deviations. See [waivers](../governance/waivers.md). |

The scaffolder also copies a snapshot of `process.yaml` and the checker into
`.process/`, so a project can be checked offline and stays pinned to its version.
