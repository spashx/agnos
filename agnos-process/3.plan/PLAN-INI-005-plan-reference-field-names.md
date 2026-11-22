# PLAN-INI-005: Plan reference field names

## Overview
Gives the plan template the task's reference field names, has `agnos-init` convert the plans of the projects it updates, and
converts this repository, its demo and its fixtures.

## References
- **Requirement refs**: RQ-INI-022, RQ-INI-023
- **ADR refs**: ADR-INI-004 (DEC-INI-016, DEC-INI-017)
- **Requirements handed to another component**: RQ-TRC-139 (FTR-TRC-013) reads the new names, amended in TASK-INI-020.

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-INI-020: Record plan field names feature
- **Tier**: S
- **Status**: Done
- **Description**: Write FTR-INI-003, ADR-INI-004 and this plan, and amend RQ-TRC-139 and DEC-TRC-082 to the new names.
- **Requirement refs**: RQ-INI-022, RQ-INI-023, RQ-TRC-139
- **ADR refs**: ADR-INI-004
- **Acceptance Criteria**: Given the documents, When `agnos-index` runs, Then it reports no duplicate.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: trigram INI, the skill converting being `agnos-init`; ADR-INI-004 accepted under the owner's order of 2026-11-22 to implement every task autonomously.

### TASK-INI-021: Implement plan field conversion in init
- **Tier**: L
- **Status**: Not Started
- **Description**: Write the Gherkin-named tests first, then the conversion in `init.ps1` and `init.sh`, and describe it in the skill's `SKILL.md`.
- **Requirement refs**: RQ-INI-023
- **ADR refs**: ADR-INI-004 (DEC-INI-017)
- **Acceptance Criteria**:
  - Given a CRLF plan with the old names under `## References` and under a task, When either script runs, Then only the two References lines are renamed And both scripts write the same bytes And `converted <path>` is reported
  - Given a converted project, When run again, Then nothing is written And no `converted` line is reported
  - Given a legacy `process/` project, When run, Then it is moved, then converted
  - Given the suite of `agnos-init`, Then all pass
- **Dependencies**: TASK-INI-020
- **Assignee**: AI
- **Verification**: [filled at closure]
- **Assumptions**: [filled at closure]

### TASK-INI-022: Rename plan fields across repository
- **Tier**: L
- **Status**: Not Started
- **Description**: Rename the fields in the process file's template and the guide, convert this repository's plans, the demo's and the fixtures' with `agnos-init`'s conversion, verify the demo and add the changelog entry.
- **Requirement refs**: RQ-INI-022, RQ-INI-023
- **ADR refs**: ADR-INI-004 (DEC-INI-016)
- **Acceptance Criteria**:
  - Given the process file and the guide, Then their plan template uses `Requirement refs` and `ADR refs` And the process file holds at most 400 lines
  - Given the plans of this repository, the demo and the fixtures, Then no `## References` section holds `**Requirements**:` nor `**ADRs**:`
  - Given the demo, When `build.ps1 -Verify` runs, Then it reports 0 failed
  - Given the suites of `agnos-init`, `agnos-graph` and `agnos-perf-center`, Then all pass
- **Dependencies**: TASK-INI-021
- **Assignee**: AI
- **Verification**: [filled at closure]
- **Assumptions**: [filled at closure]
