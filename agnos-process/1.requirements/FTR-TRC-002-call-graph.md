# FTR-TRC-002: Call Graph in the Traceability Matrix
<!-- Amended on 2026-10-31: the skill, its script and its outputs carry their current names (RQ-TRC-104, RQ-TRC-105, DEC-TRC-055). -->

## Overview
An optional analysis of the `agnos-perf-center` skill (FTR-TRC-001) that reads the scanned source files with tree-sitter and
adds the application's **call graph** to the matrix: one element per function or method, a link from each function to
the functions it calls, and a link from a function to the requirement IDs written in it or in the comment just above
it. Functions are an element type like the others ("Function"): searchable, shown in the detail panel, drawn in the graph
in their own column. The analysis is syntactic (no build, no types): calls are resolved by name and an ambiguous call is
shown as such. Languages are plug-ins; C and C++ came first, then C#, Java, JavaScript, Python and Rust (RQ-TRC-050). Out of scope: macros expanded, virtual dispatch, calls
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
- **Dependencies**: RQ-TRC-018, ADR-TRC-002, RQ-TRC-013, RQ-TRC-028 to RQ-TRC-031

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
- **Dependencies**: RQ-TRC-018, ADR-TRC-002, RQ-TRC-012, DEC-TRC-017

### RQ-TRC-035: Call graph in the overview and the quality view
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The page SHALL show in its overview the count of functions, call links, ambiguous and external calls,
  and SHALL score, as an informational check that weighs nothing in the overall score and adds nothing to the findings total, the functions that cite no ID.
- **Rationale**: the share of traced functions is useful; it is not an AGNOS rule breach.
- **Priority**: Should
- **Acceptance Criteria**: Given the fixture, When the page opens, Then the overview gives its function and call counts and
  the check "Functions traced" holds its untraced functions without changing the Quality tab's count.
- **Dependencies**: RQ-TRC-009, RQ-TRC-015
- **Amendment**: Amended by TASK-TRC-076 (owner review of 2026-10-29): the counts are shown under the graph's frame,
  only while the implementation is drawn (RQ-TRC-048), and no longer in the overview.
- **Amended by**: RQ-PLG-024 (owner review of 2026-11-05) — "Functions traced" is a medium-risk check that weighs in the score
  and counts in the findings total.

### RQ-TRC-041: Functions in the matrix, the graph toolbar and every requirement's panel
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE the page holds a call graph, the matrix SHALL have a "Functions" column (the functions citing each
  requirement, sortable by their count, exported in the CSV), the graph toolbar SHALL have a "Functions" switch bound
  to the Function type filter, and a requirement's panel SHALL always show its function count, saying when the
  requirement is cited at file level only.
- **Rationale**: a traceability matrix that hides the function level of a requirement hides what the call graph is for.
- **Priority**: Must
- **Acceptance Criteria**: Given the fixture page with the call graph, When the matrix opens, Then the row of the
  requirement cited by `net::Port::send` lists that function under "Functions" and the CSV has a "Functions" column;
  When the toolbar's "Functions" switch is turned on, Then the type filter is on too; When a requirement cited by no
  function is selected, Then its panel shows "Functions 0"; Given a page without call graph, Then none of these appear.
- **Dependencies**: RQ-TRC-018, ADR-TRC-002, RQ-TRC-014, RQ-TRC-033, RQ-TRC-034; the graph's switch is named "Implementation" by RQ-TRC-048

### RQ-TRC-047: Functions grouped in namespace and class boxes, at a chosen level of detail
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE the graph draws functions of a language with namespaces (or packages, modules) or classes, the
  graph SHALL group them in nested boxes, a namespace box holding its class boxes and free functions, a class box
  holding its methods, at the level of detail the user chooses:
  - **namespace**: the namespaces only, one box each;
  - **class**: the classes, one box each, inside their namespace box or alone;
  - **function**: the functions, inside their class box and namespace box, or inside their class box only.
  At the class and function levels, the user SHALL choose whether the enclosing boxes are drawn. At the namespace and
  class levels, the calls between functions of two boxes SHALL be drawn as one link per pair of boxes, in its
  direction, with the number of calls; a requirement cited by a function SHALL be linked to the box that holds the
  function at the level drawn. A box's kind (namespace or class) SHALL come from the declarations the analysis read
  (`namespace`, `class`, `struct`…), its name from the functions' qualified names.
- **Rationale**: thousands of functions are read by their structure first; a reviewer goes from the namespace to the
  class to the function without losing the calls or the requirements on the way.
- **Priority**: Should
- **Acceptance Criteria**: Given the fixture's call graph and functions on, When the level is "namespace", Then one
  `net` box is drawn and no function, and the call from `relay` to `net::Port::send` shows as one link from the box
  holding `relay` to `net` with its count; When the level is "class", Then the `net::Port` and `net::Session` boxes are
  drawn, inside the `net` box when enclosing boxes are on and alone when they are off; When the level is "function",
  Then `net::Port::send` is drawn inside the `net::Port` box, itself inside `net` when enclosing boxes are on; When a
  requirement cited by `net::Port::send` is drawn at the class level, Then it is linked to the `net::Port` box.
- **Dependencies**: RQ-TRC-018, ADR-TRC-002, RQ-TRC-028, RQ-TRC-029, RQ-TRC-034, RQ-TRC-037, RQ-TRC-044, DEC-TRC-014, DEC-TRC-017; the
  choice, the switch and the box kinds are named by RQ-TRC-048 ("Implementation detail", "Enclosing scopes")

### RQ-TRC-048: Graph toolbar words that tell the specification from the implementation
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE the page holds a call graph, the graph SHALL name what it draws of the code "Implementation" —
  the column (and "Callers · Implementation · Callees" around a selected function or box), the switch of RQ-TRC-041 —
  since a node of that column is a function, a class or a namespace; the choice of RQ-TRC-047 SHALL be named
  "Implementation detail" (Namespace · Class · Function) and its switch "Enclosing scopes"; the legend SHALL name the box
  kinds "Namespace", "Class" and "Global namespace", the latter labelled `(global namespace)`. The graph SHALL tell its
  two structures apart: the links feature → requirement, ADR → decision, plan → task SHALL be the "specification
  hierarchy", drawn and walked only while a "Specification hierarchy" switch is on; the link file → function SHALL be
  "defines", with its own look, drawn and walked with the source files ("Source files" switch). The toolbar's switches
  (Source files, Implementation, Specification hierarchy, Enclosing scopes) SHALL stand in one labelled "Display" group,
  like the "Depth" and "Implementation detail" groups. Without call graph, only "Source files" and "Specification
  hierarchy" remain in the group. The groups SHALL stand in the order of reading, "Depth", then "Display", then
  "Implementation detail", each label on a solid neutral background no element type of the graph uses, with the on-accent text. WHILE the "Implementation"
  switch is off (the Functions type filter too), the "Implementation detail" choice and the "Enclosing scopes" switch
  SHALL be disabled, and enabled again when it is turned on.
- **Rationale**: owner review of 2026-10-18: "Functions" named classes and namespaces too; "Containment" mixed the
  specification's structure with the code's and its effect on the graph was not understood; "Enclosing boxes" was not
  a professional term (a namespace, module, package or class is a scope in every language tree-sitter parses; blocks
  and functions, scopes too, are never drawn).
- **Priority**: Should
- **Acceptance Criteria**: Given the fixture page with the call graph, When the graph opens, Then the toolbar shows the
  groups "Depth", "Display" and "Implementation detail" in that order, "Display" holding "Source files",
  "Implementation", "Specification hierarchy" and "Enclosing scopes", and the choice and the last switch are disabled
  (the implementation is off); When "Implementation" is turned on, Then they are enabled; When it is turned off again,
  Then they are disabled; Given the tokens, Then the group labels have a background token; When functions are drawn, Then their column is "Implementation";
  When "Specification hierarchy" is off and a requirement is drawn, Then its feature is not drawn, and a function is
  still linked to its file by "defines"; When "Source files" is off, Then no file and no "defines" link is drawn; Given
  a page without call graph, Then "Display" holds "Source files" and "Specification hierarchy" only.
- **Dependencies**: RQ-TRC-018, ADR-TRC-002, RQ-TRC-041, RQ-TRC-044, RQ-TRC-045, RQ-TRC-047, DEC-TRC-022

### RQ-TRC-050: C#, Java, JavaScript, Python and Rust
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The call-graph analysis SHALL deliver C# (`.cs`), Java (`.java`), JavaScript and Node.js (`.js .jsx
  .mjs .cjs`), Python (`.py .pyw`) and Rust (`.rs`), each read with the grammar package the tree-sitter project
  publishes for it, and SHALL find in each its functions and methods with a body, its calls, its namespaces (packages,
  modules) and classes (structs, interfaces, traits, `impl` blocks) as boxes, and the comment block above a definition
  even when attributes, annotations or decorators stand between them.
- **Rationale**: AGNOS projects are not all C or C++; the official grammars follow their language and come as prebuilt
  wheels.
- **Priority**: Must
- **Acceptance Criteria**: Given one fixture file per language with a class, two functions, a call between them, a call
  to a library and an ID in the comment above a decorated or attributed function, When analysed, Then the functions have
  their qualified names, the call links them, the library call is external, the function is linked to the ID and the
  boxes are its namespace and class; Given `package a.b;` in Java or `namespace A.B;` in C#, Then the file's classes are
  in the namespace `a.b` (`A.B`), itself in `a` (`A`); Given Python, JavaScript or a Rust file module, Then a class
  outside any declared namespace is in `(global)`.
- **Dependencies**: RQ-TRC-032, RQ-TRC-047, DEC-TRC-025, DEC-TRC-026

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
