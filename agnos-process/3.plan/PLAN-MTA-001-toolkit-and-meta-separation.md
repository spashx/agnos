# PLAN-MTA-001: The Prefix and the Layers

## Overview
First step of ADR-MTA-001: rename the two meta skills and make the prefix the only criterion, in one commit since the demo's
exclusions depend on both, then state the layers. Everything stays on the local branch `feature/TRC`: nothing is pushed. The release
build is the next plan.

## References
- **Requirement refs**: RQ-MTA-001 to RQ-MTA-005; amended: RQ-DMO-002, RQ-DMO-020
- **ADR refs**: ADR-MTA-001 (DEC-MTA-002, DEC-MTA-003, DEC-MTA-006); amended: DEC-DMO-006

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
- **Status**: Done
- **Description**: Add the three layers and the prefix rule to `CONTRIBUTING.md`, correct its line budget from 800 to 400, and add one `CHANGELOG.md` bullet under `[Unreleased]` for the renaming.
- **Requirement refs**: RQ-MTA-004
- **ADR refs**: ADR-MTA-001 (DEC-MTA-002)
- **Acceptance Criteria**: Given `CONTRIBUTING.md`, Then the criterion of RQ-MTA-004 holds.
- **Dependencies**: TASK-MTA-001
- **Assignee**: AI
- **Verification**: `CONTRIBUTING.md` re-read: three layers (lines 29-31), prefix rule (33), 400 lines (44). `git diff --quiet` on `.github/instructions`: unchanged, 382 lines. Demo rebuilt with the new files, HEAD 4323b56: 22 passed, 0 failed. For TASK-MTA-001 after commit 6ff3495: `git log --follow` reaches earlier history (3, 2 and 2 commits on the renamed files).
- **Assumptions**: this task's plan text changed the tier from S to M before approval, since the edits exceed 5 lines; no unit test for documentation text, as `agnos-index` and `agnos-trace` suites were last run on TASK-MTA-001 and no code changed since.

### TASK-MTA-003: The demo without the toolkit
- **Tier**: L
- **Status**: Done
- **Description**: Amend RQ-DMO-002 and RQ-DMO-020. Write the checks first: invert the RQ-DMO-002 check in `verify.ps1` so that no toolkit file may be present, and test it. Replace the baseline step of the scenario with a project start that commits the demo's own `.gitignore` and `.gitattributes` from `assets/content/`, make `replay.ps1` and `verify.ps1` run `agnos-index` from `-Toolkit`, correct the toolkit paths in the demo's README and draft, and rebuild.
- **Requirement refs**: RQ-MTA-005, RQ-DMO-002, RQ-DMO-020
- **ADR refs**: ADR-MTA-001 (DEC-MTA-006), ADR-DMO-001 (DEC-DMO-006)
- **Acceptance Criteria**: Given the rebuilt demo, Then each criterion of RQ-MTA-005 holds, at HEAD and in every commit of its history; Given a change to a toolkit file, When the demo is rebuilt, Then `verify` still runs that toolkit's `agnos-index` and `agnos-trace` on it.
- **Dependencies**: TASK-MTA-001
- **Assignee**: AI
- **Verification**: `test_meta_prefix.py`: 5 OK, 3 of them failing before the code. `build -Verify`: HEAD 6c848f1, 22 passed, 0 failed; RQ-DMO-002 reads 0 toolkit file in the history and 0 toolkit ID in the tree; RQ-DMO-007 and RQ-DMO-008 pass from this repository's scripts, the demo having none; `git ls-files`: 95 files, none of AGNOS. Suites: `agnos-meta-docs-sync` 14 OK, `agnos-trace` 356 OK (3 skipped), `agnos-index` all passed.
- **Assumptions**: two tests of `baselineExclude` and `MAINTAINER_PATTERN` were replaced, since both went with the toolkit, and RQ-MTA-002 now holds in the docs-sync report only; the demo's `.gitignore` and `.gitattributes` are stored as `project/*.txt` so they do not apply in this repository; the check of toolkit IDs now covers the demo's whole tree, wider than the former `process/`; the README says the plugin is not available yet.
