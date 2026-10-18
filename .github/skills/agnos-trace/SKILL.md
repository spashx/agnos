---
name: agnos-trace
description: "AGNOS traceability matrix skill. From an AGNOS process folder (the one holding INDEX.idx.md) and one or more source folders, writes one self-contained HTML page: every FTR/RQ/ADR/DEC/PLAN/TASK, the source files and lines that cite them, coverage of each requirement, the gaps (uncovered requirements, tasks without requirement, undefined IDs...), searchable, with an interactive graph. USE FOR: checking MANDATORY TRACEABILITY at the end of a session or before a release; answering 'what implements / cites this requirement'. Independent of the product developed."
argument-hint: "--process <dir> --sources <dir> [--sources <dir>...] [--out <file>] [--ext <.x>...] [--exclude <pattern>...] [--title <t>] [--generated-at <t>]"
---

# AGNOS Traceability Matrix

<!-- FTR-TRC-001; ADR-TRC-001 (DEC-TRC-001 to DEC-TRC-004), ADR-TRC-002 (DEC-TRC-009 to DEC-TRC-011),
     ADR-TRC-003 (DEC-TRC-005 to DEC-TRC-008). RQ-TRC-017: this procedure. -->

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
3. Check the exit code:
   - `0`: written. The last line gives the counts:
     `agnos-trace: <n> elements, <n> files; RQ <n>: covered <n>, indirect <n>, uncovered <n>; gaps: uncovered <n>,
     untasked <n>, task-no-rq <n>, adr-no-rq <n>, empty <n>, isolated <n>, undefined <n>, untraced-files <n>; <page> written`.
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
Chrome, Chromium; `AGNOS_TRACE_BROWSER=<path>` to choose) and are skipped when none is found.

## Updating the graph library

`scripts/vendor/VENDOR.md` records the version, source and SHA-256 of `cytoscape.min.js` (RQ-TRC-024). To update:
download the new version, check its hash against the registry's, replace the file and the row, run the tests.

## Design system

Every colour, size and duration of the page is a token of `assets/tokens.json` (global → semantic → component); the CSS
and the script use only the `--s-*` and `--c-*` custom properties the generator writes from it. Change a value there,
never in `matrix.css` or `matrix.js` (a test fails on any raw colour, `px` or `ms` in them).
