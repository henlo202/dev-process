# Requirements handling

## Principles
1. **Every requirement is uniquely identified** (`REQ-nnn` functional, `NFR-nnn` non-functional), and IDs are never reused.
2. **Every requirement is testable.** Acceptance criteria use Given/When/Then, and each one can be checked by an automated test, or is marked `manual` with a reason.
3. **Every requirement is traceable**: brief → requirement → task → test → release.
4. **Approved requirements change only through versioning**, never silently.

## Lifecycle
`draft` → `approved` (at G1) → (changed: new version, re-approved at the next G1 or G4) → `retired`

## Traceability
Traceability is maintained by convention, so no tool is needed:

| Link | How |
|------|-----|
| Requirement → brief | `Source:` field in the requirement |
| Task → requirement | `Requirements:` field in the task |
| Test → requirement | Requirement ID in the test name or a comment (`REQ-007`, `test_REQ_007_...`) |
| Commit/PR → requirement | Requirement ID in the PR description |
| Release → requirement | Changelog entries mention IDs where useful |

The conformance checker scans `docs/requirements/` for IDs and the `test_paths`
folders for references. It warns about requirements with no test, and about
references to IDs that do not exist.

## Working with agents
- The Analyst agent must **ask** about anything it cannot source from the brief or the Owner, and record assumptions explicitly.
- Prefer many small requirements to a few big ones; they trace better.
- Non-functional requirements are the most often forgotten. The Reviewer agent checks for security, performance, accessibility, operability and privacy every time.

## Changing requirements mid-flight
1. Update the requirement and bump the file's version, with a change-log entry.
2. Set its status back to `draft` if the change is material.
3. Update the affected tests and tasks.
4. Re-approve: at the next G1, or explicitly in the G4 checklist for small changes.
