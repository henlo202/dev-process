# Waivers & deviations

A waiver is a **deliberate, visible** decision not to follow a rule. It lives in
the project's `.process/config.yaml`:

```yaml
waivers:
  - rule: artefact-missing:runbook
    reason: CLI library with no runtime; release steps are in CONTRIBUTING.md
    expires: 2027-06-30
```

| Field | Rule |
|-------|------|
| `rule` | The rule ID exactly as printed by the checker (e.g. `artefact-missing:runbook`, `untested-requirement:REQ-004`). A trailing `*` matches a prefix (e.g. `untested-requirement:*`). |
| `reason` | Required. Why this rule does not apply, or why not now. |
| `expires` | Required. An ISO date. Expired waivers are reported as warnings. |

## Rules
- Only the Owner adds waivers. Agents may suggest them in a PR, with reasoning.
- Waived findings still appear in the report as ℹ️, so skipping is never silent.
- Skipping a whole gate for a single increment is recorded as a gate record with `decision: approved` and a note "waived: <reason>". Do not just skip it.
- Recurring waivers across projects are a signal to [change the process](change-process.md).
