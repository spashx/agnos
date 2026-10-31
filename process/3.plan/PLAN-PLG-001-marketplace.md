# PLAN-PLG-001: AGNOS Marketplace

## Overview
Build the marketplace of FTR-PLG-001 locally and prove it by a real install. No push at any step. The order follows the risks: the wording
and the systems first, then the output, then the install.

## References
- **Requirements**: RQ-PLG-001 to RQ-PLG-009
- **ADRs**: ADR-PLG-001, ADR-MTA-001, ADR-MTA-002, ADR-INI-001

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-PLG-001: Feature, decisions and plan
- **Tier**: L
- **Status**: Done
- **Description**: Record the trial's results and the decisions, and mark what they amend in ADR-MTA-001 and ADR-INI-001.
- **Requirement refs**: RQ-PLG-001 to RQ-PLG-009
- **ADR refs**: ADR-PLG-001
- **Acceptance Criteria**: Given the owner's approval, Then ADR-PLG-001 is Accepted, And DEC-MTA-004, DEC-MTA-005, DEC-INI-003, DEC-INI-004 and DEC-INI-005 name what amends them; Given the index, Then it has no duplicate.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: ADR-PLG-001 Accepted; the five DECs each name what amends them (re-read in the edits); `agnos-index` on commit reports no duplicate.
- **Assumptions**: the trial's results stand for Copilot in VS Code until TASK-PLG-007.

### TASK-PLG-002: Skills name their files from their own folder
- **Tier**: L
- **Status**: Done
- **Description**: Rewrite the delivered `SKILL.md` files and the tests that read them, with no `.github/skills/` path and no plugin variable.
- **Requirement refs**: RQ-PLG-005
- **ADR refs**: ADR-PLG-001
- **Acceptance Criteria**: Given the delivered `SKILL.md` files, Then none holds `.github/skills/` or `CLAUDE_`; Given a project and a skill's script called from the project's root, Then its output lands in the project; Given the full suite, Then it passes.
- **Dependencies**: TASK-PLG-001
- **Assignee**: AI
- **Verification**: `test_skill_paths.py`: 2 wording tests failing before the rewrite, 4 OK after, the index and the perf center copied away write in the project only. Suites: meta-release 46, init 16, meta-demo 12, docs-sync 16, perf-center 364 OK (3 skipped), `test-build-index.ps1` all passed. Found and fixed on the way: with WSL running, `bash` on Windows is WSL's, which could not read the path given by `parse_error` in `release.py`; it now gets the bytes on its input (one first fix sent CRLF in text mode, seen in the test's output).
- **Assumptions**: agnos-init's own scripts and templates stay in `LEFT_TO_THE_BLOCK_TASK` until TASK-PLG-004.

### TASK-PLG-003: Delivered scripts on Linux
- **Tier**: M
- **Status**: Not Started
- **Description**: Run the delivered suites on Ubuntu 24.04 under WSL and fix what fails, including `python3` where only that name exists.
- **Requirement refs**: RQ-PLG-008
- **ADR refs**: ADR-PLG-001
- **Acceptance Criteria**: Given WSL, When the delivered suites run on a copy of the repository, Then they pass with the Windows results unchanged.
- **Dependencies**: TASK-PLG-002
- **Assignee**: AI
- **Verification**: Not run yet.
- **Assumptions**: None

### TASK-PLG-004: The block with no path
- **Tier**: L
- **Status**: Done
- **Description**: `agnos-init` writes the block naming `agnos-process`, with no toolkit input; its requirements are amended, its two scripts and `agnos-meta-demo` follow, and the demo is rebuilt.
- **Requirement refs**: RQ-PLG-004, RQ-INI-001, RQ-INI-006, RQ-INI-008
- **ADR refs**: ADR-PLG-001, ADR-INI-001
- **Acceptance Criteria**: Given RQ-PLG-004's criteria, Then they hold on both scripts; Given the rebuilt demo, Then its checks pass.
- **Dependencies**: TASK-PLG-002
- **Assignee**: AI
- **Verification**: `test_init.py`: 20 failures and errors before the change, 16 OK after, on both scripts; meta-release 45, meta-demo 12, docs-sync 16 OK. Demo rebuilt by a background Haiku subagent: `verify` 23 passed, 0 failed, HEAD `36f221f`; its `CLAUDE.md` re-read: names `agnos-process`, holds no path; its tree is clean.
- **Assumptions**: the block adds one line the trial did not run: if the skill is not available, stop and tell the user to install the plugin. The scenario's `init` becomes `true`.

### TASK-PLG-005: The marketplace target
- **Tier**: L
- **Status**: Not Started
- **Description**: `agnos-meta-release` gains the target: tree, four manifests, generated `agnos-process`, the existing removal and proof applied to the output, `claude plugin validate --strict` when the binary is present.
- **Requirement refs**: RQ-PLG-001, RQ-PLG-002, RQ-PLG-003, RQ-PLG-007
- **ADR refs**: ADR-PLG-001, ADR-MTA-002
- **Acceptance Criteria**: Given RQ-PLG-001, RQ-PLG-002, RQ-PLG-003 and RQ-PLG-007's criteria, Then they hold on a real run from HEAD; Given the mentions in the report (`agnos-meta-` in delivered files), Then each is removed or read and kept.
- **Dependencies**: TASK-PLG-004
- **Assignee**: AI
- **Verification**: Not run yet.
- **Assumptions**: the plugin is named `agnos` and the marketplace `agnos-marketplace`; version from `CHANGELOG.md`'s latest release.

### TASK-PLG-006: Agents generated per tool
- **Tier**: M
- **Status**: Not Started
- **Description**: The target generates each delivered agent for Claude Code and Copilot from a table of frontmatter values, proved on a test agent.
- **Requirement refs**: RQ-PLG-006
- **ADR refs**: ADR-PLG-001
- **Acceptance Criteria**: Given RQ-PLG-006's criteria, Then they hold, And the test agent is run once from an install in each tool.
- **Dependencies**: TASK-PLG-005
- **Assignee**: AI
- **Verification**: Not run yet.
- **Assumptions**: None

### TASK-PLG-007: Install proof and user documents
- **Tier**: M
- **Status**: Not Started
- **Description**: Install from a clean clone in Claude Code, Copilot CLI and VS Code, run a session up to its first commit, and write the install commands and the tested / not tested table in `README.md` and `GETTING_STARTED.MD`.
- **Requirement refs**: RQ-PLG-008, RQ-PLG-009
- **ADR refs**: ADR-PLG-001
- **Acceptance Criteria**: Given RQ-PLG-009's criteria, Then they hold in each tool on Windows; Given the README, Then every cell of the table states a result actually observed; Given the release, Then the final report's checks are true.
- **Dependencies**: TASK-PLG-006, TASK-PLG-003
- **Assignee**: Human (sessions), AI (the rest)
- **Verification**: Not run yet.
- **Assumptions**: a Linux run of a tool needs Claude Code or Copilot installed in WSL by the owner; without it the table states scripts tested, tool not run.
