# PLAN-INI-003: Session State Written by a Script

## Overview
Create the `agnos-session` skill, have the instructions call it, have `agnos-init` keep `session.yaml` out of git, untrack this
repository's copy, align the demo, then sync the documents. Order: TASK-INI-006, 007, 008, 011, 009, 010. The major release is
prepared afterwards with `agnos-meta-release-prep`, outside this plan. Everything stays local.

## References
- **Requirements**: RQ-INI-011 to RQ-INI-018; amended: RQ-DMO-006
- **ADRs**: ADR-INI-002 (DEC-INI-008 to DEC-INI-013)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-INI-006: The `agnos-session` skill
- **Tier**: L
- **Status**: Done
- **Description**: Write the Python tests first, driving both scripts on the same cases on the model of `agnos-init`'s
  `test_init.py`, then `SKILL.md`, `session.ps1` and `session.sh`; add `agnos-session` to `COPIES` of the layout generator and
  generate its copies; add the `.claude/skills/agnos-session` pointer, the tool mapping of `CLAUDE.md` and the skill table of `AGENTS.md`.
- **Requirement refs**: RQ-INI-011, RQ-INI-012, RQ-INI-013, RQ-INI-014, RQ-INI-015, RQ-INI-018
- **ADR refs**: ADR-INI-002 (DEC-INI-008, DEC-INI-009, DEC-INI-010, DEC-INI-011)
- **Acceptance Criteria**: Given the new suite, When it runs before the scripts exist, Then its tests fail; Given the scripts, When it
  runs, Then the criteria of RQ-INI-011 to RQ-INI-015 and RQ-INI-018 hold for both versions; Given `layout.py --check`, Then it exits 0.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `agnos-session/tests` before the scripts: 16 run, failures=37, errors=5; after: 16 OK, 0 skipped, PowerShell 5.1
  and Git Bash `sh` both run on Windows. Linux, macOS (fake `uname`) and PowerShell 7 (preset `IsLinux`/`IsMacOS`) are simulated
  only: no real run on Linux or macOS. `layout.py --write` then `--check`: 0 findings, exit 0. Other suites, on a copy: `agnos-init` 32 OK,
  `agnos-meta-demo` 12 OK, `agnos-meta-docs-sync` 18 OK, `agnos-meta-plugin-proof` 16 OK, `agnos-meta-qa` 32 OK (6 skipped, reasons
  not read), `agnos-meta-release` 133 OK (2 skipped, reasons not read), `agnos-meta-release-prep` 25 OK, `agnos-self-improvement` 9 OK;
  `agnos-perf-center` 408 run, failures=36, errors=168, 3 skipped (performance): its headless-browser tests fail alike on a clean
  worktree of HEAD 7791c9e (`test_brand.py`: failures=5, errors=14), so not caused by this task, and not fixed here.
- **Assumptions**: the paths come from layout copies generated for the skill (`COPIES`); `session.yaml` in LF, UTF-8 without BOM;
  the appended row takes the line ending of the log's first line, a created log is LF; the row's date is the local date; the trigram
  pattern is the skill's own, as decided by the owner.

### TASK-INI-007: The instructions call the skill
- **Tier**: L
- **Status**: Done
- **Description**: In the instructions file, START SESSION step 3 asks about tests then calls `init` and shows its table, 3.e reloads
  with `show`, END SESSION step 2 calls `close`; the folder structure says `session.yaml` is not version-controlled; the schema, the
  variables table and the Testing section use `tests`; the rule "never rename or remove existing keys" is removed.
- **Requirement refs**: RQ-INI-017, RQ-PLG-019
- **ADR refs**: ADR-INI-002 (DEC-INI-009, DEC-INI-011, DEC-INI-013)
- **Acceptance Criteria**: Given the edited file, When it is searched, Then `unit_tests` appears nowhere, And `init`, `show` and `close`
  are each named; Given its line count, Then it is at most 400, reported here.
- **Dependencies**: TASK-INI-006
- **Assignee**: AI
- **Verification**: `wc -l`: 380 lines, within 400. `grep -c unit_tests`: 0. Sub-commands named: `init` 2, `show` 3, `close` 1.
  `layout.py --check`: 0 findings. Suites: `agnos-meta-docs-sync` 18 OK, `agnos-self-improvement` 9 OK, `agnos-init` 32 OK,
  `agnos-session` 16 OK; on a copy, `agnos-meta-release` 133 OK (2 skipped: the demo is not built), `agnos-meta-release-prep` 25 OK,
  `agnos-meta-plugin-proof` 16 OK, `agnos-meta-qa` 32 OK (6 skipped: pinned analysers not installed), `agnos-meta-demo` 12 OK.
  `agnos-perf-center` not re-run: its headless-browser failures are tracked by TASK-TRC-106.
- **Assumptions**: the trigram is asked at step 3 with the tests question, since `init` needs it, and step 8 reuses it (proposed
  as 6.2.4, the owner said to continue); the reads of `session.yaml` in other skills' `SKILL.md` stay, as reading is not writing.

### TASK-INI-008: `agnos-init` keeps `session.yaml` out of git
- **Tier**: M
- **Status**: Not Started
- **Description**: Tests first in `test_init.py`, then both `init.ps1` and `init.sh` add the path to the target's `.gitignore` only
  when `git check-ignore` says it is not ignored, or by line comparison outside a git repository, and report it.
- **Requirement refs**: RQ-INI-016, RQ-INI-003
- **ADR refs**: ADR-INI-002 (DEC-INI-012)
- **Acceptance Criteria**: Given the suite, When it runs both scripts, Then the criteria of RQ-INI-016 hold, And the former tests of
  `agnos-init` still pass.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-INI-011: This repository untracks its `session.yaml`
- **Tier**: S
- **Status**: Not Started
- **Description**: Add the path to this repository's `.gitignore` and run `git rm --cached agnos-process/_sessionstate/session.yaml`;
  the file stays on disk.
- **Requirement refs**: RQ-INI-016
- **ADR refs**: ADR-INI-002 (DEC-INI-012)
- **Acceptance Criteria**: Given the commit, When `git ls-files` lists `agnos-process/_sessionstate/`, Then `session.yaml` is absent,
  And `git check-ignore` confirms it is ignored, And the file is still on disk.
- **Dependencies**: TASK-INI-008
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**:

### TASK-INI-009: The demo without a committed session state
- **Tier**: M
- **Status**: Not Started
- **Description**: Keep the change of `agnos-meta-demo/scripts/verify.ps1` that drops `session.yaml` from the RQ-DMO-006 check, remove
  "a session state file" from the Statement of RQ-DMO-006, remove `session.yaml` from the demo's content, then rebuild and verify the demo.
- **Requirement refs**: RQ-DMO-006, RQ-INI-016
- **ADR refs**: ADR-INI-002 (DEC-INI-012)
- **Acceptance Criteria**: Given the rebuilt demo, When `agnos-meta-demo build -Verify` runs, Then every check passes, And no commit of
  the demo holds `session.yaml`; Given `agnos-meta-demo/tests`, Then they pass.
- **Dependencies**: TASK-INI-008, TASK-INI-011
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-INI-010: The documents follow
- **Tier**: M
- **Status**: Not Started
- **Description**: Run `agnos-meta-docs-sync` for `AGNOS-GETTING-STARTED.md`, `AGENTS.md`, `CLAUDE.md` and the changelog, its breaking
  entries saying that `unit_tests` becomes `tests` and that a project untracks `session.yaml` itself; update the `_sessionstate`
  readme template of `agnos-init`.
- **Requirement refs**: RQ-INI-016, RQ-INI-017
- **ADR refs**: ADR-INI-002 (DEC-INI-012, DEC-INI-013)
- **Acceptance Criteria**: Given the documents, When they are searched, Then `unit_tests` and "version-controlled" next to
  `session.yaml` appear nowhere, And the changelog has the two breaking entries; Given `agnos-meta-docs-sync`'s and `agnos-init`'s tests, Then they pass.
- **Dependencies**: TASK-INI-006, TASK-INI-007, TASK-INI-008, TASK-INI-009
- **Assignee**: AI
- **Verification**:
- **Assumptions**:
