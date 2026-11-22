# PLAN-TRC-025: Typed element links

## Overview
Gives `agnos-graph.json` a `links` block naming, for each citation of a requirement, a decision, a task or a plan, the link field
holding it or `text`, and proves that every other block and the perf center's data are unchanged. The perf center is out of scope.

## References
- **Requirement refs**: RQ-TRC-138, RQ-TRC-139, RQ-TRC-140, RQ-TRC-141
- **ADR refs**: ADR-TRC-024 (DEC-TRC-081, DEC-TRC-082, DEC-TRC-083); extends ADR-TRC-022 (DEC-TRC-074, DEC-TRC-075)
- **Requirements handed to another component**: None; RQ-TRC-129 and RQ-TRC-130 (the graph file) are extended by a new block, not amended.

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-TRC-127: Document typed links of graph elements
- **Tier**: M
- **Status**: Done
- **Description**: Write FTR-TRC-013, ADR-TRC-024 and this plan.
- **Requirement refs**: RQ-TRC-138, RQ-TRC-139, RQ-TRC-140, RQ-TRC-141
- **ADR refs**: ADR-TRC-024
- **Acceptance Criteria**: Given the documents written, When `agnos-index` runs, Then FTR-TRC-013, its RQs, ADR-TRC-024, its DECs and PLAN-TRC-025 are indexed with no duplicate ID And each follows its template and the title rules.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `agnos-index`: 1072 entries, 172 documents, exit 0 (no duplicate); indexed FTR-TRC-013, RQ-TRC-138 to RQ-TRC-141, ADR-TRC-024 (Proposed), DEC-TRC-081 to DEC-TRC-083, PLAN-TRC-025, TASK-TRC-127 to TASK-TRC-129; titles checked against MANDATORY TITLE FORMAT.
- **Assumptions**: the perf center is out of scope, as for FTR-TRC-012; the field is written in a separate `links` block (DEC-TRC-081) so that it sees no side effect; ADR-TRC-024 accepted under the owner's order of 2026-11-22 to implement every task; PLAN is typed on its `References` fields, renamed as the task's by FTR-INI-003, at the owner's request of 2026-11-22.

### TASK-TRC-128: Implement link fields in the graph
- **Tier**: L
- **Status**: Done
- **Description**: Write the Gherkin-named tests on fixtures first, then the `links` block in `graph.py`, and describe it in `graph-format.md`.
- **Requirement refs**: RQ-TRC-138, RQ-TRC-139, RQ-TRC-140, RQ-TRC-141
- **ADR refs**: ADR-TRC-024 (DEC-TRC-081, DEC-TRC-082, DEC-TRC-083)
- **Acceptance Criteria**:
  - Given a fixture task citing an RQ in `Requirement refs` and another in `Description`, When the graph is built, Then their fields in `links` are `Requirement refs` and `text`
  - Given a fixture requirement citing IDs in `Statement` and `Dependencies`, and one holding `ADR refs`, Then their fields are `text`, `Dependencies` and `text`
  - Given a fixture plan citing an RQ in `Requirement refs` under `## References` and another in `## Overview`, Then their fields are `Requirement refs` and `text`
  - Given a `Dependencies` list wrapped over two lines before the next field line, Then both citations have field `Dependencies`
  - Given a fixture ADR citing a feature in its `## Context`, Then its `refs` edge is kept And `links` holds no row for it
  - Given the graph fixtures, Then every block but `links` equals the expected files of before the change And two runs write the same bytes
  - Given the suites of `agnos-graph` and `agnos-perf-center`, Then all pass
- **Dependencies**: TASK-TRC-127, TASK-INI-022
- **Assignee**: AI
- **Verification**: `test_links.py` written first on `fixtures/links` (5 errors before the code, `element_links` absent), then 10 OK: task `Requirement refs` vs `Description` `text`; RQ `Statement` `text`, `Dependencies`, misplaced `ADR refs` `text`; DEC `Rationale` `text`, `Requirement refs`; plan References vs Overview; wrapped `Dependencies` on two lines; ADR and feature edges kept with no row; model unchanged; each row matches its edge's proof lines; `links` its own block, `edges` equal. `test_graph.py` STATE_KEYS gains `links` (new expected behavior, 2 failures before). agnos-graph 167 OK, 0 skipped; agnos-perf-center 325 OK, 3 skipped (performance tests, need `AGNOS_PERF_CENTER_PERF=1`).
- **Assumptions**: None

### TASK-TRC-129: Verify link fields on repository and demo
- **Tier**: M
- **Status**: Done
- **Description**: Compare the graph and the perf center's data of this repository and of the demo between the base commit and the change, rebuild and verify the demo, and add the changelog entry.
- **Requirement refs**: RQ-TRC-141, RQ-TRC-138
- **ADR refs**: ADR-TRC-024 (DEC-TRC-081)
- **Acceptance Criteria**:
  - Given this repository and the demo, When the graph is built at the base commit and after the change, Then every block but `links` is identical And the perf center's data is identical
  - Given this repository, Then `links` holds one row per `refs` edge whose source is an RQ, a DEC, a TASK or a PLAN
  - Given the demo, When `build.ps1 -Verify` runs, Then it reports 0 failed
- **Dependencies**: TASK-TRC-128
- **Assignee**: AI
- **Verification**: Graph built by base `21cf6d1` (git worktree) and by the change on the same inputs, perf center run on each: repository, graph minus `links` equal, 5073 rows for 5073 `refs` edges of RQ/DEC/TASK/PLAN (Requirement refs 1565, ADR refs 1302, Dependencies 1110, text 1989), page, `.json` and `.data.js` byte-identical; demo, same, 266 rows for 266 edges (text 21). `build.ps1 -Verify`: "28 passed, 0 failed". CHANGELOG `[Unreleased]` Added entry.
- **Assumptions**: sources `.github` for this repository and `.` for the demo, the same on both sides.
