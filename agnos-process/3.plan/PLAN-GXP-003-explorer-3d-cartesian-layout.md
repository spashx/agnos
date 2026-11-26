# PLAN-GXP-003: Explorer 3D cartesian layout with axis indicator

## Overview
The 3D view's axis indicator in its bottom left corner, and a cartesian layout with a graduated trihedron, each toggled in
the View menu, before lot B2 (RQ-GXP-016 to RQ-GXP-018).

## References
- **Requirement refs**: RQ-GXP-020, RQ-GXP-021, RQ-GXP-022, RQ-GXP-002, RQ-GXP-019
- **ADR refs**: ADR-GXP-003 (DEC-GXP-014 to DEC-GXP-016); ADR-GXP-002; design system ADR-TRC-002 (DEC-TRC-009, DEC-TRC-010), RQ-TRC-018
- **Requirements handed to another component**: None; every change stays in `agnos-graph`'s explorer assets and tests.

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-GXP-019: Document explorer 3D cartesian layout
- **Tier**: L
- **Status**: Done
- **Description**: Write RQ-GXP-020, RQ-GXP-021, ADR-GXP-003 and this plan.
- **Requirement refs**: RQ-GXP-020, RQ-GXP-021
- **ADR refs**: ADR-GXP-003
- **Acceptance Criteria**:
  - Given the index rebuilt, Then RQ-GXP-020, RQ-GXP-021, ADR-GXP-003, DEC-GXP-014, DEC-GXP-015, PLAN-GXP-003 and TASK-GXP-019 to TASK-GXP-023 are listed
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `agnos-index`: 1211 entries, 188 documents, no duplicate; RQ-GXP-020, RQ-GXP-021, ADR-GXP-003, DEC-GXP-014, DEC-GXP-015, PLAN-GXP-003, TASK-GXP-019 to 023 listed. No test (documents only).
- **Assumptions**: owner's choices of 2026-11-26: a separate ADR; the cartesian axes reuse the angle (x), height (y) and radius (z) choices.

### TASK-GXP-020: Add 3D axis indicator
- **Tier**: M
- **Status**: Done
- **Description**: Write the tests first, then draw the axis indicator in a bottom left viewport following the camera, labelled from the dimensions, toggled in the View menu.
- **Requirement refs**: RQ-GXP-020
- **ADR refs**: ADR-GXP-003 (DEC-GXP-014)
- **Acceptance Criteria**:
  - Given the 3D view, Then the indicator is shown And its height axis reads the first commit date
  - When the height is set to the changed lines, Then the indicator's height axis reads the changed lines
  - When the axis indicator is unchecked, Then the indicator is hidden
- **Dependencies**: TASK-GXP-019
- **Assignee**: AI
- **Verification**: `Indicator3DTest` 3 tests failed first (KeyError, no indicator hook), then OK (Ran 3 tests, OK). Full suite run in TASK-GXP-023.
- **Assumptions**: in the cylindrical layout the indicator shows the height axis, the radius at angle 0 and a quarter arc for the angle; its square is 96 CSS px, cleared to the 3D background; axes x, y, z in Okabe-Ito vermillion, green, blue (new tokens axis-x/y/z).

### TASK-GXP-021: Add 3D cartesian layout
- **Tier**: M
- **Status**: Done
- **Description**: Write the tests first, then add the cylindrical and cartesian layout choice to the View menu, placing points at x, y, z from the angle, height and radius values, rings and angle labels hidden in cartesian.
- **Requirement refs**: RQ-GXP-021, RQ-GXP-020
- **ADR refs**: ADR-GXP-003 (DEC-GXP-015)
- **Acceptance Criteria**:
  - Given the 3D view, When the cartesian layout is chosen, Then no month ring is drawn And the node of greatest angle value has the greatest x
  - When the cylindrical layout is chosen, Then the positions of RQ-GXP-013 return
  - Given the cartesian layout, Then the indicator's axes read x, y and z with their dimensions
- **Dependencies**: TASK-GXP-020
- **Assignee**: AI
- **Verification**: `Cartesian3DTest` 3 tests failed first (KeyError, no layout hook), then OK; with `Indicator3DTest`, `Planes3DTest`, `Dimensions3DTest`: Ran 13 tests, OK. Full suite in TASK-GXP-023.
- **Assumptions**: each cartesian coordinate is (t - 0.5) × extent of its dimension, a category at its slot; the layout is kept across graphs, cylindrical by default; switching redraws the scene as a dimension choice does (ADR-GXP-003 rationale worded so); the cursor plane is kept in cartesian.

### TASK-GXP-022: Add 3D graduated trihedron
- **Tier**: M
- **Status**: Done
- **Description**: Write the tests first, then draw three graduated, labelled axes from the origin in the cartesian layout, toggled in the View menu, disabled in cylindrical; update the 3D help topic.
- **Requirement refs**: RQ-GXP-021, RQ-GXP-002
- **ADR refs**: ADR-GXP-003 (DEC-GXP-015)
- **Acceptance Criteria**:
  - Given the cartesian layout, Then three axes labelled with their dimensions are drawn
  - When the axes are unchecked, Then the trihedron is hidden
  - When the cylindrical layout is chosen, Then the axes choice is disabled
