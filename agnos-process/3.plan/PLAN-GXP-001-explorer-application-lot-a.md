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
  - Given the explorer, When File is clicked, Then "Open graph fileâ€¦", "Import saved queriesâ€¦" and "Export saved queriesâ€¦" are listed
  - Given an open menu, When the right arrow key is pressed, Then the next menu opens; When Escape is pressed, Then it closes
  - Given every menu item, Then it has a non-empty tooltip
- **Dependencies**: TASK-GXP-001
- **Assignee**: AI
- **Verification**: `MenuBarTest` 4 tests failed first (KeyError, no menu bar), then OK; with the impacted `ExplorerTokensTest`, `test_RQ_TRC_164`, `test_RQ_TRC_145`: 13 OK, 0 skipped. Screenshot of this repository's explorer: File, View, Filter beside the mark, View open.
- **Assumptions**: Help joins the bar with TASK-GXP-003 (RQ-GXP-001: an undelivered menu is absent); layouts stay in the toolbar and the context menu, not duplicated in View.

### TASK-GXP-003: Add explorer help dialog
- **Tier**: M
- **Status**: Done
- **Description**: Write the tests first, then copy the performance center's help dialog, licence badges and About into the explorer, with topics of the existing views, and the `@APP_VERSION@` marker in `graph.py`.
- **Requirement refs**: RQ-GXP-002, RQ-GXP-003, RQ-GXP-004
- **ADR refs**: ADR-GXP-001 (DEC-GXP-002)
- **Acceptance Criteria**:
  - Given the Nodes tab, When Help is opened, Then the topic Nodes is shown
  - Given the Licenses topic, Then badges read AGNOS AGPL-3.0 and Cytoscape.js 3.30.2 MIT
  - Given a version file, Then About reads "AGNOS v.<major>.<minor>"; Given none, Then "AGNOS"
- **Dependencies**: TASK-GXP-002
- **Assignee**: AI
- **Verification**: `HelpDialogTest` 6 tests and the amended menu test failed first (7: 2 failures, 5 errors), then OK; with the impacted `MenuBarTest`, `ExplorerTokensTest`, `ExplorerFilesTest`, `test_RQ_TRC_164`: 20 OK, 0 skipped. Screenshot of this repository's explorer: About reads "AGNOS v.4.0" with the tagline and both links.
- **Assumptions**: the marker is filled by `explorer.py`, which `graph.py` calls (DEC-GXP-002 says `graph.py`); the libraries reach the page as a JSON record (`@LIBRARY_RECORD@`), the performance center's come from its data; MenuBarTest's menu list amended to add Help, the behaviour RQ-GXP-001 states.

### TASK-GXP-004: Add relation colour choice
- **Tier**: M
- **Status**: Done
- **Description**: Write the tests first, then add the Appearance menu and the legend's colour choice per relation kind, kept in the browser, with "Reset colours", and its help topic.
- **Requirement refs**: RQ-GXP-005, RQ-TRC-165
- **ADR refs**: ADR-GXP-001 (DEC-GXP-005)
- **Acceptance Criteria**:
  - Given the graph view, When `code` is given a colour, Then its edges and legend line take it And keep it after a reload
  - When "Reset colours" is chosen, Then the token colour is back
- **Dependencies**: TASK-GXP-003
- **Assignee**: AI
- **Verification**: `RelationColourTest` 4 tests and the amended menu and help lists failed first (6: 2 failures, 4 errors), then OK; with the impacted legend, menu, help, tooltip, relation-kind, type-colour and raw-value tests: 19 OK, 0 skipped.
- **Assumptions**: the browser's own colour picker (`input type=color`) is the chooser; a reload is tested by re-reading the store (`appearance.load()`), as the saved queries are; the menu and help lists of TASK-GXP-002 and TASK-GXP-003 amended to add Appearance.

### TASK-GXP-005: Add time period filter
- **Tier**: M
- **Status**: Done
- **Description**: Write the tests first, then date the nodes from the history, add the time bar with start and end handles and the Time menu, apply the period in `isShown`, disable it without history, and write its help topic.
- **Requirement refs**: RQ-GXP-006, RQ-GXP-009
- **ADR refs**: ADR-GXP-001 (DEC-GXP-003, DEC-GXP-004)
- **Acceptance Criteria**:
  - Given a graph with history, When the period is narrowed, Then the tables and the graph show only the nodes dated in it
  - Given a node without history rows, Then it is dated `limits.first`
  - Given a graph without history, Then no time bar is shown And the Time menu is disabled with a tooltip naming `--history`
- **Dependencies**: TASK-GXP-004
- **Assignee**: AI
- **Verification**: `TimePeriodTest` (4), `TimePeriodGraphTest` (1) and the amended menu and help lists failed first (7: 2 failures, 5 errors), then OK; with the impacted menu, help, tooltip, model, query, facet, selection and token tests: 37 OK, 0 skipped. Screenshot of this repository's explorer: period 2026-09-01 â†’ 2026-11-10, 3117 / 4905 nodes shown.
- **Assumptions**: days are UTC days from the history's first day; a handle dragged past the other pushes it; sections and undefined IDs, which have no rows, are dated `limits.first` as DEC-GXP-004 states; the tests load a graph written by the test, whose dates are known.

### TASK-GXP-006: Add time playback loop
- **Tier**: M
- **Status**: Done
- **Description**: Write the tests first, then add Play, Pause, Stop, Loop, the speed and the window mode to the time bar and the Time menu, driven by animation frames, and complete the Time help topic.
- **Requirement refs**: RQ-GXP-007, RQ-GXP-008
- **ADR refs**: ADR-GXP-001 (DEC-GXP-006)
- **Acceptance Criteria**:
  - Given a period, When Play is pressed, Then the shown count grows to the end; Given Loop, Then it starts again
  - When Pause is pressed, Then the cursor stays; When Stop is pressed, Then the whole period is shown
  - Given the window mode of 7 days, Then only the nodes of the last 7 days before the cursor are shown
- **Dependencies**: TASK-GXP-005
- **Assignee**: AI
- **Verification**: `TimePlaybackTest` 5 tests failed first (5 errors), then OK; with the impacted time, menu, help, tooltip, token, facet, selection and model tests: 32 OK, 0 skipped; after the day fix below, the time, menu, tooltip and raw-value tests: 16 OK, 0 skipped. Screenshot of this repository's explorer during playback: Pause, Stop, Loop, 7 days/s, Cumulative, the cursor on the track, 675 / 4927 nodes.
- **Assumptions**: `t.advance(s)` moves the playback as the frames of s seconds would, so that the tests know each step; Pause and Play share one button; at the end with Loop the cursor starts again from the period's first day; the screenshot showed the track squeezed, now on its own row, and a first day of 2026-07-13 for a commit of 2026-07-14 01:06 +02:00: the days of TASK-GXP-005 are now the reader's calendar days, not UTC days.

### TASK-GXP-007: Verify explorer application lot A
- **Tier**: M
- **Status**: Done
- **Description**: Run the graph skill's whole suite once, build the explorer on this repository and the demo, check RQ-TRC-158's load time, and add the changelog entry.
- **Requirement refs**: RQ-GXP-001 to RQ-GXP-009, RQ-TRC-158
- **ADR refs**: ADR-GXP-001
- **Acceptance Criteria**:
  - Given the graph skill's tests, Then all pass, skipped ones stated with their cause
  - Given this repository's graph, Then the first view is drawn in less than 5 s
- **Dependencies**: TASK-GXP-006
- **Assignee**: AI
- **Verification**: `agnos-graph` suite with `AGNOS_GRAPH_PERF=1`: Ran 246 tests in 157.4 s, OK, 0 skipped; RQ-TRC-158 test ok. No other component reads the explorer's assets (`git grep`: CHANGELOG only). Explorer built on this repository and on the demo (84 elements, 452 nodes, 83 commits): playback shows 256 / 452 nodes at 2026-09-21. Changelog entry added.
- **Assumptions**: the demo's explorer is written to a scratch folder, the demo repository left unchanged.

### TASK-GXP-008: Align explorer header date
- **Tier**: M
- **Status**: Done
- **Description**: Show the generation time in the header as the performance center does (reader's date and time, UTC in a tooltip) and drop the commit, the graph being read from the working tree; amend RQ-TRC-145.
- **Requirement refs**: RQ-TRC-145
- **ADR refs**: ADR-TRC-025
- **Acceptance Criteria**:
  - Given the explorer, Then the header reads "Generated" and the date in the reader's format, its tooltip the UTC value, and no commit
- **Dependencies**: TASK-GXP-007
- **Assignee**: AI
- **Verification**: header test rewritten for the amended RQ-TRC-145, with the RQ-TRC-145 and raw-value tests: 5 OK, 0 skipped.
- **Assumptions**: the owner's review of 2026-11-25 ("mÃªme format que le perf center", "le graph n'est pas liÃ© Ã  un commit"); the counts stay.

### TASK-GXP-010: Delay period refresh during drag
- **Tier**: M
- **Status**: Done
- **Description**: While a time handle is dragged, move only the bar, its fill and its dates; refresh the views once the handle rests for a token's delay or is released.
- **Requirement refs**: RQ-GXP-006
- **ADR refs**: ADR-GXP-001 (DEC-GXP-003)
- **Acceptance Criteria**:
  - Given a handle dragged to 2026-11-01, Then its dates show 2026-11-01 at once And the views keep their nodes until the handle rests
- **Dependencies**: TASK-GXP-009
- **Assignee**: AI
- **Verification**: new test failed first (views refreshed at once), then failed on the label still showing the applied period, fixed to follow the handles; time and token tests: 16 OK, 0 skipped.
- **Assumptions**: 400 ms of rest (token `motion.time-settle`); releasing the handle applies the period at once; before this task every move refreshed every view.

### TASK-GXP-009: Rearrange explorer header and time bar
- **Tier**: M
- **Status**: Done
- **Description**: Move the generation time to the right beside the help and drop its counts, set the menus apart, and put the time track on the controls' row; amend RQ-TRC-145 again.
- **Requirement refs**: RQ-TRC-145, RQ-GXP-001, RQ-GXP-006
- **ADR refs**: ADR-GXP-001 (DEC-GXP-001, DEC-GXP-003)
- **Acceptance Criteria**:
  - Given the explorer, Then the header's date stands beside the help button And holds no count
  - Given the time bar, Then its track is on the controls' row, right of the mode
- **Dependencies**: TASK-GXP-008
- **Assignee**: AI
- **Verification**: header and time-bar tests rewritten or added, with the impacted time, header and token tests: 23 OK, 0 skipped; after narrowing the track minimum, 19 OK, 0 skipped. Screenshots: date beside the help, semibold menus after a rule; at 1600 px the track shares the controls' row.
- **Assumptions**: the owner's review of 2026-11-25; "plus en Ã©vidence" read as semibold titles set apart from the mark by a rule; the track wraps under the controls below 120 px, as on a window of 1400 px or less.
