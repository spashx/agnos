# PLAN-HST-002: Consistent Tooltips, and the Rows of the History Tab

## Overview
Implement the owner's corrections of 2026-10-24: one rich tooltip component and its content everywhere in the page
(FTR-HST-002), the identity tooltip without a merge it did not have, no implementation ID in the wording, and in the
History tab the files in a folder tree, a resizable label column and a filter on the rows (RQ-HST-019 to RQ-HST-021).
TASK-HST-007 of PLAN-HST-001 (speed, accessibility, documentation) follows this plan, to measure the final state.

## References
- **Requirement refs**: RQ-HST-016, RQ-HST-017, RQ-HST-018, RQ-HST-019, RQ-HST-020, RQ-HST-021; RQ-HST-010 and RQ-HST-014
  as amended; RQ-TRC-018, RQ-TRC-049, RQ-TRC-065 (design system, tooltips, charts' accessible names)
- **ADR refs**: ADR-HST-001 (DEC-HST-007, DEC-HST-008); ADR-TRC-002 (design system), ADR-TRC-008 (DEC-TRC-035, charts)

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
- **Status**: Done
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
- **Verification**: `python -m unittest discover -s tests` (skill folder): 228 tests, 0 failure, 1 skipped. `RichContentTest` (5, headless Edge): RQ-DEM-001's graph node tooltip has the bold line RQ-DEM-001, then Requirement, its title, its coverage (Covered directly), its location `FTR-DEM-001-demo-feature.md:8-12`; hovering the node in the graph shows it after the delay and the graph container has no `title`; a file node's bold line is its file name, its path and "IDs cited" below; a code relation's tooltip is headed "Cited in code", names `→ RQ-DEM-001` and a proof line `L<n> <text>`; the matrix's RQ-DEM-001 shows its title, a check's score gives "Score s / 10", the formula and the population, RQ-DEM-001's History label gives 3 changes, 2 identities and its last change by Alice; 18 kinds of business items (IDs, findings, coverage badges and bars, header items, quality shortcuts, Fix-first links, scores, risks, findings counts, grade chips, scale steps, trigrams, History labels and limits) carry no `title` and raise the rich tooltip. RQ-TRC-045's test accepts a rich tooltip in place of a plain one on a control. `test_literals.py` OK (literals named: `LINK_KIND_DEFINES`, `VALUE_AMBIGUOUS`, `CSS_QUICK_DELAY`). Screenshot of this repository's graph: the node tooltip as specified.
- **Assumptions**: The graph's node tooltips use the search's 300 ms delay; the relations keep their own delay token. A span or div raising a rich tooltip takes the keyboard focus (tabindex 0). The score's tooltip also gives the population and the findings, so that the formula's numbers are named. `tipFor` keeps its one-line text for its callers; the rich content is `edgeTipContent`.

### TASK-HST-011: Files in a folder tree
- **Tier**: M
- **Status**: Done
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
- **Verification**: `python -m unittest discover -s tests` (skill folder): 230 tests, 0 failure, 1 skipped. `FolderTreeTest` (2, headless Edge, files `src/a/x.py`, `src/a/y.py`, `src/b/z.py`, `tools/deep/er/w.py`): the rows are `dir:src` (depth 0), `dir:src/a` (1), `x.py`, `y.py` (2), `dir:src/b` (1), `z.py` (2), `dir:tools/deep/er` (0, three folders joined), `w.py` (1); `src/a` carries the marks of commits 1 and 3 of its files; closed (`aria-expanded=false`), it hides `x.py` and `y.py`, keeps its marks, and stays closed after a change of period and of the kind filter; opened again, its files show. The tests reading the code angle's files now leave the folder rows aside (RQ-HST-019). Screenshot of this repository: `.github/skills` joined, `agnos-demo` closed, files by name under their folders, functions below them.
- **Assumptions**: A folder holding one folder and no file joins it on one row (`a/b/c`), as editors' explorers do; in a folder, its sub-folders come before its files, each by name. A folder's marks merge those of the files below it (a function's changes are already its file's). A click on a folder opens or closes it; it selects nothing, a folder being no element of the page.

### TASK-HST-012: A resizable label column and a filter on the rows
- **Tier**: M
- **Status**: Done
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
- **Verification**: `python -m unittest discover -s tests` (skill folder): 234 tests, 0 failure, 1 skipped. `LabelColumnAndRowFilterTest` (4, headless Edge): the splitter (`role=separator`, focusable) starts at the 260 px token, three right arrows make 308 px (3 steps of 16), the band, axis, overview and rows keep the same first column, the width is stored (`agnos-trace-history-label` = 308), 200 more steps stop at the 560 px maximum, 400 left steps at the 160 px minimum, a double click returns to 260; "covered" keeps RQ-DEM-001 to 004 under one heading and the figures count their 4 commits, an empty text brings every row back; turning TASK off leaves no TASK row and the type chips hide with the code angle; in the code angle, a file's name keeps the files holding it with their folders. `FiguresAndFiltersTest` now reads the kept commits from the view's state, the taller filter bar leaving the TASK rows below the window. Screenshot of this repository: column widened, splitter focused, "HST" filter.
- **Assumptions**: The row filter also matches an element's title and a file's path; Reset filters clears it and turns every type back on. The keyboard step is the panels' splitter step token. A width read from storage is clamped to the bounds of the tokens.
