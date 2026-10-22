# Ownership

| Question | Answer |
|----------|--------|
| Who owns dev-process? | The **Owner**: the single human who runs the initiatives that use it. |
| Who may propose changes? | The Owner, and any agent (for example from a retrospective or a recurring conformance warning). |
| Who approves changes? | The Owner only. Agents never merge to this repository. |
| Who may grant waivers in a project? | The Owner only. |
| Where is the source of truth? | This repository's `main` branch. The HTML site is generated from it. |
| What language? | English, for all process documents and all project artefacts ([PDR-0005](decisions/PDR-0005-english-only.md)). |

## Principles
1. **Useful over complete.** A rule nobody follows is removed or fixed, not enforced harder.
2. **The process follows itself.** Changes to this repository go through a light version of the process (see [change process](change-process.md)).
3. **Explicit beats implicit.** Deviations are recorded as waivers, and decisions as PDRs.
4. **Tool neutral.** The core never depends on a specific agent product ([PDR-0001](decisions/PDR-0001-tool-neutral.md)).
5. **Project neutral.** Nothing here names or describes a project that uses the process ([PDR-0009](decisions/PDR-0009-project-neutral.md)). See [project neutrality](change-process.md#project-neutrality).
