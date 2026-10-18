---
name: agnos-trace
description: "AGNOS traceability matrix skill. From an AGNOS process folder (the one holding INDEX.idx.md) and one or more source folders, writes one self-contained HTML page: every FTR/RQ/ADR/DEC/PLAN/TASK, the source files and lines that cite them, coverage of each requirement, the gaps (uncovered requirements, tasks without requirement, undefined IDs...), searchable, with an interactive graph. USE FOR: checking MANDATORY TRACEABILITY at the end of a session or before a release; answering 'what implements / cites this requirement'; with --call-graph, which functions carry it and what calls them. Independent of the product developed."
argument-hint: "--process <dir> --sources <dir> [--sources <dir>...] [--out <file>] [--ext <.x>...] [--exclude <pattern>...] [--title <t>] [--generated-at <t>] [--call-graph]"
---

# AGNOS Traceability Matrix

<!-- FTR-TRC-001; ADR-TRC-001 (DEC-TRC-001 to DEC-TRC-004), ADR-TRC-002 (DEC-TRC-009 to DEC-TRC-011),
     ADR-TRC-003 (DEC-TRC-005 to DEC-TRC-008). RQ-TRC-017: this procedure. Call graph: FTR-TRC-002, ADR-TRC-004
     (DEC-TRC-013 to DEC-TRC-018), RQ-TRC-026; its boxes: ADR-TRC-005 (DEC-TRC-019 to DEC-TRC-022), RQ-TRC-047. -->

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
   - `--out <file>`: default `<process>/TRACEABILITY.html`. The page is generated: never edit it; the project decides
     whether to commit or ignore it.
   - `--ext .x` (repeatable) replaces the list of scanned extensions; `--exclude <pattern>` (repeatable, `fnmatch` on
     file and folder names) replaces the excluded names (`.git`, `node_modules`, `build*`, `dist`, `out`, `_deps`,
     `.venv`, `__pycache__`, `target`, `bin`, `obj`…).
   - `--generated-at <text>` fixes the timestamp shown, which makes the page byte-identical from run to run.
   - `--call-graph` adds the functions of the scanned files and their calls, parsed with tree-sitter (see "Call graph"
     below). It needs the packages pinned in `requirements-callgraph.txt`, installed once with
     `pip install -r .github/skills/agnos-trace/requirements-callgraph.txt` (prebuilt wheels, no compiler); without them
     the page is written all the same, without functions.
3. Check the exit code:
   - `0`: written. The last line gives the counts:
     `agnos-trace: <n> elements, <n> files; RQ <n>: covered <n>, indirect <n>, uncovered <n>; gaps: uncovered <n>,
     untasked <n>, task-no-rq <n>, adr-no-rq <n>, empty <n>, isolated <n>, undefined <n>, untraced-files <n>; <page> written`.
     With `--call-graph`, `; call graph: <n> functions, <n> calls, ambiguous <n>, external <n>` comes before the page, or
     `; call graph skipped: tree-sitter not installed, run: pip install -r …` when the packages are missing.
     Report it to the user as it is, with the gaps that are not 0.
   - `1`: input error (no `INDEX.idx.md`, missing source folder, broken design token), printed on the error stream;
     nothing is written. Apply the Error Recovery Protocol.
4. Give the user the path of the page. It opens offline in any current browser, from disk or as a mail attachment.

## What the page shows

- **Overview**: element counts, share of requirements covered, indirectly covered and uncovered, the gap counts, the
  coverage of each trigram.
- **Graph**: the selected element's links as a flow of columns (features, requirements, ADRs and decisions, plans and
  tasks, source files, undefined IDs), depth 1 to 3; "Whole graph" for everything.
- **Matrix**: one row per requirement with its feature, ADRs and decisions, plans and tasks, source files and lines,
  coverage; sortable, filtered by the search and the trigram filters, exportable as CSV.
- **Gaps**: the lists below, each element a link to its detail.
- **Detail panel**: the selection's type, title, status, location, and its links grouped by type with their count, IDs and
  the lines that make them. `#<ID>` in the URL selects an element; back and forward follow the selections.
