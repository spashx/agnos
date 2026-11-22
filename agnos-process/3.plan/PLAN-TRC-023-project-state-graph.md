# PLAN-TRC-023: Project state graph

## Overview
Separates the construction of the project's state graph from the performance center: a new `agnos-graph` skill writes
`4.knowledge/agnos-graph.json`, and `agnos-perf-center` reads it, building it first when it is absent or when asked.

## References
- **Requirements**: RQ-TRC-129, RQ-TRC-130, RQ-TRC-131, RQ-TRC-132, RQ-TRC-133
- **ADRs**: ADR-TRC-022 (DEC-TRC-074 to DEC-TRC-077); amends DEC-TRC-002, DEC-TRC-013; extends ADR-PLG-010

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-TRC-117: Create graph skill from perf-center code
- **Tier**: L
- **Status**: Done
- **Description**: Create `.github/skills/agnos-graph/` with `scripts/graph.py` (index parsing, containment, references, source scan, task tiers, extracted from `perf_center.py`), `callgraph.py`, `history.py`, the tree-sitter queries and `requirements-callgraph.txt` moved from `agnos-perf-center`, writing the dated graph file. Write the graph file's tests first in `agnos-graph/tests` and move there the pure unit tests of `callgraph` and `history`; the tests checking the page stay in `agnos-perf-center` and load the moved modules from `agnos-graph/scripts` (owner, 2026-11-22).
- **Requirement refs**: RQ-TRC-129, RQ-TRC-130, RQ-TRC-133
- **ADR refs**: ADR-TRC-022 (DEC-TRC-074)
- **Acceptance Criteria**:
  - Given the test fixture, When `graph.py --process P --sources S` runs, Then the graph file holds `meta`, `elements`, `edges`, `files`, `tasks` And no `coverage` nor `quality`
  - Given `--call-graph` and `--history`, Then it also holds `callGraph`, `history` and `delivery`
  - Given a fixed `--generated-at`, When it runs twice, Then the two files are byte-identical
  - Given a git repository, Then `meta.commit` is HEAD; Given a folder outside git, Then `meta.commit` is null
  - Given a missing source folder, Then it exits 1 And writes nothing
  - Given the moved unit tests, When they run from `agnos-graph/tests`, Then they pass
  - Given the page tests left in `agnos-perf-center`, When they load the moved modules from `agnos-graph/scripts`, Then they pass
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `agnos-graph/tests` 124 tests OK, 0 skipped (graph file: state keys and no `coverage`/`quality`; `callGraph`, `history`, `delivery` with `--call-graph --history`; byte-identical twice; `meta.commit` HEAD / null; missing source exit 1, nothing written); `agnos-perf-center/tests` 331 tests: 1 error (`test_literals` read `callgraph.py` in its old folder), fixed by splitting the check per skill, `test_literals` then OK in both, 3 skipped (performance tests, opt-in `AGNOS_PERF_CENTER_PERF=1`); `layout.py --check` 0 findings; meta-release `test_layout` 18 OK.
- **Assumptions**: `graphFile` and the `agnos-graph` layout copy were added here, not in TASK-TRC-120, because `layout.py --check` forbids the name as a literal in `graph.py`. `agents.json` and `delivery.json` moved with `history.py`, which reads them. Until TASK-TRC-118, `perf_center.py` keeps its model code and loads `callgraph.py`/`history.py` from `../agnos-graph/scripts`. The graph file also holds `callGraph.parsedFiles`/`unparsedFiles` and `meta.summaries`, which the quality checks and the summary line need. Moved tests: `test_languages`, `test_friction`, the module classes of `test_callgraph`, `test_resolution`, `test_history` and a split `test_literals`; the shared helpers of `test_history` are duplicated in both suites; the fixture repository is copied into `agnos-graph/tests/fixtures`. The call graph assertion of the page determinism test of RQ-TRC-040 became its own graph test.

### TASK-TRC-118: Feed perf-center from graph file
- **Tier**: L
- **Status**: Done
- **Description**: Make `perf_center.py` rebuild its model from the graph file given by `--graph`, then run `analyse`, `scorecard` and the rendering unchanged; remove from it the code moved to `agnos-graph`.
- **Requirement refs**: RQ-TRC-131
- **ADR refs**: ADR-TRC-022 (DEC-TRC-075)
- **Acceptance Criteria**:
  - Given a graph built from the fixture with a fixed date, When `agnos-perf-center --graph G` runs, Then `<page>.json` equals the one the single generator wrote at the parent commit, `meta` excepted for its new fields
  - Given a graph without `callGraph`, Then the page has no call graph And the run exits 0
  - Given an invalid graph file or one without `elements`, Then it exits 1 naming the file
  - Given the remaining perf-center tests, Then they pass
- **Dependencies**: TASK-TRC-117
- **Assignee**: AI
- **Verification**: fixture with `--call-graph --history`, fixed date: `page.json` from the graph is byte-identical to the one `perf_center.py` of `6a135a7` wrote, `meta` included (no new field); `GraphInputTest` 5 OK (no `callGraph` → none, exit 0; not JSON, no `elements`, absent → exit 1 naming the file); `agnos-perf-center/tests` 320 run: 2 errors (`tm.ID_PATTERN`, `perf_center.main --sources` in two tests), fixed, then OK; 3 skipped (opt-in performance tests); `agnos-graph/tests` 141 OK, 0 skipped.
- **Assumptions**: RQ-TRC-119 (scan lists) is now `agnos-graph`'s (owner, 2026-11-22): its help and run tests moved to `agnos-graph/tests/test_scan_lists.py`; the SKILL.md report test stays until TASK-TRC-121. The perf-center's options until TASK-TRC-119 are `--process`, `--graph`, `--out`, `--title`, `--generated-at`; the tests' `run_main` builds a temporary graph with `graph.main`, then runs the page on it, returning the page's stdout. The model and scanner unit tests moved to `agnos-graph/tests/test_model.py`.

### TASK-TRC-119: Build graph on demand from perf-center
- **Tier**: M
- **Status**: Done
- **Description**: Make `perf_center.py` run `../agnos-graph/scripts/graph.py` as a subprocess with its scan options when the graph file is absent or `--rebuild` is given, and refuse a missing graph without `--sources`.
- **Requirement refs**: RQ-TRC-132
- **ADR refs**: ADR-TRC-022 (DEC-TRC-076)
- **Acceptance Criteria**:
  - Given no graph file, When `agnos-perf-center --process P --sources S` runs, Then the graph file exists And the page is written
  - Given an existing graph, When it runs without `--rebuild`, Then the graph file is not rewritten
  - Given `--rebuild`, Then the graph file is rewritten
  - Given no graph and no `--sources`, Then it exits 1 And writes nothing
- **Dependencies**: TASK-TRC-118
- **Assignee**: AI
- **Verification**: `OnDemandGraphTest` 6 OK: no graph + `--sources` → graph file written and page; scan options reach the graph's `meta`; existing graph without `--rebuild` → bytes unchanged; `--rebuild` → rewritten; no graph, no `--sources` → exit 1 naming `--sources`, nothing written; failed build → exit 1, no page. With `GraphInputTest`, `test_skill_name`, `test_skill_contract`, `test_help`: 30 OK; `test_literals` OK.
- **Assumptions**: The graph is built with the page's `--generated-at` as its date, so that one fixed date keeps both reproducible; agnos-graph's stdout (scan lists, its summary) and stderr are shown before the page's summary line; the scan options' help refers to agnos-graph's for the default lists (RQ-TRC-119).

### TASK-TRC-120: Declare graph skill in layout and delivery
- **Tier**: M
- **Status**: In Progress
- **Description**: Add `graphFile` to `layout.json` and `agnos-graph` to the layout copies, add the Claude Code pointer `.claude/skills/agnos-graph/SKILL.md`, the plugin README entry and the marketplace attributes the moved vendor code needs.
- **Requirement refs**: RQ-TRC-133, RQ-TRC-129
- **ADR refs**: ADR-TRC-022 (DEC-TRC-077)
- **Acceptance Criteria**:
  - Given `layout.json`, Then `graphFile` is `4.knowledge/agnos-graph.json` And both skills read it from their copy
  - Given `layout.py --check`, Then it passes
  - Given a release rehearsal, Then the marketplace holds `plugins/agnos/skills/agnos-graph/SKILL.md` And it exits 0
- **Dependencies**: TASK-TRC-117
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-TRC-121: Document graph skill contract
- **Tier**: M
- **Status**: Not Started
- **Description**: Write `agnos-graph/SKILL.md` and `references/graph-format.md`, update `agnos-perf-center/SKILL.md` and its references to the new options and input, and add `agnos-graph` to `AGENTS.md`, `CLAUDE.md` and the getting-started guide where the perf center is described.
- **Requirement refs**: RQ-TRC-133, RQ-TRC-130, RQ-TRC-132
- **ADR refs**: ADR-TRC-022
- **Acceptance Criteria**:
  - Given `agnos-graph/SKILL.md`, Then it gives its parameters, outputs, exit codes and the path of its format reference
  - Given `agnos-perf-center/SKILL.md`, Then it gives `--graph` and `--rebuild` And says it calls `agnos-graph` when the graph is absent
  - Given `AGENTS.md` and `CLAUDE.md`, Then each lists `agnos-graph`
  - Given the skill-contract tests of both skills, Then they pass
- **Dependencies**: TASK-TRC-119, TASK-TRC-120
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-TRC-122: Verify demo and suites on separated skills
- **Tier**: M
- **Status**: Not Started
- **Description**: Point the demo's verification and the release's runners at the two skills where they ran `perf_center.py` alone, rebuild and verify the demo, and run the suites of `agnos-graph`, `agnos-perf-center`, `agnos-meta-release` and `agnos-meta-plugin-proof`.
- **Requirement refs**: RQ-TRC-131, RQ-TRC-132, RQ-TRC-133
- **ADR refs**: ADR-TRC-022
- **Acceptance Criteria**:
  - Given the demo rebuilt and verified, Then every check passes And its perf center run wrote `agnos-process/4.knowledge/agnos-graph.json`
  - Given the listed suites, Then they pass And no failing test was changed except to reflect the new input of the perf center
- **Dependencies**: TASK-TRC-121
- **Assignee**: AI
- **Verification**:
- **Assumptions**:
