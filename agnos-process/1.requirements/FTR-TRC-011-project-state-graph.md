# FTR-TRC-011: Project state graph

## Overview
The construction of the graph of the AGNOS project is separated from the performance center. A new skill, `agnos-graph`,
builds the state of the project at a given time: the elements of the process index and their links, the IDs cited by the
sources, and, on request, the call graph (tree-sitter) and the history (git). It writes it as one dated file in the knowledge
folder, `4.knowledge/agnos-graph.json` (FTR-PLG-010). `agnos-perf-center` no longer reads the process or the sources: it reads
that graph, computes the coverage, the findings and the quality score, and writes the page; it calls `agnos-graph` when the
graph is absent or when asked to rebuild it.

The word "state" names the content of the graph: true at its date and commit, unlike a fact of `0.facts/` (RQ-PLG-048).

Source: the owner's session of 2026-11-22.

Out of scope: rebuilding a graph found stale by comparing dates; new content in the graph or the page; the facts index.

## Stakeholders
- **Owner**: the repository owner (maintainer of AGNOS).
- **Consumers**: `agnos-perf-center`; any tool or agent reading the project's state; the demo and the release, which run both skills.

---

## Functional Requirements

### RQ-TRC-129: Project state graph file
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The `agnos-graph` skill SHALL write the state of the project, read from `--process` and `--sources` with the options `--ext`, `--exclude`, `--call-graph`, `--history`, `--history-since` and `--history-depth` of the performance center, to `agnos-process/4.knowledge/agnos-graph.json` by default or to `--out`, holding the elements, the edges with their proofs, the scanned files, the tier of each task, and, when asked, the call graph and the history with the delivery, and SHALL hold no coverage, finding or score.
- **Rationale**: the state is reusable by any tool once it is apart from what the performance center judges of it.
- **Priority**: Must
- **Acceptance Criteria**: Given a project, When `agnos-graph` runs with `--process` and `--sources`, Then `agnos-process/4.knowledge/agnos-graph.json` holds `elements`, `edges`, `files` And no `coverage` nor `quality`; Given `--call-graph` and `--history`, Then it also holds `callGraph`, `history` and `delivery`; Given the same inputs and a fixed `--generated-at`, When it runs twice, Then the two files are byte-identical; Given a missing source folder, Then it exits 1 And writes nothing.
- **Dependencies**: RQ-PLG-049, RQ-TRC-003 to RQ-TRC-007, RQ-TRC-026, RQ-HST-001

### RQ-TRC-130: State date of the graph
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The graph file SHALL state when it was produced (`generatedAt`) and the commit of the repository it was read at (`commit`, or null outside git), with the process folder, the source folders and the scan lists it was read with.
- **Rationale**: a state is true only at its date (RQ-PLG-049); a reader must know which commit and which scan it describes.
- **Priority**: Must
- **Acceptance Criteria**: Given a graph written in a git repository, Then its `meta` holds `generatedAt`, the HEAD commit, `process`, `sources`, the extensions and the exclusions used; Given a folder outside git, Then `commit` is null And the graph is written.
- **Dependencies**: RQ-TRC-129, RQ-TRC-119

### RQ-TRC-131: Performance center fed by the graph
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: `agnos-perf-center` SHALL read the graph file given by `--graph` (default `agnos-process/4.knowledge/agnos-graph.json`), compute from it the coverage, the findings and the quality score, and write the page and its data files with the same content as before the separation for the same inputs.
- **Rationale**: the page stays what its readers know; only where its input comes from changes.
- **Priority**: Must
- **Acceptance Criteria**: Given a graph built from the test fixture with a fixed date, When `agnos-perf-center` runs on it, Then `<page>.json` equals what the single generator wrote before the separation, `meta` excepted for its new fields; Given a graph without `callGraph`, Then the page has no call graph And the run exits 0; Given a graph file that is not valid JSON or lacks `elements`, Then it exits 1 naming the file.
- **Dependencies**: RQ-TRC-129, RQ-TRC-008 to RQ-TRC-010, RQ-TRC-064

### RQ-TRC-132: Graph built on demand by the performance center
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the graph file is absent, or `--rebuild` is given, `agnos-perf-center` SHALL invoke `agnos-graph` with its scan options before reading the graph; IF the graph file is absent and no `--sources` is given, THEN it SHALL exit 1 saying that `--sources` is needed to build it.
- **Rationale**: one command still produces the page from nothing, and an existing state is not rebuilt unasked (owner, 2026-11-22).
- **Priority**: Must
- **Acceptance Criteria**: Given no graph file, When `agnos-perf-center --process P --sources S` runs, Then the graph file exists And the page is written; Given an existing graph, When it runs without `--rebuild`, Then the graph file is not rewritten; Given `--rebuild`, Then the graph is rewritten; Given no graph and no `--sources`, Then it exits 1 And writes nothing.
- **Dependencies**: RQ-TRC-129, RQ-TRC-131

### RQ-TRC-133: Graph skill delivered with its contract
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: `agnos-graph` SHALL be a delivered skill with a `SKILL.md` for GitHub Copilot, its Claude Code pointer, a reference describing the graph file's format, and its entry in `AGENTS.md`, `CLAUDE.md` and the plugin's README; the call graph and history code and dependencies SHALL move with it, with their unit tests and new tests of the graph file, while the tests checking the page stay in the performance center and load the moved modules from `agnos-graph` (owner, 2026-11-22).
- **Rationale**: an agent finds a skill by its description and its entry points; the code that builds the graph is maintained where it lives.
- **Priority**: Must
- **Acceptance Criteria**: Given a release rehearsal, Then the marketplace holds `plugins/agnos/skills/agnos-graph/SKILL.md` And the proof passes; Given `AGENTS.md`, `CLAUDE.md` and the plugin README, Then each lists `agnos-graph`; Given the suites of both skills, Then they pass on Windows.
- **Dependencies**: RQ-TRC-129, RQ-PLG-003, RQ-TRC-098