- With `--call-graph`: functions are one more element type, found by the search; a function's panel lists its callers
  and callees (ambiguous ones marked, 50 at a time) and the IDs it cites; a requirement's panel lists its functions. The
  Functions filter is off when the page opens: turn it on to draw functions in the graph, where a selected function's
  callers stand on its left and its callees on its right; at most 400 nodes are drawn, the status line says how many
  are left out. The overview has a "Call graph" card and the gaps an informational "Untraced functions" list.
- Boxes, with `--call-graph`: the graph's "Detail" choice draws the functions at three levels. **Function** (the
  default): every function in the box of its class or namespace. **Class**: one box per class, the calls between their
  functions merged into one link per pair of boxes with its count of call sites. **Namespace**: one box per namespace,
  merged the same way. A function outside any namespace or class stands in its file's box at the class and namespace
  levels. "Enclosing boxes" draws the boxes around the level's own (namespaces around classes, and around a function's
  class) or leaves them out; it has no meaning at the namespace level. A box is selected like an element (click it,
  or `#box:<qualified name>`, `#box:file:<path>` in the URL): its panel lists the box around it, its inner boxes, its
  functions, its callers and callees by box with their call sites, and the requirements its functions cite.

## Call graph (DEC-TRC-013 to DEC-TRC-018)

- A function is a definition with a body; its key is `fn:<file>:<first line>`. It cites the IDs of its lines and of the
  comment block just above it. Coverage and the gap counts stay file-based: the call graph changes none of them.
- Calls are resolved by name: among the definitions of that name in the caller's language, the first non-empty set of
  the caller's class, its namespace, its file, its folder, the project. One left: a call link; two to five: one link to
  each, marked ambiguous; more: counted as ambiguous; none: counted as external. Macros, virtual dispatch, function
  pointers and callbacks are not followed.
- Languages are data: `assets/callgraph/languages.json` (extensions, grammar wheel and module, query file, scope
  separator) and one query file `assets/callgraph/<language>.scm` with the captures `@definition`, `@definition.name`,
  `@scope`, `@scope.name`, `@call`, `@call.name`, `@comment`. C and C++ are delivered (`.h` read as C++). To add a
  language: one table entry, one query file, its grammar wheel pinned in `requirements-callgraph.txt`; no script changes.
- Boxes come from the entry's `scopes` map (DEC-TRC-019): each scope node type its query captures as `@scope`, with
  the box kind it stands for, `namespace` or `class`. C++ maps `namespace_definition` to `namespace` and
  `class_specifier`, `struct_specifier`, `union_specifier` to `class`; C has no scope (`{}`), so its functions have no
  box. To give a new language its boxes, list its grammar's node types for packages, modules or namespaces (`namespace`)
  and for classes, structs or interfaces (`class`). A scope whose node type is not listed, like a qualifier part no
  scanned file declares (a class declared in a header outside the sources), gets a guessed kind: the innermost part of
  a method's qualifier is a class, the outer parts namespaces. Anonymous namespaces and
  lambdas make no box.

## Rules behind the numbers (DEC-TRC-003, DEC-TRC-004)

- A link is an ID written in an element's own lines (its line range without the ranges of the elements it contains), or
  in a source line. `<A> to <B>`, `<A>–<B>`, `<A>..<B>` of one type and trigram count as every defined ID between them.
- **covered**: a source file cites the requirement; **indirect**: a source file cites a decision, task, ADR, plan or
  feature linked to it (another requirement does not count); **uncovered**: neither.
- Gaps: `uncovered`, `untasked` (no task cites the requirement), `task-no-rq` (the task cites no requirement itself),
  `adr-no-rq` (neither the ADR nor its decisions cite one), `empty` (feature without requirement, ADR without decision,
  plan without task), `isolated` (no link touches the element or what it contains), `undefined` (cited, not in the
  index), `untraced-files` (scanned files citing no ID).
- An ID quoted in prose as an example (a test fixture's IDs in a task's Verification field, an instructions file's
  sample IDs) is a citation like any other: it shows as `undefined`. Write such examples without the ID grammar.

## Tests

`python -m unittest discover -s .github/skills/agnos-trace/tests -v` from the repository root: a synthetic process in
`tests/fixtures/repo` plants one element of every gap. The page tests run in a headless Chromium-family browser (Edge,
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
