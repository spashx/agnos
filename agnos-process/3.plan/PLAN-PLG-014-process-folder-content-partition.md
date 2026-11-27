# PLAN-PLG-014: Process folder content partition

## Overview
Adds the `0.facts/` and `4.knowledge/` subfolders to the AGNOS layout, restricts the artifact index to the declared indexed
subfolders, and aligns every description of the process folder, the demo and the tests on the new layout. The facts index and
the skills transforming facts are out of scope (FTR-PLG-010).

## References
- **Requirement refs**: RQ-PLG-048, RQ-PLG-049, RQ-PLG-050
- **ADR refs**: ADR-PLG-010 (DEC-PLG-038, DEC-PLG-039, DEC-PLG-040); extends ADR-PLG-006 (DEC-PLG-027, DEC-PLG-028)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-PLG-092: Restrict the index to indexed subfolders
- **Tier**: L
- **Status**: Done
- **Description**: Add `0.facts`, `4.knowledge` and the `process_indexed` list to `layout.json`, regenerate every layout copy with `layout.py --write`, and make `build-index.ps1` / `build-index.sh` scan the `process_indexed` list only.
- **Requirement refs**: RQ-PLG-048, RQ-PLG-049, RQ-PLG-050
- **ADR refs**: ADR-PLG-010 (DEC-PLG-038, DEC-PLG-039)
- **Acceptance Criteria**:
  - Given `layout.json`, Then `subfolders` lists `0.facts` and `4.knowledge` And `process_indexed` lists `1.requirements`, `2.architecture`, `3.plan`
  - Given a document holding `RQ-ABC-001` in `0.facts/` or in `4.knowledge/`, When `agnos-index` runs on Windows and on Linux, Then `process.idx.md` holds no row for it
  - Given this repository, When `agnos-index` runs, Then `process.idx.md` is unchanged
  - Given `layout.py --check`, Then it passes
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: test_layout.py 18/18 OK (new RQ-PLG-050 test: py/ps1/sh read the same `process_indexed`); test-build-index.ps1 and .sh "All checks passed", nominal fixture holding RQ-FCT-001 in 0.facts/ and FTR-KNW-001 in 4.knowledge/ with expected index unchanged (5 checks failed before the script change); repository index "unchanged"; `layout.py --check` 0 findings; 0 tests skipped.
- **Assumptions**: The key `process_indexed` keeps the owner's snake_case name, unlike the camelCase keys (owner, 2026-11-22).

### TASK-PLG-093: Create facts and knowledge folders at init
- **Tier**: M
- **Status**: Done
- **Description**: Add the `0.facts.readme.md` and `4.knowledge.readme.md` templates stating each folder's nature, so that `agnos-init` creates both folders with their `readme.md` on a new project and adds them to an existing one.
- **Requirement refs**: RQ-PLG-048, RQ-PLG-049, RQ-PLG-050
- **ADR refs**: ADR-PLG-010 (DEC-PLG-038, DEC-PLG-040)
- **Acceptance Criteria**:
  - Given an empty project, When `agnos-init` runs on Windows and on Linux, Then `agnos-process/0.facts/readme.md` and `agnos-process/4.knowledge/readme.md` exist
  - Given an AGNOS project without both folders, When `agnos-init` runs, Then both are added And no other file changes
  - Given the `0.facts` readme, Then it states that the user places the facts, that their content is never changed, and that a skill may transform and index them
  - Given the `4.knowledge` readme, Then it states that its content is dynamic, of uneven maturity, and dated
- **Dependencies**: TASK-PLG-092
- **Assignee**: AI
- **Verification**: agnos-init suite 45 tests OK after TASK-PLG-094 (RQ-INI-005 checks both new readmes byte-equal to their template, no ID, same bytes from both scripts; new RQ-PLG-048, RQ-PLG-049 wording tests; new RQ-PLG-050 test: folders removed then re-added, snapshot identical); 0 skipped.
- **Assumptions**: None

### TASK-PLG-094: Describe facts and knowledge folders in the process
- **Tier**: L
- **Status**: Done
- **Description**: List `0.facts/` and `4.knowledge/` with their nature in every Markdown file describing the process folder: the instructions file (PROCESS FOLDER STRUCTURE), `AGENTS.md`, `CLAUDE.md`, `AGNOS-GETTING-STARTED.md`, `CONTRIBUTING.md`, the PR template and the website's content.
- **Requirement refs**: RQ-PLG-048, RQ-PLG-049, RQ-PLG-050
- **ADR refs**: ADR-PLG-010 (DEC-PLG-040)
- **Acceptance Criteria**:
  - Given each file describing the process subfolders, Then it lists `0.facts/` and `4.knowledge/` with their nature
  - Given the instructions file, Then it states that facts are user-placed and immutable, that a skill may transform and index them, that knowledge is dated, And its line count stays at or under 400
  - Given `layout.py --check` and the `agnos-meta-release` suite, Then they pass
- **Dependencies**: TASK-PLG-092
- **Assignee**: AI
- **Verification**: instructions file 395 lines (<= 400; 393 before, `[IO.File]::ReadAllLines` count, blank lines included); edited: instructions PROCESS FOLDER STRUCTURE, AGENTS.md section 5, AGNOS-GETTING-STARTED.md (folder count, artifacts table), CONTRIBUTING.md; `layout.py --check` 0 findings; agnos-init 45 OK (RQ-PLG-023 guide test now passes); agnos-meta-release OK, 2 skipped: 'the demo is not built' (covered by TASK-PLG-095).
- **Assumptions**: CLAUDE.md, the PR template and the website's content cite a path or an index excerpt but do not describe the subfolders, so they are left unchanged; the guide cites no internal ID.

### TASK-PLG-095: Align demo and suites on the new layout
- **Tier**: M
- **Status**: Done
- **Description**: Update the demo's scenario and scripts to the new subfolders, and run the suites of `agnos-init`, `agnos-index`, `agnos-session`, `agnos-perf-center`, `agnos-meta-release` and `agnos-meta-release-prep`, fixing the tests whose expected layout changes.
- **Requirement refs**: RQ-PLG-050
- **ADR refs**: ADR-PLG-010 (DEC-PLG-038, DEC-PLG-039)
- **Acceptance Criteria**:
  - Given the demo rebuilt by `agnos-meta-demo`, Then its process folder holds `0.facts/` and `4.knowledge/` And its verification passes
  - Given the listed suites, When they run, Then they all pass And no failing test was changed except to reflect the new layout
- **Dependencies**: TASK-PLG-092, TASK-PLG-093, TASK-PLG-094
- **Assignee**: AI
- **Verification**: demo rebuilt by `build.ps1 -Verify`: 90 commits, 28 passed 0 failed, `0.facts/readme.md` and `4.knowledge/readme.md` present, no scenario change needed (agnos-init creates them from the layout); index tests ps1 and sh "All checks passed"; agnos-init OK; agnos-session OK; agnos-meta-release 152 OK, 0 skipped (the 2 demo tests now run); agnos-meta-release-prep OK; agnos-perf-center 443 OK, 3 skipped: the performance measures gated by `AGNOS_PERF_CENTER_PERF` (delivery, history, call graph); no test changed.
- **Assumptions**: The 3 perf-center skips are the three `AGNOS_PERF_CENTER_PERF` measures, inferred from the skip conditions (a missing browser would skip dozens).
