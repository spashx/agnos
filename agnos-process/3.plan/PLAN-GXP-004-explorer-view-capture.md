# PLAN-GXP-004: Explorer saved views with image export

## Overview
Lot B2 of FTR-GXP-001: the reader saves the current view under a name, restores it, exports and imports the saved views as
a JSON file, and saves the current graph view, 2D or 3D, as a PNG image. RQ-GXP-018 (presentation mode) was cancelled by
the owner on 2026-11-27 and takes no task.

## References
- **Requirement refs**: RQ-GXP-016, RQ-GXP-017, RQ-GXP-001, RQ-GXP-002
- **ADR refs**: ADR-GXP-004 (DEC-GXP-017 to DEC-GXP-019); ADR-GXP-001; ADR-GXP-002; ADR-TRC-025; design system ADR-TRC-002 (DEC-TRC-009, DEC-TRC-010), RQ-TRC-018
- **Requirements handed to another component**: None; every change stays in `agnos-graph`'s explorer assets and tests. RQ-GXP-001's File menu and RQ-GXP-002's help topics gain items without a change to their statements.

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-GXP-026: Document explorer view capture
- **Tier**: L
- **Status**: Done
- **Description**: Write ADR-GXP-004 and this plan; mark RQ-GXP-018 cancelled.
- **Requirement refs**: RQ-GXP-016, RQ-GXP-017, RQ-GXP-018
- **ADR refs**: ADR-GXP-004
- **Acceptance Criteria**:
  - Given the index rebuilt, Then ADR-GXP-004, DEC-GXP-017 to DEC-GXP-019, PLAN-GXP-004 and TASK-GXP-026 to TASK-GXP-029 are listed with no duplicate
  - Given FTR-GXP-001, Then RQ-GXP-018 is still defined And its priority reads Won't
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `agnos-index`: 1229 entries, 191 documents, exit 0, no duplicate; ADR-GXP-004, DEC-GXP-017 to 019, PLAN-GXP-004, TASK-GXP-026 to 029 listed; RQ-GXP-018 still listed (185-193), its Priority reads Won't. No test (documents only).
- **Assumptions**: owner's choices of 2026-11-27: RQ-GXP-018 cancelled and kept defined; inferred: the saved view also keeps the 3D layout and orbit, part of what the projection shows; the 3D image carries its HTML labels; saved views apart from the saved query buttons. Owner, 2026-11-27: views in `localStorage` with export and import as the saved queries, no project file; both exports through a save dialog remembering its folder (DEC-GXP-017); ADR-GXP-004 accepted.

### TASK-GXP-027: Add saved explorer views
- **Tier**: M
- **Status**: Done
- **Description**: Write the tests first, then save the current view under a name from the File menu, list the saved views there, restore one through the explorer's setters, and export and import them as a JSON file, the views' and the saved queries' export opening a save dialog that remembers its folder where the browser offers it; add the help topic's lines.
- **Requirement refs**: RQ-GXP-016, RQ-GXP-001, RQ-GXP-002
- **ADR refs**: ADR-GXP-004 (DEC-GXP-017, DEC-GXP-018)
- **Acceptance Criteria**:
  - Given the 3D view in isometric projection with a period, a query and a hidden node, When the view is saved, the page reloaded and the view opened, Then the same tab, projection, period, query and shown nodes are restored
  - Given saved views exported to a file, When the store is emptied and the file imported, Then the same views are listed
  - Given a saved view hiding a node the loaded graph lacks, When it is opened, Then the other values are restored And no error is raised
  - Given a browser offering `showSaveFilePicker`, When the views or the saved queries are exported, Then a save dialog opens with the last folder chosen; Given one without it, Then the file is downloaded
- **Dependencies**: TASK-GXP-026
- **Assignee**: AI
- **Verification**: `SavedViewsTest` 5 tests failed first (`views` undefined), then OK; re-run in review: `SavedViewsTest`, `MenuBarTest`: Ran 9 tests, OK, 0 skipped; neighbouring classes (SavedQueries, HelpDialog, Projection3D, RelationColour, ExplorerPage/Files/Tokens): Ran 49 tests, OK, 0 skipped; `test_literals.py` OK; `node --check explorer.js` OK. `MenuBarTest`'s File items test updated for the three new items (new behaviour, RQ-GXP-016).
- **Assumptions**: implemented by a subagent, reviewed by the session agent; the name asked with `window.prompt`; a name already saved is replaced; no delete; the help lines in the Overview topic, the help having no File topic; Export views disabled with no view; a restored preset resets the orbit angles, then the saved orbit applies.

### TASK-GXP-028: Add graph image export
- **Tier**: M
- **Status**: Done
- **Description**: Write the tests first, then add "Export image" to the File menu, saving the current 2D or 3D graph view as a PNG of the view's size, the 3D labels drawn over its canvas; disabled on the table views; add the help topic's line.
- **Requirement refs**: RQ-GXP-017, RQ-GXP-001, RQ-GXP-002
- **ADR refs**: ADR-GXP-004 (DEC-GXP-019)
- **Acceptance Criteria**:
  - Given the 3D view, When "Export image" is chosen, Then a PNG file of the view's width and height is saved
  - Given the 2D view, When "Export image" is chosen, Then a PNG file of the view's width and height is saved
  - Given the Nodes view, Then "Export image" is disabled
- **Dependencies**: TASK-GXP-026
- **Assignee**: AI
- **Verification**: `ImageExportTest` 4 tests failed first (no item, no hooks), then OK; one targeted fix after a batch failure (3D PNG encoded asynchronously after the headless dump: now `toDataURL`, size read from the PNG header); ImageExport, MenuBar, HelpDialog, SavedViews, SavedQueries: Ran 25 tests, OK, 0 skipped; re-run in review: ImageExport, MenuBar, SavedViews: Ran 13 tests, OK; `test_literals.py` OK. `MenuBarTest`'s File items updated for Export image (new behaviour).
- **Assumptions**: implemented by a subagent, reviewed by the session agent; the PNG at the view's CSS size, without the screen's pixel ratio; 2D background `--c-graph-bg`; the 3D labels drawn with their computed font and colour; `saveText` generalised to `saveBlob`.

### TASK-GXP-029: Verify explorer view capture
- **Tier**: M
- **Status**: Not Started
- **Description**: Run the full graph suite, open the explorer on this repository and the demo, and add the changelog entry.
- **Requirement refs**: RQ-GXP-016, RQ-GXP-017, RQ-GXP-019
- **ADR refs**: ADR-GXP-004
- **Acceptance Criteria**:
  - Given the full graph suite with `AGNOS_GRAPH_PERF=1`, Then every test passes or each failure is reported with its cause
  - Given the explorer written on this repository and on the demo, When a view is saved and an image exported, Then both work
  - Given CHANGELOG.md, Then its Unreleased section has one user-facing entry for saved views and image export
- **Dependencies**: TASK-GXP-027, TASK-GXP-028
- **Assignee**: AI
- **Verification**:
- **Assumptions**:
