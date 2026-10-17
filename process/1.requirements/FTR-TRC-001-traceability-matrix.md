# FTR-TRC-001: AGNOS Traceability Matrix

## Overview
A skill, `agnos-trace`, that reads an AGNOS process folder (the one holding `INDEX.idx.md`) and one or more source
folders, and writes a self-contained HTML page: the complete traceability matrix of the requirements, ADRs, decisions,
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
  output path (default `<process>/TRACEABILITY.html`), and SHALL write the page at that path.
- **Rationale**: one command, run from any project, gives the page.
- **Priority**: Must
- **Acceptance Criteria**: Given a process folder and a source folder, When `python <skill>/scripts/trace_matrix.py
  --process process --sources src` runs, Then it exits 0 and the page exists at `process/TRACEABILITY.html`.
- **Dependencies**: DEC-TRC-001

### RQ-TRC-002: Missing or unreadable inputs
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: IF the process folder has no `INDEX.idx.md`, or a source folder does not exist, THEN the trace generator
  SHALL write nothing, print the cause on the error stream and exit with code 1.
- **Rationale**: a page built from a partial input would show false gaps.
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
- **Rationale**: an uncovered requirement is the gap the matrix exists to show.
- **Priority**: Must
- **Acceptance Criteria**: Given RQ-X-001 cited by a source file, RQ-X-002 cited only by TASK-X-001 which a source file
  cites, and RQ-X-003 cited by no source and no linked element, Then they are rated covered, indirect and uncovered.
- **Dependencies**: DEC-TRC-004

### RQ-TRC-009: Gaps
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The trace generator SHALL list, each with its count and IDs: uncovered requirements; requirements no task
  references; tasks that reference no requirement; ADRs that, with their decisions, reference no requirement; features,
  ADRs and plans that contain nothing; elements with no link other than containment; undefined IDs; source files that
  reference no ID.
- **Rationale**: each list is a breach of an AGNOS traceability rule.
- **Priority**: Must
- **Acceptance Criteria**: Given a fixture process with one element of each gap, When the page is built, Then each gap list
  holds exactly that element.
- **Dependencies**: DEC-TRC-004

### RQ-TRC-010: Self-contained page
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The trace generator SHALL write one HTML file that holds all its data, styles, scripts and graph library
  inline, and that requests nothing over the network when it is opened.
- **Rationale**: the page is mailed, attached and opened offline.
- **Priority**: Must
- **Acceptance Criteria**: Given a generated page, When it is searched for `<script src`, `<link` and `url(http`, Then none is
  found, and the page works with the network off.
- **Dependencies**: DEC-TRC-005, DEC-TRC-006

### RQ-TRC-011: Search
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the user types in the search field, the page SHALL list the elements whose ID, title or file path
  contains the text, and WHEN the user picks a result, the page SHALL select that element.
- **Rationale**: an ID or a file name is how a reader enters the matrix.
- **Priority**: Must
- **Acceptance Criteria**: Given the text "a.py", When it is typed, Then `src/a.py` is listed; When it is picked, Then it is
  selected in the graph and the detail panel.
- **Dependencies**: RQ-TRC-012, RQ-TRC-013

### RQ-TRC-012: Interactive graph
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN an element is selected, the page SHALL draw it with its linked elements up to the chosen depth (1 to
  3), each type with its own colour and shape, highlight the element and its direct links, fade the others, and select
  any element the user clicks; the whole graph SHALL be drawable on request.
- **Rationale**: navigating links is faster on a graph than in tables.
- **Priority**: Must
- **Acceptance Criteria**: Given a requirement linked to one decision and one file, When it is selected at depth 1, Then the
  graph shows those three elements; When the file is clicked, Then the file becomes the selection.
- **Dependencies**: DEC-TRC-006, RQ-TRC-022

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
- **Dependencies**: RQ-TRC-005, RQ-TRC-006

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
- **Dependencies**: RQ-TRC-008

### RQ-TRC-015: Overview
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The page SHALL open on an overview giving the count of each element type, the share of requirements
  covered, indirectly covered and uncovered, the count of each gap, and the coverage per trigram.
- **Rationale**: the state of traceability at a glance.
- **Priority**: Should
- **Acceptance Criteria**: Given 10 requirements of which 7 are covered, When the page opens, Then the overview shows 70 %
  covered.
- **Dependencies**: RQ-TRC-008, RQ-TRC-009

### RQ-TRC-016: Deep links and history
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN an element is selected, the page SHALL put its ID in the URL fragment, and WHEN the page opens with a
  fragment or the browser goes back or forward, the page SHALL select the element it names.
- **Rationale**: a link to one element can be sent; back undoes a navigation.
- **Priority**: Should
- **Acceptance Criteria**: Given `TRACEABILITY.html#RQ-X-002`, When it is opened, Then RQ-X-002 is selected.
- **Dependencies**: RQ-TRC-012

### RQ-TRC-017: Skill procedure
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The skill SHALL give, for GitHub Copilot and Claude Code, the command per platform, its arguments, its exit
  codes and how to read the result.
- **Rationale**: agents run it the way they run the other AGNOS skills.
- **Priority**: Must
- **Acceptance Criteria**: Given an agent that loads the skill, When it follows the procedure, Then it produces the page and
  reports the gap counts printed by the generator.
- **Dependencies**: DEC-TRC-008

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
