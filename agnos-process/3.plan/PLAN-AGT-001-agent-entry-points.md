# PLAN-AGT-001: Agent entry points

## Overview
Implements FTR-AGT-001: `AGENTS.md` and the alignment of `CLAUDE.md` on the four skills.

## References
- **Requirement refs**: RQ-AGT-001
- **ADR refs**: None

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

### TASK-AGT-003: AGENTS.md says how each tool reads it, RQ-AGT-002 made consistent
- **Tier**: M
- **Status**: Done
- **Description**: `AGENTS.md` keeps its read-in-words order (no `@` line: no other tool documents an import syntax)
  and states that Claude Code already holds the instructions file through `CLAUDE.md`'s import; its closing sentence,
  false since TASK-AGT-002, says which tools read it. RQ-AGT-002's statement is aligned with its acceptance criterion.
  `CLAUDE.md` keeps both imports.
- **Requirement refs**: RQ-AGT-001, RQ-AGT-002
- **ADR refs**: None
- **Acceptance Criteria** (Gherkin):
  - **Given** `AGENTS.md`, **When** it is read, **Then** no line starts with `@`, §1 still orders reading the
    instructions file in full, and no sentence says that Claude Code does not read it
  - **Given** RQ-AGT-002, **When** its statement and its acceptance criterion are read, **Then** both accept a
    restatement carried through an import
  - **Given** `CLAUDE.md`, **When** it is read, **Then** it still holds `@AGENTS.md` and
    `@.github/instructions/agnos-sw-eng.instructions.md`
- **Dependencies**: TASK-AGT-002
- **Assignee**: AI
- **Verification**: search `^@` over `AGENTS.md` and `CLAUDE.md`: only `CLAUDE.md:5 @AGENTS.md` and
  `CLAUDE.md:6 @.github/instructions/agnos-sw-eng.instructions.md`; `AGENTS.md:11` still "read **in full**", no
  "every other agent" left except the new line 15 about the other agents. RQ-AGT-002's statement now names "their own
  text or in a file they import", as its criterion does. `agnos-meta-docs-sync` tests: 18 run, 18 passed, 0 skipped.
  `layout.py --check`: exit 1, 4 findings, all in `perf_center.py` (VERSION read from the layout), a file unchanged
  since `0b1de8b` (TASK-TRC-094), so not caused by this task. No unit test: documentation only.
- **Assumptions**: Option A of the owner's review of 2026-11-07, chosen over a `@` line in `AGENTS.md`
  (TASK-AGT-003's first draft, never written) after a critic's review and the vendors' documentation.
