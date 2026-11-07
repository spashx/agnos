# PLAN-RSI-001: Recursive self-improvement as a skill

<!-- PLAN-RSI-001: RQ-RSI-001 to RQ-RSI-004 / ADR-RSI-001 -->

## Overview
Implements FTR-RSI-001: the `agnos-self-improvement` skill, its budget script, and the reduction of
the RECURSIVE SELF-IMPROVEMENT SESSIONS section of the instructions file.

## References
- **Requirements**: RQ-RSI-001, RQ-RSI-002, RQ-RSI-003, RQ-RSI-004
- **ADRs**: ADR-RSI-001 (DEC-RSI-001, DEC-RSI-002, DEC-RSI-003)

---

## Tasks

### TASK-RSI-001: Feature, ADR and plan
- **Tier**: M
- **Status**: Done
- **Description**: Write FTR-RSI-001, ADR-RSI-001 and this plan, then rebuild the index.
- **Requirement refs**: RQ-RSI-001, RQ-RSI-002, RQ-RSI-003, RQ-RSI-004
- **ADR refs**: ADR-RSI-001
- **Acceptance Criteria** (Gherkin):
  - **Given** the three documents
  - **When** `agnos-index` runs
  - **Then** it exits 0 and indexes FTR-RSI-001, RQ-RSI-001 to 004, ADR-RSI-001, DEC-RSI-001 to 003,
    PLAN-RSI-001 and TASK-RSI-001 to 005
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `build-index.ps1`: 762 entries, 110 documents, exit 0; FTR-RSI-001, RQ-RSI-001
  to 004, ADR-RSI-001, DEC-RSI-001 to 003, PLAN-RSI-001, TASK-RSI-001 to 005 indexed, no duplicate.
- **Assumptions**: The line-budget sentence of the instructions file carries the marker RQ-PLG-019,
  which is about the process naming itself, not the budget: the ceiling is read from the sentence,
  not from a marker. The ceiling override in a declaration is written `at most <N> lines`. No unit
  test: documents only.

### TASK-RSI-002: Budget script and its tests
- **Tier**: L
- **Status**: Not Started
- **Description**: Write `scripts/self_improvement.py` (target resolution, ceiling, budget) and its
  unit tests, tests first.
- **Requirement refs**: RQ-RSI-002, RQ-RSI-003, RQ-RSI-004
- **ADR refs**: ADR-RSI-001 (DEC-RSI-002, DEC-RSI-003)
- **Acceptance Criteria** (Gherkin): those of RQ-RSI-002, RQ-RSI-003 and RQ-RSI-004, one test each
- **Dependencies**: TASK-RSI-001
- **Assignee**: AI
- **Verification**: pending
- **Assumptions**: None

### TASK-RSI-003: The skill's entry points
- **Tier**: M
- **Status**: Not Started
- **Description**: Write `.github/skills/agnos-self-improvement/SKILL.md`, following the skill
  authoring practices, and its `.claude/skills/` pointer.
- **Requirement refs**: RQ-RSI-001
- **ADR refs**: ADR-RSI-001 (DEC-RSI-001)
- **Acceptance Criteria** (Gherkin): those of RQ-RSI-001 on the skill
- **Dependencies**: TASK-RSI-002
- **Assignee**: AI
- **Verification**: pending
- **Assumptions**: None

### TASK-RSI-004: Instructions file and entry points
- **Tier**: L
- **Status**: Not Started
- **Description**: Reduce the RECURSIVE SELF-IMPROVEMENT SESSIONS section and END SESSION step 3; add
  the improvement-target declaration and the skill to this repository's `CLAUDE.md` and `AGENTS.md`.
- **Requirement refs**: RQ-RSI-001, RQ-RSI-002
- **ADR refs**: ADR-RSI-001 (DEC-RSI-001, DEC-RSI-002)
- **Acceptance Criteria** (Gherkin): those of RQ-RSI-001 on the instructions file; the script resolves
  this repository's target to the instructions file; `agnos-init` tests pass unchanged; post-edit line
  count reported
- **Dependencies**: TASK-RSI-003
- **Assignee**: AI
- **Verification**: pending
- **Assumptions**: None

### TASK-RSI-005: Changelog entry
- **Tier**: S
- **Status**: Not Started
- **Description**: Add the new skill and the amended target rule to `CHANGELOG.md`.
- **Requirement refs**: RQ-RSI-001, RQ-RSI-002
- **ADR refs**: ADR-RSI-001
- **Acceptance Criteria** (Gherkin): Given `CHANGELOG.md`, When its unreleased entries are read, Then
  they name the skill and the removed fallback
- **Dependencies**: TASK-RSI-004
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: None
