# PLAN-PLG-002: A Deterministic Release and its Report Page

## Overview
Make `agnos-meta-release` give the same verdict whoever runs it, and write a page for its report (FTR-PLG-002). No push at any step
(DEC-PLG-007). The order: what the output holds, then what is said, then the page.

## References
- **Requirements**: RQ-PLG-012 to RQ-PLG-017, RQ-MTA-012, RQ-TRC-018
- **ADRs**: ADR-PLG-002, ADR-TRC-002, ADR-MTA-002

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-PLG-010: Feature, decisions and plan
- **Tier**: L
- **Status**: Done
- **Description**: Write FTR-PLG-002, ADR-PLG-002 and this plan, and mark RQ-MTA-012 as amended.
- **Requirement refs**: RQ-PLG-012 to RQ-PLG-017, RQ-MTA-012
- **ADR refs**: ADR-PLG-002
- **Acceptance Criteria**: Given the owner's approval, Then ADR-PLG-002 is Accepted, And RQ-MTA-012 names RQ-PLG-014; Given the index, Then it has no duplicate.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: ADR-PLG-002 Accepted, owner's "ok pour tout" of 2026-11-03; RQ-MTA-012 holds "Amended by: RQ-PLG-014"; `agnos-index` exit 0, no duplicate. No test: documents only.
- **Assumptions**: DEC-PLG-010 revised at the owner's review: the release checks manifests by script, Claude Code's validation stays in the proof.

### TASK-PLG-011: The output holds what is declared
- **Tier**: M
- **Status**: Done
- **Description**: No bytecode written by the checks, and an inventory of the output against the delivered and generated paths.
- **Requirement refs**: RQ-PLG-012
- **ADR refs**: ADR-PLG-002 (DEC-PLG-008)
- **Acceptance Criteria**: Given RQ-PLG-012's criteria, Then they hold.
- **Dependencies**: TASK-PLG-010
- **Assignee**: AI
- **Verification**: `test_inventory.py` written first, 2 of 3 failed (stray file exit 0, `__pycache__` written), then 3 OK; full meta-release suite 66 OK, 0 skipped, the demo rehearsal included.
- **Assumptions**: only extra files are named; a missing file is left to the existing checks. The release's own process imports nothing from the output, so only its subprocesses get `PYTHONDONTWRITEBYTECODE`.

### TASK-PLG-012: Same commit, same output
- **Tier**: M
- **Status**: Done
- **Description**: A test rehearsing HEAD twice and comparing trees and reports; fix any difference it finds.
- **Requirement refs**: RQ-PLG-013
- **ADR refs**: ADR-PLG-002 (DEC-PLG-008)
- **Acceptance Criteria**: Given RQ-PLG-013's criteria, Then they hold.
- **Dependencies**: TASK-PLG-011
- **Assignee**: AI
- **Verification**: `test_determinism.py` rehearses in two processes with `PYTHONHASHSEED` 1 and 2 (shown to order a same set differently): 2 OK, HEAD with the proof on the demo included; no difference found, so no code changed. Full suite 68 OK, 0 skipped.
- **Assumptions**: identical means file names and bytes; file modes and times are not compared. Another machine, Python version or system is not covered here: it is the proof's and `--linux`'s.

### TASK-PLG-013: The console says everything to act on
- **Tier**: M
- **Status**: Done
- **Description**: Print problems, lines to read, mentions and IDs outside comments, and end with the `exit=` line.
- **Requirement refs**: RQ-PLG-014, RQ-MTA-012
- **ADR refs**: ADR-PLG-002 (DEC-PLG-009)
- **Acceptance Criteria**: Given RQ-PLG-014's criteria, Then they hold.
- **Dependencies**: TASK-PLG-010
- **Assignee**: AI
- **Verification**: `test_console.py` written first, 5 of 5 failed, then 5 OK (line to read and mention printed with file and line; last line `exit=0`, `exit=1` after a failure, `exit=1, nothing written` after a refusal). Full suite 73 OK, 0 skipped.
- **Assumptions**: a rehearsal's problems move to the standard output with its other findings, so their order holds; refusals before writing stay on the error stream. `test_inventory.py` now reads both streams, as this new behaviour requires. The SKILL.md wording is left to TASK-PLG-017.

### TASK-PLG-014: The manifests checked by script
- **Tier**: L
- **Status**: Not Started
- **Description**: Replace the call of `claude plugin validate` by a script check of the manifests and catalogues, `checks.manifests` in the report.
- **Requirement refs**: RQ-PLG-015
- **ADR refs**: ADR-PLG-002 (DEC-PLG-010)
- **Acceptance Criteria**: Given RQ-PLG-015's criteria, Then they hold; Given `agnos-meta-plugin-proof`'s tests, Then they pass.
- **Dependencies**: TASK-PLG-013
- **Assignee**: AI
- **Verification**: 
- **Assumptions**: 

### TASK-PLG-015: The page's tokens from the perf center
- **Tier**: M
- **Status**: Not Started
- **Description**: Compile the output's perf-center tokens into the page's custom properties, and a stylesheet that uses only them.
- **Requirement refs**: RQ-PLG-017, RQ-TRC-018
- **ADR refs**: ADR-PLG-002 (DEC-PLG-012), ADR-TRC-002
- **Acceptance Criteria**: Given RQ-PLG-017's criteria, Then they hold.
- **Dependencies**: TASK-PLG-011
- **Assignee**: AI
- **Verification**: 
- **Assumptions**: 

### TASK-PLG-016: The report page
- **Tier**: M
- **Status**: Not Started
- **Description**: The `report.html` template, its embedded data and the sections of RQ-PLG-016, written beside the JSON.
- **Requirement refs**: RQ-PLG-016, RQ-PLG-017
- **ADR refs**: ADR-PLG-002 (DEC-PLG-011, DEC-PLG-012), ADR-TRC-002
- **Acceptance Criteria**: Given RQ-PLG-016's criteria, Then they hold.
- **Dependencies**: TASK-PLG-015, TASK-PLG-013
- **Assignee**: AI
- **Verification**: 
- **Assumptions**: 

### TASK-PLG-017: The skill said, and a rehearsal
- **Tier**: M
- **Status**: Not Started
- **Description**: Update the skill's procedure (exit code per shell, console, the manifest check, the page) and rehearse into `agnos-marketplace`.
- **Requirement refs**: RQ-PLG-012 to RQ-PLG-017
- **ADR refs**: ADR-PLG-002
- **Acceptance Criteria**: Given the skill, Then it states the new behaviour; Given a rehearsal of the last commit, Then the exit is 0, the output holds no stray file, And the page opens.
- **Dependencies**: TASK-PLG-012, TASK-PLG-014, TASK-PLG-016
- **Assignee**: AI
- **Verification**: 
- **Assumptions**: 
