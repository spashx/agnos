# FTR-TRC-002: Call Graph in the Traceability Matrix

## Overview
An optional analysis of the `agnos-trace` skill (FTR-TRC-001) that reads the scanned source files with tree-sitter and
adds the application's **call graph** to the matrix: one element per function or method, a link from each function to
the functions it calls, and a link from a function to the requirement IDs written in it or in the comment just above
it. Functions are an element type like the others ("Function"): searchable, shown in the detail panel, drawn in the graph
in their own column. The analysis is syntactic (no build, no types): calls are resolved by name and an ambiguous call is
shown as such. Languages are plug-ins; C and C++ come first. Out of scope: macros expanded, virtual dispatch, calls
through function pointers or callbacks, a call graph across languages (ADR-TRC-004).

## Stakeholders
- **Owner**: the repository owner.
- **Consumers**: reviewers asking "which functions implement this requirement, and what calls them"; agents doing impact
  analysis before a change; the matrix page (FTR-TRC-001), whose graph must stay fast with thousands of functions.

---

## Functional Requirements

### RQ-TRC-026: Opt-in analysis
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the trace generator is run with `--call-graph`, it SHALL parse the scanned source files of every
  supported language with tree-sitter and add their functions and calls to the page; without the option, the page SHALL
  be the one FTR-TRC-001 describes, byte for byte.
- **Rationale**: the analysis costs time and needs packages the matrix does not; it is asked for, not imposed.
- **Priority**: Must
- **Acceptance Criteria**: Given the fixture, When the generator runs without `--call-graph`, Then the page equals the one
  of the same run before this feature; When it runs with it, Then the page holds the fixture's functions.
- **Dependencies**: RQ-TRC-006, DEC-TRC-013

### RQ-TRC-027: Missing parser
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: IF `--call-graph` is given and the tree-sitter package or the grammar package of a language is not
  installed, THEN the trace generator SHALL write the page without the functions of that language, print the missing
  package and the command that installs it, and exit with code 0.
- **Rationale**: a missing optional package must not cost the matrix.
- **Priority**: Must
- **Acceptance Criteria**: Given no tree-sitter installed, When the generator runs with `--call-graph`, Then it exits 0,
  the summary line says "call graph skipped" with the `pip install` command, and the page is written.
- **Dependencies**: DEC-TRC-013

### RQ-TRC-028: Function elements
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The trace generator SHALL make one element of type Function of every function and method definition it
  parses, with its qualified name (namespace and class included), language, file, line range and the text of its first
  line, contained by its source file.
- **Rationale**: the function is the unit a reviewer reads and an agent changes.
- **Priority**: Must
- **Acceptance Criteria**: Given `src/lib/b.cpp` defining `int Session::send()` at lines 10-20, When the page is built, Then
  a Function `Session::send` with lines 10-20 is contained by `src/lib/b.cpp`.
- **Dependencies**: RQ-TRC-026, DEC-TRC-014, DEC-TRC-016

### RQ-TRC-029: Calls
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The trace generator SHALL link each function to every function it calls, once per callee, with the line
  numbers of the call sites, resolving the called name to the definitions of that name in this order of preference: same
  class, same namespace, same file, same folder, the whole project.
- **Rationale**: a call graph without the call sites cannot be checked against the code.
- **Priority**: Must
- **Acceptance Criteria**: Given `a()` calling `b()` on lines 4 and 9 with one `b` defined in the project, When the page is
  built, Then one call link joins `a` to `b` with lines 4 and 9.
- **Dependencies**: RQ-TRC-028, DEC-TRC-015

### RQ-TRC-030: Ambiguous and external calls
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: IF a called name still matches several definitions after the preferences of RQ-TRC-029, THEN the trace
  generator SHALL link the call to each of them, up to five, marked ambiguous, and count it as ambiguous beyond five; IF it
  matches none, THEN the generator SHALL count it as external (library, system) and make no link.
- **Rationale**: a syntactic analysis cannot know the type of a receiver; it says so instead of guessing.
- **Priority**: Must
- **Acceptance Criteria**: Given `x.send()` where `Port::send` and `Session::send` both exist and the caller is in neither
  class, When the page is built, Then two call links are drawn, both marked ambiguous; Given a call to `printf`, Then no
  link is made and the external count includes it.
- **Dependencies**: RQ-TRC-029, DEC-TRC-015

### RQ-TRC-031: Requirement IDs at function level
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The trace generator SHALL link a function to every AGNOS ID written in its line range or in the comment
  block that ends on the line just above it, with the lines, in addition to the link of its file (RQ-TRC-006).
- **Rationale**: AGNOS puts requirement IDs in doc comments; the function is where they belong.
- **Priority**: Must
- **Acceptance Criteria**: Given `/// RQ-X-002` on the line above `void f()`, When the page is built, Then `f` is linked to
  RQ-X-002, and its file still is.
- **Dependencies**: RQ-TRC-028, DEC-TRC-016

### RQ-TRC-032: Language plug-ins
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The call-graph analysis SHALL take each language from one entry of a language table (file extensions,
  grammar package, query file) and one tree-sitter query file naming its definitions, calls and scopes, so that adding a
  language changes no code; C and C++ SHALL be delivered.
- **Rationale**: the skill is for any AGNOS project, in any language tree-sitter reads.
- **Priority**: Must
- **Acceptance Criteria**: Given the table and the C and C++ query files, When the fixture's `.c`, `.cpp` and `.hpp` files are
  analysed, Then their functions and calls are found; Given a new entry and query file for a language, Then its files are
  analysed with no change to the scripts.
- **Dependencies**: DEC-TRC-014

### RQ-TRC-033: Functions in the detail panel and the search
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN a function is selected, the page SHALL show its qualified name, file, lines and first line, its
  callers and callees (count and names, ambiguous ones marked), and the IDs it cites; WHEN a requirement is selected, the
  page SHALL list the functions that cite it; the search SHALL find functions by name.
- **Rationale**: "what implements this requirement, what calls it" in one click.
- **Priority**: Must
- **Acceptance Criteria**: Given a function called by two functions and citing RQ-X-002, When it is selected, Then the
  panel shows "Callers 2" and the requirement; When RQ-X-002 is selected, Then the function is listed under "Functions".
- **Dependencies**: RQ-TRC-013, RQ-TRC-028 to RQ-TRC-031

### RQ-TRC-034: Functions in the graph
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE the Function type is enabled in the type filters (it is off when the page opens), the graph SHALL
  draw functions in a "Functions" column between "Plans · tasks" and "Source files", calls with a line style of their own
  and ambiguous calls distinguished from the others.
- **Rationale**: thousands of functions must not crowd every neighbourhood unless the reader asks for them.
- **Priority**: Must
- **Acceptance Criteria**: Given the page just opened, When a requirement cited by two functions is selected, Then the graph
  shows no function; When the Function filter is turned on, Then the two functions appear in their column.
- **Dependencies**: RQ-TRC-012, DEC-TRC-017

### RQ-TRC-035: Call graph in the overview and the gaps
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The page SHALL show in its overview the count of functions, call links, ambiguous and external calls,
  and SHALL list as an informational gap, not counted in the gap total, the functions that cite no ID.
- **Rationale**: the share of traced functions is useful; it is not an AGNOS rule breach.
- **Priority**: Should
- **Acceptance Criteria**: Given the fixture, When the page opens, Then the overview gives its function and call counts and
  the gap list "Untraced functions" holds its untraced functions without changing the Gaps tab's count.
- **Dependencies**: RQ-TRC-009, RQ-TRC-015

---

## Non-Functional Requirements

### RQ-TRC-036: Analysis time
- **Category**: Non-Functional
- **NFR Type**: Performance
- **EARS Type**: Ubiquitous
- **Statement**: The call-graph analysis SHALL add at most 30 s to a run on 2,000 source files holding 20,000 functions.
- **Metric**: run time with `--call-graph` minus run time without it ≤ 30 s.
- **Measurement Method**: `Measure-Command` / `time` on this repository and on a generated 2,000-file fixture.
- **Priority**: Should
- **Acceptance Criteria**: Given this repository, When the generator runs with and without `--call-graph`, Then the
  difference is under 30 s.
- **Dependencies**: DEC-TRC-013

### RQ-TRC-037: Page responsiveness with a call graph
- **Category**: Non-Functional
- **NFR Type**: Performance
- **EARS Type**: Ubiquitous
- **Statement**: With 20,000 functions and 100,000 call links, the page SHALL be interactive within 3 s, SHALL redraw a
  selection within 500 ms and SHALL never draw more than 400 nodes in the flow graph, saying how many it left out.
- **Metric**: time to interactive ≤ 3 s; redraw ≤ 500 ms at depth 2 with functions on; drawn nodes ≤ 400.
- **Measurement Method**: the page's own timings (status line, console) on a generated 20,000-function page, in headless
  Edge.
- **Priority**: Must
- **Acceptance Criteria**: Given the generated page, When a much-called function is selected at depth 2, Then it is drawn
  within 500 ms with at most 400 nodes and the status line gives the number not drawn.
- **Dependencies**: DEC-TRC-016, DEC-TRC-017

### RQ-TRC-038: Page size
- **Category**: Non-Functional
- **NFR Type**: Performance
- **EARS Type**: Ubiquitous
- **Statement**: The call graph SHALL add to the page at most 120 bytes per function and 16 bytes per call link on average.
- **Metric**: (page size with − page size without) ≤ 120 × functions + 16 × calls.
- **Measurement Method**: generate both pages of this repository and of the generated fixture, compare their sizes.
- **Priority**: Should
- **Acceptance Criteria**: Given 20,000 functions and 100,000 calls, Then the call graph adds at most 4 MB.
- **Dependencies**: DEC-TRC-016

### RQ-TRC-039: Optional dependency, unchanged independence
- **Category**: Non-Functional
- **NFR Type**: Portability
- **EARS Type**: Ubiquitous
- **Statement**: The trace generator SHALL import tree-sitter only when `--call-graph` is given, SHALL pin the versions of
  the packages it supports in one requirements file of the skill, and SHALL still hold no term of the product developed.
- **Metric**: the stdlib-only test of RQ-TRC-021 still passes for the core script; the independence test of RQ-TRC-019
  still passes on the whole skill.
- **Measurement Method**: the existing tests; a run without tree-sitter installed.
- **Priority**: Must
- **Acceptance Criteria**: Given a Python without tree-sitter, When the generator runs without `--call-graph`, Then it works
  as before and imports no tree-sitter module.
- **Dependencies**: RQ-TRC-019, RQ-TRC-021, DEC-TRC-013

### RQ-TRC-040: Reproducible call graph
- **Category**: Non-Functional
- **NFR Type**: Reliability
- **EARS Type**: Ubiquitous
- **Statement**: The call-graph analysis SHALL give the same functions and links, in the same order (file path, then line),
  for the same sources and package versions.
- **Metric**: two runs with one `--generated-at`, same SHA-256.
- **Measurement Method**: the reproducibility test of RQ-TRC-023 run with `--call-graph`.
- **Priority**: Must
- **Acceptance Criteria**: Given the fixture, When the generator runs twice with `--call-graph`, Then the pages are identical.
- **Dependencies**: RQ-TRC-023
