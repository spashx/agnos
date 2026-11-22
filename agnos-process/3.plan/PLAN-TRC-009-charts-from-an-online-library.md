# PLAN-TRC-009: Charts from an Online Library

## Overview
Load Cytoscape.js and Apache ECharts from cdnjs, draw the Delivery charts and the Quality radar with ECharts in the
design system, and group the overlapping marks of the History timeline. Each step leaves the page and its tests working.

**Session split** (AGNOS context management, at most 10 tasks per session): the session of 2026-10-27/28 on
`feature/TRC` already holds TASK-TRC-055 to TASK-TRC-062; it does TASK-TRC-063 and TASK-TRC-064 only. **Handoff**:
the next session starts from TASK-TRC-065, reads ADR-TRC-010 first, and needs the network for the page tests.

## References
- **Requirements**: RQ-TRC-080 to RQ-TRC-088; amended: RQ-TRC-010, RQ-TRC-024 (superseded by RQ-TRC-082), RQ-TRC-061,
  RQ-TRC-075, RQ-TRC-079
- **ADRs**: ADR-TRC-010 (DEC-TRC-040 to DEC-TRC-044); ADR-TRC-002 (design system); amended: ADR-TRC-003 (DEC-TRC-005,
  DEC-TRC-006), ADR-TRC-008 (DEC-TRC-035), ADR-TRC-009 (DEC-TRC-039)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-TRC-063: The online libraries specified and decided
- **Tier**: M
- **Status**: Done
- **Description**: Write FTR-TRC-005 and ADR-TRC-010 from the owner's review of 2026-10-28, and mark the requirements and
  decisions they amend or supersede with a note naming them.
- **Requirement refs**: RQ-TRC-080 to RQ-TRC-088
- **ADR refs**: ADR-TRC-010 (DEC-TRC-040 to DEC-TRC-044)
- **Acceptance Criteria**: Given the documents, When `agnos-index` runs, Then RQ-TRC-080 to RQ-TRC-088 and DEC-TRC-040 to
  DEC-TRC-044 are listed with no duplicate; Given RQ-TRC-010, RQ-TRC-024, RQ-TRC-061, RQ-TRC-075, RQ-TRC-079,
  DEC-TRC-005, DEC-TRC-006, DEC-TRC-035, DEC-TRC-039, Then each names what amends it; Given the owner's review, Then
  ADR-TRC-010 is Accepted.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `agnos-index`: 391 entries, 48 documents, exit 0, RQ-TRC-080 to 088 and DEC-TRC-040 to 044 listed;
  `git diff`: one note added to each of RQ-TRC-010, RQ-TRC-024 (superseded), RQ-TRC-061, RQ-TRC-075, RQ-TRC-079,
  DEC-TRC-005, DEC-TRC-006, DEC-TRC-035, DEC-TRC-039; owner approval of 2026-10-28, ADR-TRC-010 Accepted. No code.
- **Assumptions**: ECharts 6.1.0 (latest on the cdnjs API on 2026-10-28) and Cytoscape.js 3.30.2 (the vendored version)
  with their cdnjs `sha512` hashes; the History overlap is solved by grouping marks (not by shifting them); the
  "lines per task" chart is replaced by "tasks per tier".

### TASK-TRC-064: Libraries from cdnjs, said when missing
- **Tier**: L
- **Status**: Done
- **Description**: Add `assets/libraries.json`; write the library scripts with their integrity from it; remove
  `scripts/vendor/`; name the libraries and licences in the footer; guard every use of Cytoscape.js and ECharts with the
  missing-library message; page tests skipped with their reason when cdnjs is unreachable (tests first).
- **Requirement refs**: RQ-TRC-080, RQ-TRC-081, RQ-TRC-082
- **ADR refs**: ADR-TRC-010 (DEC-TRC-040, DEC-TRC-041)
- **Acceptance Criteria**: Given a generated page, Then its scripts are the two cdnjs URLs with `integrity` and
  `crossorigin="anonymous"`, and `<page>.data.js`; Given a page whose library URLs fail, Then the Graph view shows the
  message naming Cytoscape.js and the Matrix is filled; Given a version changed in `libraries.json`, Then the page loads
  it; Given the whole suite with the network, Then it passes.
- **Dependencies**: TASK-TRC-063
- **Assignee**: AI
- **Verification**: Tests written first (4 errors: no `LIBRARIES_PATH`), then OK: the page's scripts are the cdnjs URLs of
  Cytoscape.js 3.30.2 and ECharts 6.1.0, each with its `integrity` and `crossorigin="anonymous"`, then `page.data.js`;
  the record's versions, URLs and `sha512` hashes valid, `scripts/vendor/` gone; a version changed in a copy of the record
  gives `/cytoscape/9.9.9/` in the page and in `meta.libraries`; a page whose library URLs fail shows "Cytoscape.js
  could not be loaded" in the Graph view and fills the matrix. Whole suite with the network: 291 tests OK, 3 skipped
  (the three `AGNOS_TRACE_PERF` measures). `SKILL.md`: the vendoring section replaced by "Libraries", the description
  and step 4 no longer say offline.
- **Assumptions**: the sentinel of RQ-TRC-026 (`DATA_BEFORE_PLAN_SHA256`) re-pinned on purpose, `meta.library` having
  become `meta.libraries` (RQ-TRC-082); the data-missing message names the `.data.js` script, no longer the first
  script; offline, the tests skip every page test (not only those of the libraries), cdnjs being probed once.

### TASK-TRC-065: ECharts in the design system, and its keyboard path
- **Tier**: M
- **Status**: Done
- **Description**: One helper that initialises an ECharts chart in SVG with `aria` and decals, its theme read from the
  resolved tokens, redrawn on a theme change, and the keyboard path (Tab, arrows, Enter) over its data items.
- **Requirement refs**: RQ-TRC-085, RQ-TRC-087
- **ADR refs**: ADR-TRC-010 (DEC-TRC-042, DEC-TRC-043); ADR-TRC-002 (DEC-TRC-009, DEC-TRC-010)
- **Acceptance Criteria**: Given a chart drawn in each theme, Then its text colour and font family equal the resolved
  tokens; Given the chart focused, When the right arrow is pressed, Then the first item's tooltip shows; Given the code,
  Then no raw visual literal is written.
- **Dependencies**: TASK-TRC-064
- **Assignee**: AI
- **Verification**: `tests/test_library_charts.py` written first (4 failing), then 4 tests OK with ECharts 6.1.0 from cdnjs:
  an SVG chart whose text fill is the resolved `--s-text-muted` (#475569, 12 px caption) in light and in dark after
  `redrawLibraryCharts()`, font family the resolved `--s-font-sans`; `tabindex` 0, name "Test chart", two right arrows
  show "second" in the tooltip, Enter activates item 1; `aria.enabled` and `aria.decal.show` true, description "Three
  bars"; without `window.echarts`, "Apache ECharts could not be loaded" and `null`. Literal test OK; whole suite 295
  tests OK, 3 skipped (the perf measures).
- **Assumptions**: ECharts writes its generated description into the container's `aria-label`, so the page sets its own
  name and `aria-description` again after each drawing; the chart is drawn without animation; charts whose box left the
  page are disposed at the next chart's creation.

### TASK-TRC-066: The Delivery charts with ECharts
- **Tier**: M
- **Status**: Done
- **Description**: Replace the three hand-drawn Delivery charts: points per active day per identity (A, B hatched),
  points over time with A and B marked and a zoom, tasks per tier A beside B; tiers named in full from `delivery.json`.
- **Requirement refs**: RQ-TRC-083, RQ-TRC-075, RQ-TRC-087
- **ADR refs**: ADR-TRC-010 (DEC-TRC-043); ADR-TRC-009 (DEC-TRC-039)
- **Acceptance Criteria**: Given the fixture, Then three library charts are drawn, their legends read "S, small task, 1
  point", "M, medium task, 3 points", "L, large task, 8 points", the third has one A and one B value per tier, and their
  texts use the caption or small size.
- **Dependencies**: TASK-TRC-065
- **Assignee**: AI
- **Verification**: `DeliveryChartsTest` rewritten first for the library charts (5 failing), then 6 tests OK: charts
  "throughput,timeline,tiers" drawn by ECharts, each focusable and named; legend "S, small task, 1 point|M, medium task,
  3 points|L, large task, 8 points"; text and legend sizes equal to `--s-text-small` and `--s-text-caption`; Claude's A
  bars sum 3.333, B 0.000, B series with a decal, colour the resolved `--c-history-identity-2`; timeline 42 days, 2 mark
  areas, a data zoom, 7 weeks, last week 2026-10-26 with 1 point; tiers "A:2,0,1 B:0,1,0", with tag S "A:2,0,0 B:0,0,0";
  arrow on the throughput chart shows Alice. Whole suite: 296 tests OK, 3 skipped. `node --check` OK. Screenshots of
  XS56K (6 weeks), light and dark: first an e-mail name squeezed the bars, the tier labels overlapped and the legend
  touched the bars; fixed (names cut at `delivery-label-width`, tier labels on three lines, room for the legend). Two
  slips caught on the way: `decal: "none"` refused by ECharts 6.1 (an empty decal instead), a `labelWidth` name already
  declared (renamed, found by `node --check`).
- **Assumptions**: the tier is told by the opacity of the identity's colour, B by ECharts' first decal in the card's
  colour; two test outputs renamed (`rate_a`, `rate_b`) as they clashed with the band's `data-a`/`data-b` attributes; the
  token `delivery-hatch-opacity` removed (no longer read), `delivery-chart-height`, `delivery-row-height` and
  `delivery-label-width` added.

### TASK-TRC-070: One colour per period, shades for the tiers
- **Tier**: M
- **Status**: Done
- **Description**: Owner review of 2026-10-28: tokens `period-a` and `period-b` mark A and B in the header (period
  marks, band of figures) and colour the Delivery charts, the tiers as shades of them; no pattern and no identity colour
  in the charts; the points over time keep their form, columns neutral, areas in the periods' colours.
- **Requirement refs**: RQ-TRC-083, RQ-TRC-087, RQ-TRC-085
- **ADR refs**: ADR-TRC-010 (DEC-TRC-043); ADR-TRC-002 (DEC-TRC-009, DEC-TRC-010)
- **Acceptance Criteria**: Given the tab, Then the A and B marks of the header take `period-a` and `period-b`, and the A
  bars of every chart the colour of `period-a`, the B bars that of `period-b`; Given a tier, Then its bars are its
  period's colour at its tier's opacity; Given the charts, Then no series has a decal and each bar writes its value;
  Given both themes, Then each mark's text meets 4.5:1 on its colour.
- **Dependencies**: TASK-TRC-066
- **Assignee**: AI
- **Verification**: Tests changed first (3 failing), then OK: the header's A and B marks take the resolved `period-a`
  and `period-b`, the band's figures carry both marks; throughput A series all `period-a`, B all `period-b`, tier
  opacities 0.4, 0.7, 1, no decal, totals written; tiers chart A/B in their colours, counts written; timeline areas in
  the periods' colours; `aria.decal.show` false. Contrast of the marks' text: light A 5.17, B 5.02; dark A 7.41, B 11.28.
  Whole suite: 297 tests OK, 3 skipped; `node --check` OK. Screenshots of XS56K, light and dark: no pattern, A blue and B
  amber from the header to the charts, values on the bars, timeline columns neutral.
- **Assumptions**: B is the design system's amber (`amber-700`, `amber-400` in dark), the pair blue and amber being the
  one colour-blind readers tell apart best; the text on a mark is white in light and `slate-950` in dark; the timeline's
  columns turn neutral (slate) so that blue is never read as period A outside it.

### TASK-TRC-071: An identity's icon before its name in the throughput chart
- **Tier**: M
- **Status**: Done
- **Description**: Owner request of 2026-10-28: each name of the "Points per active day" axis is led by its kind's icon
  (human or agent), drawn in the identity's colour as everywhere else in the page; the bars keep the periods' colours.
- **Requirement refs**: RQ-TRC-083, RQ-HST-026
- **ADR refs**: ADR-TRC-010 (DEC-TRC-043)
- **Acceptance Criteria**: Given the throughput chart, Then each axis label starts with an image of its identity's kind
  icon (human or agent) filled with the identity's resolved colour, then the name.
- **Dependencies**: TASK-TRC-070
- **Assignee**: AI
- **Verification**: Test first (1 error), then OK: rich keys p0,p1, label "{p1|} Claude Opus 5.5", Alice's image a human icon in `--c-history-identity-1`, Claude's an agent icon in `--c-history-identity-2`. Whole suite 298 OK, 3 skipped (one failure on the way: `innerHTML` forbidden by RQ-TRC-022, replaced by `XMLSerializer`). Screenshots of XS56K light and dark: icons before every name.
- **Assumptions**: owner choice of 2026-10-28: the icon in the identity's colour; its cut-outs in the card's colour.

### TASK-TRC-072: The timeline's bars in A and B in their period's colour
- **Tier**: S
- **Status**: Done
- **Description**: Owner request of 2026-10-28: in "Points over time", the bars inside period A or B take that period's
  colour (shaded by tier), the others stay in shades of grey.
- **Requirement refs**: RQ-TRC-083
- **ADR refs**: ADR-TRC-010 (DEC-TRC-043)
- **Acceptance Criteria**: Given the timeline, Then a bar of a day in A is `period-a`, one in B is `period-b`, one in
  neither is the neutral colour.
- **Dependencies**: TASK-TRC-070
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: None

### TASK-TRC-067: The checks radar with ECharts
- **Tier**: M
- **Status**: Done
- **Description**: Replace the hand-drawn radar of the Quality view by an ECharts radar, one indicator per scored check,
  its tooltip and the click or Enter opening the check.
- **Requirement refs**: RQ-TRC-084, RQ-TRC-061, RQ-TRC-087
- **ADR refs**: ADR-TRC-010 (DEC-TRC-043); ADR-TRC-008 (DEC-TRC-035)
- **Acceptance Criteria**: Given the fixture, When the Quality view opens, Then the radar has one indicator per scored
  check with its score; When a point is chosen with the keyboard and Enter pressed, Then its check opens.
- **Dependencies**: TASK-TRC-065
- **Assignee**: AI
- **Verification**: Tests rewritten first (2 failing), then OK: the radar an ECharts chart with one indicator per scored check in order (covered … files-traced), focusable and named; first arrow shows "Requirements covered, score 4.0, population 5, 3 findings", the next "IDs defined"; Enter on the sixth opens "filled"; one tooltip only (the library's, bold head), no title around. Fit in 1440×900 kept: the radar's height a token, 150 px (first 190 px overflowed by 5 px, measured). Whole suite 299 OK, 3 skipped; `node --check` OK.
- **Assumptions**: the radar in the accent colour (grades stay on the report card and the bars); the pointer shows all checks' scores, the keyboard one check at a time; the named-charts test of RQ-HST-016 counts two inline SVG charts and the radar's container.

### TASK-TRC-073: A readable, more elaborate radar
- **Tier**: M
- **Status**: Done
- **Description**: Owner review of 2026-10-29: the radar fills its card (150 px at least, the fit of RQ-TRC-063), polygon
  rings with light bands, each check's score under its name in its grade's colour, a thicker outline with ringed points;
  the pointer's tooltip is again the check of the nearest axis. A dashed attention ring was tried and removed at the
  owner's request (no specification asks for it).
- **Requirement refs**: RQ-TRC-084, RQ-TRC-087, RQ-TRC-063, RQ-TRC-065
- **ADR refs**: ADR-TRC-010 (DEC-TRC-043); ADR-TRC-008 (DEC-TRC-035)
- **Acceptance Criteria**: Given a wide window, Then the radar grows with its card; Given 1440 by 900, Then the Quality
  view has no vertical scroll; Given the pointer above the radar's centre, Then its tooltip is the first check's.
- **Dependencies**: TASK-TRC-067
- **Assignee**: AI
- **Verification**: Hover test first (failing), then OK: pointer above the centre gives "covered"; probe of the four sides
  top covered, right connected, bottom adr-rq, left tasked (ECharts' counter-clockwise order). Fit tests OK (radar 150 px
  at 1440×900, overflow 0). Whole suite 299 OK, 3 skipped; `node --check` OK. Visual check by the owner on XS56K.
- **Assumptions**: the nearest axis is found from the pointer's angle around the box's centre, where ECharts centres the
  radar; the hover test runs before Enter, which scrolls the view to the opened check.

### TASK-TRC-074: Feature areas and coverage in one chart
- **Tier**: M
- **Status**: Done
- **Description**: Owner review of 2026-10-29: replace the inline-SVG "Feature areas" bars and "Coverage" shares of the
  Quality view by one ECharts horizontal chart "Feature areas": a Total row first (today's Coverage), then one row per
  trigram that has requirements, the shares of its covered, indirect and uncovered requirements stacked to 100 % in the
  coverage colours, with the grade and score written at the row's end in the grade colour. Keyboard path and tooltip by
  `libraryChart`. Owner review on XS56K: the charts' grid has two columns, a row per trigram's height (token), the
  radar takes the card's height, the shares in percent, the end label's room, trigrams without requirement hidden.
- **Requirement refs**: RQ-TRC-061 (amended), RQ-TRC-065, RQ-TRC-087, RQ-TRC-063
- **ADR refs**: ADR-TRC-010 (DEC-TRC-043); ADR-TRC-008 (DEC-TRC-035, amended); ADR-TRC-002 (design system)
- **Acceptance Criteria**: Given the fixture, When the Quality view opens, Then it holds the radar and one "Feature
  areas" chart, and no "Coverage" chart; Then its first row is Total and the next rows are the trigrams, in order;
  Then each row's covered, indirect and uncovered counts equal the requirements of its trigram (the Total's equal
  today's coverage shares), stacked to 100 %; Then each row's end label is the trigram's grade and score in its grade colour; When a
  row is focused by the arrow keys, Then its tooltip gives the counts, shares and grade; Given 1440 by 900, Then the
  Quality view has no vertical scroll; Then no raw colour, size or duration is in the code (tokens only).
- **Dependencies**: TASK-TRC-073
- **Assignee**: AI
- **Verification**: Tests first, failing (`svgs` 2 != 0), then OK: rows Total + trigrams, counts per row, max 100,
  end labels `{gA|A 9.6}` in their grade colour, keyboard tip; RQ-HST-016 named charts OK; fit 1440×900 OK for the
  fixture and five areas (2 charts). Whole suite 300 OK, 3 skipped; `node --check` OK. Visual check by the owner on XS56K.
- **Assumptions**: the Total row carries the overall grade and score of the report card; the colours are the existing
  coverage and grade tokens, one row-height token added (`quality-area-row-height`, 18 px).

### TASK-TRC-068: Grouped marks and a readable "together" mark in the History timeline
- **Tier**: L
- **Status**: Done
- **Description**: Merge the marks of a row that overlap at the current zoom into one group mark with its count and kind,
  its tooltip listing its commits, its activation zooming on them; replace the ringed "together" mark by a circle holding
  a diamond whose two colours can never be confused.
- **Requirement refs**: RQ-TRC-086, RQ-TRC-089, RQ-HST-007, RQ-HST-014
- **ADR refs**: ADR-TRC-010 (DEC-TRC-044); ADR-HST-001 (DEC-HST-005)
- **Acceptance Criteria**: Given a row with three commits within one hour and the whole history in view, Then one group
  mark reading 3 is drawn; When the view is zoomed on that hour, Then three marks are drawn. Given a commit by a human and
  an agent, Then a circle of the human's colour and a diamond of the agent's are drawn with no ring, also when the agent
  is the author; Given the two with the same colour, Then the diamond differs by at least the threshold in both themes.
  Given a group of two humans, Then its mark is neutral; Given a group of one human, Then it has that human's colour;
  Given a human and an agent commit grouped, Then the mark is the mixed rounded square.
- **Dependencies**: TASK-TRC-064
- **Assignee**: AI
- **Verification**: `test_history_groups.py`: 13 tests OK, those of the fixed size, of the count beside the symbol and of
  the bold dates in a group's tooltip failing before the code (one mark reading 3 then three on zoom; circle and diamond
  with no ring, either author; the diamond differing in both themes; neutral, single-identity and mixed groups; count at
  4.5:1). Full suite: 317 tests OK, 3 skipped. `AGNOS_TRACE_PERF=1`: History tab drawn in 34 ms, P95 11.7 ms on 2000 commits. Visual check left to the owner.
- **Assumptions**: threshold 0.12 in OKLab; sizes from the UX proposal 2 chosen by the owner (row 28, circle 9, diamond
  10.5, inner diamond 7, square 8, separator 1.5, count 12, reach 40); the proposal's count background is a text halo;
  the owner's choice of the proposal covers its lines changed moving to the tooltip; counts above 99 read "99+"; a group
  that cannot split selects its newest commit when activated; the git graph's own ring marks its current commit and is
  unchanged.

### TASK-TRC-123: Remove vendored-library attribute from marketplace
- **Tier**: S
- **Status**: Done
- **Description**: Remove from `agnos-meta-release/assets/marketplace.gitattributes.txt` the attribute and the comment of the vendored library, gone since DEC-TRC-040 (owner, 2026-11-22).
- **Requirement refs**: RQ-TRC-080, RQ-TRC-082
- **ADR refs**: ADR-TRC-010 (DEC-TRC-040)
- **Acceptance Criteria**: Given the attributes file, Then it names no `vendor` path; Given a release rehearsal, Then it exits 0 with no problem; Given `test_marketplace` and `test_select`, Then they pass.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: None
