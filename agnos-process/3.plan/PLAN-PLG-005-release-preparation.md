# PLAN-PLG-005: Release Preparation

## Overview
Write the maintainer skill `agnos-meta-release-prep` (FTR-PLG-005) and the release's line on unreleased entries, then run the
preparation once on this repository. Runs after PLAN-PLG-006: the process folder it names is the layout's
(RQ-PLG-034, RQ-PLG-036). No push at any step (DEC-PLG-007).

## References
- **Requirements**: RQ-PLG-027, RQ-PLG-028, RQ-PLG-029, RQ-PLG-030, RQ-PLG-031, RQ-PLG-032, RQ-PLG-033
- **ADRs**: ADR-PLG-005, ADR-PLG-002, ADR-PLG-003

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-PLG-032: Feature, decisions and plan
- **Tier**: L
- **Status**: Done
- **Description**: Write FTR-PLG-005, ADR-PLG-005 and this plan.
- **Requirement refs**: RQ-PLG-027, RQ-PLG-028, RQ-PLG-029, RQ-PLG-030, RQ-PLG-031, RQ-PLG-032, RQ-PLG-033
- **ADR refs**: ADR-PLG-005
- **Acceptance Criteria**: Given the owner's approval, Then ADR-PLG-005 is Accepted; Given the index, Then it has no duplicate.
- **Dependencies**: TASK-PLG-047
- **Assignee**: AI
- **Verification**: ADR-PLG-005 Accepted (owner, 2026-11-06); `agnos-index`: 694 entries, exit 0, no duplicate; no `process/` path left in FTR/ADR/PLAN-PLG-005.
- **Assumptions**: DEC-PLG-024, cited by TASK-PLG-035 but absent, written from RQ-PLG-031; `process/` read as `agnos-process/` (RQ-PLG-034).

### TASK-PLG-033: The preparation script
- **Tier**: M
- **Status**: Not Started
- **Description**: Write `scripts/release_prep.py` with `check`, `review` and `set-version`, and its unit tests on temporary git repositories.
- **Requirement refs**: RQ-PLG-027, RQ-PLG-028, RQ-PLG-029, RQ-PLG-032
- **ADR refs**: ADR-PLG-005 (DEC-PLG-022, DEC-PLG-023, DEC-PLG-025)
- **Acceptance Criteria**: Given the criteria of RQ-PLG-027 to RQ-PLG-029, Then they hold, tested first; Given the suite, Then it passes, the skipped tests stated with why.
- **Dependencies**: TASK-PLG-032, TASK-PLG-035
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-PLG-034: The skill's procedure
- **Tier**: M
- **Status**: Not Started
- **Description**: Write the SKILL.md (docs-sync sub-agent, the approval question, `commit-task`, the next steps printed) and its Claude Code pointer, tested for the steps' order and for the release leaving the skill out.
- **Requirement refs**: RQ-PLG-028, RQ-PLG-029, RQ-PLG-030
- **ADR refs**: ADR-PLG-005 (DEC-PLG-022)
- **Acceptance Criteria**: Given the SKILL.md, Then it names the steps in RQ-PLG-030's order And runs none of the publishing ones; Given a rehearsal, Then the skill is left out of the marketplace.
- **Dependencies**: TASK-PLG-033
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-PLG-035: The release reads `VERSION` and reports unreleased entries
- **Tier**: L
- **Status**: Done
- **Description**: Create the init's template `VERSION` at `3.1.0`; make `release.py` read it and refuse it absent or not SemVer 2.0.0, and print and record the unreleased entries in the report and its page.
- **Requirement refs**: RQ-PLG-031, RQ-PLG-032
- **ADR refs**: ADR-PLG-005 (DEC-PLG-024, DEC-PLG-025), ADR-PLG-002
- **Acceptance Criteria**: Given the criteria of RQ-PLG-031 and RQ-PLG-032, Then they hold, tested first; Given the release's suite, Then it passes; Given a rehearsal of HEAD, Then the manifests hold `3.1.0`.
- **Dependencies**: TASK-PLG-032
- **Assignee**: AI
- **Verification**: `test_version.py` (11 tests, RQ-PLG-031/032) written first; release suite on a committed scratch clone with the demo: 130 run, OK, 0 skipped. Rehearsal of that HEAD: exit 0, the manifests and report `version` `3.1.0`, `unreleasedEntries` 81. The clone lacked some `agnos-meta-demo/assets/content` files (Windows path length), Meta layer, not delivered.
- **Assumptions**: The owner's 4.0.0 is chosen at TASK-PLG-036, `VERSION` created at `3.1.0` per DEC-PLG-025; fixture-count tests (`test_console`, `test_select`, `test_inventory`) and RQ-PLG-002's changelog-version tests updated to the behaviour RQ-PLG-032 replaces.

### TASK-PLG-037: `agnos-init` writes the guide and the version into `agnos-process/`
- **Tier**: L
- **Status**: Not Started
- **Description**: Make `init.ps1` and `init.sh` write `agnos-process/AGNOS-GETTING-STARTED.md` and `agnos-process/VERSION` and move a root guide of AGNOS's; update the init's success step, `README.md`, the guide's references and the demo if its checks require it.
- **Requirement refs**: RQ-PLG-033, RQ-PLG-021, RQ-PLG-022
- **ADR refs**: ADR-PLG-005 (DEC-PLG-026), ADR-PLG-003 (DEC-PLG-016)
- **Acceptance Criteria**: Given RQ-PLG-033's criteria, Then they hold, tested first on both scripts; Given the suites of `agnos-init`, `agnos-meta-release`, `agnos-meta-demo` and `agnos-perf-center`, Then they pass.
- **Dependencies**: TASK-PLG-035
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-PLG-036: The preparation run on this repository
- **Tier**: M
- **Status**: Not Started
- **Description**: Run `agnos-meta-release-prep` on `feature/PLG`, the owner reviewing the diff and choosing the version; stop at the printed next steps.
- **Requirement refs**: RQ-PLG-027 to RQ-PLG-030
- **ADR refs**: ADR-PLG-005
- **Acceptance Criteria**: Given the owner's approval, Then the commit holds the synced documents and the version heading; Given the next steps, Then none was run.
- **Dependencies**: TASK-PLG-034, TASK-PLG-035, TASK-PLG-037
- **Assignee**: AI
- **Verification**:
- **Assumptions**:
