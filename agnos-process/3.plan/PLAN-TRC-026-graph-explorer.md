# PLAN-TRC-026: Graph explorer

## Overview
Moves the graph file into `4.knowledge/graph/`, gives the performance center's outputs lowercase names, and adds to the graph
skill an explorer page written with `--explorer`: whole graph content, shared type colours, resizable panels, tables, a graph
view with movable nodes, facets, a text query language and saved query buttons. The performance center reading `links` is out
of scope.

## References
- **Requirement refs**: RQ-TRC-142, RQ-TRC-143, RQ-TRC-144, RQ-TRC-145, RQ-TRC-146, RQ-TRC-147, RQ-TRC-148, RQ-TRC-149, RQ-TRC-150, RQ-TRC-151, RQ-TRC-152, RQ-TRC-153, RQ-TRC-154, RQ-TRC-155, RQ-TRC-156, RQ-TRC-157, RQ-TRC-158
- **ADR refs**: ADR-TRC-025 (DEC-TRC-084 to DEC-TRC-093); amends ADR-TRC-022 (DEC-TRC-077) and ADR-TRC-013 (DEC-TRC-054); design system ADR-TRC-002 (DEC-TRC-009, DEC-TRC-010), RQ-TRC-018
- **Requirements handed to another component**: amended in TASK-TRC-130, the first task that changes them: RQ-TRC-129 and RQ-TRC-131 (graph path, by RQ-TRC-142); RQ-TRC-105 and RQ-TRC-107 (output names, by RQ-TRC-143); RQ-TRC-001, RQ-TRC-016, RQ-TRC-121, RQ-DMO-026, RQ-MTA-011 and RQ-WEB-002 (output names cited); DEC-TRC-077 (by DEC-TRC-086); DEC-TRC-054 (by DEC-TRC-087); DEC-TRC-001, DEC-TRC-004, DEC-TRC-011, DEC-TRC-012, DEC-TRC-066, DEC-WEB-002 and DEC-WEB-008 (output names cited).

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-TRC-130: Document graph explorer feature
- **Tier**: L
- **Status**: Done
- **Description**: Write FTR-TRC-014, ADR-TRC-025 and this plan, and align the features and ADRs that name the graph path or the performance center's outputs, with a dated comment.
- **Requirement refs**: RQ-TRC-142 to RQ-TRC-158
- **ADR refs**: ADR-TRC-025 (DEC-TRC-084 to DEC-TRC-093), ADR-TRC-022 (DEC-TRC-077), ADR-TRC-013 (DEC-TRC-054)
- **Acceptance Criteria**:
  - Given the documents written, When `agnos-index` runs, Then FTR-TRC-014, RQ-TRC-142 to RQ-TRC-158, ADR-TRC-025, DEC-TRC-084 to DEC-TRC-093, PLAN-TRC-026 and its tasks are indexed with no duplicate ID
  - Given each new artifact, Then it follows its template and the title rules
  - Given the features and ADRs, When `PERF-CENTER` and `4.knowledge/agnos-graph.json` are searched, Then only dated former names remain And each aligned file holds its dated comment
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `agnos-index`: 1121 entries, 179 documents, exit 0 (no duplicate); 39 new IDs indexed (FTR-TRC-014, RQ-TRC-142 to RQ-TRC-158, ADR-TRC-025, DEC-TRC-084 to DEC-TRC-093, PLAN-TRC-026, TASK-TRC-130 to TASK-TRC-138); titles checked against MANDATORY TITLE FORMAT (four RQ titles rewritten); `git grep "PERF-CENTER|4.knowledge/agnos-graph.json"` on features and ADRs: no hit; 13 files aligned, each with its dated comment; RQ-TRC-105, RQ-TRC-129, RQ-TRC-131, DEC-TRC-054, DEC-TRC-077 name their amendment.
- **Assumptions**: the graph folder is under `4.knowledge/`; plans and `CHANGELOG.md` keep the former names as history (DEC-TRC-055); the explorer has no dark theme; RQ-TRC-158's 5 s threshold and the default button list are inferred; ADR-TRC-025 accepted by the owner on 2026-11-23, after its diagrams were split into the graph explorer and performance center systems; the owner's order of 2026-11-23 ("fais le plan et implémente") approves every task of this plan and their commits.

### TASK-TRC-131: Move graph file into graph folder
- **Tier**: L
- **Status**: Done
- **Description**: Write the Gherkin-named tests first, then set `graphFile` to `4.knowledge/graph/agnos-graph.json` in `layout.json`, regenerate its copies, and update every hit of a `git grep` of the former path: scripts, tests, `SKILL.md` files, `graph-format.md`, `AGENTS.md`, the guide, the demo and the release.
- **Requirement refs**: RQ-TRC-142, RQ-TRC-156
- **ADR refs**: ADR-TRC-025 (DEC-TRC-086)
- **Acceptance Criteria**:
  - Given a fixture project, When `agnos-graph` runs without `--out`, Then the graph is written to `4.knowledge/graph/agnos-graph.json`
  - Given that graph, When `agnos-perf-center` runs without `--graph`, Then it reads it without rebuilding And its data equals the data of before the change
  - Given `layout.json` and its copies, When `layout.py --check` runs, Then it reports 0 findings
  - Given the tracked files other than plans, `CHANGELOG.md` and the index, Then none names `4.knowledge/agnos-graph.json` but as a dated former path
  - Given the suites of the skills touched and the demo's `build.ps1 -Verify`, Then all pass
- **Dependencies**: TASK-TRC-130
- **Assignee**: AI
- **Verification**: 3 tests written first, each FAILED before the change (`test_graph` RQ_TRC_142 graph in `4.knowledge/graph/`, `test_perf_center` RQ_TRC_142 read not rebuilt, `test_layout` RQ_TRC_142 `graphFile`), OK after. `layout.py --write` then `--check`: 0 findings, 13 copies regenerated. `git grep 4.knowledge/agnos-graph.json` outside plans, changelog, index: 2 hits, both named former paths (test constant, ADR-TRC-025 consequence). Base `a92a72c` (worktree) vs change, same inputs and date: graph, page, `.json`, `.data.js` byte-identical. Suites: agnos-graph 168 OK; agnos-perf-center 326 OK, 3 skipped (performance tests, need `AGNOS_PERF_CENTER_PERF=1`); agnos-meta-release 153 OK; agnos-init 48 OK; agnos-index `test-build-index.ps1` all passed; demo `build.ps1 -Verify` 28 passed, 0 failed. agnos-session (import of `history` from the perf center's scripts) and agnos-meta-demo `test_citations` (IDs as text in `data-format.md`) fail identically at the base commit: not caused by this task, reported to the owner.
- **Assumptions**: SKILL.md files, `graph-format.md`, `AGENTS.md` and the guide updated in place, `CLAUDE.md` and the README naming no path; the agnos-session and test_citations failures are left out of scope.

### TASK-TRC-132: Rename performance center outputs to lowercase
- **Tier**: L
- **Status**: Done
- **Description**: Write the Gherkin-named tests first, then set `perfCenterPage` to `perf-center.html` in `layout.json`, regenerate its copies, and update every hit of a `git grep` of `PERF-CENTER`: the performance center, its former-name test, the website, the demo, `.gitignore`, `README.md`, the guide and the release.
- **Requirement refs**: RQ-TRC-143, RQ-TRC-106
- **ADR refs**: ADR-TRC-025 (DEC-TRC-087), ADR-TRC-013 (DEC-TRC-055)
- **Acceptance Criteria**:
  - Given a process folder and a graph, When `agnos-perf-center` runs without `--out`, Then `perf-center.html`, `perf-center.json` and `perf-center.data.js` are written
  - Given the tracked files other than plans, `CHANGELOG.md` and the index, When the former-name test runs, Then none names `PERF-CENTER.*`
  - Given the website built with `--demo-page`, Then `demo/perf-center.html` is its demo page
  - Given the suites of the skills touched and the demo's `build.ps1 -Verify`, Then all pass
- **Dependencies**: TASK-TRC-131
- **Assignee**: AI
- **Verification**: Tests first, FAILED before the change: `test_skill_name` RQ_TRC_105 (names read from the folder, case included, `is_file` being case-blind on Windows) and RQ_TRC_143 (uppercase outputs in live files), 6 `agnos-meta-website` tests expecting `perf-center.*`; all OK after. `layout.py --write` then `--check`: 0 findings. `git grep PERF-CENTER` outside plans, changelog, index: 2 hits, FTR-TRC-014 and ADR-TRC-025 naming them as former. Suites: agnos-perf-center 327 OK, 3 skipped (performance tests, need `AGNOS_PERF_CENTER_PERF=1`); agnos-graph 168 OK; agnos-meta-website 83 OK; agnos-meta-release 153 OK; agnos-init 48 OK; agnos-index all passed; demo `build.ps1 -Verify` 28 passed, 0 failed; agnos-meta-demo 18 tests, 1 failure, `test_citations` on `data-format.md`, the same as at the base commit of TASK-TRC-131.
- **Assumptions**: `.gitignore` and the demo's `gitignore.txt` list the lowercase names only, git matching ignore rules without case on Windows; the published website's demo page and the links of `README.md`, `assets/links.json` and the demo's READMEs take the lowercase name, which needs the website rebuilt and published by the owner.

### TASK-TRC-133: Generate explorer page shell
- **Tier**: L
- **Status**: Done
- **Description**: Write the Gherkin-named tests first, then add `--explorer` to `graph.py`, the `assets/explorer/` template, style, tokens with `type-*-text`, and the shell: data loading and file drop, view model, three panels with splitters, node and relation tables, detail panel.
- **Requirement refs**: RQ-TRC-144, RQ-TRC-145, RQ-TRC-146, RQ-TRC-147, RQ-TRC-148, RQ-TRC-149, RQ-TRC-154, RQ-TRC-155, RQ-TRC-156, RQ-TRC-157, RQ-TRC-018
- **ADR refs**: ADR-TRC-025 (DEC-TRC-084, DEC-TRC-085, DEC-TRC-088, DEC-TRC-089, DEC-TRC-091), ADR-TRC-002 (DEC-TRC-009, DEC-TRC-010)
- **Acceptance Criteria**:
  - Given a fixture project, When `agnos-graph --explorer` runs, Then `graph-explorer.html` and `agnos-graph.data.js` are written beside the graph And the graph's bytes equal those of a run without `--explorer`
  - Given a run without `--explorer`, Then no explorer file is written
  - Given the page opened in a headless browser, Then the node and relation tables list the fixture's nodes and relations, scroll under a fixed header and sort on a header click
  - Given a dropped file holding `{}`, Then a message names it And the former graph stays shown
  - Given the splitters, When dragged or moved with the arrow keys, Then the panels resize by the tokens' step
  - Given each `type-*-text` token, Then its contrast on the backgrounds is at least 4.5:1 And no raw visual value is in the explorer's code
  - Given a selected node, Then the detail panel lists its properties and relations with field and proofs
- **Dependencies**: TASK-TRC-132
- **Assignee**: AI
- **Verification**: `test_explorer.py` written first (run stopped on the unknown `--explorer` option), then 16 OK, 0 skipped, the 8 page tests in headless Edge: page and data script beside the graph only with `--explorer`; graph bytes equal with and without it; data script = `window.AGNOS_GRAPH = <graph>`; page English, markers replaced; every node type has `type-*` and `type-*-text`; each text token at least 4.5:1 on surface, surface-subtle, surface-selected (lowest 4.76, FTR on surface-selected); no raw visual value in `explorer.css`, `explorer.js`; header date and counts; tables list every node (elements, sections, files) and relation (edges, section relations); sticky header, scrolling body, sort by click then reversed; `{}` named with "no elements list", graph kept; another valid graph replaces it; splitters move by the step token with the arrow keys; selected plan's detail lists its `ADR refs` relation and proof; type label colour equals `--s-type-rq-text`. `test_perf_center` RQ_TRC_144: graph folder holds the graph alone when the perf center builds it. Suites: agnos-graph 185 OK (`test_literals` extended to `explorer.py` and `explorer.js`; `IndependenceTest` expects `explorer`, the skill's own module, DEC-TRC-084); agnos-meta-release 153 OK; `layout.py --check` 0 findings; agnos-meta-demo the known `test_citations` failure only. Screenshots of this repository's explorer (1984 nodes, 11778 relations) checked; long cells capped by a token and ellipsed after review.
- **Assumptions**: the default view is the node table until the graph view exists (TASK-TRC-134); sections relate to their parent by `contains` and to the IDs they cite by `refs` with no field, marked `origin: sections`; an undefined ID is shown with the type `UNDEFINED`; the header counts `elements` as the file lists them, undefined IDs included; the explorer writes no error page when its assets fail, `agnos-graph` exits 1 naming the asset.

### TASK-TRC-134: Implement explorer graph view
- **Tier**: M
- **Status**: Done
- **Description**: Write the Gherkin-named tests first, then the Cytoscape graph view: type colours, draggable nodes, wheel and button zoom, fit, pan, positions kept across filters, hide, isolate and widen by one hop.
- **Requirement refs**: RQ-TRC-147, RQ-TRC-150, RQ-TRC-154
- **ADR refs**: ADR-TRC-025 (DEC-TRC-090, DEC-TRC-091)
- **Acceptance Criteria**:
  - Given the graph view, When a node is dragged and a facet hides then shows another type, Then the node keeps its position
  - Given the fit button, Then every shown node is in the view; Given the wheel, Then the zoom stays within the tokens' bounds
  - Given a selected node, When its neighbourhood is isolated then widened, Then the nodes at one then two hops are shown; When it is hidden, Then it is listed as hidden And can be shown again
- **Dependencies**: TASK-TRC-133
- **Assignee**: AI
- **Verification**: `GraphViewTest` written first (6 errors, no graph hooks), then 6 OK in headless Edge with Cytoscape.js from cdnjs: a dragged node keeps its position while a type is hidden then shown; Fit frames every shown node; zoom bounds equal the tokens and 40 zoom-in clicks stay under the maximum; isolate shows the node and its one-hop neighbours (its feature included), widen shows more; a hidden node is listed, its chip shows it again; node colour equals `--s-type-rq`. Brand test: the header holds the five parts of the AGNOS mark and its colours equal the performance center's brand tokens. agnos-graph suite 192 OK, 0 skipped. Screenshots of this repository's graph: a neighbourhood isolated around RQ-TRC-142 laid in circles, readable.
- **Assumptions**: owner's request of 2026-11-23 during the task: the header's logo is the AGNOS mark "Spans" with the performance center's brand colours (RQ-TRC-114, DEC-TRC-056, copied); the graph view is the default view; the whole graph is laid in one column per type, wrapped every 40 nodes; isolating or widening lays the shown nodes in circles around the selection, one circle per hop, kept as moved positions; shown nodes are read from the hidden class, Cytoscape caching `visible()`; the fit test moves a node 5000 units away, the minimum zoom token framing about 11000.

### TASK-TRC-135: Implement explorer query language
- **Tier**: M
- **Status**: Not Started
- **Description**: Write the Gherkin-named tests first, then the term parser, its evaluation on the view model, the facets with counts that write their term into the query, and the error message.
- **Requirement refs**: RQ-TRC-151, RQ-TRC-152, RQ-TRC-155
- **ADR refs**: ADR-TRC-025 (DEC-TRC-092)
- **Acceptance Criteria**:
  - Given each term form of RQ-TRC-152, When it is run on the fixture, Then the shown nodes or relations are the expected ones
  - Given `type:`, Then a message names the term And the former result stays
  - Given a facet value unchecked, Then its nodes or relations are hidden in every view; When clicked with the query focused, Then its term is written into the query
- **Dependencies**: TASK-TRC-133
- **Assignee**: AI
- **Verification**: [to fill at closure]
- **Assumptions**: [to fill at closure]

### TASK-TRC-136: Implement saved query buttons
- **Tier**: M
- **Status**: Not Started
- **Description**: Write the Gherkin-named tests first, then the buttons under the query field, their creation, edition, deletion and reordering, their storage, export and import, and the default list in `presets.json`.
- **Requirement refs**: RQ-TRC-153, RQ-TRC-155
- **ADR refs**: ADR-TRC-025 (DEC-TRC-093)
- **Acceptance Criteria**:
  - Given an empty store, Then the default buttons of `presets.json` are shown
  - Given a button created, edited, moved or deleted, When the page is reloaded, Then the change is kept
  - Given the buttons exported then imported in a fresh browser profile, Then the same buttons are shown in the same order
- **Dependencies**: TASK-TRC-135
- **Assignee**: AI
- **Verification**: [to fill at closure]
- **Assumptions**: [to fill at closure]

### TASK-TRC-137: Show call graph and history
- **Tier**: M
- **Status**: Not Started
- **Description**: Write the Gherkin-named tests first, then add the call graph's functions and calls to the view model as nodes and relations, and the history and delivery as properties of their nodes and as table rows.
- **Requirement refs**: RQ-TRC-146
- **ADR refs**: ADR-TRC-025 (DEC-TRC-089)
- **Acceptance Criteria**:
  - Given a fixture graph built with `--call-graph` and `--history`, When it is loaded, Then the functions and calls are nodes and relations of every view
  - Given a task with history, Then its detail shows its commits and identities And its delivery
- **Dependencies**: TASK-TRC-134, TASK-TRC-135
- **Assignee**: AI
- **Verification**: [to fill at closure]
- **Assumptions**: [to fill at closure]

### TASK-TRC-138: Verify explorer on repository and demo
- **Tier**: M
- **Status**: Not Started
- **Description**: Build the graph and its explorer for this repository and the demo, time the explorer's first view, compare the graph and the performance center's data with the base commit, rebuild and verify the demo, and add the changelog entry.
- **Requirement refs**: RQ-TRC-156, RQ-TRC-158, RQ-TRC-142, RQ-TRC-143
- **ADR refs**: ADR-TRC-025 (DEC-TRC-085, DEC-TRC-086, DEC-TRC-087)
- **Acceptance Criteria**:
  - Given this repository and the demo, When the graph is built with and without `--explorer`, Then the two graph files are byte-identical
  - Given the performance center's data at the base commit and after the change, Then they are identical but for the names and the graph path
  - Given this repository's graph with call graph and history, When the explorer is opened headless, Then its first view is drawn in less than 5 s
  - Given the demo, When `build.ps1 -Verify` runs, Then it reports 0 failed
- **Dependencies**: TASK-TRC-136, TASK-TRC-137
- **Assignee**: AI
- **Verification**: [to fill at closure]
- **Assumptions**: [to fill at closure]
