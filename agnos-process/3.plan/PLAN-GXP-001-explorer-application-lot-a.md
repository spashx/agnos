# PLAN-GXP-001: Explorer application with time and colours

## Overview
Lot A of FTR-GXP-001: the explorer's menu bar, the help dialog copied from the performance center, the reader's relation
colours, the time period filter and its playback, on the existing views. Lot B (the 3D view, RQ-GXP-010 to RQ-GXP-019) takes
a plan of its own in a later session.

## References
- **Requirement refs**: RQ-GXP-001, RQ-GXP-002, RQ-GXP-003, RQ-GXP-004, RQ-GXP-005, RQ-GXP-006, RQ-GXP-007, RQ-GXP-008, RQ-GXP-009, RQ-TRC-158
- **ADR refs**: ADR-GXP-001 (DEC-GXP-001 to DEC-GXP-006); ADR-TRC-025; design system ADR-TRC-002 (DEC-TRC-009, DEC-TRC-010), RQ-TRC-018
- **Requirements handed to another component**: None; every change stays in `agnos-graph` (its explorer assets, `graph.py`'s `@APP_VERSION@` marker). RQ-TRC-165 (legend) keeps its statement: the legend draws the colours the graph draws.

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-GXP-001: Document graph explorer application
- **Tier**: L
- **Status**: Done
- **Description**: Write FTR-GXP-001 (RQ-GXP-001 to RQ-GXP-019), ADR-GXP-001 and this plan.
- **Requirement refs**: RQ-GXP-001 to RQ-GXP-019
- **ADR refs**: ADR-GXP-001
- **Acceptance Criteria**:
  - Given the index rebuilt, Then FTR-GXP-001, RQ-GXP-001 to RQ-GXP-019, ADR-GXP-001, DEC-GXP-001 to DEC-GXP-006 and TASK-GXP-001 to TASK-GXP-007 are listed
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `agnos-index` run after writing; see the commit.
- **Assumptions**: owner's decisions of 2026-11-24 (flat tabs, two lots, hand-written orbit, 3D without history, node colours kept, help copied); the sliding window kept as Should; the owner let the agent proceed autonomously.

### TASK-GXP-002: Add explorer menu bar
- **Tier**: M
- **Status**: Done
- **Description**: Write the Gherkin-named tests first, then replace the header's file button by a menu bar File, View, Filter and Help, with the existing actions (open graph, saved queries import and export, tabs, show all, layouts).
- **Requirement refs**: RQ-GXP-001, RQ-TRC-164
- **ADR refs**: ADR-GXP-001 (DEC-GXP-001)
- **Acceptance Criteria**:
  - Given the explorer, When File is clicked, Then "Open graph file…", "Import saved queries…" and "Export saved queries…" are listed
  - Given an open menu, When the right arrow key is pressed, Then the next menu opens; When Escape is pressed, Then it closes
  - Given every menu item, Then it has a non-empty tooltip
- **Dependencies**: TASK-GXP-001
- **Assignee**: AI
- **Verification**: `MenuBarTest` 4 tests failed first (KeyError, no menu bar), then OK; with the impacted `ExplorerTokensTest`, `test_RQ_TRC_164`, `test_RQ_TRC_145`: 13 OK, 0 skipped. Screenshot of this repository's explorer: File, View, Filter beside the mark, View open.
- **Assumptions**: Help joins the bar with TASK-GXP-003 (RQ-GXP-001: an undelivered menu is absent); layouts stay in the toolbar and the context menu, not duplicated in View.

### TASK-GXP-003: Add explorer help dialog
- **Tier**: M
- **Status**: Not Started
- **Description**: Write the tests first, then copy the performance center's help dialog, licence badges and About into the explorer, with topics of the existing views, and the `@APP_VERSION@` marker in `graph.py`.
- **Requirement refs**: RQ-GXP-002, RQ-GXP-003, RQ-GXP-004
- **ADR refs**: ADR-GXP-001 (DEC-GXP-002)
- **Acceptance Criteria**:
  - Given the Nodes tab, When Help is opened, Then the topic Nodes is shown
  - Given the Licenses topic, Then badges read AGNOS AGPL-3.0 and Cytoscape.js 3.30.2 MIT
  - Given a version file, Then About reads "AGNOS v.<major>.<minor>"; Given none, Then "AGNOS"
- **Dependencies**: TASK-GXP-002
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-GXP-004: Add relation colour choice
- **Tier**: M
- **Status**: Not Started
- **Description**: Write the tests first, then add the Appearance menu and the legend's colour choice per relation kind, kept in the browser, with "Reset colours", and its help topic.
- **Requirement refs**: RQ-GXP-005, RQ-TRC-165
- **ADR refs**: ADR-GXP-001 (DEC-GXP-005)
- **Acceptance Criteria**:
  - Given the graph view, When `code` is given a colour, Then its edges and legend line take it And keep it after a reload
  - When "Reset colours" is chosen, Then the token colour is back
- **Dependencies**: TASK-GXP-003
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-GXP-005: Add time period filter
- **Tier**: M
- **Status**: Not Started
- **Description**: Write the tests first, then date the nodes from the history, add the time bar with start and end handles and the Time menu, apply the period in `isShown`, disable it without history, and write its help topic.
- **Requirement refs**: RQ-GXP-006, RQ-GXP-009
- **ADR refs**: ADR-GXP-001 (DEC-GXP-003, DEC-GXP-004)
- **Acceptance Criteria**:
  - Given a graph with history, When the period is narrowed, Then the tables and the graph show only the nodes dated in it
  - Given a node without history rows, Then it is dated `limits.first`
  - Given a graph without history, Then no time bar is shown And the Time menu is disabled with a tooltip naming `--history`
- **Dependencies**: TASK-GXP-004
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-GXP-006: Add time playback loop
- **Tier**: M
- **Status**: Not Started
- **Description**: Write the tests first, then add Play, Pause, Stop, Loop, the speed and the window mode to the time bar and the Time menu, driven by animation frames, and complete the Time help topic.
- **Requirement refs**: RQ-GXP-007, RQ-GXP-008
- **ADR refs**: ADR-GXP-001 (DEC-GXP-006)
- **Acceptance Criteria**:
  - Given a period, When Play is pressed, Then the shown count grows to the end; Given Loop, Then it starts again
  - When Pause is pressed, Then the cursor stays; When Stop is pressed, Then the whole period is shown
  - Given the window mode of 7 days, Then only the nodes of the last 7 days before the cursor are shown
- **Dependencies**: TASK-GXP-005
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-GXP-007: Verify explorer application lot A
- **Tier**: M
- **Status**: Not Started
- **Description**: Run the graph skill's whole suite once, build the explorer on this repository and the demo, check RQ-TRC-158's load time, and add the changelog entry.
- **Requirement refs**: RQ-GXP-001 to RQ-GXP-009, RQ-TRC-158
- **ADR refs**: ADR-GXP-001
- **Acceptance Criteria**:
  - Given the graph skill's tests, Then all pass, skipped ones stated with their cause
  - Given this repository's graph, Then the first view is drawn in less than 5 s
- **Dependencies**: TASK-GXP-006
- **Assignee**: AI
- **Verification**:
- **Assumptions**:
