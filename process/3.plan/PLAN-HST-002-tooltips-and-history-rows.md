# PLAN-HST-002: Consistent Tooltips, and the Rows of the History Tab

## Overview
Implement the owner's corrections of 2026-10-24: one rich tooltip component and its content everywhere in the page
(FTR-HST-002), the identity tooltip without a merge it did not have, no implementation ID in the wording, and in the
History tab the files in a folder tree, a resizable label column and a filter on the rows (RQ-HST-019 to RQ-HST-021).
TASK-HST-007 of PLAN-HST-001 (speed, accessibility, documentation) follows this plan, to measure the final state.

## References
- **Requirements**: RQ-HST-016, RQ-HST-017, RQ-HST-018, RQ-HST-019, RQ-HST-020, RQ-HST-021; RQ-HST-010 and RQ-HST-014
  as amended; RQ-TRC-018, RQ-TRC-049, RQ-TRC-065 (design system, tooltips, charts' accessible names)
- **ADRs**: ADR-HST-001 (DEC-HST-007, DEC-HST-008); ADR-TRC-002 (design system), ADR-TRC-008 (DEC-TRC-035, charts)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-HST-009: The rich tooltip component; no double tooltip; no implementation ID
- **Tier**: M
- **Status**: Done
- **Description**: Add the page-level rich tooltip component of DEC-HST-007 and move the search's, the charts' and the
  History tab's tooltips onto it; remove the plain `title` from every element raising a rich tooltip and from its
  containers (the charts' SVG `<title>` becomes `aria-label`, the timeline frame's help goes to the legend); give the
  identity chips and the commit card's people the sidebar's tooltip, its merge line only when merged; remove the ID from
  the History button's tooltip and test that no string of the page names an ID of the skill's process.
- **Requirement refs**: RQ-HST-016, RQ-HST-018, RQ-HST-010, RQ-HST-014; RQ-TRC-018, RQ-TRC-049, RQ-TRC-065
- **ADR refs**: ADR-HST-001 (DEC-HST-007); ADR-TRC-002; ADR-TRC-008 (DEC-TRC-035)
- **Acceptance Criteria**: Given the page, When a radar point, a commit mark or an identity raises its tooltip, Then one
  rich tooltip shows, with a bold first line, and no `title` nor SVG `<title>` lies on the element or its containers;
  Given each chart, Then it has an `aria-label` and a `<desc>`; Given an identity that merged nothing, Then its tooltip
  says nothing of a merge; Given an identity's chip in the History tab, Then its tooltip is the sidebar's; Given the
  script's strings and the skeleton's text, Then no ID of the AGNOS grammar is in them.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `python -m unittest discover -s tests` (skill folder): 223 tests, 0 failure, 1 skipped. `TooltipComponentTest` (4, headless Edge): a focused radar point shows one tooltip (`#tip`, the only visible `role=tooltip`), its first line bold (weight >= 600), no `title` nor SVG `<title>` on the point or its containers; same for a commit mark (the timeline frame's `title` is gone, its help is in the legend and the frame's `aria-label`); the three charts are named by `aria-label`, described by `<desc>`, with no `<title>`; Alice's tooltip says "merged by e-mail", Claude Opus 5.5's (nothing merged) says nothing of a merge, Alice's chip in the History tab shows the sidebar's tooltip and has no `title`. `WordingTest`: no line of `matrix.js` outside comments, nor of `matrix.html` outside comments, holds an ID of the AGNOS grammar (the History button's "(RQ-HST-011)" removed). The search, chart and History tooltips now use the one component; `test_trace_matrix.py` (RQ-TRC-049) and `test_scorecard.py` (RQ-TRC-061) read `#tip`, and RQ-TRC-065's test checks the charts' `aria-label` instead of an SVG title (DEC-HST-007). `test_literals.py` OK, direct count of the history section: no repeated literal.
- **Assumptions**: The charts' tooltip shows at once on hover, as before; the search's after its 300 ms token, the History tab's after its own; a tooltip with no delay token shows at once. The graph's node and relation tooltips move to the component in TASK-HST-010, with their new content. The commit card's people are focusable, so that their tooltip has a keyboard path.

### TASK-HST-010: The content of the rich tooltips
- **Tier**: M
- **Status**: Not Started
- **Description**: Give every business tooltip of RQ-HST-017 its content on the component: the graph's nodes (element,
  file by its name with its path below, function, box), relations and legend; the matrix's IDs, findings, coverage
  badges and bars; the header items; the quality shortcuts, "Fix first" links, scores, risks, findings, grades and
  trigrams; the History row labels and limits; the detail panel's call-site and badge explanations.
- **Requirement refs**: RQ-HST-017, RQ-HST-016
- **ADR refs**: ADR-HST-001 (DEC-HST-007)
- **Acceptance Criteria**: Given the fixture page, When the pointer rests on a requirement node of the graph, Then the
  tooltip's bold line is its ID and it shows its title, coverage and location; Given a file node, Then its bold line is
  the file name and its path is below; Given a matrix ID, Then its tooltip has the search's form; Given a check's score,
  Then its tooltip gives the formula; Given a History row label, Then its tooltip gives its changes, identities and last
  change; Given any element listed by RQ-HST-017, Then it has no plain `title`.
- **Dependencies**: TASK-HST-009
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-HST-011: Files in a folder tree
- **Tier**: M
- **Status**: Not Started
- **Description**: Build the code angle by file as a tree of folders, each folder row carrying the merged interventions
  below it, opened by default and closed or opened by a click or Enter, the closed folders kept across redraws; files by
  their name under their folder, functions below them.
- **Requirement refs**: RQ-HST-019
- **ADR refs**: ADR-HST-001 (DEC-HST-008)
- **Acceptance Criteria**: Given `src/a/x.py`, `src/a/y.py` and `src/b/z.py`, Then the rows are `src`, `a`, `x.py`,
  `y.py`, `b`, `z.py`, indented by depth; When `a` is closed, Then `x.py` and `y.py` hide and `a` keeps their commits'
  marks; When opened again, Then they show; Given a closed folder, When the period or a filter changes, Then it stays
  closed.
- **Dependencies**: TASK-HST-009
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-HST-012: A resizable label column and a filter on the rows
- **Tier**: M
- **Status**: Not Started
- **Description**: Add the splitter between the History tab's labels and timeline (drag, arrow keys, double click,
  bounds and step from tokens, width kept per viewer, axis, band and overview aligned) and the row filter (a text field
  and, in the requirements angle, type chips) combined with the identity, kind and scope filters.
- **Requirement refs**: RQ-HST-020, RQ-HST-021; RQ-TRC-018, RQ-TRC-025
- **ADR refs**: ADR-HST-001 (DEC-HST-008); ADR-TRC-002
- **Acceptance Criteria**: Given the History tab, When the splitter moves right by three arrow steps, Then the label
  column is three steps wider and the axis, band and rows stay aligned; When dragged past the maximum, Then it stops
  there; When double-clicked, Then it is back to the default; Given the page reopened, Then the width is kept; When
  "HST" is typed, Then only the rows holding it stay with their headings; When TASK is turned off, Then no TASK row
  stays; Given the code angle, When "trace" is typed, Then only the files holding it stay with their folders; When
  cleared, Then every row shows.
- **Dependencies**: TASK-HST-011
- **Assignee**: AI
- **Verification**:
- **Assumptions**:
