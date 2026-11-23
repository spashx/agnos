# PLAN-TRC-027: Graph explorer review corrections

## Overview
The owner's review of the graph explorer (2026-11-23): resizable table columns, facet bulk selection, counts clear of
scrollbars, relation kind filter applied to the graph, automatic layouts, a context menu, labelled controls with tooltips and
a legend.

## References
- **Requirement refs**: RQ-TRC-151, RQ-TRC-159, RQ-TRC-160, RQ-TRC-161, RQ-TRC-162, RQ-TRC-163, RQ-TRC-164, RQ-TRC-165, RQ-TRC-156, RQ-TRC-158
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
- **Status**: Not Started
- **Description**: Write the test first, then add a drag handle to each table header, bounded by a minimum width token.
- **Requirement refs**: RQ-TRC-159
- **ADR refs**: ADR-TRC-025 (DEC-TRC-010)
- **Acceptance Criteria**:
  - Given the node table, When the Title header's edge is dragged, Then the column widens And keeps its width after a sort And never goes under the token's minimum
- **Dependencies**: TASK-TRC-139
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-TRC-143: Implement graph layouts and context menu
- **Tier**: M
- **Status**: Not Started
- **Description**: Write the tests first, then add a layout selector and a right-click menu with the layouts, fit, select, hide and neighbours at 1, 2 or 3 hops.
- **Requirement refs**: RQ-TRC-162, RQ-TRC-163
- **ADR refs**: ADR-TRC-025 (DEC-TRC-094, DEC-TRC-095)
- **Acceptance Criteria**:
  - Given the graph view, When "Circle" is chosen, Then the shown nodes are on a circle, in the view, And keep their positions after a filter change
  - Given a node right-clicked, When "Neighbours, 2 hops" is chosen, Then only the nodes at most two hops away are shown
  - Given the background right-clicked, Then the menu lists the layouts And no node action; When Escape is pressed, Then it closes
- **Dependencies**: TASK-TRC-140
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-TRC-144: Label controls with tooltips
- **Tier**: M
- **Status**: Not Started
- **Description**: Write the test first, then replace the saved query tool symbols by words and give every control a tooltip.
- **Requirement refs**: RQ-TRC-164, RQ-TRC-155
- **ADR refs**: ADR-TRC-025 (DEC-TRC-093)
- **Acceptance Criteria**:
  - Given the buttons being edited, Then every button, tab, checkbox and field has a non-empty `title` And the tools read "Edit", "Move left", "Move right", "Delete"
- **Dependencies**: TASK-TRC-141, TASK-TRC-143
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-TRC-145: Show graph legend
- **Tier**: M
- **Status**: Not Started
- **Description**: Write the test first, then draw a foldable legend over the graph view, of the node types and relation kinds present, from the graph's tokens.
- **Requirement refs**: RQ-TRC-165
- **ADR refs**: ADR-TRC-025 (DEC-TRC-090, DEC-TRC-091)
- **Acceptance Criteria**:
  - Given a graph with RQ and `contains`, Then the legend lists RQ with its colour And `contains` dashed; When folded, Then only its title stays
- **Dependencies**: TASK-TRC-140
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-TRC-146: Verify explorer review corrections
- **Tier**: M
- **Status**: Not Started
- **Description**: Run the graph skill's suite, check the graph is byte-identical with and without `--explorer` on this repository, time the first view, and add the changelog entry.
- **Requirement refs**: RQ-TRC-156, RQ-TRC-158
- **ADR refs**: ADR-TRC-025 (DEC-TRC-085)
- **Acceptance Criteria**:
  - Given this repository, When the graph is built with and without `--explorer`, Then both files are byte-identical
  - Given this repository's graph with call graph and history, When the explorer is opened headless, Then its first view is drawn in less than 5 s
- **Dependencies**: TASK-TRC-140, TASK-TRC-141, TASK-TRC-142, TASK-TRC-143, TASK-TRC-144, TASK-TRC-145, TASK-TRC-147
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-TRC-147: Explain undefined node type in detail
- **Tier**: S
- **Status**: Not Started
- **Description**: In the detail panel of an UNDEFINED node, say that its ID is cited with the prefix of a type but defined nowhere in the index (owner, 2026-11-23: ADR-ABC-010 shown UNDEFINED in the table, ADR in the detail).
- **Requirement refs**: RQ-TRC-146, RQ-TRC-154
- **ADR refs**: ADR-TRC-025 (DEC-TRC-089)
- **Acceptance Criteria**:
  - Given an undefined ADR ID selected, Then the detail reads that the ADR ID is cited but not defined in the index
- **Dependencies**: TASK-TRC-139
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: the UNDEFINED type is kept: the ID is no artifact, as the performance center classes it.