- **Dependencies**: TASK-GXP-021
- **Assignee**: AI
- **Verification**: `Trihedron3DTest` 3 tests failed first (KeyError, no trihedron hook), then OK (Ran 3 tests, OK). Full suite in TASK-GXP-023.
- **Assumptions**: the axes start at the cube's low corner; a number axis is graduated in 4 even steps (token), a date as YYYY-MM-DD, a category at each slot; shown by default, kept across graphs; the 3D help lives in the Graph topic (RQ-GXP-010), one item added there.

### TASK-GXP-023: Verify explorer 3D cartesian layout
- **Tier**: M
- **Status**: Done
- **Description**: Run the full graph suite with the timing tests, check the explorer on this repository's graph, update the changelog.
- **Requirement refs**: RQ-GXP-019, RQ-GXP-020, RQ-GXP-021
- **ADR refs**: ADR-GXP-003
- **Acceptance Criteria**:
  - Given this repository's graph, When Graph 3D is clicked in a headless browser, Then its first frame is drawn in less than 3 s
  - Given the graph suite, Then every test passes
- **Dependencies**: TASK-GXP-022
- **Assignee**: AI
- **Verification**: `agnos-graph` suite with `AGNOS_GRAPH_PERF=1`: Ran 278 tests in 238.6 s, OK, 0 skipped (RQ-GXP-019 first 3D frame test included). Screenshot of this repository's graph (2100 nodes) in cartesian layout: indicator labels clipped at the left edge and dozens of trigram graduations, both fixed (labels kept inside the canvas, at most 12 category graduations, token); the 8 3D test classes rerun after the fix: Ran 25 tests, OK. Changelog shortened to delivery entries on the owner's request.
- **Assumptions**: the full suite ran partly before the two display fixes, hence the 3D classes rerun after them.

### TASK-GXP-024: Scale 3D dates on the period
- **Tier**: L
- **Status**: Done
- **Description**: Write the tests first, then normalise the 3D date dimensions and month rings over the selected period, redrawn when the period changes; add RQ-GXP-022 and DEC-GXP-016.
- **Requirement refs**: RQ-GXP-022
- **ADR refs**: ADR-GXP-003 (DEC-GXP-016)
- **Acceptance Criteria**:
  - Given height by first commit date And the period from 2026-10-01, Then the only ring is 2026-11 at its height in the period And every shown point lies within the cylinder
  - When the whole history is selected again, Then the former positions return
- **Dependencies**: TASK-GXP-023
- **Assignee**: AI
- **Verification**: `PeriodScale3DTest` 2 tests failed first (rings 2026-08 to 2026-11, positions unmoved), then OK; a first version scaling the whole history on calendar days failed 2 `Planes3DTest` tests, so without a period the scale stays the first to last commit; `PeriodScale3DTest`, `Planes3DTest`, `Dimensions3DTest`, `Trihedron3DTest`, `Cartesian3DTest`: Ran 15 tests, OK. Full suite with `AGNOS_GRAPH_PERF=1`: Ran 280 tests, 0 skipped, 1 failure, `test_RQ_GXP_019_..._less_than_3_s` (first 3D frame, under the suite's load); that test alone: 3 runs OK. The change runs on a period change only, not on the first 3D show.
- **Assumptions**: the owner's screenshot answered the task's presentation; the scale follows the period, not the playback cursor; outside dates clamped to the period's ends.

### TASK-GXP-025: Name cartesian dimension choices
- **Tier**: M
- **Status**: Done
- **Description**: Write the tests first, then name the toolbar's height, angle and radius choices and the Dimensions menu items X, Y, Z in the X, Y, Z order in cartesian, back to Height, Angle, Radius in cylindrical; amend RQ-GXP-021.
- **Requirement refs**: RQ-GXP-021, RQ-GXP-013
- **ADR refs**: ADR-GXP-003 (DEC-GXP-015)
- **Acceptance Criteria**:
  - Given the cartesian layout, Then the toolbar and the Dimensions menu read X, Y, Z, Colour, Size
  - When the cylindrical layout is chosen, Then they read Height, Angle, Radius, Colour, Size again
- **Dependencies**: TASK-GXP-021
- **Assignee**: AI
- **Verification**: `AxisNames3DTest` failed first (toolbar read Height|Angle|Radius in cartesian), then OK; `test_explorer`: Ran 112 tests, OK, 2 skipped (RQ-TRC-158 and RQ-GXP-019 load times, need AGNOS_GRAPH_PERF=1; this change touches neither first view).
- **Assumptions**: the choices keep their roles and values across layouts (X = angle, Y = height, Z = radius, DEC-GXP-015); a menu item takes the name of its place's role when its menu opens.
