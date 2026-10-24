# PLAN-TRC-006: Feature Titles, Fixed Detail Band, Tag Filters, Finer Wheel Zoom

## Overview
Implement RQ-TRC-053 to RQ-TRC-056 after ADR-TRC-007, in the skill's `assets/` (`matrix.js`, `matrix.css`,
`tokens.json`) and its tests.

## References
- **Requirements**: RQ-TRC-053, RQ-TRC-054, RQ-TRC-055, RQ-TRC-056; RQ-TRC-016, RQ-TRC-045 (kept)
- **ADRs**: ADR-TRC-007 (DEC-TRC-029, DEC-TRC-030, DEC-TRC-031)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-TRC-041: The feature's title in the matrix
- **Tier**: M
- **Status**: Done
- **Description**: Draw the title under each feature ID of the Feature column, like the requirement's.
- **Requirement refs**: RQ-TRC-053
- **ADR refs**: ADR-TRC-007 (DEC-TRC-029)
- **Acceptance Criteria**: Given the matrix, When a row is read, Then its Feature cell holds the feature's ID and, under
  it, its title.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `python -m unittest discover -s tests` (skill folder): 132 tests, 1 failure (RQ-TRC-026 data hash, failing before this plan), 1 skipped. `FeatureTitleTest` passes in headless Edge: the Feature cell of RQ-DEM-001 holds FTR-DEM-001 and, under it, "Demo Feature" (`.cell-title`).
- **Assumptions**: None

### TASK-TRC-042: A fixed, highlighted band for the selected element
- **Tier**: M
- **Status**: Done
- **Description**: Split the detail panel into a fixed band (identity and tags) and a scrolling body, and give the
  band its type-colour bar, tinted background and larger title.
- **Requirement refs**: RQ-TRC-054
- **ADR refs**: ADR-TRC-007 (DEC-TRC-030)
- **Acceptance Criteria**: Given a selected element whose links overflow the panel, When the body is scrolled, Then the
  band stays at the top, unmoved; Given any selection, Then the band's title is larger than the rows' text.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `python -m unittest discover -s tests` (skill folder): 133 tests, 1 failure (RQ-TRC-026 data hash, failing before this plan), 1 skipped. `DetailBandTest` passes in headless Edge: with the body limited to 40 px, its content overflows and scrolls while the band keeps its top position; `.detail` has overflow hidden, `.detail-body` auto; the band title is larger than a link row, its left bar colour equals the type dot colour. Screenshot of the demo trace checked: band fixed over scrolled links.
- **Assumptions**: None

### TASK-TRC-043: Tags that filter the groups
- **Tier**: M
- **Status**: Done
- **Description**: Make each group tag a toggle that shows only its group, for elements and boxes, cleared on a new
  selection.
- **Requirement refs**: RQ-TRC-055, RQ-TRC-045
- **ADR refs**: ADR-TRC-007 (DEC-TRC-030)
- **Acceptance Criteria**: Given a requirement with several groups, When the Tasks tag is clicked, Then only that group
  shows and the tag is pressed; When clicked again, Then all groups show; When another element is selected, Then no tag
  is pressed.
- **Dependencies**: TASK-TRC-042
- **Assignee**: AI
- **Verification**: `python -m unittest discover -s tests` (skill folder): 134 tests, 1 failure (RQ-TRC-026 data hash, failing before this plan), 1 skipped. `TagFilterTest` passes in headless Edge on RQ-DEM-001: one tag per group in the groups' order; first tag shows only its group and is `aria-pressed`; a second tag adds its group; unpressing both shows all groups; selecting RQ-DEM-002 leaves no tag pressed and all groups shown; the tag has a title.
- **Assumptions**: None

### TASK-TRC-044: A finer wheel zoom
- **Tier**: M
- **Status**: Not Started
- **Description**: Add the token `dimension.graph-wheel-sensitivity` (0.1, about 10 % of zoom per wheel notch instead of 150 %) through the three tiers and give it to the
  graph as its wheel sensitivity; document it in `SKILL.md`.
- **Requirement refs**: RQ-TRC-056
- **ADR refs**: ADR-TRC-007 (DEC-TRC-031)
- **Acceptance Criteria**: Given the tokens, Then the wheel sensitivity is 0.1; Given the graph, When it is created,
  Then it uses that value.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: Pending.
- **Assumptions**: None
