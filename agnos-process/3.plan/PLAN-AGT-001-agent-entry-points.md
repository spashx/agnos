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

### TASK-AGT-002: CLAUDE.md imports AGENTS.md's own reminders
- **Tier**: S
- **Status**: Done
- **Description**: `CLAUDE.md` gains an `@AGENTS.md` import (Claude Code's own native cross-tool-sharing
  mechanism) ahead of its existing `@.github/instructions/agnos-sw-eng.instructions.md` import, so
  AGENTS.md's "Non-negotiable rules" and generic tool mapping — including the explicit approval-gate
  restatement — load into every Claude Code session without duplicating that text in CLAUDE.md itself.
- **Requirement refs**: RQ-AGT-002
- **ADR refs**: None
- **Acceptance Criteria** (Gherkin):
  - **Given** `CLAUDE.md`
  - **When** it is read
  - **Then** its first import is `@AGENTS.md`, ahead of the existing instructions-file import
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `CLAUDE.md` reread after the edit: `@AGENTS.md` present as the first `@` line, followed
  by `@.github/instructions/agnos-sw-eng.instructions.md`, unchanged. No unit test: documentation-only,
  nothing executable (Tier S).
- **Assumptions**: Chosen over copying AGENTS.md's "Non-negotiable rules" text into CLAUDE.md verbatim
  (the alternative the owner was offered), per the owner's explicit choice of the import mechanism over
  duplication.
