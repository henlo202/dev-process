# Playbook: Analyst agent

**Phases:** P0 (brief), P1 (requirements)
**Reads:** `AGENTS.md`, `docs/brief.md`, existing `docs/requirements/`
**Writes:** `docs/brief.md` (draft), `docs/requirements/*.md`

## Steps
1. Summarise your understanding of the goal in three sentences and list open questions. **Ask them before writing.**
2. Write requirements using the template in `.process/templates/requirements.md`:
   - Functional `REQ-nnn` and non-functional `NFR-nnn`, continuing from the highest existing ID.
   - At least one Given/When/Then acceptance criterion each, observable by a test.
   - Priority and a `Source:` for every requirement.
3. Check for NFRs in security, performance, accessibility, operability and privacy, even if the brief is silent.
4. Record assumptions explicitly in the requirements file.
5. Set the status to `in-review` and hand over to the Reviewer agent.

## Stop and ask when
- A requirement would contradict a non-goal in the brief.
- You cannot find a source for a requirement.
- An approved requirement needs to change.
