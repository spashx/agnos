# FTR-TRC-001: AGNOS Traceability Matrix
<!-- Amended on 2026-11-22: the performance center's outputs are lowercase, perf-center.* (RQ-TRC-143, DEC-TRC-087). -->
<!-- Amended on 2026-10-31: the skill, its script and its outputs carry their current names (RQ-TRC-104, RQ-TRC-105, DEC-TRC-055). -->

## Overview
A skill, `agnos-perf-center`, that reads an AGNOS process folder (the one holding `INDEX.idx.md`) and one or more source
folders, and writes an offline HTML page, its data beside it (RQ-TRC-010): the complete traceability matrix of the requirements, ADRs, decisions,
plans and tasks of the process, and of the source files and lines that reference them. The page searches, navigates and
highlights an element and its linked elements through an interactive graph, and lists the elements that are not linked
(a requirement that no source file references, a task that implements no requirement…). The skill knows the AGNOS ID
grammar and the `INDEX.idx.md` format only: nothing of the product being developed (ADR-TRC-001, ADR-TRC-002,
ADR-TRC-003).

## Stakeholders
- **Owner**: the repository owner.
- **Consumers**: the owner and reviewers reading the page; AI agents running the skill at the end of a session or before
  a release; the AGNOS process, whose MANDATORY TRACEABILITY rule the page checks.

---

## Functional Requirements

### RQ-TRC-001: Command-line inputs and output
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The trace generator SHALL take a process folder holding `INDEX.idx.md`, one or more source folders and an
  output path (default `<process>/perf-center.html`), and SHALL write the page at that path.
- **Rationale**: one command, run from any project, gives the page.
- **Priority**: Must
- **Acceptance Criteria**: Given a process folder and a source folder, When `python <skill>/scripts/perf_center.py
  --process process --sources src` runs, Then it exits 0 and the page exists at `process/perf-center.html`.
- **Dependencies**: DEC-TRC-001

### RQ-TRC-119: What is scanned and excluded is always shown
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The `agnos-graph` skill, which scans the sources since FTR-TRC-011 (RQ-TRC-129; owner, 2026-11-22), SHALL show the scanned extensions, the always-scanned file names and the excluded patterns
  in its `--help`, with the default lists, and on every run in one line each before the summary line, each line saying whether
  the list is the default or the user's (`--ext`, `--exclude` replace the default list, at the user's own responsibility); the
  skill SHALL have those lines reported with the summary line, so that a user calling the skill through an AI learns them too.
- **Rationale**: the user must understand what the tool reads and skips, whether they call it or an AI does (owner, 2026-11-07).
- **Priority**: Must
- **Acceptance Criteria**: Given `--help`, Then the help of `--ext` and `--exclude` lists every default entry and says it
  replaces it; Given a run without them, Then stdout holds `scanned extensions (default):`, `scanned names (always):` and
  `excluded (default):` lines with every default entry, before an unchanged summary line; Given `--exclude "*.md"`, Then stdout
  holds `excluded (user): *.md`; Given `SKILL.md`, Then its Report step names those lines.
- **Dependencies**: RQ-TRC-001, RQ-TRC-006, DEC-TRC-001, RQ-TRC-129

### RQ-TRC-002: Missing or unreadable inputs
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: IF the process folder has no `INDEX.idx.md`, or a source folder does not exist, THEN the trace generator
  SHALL write nothing, print the cause on the error stream and exit with code 1.
- **Rationale**: a page built from a partial input would show false findings.
- **Priority**: Must
- **Acceptance Criteria**: Given a process folder without `INDEX.idx.md`, When the generator runs, Then it exits 1, names
  the missing file, and no output file is created.
- **Dependencies**: RQ-TRC-001

### RQ-TRC-003: Process artifacts from the index
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The trace generator SHALL make one element of every row of `INDEX.idx.md`, with its ID, type (FTR, RQ, ADR,
  DEC, PLAN, TASK), trigram, document, line range, status and title.
- **Rationale**: the index is the AGNOS source of truth for what exists and where.
- **Priority**: Must
- **Acceptance Criteria**: Given an index of N rows, When the page is built, Then it holds N process elements, each with its
  document and line range.
- **Dependencies**: DEC-TRC-002, DEC-TRC-003

### RQ-TRC-004: Containment links
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The trace generator SHALL link each element to the element of the same document whose line range most
  closely encloses its own (a feature to its requirements, an ADR to its decisions, a plan to its tasks).
- **Rationale**: the document structure is a link the text does not repeat.
- **Priority**: Must
- **Acceptance Criteria**: Given RQ-X-002 at lines 20-30 inside FTR-X-001 at lines 1-90, When the page is built, Then a
  containment link joins FTR-X-001 to RQ-X-002.
- **Dependencies**: DEC-TRC-003

### RQ-TRC-005: Process references
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The trace generator SHALL link an element to every AGNOS ID written in its own lines (its range without
  the ranges of the elements it contains), a range written `<ID-a> to <ID-b>` (or with `–`, `..`) counting as every
  defined ID of the same type and trigram between the two.
- **Rationale**: Dependencies, ADR refs and Requirement refs fields are written as IDs, often as ranges.
- **Priority**: Must
- **Acceptance Criteria**: Given a task whose lines say "RQ-X-001 to RQ-X-003", When the page is built, Then the task is
  linked to RQ-X-001, RQ-X-002 and RQ-X-003, and its parent plan is not.
- **Dependencies**: DEC-TRC-003

### RQ-TRC-006: Source references
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The trace generator SHALL scan every file of the source folders whose extension or name is in its source
  list and whose path matches no exclusion, and SHALL link the file to every AGNOS ID it contains (ranges expanded as in
  RQ-TRC-005), keeping for each link the line numbers and the text of those lines.
- **Rationale**: the AGNOS rule puts requirement IDs in file headers, doc comments and test names.
- **Priority**: Must
- **Acceptance Criteria**: Given `src/a.py` whose line 12 says `# RQ-X-002`, When the page is built, Then `src/a.py` is linked
  to RQ-X-002 with line 12 and its text.
- **Dependencies**: DEC-TRC-003

### RQ-TRC-007: Dangling references
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: IF a process element or a source file references an ID that the index does not define, THEN the trace
  generator SHALL show that ID as an undefined element, linked to every place that references it.
- **Rationale**: a typo or a deleted requirement leaves code pointing at nothing.
- **Priority**: Must
- **Acceptance Criteria**: Given a source line citing RQ-X-099, not in the index, When the page is built, Then RQ-X-099 is
  listed as undefined with that file and line.
- **Dependencies**: RQ-TRC-005, RQ-TRC-006

### RQ-TRC-008: Requirement coverage
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The trace generator SHALL rate each requirement as covered (a source file references it), indirectly
  covered (no source file does, but one references a decision, task or ADR linked to it) or uncovered.
- **Rationale**: an uncovered requirement is the finding the matrix exists to show.
- **Priority**: Must
- **Acceptance Criteria**: Given RQ-X-001 cited by a source file, RQ-X-002 cited only by TASK-X-001 which a source file
  cites, and RQ-X-003 cited by no source and no linked element, Then they are rated covered, indirect and uncovered.
- **Dependencies**: DEC-TRC-004

### RQ-TRC-009: Findings of each rule
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The trace generator SHALL list, as the findings of a rule, each with its count and IDs: uncovered requirements; requirements no task
  references; tasks that reference no requirement; ADRs that, with their decisions, reference no requirement; features,
  ADRs and plans that contain nothing; elements with no link other than containment; undefined IDs; source files that
  reference no ID.
- **Rationale**: each list is a breach of an AGNOS traceability rule.
- **Priority**: Must
- **Acceptance Criteria**: Given a fixture process with one element of each finding, When the page is built, Then each rule's findings
  hold exactly that element.
- **Dependencies**: DEC-TRC-004

### RQ-TRC-010: Offline page, its data beside it
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The trace generator SHALL write the HTML page with its styles, scripts and graph library inline, and its
  data beside it in two files of the same name: `<page>.json`, the data alone, for any other tool, and `<page>.data.js`,
  the same data loaded by the page. The page SHALL load nothing but that sibling script, SHALL request nothing over the
  network, and SHALL work when opened from disk.
- **Rationale**: the page is opened offline and from disk; owner decision of 2026-10-18: the data out of the page is
  easier to maintain and lets the graph be used outside the page (a browser does not let a page opened from disk read a
  `.json` file, hence the `.js` twin).
- **Priority**: Must
- **Acceptance Criteria**: Given a generated page, When it is searched for `<script src`, `<link` and `url(http`, Then the
  only one found is `<script src="<page>.data.js">`; the `.json` file and the `.js` file hold the same data; the page
  works from disk with the network off; When the data script is missing, Then the page says which file it lacks.
- **Dependencies**: DEC-TRC-005, DEC-TRC-006
- **Amendment**: Amended by RQ-TRC-080 (FTR-TRC-005, owner review of 2026-10-28): the page also loads its two libraries from cdnjs.

### RQ-TRC-011: Search
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the user types in the search field, the page SHALL list the elements whose ID, title or file path
  contains the text, and WHEN the user picks a result, the page SHALL select that element.
- **Rationale**: an ID or a file name is how a reader enters the matrix.
- **Priority**: Must
- **Acceptance Criteria**: Given the text "a.py", When it is typed, Then `src/a.py` is listed; When it is picked, Then it is
  selected in the graph and the detail panel.
- **Dependencies**: RQ-TRC-018, ADR-TRC-002, RQ-TRC-012, RQ-TRC-013

### RQ-TRC-012: Interactive graph
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN an element is selected, the page SHALL draw it with its linked elements up to the chosen depth (1 to
  3), each type with its own colour and shape, highlight the element and its direct links, fade the others, and select
  any element the user clicks. (amended on 2026-11-07, ADR-TRC-015: the whole graph is no longer drawable on request —
  a force layout of every element was unreadable)
- **Rationale**: navigating links is faster on a graph than in tables.
- **Priority**: Must
- **Acceptance Criteria**: Given a requirement linked to one decision and one file, When it is selected at depth 1, Then the
  graph shows those three elements; When the file is clicked, Then the file becomes the selection.
- **Dependencies**: RQ-TRC-018, ADR-TRC-002, DEC-TRC-006, RQ-TRC-022

### RQ-TRC-013: Detail panel
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN an element is selected, the page SHALL show its type, ID, title, status, location (document and line
  range, or file path), its linked elements grouped by type with the count and IDs of each group, and, for source links,
  the file, line number and line text.
- **Rationale**: the "type, number and identifiers" of what is linked answer the reviewer's question.
- **Priority**: Must
- **Acceptance Criteria**: Given a requirement linked to two tasks and one file, When it is selected, Then the panel shows
  "TASK 2" with both IDs and "File 1" with its lines.
- **Dependencies**: RQ-TRC-018, ADR-TRC-002, RQ-TRC-005, RQ-TRC-006

### RQ-TRC-014: Matrix view
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The page SHALL show a table with one row per requirement giving its feature, the ADRs and decisions, plans
  and tasks linked to it, the source files and lines that reference it and its coverage, sortable by any column,
  filterable by the search text and exportable as CSV.
- **Rationale**: the classic requirements traceability matrix, for review and audit.
- **Priority**: Must
- **Acceptance Criteria**: Given the matrix, When "Export CSV" is pressed, Then a CSV file with one line per requirement and
  the same columns is downloaded.
- **Dependencies**: RQ-TRC-018, ADR-TRC-002, RQ-TRC-008

### RQ-TRC-015: Overview
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The page SHALL open on an overview giving the count of each element type, the share of requirements
  covered, indirectly covered and uncovered, the quality score and grade, the findings of each check, and the coverage per trigram.
- **Rationale**: the state of traceability at a glance.
- **Priority**: Should
- **Acceptance Criteria**: Given 10 requirements of which 7 are covered, When the page opens, Then the overview shows 70 %
  covered.
- **Dependencies**: RQ-TRC-018, ADR-TRC-002, RQ-TRC-008, RQ-TRC-009
- **Amendment**: Amended by TASK-TRC-075 (owner review of 2026-10-29): the coverage per trigram is the feature-areas
  chart of RQ-TRC-061, inside the requirement coverage card, a row's click showing the matrix filtered on its trigram.

### RQ-TRC-016: Deep links and history
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN an element is selected, the page SHALL put its ID in the URL fragment, and WHEN the page opens with a
  fragment or the browser goes back or forward, the page SHALL select the element it names.
- **Rationale**: a link to one element can be sent; back undoes a navigation.
- **Priority**: Should
- **Acceptance Criteria**: Given `perf-center.html#RQ-X-002`, When it is opened, Then RQ-X-002 is selected.
- **Dependencies**: RQ-TRC-018, ADR-TRC-002, RQ-TRC-012

### RQ-TRC-121: Deep link to a view
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the page opens with, or its URL fragment changes to, `#view=<name>`, the page SHALL show the view whose tab
  has that name, any tab the page shows being accepted with no list of names in the code; IF no shown tab has that name, THEN
  the page SHALL open on its default view as it does with no fragment.
- **Rationale**: a presentation or a message can send its reader straight to one view, such as the matrix, and a view added
  later is linkable as is (owner request of 2026-11-12).
- **Priority**: Should
- **Acceptance Criteria**: Given `perf-center.html#view=matrix`, When it is opened, Then the Matrix tab is selected and its view
  shown; Given each tab the page shows, Then `#view=<its name>` opens it; Given `#view=history` on a page built without
  `--history`, or `#view=unknown`, Then the Overview opens; Given `#RQ-X-002`, Then RQ-TRC-016 applies unchanged.
- **Dependencies**: RQ-TRC-016

### RQ-TRC-017: Skill procedure
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The skill SHALL give, for GitHub Copilot and Claude Code, the command per platform, its arguments, its exit
  codes and how to read the result.
- **Rationale**: agents run it the way they run the other AGNOS skills.
- **Priority**: Must
- **Acceptance Criteria**: Given an agent that loads the skill, When it follows the procedure, Then it produces the page and
  reports the quality score and the check scores printed by the generator.
- **Dependencies**: DEC-TRC-008
- **Amendment**: Refined by RQ-TRC-098 and RQ-TRC-102 (FTR-TRC-007, 2026-10-31): the skill holds its contract, 50 lines at most.

### RQ-TRC-018: Design system of the page
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The page's visual values (colours, type, spacing, radii, strokes, durations, graph styles) SHALL come from
  one machine-readable token file in three tiers (global, semantic, component), in a light and a dark theme, and no style
  sheet or script of the page SHALL hold a raw visual literal.
- **Rationale**: AGNOS MANDATORY DESIGN SYSTEM; one place to restyle a professional-looking page.
- **Priority**: Must
- **Acceptance Criteria**: Given the page's style sheet and script sources, When they are searched for `#hex`, `rgb(` and
  numeric `px` literals, Then none is found outside the token file.
- **Dependencies**: ADR-TRC-002

### RQ-TRC-025: Resizable panels
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the user drags one of the two splitter bars between the filters panel, the central views and the
  detail panel (or presses the left or right arrow key on a focused bar), the page SHALL change the width of that side
  panel, keep each panel between its minimum and maximum width from the design tokens, remember the widths in the browser,
  and restore the default widths when the bar is double-clicked.
- **Rationale**: a long title, a deep path or a wide graph needs room the default layout gives elsewhere.
- **Priority**: Should
- **Acceptance Criteria**: Given the page at its default widths, When the left bar is focused and the right arrow pressed
  three times, Then the filters panel is three keyboard steps wider; When the right bar is moved far past its limit, Then
  the detail panel stops at its maximum width; When the page is reopened, Then the widths are the ones left.
- **Dependencies**: RQ-TRC-018, ADR-TRC-002, DEC-TRC-012

### RQ-TRC-042: Scrolling the central views
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE the matrix or the drawn graph is wider (or taller) than the central area, the page SHALL keep the
  matrix columns at their minimum width from the design tokens and the graph at its readable zoom, and SHALL show a
  scrollbar on that area to reach the rest.
- **Rationale**: an ID cut to "ADR-AK" or a graph column out of reach cannot be read; the reader scrolls rather than
  guesses.
- **Priority**: Must
- **Acceptance Criteria**: Given the side panels at their maximum widths, When the matrix is shown, Then its frame
  scrolls horizontally and the table is not narrower than its token minimum; When a graph wider than the area is drawn,
  Then its frame scrolls horizontally and the zoom is not below the readable zoom.
- **Dependencies**: RQ-TRC-012, RQ-TRC-014, RQ-TRC-018, RQ-TRC-025, DEC-TRC-006, DEC-TRC-012

### RQ-TRC-043: Resizable matrix columns
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the user drags the grip at the right edge of a matrix column header (or presses the left or right
  arrow key on a focused grip), the page SHALL change that column's width by the pointer's move or one keyboard step,
  never below the minimum column width of the design tokens, leave the other columns as they are, remember the widths in
  the browser, and restore the default widths when a grip is double-clicked; a grip SHALL never sort the column.
- **Rationale**: a long title, qualified function names or deep paths need room the default widths give elsewhere.
- **Priority**: Should
- **Acceptance Criteria**: Given the matrix at its default widths, When the first column's grip is focused and the right
  arrow pressed three times, Then that column is three keyboard steps wider, the second keeps its width and the sort is
  unchanged; When the grip is double-clicked, Then the default widths come back.
- **Dependencies**: RQ-TRC-014, RQ-TRC-018, RQ-TRC-025, RQ-TRC-042, DEC-TRC-012

### RQ-TRC-044: Readable relations in the graph
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The graph SHALL draw each relation (specification hierarchy, defines, cites, cited in code, calls,
  ambiguous call; the first two named by RQ-TRC-048) with a colour of its own and a line style, an arrow from the
  container to the contained, from the file to the function it defines, from the citing to the cited and from
  the caller to the callee, and SHALL show in its legend a drawn sample of each line with its arrow and its meaning.
- **Rationale**: two relations drawn alike, or a call without direction, cannot be read.
- **Priority**: Must
- **Acceptance Criteria**: Given the page, When the graph's look of the relations is read, Then no two relations share
  a colour and every relation has an arrow; When the legend is shown, Then it has one drawn sample per
  relation, with no line-style word.
- **Dependencies**: RQ-TRC-012, RQ-TRC-018, RQ-TRC-034, DEC-TRC-006, DEC-TRC-017

### RQ-TRC-045: Explanatory tooltips
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The page SHALL give every control (view tabs, type and trigram filters, quality shortcuts, the graph
  toolbar's depth, switches, Fit, the coverage filter, Export CSV, the matrix headers, the detail panel's
  buttons, the overview tiles) a tooltip that says what it does or what it counts. (amended on 2026-11-07, ADR-TRC-015:
  Whole graph removed)
- **Rationale**: a reader new to the page learns it by pointing, not by reading a manual.
- **Priority**: Should
- **Acceptance Criteria**: Given the page, When its controls are read, Then each one listed has a non-empty title.
- **Dependencies**: RQ-TRC-018, ADR-TRC-002, RQ-TRC-010 to RQ-TRC-016

### RQ-TRC-046: A relation's tooltip
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the pointer rests on a link of the graph for the delay of the design tokens (1 s), the page SHALL
  show next to it the relation's meaning, its two ends in their direction, and its count of proof lines, and SHALL hide
  it when the pointer leaves the link or the graph moves.
- **Rationale**: a link in a dense graph is told apart by pointing at it, not by following it.
- **Priority**: Should
- **Acceptance Criteria**: Given a function's graph with functions on, When the tooltip of the call from
  `net::Port::send` to `net::Port::write` is asked, Then it says "calls (caller → callee)" with both names in that
  order; Given the tokens, Then the delay is 1 s.
- **Dependencies**: RQ-TRC-018, ADR-TRC-002, RQ-TRC-012, RQ-TRC-044, RQ-TRC-045

### RQ-TRC-049: A search result's full text
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the pointer rests on a result of the search list, or the keyboard moves onto one, for the quick
  delay of the design tokens (300 ms), the page SHALL show beside the list the result's type, its whole name, its whole
  title and its location, wrapped and not truncated, and SHALL hide it when the pointer leaves the list, the keyboard
  moves again, the search closes or a result is picked.
- **Rationale**: names and titles are cut to the list's width; a long function name or a title is read in full without
  selecting it.
- **Priority**: Should
- **Acceptance Criteria**: Given a search whose result's name is longer than the list, When the result is pointed at,
  Then, after the delay, a tooltip holds its type, whole name, whole title and location; When the pointer leaves the
  list, Then it is gone; Given the tokens, Then the delay is 300 ms.
- **Dependencies**: RQ-TRC-018, ADR-TRC-002, RQ-TRC-011, RQ-TRC-045

### RQ-TRC-051: Matrix columns in the order of the specification
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The matrix SHALL show its columns, by default, in the order of the specification hierarchy: Feature,
  Requirement, Coverage, ADRs / decisions, Plans / tasks, then Functions (with a call graph), Source files and Lines.
- **Rationale**: a row reads from the feature that contains the requirement down to the code that implements it, as the
  graph's columns do.
- **Priority**: Should
- **Acceptance Criteria**: Given the page opened for the first time, When the matrix headers are read from left to
  right, Then they are Feature, Requirement, Coverage, ADRs / decisions, Plans / tasks, Source files, Lines (with
  Functions before Source files when the page has a call graph), and each cell stands under its own header.
- **Dependencies**: RQ-TRC-014, RQ-TRC-041, RQ-TRC-043, ADR-TRC-006, DEC-TRC-027

### RQ-TRC-052: Rearrangeable matrix columns
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the user drags a matrix column header onto another header (or presses Alt with the left or right
  arrow key on a focused header), the page SHALL move that column to the dropped position, keep every cell under its
  own header, leave the sort and the widths of the columns as they are, remember the order in the browser, and restore
  the default order and widths when the user presses the "Reset columns" button; a resize grip SHALL never start a move.
- **Rationale**: readers of the matrix care about different columns first (a developer the functions, a product owner
  the coverage), so the order is theirs to choose.
- **Priority**: Should
- **Acceptance Criteria**: Given the matrix at its default order, When the Coverage header is moved before the Feature
  header, Then Coverage is the first column with its cells, the sort and the widths are unchanged, and the order is
  still there after the page is reloaded; When "Reset columns" is pressed, Then the default order and widths come back.
- **Dependencies**: RQ-TRC-014, RQ-TRC-018, RQ-TRC-043, RQ-TRC-045, RQ-TRC-051, ADR-TRC-006, DEC-TRC-028

### RQ-TRC-053: A feature's title in the matrix
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The matrix SHALL show, under the ID of each feature in its Feature column, the feature's title, in the
  same way as it shows a requirement's title under the requirement's ID.
- **Rationale**: an ID such as FTR-BKG-001 says nothing; its title tells which feature a row belongs to without opening it.
- **Priority**: Should
- **Acceptance Criteria**: Given the matrix, When the row of a requirement is read, Then its Feature cell holds the
  feature's ID and, under it, the feature's title, and the title is cut with an ellipsis when the column is narrow.
- **Dependencies**: RQ-TRC-014, RQ-TRC-043, RQ-TRC-051, ADR-TRC-007, DEC-TRC-029

### RQ-TRC-054: A selected element that stays in view
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE an element is selected, the detail panel SHALL show the element's identity (type, ID, title,
  location, status and coverage, actions) and its tags (the count of its links by type) in a band that stands out from
  the links below it, by a larger title, a bar in the element's type colour and a tinted background, and SHALL keep that
  band fixed and visible at the top of the panel while only the links below it scroll.
- **Rationale**: the reader scrolling a long list of links must still see which element they belong to.
- **Priority**: Should
- **Acceptance Criteria**: Given a selected element with more links than the panel can show, When the links are
  scrolled down, Then the identity and the tags stay at the top of the panel, unmoved, and the links scroll under them;
  Given any selection, Then the band's title is larger than the link rows' text and its bar uses the type colour.
- **Dependencies**: RQ-TRC-016, RQ-TRC-018, RQ-TRC-025, ADR-TRC-002, ADR-TRC-007, DEC-TRC-030

### RQ-TRC-055: Tags that filter the links
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the user clicks a tag of the detail panel, the page SHALL show below it only the group of links
  that the tag counts (the tags clicked together show their groups together), mark the tag as pressed, show all the
  groups again when the pressed tag is clicked again, and drop the filter when another element is selected.
- **Rationale**: a requirement cited by hundreds of lines is read one type at a time.
- **Priority**: Should
- **Acceptance Criteria**: Given a requirement with ADRs, tasks and files, When the "Tasks" tag is clicked, Then only
  the Tasks group is shown and the tag is pressed; When it is clicked again, Then every group is shown; When another
  element is selected, Then no tag is pressed.
- **Dependencies**: RQ-TRC-016, RQ-TRC-033, RQ-TRC-041, RQ-TRC-045, RQ-TRC-047, RQ-TRC-054, ADR-TRC-007, DEC-TRC-030

### RQ-TRC-056: A finer wheel zoom in the graph
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the user turns the mouse wheel over the graph, the page SHALL zoom by a step smaller than the
  default of the graph library, the wheel sensitivity being a design token (0.1, about 10 % of zoom per wheel notch instead of 150 %), still within the minimum and maximum
  zoom of the tokens.
- **Rationale**: one notch of the default wheel jumps over the level of detail the reader wanted.
- **Priority**: Should
- **Acceptance Criteria**: Given the graph, When the wheel turns by one notch, Then the zoom changes by less than it
  did with the library's default sensitivity; Given the tokens, Then the wheel sensitivity is 0.1.
- **Dependencies**: RQ-TRC-012, RQ-TRC-018, ADR-TRC-002, ADR-TRC-007, DEC-TRC-031

---

## Non-Functional Requirements

### RQ-TRC-019: Independence from the product
- **Category**: Non-Functional
- **NFR Type**: Portability
- **EARS Type**: Ubiquitous
- **Statement**: The skill SHALL depend only on the AGNOS ID grammar and the `INDEX.idx.md` format, and SHALL hold no name,
  term or path of the product being developed.
- **Metric**: 0 occurrences of the product's names and domain terms in the skill folder; the tests use a synthetic process.
- **Measurement Method**: a test that scans the skill's scripts, assets and SKILL.md for the host project's terms.
- **Priority**: Must
- **Acceptance Criteria**: Given the skill folder, When the independence test runs, Then it finds no product term.
- **Dependencies**: DEC-TRC-001

