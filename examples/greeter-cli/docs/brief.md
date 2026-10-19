---
artefact: brief
status: approved
version: 1.0.0
owner: Owner
updated: 2026-10-19
---
# greeter-cli: Initiative brief

> Worked example for dev-process. Small on purpose: it shows every T2 artefact
> without much domain content to read.

## 1. Problem
Scripts and onboarding demos need a predictable way to print a greeting in
English or Swedish. Today, each script hand-rolls its own `echo`, and the
output is inconsistent.

## 2. Target users
Developers who write shell scripts and demos.

## 3. Goals & success criteria
- SC-1: A single command prints a greeting in English or Swedish.
- SC-2: The tool installs with no third-party dependencies.

## 4. Scope
### In scope
- A command-line tool `greet` with a name argument and a language option.
### Non-goals
- A graphical or web interface.
- Languages other than English and Swedish in v1.

## 5. Constraints
Python 3.9+, standard library only.

## 6. Risk tier
**Tier:** T2. A new tool, but small, with no data, no network and no security
surface. It is not T1, because it introduces a new user-facing interface.

## 7. First increments
- INC-001: walking skeleton, greeting in English
- INC-002: Swedish greeting and input validation

## 8. Open questions & assumptions
- Assumption: names are passed as one argument (quoted if they contain spaces).

## History
| Date | Change |
|------|--------|
| 2026-10-19 | Created and approved at G0 |
