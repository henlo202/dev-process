---
artefact: requirements
status: approved
version: 1.0.0
owner: Analyst agent
updated: 2026-10-19
---
# Requirements: greeting

## Functional requirements

### REQ-001: Greet a person by name
- **Priority:** must
- **Status:** approved
- **Source:** brief SC-1

The user can print a greeting addressed to a given name.

**Acceptance criteria**
- AC-001.1: Given the name "Ada", when the user runs `greet Ada`, then "Hello, Ada!" is printed.

### REQ-002: Greet in Swedish
- **Priority:** must
- **Status:** approved
- **Source:** brief SC-1

**Acceptance criteria**
- AC-002.1: Given the name "Ada", when the user runs `greet Ada --lang sv`, then "Hej, Ada!" is printed.

### REQ-003: Reject an empty name
- **Priority:** should
- **Status:** approved
- **Source:** Owner, G1 review

**Acceptance criteria**
- AC-003.1: Given an empty or whitespace-only name, when the user runs `greet ""`, then the tool exits with status 2 and prints an error to stderr.

### REQ-004: Helpful usage text
- **Priority:** could
- **Status:** approved
- **Source:** Owner

**Acceptance criteria**
- AC-004.1 (manual): `greet --help` explains the arguments in plain language. This is checked by reading, since "plain language" is not machine-checkable. A waiver is recorded in `.process/config.yaml`.

## Non-functional requirements

### NFR-001: No third-party dependencies
- **Priority:** must
- **Status:** approved
- **Category:** operability

**Acceptance criteria**
- AC-NFR-001.1: The package imports only Python standard-library modules.

## Change log
| Date | Version | Change |
|------|---------|--------|
| 2026-10-19 | 1.0.0 | REQ-001 and NFR-001 approved at G1 for INC-001; REQ-002 to REQ-004 at G1 for INC-002 (REQ-003 added during review) |
