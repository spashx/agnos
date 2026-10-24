# PLAN-TRC-005: Matrix Columns in Specification Order and Rearrangeable

## Overview
Implement RQ-TRC-051 and RQ-TRC-052 after ADR-TRC-006: the matrix is drawn from one column model, its default order
starts with the Feature, and the reader can move the columns, keep the order and reset it. Work stays in the skill's
`assets/` (`matrix.js`, `matrix.css`, `matrix.html`) and `SKILL.md`.

## References
- **Requirements**: RQ-TRC-051, RQ-TRC-052; RQ-TRC-014, RQ-TRC-041, RQ-TRC-043, RQ-TRC-045 (kept)
- **ADRs**: ADR-TRC-006 (DEC-TRC-027, DEC-TRC-028)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-TRC-039: One column model and the default order
- **Tier**: M
- **Status**: Done
- **Description**: Declare each matrix column once (key, label, hint, sort value, cell), draw the header and the rows
  from the ordered list of keys, select the default widths by `data-column`, and make Feature the first column.
- **Requirement refs**: RQ-TRC-051
- **ADR refs**: ADR-TRC-006 (DEC-TRC-027)
- **Acceptance Criteria**: Given the page opened with no saved order, When the matrix headers are read, Then they are
  Feature, Requirement, Coverage, ADRs / decisions, Plans / tasks, (Functions,) Source files, Lines, each cell under its
  own header, the default widths of each column unchanged, and the sort and the CSV as before.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `python -m unittest discover -s tests` (skill folder): 130 tests, 1 failure `test_RQ_TRC_026_..._data_is_the_one_before_this_feature`, which fails identically without this change (checked with the changes stashed), 1 skipped. New assertion in `test_callgraph` passes: headers feature, id, coverage, decisions, tasks, functions, files, lines; `ColumnResizeTest` passes with Requirement still sorted ascending. The default widths now select `th[data-column=…]` (no unquoted-quote form, so the page without a call graph holds no `data-column="functions"` text).
- **Assumptions**: None

### TASK-TRC-040: Move columns, remember the order, reset
- **Tier**: M
- **Status**: Not Started
- **Description**: Make the headers draggable and Alt+arrow movable, keep the order in the browser, add the "Reset
  columns" button with its tooltip, and document the matrix in `SKILL.md`.
- **Requirement refs**: RQ-TRC-052, RQ-TRC-045
- **ADR refs**: ADR-TRC-006 (DEC-TRC-028)
- **Acceptance Criteria**: Given the default order, When the Coverage header is moved before Feature, Then Coverage is
  first with its cells, the sort and widths are unchanged and the order survives a reload; When "Reset columns" is
  pressed, Then the default order and widths come back; Given a resize grip, When it is dragged, Then no move starts.
- **Dependencies**: TASK-TRC-039
- **Assignee**: AI
- **Verification**: Pending.
- **Assumptions**: None