### RQ-TRC-020: Generation and interaction time
- **Category**: Non-Functional
- **NFR Type**: Performance
- **EARS Type**: Ubiquitous
- **Statement**: The trace generator SHALL write the page in at most 10 s for 1,000 process elements and 2,000 source
  files, and the page SHALL be interactive within 3 s of opening and redraw a selection within 500 ms.
- **Metric**: generation wall-clock ≤ 10 s; time to interactive ≤ 3 s; selection redraw ≤ 500 ms, at depth 2.
- **Measurement Method**: `Measure-Command` / `time` on the host repository and on a generated 1,000-element fixture; the
  page's own timing printed to the console.
- **Priority**: Should
- **Acceptance Criteria**: Given the host repository, When the generator runs, Then it ends within 10 s.
- **Dependencies**: DEC-TRC-002, DEC-TRC-006

### RQ-TRC-021: Portability of generator and page
- **Category**: Non-Functional
- **NFR Type**: Portability
- **EARS Type**: Ubiquitous
- **Statement**: The trace generator SHALL run with Python 3.9 or later and its standard library only, on Windows, Linux and
  macOS, and the page SHALL work offline in the current versions of Chrome, Edge, Firefox and Safari.
- **Metric**: no import outside the standard library; no network request from the page.
- **Measurement Method**: read the imports; open the page in a headless browser with the network off.
- **Priority**: Must
- **Acceptance Criteria**: Given a machine with Python and no package installed, When the generator runs, Then it succeeds.
- **Dependencies**: DEC-TRC-001

### RQ-TRC-022: Safe display of scanned text
- **Category**: Non-Functional
- **NFR Type**: Security
- **EARS Type**: Ubiquitous
- **Statement**: The page SHALL insert every text taken from the process and source files as text, never as HTML, and the
  generator SHALL embed its data so that no file content can close the data block.
- **Metric**: 0 uses of `innerHTML` with data in the page script; a fixture line `</script><img src=x onerror=alert(1)>`
  renders as text.
- **Measurement Method**: a test on that fixture line; a search of the script for `innerHTML`.
- **Priority**: Must
- **Acceptance Criteria**: Given a source line holding `</script>`, When the page is opened, Then the line shows as text and
  no script runs.
- **Dependencies**: DEC-TRC-005

### RQ-TRC-023: Reproducible output
- **Category**: Non-Functional
- **NFR Type**: Reliability
- **EARS Type**: Ubiquitous
- **Statement**: The trace generator SHALL write byte-identical pages for the same inputs and the same `--generated-at`
  value, in UTF-8 with LF line endings.
- **Metric**: two runs, same SHA-256.
- **Measurement Method**: a test that runs twice on the fixture and compares the bytes.
- **Priority**: Must
- **Acceptance Criteria**: Given the fixture, When the generator runs twice with one `--generated-at`, Then the two files are
  identical.
- **Dependencies**: DEC-TRC-002

### RQ-TRC-024: Vendored library
- **Category**: Non-Functional
- **NFR Type**: Compliance
- **EARS Type**: Ubiquitous
- **Statement**: The skill SHALL hold the graph library at one pinned version, with its licence, its source URL and its
  SHA-256, and the page SHALL carry the library's licence notice.
- **Metric**: version, URL, SHA-256 and licence recorded; the hash of the vendored file matches.
- **Measurement Method**: a test that hashes the vendored file and compares it with the recorded value.
- **Priority**: Must
- **Acceptance Criteria**: Given the vendored file, When the test hashes it, Then the hash equals the recorded one.
- **Dependencies**: DEC-TRC-006
- **Amendment**: Superseded by RQ-TRC-082 (FTR-TRC-005, 2026-10-28): the libraries are loaded from cdnjs, recorded in `libraries.json`.
