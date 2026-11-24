# PLAN-GXP-002: Explorer 3D view with dimensions

## Overview
Lot B1 of FTR-GXP-001: the flat tabs, the Graph 3D view drawn with three.js, its interaction, dimensions, projections and
reference planes, and its draw time. RQ-GXP-016 to RQ-GXP-018 take a plan of their own in a later session.

## References
- **Requirement refs**: RQ-GXP-010, RQ-GXP-011, RQ-GXP-012, RQ-GXP-013, RQ-GXP-014, RQ-GXP-015, RQ-GXP-019, RQ-GXP-003, RQ-TRC-158
- **ADR refs**: ADR-GXP-002 (DEC-GXP-007 to DEC-GXP-013); ADR-GXP-001; ADR-TRC-025; design system ADR-TRC-002 (DEC-TRC-009, DEC-TRC-010), RQ-TRC-018
- **Requirements handed to another component**: None; every change stays in `agnos-graph`'s explorer assets and tests. RQ-GXP-003 (licence list) gains the three.js row in TASK-GXP-012.

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-GXP-011: Document explorer 3D view
- **Tier**: L
- **Status**: Done
- **Description**: Write ADR-GXP-002 and this plan.
- **Requirement refs**: RQ-GXP-010 to RQ-GXP-015, RQ-GXP-019
- **ADR refs**: ADR-GXP-002
- **Acceptance Criteria**:
  - Given the index rebuilt, Then ADR-GXP-002, DEC-GXP-007 to DEC-GXP-013, PLAN-GXP-002 and TASK-GXP-011 to TASK-GXP-018 are listed
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `agnos-index`: 1200 entries, 186 documents, no duplicate; ADR-GXP-002, DEC-GXP-007 to 013, PLAN-GXP-002, TASK-GXP-011 to 018 listed. No test (documents only).
- **Assumptions**: owner's choices of 2026-11-25: three.js from cdnjs, scope B1.

### TASK-GXP-012: Add flat tabs with lazy three.js
- **Tier**: L
- **Status**: Done
- **Description**: Write the tests first, then rename the Graph tab to Graph 2D, add a Graph 3D tab and panel, and record three.js in `libraries.json` and the licence list, loaded on the tab's first show.
- **Requirement refs**: RQ-GXP-010, RQ-GXP-003, RQ-GXP-019
- **ADR refs**: ADR-GXP-002 (DEC-GXP-007)
- **Acceptance Criteria**:
  - Given the explorer, Then four tabs read Graph 2D, Graph 3D, Nodes and Relations
  - Given the page loaded, When Graph 3D was never shown, Then three.js is not loaded
  - Given the help dialog, Then the licence list shows three.js, MIT
- **Dependencies**: TASK-GXP-011
- **Assignee**: AI
- **Verification**: `FlatTabsTest` 4 tests failed first (StopIteration, tabs `Graph|Nodes|Relations`, no badge), then OK; `test_explorer` 83 tests OK, 1 skipped (RQ-TRC-158 load time, needs AGNOS_GRAPH_PERF=1, run in TASK-GXP-018). Two existing tests updated to the new expected behaviour: menu item `Graph 2D`, three.js badge.
- **Assumptions**: three.js 0.149.0, the last UMD build without the r150 deprecation warning; `lazy: true` in `libraries.json` marks a library loaded by the script; the 3D view opens the Graph help topic.

### TASK-GXP-013: Draw 3D points and lines
- **Tier**: L
- **Status**: Done
- **Description**: Write the tests first, then draw the shown nodes and relations in two buffers coloured by tokens and overrides, filtered by `isShown`, with the hand-written orbit controller.
- **Requirement refs**: RQ-GXP-011
- **ADR refs**: ADR-GXP-002 (DEC-GXP-008, DEC-GXP-009)
- **Acceptance Criteria**:
  - Given this repository's graph, When Graph 3D is shown, Then the shown point count equals the node table's row count
  - When type FN is unchecked, Then no function point is shown
  - When the view is dragged, Then the camera rotates around its target
- **Dependencies**: TASK-GXP-012
- **Assignee**: AI
- **Verification**: `View3DTest` 3 tests failed first (KeyError, no 3D hook), then OK; `test_explorer` 86 tests OK, 1 skipped (RQ-TRC-158, AGNOS_GRAPH_PERF, TASK-GXP-018). Screenshot of this repository's graph in Graph 3D: 4933 points, 22835 lines drawn.
- **Assumptions**: the fixture has no function, so type RQ stands for FN in the facet test; the test excludes elements of kind `undefined`, typed UNDEFINED by the model (owner's approval after Error Recovery, 2026-11-25); provisional placement (angle by trigram, radius by type layer, height by date or relation count) until TASK-GXP-015; pan by middle or Shift drag, right click left to RQ-GXP-012.

### TASK-GXP-014: Add 3D node interaction
- **Tier**: M
- **Status**: Done
- **Description**: Write the tests first, then pick the point under the pointer and reuse the selection, tooltip and node context menu of the 2D view.
- **Requirement refs**: RQ-GXP-012
- **ADR refs**: ADR-GXP-002 (DEC-GXP-010)
- **Acceptance Criteria**:
  - Given the 3D view, When a point is clicked, Then the detail panel shows its node
  - When the pointer rests on a point, Then its tooltip is shown after the delay
  - When a point is right-clicked And "Neighbours, 1 hop" is chosen, Then only it and its neighbours are shown
- **Dependencies**: TASK-GXP-013
- **Assignee**: AI
- **Verification**: `Interaction3DTest` 3 tests failed first (KeyError, no picker), then OK; `test_explorer` 89 tests OK, 1 skipped (RQ-TRC-158, AGNOS_GRAPH_PERF, TASK-GXP-018).
- **Assumptions**: pick radius 8 CSS px (token); the 3D context menu holds the node actions only, the layouts and Fit being the 2D view's; the tooltip and menu move into the shown graph panel.

### TASK-GXP-015: Add 3D dimensions menu
- **Tier**: M
- **Status**: Not Started
- **Description**: Write the tests first, then add the dimensions table and the Dimensions menu placing and drawing the points, with the defaults of RQ-GXP-013.
- **Requirement refs**: RQ-GXP-013, RQ-GXP-009
- **ADR refs**: ADR-GXP-002 (DEC-GXP-011)
- **Acceptance Criteria**:
  - Given the 3D view, When the height is set to the changed lines, Then the most changed nodes are the highest
  - Given a graph without history, Then the history's dimensions are disabled And the height defaults to the relation count
- **Dependencies**: TASK-GXP-013
- **Assignee**: AI
- **Verification**: pending
- **Assumptions**: pending

### TASK-GXP-016: Add 3D camera projections
- **Tier**: M
- **Status**: Not Started
- **Description**: Write the tests first, then add the perspective and orthographic cameras and the isometric, top, front and side presets to the View menu, points at a fixed screen size.
- **Requirement refs**: RQ-GXP-014
- **ADR refs**: ADR-GXP-002 (DEC-GXP-012)
- **Acceptance Criteria**:
  - Given the 3D view, When "Isometric" is chosen, Then two points of the same height share the same screen height
  - When "Top" is chosen, Then the camera looks down the height axis
- **Dependencies**: TASK-GXP-013
- **Assignee**: AI
- **Verification**: pending
- **Assumptions**: pending

### TASK-GXP-017: Add 3D reference planes
- **Tier**: M
- **Status**: Not Started
- **Description**: Write the tests first, then draw the month rings, the cursor's grid plane and the angle's labels, each toggled in the View menu.
- **Requirement refs**: RQ-GXP-015
- **ADR refs**: ADR-GXP-002 (DEC-GXP-013)
- **Acceptance Criteria**:
  - Given the 3D view with height by first commit date, Then a ring labelled 2026-08 lies at that month's height
  - When Play is pressed, Then the grid plane rises with the cursor
- **Dependencies**: TASK-GXP-015
- **Assignee**: AI
- **Verification**: pending
- **Assumptions**: pending

### TASK-GXP-018: Verify explorer lot B1
- **Tier**: M
- **Status**: Not Started
- **Description**: Time the first 3D frame and RQ-TRC-158's first view in a headless browser on this repository's graph, run the full graph suite, check the explorer on the repository and the demo, update the changelog.
- **Requirement refs**: RQ-GXP-019, RQ-TRC-158
- **ADR refs**: ADR-GXP-002
- **Acceptance Criteria**:
  - Given this repository's graph, When Graph 3D is clicked in a headless browser, Then its first frame is drawn in less than 3 s And the first view in less than 5 s
  - Given the graph suite, Then every test passes
- **Dependencies**: TASK-GXP-014, TASK-GXP-016, TASK-GXP-017
- **Assignee**: AI
- **Verification**: pending
- **Assumptions**: pending
