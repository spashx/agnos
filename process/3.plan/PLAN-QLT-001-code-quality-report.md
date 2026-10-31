# PLAN-QLT-001: The agnos-meta-qa Skill and agnos-trace's Quality Pass

## Overview
Delivers `agnos-meta-qa`, then corrects what it and VS Code report on `agnos-trace`. Everything stays local on `feature/TRC`: nothing is pushed.
The owner approved the plan and asked for it to run unattended on 2026-10-31.

## References
- **Requirements**: RQ-QLT-001 to RQ-QLT-010
- **ADRs**: ADR-QLT-001 (DEC-QLT-001 to DEC-QLT-008)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-QLT-001: The skill
- **Tier**: L
- **Status**: Done
- **Description**: Write the tests first, then `scripts/qa.py` with `setup` and `check`, the pinned assets, `SKILL.md`, its Claude Code pointer and the `.gitignore` entry.
- **Requirement refs**: RQ-QLT-001, RQ-QLT-002, RQ-QLT-003, RQ-QLT-004, RQ-QLT-005, RQ-QLT-006, RQ-QLT-007, RQ-QLT-008
- **ADR refs**: ADR-QLT-001 (DEC-QLT-001 to DEC-QLT-007)
- **Acceptance Criteria**: Given the skill's tests, When they run, Then each criterion of RQ-QLT-001 to RQ-QLT-008 holds; Given `setup` then `check --all`, Then the real analysers give a report with the schema.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `agnos-meta-qa/tests`: 32 OK, the three real analysers included, one failing first on a fixture's misplaced marker. `setup` exit 0; `check --all` exit 0 with 92 findings on 7 files, 13 complexity and 4 JS complexity among them. `check` on the skill itself: 2 open at the task's commit, 0 after a docstring's correction in the commit of TASK-QLT-002. `agnos-meta-demo` 7 OK, `agnos-meta-docs-sync` 14 OK.
- **Assumptions**: the owner's "go" for unattended work counts as DoR approval and as confirmation of each commit; the 5 `matrix.js` findings only VS Code reports stay outside the report, by DEC-QLT-007; `setup` ran on Windows only.

### TASK-QLT-002: matrix.js, the simple findings
- **Tier**: M
- **Status**: Done
- **Description**: Correct the 25 findings of `matrix.js` other than complexity, dead code included, with the 5 only VS Code reports.
- **Requirement refs**: RQ-QLT-009
- **ADR refs**: ADR-QLT-001 (DEC-QLT-007, DEC-QLT-008)
- **Acceptance Criteria**: Given `matrix.js`, When the report and its diagnostics are read, Then only complexity findings are left, And the page tests pass.
- **Dependencies**: TASK-QLT-001
- **Assignee**: AI
- **Verification**: committed with TASK-QLT-003, the same output proving both: report on `matrix.js` 0 open; VS Code diagnostics of the file: empty; `agnos-trace/tests`: 356 OK (3 skipped), the page run in Edge.
- **Assumptions**: the removed `showSearchTip`, `MONTHS_PER_YEAR` and `n` were unused, as a search of the file confirmed; TASK-QLT-002 and TASK-QLT-003 share one commit, since one set of replacements applied both.

### TASK-QLT-003: matrix.js, the complex functions
- **Tier**: M
- **Status**: Done
- **Description**: Cut the 4 functions above a cognitive complexity of 15 into named helpers, with no change of behaviour.
- **Requirement refs**: RQ-QLT-009
- **ADR refs**: ADR-QLT-001 (DEC-QLT-008)
- **Acceptance Criteria**: Given `matrix.js`, When the report is read, Then it has no open finding, And the page tests pass.
- **Dependencies**: TASK-QLT-002
- **Assignee**: AI
- **Verification**: report on `matrix.js`: 0 open, from 24; the 4 functions (`shownRows` 31, the module's flow 25, `renderDetail` 17, `renderCommitDetail` 16) are below 15, no exception used; `agnos-trace/tests`: 356 OK (3 skipped).
- **Assumptions**: the suite is the behaviour's safeguard, and no human looked at the page: a visual check remains to be done by the owner.

### TASK-QLT-004: Python, the rule findings
- **Tier**: M
- **Status**: Not Started
- **Description**: Correct the `ruff` findings of the four scripts of `agnos-trace`.
- **Requirement refs**: RQ-QLT-009
- **ADR refs**: ADR-QLT-001 (DEC-QLT-006, DEC-QLT-008)
- **Acceptance Criteria**: Given the scripts, When the report is read, Then only complexity findings are left, And the skill's unit tests pass.
- **Dependencies**: TASK-QLT-001
- **Assignee**: AI
- **Verification**: pending
- **Assumptions**: pending

### TASK-QLT-005: Python, the complex functions
- **Tier**: L
- **Status**: Not Started
- **Description**: Cut the 13 functions above a cognitive complexity of 15 into named helpers, with no change of behaviour, the data file staying byte-identical.
- **Requirement refs**: RQ-QLT-009
- **ADR refs**: ADR-QLT-001 (DEC-QLT-008)
- **Acceptance Criteria**: Given the scripts, When the report is read, Then no open finding is left; Given this repository, When the generator runs before and after with a fixed time, Then the page's data is byte-identical, And the suite passes.
- **Dependencies**: TASK-QLT-004
- **Assignee**: AI
- **Verification**: pending
- **Assumptions**: pending

### TASK-QLT-006: matrix.html, the accessibility findings
- **Tier**: M
- **Status**: Not Started
- **Description**: Correct, or record with a reason, each of the 20 findings of `matrix.html`, with no visual change.
- **Requirement refs**: RQ-QLT-010
- **ADR refs**: ADR-QLT-001 (DEC-QLT-007)
- **Acceptance Criteria**: Given the file's diagnostics, Then each one left is recorded here with its reason, And the page tests pass.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: pending
- **Assumptions**: pending

### TASK-QLT-007: Say the skill exists
- **Tier**: S
- **Status**: Not Started
- **Description**: Mention the skill in `CONTRIBUTING.md` and `CHANGELOG.md`.
- **Requirement refs**: RQ-QLT-001, RQ-QLT-008
- **ADR refs**: ADR-QLT-001 (DEC-QLT-001)
- **Acceptance Criteria**: Given both files, Then each names the skill, And `CONTRIBUTING.md` says it blocks nothing.
- **Dependencies**: TASK-QLT-001
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: None
