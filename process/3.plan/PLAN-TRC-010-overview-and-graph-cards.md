# PLAN-TRC-010: Overview and Graph Cards Rearranged

## Overview
Owner review of 2026-10-29: the Overview's "Coverage by trigram" table repeats the Quality view's "Feature areas" chart,
and the call graph's counts belong with the graph. One chart is shown in both views, and the call graph card moves under
the graph's frame, shown only while the implementation is drawn.

## References
- **Requirements**: amended: RQ-TRC-015, RQ-TRC-035, RQ-TRC-062; RQ-TRC-061, RQ-TRC-048, RQ-TRC-087
- **ADRs**: ADR-TRC-010 (DEC-TRC-043); ADR-TRC-008 (DEC-TRC-035); ADR-TRC-005 (DEC-TRC-023); ADR-TRC-002 (design system)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-TRC-075: One feature-areas chart in the Overview and the Quality view
- **Tier**: M
- **Status**: Done
- **Description**: The Overview's "Coverage by trigram" card is removed; its place is taken, inside the "Requirement
  coverage" card (left of Quality) and under its bar and legend, by the "Feature areas" chart of TASK-TRC-074, drawn by
  the same function. A click or Enter on a trigram's row shows the matrix filtered on that trigram, on the Total row the
  matrix without trigram filter, in both views.
- **Requirement refs**: RQ-TRC-015 (amended), RQ-TRC-061, RQ-TRC-087
- **ADR refs**: ADR-TRC-010 (DEC-TRC-043); ADR-TRC-008 (DEC-TRC-035); ADR-TRC-002
- **Acceptance Criteria**: Given the fixture, When the page opens, Then the Overview has no "Coverage by trigram" card
  and the "Requirement coverage" card holds the feature-areas chart, beside the Quality card; Then its rows are those of
  the Quality view's chart; When Enter is pressed on a trigram's row, Then the matrix is shown filtered on that trigram;
  When on the Total row, Then the matrix is shown with every trigram.
- **Dependencies**: TASK-TRC-074
- **Assignee**: AI
- **Verification**: Test first, failing ("Coverage by trigram" still a card title), then OK: no such card, the same
  rows as the Quality chart, Enter on the first trigram gives the matrix filtered on it, on Total every trigram. Owner
  review on XS56K: every trigram named, the grade as a chip, the score in the text colour, rows of 28 px, no second
  legend in the Overview. Whole suite OK before the commit.
- **Assumptions**: None

### TASK-TRC-076: The call graph card under the graph's frame, while the implementation is drawn
- **Tier**: M
- **Status**: Done
- **Description**: The "Call graph" card leaves the Overview for the Graph view, under the graph's frame, with its five
  counts and their clicks unchanged; it is shown only while "Implementation" is checked in Display (the Functions type
  filter on), and hidden otherwise.
- **Requirement refs**: RQ-TRC-035 (amended), RQ-TRC-048
- **ADR refs**: ADR-TRC-005 (DEC-TRC-023); ADR-TRC-002
- **Acceptance Criteria**: Given a page with a call graph, When the page opens, Then the Overview has no "Call graph"
  card; When the Graph view is shown with Implementation checked, Then the card is under the graph's frame with the
  function, call, ambiguous, external and untraced counts; When Implementation is unchecked (or the Functions filter is
  removed), Then the card is hidden; Given a page without call graph, Then no card is drawn.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: Test first, failing (no card in the Graph view), then OK: no card in the Overview, hidden at
  load, shown under the graph's frame with its five counts when Implementation is checked, hidden again when unchecked.
  Owner review on XS56K. Whole suite OK before the commit.
- **Assumptions**: None

### TASK-TRC-077: The checks by risk level, three in a row, the same in the sidebar and the Overview
- **Tier**: M
- **Status**: Done
- **Description**: The Quality view's check cards are ordered by risk level, the highest first, then by title, at most
  three in a row filling the central area's width; the sidebar's checks under Quality follow that order; the Overview's
  Quality card shows the checks in that order as their compact form (title, risk, score bar, findings), without chevron
  nor detail, a click opening the check. "Fix first" keeps the lowest scores first.
- **Requirement refs**: RQ-TRC-062 (amended), RQ-TRC-015, RQ-TRC-058
- **ADR refs**: ADR-TRC-008 (DEC-TRC-034); ADR-TRC-002 (design system)
- **Acceptance Criteria**: Given the fixture, When the Quality view opens, Then its cards stand by risk weight then title;
  Then, in a 1440 by 900 window, the first three share a row, the fourth starts the next, and a row fills the list's width;
  Then the sidebar's checks and the Overview's Quality card list the same order; Then the Overview's card has each
  check's title, risk, score and findings and no chevron nor detail; When one is clicked, Then that check opens.
- **Dependencies**: TASK-TRC-076
- **Assignee**: AI
- **Verification**: Test first, failing (sidebar "IDs defined|Requirements covered…" in the old order), then OK: the
  Quality cards, the sidebar and the Overview card by risk then title; at 1440×900 three in a row filling the list's
  width; the Overview card compact, no chevron nor detail, a click opening the check. The chevrons test now opens
  "covered" by name. Owner review on XS56K. Whole suite OK before the commit.
- **Assumptions**: the risk level is the check's `risk` and its weight in `scoring.json` (critical first, informational
  last); a narrow window may hold fewer than three in a row.
