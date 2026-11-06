# PLAN-AGT-001: Agent entry points

## Overview
Implements FTR-AGT-001: `AGENTS.md` and the alignment of `CLAUDE.md` on the four skills.

## References
- **Requirements**: RQ-AGT-001
- **ADRs**: None

---

## Tasks

### TASK-AGT-001: AGENTS.md and CLAUDE.md skill alignment
- **Tier**: M
- **Status**: Done
- **Description**: Add `AGENTS.md` (process loading, rules reminder, skills, tool mapping, layout)
  and add the missing `agnos-trace` entry to `CLAUDE.md`.
- **Requirement refs**: RQ-AGT-001
- **ADR refs**: None
- **Acceptance Criteria** (Gherkin):
  - **Given** `AGENTS.md` and `CLAUDE.md`
  - **When** they are searched for the instructions file and the four skill names
  - **Then** every one is found in both files
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `Select-String` over `AGENTS.md` and `CLAUDE.md` for
  `agnos-sw-eng.instructions.md`, `agnos-index`, `agnos-git-workflow`, `agnos-design-system`,
  `agnos-trace`: 10/10 True. `.claude/skills/agnos-trace/SKILL.md` exists.
- **Assumptions**: No unit test: documentation only, nothing executable. No ADR: Tier M.
