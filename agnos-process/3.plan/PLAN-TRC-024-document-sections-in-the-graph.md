# PLAN-TRC-024: Document sections in the graph

## Overview
Gives `agnos-graph.json` a `sections` block holding the sections and subsections of the features, ADRs and plans that hold no
requirement, decision or task, with their citations, and proves that every other block and the perf center's data are unchanged.
The perf center is out of scope.

## References
- **Requirement refs**: RQ-TRC-134, RQ-TRC-135, RQ-TRC-136, RQ-TRC-137
- **ADR refs**: ADR-TRC-023 (DEC-TRC-078, DEC-TRC-079, DEC-TRC-080); extends ADR-TRC-022 (DEC-TRC-074, DEC-TRC-075)
- **Requirements handed to another component**: None; RQ-TRC-129 and RQ-TRC-130 (the graph file) are extended by a new block, not amended.

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-TRC-124: Record section feature and decisions
- **Tier**: S
- **Status**: Done
- **Description**: Write FTR-TRC-012, ADR-TRC-023 and this plan, accepted by the owner.
- **Requirement refs**: RQ-TRC-134, RQ-TRC-135, RQ-TRC-136, RQ-TRC-137
- **ADR refs**: ADR-TRC-023
- **Acceptance Criteria**: Given the three documents, When `agnos-index` runs, Then it reports no duplicate And ADR-TRC-023 is Accepted.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: None

### TASK-TRC-125: Implement section nodes in the graph
- **Tier**: L
- **Status**: Done
- **Description**: Write the Gherkin-named tests on fixtures first, then the `sections` block in `graph.py`, and describe it in `graph-format.md`.
- **Requirement refs**: RQ-TRC-134, RQ-TRC-135, RQ-TRC-136, RQ-TRC-137
- **ADR refs**: ADR-TRC-023 (DEC-TRC-078, DEC-TRC-079, DEC-TRC-080)
- **Acceptance Criteria**:
  - Given a fixture ADR with `## Context` and `## Decision` holding a DEC, When the graph is built, Then `ADR-…#Context` is in `sections` And `## Decision` is not
  - Given a fixture feature with an added `## Glossary`, Then it is a section
  - Given a `###` inside a retained section and a `####` inside it, Then the `###` is a level 3 node with its parent And the `####` is no node
  - Given two `### Note` under one section, Then their identifiers end in `/Note` and `/Note.2`
  - Given a citation in a section's own lines and one in its subsection, Then each is attributed to the narrowest section, with its line and text
  - Given the graph fixtures, Then `elements`, `edges`, `files` and `tasks` equal the expected files of before the change And two runs write the same bytes
  - Given the suites of `agnos-graph` and `agnos-perf-center`, Then all pass
- **Dependencies**: TASK-TRC-124
- **Assignee**: AI
- **Verification**: `test_sections.py` written first (3 errors, 1 failure before the code), then 11 OK on `fixtures/sections` (Context kept, Decision and Functional Requirements excluded, added Glossary kept, fenced heading ignored, `/Scope` level 3 and `####` no node, `/Note.2`, narrowest citation with proofs, model unchanged, no `SEC` in elements or edges, two runs byte-identical). `test_graph.py` STATE_KEYS gains `sections` (new expected behavior); `test_skill_contract` required `sections` in `graph-format.md`, documented. agnos-graph 157 OK, 0 skipped; agnos-perf-center 325 OK, 3 skipped (performance tests, need `AGNOS_PERF_CENTER_PERF=1`). This repository: 479 sections, all level 2.
- **Assumptions**: None

### TASK-TRC-126: Verify unchanged consumers on repository and demo
- **Tier**: M
- **Status**: Done
- **Description**: Compare the graph and the perf center's data of this repository and of the demo between the base commit and the change, rebuild and verify the demo, and add the changelog entry.
- **Requirement refs**: RQ-TRC-137, RQ-TRC-134
- **ADR refs**: ADR-TRC-023 (DEC-TRC-078)
- **Acceptance Criteria**:
  - Given this repository and the demo, When the graph is built at the base commit and after the change, Then every block but `sections` is identical And the perf center's data is identical
  - Given this repository, Then `sections` holds the sections of its ADRs, features and plans
  - Given the demo, When `build.ps1 -Verify` runs, Then it reports 0 failed
- **Dependencies**: TASK-TRC-125
- **Assignee**: AI
- **Verification**: Graph built by base `969456a` (git worktree) and by the change on the same inputs, perf center run on each: repository, graph minus `sections` equal, perf center page and data byte-identical, 479 sections; demo, same, 75 sections. `build.ps1 -Verify`: "28 passed, 0 failed", 0 skipped. CHANGELOG `[Unreleased]` Added entry.
- **Assumptions**: None
