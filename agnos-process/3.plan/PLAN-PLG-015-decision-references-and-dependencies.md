# PLAN-PLG-015: Decision references and dependencies

## Overview
Delivers the owner's edit of the ADR template of the instructions file (2026-11-22): every DEC names its requirement
references and the DECs it depends on, and its rationale may no longer be "None". Aligns RQ-PLG-040, the demo's ADRs,
the user's guide and the changelog. Out of scope: rewriting the existing DECs of this repository's `agnos-process/`.

## References
- **Requirement refs**: RQ-PLG-040, RQ-DMO-005
- **ADR refs**: None

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-PLG-096: Align decision fields across AGNOS
- **Tier**: M
- **Status**: Done
- **Description**: Amend RQ-PLG-040 to the owner's DEC template, and add Requirement refs and Dependencies to every DEC of the demo and of the user's guide, with a changelog entry.
- **Requirement refs**: RQ-PLG-040, RQ-DMO-005
- **ADR refs**: None
- **Acceptance Criteria**:
  - Given the ADR template of the instructions file, Then each DEC holds a Statement, a Rationale with no "None", Requirement refs and Dependencies
  - Given the DECs of the demo and of the user's guide, Then each holds the four fields
  - Given the rebuilt demo, When its verification and suites run, Then they pass And every scenario edit finds its text
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: Instructions file line 242 re-read: `**Requirement refs**:` and `**Dependencies**` present, Rationale without "None"; file 397 lines (budget 400). Demo script: 12/12 DECs given both fields; guide 2/2. `build.ps1 -Verify`: "28 passed, 0 failed", RQ-DMO-005 "ADRs 7 (7 with DEC and diagram), duplicate IDs 0"; scenario replayed, so every edit found its text; 0 tests skipped.
- **Assumptions**: The website's ADR excerpt shows a DEC heading only, not a DEC's fields: left unchanged.
