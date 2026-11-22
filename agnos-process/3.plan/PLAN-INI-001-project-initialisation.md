# PLAN-INI-001: The agnos-init Skill

## Overview
Delivers `agnos-init`, states where it must be called, and makes the demo an initialised project. Everything stays local on
`feature/TRC`: nothing is pushed.

## References
- **Requirement refs**: RQ-INI-001 to RQ-INI-009; amended: RQ-IDX-008, RQ-MTA-005, RQ-DMO-002
- **ADR refs**: ADR-INI-001 (DEC-INI-001 to DEC-INI-006); amended: DEC-MTA-005, DEC-MTA-006

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-INI-001: The skill and its scripts
- **Tier**: L
- **Status**: Done
- **Description**: Accept ADR-INI-001 and amend DEC-MTA-005. Write first one Python test suite that runs both scripts on the same cases. Then write `agnos-init` with skill-creator's guidance: `SKILL.md`, Claude Code pointer, `init.ps1`, `init.sh`, two templates, line-ending rules in `.gitattributes`, and its entries in `CLAUDE.md`, `AGENTS.md` and `CHANGELOG.md`.
- **Requirement refs**: RQ-INI-001, RQ-INI-002, RQ-INI-003, RQ-INI-004, RQ-INI-005, RQ-INI-006, RQ-INI-009
- **ADR refs**: ADR-INI-001 (DEC-INI-001 to DEC-INI-005), ADR-MTA-001 (DEC-MTA-005)
- **Acceptance Criteria**: Given the test suite, When it runs both scripts, Then each criterion of RQ-INI-001 to RQ-INI-006 and RQ-INI-009 holds, And both give the same bytes on each case.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `agnos-init/tests`: 14 OK, comparing both scripts' bytes; two failed first and exposed a lost BOM (PowerShell) and an undetected CRLF (bash). `agnos-meta-docs-sync/tests`: 14 OK; `agnos-meta-demo/tests`: 5 OK.
- **Assumptions**: the bash version was run by Git Bash on Windows, not on Linux or macOS; an absolute toolkit path is accepted and written as given, the skill recommending a relative one; skill-creator's evals were not run, since the skill's result is checked byte for byte.

### TASK-INI-002: State where the call is needed
- **Tier**: M
- **Status**: Done
- **Description**: Amend RQ-IDX-008. Update its tests, then the error of `agnos-index` in both versions. Add the rule to START SESSION, and the step to `README.md` and `GETTING_STARTED.MD`.
- **Requirement refs**: RQ-INI-007, RQ-IDX-008
- **ADR refs**: ADR-INI-001 (DEC-INI-006)
- **Acceptance Criteria**: Given the `agnos-index` tests in both versions, Then they pass with the new text; Given the instructions file, Then the criterion of RQ-INI-007 holds, And its post-edit line count is at most 400; Given `README.md` and `GETTING_STARTED.MD`, Then each gives the step.
- **Dependencies**: TASK-INI-001
- **Assignee**: AI
- **Verification**: `agnos-index` tests: 1 and 2 FAIL before the scripts' change, then "All checks passed" in PowerShell and Git Bash. Instructions: rule at line 47, 383 lines. `README.md` lines 37-44 and `GETTING_STARTED.MD` line 31 give the step. `agnos-init/tests` and `agnos-meta-docs-sync/tests`: OK.
- **Assumptions**: the test's expected text changed because the required behaviour changed (RQ-IDX-008 amended); the README's commands assume the clone beside the project, its usual layout.

### TASK-INI-003: The demo as an initialised project
- **Tier**: L
- **Status**: Done
- **Description**: Amend RQ-MTA-005, RQ-DMO-002 and DEC-MTA-006. Write the checks first: allow only the two files in `$TOOLKIT_PATTERN`, add `INI` and `MTA` to its trigrams, and add the check of RQ-INI-008. Then add a scenario field that calls `agnos-init` in the first commit, correct the demo's README, rebuild and verify.
- **Requirement refs**: RQ-INI-008, RQ-MTA-005, RQ-DMO-002
- **ADR refs**: ADR-INI-001 (DEC-INI-004, DEC-INI-005), ADR-MTA-001 (DEC-MTA-006)
- **Acceptance Criteria**: Given the rebuilt demo, Then each criterion of RQ-INI-008 holds; Given `test_meta_prefix.py`, Then it passes with `CLAUDE.md` and `AGENTS.md` moved to the project's paths.
- **Dependencies**: TASK-INI-001
- **Assignee**: AI
- **Verification**: `test_meta_prefix.py`: 7 OK, 3 failing before the code. `build -Verify`: HEAD 2ca06f3, 23 passed, 0 failed; RQ-INI-008: 2 of 2 files hold the block alone, 0 change after a new call; RQ-DMO-021: same HEAD on a second build; RQ-DMO-002: 0 other toolkit file in the history. First commit holds `CLAUDE.md`, `AGENTS.md`, the git files and four `.gitkeep`. Suites: `agnos-init` OK, `agnos-meta-docs-sync` OK, `agnos-trace` 356 OK (3 skipped), `agnos-index` all passed.
- **Assumptions**: the second build of RQ-DMO-021 now runs in a folder beside the toolkit, removed afterwards, since the block's relative path is checked; the check of the toolkit path assumes this repository's folder name `agnos-lightweight-process`; no agent session was actually run in the demo.
