# PLAN-HST-003: The Commit in the Detail Panel, its Git Graph, and the History Tab's Controls

## Overview
Owner request of 2026-10-24, five corrections to the History tab: the kind selector beside the angle selector, the
row filter first on its line and as wide as the sidebar's search, a commit shown in the detail panel instead of a card
to close, a git graph of the commit's branches in that panel, and an identity drawn by its icon in its colour, with no
dot (FTR-HST-001: RQ-HST-022 to RQ-HST-026, RQ-HST-006, RQ-HST-007 and RQ-HST-014 amended; ADR-HST-001: DEC-HST-009
to DEC-HST-011).

## References
- **Requirement refs**: RQ-HST-022, RQ-HST-023, RQ-HST-024, RQ-HST-025, RQ-HST-026; RQ-HST-006, RQ-HST-007, RQ-HST-014
  (amended); RQ-HST-013 (measured again)
- **ADR refs**: ADR-HST-001 (DEC-HST-009, DEC-HST-010, DEC-HST-011; DEC-HST-005, DEC-HST-007); ADR-TRC-002 (design system)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-HST-013: The selectors together, the row filter first
- **Tier**: M
- **Status**: Done
- **Description**: Move the kind selector to the toolbar after the angle and code grouping selectors; put the row filter
  first on the filter line, its width a component token aliasing the sidebar search field's default width.
- **Requirement refs**: RQ-HST-022, RQ-HST-014
- **ADR refs**: ADR-HST-001 (DEC-HST-006), ADR-TRC-002
- **Acceptance Criteria**: Given the History tab, When it opens, Then the kind selector follows the angle selector (and
  the grouping when it shows) on the toolbar, and the row filter is the first control of the filter line; Given the
  sidebar at its default width, Then the row filter and the search field have the same width within one pixel.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `test_RQ_HST_022_…_row_filter_comes_first` OK: toolbar fieldsets `history-angle,history-kind`, with the
  code angle `history-angle,history-grouping,history-kind`; first control of the filter line `history-filter`; widths
  of the row filter and of `#search` within 1 px. `test_history_*.py`: 43 tests OK, 1 skipped (the measure).
- **Assumptions**: The row filter's width is the sidebar's default width less its two paddings (a `calc` of the tokens
  `--c-sidebar-width` and `--s-space-lg`); it does not follow a sidebar resized by the reader.

### TASK-HST-014: An identity drawn by its icon in its colour
- **Tier**: M
- **Status**: Done
- **Description**: In the sidebar's History section, the identity chips and every person tag, draw the kind icon in
  the identity's colour and remove the colour dot; the timeline's marks are unchanged.
