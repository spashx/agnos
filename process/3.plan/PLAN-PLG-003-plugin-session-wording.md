# PLAN-PLG-003: The Process Speaks to a Plugin User, and a New Release

## Overview
Correct the three findings of the owner's Claude Code session of 2026-11-04 (FTR-PLG-003), bring the entry-point documents up to date,
and rehearse the release again for the Copilot checks of TASK-PLG-007. No push at any step (DEC-PLG-007).

## References
- **Requirements**: RQ-PLG-018 to RQ-PLG-022, RQ-PLG-004, RQ-DOC-001, RQ-DOC-002, RQ-INI-007 (amended), RQ-PLG-008, RQ-PLG-009
- **ADRs**: ADR-PLG-003, ADR-PLG-001, ADR-PLG-002

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-PLG-018: Feature, decisions and plan
- **Tier**: L
- **Status**: Done
- **Description**: Write FTR-PLG-003, ADR-PLG-003 and this plan, and mark the requirements it amends.
- **Requirement refs**: RQ-PLG-018 to RQ-PLG-022
- **ADR refs**: ADR-PLG-003
- **Acceptance Criteria**: Given the owner's approval, Then ADR-PLG-003 is Accepted; Given the index, Then it has no duplicate.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: ADR-PLG-003 Accepted, owner's "d'accord pour tout" of 2026-11-04; RQ-PLG-004, RQ-DOC-001, RQ-DOC-002 and RQ-INI-007 hold "Amended by"; `agnos-index` exit 0, no duplicate. No test: documents only.
- **Assumptions**: the file is named `AGNOS-GETTING-STARTED.md`, the prefix keeping a developer's own guide untouched; the target of self-improvement is named by the block, after the owner found "the project's folder" unclear.

### TASK-PLG-019: The improvement target, and "this file"
- **Tier**: M
- **Status**: Not Started
- **Description**: Define the improvement target in the RECURSIVE SELF-IMPROVEMENT section, refer to it from END SESSION step 3, and drop the file name from the line budget.
- **Requirement refs**: RQ-PLG-018, RQ-PLG-019
- **ADR refs**: ADR-PLG-003 (DEC-PLG-013, DEC-PLG-014)
- **Acceptance Criteria**: Given RQ-PLG-018's and RQ-PLG-019's criteria, Then they hold, tested on the skill `process_skill` generates; Given the instructions file, Then its line count is at most 400 and is reported.
- **Dependencies**: TASK-PLG-018
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-PLG-020: The block reads the project's rules, and the init's last words in two steps
- **Tier**: M
- **Status**: Not Started
- **Description**: Add the line reading `process/project-rules.md` to both block templates, reword the success step of `agnos-init`'s SKILL.md, and rebuild the demo with the new block.
- **Requirement refs**: RQ-PLG-018, RQ-PLG-020, RQ-PLG-004
- **ADR refs**: ADR-PLG-003 (DEC-PLG-013, DEC-PLG-015)
- **Acceptance Criteria**: Given RQ-PLG-018's block criterion and RQ-PLG-020's criteria, Then they hold, tested first in `agnos-init`'s suite; Given `agnos-meta-demo`'s suite, Then it passes.
- **Dependencies**: TASK-PLG-018
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-PLG-021: The getting-started file written by init
- **Tier**: M
- **Status**: Not Started
- **Description**: Reword `GETTING_STARTED.MD` for a plugin user into the template `AGNOS-GETTING-STARTED.md`, and make both init scripts write and report it; the init's skill points to it.
- **Requirement refs**: RQ-PLG-021, RQ-PLG-020, RQ-PLG-022
- **ADR refs**: ADR-PLG-003 (DEC-PLG-016, DEC-PLG-017)
- **Acceptance Criteria**: Given RQ-PLG-021's criteria, Then they hold, tested first in `agnos-init`'s suite on both scripts; Given the template, Then it names no file of this repository a plugin user lacks; Given `agnos-meta-demo`'s suite, Then it passes.
- **Dependencies**: TASK-PLG-020
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-PLG-022: The guide leaves the root
- **Tier**: L
- **Status**: Not Started
- **Description**: Remove `GETTING_STARTED.MD`; `agnos-meta-docs-sync` keeps the template as its fourth document; the release stops delivering the guide; links in `README.md`, `CONTRIBUTING.md` and the issue template follow.
- **Requirement refs**: RQ-PLG-022, RQ-DOC-001, RQ-DOC-002, RQ-INI-007
- **ADR refs**: ADR-PLG-003 (DEC-PLG-017)
- **Acceptance Criteria**: Given RQ-PLG-022's criteria, Then they hold, the docs-sync and release ones tested first in their suites.
- **Dependencies**: TASK-PLG-021
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-PLG-023: The entry-point documents brought up to date
- **Tier**: M
- **Status**: Not Started
- **Description**: Record the Claude Code full session in the README's "What was tested" table, then run `agnos-meta-docs-sync` and review what it changes.
- **Requirement refs**: RQ-PLG-008, RQ-PLG-009
- **ADR refs**: ADR-PLG-001 (DEC-PLG-006)
- **Acceptance Criteria**: Given the README, Then the Claude Code row states the full session observed on 2026-11-04 and only that; Given `CHANGELOG.md`, Then `[Unreleased]` holds PLAN-PLG-002 and PLAN-PLG-003 changes; Given `agnos-meta-demo`'s suite, Then it passes.
- **Dependencies**: TASK-PLG-019, TASK-PLG-022
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-PLG-024: The release rehearsed again, and proved
- **Tier**: M
- **Status**: Not Started
- **Description**: Rehearse HEAD into `C:\dev\repos\spashx\agnos-marketplace`, then run `agnos-meta-plugin-proof` on it.
- **Requirement refs**: RQ-PLG-007, RQ-PLG-010, RQ-PLG-012 to RQ-PLG-017
- **ADR refs**: ADR-PLG-002, ADR-PLG-001
- **Acceptance Criteria**: Given a rehearsal of the last commit, Then the exit is 0 and the lines to read are judged; Given the proof, Then every line it runs passes, And the lines it skips are stated with why.
- **Dependencies**: TASK-PLG-023
- **Assignee**: AI
- **Verification**:
- **Assumptions**:
