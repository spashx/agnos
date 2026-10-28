# PLAN-TRC-009: Charts from an Online Library

## Overview
Load Cytoscape.js and Apache ECharts from cdnjs, draw the Delivery charts and the Quality radar with ECharts in the
design system, and group the overlapping marks of the History timeline. Each step leaves the page and its tests working.

**Session split** (AGNOS context management, at most 10 tasks per session): the session of 2026-10-27/28 on
`feature/TRC` already holds TASK-TRC-055 to TASK-TRC-062; it does TASK-TRC-063 and TASK-TRC-064 only. **Handoff**:
the next session starts from TASK-TRC-065, reads ADR-TRC-010 first, and needs the network for the page tests.

## References
- **Requirements**: RQ-TRC-080 to RQ-TRC-088; amended: RQ-TRC-010, RQ-TRC-024 (superseded by RQ-TRC-082), RQ-TRC-061,
  RQ-TRC-075, RQ-TRC-079
- **ADRs**: ADR-TRC-010 (DEC-TRC-040 to DEC-TRC-044); ADR-TRC-002 (design system); amended: ADR-TRC-003 (DEC-TRC-005,
  DEC-TRC-006), ADR-TRC-008 (DEC-TRC-035), ADR-TRC-009 (DEC-TRC-039)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-TRC-063: The online libraries specified and decided
- **Tier**: M
- **Status**: Done
- **Description**: Write FTR-TRC-005 and ADR-TRC-010 from the owner's review of 2026-10-28, and mark the requirements and
  decisions they amend or supersede with a note naming them.
- **Requirement refs**: RQ-TRC-080 to RQ-TRC-088
- **ADR refs**: ADR-TRC-010 (DEC-TRC-040 to DEC-TRC-044)
- **Acceptance Criteria**: Given the documents, When `agnos-index` runs, Then RQ-TRC-080 to RQ-TRC-088 and DEC-TRC-040 to
  DEC-TRC-044 are listed with no duplicate; Given RQ-TRC-010, RQ-TRC-024, RQ-TRC-061, RQ-TRC-075, RQ-TRC-079,
  DEC-TRC-005, DEC-TRC-006, DEC-TRC-035, DEC-TRC-039, Then each names what amends it; Given the owner's review, Then
  ADR-TRC-010 is Accepted.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `agnos-index`: 391 entries, 48 documents, exit 0, RQ-TRC-080 to 088 and DEC-TRC-040 to 044 listed;
  `git diff`: one note added to each of RQ-TRC-010, RQ-TRC-024 (superseded), RQ-TRC-061, RQ-TRC-075, RQ-TRC-079,
  DEC-TRC-005, DEC-TRC-006, DEC-TRC-035, DEC-TRC-039; owner approval of 2026-10-28, ADR-TRC-010 Accepted. No code.
- **Assumptions**: ECharts 6.1.0 (latest on the cdnjs API on 2026-10-28) and Cytoscape.js 3.30.2 (the vendored version)
  with their cdnjs `sha512` hashes; the History overlap is solved by grouping marks (not by shifting them); the
  "lines per task" chart is replaced by "tasks per tier".

### TASK-TRC-064: Libraries from cdnjs, said when missing
- **Tier**: L
- **Status**: Done
- **Description**: Add `assets/libraries.json`; write the library scripts with their integrity from it; remove
  `scripts/vendor/`; name the libraries and licences in the footer; guard every use of Cytoscape.js and ECharts with the
  missing-library message; page tests skipped with their reason when cdnjs is unreachable (tests first).
- **Requirement refs**: RQ-TRC-080, RQ-TRC-081, RQ-TRC-082
- **ADR refs**: ADR-TRC-010 (DEC-TRC-040, DEC-TRC-041)
- **Acceptance Criteria**: Given a generated page, Then its scripts are the two cdnjs URLs with `integrity` and
  `crossorigin="anonymous"`, and `<page>.data.js`; Given a page whose library URLs fail, Then the Graph view shows the
  message naming Cytoscape.js and the Matrix is filled; Given a version changed in `libraries.json`, Then the page loads
  it; Given the whole suite with the network, Then it passes.
- **Dependencies**: TASK-TRC-063
- **Assignee**: AI
- **Verification**: Tests written first (4 errors: no `LIBRARIES_PATH`), then OK: the page's scripts are the cdnjs URLs of
  Cytoscape.js 3.30.2 and ECharts 6.1.0, each with its `integrity` and `crossorigin="anonymous"`, then `page.data.js`;
  the record's versions, URLs and `sha512` hashes valid, `scripts/vendor/` gone; a version changed in a copy of the record
  gives `/cytoscape/9.9.9/` in the page and in `meta.libraries`; a page whose library URLs fail shows "Cytoscape.js
  could not be loaded" in the Graph view and fills the matrix. Whole suite with the network: 291 tests OK, 3 skipped
  (the three `AGNOS_TRACE_PERF` measures). `SKILL.md`: the vendoring section replaced by "Libraries", the description
  and step 4 no longer say offline.
- **Assumptions**: the sentinel of RQ-TRC-026 (`DATA_BEFORE_PLAN_SHA256`) re-pinned on purpose, `meta.library` having
  become `meta.libraries` (RQ-TRC-082); the data-missing message names the `.data.js` script, no longer the first
  script; offline, the tests skip every page test (not only those of the libraries), cdnjs being probed once.

### TASK-TRC-065: ECharts in the design system, and its keyboard path
- **Tier**: M
- **Status**: Not Started
- **Description**: One helper that initialises an ECharts chart in SVG with `aria` and decals, its theme read from the
  resolved tokens, redrawn on a theme change, and the keyboard path (Tab, arrows, Enter) over its data items.
- **Requirement refs**: RQ-TRC-085, RQ-TRC-087
- **ADR refs**: ADR-TRC-010 (DEC-TRC-042, DEC-TRC-043); ADR-TRC-002 (DEC-TRC-009, DEC-TRC-010)
- **Acceptance Criteria**: Given a chart drawn in each theme, Then its text colour and font family equal the resolved
  tokens; Given the chart focused, When the right arrow is pressed, Then the first item's tooltip shows; Given the code,
  Then no raw visual literal is written.
- **Dependencies**: TASK-TRC-064
- **Assignee**: AI
- **Verification**: 
- **Assumptions**: 

### TASK-TRC-066: The Delivery charts with ECharts
- **Tier**: M
- **Status**: Not Started
- **Description**: Replace the three hand-drawn Delivery charts: points per active day per identity (A, B hatched),
  points over time with A and B marked and a zoom, tasks per tier A beside B; tiers named in full from `delivery.json`.
- **Requirement refs**: RQ-TRC-083, RQ-TRC-075, RQ-TRC-087
- **ADR refs**: ADR-TRC-010 (DEC-TRC-043); ADR-TRC-009 (DEC-TRC-039)
- **Acceptance Criteria**: Given the fixture, Then three library charts are drawn, their legends read "S, small task, 1
  point", "M, medium task, 3 points", "L, large task, 8 points", the third has one A and one B value per tier, and their
  texts use the caption or small size.
- **Dependencies**: TASK-TRC-065
- **Assignee**: AI
- **Verification**: 
- **Assumptions**: 

### TASK-TRC-067: The checks radar with ECharts
- **Tier**: M
- **Status**: Not Started
- **Description**: Replace the hand-drawn radar of the Quality view by an ECharts radar, one indicator per scored check,
  its tooltip and the click or Enter opening the check.
- **Requirement refs**: RQ-TRC-084, RQ-TRC-061, RQ-TRC-087
- **ADR refs**: ADR-TRC-010 (DEC-TRC-043); ADR-TRC-008 (DEC-TRC-035)
- **Acceptance Criteria**: Given the fixture, When the Quality view opens, Then the radar has one indicator per scored
  check with its score; When a point is chosen with the keyboard and Enter pressed, Then its check opens.
- **Dependencies**: TASK-TRC-065
- **Assignee**: AI
- **Verification**: 
- **Assumptions**: 

### TASK-TRC-068: Grouped marks in the History timeline
- **Tier**: M
- **Status**: Not Started
- **Description**: Merge the marks of a row that overlap at the current zoom into one group mark with its count and kind,
  its tooltip listing its commits, its activation zooming on them.
- **Requirement refs**: RQ-TRC-086, RQ-HST-007, RQ-HST-014
- **ADR refs**: ADR-TRC-010 (DEC-TRC-044); ADR-HST-001 (DEC-HST-005)
- **Acceptance Criteria**: Given a row with three commits within one hour and the whole history in view, Then one group
  mark reading 3 is drawn; When the view is zoomed on that hour, Then three marks are drawn.
- **Dependencies**: TASK-TRC-064
- **Assignee**: AI
- **Verification**: 
- **Assumptions**: 

### TASK-TRC-069: Speed, documentation and a run on XS56K
- **Tier**: M
- **Status**: Not Started
- **Description**: Measure the Delivery tab and the Quality view with the libraries cached, document the libraries,
  their record and the network need in `SKILL.md`, and generate the page of XS56K.
- **Requirement refs**: RQ-TRC-088, RQ-TRC-017
- **ADR refs**: ADR-TRC-010
- **Acceptance Criteria**: Given `AGNOS_TRACE_PERF=1`, Then the thresholds of RQ-TRC-088 hold; Given `SKILL.md`, Then it
  describes the libraries, `libraries.json` and the behaviour without network; Given the XS56K run, Then exit 0.
- **Dependencies**: TASK-TRC-066, TASK-TRC-067, TASK-TRC-068
- **Assignee**: AI
- **Verification**: 
- **Assumptions**: 
