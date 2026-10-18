# PLAN-TRC-002: Call Graph in agnos-trace

## Overview
Add the optional tree-sitter call-graph analysis of FTR-TRC-002 to the `agnos-trace` skill: the optional module and its
language table, C/C++ functions and function-level IDs, call resolution, the page's data, panel, search and overview,
then the graph and its performance limits, and the skill's documentation.

## References
- **Requirements**: RQ-TRC-026 to RQ-TRC-040 (FTR-TRC-002)
- **ADRs**: ADR-TRC-004; ADR-TRC-001, ADR-TRC-002, ADR-TRC-003 (extended)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-TRC-009: Optional call-graph module and language table
- **Tier**: L
- **Status**: Done
- **Description**: Add `scripts/callgraph.py`, imported only with `--call-graph`, its py-tree-sitter adapter,
  `assets/callgraph/languages.json`, `requirements-callgraph.txt` (tree-sitter 0.25.2, tree-sitter-c 0.24.1,
  tree-sitter-cpp 0.23.4, to be confirmed when installed), and the "call graph skipped" path when a package is missing.
- **Requirement refs**: RQ-TRC-026, RQ-TRC-027, RQ-TRC-032, RQ-TRC-039
- **ADR refs**: ADR-TRC-004 (DEC-TRC-013, DEC-TRC-014)
- **Acceptance Criteria**: Given no tree-sitter, When the generator runs with `--call-graph`, Then it exits 0 and prints
  the install command; Given no `--call-graph`, Then the page equals the one before this plan and no tree-sitter module is
  imported; the stdlib-only and independence tests still pass.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `unittest discover` 45 tests OK (38 before + 7 of `test_callgraph.py`): with `tree_sitter` masked,
  `--call-graph` exits 0, "call graph skipped: tree-sitter not installed, run: pip install -r …requirements-callgraph.txt",
  page written; without the option the fixture data hashes to the value taken before this plan (c43656a2…) and a fresh
  interpreter has no `tree_sitter*` / `agnos_trace*` module; stdlib-only test passes on both scripts; pins equal the
  installed versions. Fixture run with the packages: "call graph: 0 functions, 0 calls, ambiguous 0, external 0" (both
  queries compile). IDE SonarQube: no finding.
- **Assumptions**: the two query files are written here because the table names them, their captures tested by
  TASK-TRC-010/011; the module is loaded by file path so the core script holds no non-stdlib import statement; the
  "same page" check compares the data block with the two machine-dependent paths blanked (assets change in TASK-TRC-012).

### TASK-TRC-010: C and C++ functions and their IDs
- **Tier**: M
- **Status**: Done
- **Description**: Write the C and C++ query files and extract each definition's qualified name, lines and first line,
  contained by its file, with the IDs of its lines and of the comment block just above it.
- **Requirement refs**: RQ-TRC-028, RQ-TRC-031, RQ-TRC-032
- **ADR refs**: ADR-TRC-004 (DEC-TRC-014, DEC-TRC-016)
- **Acceptance Criteria**: Given a fixture of `.c`, `.cpp` and `.hpp` files (free functions, methods defined in and out of
  their class, namespaces, constructors, operators), When analysed, Then every definition is found with its qualified name
  and lines, and a `///` ID above a function links that function.
- **Dependencies**: TASK-TRC-009
- **Assignee**: AI
- **Verification**: `unittest discover` 49 tests OK; `FunctionsTest` on `tests/fixtures/repo/calls` (`.c`, `.cpp`, `.hpp`):
  the 11 definitions in file then line order with qualified names and lines (in-class and out-of-class methods,
  namespace, constructor, `operator==`, `int **` return); key `fn:calls/net/session.cpp:14`, language, first line; `///`,
  `//` and two-line `/* */` blocks just above link their function, a function without one has no ID, the file keeps its
  link. IDE SonarQube: no finding.
- **Assumptions**: a separate fixture folder `calls/` keeps the counts of the FTR-TRC-001 tests; a function's IDs are the
  file's own citations within its range (no second scan); a comment after code on its line starts no block; two
  definitions on one line get keys `…:<line>` and `…:<line>.2`.

### TASK-TRC-011: Call resolution
- **Tier**: M
- **Status**: Done
- **Description**: Find the call sites and resolve each called name with the preferences of DEC-TRC-015: one link, up to
  five ambiguous links, or an ambiguous / external count; the same order on every run.
- **Requirement refs**: RQ-TRC-029, RQ-TRC-030, RQ-TRC-040
- **ADR refs**: ADR-TRC-004 (DEC-TRC-015)
- **Acceptance Criteria**: Given the fixture, Then a call with one definition gives one link with its lines, `x.send()`
  with two candidates outside both classes gives two ambiguous links, `printf` counts as external, and two runs give the
  same page.
- **Dependencies**: TASK-TRC-010
- **Assignee**: AI
- **Verification**: `unittest discover` 55 tests OK; `CallResolutionTest`: `relay`→`log` one link lines 8, 9; `Port::send`→
  `Port::write` (its class) and not `Session::write`; `x.send()` / `port.write()` from `relay` two ambiguous links each;
  `printf` and `puts` external, `(*fp)()` not followed: "call graph: 11 functions, 8 calls, ambiguous 2, external 2"; six
  `f` in six folders: no link, ambiguous 1; two `--call-graph` pages identical. On a C++ code base: 1,908
  functions, 7,745 calls, +1.0 s. IDE SonarQube (checked live on a canary): no finding.
- **Assumptions**: candidates are taken in the caller's language only (cross-language calls are out of scope); a free
  function's "class" level is its namespace and the global scope is no level; ambiguous and external counts are per
  (caller, called name), as links are per callee.

### TASK-TRC-012: Functions in the page — data, panel, search, overview
- **Tier**: M
- **Status**: Done
- **Description**: Embed functions and calls in the compact arrays of DEC-TRC-016, build their adjacency at load, show
  callers, callees and IDs in the detail panel (first 50, more on request), the functions of a requirement, function
  search, the overview counts and the informational "Untraced functions" list.
- **Requirement refs**: RQ-TRC-033, RQ-TRC-035, RQ-TRC-038
- **ADR refs**: ADR-TRC-004 (DEC-TRC-016, DEC-TRC-018), ADR-TRC-002 (DEC-TRC-010)
- **Acceptance Criteria**: Given the fixture page in a headless browser, When a function is selected, Then the panel shows
  its callers and callees with counts and its IDs; When its requirement is selected, Then the function is listed; the
  call graph adds at most 120 bytes per function and 16 per call.
- **Dependencies**: TASK-TRC-011
- **Assignee**: AI
- **Verification**: `unittest discover` 62 tests OK; headless Edge: `net::Port::write` selected shows "Callers 2" (`relay`
  ambiguous, `net::Port::send`) and "Callees 0", `net::Port::send` its requirement and location; that requirement
  selected lists "Function 1"; searching "port::wr" finds the function; overview "Call graph" card ("8 call links"), "Untraced
  functions" listed, Gaps tab count = sum of the counted gaps. Size: fixture within 120 B/function + 16 B/call; a C++ code base
  +331,839 bytes for 1,908 functions and 7,745 calls (budget 352,880). Screenshots light/dark checked. IDE SonarQube: no
  finding.
- **Assumptions**: the Functions column and its filter off at load are done here (a Function type without its column
  would break the graph), TASK-TRC-013 keeps the call edges and the limits; the search finds functions even while
  their type filter is off (that filter keeps them out of the graph only); a function's ID proofs are its file's.

### TASK-TRC-013: Functions in the graph, within its limits
- **Tier**: M
- **Status**: Done
- **Description**: Add the "Functions" column (type filter off at load), call edges in `haystack` style hidden while
  panning, ambiguous calls dashed, the 400-node cap with its status message; measure on a generated 20,000-function,
  100,000-call page.
- **Requirement refs**: RQ-TRC-034, RQ-TRC-036, RQ-TRC-037
- **ADR refs**: ADR-TRC-004 (DEC-TRC-017), ADR-TRC-003 (DEC-TRC-006)
- **Acceptance Criteria**: Given the generated page, When a much-called function is selected at depth 2 with functions on,
  Then at most 400 nodes are drawn within 500 ms and the status line gives the number not drawn; the page is interactive
  within 3 s; the analysis adds at most 30 s on 2,000 files.
- **Dependencies**: TASK-TRC-012
- **Assignee**: AI
- **Verification**: `unittest discover` with `AGNOS_TRACE_PERF=1`: 65 tests OK. `FunctionGraphTest`: the fixture's first requirement
  drawn with one node more once Functions is on; `net::Port::write` with functions on: "4 elements · 5 links". Generated tree
  (2,000 files, 20,002 functions, 100,000 calls): run 1.5 s, with the call graph 3.6 s (+2.1 s, limit 30 s); page +1,858,549
  bytes (limit 4.0 MB); interactive 177 ms after opening (limit 3 s); `hub` at depth 2: 74 nodes in 106 ms, "21928 not
  drawn". Screenshots of a function's and a requirement's graph on a C++ code base checked. IDE SonarQube: no finding.
- **Assumptions**: the 400-node limit is applied before the column cap of 72, which stays (DEC-TRC-017); a recursive call
  is not drawn (a haystack edge cannot loop); the large test runs only with `AGNOS_TRACE_PERF=1` (about a minute); around
  a selected function its column splits into callers, function, callees (recorded in DEC-TRC-017).

### TASK-TRC-014: Documentation and run on this repository
- **Tier**: M
- **Status**: Done
- **Description**: Document `--call-graph`, the requirements file and the language table in SKILL.md and AGENTS.md, and
  run the skill with the call graph on this repository.
- **Requirement refs**: RQ-TRC-017, RQ-TRC-026
- **ADR refs**: ADR-TRC-004 (DEC-TRC-013)
- **Acceptance Criteria**: Given this repository, When the documented command runs with `--call-graph`, Then the page holds
  the call graph of a C++ code base and the summary line gives its counts.
- **Dependencies**: TASK-TRC-013
- **Assignee**: AI
- **Verification**: re-tiered S to M (documentation beyond 5 lines). The AGENTS.md command with `--call-graph` exits 0:
  "577 elements, 325 files; RQ 225: covered 205, indirect 17, uncovered 3 (three product coverage items, outside this
  plan); … call graph: 1908 functions, 7745 calls, ambiguous 1242, external 2806"; no TRC requirement uncovered, no
  undefined TRC ID. `unittest discover` 65 tests OK (1 skipped: the large measure), the independence test included.
- **Assumptions**: only a C++ code base gets functions here: the skill's own sources are Python and JavaScript, languages with no
  entry in the table yet.

### TASK-TRC-015: Functions in the matrix, the graph toolbar and the requirement panel
- **Tier**: M
- **Status**: Done
- **Description**: Add the matrix's "Functions" column (cells, sort, CSV), the graph toolbar's "Functions" switch bound to
  the type filter, and "Functions 0" with its file-level note in a requirement's panel; nothing of it without call graph.
- **Requirement refs**: RQ-TRC-041, RQ-TRC-014, RQ-TRC-033, RQ-TRC-034
- **ADR refs**: ADR-TRC-004 (DEC-TRC-017), ADR-TRC-003 (DEC-TRC-007), ADR-TRC-002 (DEC-TRC-010)
- **Acceptance Criteria**: as RQ-TRC-041.
- **Dependencies**: TASK-TRC-014
- **Assignee**: AI
- **Verification**: `unittest discover` 69 tests OK (1 skipped: the large measure). `FunctionMatrixTest` in headless Edge:
  "Functions" column header, the function listed in its requirement's row, CSV header and row with it; the toolbar
  switch turns the type filter's chip on; an uncited requirement shows "Functions 0"; a page without call graph shows
  none of the three. Screenshot of the matrix on a C++ code base checked. IDE SonarQube: no finding.
- **Assumptions**: added after the owner's review of the page (the plan had left the matrix out); the panel's note says
  "cited at file level only" when a source file cites the requirement, else "no function cites it".

### TASK-TRC-016: Scrollbars for the matrix and the graph
- **Tier**: M
- **Status**: Done
- **Description**: Give the matrix a token minimum width, so that its frame scrolls instead of cutting IDs, and put the
  graph in a scrolling frame whose canvas grows to the flow drawn at its readable zoom.
- **Requirement refs**: RQ-TRC-042, RQ-TRC-012, RQ-TRC-014, RQ-TRC-018
- **ADR refs**: ADR-TRC-003 (DEC-TRC-006, DEC-TRC-012), ADR-TRC-002 (DEC-TRC-010)
- **Acceptance Criteria**: as RQ-TRC-042.
- **Dependencies**: TASK-TRC-015
- **Assignee**: AI
- **Verification**: `unittest discover` 70 tests OK (1 skipped: the large measure). `ScrollTest`, side panels at their
  maximum, headless Edge: matrix frame scrolls, table 1180 px (its token minimum); depth-3 graph: canvas 1031 px in a
  430 px frame that scrolls, zoom 0.80 (the readable floor). Screenshots of the matrix and a depth-2 graph on a C++ code base
  checked. IDE SonarQube: no finding.
- **Assumptions**: asked by the owner during the session; vertical scrolling comes with it; the depth buttons now
  redraw only a visible graph (drawing into the hidden frame left the zoom unfitted, found by this task's test).

### TASK-TRC-017: Matrix headers aligned with their cells
- **Tier**: S
- **Status**: Done
- **Description**: The list columns (ADRs / decisions, Plans / tasks, Functions, Source files) sort by count but show
  IDs: their headers align left like their cells; only Lines stays right-aligned (owner review of the page).
- **Requirement refs**: RQ-TRC-014, RQ-TRC-041, RQ-TRC-018
- **ADR refs**: ADR-TRC-002 (DEC-TRC-011)
- **Acceptance Criteria**: Given the matrix, Then each list column's header starts above its cells' IDs and "Lines"
  stays right-aligned.
- **Dependencies**: TASK-TRC-016
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: None

### TASK-TRC-018: Resizable matrix columns
- **Tier**: M
- **Status**: In Progress
- **Description**: A focusable grip at the right edge of each matrix header: drag or arrow keys change that column's width
  (token minimum, token step), widths kept in the browser, double-click restores the defaults, the grip never sorts.
- **Requirement refs**: RQ-TRC-043, RQ-TRC-014, RQ-TRC-018
- **ADR refs**: ADR-TRC-003 (DEC-TRC-012), ADR-TRC-002 (DEC-TRC-010)
- **Acceptance Criteria**: as RQ-TRC-043.
- **Dependencies**: TASK-TRC-017
- **Assignee**: AI
- **Verification**:
- **Assumptions**:
