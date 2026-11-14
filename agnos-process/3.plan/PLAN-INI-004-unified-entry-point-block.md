# PLAN-INI-004: Unified context-aware entry-point block

## Overview
Write one block for `CLAUDE.md` and `AGENTS.md`, explain in its comments how Claude Code and GitHub Copilot keep the process in context,
and explain the risks in the README. Order: TASK-INI-013, 014, 015, 016. The demo rebuild and the user's guide follow in a later session.
Everything stays local, on `feature/PLG`.

## References
- **Requirements**: RQ-INI-019, RQ-INI-020, RQ-INI-021
- **ADRs**: ADR-INI-003 (DEC-INI-014, DEC-INI-015)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-INI-013: Record block unification artifacts
- **Tier**: M
- **Status**: Done
- **Description**: Add RQ-INI-019 to RQ-INI-021 to FTR-INI-001, write ADR-INI-003 and this plan.
- **Requirement refs**: RQ-INI-019, RQ-INI-020, RQ-INI-021
- **ADR refs**: ADR-INI-003
- **Acceptance Criteria**: Given the artifacts, When `agnos-index` runs, Then it exits 0 And lists the new IDs.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `agnos-index`: exit 0, 905 entries, lists RQ-INI-019 to RQ-INI-021, ADR-INI-003, DEC-INI-014, DEC-INI-015,
  PLAN-INI-004, TASK-INI-013 to TASK-INI-016; DEC-INI-003 marked amended in ADR-INI-001.
- **Assumptions**: the artifacts take the trigram INI, their functional area, on the PLG session branch.

### TASK-INI-014: Merge block templates
- **Tier**: L
- **Status**: Done
- **Description**: Write the tests first, then replace `CLAUDE.block.md` and `AGENTS.block.md` by `agnos.block.md`, read by `init.ps1` and
  `init.sh`, with one question line for both tools.
- **Requirement refs**: RQ-INI-019
- **ADR refs**: ADR-INI-003 (DEC-INI-014)
- **Acceptance Criteria**: Given the new tests, When they run before the change, Then they fail; Given the change, When `agnos-init`'s
  suite runs, Then both blocks are byte-identical in both script versions, And every former test passes.
- **Dependencies**: TASK-INI-013
- **Assignee**: AI
- **Verification**: 2 new RQ-INI-019 tests before the change: 2 run, failures=2 (blocks differ; `AGENTS.block.md`, `CLAUDE.block.md`
  listed); after: `agnos-init` suite 40 run, OK, 0 skipped, PowerShell 5.1 and Git Bash both run on Windows.
- **Assumptions**: `CLAUDE.block.md` renamed with `git mv` so its history follows; the question line reuses the instructions file's wording.

### TASK-INI-015: Add context behaviour comments
- **Tier**: M
- **Status**: Not Started
- **Description**: Write the tests first, then add to the block its HTML comments on Claude Code and GitHub Copilot, and the visible
  order to invoke the process skill again after a compaction.
- **Requirement refs**: RQ-INI-020
- **ADR refs**: ADR-INI-003 (DEC-INI-015)
- **Acceptance Criteria**: Given the new tests, When they run before the change, Then they fail; Given the change, Then the comments
  name both tools, session start, clear and compaction, And the block holds no artifact ID.
- **Dependencies**: TASK-INI-014
- **Assignee**: AI
- **Verification**: pending
- **Assumptions**: pending

### TASK-INI-016: Document context-loss risks
- **Tier**: M
- **Status**: Not Started
- **Description**: Add to `README.md` a section on what happens to the process after a clear, an automatic and a manual compaction,
  for Claude Code and GitHub Copilot, with the risks and the action to take.
- **Requirement refs**: RQ-INI-021
- **ADR refs**: ADR-INI-003
- **Acceptance Criteria**: Given `README.md`, Then the section names both tools, clear, automatic and manual compaction, their risks
  and the action to take, And states what the documentation leaves unsaid.
- **Dependencies**: TASK-INI-015
- **Assignee**: AI
- **Verification**: pending
- **Assumptions**: pending
