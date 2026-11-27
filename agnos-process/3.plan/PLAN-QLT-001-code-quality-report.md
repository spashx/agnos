# PLAN-QLT-001: The agnos-meta-qa Skill and agnos-trace's Quality Pass

## Overview
Delivers `agnos-meta-qa`, then corrects what it and VS Code report on `agnos-trace`. Everything stays local on `feature/TRC`: nothing is pushed.
The owner approved the plan and asked for it to run unattended on 2026-10-31.

## References
- **Requirement refs**: RQ-QLT-001 to RQ-QLT-010
- **ADR refs**: ADR-QLT-001 (DEC-QLT-001 to DEC-QLT-008)

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
- **Status**: Done
- **Description**: Correct the `ruff` findings of the four scripts of `agnos-trace`.
- **Requirement refs**: RQ-QLT-009
- **ADR refs**: ADR-QLT-001 (DEC-QLT-006, DEC-QLT-008)
- **Acceptance Criteria**: Given the scripts, When the report is read, Then only complexity findings are left, And the skill's unit tests pass.
- **Dependencies**: TASK-QLT-001
- **Assignee**: AI
- **Verification**: committed with TASK-QLT-005, the same output proving both: report on the scripts 0 open and 1 exception, from 38 `ruff` findings; `agnos-trace/tests`: 356 OK (3 skipped).
- **Assumptions**: `build`'s `patterns` was removed, since no caller passed it; its `depth` and `tasks` became keyword-only; `build` keeps 8 parameters as the one recorded exception (PLR0913), since the tests fix the first 6.

### TASK-QLT-005: Python, the complex functions
- **Tier**: L
- **Status**: Done
- **Description**: Cut the 13 functions above a cognitive complexity of 15 into named helpers, with no change of behaviour, the data file staying byte-identical.
- **Requirement refs**: RQ-QLT-009
- **ADR refs**: ADR-QLT-001 (DEC-QLT-008)
- **Acceptance Criteria**: Given the scripts, When the report is read, Then no open finding is left; Given this repository, When the generator runs before and after with a fixed time, Then the page's data is byte-identical, And the suite passes.
- **Dependencies**: TASK-QLT-004
- **Assignee**: AI
- **Verification**: report on the scripts and assets: 0 open, 1 exception, from 13 functions above 15. `page.json` and `page.data.js` byte-identical before and after, with `--call-graph --history` and a fixed time, on a clone of this repository (166 commits, 1646 functions) and on the demo (80 commits, merges, 7 identities). `page.html` identical apart from the data script's name in the comparison. `agnos-trace/tests`: 356 OK (3 skipped), performance tests included.
- **Assumptions**: the clone's checkout stopped on Windows' path limit, so it also ran with files missing from its working tree; SonarQube's own Python rules were read only in VS Code, where `trace_matrix.py`, `history.py` and `qa.py` show none and `scorecard.py` and `callgraph.py`, not open, may simply not be analysed.

### TASK-QLT-006: matrix.html, the accessibility findings
- **Tier**: M
- **Status**: Done
- **Description**: Correct, or record with a reason, each of the 20 findings of `matrix.html`, with no visual change.
- **Requirement refs**: RQ-QLT-010
- **ADR refs**: ADR-QLT-001 (DEC-QLT-007)
- **Acceptance Criteria**: Given the file's diagnostics, Then each one left is recorded here with its reason, And the page tests pass.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: diagnostics: 20 to 12. Corrected, 8: `nav role=tablist` became a `div` (S6842), seven `div role=group` became `fieldset` (S6819). Kept, 12, with the reason of each: `#split-left`, `#split-right`, `#history-split` (3 S6845, 3 S6819), the focusable separator of WAI-ARIA's window splitter, which an `hr` cannot be; `#search-results` (S6842, S6819), the popup listbox of WAI-ARIA's combobox, whose rich rows a `datalist` cannot show; `#help-body` (S6845), a scrolling region must take the keyboard's focus; `#history-plot` (S6845), it handles its zoom and pan keys; `#history-overview` (S6819), an `svg` cannot be a `fieldset`; `#matrix-table` (S5256), its `th` are added by the script. Rendering in Edge at 1440x900, six tabs, the demo's data: 232 rectangles measured, 0 different. `agnos-trace/tests`: 356 OK (3 skipped).
- **Assumptions**: the rectangles cover the elements with an `id` and the tabs; no human looked at the page, and no screen reader was run.

### TASK-QLT-007: Say the skill exists
- **Tier**: S
- **Status**: Done
- **Description**: Mention the skill in `CONTRIBUTING.md` and `CHANGELOG.md`.
- **Requirement refs**: RQ-QLT-001, RQ-QLT-008
- **ADR refs**: ADR-QLT-001 (DEC-QLT-001)
- **Acceptance Criteria**: Given both files, Then each names the skill, And `CONTRIBUTING.md` says it blocks nothing.
- **Dependencies**: TASK-QLT-001
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: None