- **Requirement refs**: RQ-HST-026, RQ-HST-014
- **ADR refs**: ADR-HST-001 (DEC-HST-005), ADR-TRC-002
- **Acceptance Criteria**: Given an identity, When the page opens, Then its sidebar line and its chip show its icon in
  its colour, its name and its count, and no dot; Given the timeline, Then its marks keep their shapes and colours.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `test_RQ_HST_026_…_no_dot_is_drawn` OK: 0 dots in the sidebar and the chips, the icons' colours equal
  between sidebar and chips and 3 distinct for 3 identities, a human mark still a circle;
  `test_RQ_HST_014_given_20_identities…` (now reading the icons' colour) OK: 20 colours.
- **Assumptions**: The icon of every person tag (the commit, later its git graph) goes through the same function, so
  that RQ-HST-026 holds wherever an identity is named. Committed with TASK-HST-013, the two tasks sharing the
  stylesheet.

### TASK-HST-015: The commit graph in the history block
- **Tier**: L
- **Status**: Done
- **Description**: In `history.py`, read the local branch tips, find each commit's branch by the first-parent walk of
  DEC-HST-010, and write the `graph` block (`branches`, `nodes`) from the commits already read; tests on git repositories
  in temporary folders.
- **Requirement refs**: RQ-HST-024, RQ-HST-006
- **ADR refs**: ADR-HST-001 (DEC-HST-010, DEC-HST-004)
- **Acceptance Criteria**: Given `main` with m1 and m2 and `feature/A` (a1, a2) merged by "Merge branch 'feature/A'"
  then deleted, When the history is built, Then m1, m2 and the merge are on `main`, a1 and a2 on `feature/A`, and the
  merge's parents are m2 and a2; Given a branch not merged, Then its commits are on it; Given a merge that names no
  branch and that no tip reaches, Then its second parent's commits are on an unnamed branch; Given two runs, Then the
  data files are equal; Given a run without `--history`, Then the RQ-TRC-026 sentinel is unchanged.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `BranchGraphTest`, 6 tests OK: a branch merged then deleted (m1, m2 and the merge on `main`, a1 and
  a2 on `feature/A`, the merge's parents m2 and a2, the merge with no commit index); the GitHub and "Merge X into Y"
  messages; a branch checked out; a branch made from another; a merge naming nothing (its side unnamed); a commit outside
  the folders (in the graph, no commit index). `test_RQ_HST_006_given_two_runs…` OK (same bytes); the sentinel test of
  RQ-TRC-026 OK; whole suite 246 tests OK, 2 skipped. On the demo: 6 branches found, the WEB commits on `feature/WEB`.
- **Assumptions**: The graph is HEAD's history, as the timeline is: a local branch HEAD does not reach brings no node.
  The path-limited log rewrites parents and drops merges (seen on the demo), so the graph is read by a second log with
  no path and no patch; DEC-HST-010 amended accordingly.

### TASK-HST-016: The commit in the detail panel
- **Tier**: L
- **Status**: Done
- **Description**: Make `commit:<hash>` a key of the selection; render the commit in the detail panel (band, tags,
  groups of what it changed with their lines); select it on a mark's click or Enter; remove the pinned card.
- **Requirement refs**: RQ-HST-023, RQ-HST-007, RQ-HST-026
- **ADR refs**: ADR-HST-001 (DEC-HST-009, DEC-HST-007), ADR-TRC-002
- **Acceptance Criteria**: Given a commit that changed two requirements and one file, When its mark is clicked, Then
  the detail panel shows its hash, subject, contributors with their icons, kind and total lines, and the groups of 2
  requirements and 1 file with their lines; When an item of a group is clicked, Then it is selected; Given the timeline,
  Then no card shows over it and the selected commit's mark is marked; When the panel scrolls, Then its band stays.
- **Dependencies**: TASK-HST-014
- **Assignee**: AI
- **Verification**: `CommitDetailTest`, 4 tests OK: a click selects `commit:a000000005`, the History tab stays, no
  `#history-card`; band "Commit · Agent", hash, subject, Claude Opus 5.5 with its icon, badges `7 lines,main`, tags
  `RQ,FILE`, groups `RQ-DEM-002=3 lines` and `a.py=4 lines`, the mark marked, address `#commit:a000000005`; a group item
  selects it and unmarks the mark; a feature and its requirement counted once (31 lines); Enter on a mark selects its
  commit, and the graph then shows its empty state. The band is the panel's `detail-top`, which does not scroll
  (RQ-TRC-054). `test_RQ_HST_007_…_click_selects_it_in_the_detail_panel` OK. Whole suite: 250 tests OK, 2 skipped.
- **Assumptions**: The total of lines counts the files and the process elements that no other changed element contains
  (a feature's range holds its requirements'); functions are inside their files. A merge, or a commit that changed no
  folder read, is selectable from the git graph (TASK-HST-017) and shows a note instead of groups. The commit's band
  takes the accent colour as its type colour.

### TASK-HST-017: The git graph of the selected commit
- **Tier**: L
- **Status**: Done
- **Description**: Draw, in the commit's detail panel, the git graph of DEC-HST-011: lanes by branch, names, dots,
  curved lines to the parents, rows with hash, subject and author's icon, the selected commit marked, a click selecting a
  commit; branch tokens added to the design system.
- **Requirement refs**: RQ-HST-025, RQ-HST-014
- **ADR refs**: ADR-HST-001 (DEC-HST-011), ADR-TRC-002
- **Acceptance Criteria**: Given RQ-HST-024's repository, When a2 is selected, Then the graph shows the lanes `main` and
  `feature/A` named, a2 marked on `feature/A`, a line a2 → a1, a curve from the merge to a2 and a curve from a1 to m1;
  When the merge's row is clicked, Then the merge is selected; Given both themes, Then the lanes, dots and labels take
  their tokens and the literal test passes.
- **Dependencies**: TASK-HST-015, TASK-HST-016
- **Assignee**: AI
- **Verification**: `GitGraphTest`, 2 tests OK: with a4 selected, 7 rows newest first, a4 `aria-current`, lanes `main` 0
  and `feature/A` 1, labels `main,feature/A`, 7 lines of which 2 curved, 6 author icons, 1 ring, the two lanes'
  strokes differ; a click on the merge's row selects it ("Commit · Merge", its note), every row a named button with the
  rich tooltip and no title. Literal test OK. Whole suite 252 tests OK, 2 skipped. On the demo's page, a commit of
  `feature/WEB` drawn on its lane under `main`'s merge, both named (screenshot checked).
- **Assumptions**: The window is 12 commits above and below the selected one; lanes are coloured by branch (stable
  from one selection to the next), the eight branch tokens taken in turn. Each row raises the rich tooltip with the whole
  subject, since the panel truncates it.

### TASK-HST-018: Speed measured again, documentation, the demo's page
- **Tier**: M
- **Status**: Done
- **Description**: Run the performance measure of RQ-HST-013 again with the graph block, update the skill's
  documentation (the commit in the detail panel, the git graph), run the whole suite and regenerate the demo's
  traceability page with `--call-graph --history`.
- **Requirement refs**: RQ-HST-013, RQ-HST-023, RQ-HST-025
- **ADR refs**: ADR-HST-001 (DEC-HST-009 to DEC-HST-011)
- **Acceptance Criteria**: Given the generated repository of 2,000 commits, When the measure runs, Then the added time,
  size and drawing times are within RQ-HST-013's metrics; Given the skill's tests, Then they all pass; Given the demo's
  page, Then a commit of `feature/WEB` shows on its branch in the git graph.
- **Dependencies**: TASK-HST-013 to TASK-HST-017
- **Assignee**: AI
- **Verification**: `test_history_perf.py` (`AGNOS_TRACE_PERF=1`): history adds 2.30 s and 428 KiB (limits 20 s, 3 MB), the
  tab drawn in 57 to 64 ms (limit 300); the P95 of the steps was 51.0 and 58.0 ms on two of six runs, 37.2 to 39.8 ms
  on the others; the version before this plan (`fcf70ce`), measured the same way, gave 40.4 to 48.3 ms: no
  regression, the machine's noise around a 50 ms limit. Whole suite 252 tests OK, 2 skipped. `SKILL.md`: the commit in
  the detail panel, the git graph, the `graph` block, the selectors. The demo's page with `--call-graph --history`:
  78 commits, 7 humans; `commit:1164d205e6` reads "…, feature/WEB" with the labels `main,feature/WEB`.
- **Assumptions**: The P95 metric of RQ-HST-013 is kept as it is; its margin on this machine is small, which is
  reported to the owner.

### TASK-HST-019: A tag to show the git graph or not
- **Tier**: S
- **Status**: Done
- **Description**: Make the commit's git graph a group of the detail panel, with a "Git graph" tag among the band's tags
  that shows it alone or with the others (owner request of 2026-10-25).
- **Requirement refs**: RQ-HST-025 (amended), RQ-TRC-055
- **ADR refs**: ADR-HST-001 (DEC-HST-011), ADR-TRC-007 (DEC-TRC-030)
- **Acceptance Criteria**: Given a commit selected, When its "Git graph" tag is pressed, Then only the git graph shows;
  When it is pressed again, Then every group shows.
- **Dependencies**: TASK-HST-017
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: The tag comes first, counts the commits drawn, and takes the commit's accent colour.

### TASK-HST-020: A merge left with one parent by the folders' history credits no one
- **Tier**: M
- **Status**: Done
- **Description**: Fix found on the demo on 2026-10-24: git's history simplification can leave a merge with one parent
  in the path-limited log (its other parent's side never changed the folders read), and the merge was then credited
  as an ordinary commit of its author. The merges are now known from their true parents (`git rev-list --merges`).
- **Requirement refs**: RQ-HST-002, RQ-HST-004
- **ADR refs**: ADR-HST-001 (DEC-HST-002)
- **Acceptance Criteria**: Given a branch merged into a `main` whose commits never changed the folders read, When the
  history is built, Then the merge, shown with one parent by the folders' log, is no commit of the timeline, its author
  no identity, and it credits no element.
- **Dependencies**: TASK-HST-015
- **Assignee**: AI
- **Verification**: `test_RQ_HST_002_given_a_merge_left_with_one_parent…` failed first (`['m1', 's1', "Merge branch
  'side'"]`), then OK: the merge has one parent in the folders' log, the commits are `m1, s1`, Dan is no identity, RQ-A
  is credited to m1 and s1 only. Whole suite 254 tests OK, 2 skipped. The demo's page: 77 commits (78 before), no merge
  credited, `Merge branch 'feature/BKG'` kept in the git graph as a merge with no commit index.
- **Assumptions**: One `git rev-list --merges` with the same `--since`; the ranges are still carried through such a
  merge to its parent, only the credit is withheld.
