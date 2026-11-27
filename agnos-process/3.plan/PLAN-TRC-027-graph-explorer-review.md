# PLAN-TRC-027: Graph explorer review corrections

## Overview
The owner's review of the graph explorer (2026-11-23): resizable table columns, facet bulk selection, counts clear of
scrollbars, relation kind filter applied to the graph, automatic layouts, a context menu, labelled controls with tooltips and
a legend.

## References
- **Requirement refs**: RQ-TRC-151, RQ-TRC-159, RQ-TRC-160, RQ-TRC-161, RQ-TRC-162, RQ-TRC-163, RQ-TRC-164, RQ-TRC-165, RQ-TRC-166, RQ-TRC-167, RQ-TRC-156, RQ-TRC-158
- **ADR refs**: ADR-TRC-025 (DEC-TRC-090, DEC-TRC-094, DEC-TRC-095); design system ADR-TRC-002 (DEC-TRC-009, DEC-TRC-010), RQ-TRC-018
- **Requirements handed to another component**: None; every change stays in the explorer's assets of `agnos-graph`.

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-TRC-139: Document explorer review corrections
- **Tier**: M
- **Status**: Done
- **Description**: Add RQ-TRC-159 to RQ-TRC-165 to FTR-TRC-014, DEC-TRC-094 and DEC-TRC-095 to ADR-TRC-025, and this plan.
- **Requirement refs**: RQ-TRC-159, RQ-TRC-160, RQ-TRC-161, RQ-TRC-162, RQ-TRC-163, RQ-TRC-164, RQ-TRC-165
- **ADR refs**: ADR-TRC-025 (DEC-TRC-094, DEC-TRC-095)
- **Acceptance Criteria**:
  - Given the index rebuilt, Then RQ-TRC-159 to RQ-TRC-165, DEC-TRC-094, DEC-TRC-095 and TASK-TRC-139 to TASK-TRC-146 are listed
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: see the commit; `agnos-index` lists the new IDs.
- **Assumptions**: the owner approved the plan as presented in chat ("ok fait tout", 2026-11-23).

### TASK-TRC-140: Fix relation kind filter
- **Tier**: M
- **Status**: Done
- **Description**: Write the Gherkin-named test first, then hide in the graph view the relations an unchecked relation facet or a query excludes, and make the shown count follow them.
- **Requirement refs**: RQ-TRC-151
- **ADR refs**: ADR-TRC-025 (DEC-TRC-090)
- **Acceptance Criteria**:
  - Given the graph view, When `contains` is unchecked, Then no `contains` edge is shown in the graph And the relation count drops by their number
- **Dependencies**: TASK-TRC-139
- **Assignee**: AI
- **Verification**: probe before the fix, headless: the count already followed each kind (repository 11810 → 10358 without `contains`, 9370 without `code`, 3892 without `refs`), but `applyVisibility` hid nodes only, so every edge stayed drawn. Test `..._relation_kind_unchecked_...` failed first, then OK; `GraphViewTest` 7 OK, 0 skipped.
- **Assumptions**: the owner's "count does not change" was the drawn edges staying; the count needed no change.

### TASK-TRC-141: Add facet bulk selection
- **Tier**: M
- **Status**: Done
- **Description**: Write the tests first, then add "All" and "None" controls to each facet and reserve the scrollbar's room in the facet lists and the panel.
- **Requirement refs**: RQ-TRC-160, RQ-TRC-161
- **ADR refs**: ADR-TRC-025 (DEC-TRC-010)
- **Acceptance Criteria**:
  - Given the Node types facet, When "None" then "All" is clicked, Then no node then every node is shown
  - Given the Trigrams list with its scrollbar, Then every count ends left of the scrollbar
- **Dependencies**: TASK-TRC-140
- **Assignee**: AI
- **Verification**: `..._RQ_TRC_160_...` and `..._RQ_TRC_161_...` failed first (no `data-bulk`; panel `scrollbar-gutter: auto`), then OK; the RQ-TRC-160 test's stale fieldset reference was corrected (the facets are re-rendered), its expectations unchanged. `QueryLanguageTest` 11 OK, 0 skipped.
- **Assumptions**: tested on the Node types list made shorter than its values, the fixture holding one trigram; `scrollbar-gutter: stable` on the panel and every facet list.

### TASK-TRC-142: Implement resizable table columns
- **Tier**: M
- **Status**: Done
- **Description**: Write the test first, then add a drag handle to each table header, bounded by a minimum width token.
- **Requirement refs**: RQ-TRC-159
- **ADR refs**: ADR-TRC-025 (DEC-TRC-010)
- **Acceptance Criteria**:
  - Given the node table, When the Title header's edge is dragged, Then the column widens And keeps its width after a sort And never goes under the token's minimum
- **Dependencies**: TASK-TRC-139
- **Assignee**: AI
- **Verification**: `..._RQ_TRC_159_...` failed first (no handle), then 0 px wider (a fixed table of `width: auto`), then OK after the table width was set to the sum of its columns: +150 px, kept after a sort, 48 px minimum (`--c-table-column-min-width`). With `..._RQ_TRC_149_...`: 2 OK, 0 skipped.
- **Assumptions**: tokens `dimension.column-min` 48 px and `dimension.column-handle` 6 px; widths last as long as the page, not stored.

### TASK-TRC-143: Implement graph layouts and context menu
- **Tier**: M
- **Status**: Done
- **Description**: Write the tests first, then add a layout selector and a right-click menu with the layouts, fit, select, hide and neighbours at 1, 2 or 3 hops.
- **Requirement refs**: RQ-TRC-162, RQ-TRC-163
- **ADR refs**: ADR-TRC-025 (DEC-TRC-094, DEC-TRC-095)
- **Acceptance Criteria**:
  - Given the graph view, When "Circle" is chosen, Then the shown nodes are on a circle, in the view, And keep their positions after a filter change
  - Given a node right-clicked, When "Neighbours, 2 hops" is chosen, Then only the nodes at most two hops away are shown
  - Given the background right-clicked, Then the menu lists the layouts And no node action; When Escape is pressed, Then it closes
- **Dependencies**: TASK-TRC-140
- **Assignee**: AI
- **Verification**: 3 tests `..._RQ_TRC_162_...`, `..._RQ_TRC_163_...` failed first (no selector, no menu), then OK: circle spread < 1 % of its radius, all in view, position kept after a filter; "Neighbours, 2 hops" shows the same nodes as isolate then widen; background menu holds `layout:*` and no node action, Escape closes it. `GraphViewTest` 10 OK, 0 skipped.
- **Assumptions**: layouts Type columns (default), Grid, Circle, Concentric, Tree (`breadthfirst`), Force-directed (`cose`); a menu opened by a node's `cxttap` without pointer position opens at the view's centre.

### TASK-TRC-144: Label controls with tooltips
- **Tier**: M
- **Status**: Done
- **Description**: Write the test first, then replace the saved query tool symbols by words and give every control a tooltip.
- **Requirement refs**: RQ-TRC-164, RQ-TRC-155
- **ADR refs**: ADR-TRC-025 (DEC-TRC-093)
- **Acceptance Criteria**:
  - Given the buttons being edited, Then every button, tab, checkbox and field has a non-empty `title` And the tools read "Edit", "Move left", "Move right", "Delete"
- **Dependencies**: TASK-TRC-141, TASK-TRC-143
- **Assignee**: AI
- **Verification**: `..._RQ_TRC_164_...` failed first (file input, checkboxes, tools... untitled), then OK: 0 untitled control with the buttons edited and a node selected, tools "Edit|Move left|Move right|Delete". With `SavedQueriesTest`: 6 OK, 0 skipped.
- **Assumptions**: a tooltip is the `title` attribute; the menu items of TASK-TRC-143 already had theirs.

### TASK-TRC-145: Show graph legend
- **Tier**: M
- **Status**: Done
- **Description**: Write the test first, then draw a foldable legend over the graph view, of the node types and relation kinds present, from the graph's tokens.
- **Requirement refs**: RQ-TRC-165
- **ADR refs**: ADR-TRC-025 (DEC-TRC-090, DEC-TRC-091)
- **Acceptance Criteria**:
  - Given a graph with RQ and `contains`, Then the legend lists RQ with its colour And `contains` dashed; When folded, Then only its title stays
- **Dependencies**: TASK-TRC-140
- **Assignee**: AI
- **Verification**: `..._RQ_TRC_165_...` failed first (no legend), then OK: RQ swatch = `--s-type-rq`, `contains` line dashed in `--c-graph-edge-contains`, body `display: none` once folded, title kept. With `..._RQ_TRC_164_...` and `..._DEC_TRC_010_...`: 3 OK, 0 skipped.
- **Assumptions**: the legend sits over the graph's top left corner, with each type's and kind's count; token `dimension.legend-line` 24 px.

### TASK-TRC-146: Verify explorer review corrections
- **Tier**: M
- **Status**: Done
- **Description**: Run the graph skill's suite, check the graph is byte-identical with and without `--explorer` on this repository, time the first view, and add the changelog entry.
- **Requirement refs**: RQ-TRC-156, RQ-TRC-158
- **ADR refs**: ADR-TRC-025 (DEC-TRC-085)
- **Acceptance Criteria**:
  - Given this repository, When the graph is built with and without `--explorer`, Then both files are byte-identical
  - Given this repository's graph with call graph and history, When the explorer is opened headless, Then its first view is drawn in less than 5 s
- **Dependencies**: TASK-TRC-140, TASK-TRC-141, TASK-TRC-142, TASK-TRC-143, TASK-TRC-144, TASK-TRC-145, TASK-TRC-147
- **Assignee**: AI
- **Verification**: agnos-graph suite 218 tests OK, 1 skipped (`LoadTimeTest`, skipped unless `AGNOS_GRAPH_PERF=1`), then run with it: OK (first view < 5 s). `test_literals.py` of agnos-graph and agnos-perf-center: 2 OK each. This repository at a fixed date: graph byte-identical with and without `--explorer` (`cmp` silent, 1140 elements). CHANGELOG `[Unreleased]` Added and Fixed entries.
- **Assumptions**: the demo is not rebuilt: no change reaches the graph file nor the performance center.

