# PLAN-GXP-003: Explorer 3D cartesian layout with axis indicator

## Overview
The 3D view's axis indicator in its bottom left corner, and a cartesian layout with a graduated trihedron, each toggled in
the View menu, before lot B2 (RQ-GXP-016 to RQ-GXP-018).

## References
- **Requirement refs**: RQ-GXP-020, RQ-GXP-021, RQ-GXP-002, RQ-GXP-019
- **ADR refs**: ADR-GXP-003 (DEC-GXP-014, DEC-GXP-015); ADR-GXP-002; design system ADR-TRC-002 (DEC-TRC-009, DEC-TRC-010), RQ-TRC-018
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
- **Status**: Not Started
- **Description**: Write the tests first, then draw the axis indicator in a bottom left viewport following the camera, labelled from the dimensions, toggled in the View menu.
- **Requirement refs**: RQ-GXP-020
- **ADR refs**: ADR-GXP-003 (DEC-GXP-014)
- **Acceptance Criteria**:
  - Given the 3D view, Then the indicator is shown And its height axis reads the first commit date
  - When the height is set to the changed lines, Then the indicator's height axis reads the changed lines
  - When the axis indicator is unchecked, Then the indicator is hidden
- **Dependencies**: TASK-GXP-019
- **Assignee**: AI
- **Verification**: pending
- **Assumptions**: pending

### TASK-GXP-021: Add 3D cartesian layout
- **Tier**: M
- **Status**: Not Started
- **Description**: Write the tests first, then add the cylindrical and cartesian layout choice to the View menu, placing points at x, y, z from the angle, height and radius values, rings and angle labels hidden in cartesian.
- **Requirement refs**: RQ-GXP-021, RQ-GXP-020
- **ADR refs**: ADR-GXP-003 (DEC-GXP-015)
- **Acceptance Criteria**:
  - Given the 3D view, When the cartesian layout is chosen, Then no month ring is drawn And the node of greatest angle value has the greatest x
  - When the cylindrical layout is chosen, Then the positions of RQ-GXP-013 return
  - Given the cartesian layout, Then the indicator's axes read x, y and z with their dimensions
- **Dependencies**: TASK-GXP-020
- **Assignee**: AI
- **Verification**: pending
- **Assumptions**: pending

### TASK-GXP-022: Add 3D graduated trihedron
- **Tier**: M
- **Status**: Not Started
- **Description**: Write the tests first, then draw three graduated, labelled axes from the origin in the cartesian layout, toggled in the View menu, disabled in cylindrical; update the 3D help topic.
- **Requirement refs**: RQ-GXP-021, RQ-GXP-002
- **ADR refs**: ADR-GXP-003 (DEC-GXP-015)
- **Acceptance Criteria**:
  - Given the cartesian layout, Then three axes labelled with their dimensions are drawn
  - When the axes are unchecked, Then the trihedron is hidden
  - When the cylindrical layout is chosen, Then the axes choice is disabled
- **Dependencies**: TASK-GXP-021
- **Assignee**: AI
- **Verification**: pending
- **Assumptions**: pending

### TASK-GXP-023: Verify explorer 3D cartesian layout
- **Tier**: M
- **Status**: Not Started
- **Description**: Run the full graph suite with the timing tests, check the explorer on this repository's graph, update the changelog.
- **Requirement refs**: RQ-GXP-019, RQ-GXP-020, RQ-GXP-021
- **ADR refs**: ADR-GXP-003
- **Acceptance Criteria**:
  - Given this repository's graph, When Graph 3D is clicked in a headless browser, Then its first frame is drawn in less than 3 s
  - Given the graph suite, Then every test passes
- **Dependencies**: TASK-GXP-022
- **Assignee**: AI
- **Verification**: pending
- **Assumptions**: pending
