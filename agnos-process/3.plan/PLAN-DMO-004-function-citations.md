# PLAN-DMO-004: Function citations in the demo code

## Overview
Bring the demo's "Functions traced" score from 3.0 (154 of 219 functions uncited on 2026-11-12) to between 8.5 and
10.0, by citing the requirement of each public function and of each test function, then rebuild and verify the demo
with the agent collaboration of PLAN-DMO-003.

## References
- **Requirements**: RQ-DMO-026; RQ-DMO-004, RQ-DMO-008, RQ-DMO-021; RQ-PLG-025, RQ-PLG-026; RQ-DMO-023 to RQ-DMO-025
- **ADRs**: ADR-DMO-001 (DEC-DMO-004, DEC-DMO-005, DEC-DMO-006); ADR-DMO-002

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-DMO-017: Cite requirements in demo functions
- **Tier**: M
- **Status**: Done
- **Description**: Amend `references/code-contract.md` so that each public function, method and test cites its
  requirement in its docstring or in the comment just above it, private helpers, special methods and one-line accessors
  excepted; add those citations in the Python and TypeScript files of the content library, with no other change of code.
- **Requirement refs**: RQ-DMO-026, RQ-DMO-004, RQ-PLG-025, RQ-PLG-026
- **ADR refs**: ADR-DMO-001 (DEC-DMO-004)
- **Acceptance Criteria** (Gherkin): Given the content library, When `agnos-perf-center --call-graph` runs on its
  `service` and `client` folders, Then "Functions traced" is at least 8.5 and below 10.0, and each uncited function is
  private, special or a one-line accessor; Given the demo's Python and TypeScript tests, When they run, Then all pass;
  Given each cited ID, Then it is defined in the content's `agnos-process/` and committed before the file citing it.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: 28 content files, 218 comments added, no code changed. Scenario replayed into a scratch folder,
  `verify.ps1`: RQ-DMO-026 PASS, Functions traced 8.6 (30 uncited of 219, all `__init__`/`__post_init__` or private test
  helpers); RQ-DMO-017 PASS (81 commits, 0 citation before definition); RQ-DMO-004 PASS. `service`: 93 tests OK;
  `client`: `node --test "tests/*.test.ts"` 81 pass, 0 skipped.
- **Assumptions**: each function cites an ID of its file's header line; the call graph parses Python only, so the
  TypeScript citations do not move the score; nine private helpers of `api.py` are cited, being part of RQ-CLI-005.

### TASK-DMO-018: Rebuild the demo with agents
- **Tier**: M
- **Status**: Not Started
- **Description**: Run `agnos-meta-demo build` twice and `verify` on the demo, and record the Performance Center's
  history and "Functions traced" figures.
- **Requirement refs**: RQ-DMO-023, RQ-DMO-024, RQ-DMO-025, RQ-DMO-026, RQ-DMO-021, RQ-DMO-020
- **ADR refs**: ADR-DMO-002, ADR-DMO-001 (DEC-DMO-005, DEC-DMO-006)
- **Acceptance Criteria** (Gherkin): Given the demo rebuilt, When `verify` runs, Then every line is PASS, those of
  RQ-DMO-023 to RQ-DMO-026 included; Given two builds, Then both end on the same HEAD; Given `agnos-perf-center
  --history` on the demo, Then its summary counts 4 agents.
- **Dependencies**: TASK-DMO-016, TASK-DMO-017
- **Assignee**: AI
- **Verification**: 
- **Assumptions**: 
