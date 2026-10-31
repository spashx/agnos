---
name: agnos-trace
description: "AGNOS traceability matrix skill. From an AGNOS process folder and source folders, writes an HTML page and its data: every artifact, what cites it, coverage, a quality score and findings. USE FOR: checking MANDATORY TRACEABILITY at session end or before a release; what cites a requirement; with --call-graph, its functions; with --history, who changed what and what was delivered."
argument-hint: "--process <dir> --sources <dir> [--sources <dir>...] [--out <file>] [--ext <.x>...] [--exclude <pattern>...] [--title <t>] [--generated-at <t>] [--call-graph] [--history [--history-since <date|duration>] [--history-depth <n>]]"
---

# AGNOS Traceability Matrix

<!-- RQ-TRC-017, RQ-TRC-098, DEC-TRC-050. Shared by GitHub Copilot and Claude Code (`.claude/skills/agnos-trace/` points here). -->

Needs Python 3.9 or later, standard library only. It knows only the AGNOS ID grammar and index format, so it works on any AGNOS
project. Run it; do not read the scripts.

1. Invoke the `agnos-index` skill first: the matrix reads `INDEX.idx.md`, never the documents' headings.
2. From the repository root (`python` on `windows`, `python3` on `linux` / `macos`):
   `python .github/skills/agnos-trace/scripts/trace_matrix.py --process process --sources <source folder>`

| Parameter | Meaning |
|---|---|
| `--process <dir>` | The folder holding `INDEX.idx.md` |
| `--sources <dir>` | Repeatable: every folder whose files should carry IDs (code, tests, build, CI). Not a documentation folder quoting IDs as examples: they would be counted. |
| `--out <file>` | Default `<process>/TRACEABILITY.html` |
| `--ext .x`, `--exclude <pattern>` | Repeatable; replace the scanned extensions, the excluded names (`fnmatch`) |
| `--title <t>`, `--generated-at <t>` | The page's title; a fixed timestamp makes the page byte-identical |
| `--call-graph` | Adds functions and calls. Needs once `pip install -r .github/skills/agnos-trace/requirements-callgraph.txt`; without it the page is written without them |
| `--history` | Adds who changed what and the deliveries, from git |
| `--history-since <date or duration>`, `--history-depth <n>` | Limit the history read (`6.months`, `2026-01-01`); only with `--history` |

**Outputs:** the page, `<page>.json` and `<page>.data.js` beside it: generated, never edit them; the project decides whether to commit or ignore
them; share the three together. The page loads its libraries from cdnjs, so it needs the network once.

**Exit codes:**
- `0`: written. The last line reads `agnos-trace: <n> elements, <n> files; RQ <n>: covered <n>, indirect <n>, uncovered <n>;
  quality: <grade> <score>/10; checks: <key> <score>, …; findings <n>; <page> written`, with the call graph and the history before
  the page when asked. A `no history: <cause>` warning on the error stream still means the page is written.
- `1`: input error on the error stream, nothing written. Apply the Error Recovery Protocol.

**Report** to the user the line as it is, the checks scoring under 10, and the path of the page, which tells the rest to its reader.

**When asked to explain or maintain, read only the file concerned:**

| Question | File |
|---|---|
| What a finding, a check, a score, the call graph, the history or a delivery figure means | `references/rules.md` |
| What `<page>.json` holds | `references/data-format.md` |
| How to run the tests, change a library or a visual value | `references/maintaining.md` |