### TASK-TRC-147: Explain undefined node type in detail
- **Tier**: S
- **Status**: Done
- **Description**: In the detail panel of an UNDEFINED node, say that its ID is cited with the prefix of a type but defined nowhere in the index (owner, 2026-11-23: ADR-ABC-010 shown UNDEFINED in the table, ADR in the detail).
- **Requirement refs**: RQ-TRC-146, RQ-TRC-154
- **ADR refs**: ADR-TRC-025 (DEC-TRC-089)
- **Acceptance Criteria**:
  - Given an undefined ADR ID selected, Then the detail reads that the ADR ID is cited but not defined in the index
- **Dependencies**: TASK-TRC-139
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: the UNDEFINED type is kept: the ID is no artifact, as the performance center classes it.

### TASK-TRC-148: Move graph legend to bottom band
- **Tier**: M
- **Status**: Done
- **Description**: Amend RQ-TRC-165, write the tests first, then lay the legend out as a wrapped horizontal band along the graph's bottom edge, as the performance center's, and test the undefined node note on a type other than ADR.
- **Requirement refs**: RQ-TRC-165, RQ-TRC-146
- **ADR refs**: ADR-TRC-025 (DEC-TRC-091)
- **Acceptance Criteria**:
  - Given the graph view, Then the legend's bottom edge is near the view's bottom And its items run in rows, left to right
  - Given an undefined TASK ID selected, Then the detail says a cited TASK ID is not defined in the index
- **Dependencies**: TASK-TRC-145, TASK-TRC-147
- **Assignee**: AI
- **Verification**: `..._legend_is_a_wrapped_band_along_its_bottom` failed first (368 px above the bottom), then OK (within 40 px, items in a row, wider than tall); `..._undefined_task_id_..._names_its_type_...` OK at once, as TASK-TRC-147's note reads any type's prefix. With the RQ-TRC-165 fold test: 3 OK, 0 skipped.
- **Assumptions**: RQ-TRC-165 amended with a dated comment; the band keeps the fold button first, then the types, then the kinds.

### TASK-TRC-149: Add layout direction choice
- **Tier**: L
- **Status**: Done
- **Description**: Add RQ-TRC-166, amend DEC-TRC-094, write the tests first, then add a direction selector that transposes the type columns, tree and grid layouts, disabled for the others.
- **Requirement refs**: RQ-TRC-166, RQ-TRC-162
- **ADR refs**: ADR-TRC-025 (DEC-TRC-094)
- **Acceptance Criteria**:
  - Given the type columns layout, When "Top to bottom" is chosen, Then the nodes of one type share one row And the types follow one another downwards
  - Given "Circle" chosen, Then the direction selector is disabled
- **Dependencies**: TASK-TRC-143
- **Assignee**: AI
- **Verification**: `..._RQ_TRC_166_...` failed first (no direction selector), then OK: in Top to bottom, RQ-DEM-001 and RQ-DEM-002 share a row, FTR above RQ above TASK; the selector is enabled for type columns, disabled for Circle. `GraphViewTest` and `..._RQ_TRC_164_...` 12 OK; full agnos-graph suite 221 OK, 1 skipped (`LoadTimeTest`, unless `AGNOS_GRAPH_PERF=1`); `test_literals` OK.
- **Assumptions**: natural directions: type columns and grid left to right, tree top to bottom; the other direction swaps x and y; DEC-TRC-094 amended in place (Tier L).

### TASK-TRC-150: Show node hover tooltip
- **Tier**: M
- **Status**: Done
- **Description**: Add RQ-TRC-167, write the test first, then show after the copied tooltip delay a tooltip of a hovered graph node's detail head and properties, sharing the detail panel's rendering.
- **Requirement refs**: RQ-TRC-167, RQ-TRC-154
- **ADR refs**: ADR-TRC-025 (DEC-TRC-090, DEC-TRC-010)
- **Acceptance Criteria**:
  - Given RQ-DEM-002 selected, When the pointer rests on RQ-DEM-001, Then no tooltip before the delay, then one listing RQ-DEM-001's detail properties, And the detail still shows RQ-DEM-002
  - When the pointer leaves the node, Then the tooltip is hidden
- **Dependencies**: TASK-TRC-147
- **Assignee**: AI
- **Verification**: `..._RQ_TRC_167_...` failed first (no tooltip), then OK: hidden at half the 1000 ms delay, shown after it with RQ-DEM-001's ID and the same property keys as its detail, detail still RQ-DEM-002, hidden on mouseout. Full agnos-graph suite: a first run reported 1 error not captured, then two runs 222 OK, 1 skipped (`LoadTimeTest`, unless `AGNOS_GRAPH_PERF=1`); `test_literals` OK.
- **Assumptions**: the tooltip holds the detail's head and every property, no relation nor action; it is placed right of and below the node, kept inside the view; tokens `motion.tooltip` 1000 ms (the performance center's `duration.tooltip`) and a maximum width of the detail panel's default.
