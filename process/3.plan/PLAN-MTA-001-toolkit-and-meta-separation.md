# PLAN-MTA-001: The Prefix and the Layers

## Overview
First step of ADR-MTA-001: rename the two meta skills and make the prefix the only criterion, in one commit since the demo's
exclusions depend on both, then state the layers. Everything stays on the local branch `feature/TRC`: nothing is pushed. The release
build is the next plan.

## References
- **Requirements**: RQ-MTA-001 to RQ-MTA-004; amended: RQ-DMO-002, RQ-DMO-020
- **ADRs**: ADR-MTA-001 (DEC-MTA-002, DEC-MTA-003); amended: DEC-DMO-006

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-MTA-001: Rename the meta skills, the prefix as the only criterion
- **Tier**: L
- **Status**: Done
- **Description**: Accept ADR-MTA-001, amend DEC-DMO-006, RQ-DMO-002 and RQ-DMO-020 with their dates. Write the tests of the criterion first, then `git mv` both skills, their pointers and the sub-agent, update their live references, make `changes_since.py`, `baselineExclude` and `MAINTAINER_PATTERN` read the prefix, and rebuild the demo.
- **Requirement refs**: RQ-MTA-001, RQ-MTA-002, RQ-MTA-003, RQ-DMO-002, RQ-DMO-020
- **ADR refs**: ADR-MTA-001 (DEC-MTA-003), ADR-DMO-001 (DEC-DMO-006)
- **Acceptance Criteria**: Given the repository, Then each criterion of RQ-MTA-001 and RQ-MTA-002 holds in Gherkin-named tests; Given the demo built before this task, When `agnos-meta-demo build -Verify` runs, Then the criterion of RQ-MTA-003 holds; Given `git log --follow` on a renamed `SKILL.md`, Then it reaches the file's earlier history.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `agnos-meta-docs-sync/tests`: 14 OK; `agnos-meta-demo/tests/test_meta_prefix.py`: 4 OK, failing before the code; report flags only the two `agnos-meta-` skills. Demo built before this task, `build -Verify`: rebuilt, HEAD efeb53b, 22 passed, 0 failed, 0 meta file. Staged renames detected, 102 at 95% similarity or more; `git log --follow` checked after the commit, reported in TASK-MTA-002.
- **Assumptions**: tests live in a new `agnos-meta-demo/tests/` folder; `MARKER_TEXT` and the scripts' output prefix follow the new name since nothing reads them; `README.md`'s exclusion stays by path; `ADR-TRC-012` keeps its mention as history.

### TASK-MTA-002: State the layers
- **Tier**: M
- **Status**: Not Started
- **Description**: Add the three layers and the prefix rule to `CONTRIBUTING.md`, correct its line budget from 800 to 400, and add one `CHANGELOG.md` bullet under `[Unreleased]` for the renaming.
- **Requirement refs**: RQ-MTA-004
- **ADR refs**: ADR-MTA-001 (DEC-MTA-002)
- **Acceptance Criteria**: Given `CONTRIBUTING.md`, Then the criterion of RQ-MTA-004 holds.
- **Dependencies**: TASK-MTA-001
- **Assignee**: AI
- **Verification**:
- **Assumptions**:
