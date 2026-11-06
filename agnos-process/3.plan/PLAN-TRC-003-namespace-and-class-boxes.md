# PLAN-TRC-003: Namespace and Class Boxes in the Graph

## Overview
Implement RQ-TRC-047 after ADR-TRC-005: the scopes of the call graph as data, the mapping of functions to their boxes at
the chosen level of detail, the boxes drawn as compound nodes in the flow layout, the toolbar controls and the box's
detail panel, then the skill's documentation and a run on this repository.

## References
- **Requirements**: RQ-TRC-047; RQ-TRC-037, RQ-TRC-038, RQ-TRC-040 (limits kept), RQ-TRC-044, RQ-TRC-045, RQ-TRC-046
  (relation look, tooltips)
- **ADRs**: ADR-TRC-005 (DEC-TRC-019 to DEC-TRC-022); ADR-TRC-004 (DEC-TRC-014, DEC-TRC-016, DEC-TRC-017),
  ADR-TRC-003 (DEC-TRC-006), ADR-TRC-002 (DEC-TRC-010, DEC-TRC-011)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-TRC-023: Scopes and their kinds in the call graph data
- **Tier**: L
- **Status**: Done
- **Description**: Add the `scopes` map to each entry of `languages.json` (C++: namespace and class kinds; C: none),
  record every scope the analysis reads with its qualified name, kind and parent, guess the kind of a qualifier part no
  scanned file declares (innermost part of a method's qualifier: class; else namespace), and embed the `scopes` table
  and one scope index per function in the page data (DEC-TRC-016's compact rows).
- **Requirement refs**: RQ-TRC-047, RQ-TRC-032, RQ-TRC-038, RQ-TRC-040
- **ADR refs**: ADR-TRC-005 (DEC-TRC-019), ADR-TRC-004 (DEC-TRC-014, DEC-TRC-016)
- **Acceptance Criteria**: Given the fixture, When analysed, Then the scopes are `net` (namespace), `net::Port` and
  `net::Session` (class, `net` their parent), the out-of-class `net::Session::send` has the scope `net::Session`,
  `relay` and the C functions have none; Given a method of a class declared in no scanned file, Then its class is
  guessed with the kind class and its outer part namespace; Given two runs, Then the pages are identical; the data adds
  at most one integer per function and one row per scope.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `ScopesTest` 6/6 OK (scopes `net` namespace, `net::Port` and `net::Session` class with parent 0;
  `Session::send` and the constructor in `net::Session`; `relay`, `log`, `operator==` and the C functions none; guessed
  `ui` namespace and `ui::Widget` class; 8-field rows, one scope row each); whole suite 80 OK, 1 skipped, the golden
  page without call graph and the two identical runs included. On a C++ code base: 124 scopes (108 class, 16 namespace), 1584
  of 1908 functions in a scope, 4806 bytes of scope table; Sonar: no finding.
- **Assumptions**: the table keeps only the scopes that hold a function, directly or through an inner scope (a declared
  scope without function body would be an empty box); the first declaration in file order gives a scope's kind.

### TASK-TRC-024: Functions mapped to boxes at a level of detail
- **Tier**: M
- **Status**: Done
- **Description**: In the page, map each function to the box that stands for it at the namespace, class or function
  level (functions without scope: one box per file), after the neighbourhood walk; merge the calls between two boxes into
  one link per ordered pair with its count, drop calls inside one box, move a function's ID links to its box; apply the
  400-node limit after the mapping.
- **Requirement refs**: RQ-TRC-047, RQ-TRC-037
- **ADR refs**: ADR-TRC-005 (DEC-TRC-021), ADR-TRC-004 (DEC-TRC-017)
- **Acceptance Criteria**: Given the fixture page with functions on, When the level is namespace, Then `relay`'s calls
  to `net::Port::send` and `net::Session::send` become one link from `relay`'s file box to `net` with their count, and
  no function is drawn; When the level is class, Then a requirement cited by `net::Port::send` is linked to
  `net::Port`; When the level is function, Then the drawing is the one before this plan.
- **Dependencies**: TASK-TRC-023
- **Assignee**: AI
- **Verification**: `DetailLevelTest` 3/3 OK in headless Edge: namespace level around `relay`, no `fn:` node, `box:net`
  drawn, `main.cpp` box → `net` one link of 2 call sites, ambiguous; `main.cpp` box → `session.cpp` box 2 sites;
  `net` → `session.cpp` box 1 site (`Session::send` calls `log`); `Port::send` → `Port::write` inside `net`, not drawn;
  class level, the code link from `box:net::Port` to the fixture's demo requirement drawn, `net::Port::send` not; function level after namespace: same
  elements as before. Whole suite 83 OK, 1 skipped. Sonar: no finding (complexity and outer-scope findings fixed).
- **Assumptions**: an aggregated call link counts its distinct call sites (caller, line), so one ambiguous call to two
  methods of a box counts once; it is ambiguous only when every merged call is; at the class level a function with a
  namespace but no class goes to its namespace's box; at the namespace level a method of a class outside any namespace
  goes to its file's box; a link is drawn only between nodes the walk reached; box selection waits for TASK-TRC-026.

### TASK-TRC-025: Boxes drawn as compound nodes in the flow layout
- **Tier**: M
- **Status**: Done
- **Description**: Draw boxes as Cytoscape compound nodes in the Functions column, stacked in name order, their children
  in rows inside; keep the callers · selection · callees split by box; draw or leave out the enclosing boxes; box look
  from new tokens per kind (frame, fill, label, padding).
- **Requirement refs**: RQ-TRC-047, RQ-TRC-037, RQ-TRC-018
- **ADR refs**: ADR-TRC-005 (DEC-TRC-020), ADR-TRC-003 (DEC-TRC-006), ADR-TRC-002 (DEC-TRC-010, DEC-TRC-011)
- **Acceptance Criteria**: Given the fixture page at the function level with enclosing boxes on, Then `net::Port::send`
  is drawn inside the `net::Port` box, itself inside `net`; With enclosing boxes off, Then `net::Port` has no parent;
  Given the generated 20,000-function tree, When the much-called function is drawn at each level at depth 2, Then each
  drawing takes under 500 ms with at most 400 nodes.
- **Dependencies**: TASK-TRC-024
- **Assignee**: AI
- **Verification**: `BoxDrawingTest` 4/4 OK in headless Edge: `send` (named inside its box) has the parent `net::Port`
  (label `Port`, kind class), itself inside `net` (namespace), `relay` no parent; enclosing boxes off: `net::Port`
  alone, whole name, no namespace box; class level: `box:net::Port` inside `net`; the three box tokens. Whole suite 87
  OK, 1 skipped. `AGNOS_TRACE_PERF=1` (2,000 classes in 20 namespaces, hub at depth 2): function 74 nodes 90 ms,
  class 74 nodes 105 ms, namespace 93 nodes 193 ms; page +2,243,556 bytes, interactive 141 ms. Screenshots on a C++ code base
  (light and dark): nested dashed namespace and class frames per column. Sonar: no finding (S7721 fixed).
- **Assumptions**: at the function level a function is always drawn in its own scope box, the switch adding or
  removing the outer ones; a boxed column is one pill per row (no sub-columns); a box appearing in two columns is
  drawn once in each; inside a drawn box a name drops the box's own name (`send` in `Port`, `Port` in `net`), the whole
  name staying in the node's data; namespace frames dashed, class frames solid violet.

### TASK-TRC-026: Detail choice, enclosing-boxes switch and the box's panel
- **Tier**: M
- **Status**: Done
- **Description**: Add, with a call graph only, the toolbar's "Detail" choice (Namespace · Class · Function, Function
  by default) and its "Enclosing boxes" switch (on, disabled at the namespace level), both with tooltips; make a box
  selectable, with a deep link and a detail panel (kind, qualified name, enclosing box, classes and functions, calls in
  and out by box, requirements cited); an aggregated link's tooltip gives its count; the legend shows the box kinds.
- **Requirement refs**: RQ-TRC-047, RQ-TRC-013, RQ-TRC-016, RQ-TRC-045, RQ-TRC-046
- **ADR refs**: ADR-TRC-005 (DEC-TRC-022), ADR-TRC-003 (DEC-TRC-007), ADR-TRC-002 (DEC-TRC-010)
- **Acceptance Criteria**: Given the fixture page, When "Class" is chosen, Then the graph is drawn at the class level and
  the switch is enabled; When "Namespace" is chosen, Then the switch is disabled; When the `net::Port` box is selected,
  Then its panel lists its two methods and the requirement they cite; Given a page without call graph, Then neither
  control appears.
- **Dependencies**: TASK-TRC-025
- **Assignee**: AI
- **Verification**: `DetailControlsTest` 7/7 OK in headless Edge: "Class" pressed, switch enabled, `box:net::Port` drawn;
  "Namespace" pressed, switch disabled; tooltips on the choice, its three buttons and the switch; the deep link
  `#box:net::Port` opens a "Class box" panel listing `net::Port::send`, `net::Port::write`, the fixture's demo
  requirement and the enclosing `net`, no stray text; the merged link `main.cpp` → `net` tip "ambiguous call … · 2 call
  sites"; three box kinds in the legend; without call graph no choice, switch or box sample. Whole suite 94 OK, 1
  skipped. Screenshot on a C++ code base (class level, `core::ByteWriter` selected): 13 functions, callers by box with call
  sites. Sonar: no finding.
- **Assumptions**: the choice is `#detail-level` (`#detail` is the panel); a box's calls by box are counted at its own
  level (class for a class box, namespace for a namespace or file box); a file box holds its file's functions standing
  outside any namespace; a selected box is drawn from all its functions at level 0, highlighted as its frames; the
  panel lists the requirements only among the IDs its functions cite.

### TASK-TRC-027: Documentation and run on this repository
- **Tier**: M
- **Status**: Done
- **Description**: Document the levels of detail, the boxes and the `scopes` map of the language table in SKILL.md, and
  run the skill with the call graph on this repository at the three levels.
- **Requirement refs**: RQ-TRC-047, RQ-TRC-017, RQ-TRC-032
- **ADR refs**: ADR-TRC-005 (DEC-TRC-019, DEC-TRC-022)
- **Acceptance Criteria**: Given this repository, When the page is opened at each level, Then the namespaces, classes
  and functions of a C++ code base are drawn in their boxes; SKILL.md says how to add a language's scopes.
- **Dependencies**: TASK-TRC-026
- **Assignee**: AI
- **Verification**: `trace_matrix.py --process process --sources <cpp-sources> --call-graph`: 1908 functions, 7745 calls, undefined
  92 (unchanged). Drawn in headless Edge around `core::setZoneSample`: function level 16 elements · 25 links, 15
  functions in 8 class and 12 namespace frames; class level 11 · 20, 8 class and 2 namespace pills in 10 namespace
  frames; namespace level 8 · 16, 7 namespace pills. SKILL.md: the three levels, the switch, box deep links and panel
  under "What the page shows"; the `scopes` map, C++'s and C's entries and how to give a language its boxes under
  "Call graph".
- **Assumptions**: AGENTS.md's trace bullet is left as it is (minimal; the skill documents the boxes).

### TASK-TRC-028: One (global) box instead of a box per file
- **Tier**: M
- **Status**: Done
- **Description**: Owner review of the namespace level on a C++ code base (file names among the namespaces): replace the file
  boxes by one `(global)` box, of kind `global`, for what stands in no named namespace, anonymous namespaces included;
  at the class level it holds the functions without scope and, with enclosing boxes, frames the classes outside any
  namespace; its panel, legend sample, token and documentation follow.
- **Requirement refs**: RQ-TRC-047, RQ-TRC-018, RQ-TRC-016
- **ADR refs**: ADR-TRC-005 (DEC-TRC-019 as amended, DEC-TRC-021, DEC-TRC-022)
- **Acceptance Criteria**: Given the fixture page, When the level is namespace and `relay` is drawn, Then no file box
  is drawn, `relay`'s calls are one link from `(global)` to `net` and `log`, global too, is inside `(global)`; Given
  the `(global)` box selected, Then its panel lists `relay`, `log` and the C functions; Given a C++ code base at the namespace
  level, Then no box is named after a file.
- **Dependencies**: TASK-TRC-027
- **Assignee**: AI
- **Verification**: whole suite 95 OK, 1 skipped. `DetailLevelTest`: namespace level around `relay`, no `fn:` or file
  box, `(global)` → `net` 2 call sites ambiguous, `net` → `(global)` 1 (`Session::send` calls `log`), 2 call links
  (`relay` → `log` inside `(global)`); `DetailControlsTest`: `#box:(global)` panel "Global box" lists `relay`, `log`,
  `operator==`, `helper`, `table`, `run`, not `net::Port::send`; the merged link's tip "2 call sites"; legend and token
  `global`. On a C++ code base at the three levels around `core::setZoneSample`: no box named after a file; namespace level
  around `core::Session::submit`, depth 2: callers `(global)`, `core::harness`, `core::test`, `server`. Sonar: no finding.
- **Assumptions**: `(global)` also frames the classes outside any namespace at the function level when enclosing
  boxes are on (as namespaces frame theirs); C functions, having no scope, are in `(global)`; its colour is the source
  files' grey (`graph-box-global` → `type-file`).

### TASK-TRC-029: Implementation words, a Display group, the specification hierarchy apart from "defines"
- **Tier**: M
- **Status**: Done
- **Description**: Owner review of the toolbar: name the code column, its split and its switch "Implementation", the
  choice "Implementation detail", the switch "Enclosing scopes", the box kinds "Namespace", "Class", "Global namespace"
  (label `(global namespace)`); split "Containment" into the "Specification hierarchy" switch (feature, ADR, plan
  links) and a `defines` link kind for file → function with its own look and colour token, governed by "Source files";
  group the switches in a "Display" fieldset; tooltips and SKILL.md follow.
- **Requirement refs**: RQ-TRC-048, RQ-TRC-041, RQ-TRC-044, RQ-TRC-045, RQ-TRC-047, RQ-TRC-018
- **ADR refs**: ADR-TRC-005 (DEC-TRC-022 as renamed, DEC-TRC-023), ADR-TRC-002 (DEC-TRC-010)
- **Acceptance Criteria**: those of RQ-TRC-048; Given the relation looks, Then `defines` has a colour of its own, an
  arrow and a legend sample (RQ-TRC-044).
- **Dependencies**: TASK-TRC-028
- **Assignee**: AI
- **Verification**: whole suite 100 OK, 1 skipped. `ToolbarWordsTest` 5/5 in headless Edge: groups Depth, Implementation
  detail, Display (Source files, Implementation, Specification hierarchy, Enclosing scopes); without call graph Depth
  and Display (Source files, Specification hierarchy); the code column "Implementation · 1"; hierarchy off: the
  fixture's feature not drawn, port.hpp → `net::Port::send` "defines" drawn, no `contains`; source files off: no file,
  no "defines", the feature drawn. `RelationLookTest`: six looks, six colours, `defines` sampled; panels "Class",
  "Global namespace", `(global namespace)`; tooltip targets include `#display`, `#show-hierarchy`. Screenshot on
  a C++ code base: the three groups, "Implementation" column, legend "specification hierarchy" and "defines". Sonar: no finding
  in matrix.js (S3776 fixed); matrix.html's earlier findings (lines 41, 58, 62, 126, 134) untouched.
- **Assumptions**: "defines" is lime with a short dash (`dash.short`); the legend says "specification hierarchy (…)"
  rather than "part of", the arrow running from the container; the panel's groups read "Enclosing scope", "Inner
  scopes", "Callers / Callees by scope"; the global box's key stays `box:(global)` so deep links keep working; at 1600 px
  the toolbar now wraps onto a second line.

### TASK-TRC-030: A search result's tooltip, the detail choice following "Implementation", toolbar order and labels
- **Tier**: M
- **Status**: Done
- **Description**: Second owner review of the page. (1) A result of the search list gets a tooltip of the page's own
  (type, whole name, whole title, location) after the quick delay token, on hover and on keyboard move. (2) The
  "Implementation detail" choice and "Enclosing scopes" are disabled while "Implementation" is off, from the switch or
  the Functions type filter, and enabled again when it is on. (3) The groups stand Depth, Display, Implementation
  detail. (4) Each group label gets a background from the design system (accent-subtle) with the accent text.
- **Requirement refs**: RQ-TRC-049, RQ-TRC-048, RQ-TRC-045, RQ-TRC-018
- **ADR refs**: ADR-TRC-005 (DEC-TRC-023 as amended, DEC-TRC-024), ADR-TRC-002 (DEC-TRC-010, DEC-TRC-011)
- **Acceptance Criteria**: those of RQ-TRC-049 and RQ-TRC-048.
- **Dependencies**: TASK-TRC-029
- **Assignee**: AI
- **Verification**: whole suite 109 OK, 1 skipped. `SearchTooltipTest` 4/4 in headless Edge (virtual time): a result
  pointed at shows, after the delay, its type, whole name, whole title and `file:lines`; the pointer leaving the list
  at 500 ms hides it; ArrowDown shows it; tokens `duration.quick` 300ms, `search-tip-delay`, `group-label-bg`,
  `group-label-text`. `ToolbarWordsTest` 10/10: groups in the order depth, display, detail-level; at load, with the
  implementation off, the choice, its three buttons and Enclosing scopes are disabled; the switch on enables them, off
  again disables them; the Functions type filter does the same; namespace detail keeps Enclosing scopes disabled.
  Screenshots on a C++ code base (light and dark): the tooltip beside the list for `core::Session::submit` with its location;
  the three group labels on the accent-subtle background; the choice greyed while the implementation is off. Sonar: no
  finding.
- **Assumptions**: the tooltip appears on hover and on arrow-key moves, not for the first result when the list opens;
  it is positioned beside the list (fixed), clamped to the window; the group labels use accent-subtle / accent, the
  fill and colour of a selected item; "Implementation detail" shows muted (`opacity.muted`) when disabled; at 1600 px
  the third group wraps onto a second line.

### TASK-TRC-031: The page's data in two files beside it
- **Tier**: M
- **Status**: Done
- **Description**: Owner decision: write the data as `<page>.json` and `<page>.data.js` beside the page, load the latter
  with `<script src>`, read `window.AGNOS_TRACE_DATA`, say which file is missing when it is; tests read the `.json`;
  SKILL.md and `.gitignore` follow.
- **Requirement refs**: RQ-TRC-010, RQ-TRC-022, RQ-TRC-023, RQ-TRC-038
- **ADR refs**: ADR-TRC-003 (DEC-TRC-005 as amended)
- **Acceptance Criteria**: those of RQ-TRC-010; two runs give identical pages and data files (RQ-TRC-023); the call
  graph's added size is measured on the data files (RQ-TRC-038).
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: whole suite 110 OK, 1 skipped: the page's only `<script src>` is `page.data.js`; `.json` and `.js`
  hold the same data; the page copied alone says `page.data.js` is missing; two runs to two names give the same page
  (data file name blanked) and the same data, all in LF; the golden data hash before PLAN-TRC-002 unchanged; the call
  graph's added size measured on page + data script. On a C++ code base: TRACEABILITY.html 529,642 bytes, .json 2,106,188,
  .data.js 2,106,215; opened from disk in headless Edge, the panel drawn as before.
- **Assumptions**: the `.json` holds the same escaped JSON as the script (`<` as `<`, still valid JSON); the data
  script is loaded by a relative name, so the three files move together; the generator's last line still names the
  page only.
