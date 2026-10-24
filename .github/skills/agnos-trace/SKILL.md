---
name: agnos-trace
description: "AGNOS traceability matrix skill. From an AGNOS process folder (the one holding INDEX.idx.md) and one or more source folders, writes an offline HTML page with its data beside it (<page>.json, <page>.data.js): every FTR/RQ/ADR/DEC/PLAN/TASK, the source files and lines that cite them, coverage of each requirement, a quality score and grade, with the findings of each check (uncovered requirements, tasks without requirement, undefined IDs...), searchable, with an interactive graph. USE FOR: checking MANDATORY TRACEABILITY at the end of a session or before a release; answering 'what implements / cites this requirement'; with --call-graph, which functions carry it and what calls them; with --history, who (humans and agents) changed each element and its code, and when. Independent of the product developed."
argument-hint: "--process <dir> --sources <dir> [--sources <dir>...] [--out <file>] [--ext <.x>...] [--exclude <pattern>...] [--title <t>] [--generated-at <t>] [--call-graph] [--history [--history-since <date|duration>] [--history-depth <n>]]"
---

# AGNOS Traceability Matrix

<!-- FTR-TRC-001; ADR-TRC-001 (DEC-TRC-001 to DEC-TRC-004), ADR-TRC-002 (DEC-TRC-009 to DEC-TRC-011),
     ADR-TRC-003 (DEC-TRC-005 to DEC-TRC-008). RQ-TRC-017: this procedure. Call graph: FTR-TRC-002, ADR-TRC-004
     (DEC-TRC-013 to DEC-TRC-018), RQ-TRC-026; its boxes: ADR-TRC-005 (DEC-TRC-019 to DEC-TRC-022), RQ-TRC-047. Matrix columns: ADR-TRC-006 (DEC-TRC-027, DEC-TRC-028), RQ-TRC-051, RQ-TRC-052.
     Detail band, tags, feature titles, wheel zoom: ADR-TRC-007 (DEC-TRC-029 to DEC-TRC-031), RQ-TRC-053 to RQ-TRC-056.
     History: FTR-HST-001, ADR-HST-001 (DEC-HST-001 to DEC-HST-011), RQ-HST-001 to RQ-HST-026. -->

Canonical procedure, shared by GitHub Copilot (`.github/skills/agnos-trace/`) and Claude Code
(`.claude/skills/agnos-trace/`, which points here). The skill knows the AGNOS ID grammar and the `INDEX.idx.md` format
only, so it works on any AGNOS project. It needs Python 3.9 or later, standard library only (3.10 to run its tests).

## Procedure

1. Refresh the index first: invoke the `agnos-index` skill (the matrix reads `INDEX.idx.md`, never the documents' headings).
2. From the repository root, run (one command; `python3` on `linux` / `macos`, `python` on `windows`):

   ```
   python .github/skills/agnos-trace/scripts/trace_matrix.py --process process --sources <source folder>
   ```

   - `--sources` is repeatable: give every folder whose files should carry requirement IDs (code, tests, build files,
     CI workflows). Do not give a folder of documentation that quotes IDs as examples: its IDs would be counted.
   - `--out <file>`: default `<process>/TRACEABILITY.html`. Its data are written beside it (RQ-TRC-010):
     `<page>.json`, the data alone, for any other tool, and `<page>.data.js`, the same data, which the page loads. The
     three files are generated: never edit them; the project decides whether to commit or ignore them.
   - `--ext .x` (repeatable) replaces the list of scanned extensions; `--exclude <pattern>` (repeatable, `fnmatch` on
     file and folder names) replaces the excluded names (`.git`, `node_modules`, `build*`, `dist`, `out`, `_deps`,
     `.venv`, `__pycache__`, `target`, `bin`, `obj`…).
   - `--generated-at <text>` fixes the timestamp shown, which makes the page byte-identical from run to run.
   - `--call-graph` adds the functions of the scanned files and their calls, parsed with tree-sitter (see "Call graph"
     below). It needs the packages pinned in `requirements-callgraph.txt`, installed once with
     `pip install -r .github/skills/agnos-trace/requirements-callgraph.txt` (prebuilt wheels, no compiler); without them
     the page is written all the same, without functions.
   - `--history` adds who worked on each element, file and function, read from git (see "History" below).
     `--history-since <date or duration>` (a form git reads: `6.months`, `2.weeks`, `2026-01-01`) keeps the commits
     authored since then, `--history-depth <n>` the `n` most recent; both apply together. Either one without
     `--history`, or a depth that is not a positive integer, is an input error.
3. Check the exit code:
   - `0`: written. The last line gives the counts and the quality score (see "Quality scoring" below):
     `agnos-trace: <n> elements, <n> files; RQ <n>: covered <n>, indirect <n>, uncovered <n>; quality: <grade> <score>/10;
     checks: covered <s>, defined <s>, tasked <s>, task-rq <s>, adr-rq <s>, filled <s>, connected <s>, files-traced <s>;
     findings <n>; <page> written`.
     With `--call-graph`, `functions-traced <s>` joins the checks and `; call graph: <n> functions, <n> calls, ambiguous
     <n>, external <n>` comes before the page, or `; call graph skipped: tree-sitter not installed, run: pip install -r …`
     when the packages are missing. With `--history`, `; history: <n> commits, <n> humans, <n> agents` comes next, or a
     warning `no history: <cause>` on the error stream when git is missing, the process folder is in no git working
     tree, or the repository has no commit (the page is written without history, exit code 0). Report it to the user as
     it is, with the checks scoring under 10.
   - `1`: input error (no `INDEX.idx.md`, missing source folder, broken design token, a history option misused),
     printed on the error stream; nothing is written. Apply the Error Recovery Protocol.
4. Give the user the path of the page. It opens offline in any current browser, from disk, as long as its
   `<page>.data.js` stands beside it (share the three files together; alone, the page says which file it lacks).

## What the page shows

- **Overview**: element counts, share of requirements covered, indirectly covered and uncovered, the quality score and grade with the findings per check,
  the coverage of each trigram.
- **Graph**: the mouse wheel zooms by about 10 % a notch, from the design token `graph-wheel-sensitivity` (RQ-TRC-056). The selected element's links as a flow of columns (features, requirements, ADRs and decisions, plans and
  tasks, source files, undefined IDs), depth 1 to 3; "Whole graph" for everything.
- **Matrix**: one row per requirement with its feature, ADRs and decisions, plans and tasks, source files and lines,
  coverage; sortable, filtered by the search and the trigram filters, exportable as CSV. The columns stand by default
  in the order of the specification (Feature, Requirement, Coverage, ADRs / decisions, Plans / tasks, Functions,
  Source files, Lines; RQ-TRC-051). Drag a header onto another, or press Alt+← / Alt+→ on a focused header, to move the
  column; the order is remembered in the browser, like the widths, and "Reset columns" brings back the default order and
  widths (RQ-TRC-052). The CSV keeps its own fixed columns. The Feature column shows each feature's title under its ID (RQ-TRC-053).
- **Quality** (RQ-TRC-060 to RQ-TRC-063): for the decision maker, a report card at the top (the project's grade A to E on
  a green-to-red scale (as the Nutri-Score and DPE labels) with its letter always written, its score out of 10, a one-sentence verdict, the grade of each
  feature area and the three lowest-scored checks as "Fix first"), then three charts (a radar of the checks, bars per
  feature area, the coverage shares; each with a tooltip on hover and on keyboard focus, a radar axis opens its check);
  for the technician, the checks (see "Quality scoring") in a grid, lowest score first, each compact (title, risk, score
  bar, count of findings) and opened by its chevron to the rule, the formula, the figures and the findings, each finding a
  link to its detail ("Expand all", "Collapse all"). It fits a 1440 by 900 window without vertical scrolling.
- **History**, with `--history` (FTR-HST-001; the tab comes before Quality): a timeline of who changed what, read from
  two angles. **Requirements**: one row per process element, grouped by type; **Code**: the files in a tree of their
  folders that opens and closes (their functions below them with a call graph), or the elements by the code citing
  them. A mark is one commit on a row: its shape tells the kind (circle: human, diamond: agent, ringed circle: human
  and agent together, the ring in the agent's colour), its colour the author (one colour per identity), its size the
  lines changed; hover it for the commit, click it (or Enter) to select the commit in the detail panel (RQ-HST-023:
  its kind, hash, subject, date, contributors, lines and branch in the fixed band; below, the **git graph** of the
  commits around it, a lane and a colour per branch, its name at its newest commit, the lines to the parents curving
  where a branch starts or is merged, a click on a row selecting that commit (RQ-HST-025); then what the commit
  changed, by type, with the lines changed in each). The
  figures (commits, humans, agents, share with an agent, period) and an activity band stacked by kind follow the rows
  shown. The wheel over the marks zooms, a drag pans, `+` `-` `0` and the arrows do the same; the overview strip at
  the bottom moves the period. The selectors stand together on the toolbar: angle, code grouping, kind (all, humans,
  agents). Filters: identities (one or more), a text on the rows (ID, title, path, function; the first field of its
  line, as wide as the sidebar's search), the element types; "Rows without changes" shows the rows a filter empties. The labels column
  is resized by its edge (drag, arrows, double click to reset; remembered in the browser). The sidebar's **History**
  section lists the identities (a person or an agent icon in the identity's colour, their commits; its tooltip tells their names, e-mails and
  how they were merged, when they were): a click opens the tab filtered on that one. The detail panel's **History**
  button opens the tab on the selected element and what it contains (or a file and its functions), shown as a chip
  that removes the scope.
- **Tooltips** (FTR-HST-002): every piece of business information (an element, a file, a function, a relation, a
  figure, a grade, an identity, a commit) has a rich tooltip, its first line bold and its details below, on hover and
  on keyboard focus; the browser's plain tooltip only says what a control does. Never two at once.
- **Detail panel**: the selection's type, title, status, location and tags (the count of its links by type) stand in a
  band, fixed at the top (RQ-TRC-054); below it, only the links scroll, grouped by type with their IDs and the lines that
  make them. Clicking a tag shows only its group (several tags, several groups), clicking it again shows them all, and
  a new selection drops the filter (RQ-TRC-055). `#<ID>` in the URL selects an element; back and forward follow the selections.
- With `--call-graph`: functions are one more element type, found by the search; a function's panel lists its callers
  and callees (ambiguous ones marked, 50 at a time) and the IDs it cites; a requirement's panel lists its functions. The
  Functions filter is off when the page opens: turn it on (or the graph's "Implementation" switch, the same filter) to
  draw the implementation in the graph's "Implementation" column, where a selected function's callers stand on its left
  and its callees on its right; at most 400 nodes are drawn, the status line says how many are left out. The overview
  has a "Call graph" card and the Quality view an informational "Functions traced" check.
- The search list (RQ-TRC-049): pointing at a result, or moving onto it with the arrow keys, shows after 300 ms a
  tooltip beside the list with its type, whole name, whole title and location; the list itself cuts them to its width.
- The graph's toolbar groups stand in the order Depth, Display, Implementation detail (RQ-TRC-048). The "Display"
  group: **Source files** draws the files, linked to the IDs they cite ("cited in
  code") and to the functions they define ("defines"); **Specification hierarchy** draws and follows feature →
  requirement, ADR → decision, plan → task (off, a requirement no longer brings its feature); with `--call-graph`,
  **Implementation** and **Enclosing scopes** (below). While "Implementation" (or the Functions type filter) is off,
  the "Implementation detail" choice and "Enclosing scopes" are disabled.
- Scopes, with `--call-graph`: the "Implementation detail" choice draws the implementation at three levels.
  **Function** (the default): every function in the frame of its class or namespace. **Class**: one node per class, the
  calls between their functions merged into one link per pair with its count of call sites. **Namespace**: one node per
  namespace, merged the same way. What stands in no named namespace (global functions, those of anonymous namespaces,
  classes outside any namespace) is the `(global namespace)` at the class and namespace levels. "Enclosing scopes"
  draws each class inside its namespace (or the global namespace) and a function's class inside its namespace, or
  leaves them out; it has no meaning at the namespace level. Blocks and functions, scopes too, are never drawn as
  frames. A scope is selected like an element (click it, or `#box:<qualified name>`, `#box:(global)` in the URL): its
  panel lists its enclosing scope, its inner scopes, its functions, its callers and callees by scope with their call
  sites, and the requirements its functions cite.

## Call graph (DEC-TRC-013 to DEC-TRC-018)

- A function is a definition with a body; its key is `fn:<file>:<first line>`. It cites the IDs of its lines and of the
  comment block just above it. Coverage and the findings stay file-based: the call graph changes none of them.
- Calls are resolved by name: among the definitions of that name in the caller's language, the first non-empty set of
  the caller's class, its namespace, its file, its folder, the project. One left: a call link; two to five: one link to
  each, marked ambiguous; more: counted as ambiguous; none: counted as external. Macros, virtual dispatch, function
  pointers and callbacks are not followed.
- Languages are data: `assets/callgraph/languages.json` (extensions, grammar wheel and module, query file, scope
  separator) and one query file `assets/callgraph/<language>.scm` with the captures `@definition`, `@definition.name`,
  `@scope`, `@scope.name`, `@call`, `@call.name`, `@comment`. To add a language: one table entry, one query file, its
  grammar wheel pinned in `requirements-callgraph.txt`; no script changes.
- Delivered, each with the grammar the tree-sitter project publishes (RQ-TRC-050, DEC-TRC-025): C (`.c`), C++ (`.h`
  read as C++), C# (`.cs`), Java (`.java`), JavaScript and Node.js (`.js .jsx .mjs .cjs`), Python (`.py .pyw`; stubs
  `.pyi` are not read) and Rust (`.rs`). A definition is a function or method with a body: in JavaScript also a function
  or arrow given to a name, an object key or a member (`exports.f = function`); a Rust trait's default method; not an
  interface or abstract method. `new`, macros (`println!`) and calls outside any function are not calls.
- What differs between languages is settled in their query files (DEC-TRC-026): Java's `package a.b;` and C#'s
  `namespace A.B;` stand before the classes, so the file's root node is captured as that namespace's scope; Python's
  decorators and Rust's attributes are captured as `@comment`, so the comment block above them reaches the definition.
- Boxes come from the entry's `scopes` map (DEC-TRC-019): each scope node type its query captures as `@scope`, with
  the box kind it stands for, `namespace` or `class`. C++ maps `namespace_definition` to `namespace` and
  `class_specifier`, `struct_specifier`, `union_specifier` to `class`; C has no scope (`{}`), so its functions are in
  `(global)`. C# and Java: namespaces (the package) and classes, structs, interfaces, enums, records; Rust: inline
  `mod` blocks, `impl` blocks by their type and traits; JavaScript and Python: classes only, a module being a file, so
  their classes are in `(global)`. To give a new language its boxes, list its grammar's node types for packages, modules or namespaces (`namespace`)
  and for classes, structs or interfaces (`class`). A scope whose node type is not listed, like a qualifier part no
  scanned file declares (a class declared in a header outside the sources), gets a guessed kind: the innermost part of
  a method's qualifier is a class, the outer parts namespaces. Anonymous namespaces and
  lambdas make no box.

## History (FTR-HST-001; ADR-HST-001: DEC-HST-001 to DEC-HST-004, DEC-HST-010)

- `scripts/history.py` is loaded only with `--history`; it runs the `git` command, nothing else beyond the standard
  library. Without `--history`, git is not run and the data file is unchanged.
- An **intervention** is a non-merge commit that changed lines of an element's definition (its range in
  `INDEX.idx.md`), of a function's range (with `--call-graph`), or of a scanned file. The ranges of the working tree are
  followed back through every earlier version, across renames and merges, from one `git log -p -U0 -M -m --parents`
  over the process and source folders, as `git log -L` follows one range. Merge commits and uncommitted changes credit
  no one. The changed lines are counted as git's `--numstat` counts them, a hunk's removed lines in proportion of its
  added lines in the range.
- An **identity** is the commit's author (never its committer, who may be the service that merged), after the
  repository's `.mailmap`, and each `Co-Authored-By` co-author. Humans sharing an e-mail address (ignoring case) are one
  identity, named by their most frequent name; an agent is one name and address, since the models of one vendor share a
  no-reply address. An identity is an **agent** when its name or address matches a pattern of `assets/agents.json`
  (edit it to class another assistant), else a **human**; a commit is `human`, `agent` or `together`.
- The period: `--history-since` is given to git, and the author date is then checked against the same cutoff;
  `--history-depth` is git's `--max-count`. A shallow clone is read as far as it goes and marked `shallow`.
- Written to the data file as `history`: `limits` (`since`, `depth`, `commits`, `first`, `last`, `shallow`), `people`
  (`name`, `names`, `emails`, `mergedBy` among `email` and `mailmap`, `kind`, `commits` as author, `coCommits`),
  `commits` in author-date order (`hash` of 10 characters, `date`, `subject`, `author` and `coAuthors` as indexes into
  `people`, `kind`) and `interventions`: `elements` by ID, `files` by path and, with a call graph, `functions` by index
  into `callGraph.functions`, each a list of `[commit index, changed lines]`; and `graph` (RQ-HST-024, DEC-HST-010):
  `branches` (names, `null` for an unnamed branch) and `nodes`, HEAD's commits newest first in topological order down
  to the oldest commit of `commits`, merges and commits outside the folders read included (`hash`, `parents` as node
  indexes, `branch`, `commit` index or `null`, and then `date` and `subject`). It is read by a second `git log` with no
  path, since a path-limited log rewrites parents and drops merges. A commit's branch is found by following first
  parents from the default branch's tip (`main`, `master`, else the branch checked out), the other local tips oldest
  first, then the second parent of each merge whose message names its branch (`Merge branch 'X'`, `Merge pull request
  #n from owner/X`, `Merge X into Y`); a commit keeps the first branch that reaches it.

## Rules behind the numbers (DEC-TRC-003, DEC-TRC-004)

- A link is an ID written in an element's own lines (its line range without the ranges of the elements it contains), or
  in a source line. `<A> to <B>`, `<A>–<B>`, `<A>..<B>` of one type and trigram count as every defined ID between them.
- **covered**: a source file cites the requirement; **indirect**: a source file cites a decision, task, ADR, plan or
  feature linked to it (another requirement does not count); **uncovered**: neither.
- Findings (the elements that fail a check): `uncovered`, `untasked` (no task cites the requirement), `task-no-rq` (the
  task cites no requirement itself), `adr-no-rq` (neither the ADR nor its decisions cite one), `empty` (feature without
  requirement, ADR without decision, plan without task), `isolated` (no link touches the element or what it contains),
  `undefined` (cited, not in the index), `untraced-files` (scanned files citing no ID).
- An ID quoted in prose as an example (a test fixture's IDs in a task's Verification field, an instructions file's
  sample IDs) is a citation like any other: it shows as `undefined`. Write such examples without the ID grammar.

## Quality scoring (ADR-TRC-008: DEC-TRC-032, DEC-TRC-033; RQ-TRC-058, RQ-TRC-059, RQ-TRC-064)

Each rule is a **check**. Its **score** is 10 × the share of its **population** that is not a finding, to one decimal
(half up); a check with an empty population has no score and weighs nothing. The **overall score** is the average of
the checks' scores weighted by risk (critical 10, high 7.5, medium 5, low 2.5, informational 0); the **grade** is A
from 9, B from 7.5, C from 6, D from 4, else E. A trigram's score uses the same formula on its own elements (the checks
whose findings are IDs; files and functions belong to no trigram). The checks, risks, weights and thresholds are data in
`assets/scoring.json`: change a number there, never in the code. Written to the data file as `quality`
(`score`, `grade`, `checks[]` with `key`, `title`, `rule`, `risk`, `items`, `population`, `findings`, `score`, and
`trigrams`), and summarised on the generator's last line.

| Check (key) | Risk | Population | Findings |
|---|---|---|---|
| Requirements covered (`covered`) | critical | requirements | `uncovered` |
| IDs defined (`defined`) | critical | IDs cited by the process or the sources | `undefined` |
| Requirements tasked (`tasked`) | high | requirements | `untasked` |
| Tasks with a requirement (`task-rq`) | high | tasks | `task-no-rq` |
| ADRs with a requirement (`adr-rq`) | medium | ADRs | `adr-no-rq` |
| Containers not empty (`filled`) | medium | features, ADRs, plans | `empty` |
| Elements connected (`connected`) | medium | defined elements | `isolated` |
| Source files traced (`files-traced`) | medium | scanned files | `untraced-files` |
| Functions traced (`functions-traced`) | informational | functions (with `--call-graph`) | functions citing no ID |

## Tests

`python -m unittest discover -s .github/skills/agnos-trace/tests -v` from the repository root: a synthetic process in
`tests/fixtures/repo` plants one element of every finding. The page tests run in a headless Chromium-family browser (Edge,
Chrome, Chromium; `AGNOS_TRACE_BROWSER=<path>` to choose) and are skipped when none is found. The call-graph tests
(`tests/fixtures/repo/calls`) are skipped without the tree-sitter packages; `AGNOS_TRACE_PERF=1` adds the measure on a
generated tree of 20,000 functions and 100,000 calls (about a minute).

## Updating the graph library

`scripts/vendor/VENDOR.md` records the version, source and SHA-256 of `cytoscape.min.js` (RQ-TRC-024). To update:
download the new version, check its hash against the registry's, replace the file and the row, run the tests.

## Design system

Every colour, size and duration of the page is a token of `assets/tokens.json` (global → semantic → component); the CSS
and the script use only the `--s-*` and `--c-*` custom properties the generator writes from it. Change a value there,
never in `matrix.css` or `matrix.js` (a test fails on any raw colour, `px` or `ms` in them).
