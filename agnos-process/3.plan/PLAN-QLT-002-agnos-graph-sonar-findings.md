# PLAN-QLT-002: Corrected agnos-graph scripts

## Overview
Corrects the 4 SonarQube findings VS Code reports on the scripts of `agnos-graph`, in one task, with no change of behaviour.

## References
- **Requirement refs**: RQ-QLT-011
- **ADR refs**: ADR-QLT-001 (DEC-QLT-007)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-QLT-008: Correct Sonar findings of agnos-graph scripts
- **Tier**: S
- **Status**: Done
- **Description**: In `history.py`, write `ID_RE` with `\d` (and `re.ASCII`) instead of `[0-9]` (python:S6353, 2 findings); in `graph.py`, keep each `# noqa: E402` alone on its line so SonarQube reads it, the traceability moving to a comment above (python:S7632, 2 findings).
- **Requirement refs**: RQ-QLT-011
- **ADR refs**: ADR-QLT-001 (DEC-QLT-007)
- **Acceptance Criteria**: Given both scripts, When their VS Code diagnostics are read, Then none is left, And both still parse.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: `re.ASCII` keeps `[0-9]`'s ASCII-only matching; the traceability comment of the two imports stays in `graph.py`, above them.

### TASK-QLT-009: Rewrap long lines of agnos-graph scripts
- **Tier**: M
- **Status**: Done
- **Description**: Rewrap the 7 lines above 120 characters that `agnos-meta-qa` reports in `graph.py` (4) and `history.py` (3), with no change of behaviour. The 2 cognitive-complexity findings stay out of this task.
- **Requirement refs**: RQ-QLT-011
- **ADR refs**: ADR-QLT-001 (DEC-QLT-006)
- **Acceptance Criteria**: Given both scripts, When `agnos-meta-qa check` runs on them, Then no E501 finding is open, And both still parse.
- **Dependencies**: TASK-QLT-008
- **Assignee**: AI
- **Verification**: `agnos-meta-qa check` on both scripts: 2 open, both cognitive-complexity (was 9 open: 7 E501); `ast.parse` of both: OK; tests skipped: session `tests=false`.
- **Assumptions**: Tier M since 7 lines change, above Tier S's 5; the 2 complexity findings are left for a later task, as the owner asked; `# RQ-TRC-144` comment on graph.py's `--explorer` line shortened by dropping "which stays".

### TASK-QLT-010: Rename old repository name in live files
- **Tier**: M
- **Status**: Done
- **Description**: Replace `agnos-lightweight-process.demo` by `agnos-demo` in the demo, release and website skills, the wording of FTR-DMO-001, ADR-DMO-001, ADR-WEB-001, PLAN-DMO-001 and PLAN-PLG-013, and `agnos-lightweight-process` by `agnos` in FTR-DMO-001. ADR-DOC-001, FTR-MTA-001 and PLAN-INI-001 keep the old name, which they cite as history.
- **Requirement refs**: RQ-DMO-001
- **ADR refs**: ADR-DMO-001
- **Acceptance Criteria**: Given the repository, When `git grep -i lightweight-process` runs, Then only the 3 historical mentions are left, And the scripts still parse.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `git grep -n -I -i lightweight-process`: 3 hits (ADR-DOC-001:8, FTR-MTA-001:52, PLAN-INI-001:50); `ast.parse` of `release.py` and `test_page.py`, and `tokens.json` parse: OK; tests skipped: session `tests=false`.
- **Assumptions**: the renamed local folder is `agnos-demo`, the dev's own folder name and the demo's remote `spashx/agnos-demo`; no requirement amendment beyond the folder name; the `.complexipy_cache` folder, ignored by git, was deleted; the demo skill's tests and `build -Verify` were not run.
