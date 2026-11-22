# PLAN-INI-004: Unified context-aware entry-point block

## Overview
Write one block for `CLAUDE.md` and `AGENTS.md`, explain in its comments how Claude Code and GitHub Copilot keep the process in context,
and explain the risks in the README. Order: TASK-INI-013, 014, 015, 016, 017, 018: the user's guide, then the demo rebuild.
Everything stays local, on `feature/PLG`.

## References
- **Requirement refs**: RQ-INI-019, RQ-INI-020, RQ-INI-021
- **ADR refs**: ADR-INI-003 (DEC-INI-014, DEC-INI-015)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-INI-013: Record block unification artifacts
- **Tier**: M
- **Status**: Done
- **Description**: Add RQ-INI-019 to RQ-INI-021 to FTR-INI-001, write ADR-INI-003 and this plan.
- **Requirement refs**: RQ-INI-019, RQ-INI-020, RQ-INI-021
- **ADR refs**: ADR-INI-003
- **Acceptance Criteria**: Given the artifacts, When `agnos-index` runs, Then it exits 0 And lists the new IDs.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `agnos-index`: exit 0, 905 entries, lists RQ-INI-019 to RQ-INI-021, ADR-INI-003, DEC-INI-014, DEC-INI-015,
  PLAN-INI-004, TASK-INI-013 to TASK-INI-016; DEC-INI-003 marked amended in ADR-INI-001.
- **Assumptions**: the artifacts take the trigram INI, their functional area, on the PLG session branch.

### TASK-INI-014: Merge block templates
- **Tier**: L
- **Status**: Done
- **Description**: Write the tests first, then replace `CLAUDE.block.md` and `AGENTS.block.md` by `agnos.block.md`, read by `init.ps1` and
  `init.sh`, with one question line for both tools.
- **Requirement refs**: RQ-INI-019
- **ADR refs**: ADR-INI-003 (DEC-INI-014)
- **Acceptance Criteria**: Given the new tests, When they run before the change, Then they fail; Given the change, When `agnos-init`'s
  suite runs, Then both blocks are byte-identical in both script versions, And every former test passes.
- **Dependencies**: TASK-INI-013
- **Assignee**: AI
- **Verification**: 2 new RQ-INI-019 tests before the change: 2 run, failures=2 (blocks differ; `AGENTS.block.md`, `CLAUDE.block.md`
  listed); after: `agnos-init` suite 40 run, OK, 0 skipped, PowerShell 5.1 and Git Bash both run on Windows.
- **Assumptions**: `CLAUDE.block.md` renamed with `git mv` so its history follows; the question line reuses the instructions file's wording.

### TASK-INI-015: Add context behaviour comments
- **Tier**: M
- **Status**: Done
- **Description**: Write the tests first, then add to the block its HTML comments on Claude Code and GitHub Copilot, and the visible
  order to invoke the process skill again after a compaction.
- **Requirement refs**: RQ-INI-020
- **ADR refs**: ADR-INI-003 (DEC-INI-015)
- **Acceptance Criteria**: Given the new tests, When they run before the change, Then they fail; Given the change, Then the comments
  name both tools, session start, clear and compaction, And the block holds no artifact ID.
- **Dependencies**: TASK-INI-014
- **Assignee**: AI
- **Verification**: 2 new RQ-INI-020 tests before the change: 2 run, failures=2; after: `agnos-init` 42 run, OK, 0 skipped (PowerShell
  5.1 and Git Bash); `agnos-session` 17 OK, `agnos-self-improvement` 9 OK, `agnos-meta-release` 133 OK, skips not reported by the run;
  the RQ-INI-006 test confirms no artifact ID in the block. Other suites not run.
- **Assumptions**: the facts come from code.claude.com/docs (memory, skills) and code.visualstudio.com/docs (custom instructions, agent
  skills), read on 2026-11-14; the instructions skill measured at about 7,000 tokens (28,257 characters / 4).

### TASK-INI-016: Document context-loss risks
- **Tier**: M
- **Status**: Done
- **Description**: Add to `README.md` a section on what happens to the process after a clear, an automatic and a manual compaction,
  for Claude Code and GitHub Copilot, with the risks and the action to take.
- **Requirement refs**: RQ-INI-021
- **ADR refs**: ADR-INI-003
- **Acceptance Criteria**: Given `README.md`, Then the section names both tools, clear, automatic and manual compaction, their risks
  and the action to take, And states what the documentation leaves unsaid.
- **Dependencies**: TASK-INI-015
- **Assignee**: AI
- **Verification**: README re-read: the subsection names both tools, new conversation, clear, automatic and manual compaction, 3 risks,
  4 actions, and marks 2 behaviours as undocumented. First run: `agnos-meta-release` 133 run, failures=1 (RQ-PLG-023 test fixes the
  `##` sections); fix: a `###` subsection under Getting Started; re-run 133 OK. `agnos-init` 42 OK, `agnos-meta-release-prep` 25 OK,
  `agnos-meta-docs-sync` 18 OK, `agnos-meta-demo` 18 OK, `agnos-git-workflow` 8 OK; skips not reported by the runs; other suites not run.
- **Assumptions**: a subsection rather than a new `##` section, so RQ-PLG-023's list of sections stays as it is.

### TASK-INI-017: Update guide on context loss
- **Tier**: M
- **Status**: Done
- **Description**: Amend RQ-INI-021 to cover the user's guide, then state in `AGNOS-GETTING-STARTED.md` the shared block, one session
  per conversation, the re-invocation after a compaction, and the matching mistake.
- **Requirement refs**: RQ-INI-021
- **ADR refs**: ADR-INI-003
- **Acceptance Criteria**: Given the guide, Then it no longer says one conversation may hold several sessions, And it orders the
  re-invocation after a compaction; Given the suites reading the guide, When they run, Then they pass.
- **Dependencies**: TASK-INI-016
- **Assignee**: AI
- **Verification**: guide re-read: lines on the shared block, one session per conversation, "Keep the process loaded", and a new row in
  "Mistakes that cost the most"; `agnos-init` 42 OK, `agnos-meta-docs-sync` 18 OK, `agnos-meta-release-prep` 25 OK, skips not reported.
- **Assumptions**: the guide points to the plugin's README for the details rather than repeating its table.

### TASK-INI-018: Rebuild demo on unified block
- **Tier**: M
- **Status**: Done
- **Description**: Run `agnos-meta-demo build -Verify`, so that the demo's `CLAUDE.md`, `AGENTS.md` and guide come from the new templates.
- **Requirement refs**: RQ-INI-008, RQ-INI-019, RQ-INI-020
- **ADR refs**: ADR-INI-003
- **Acceptance Criteria**: Given the rebuilt demo, When `verify` runs, Then every requirement prints PASS.
- **Dependencies**: TASK-INI-017
- **Assignee**: AI
- **Verification**: `build -Verify` (Sonnet subagent): exit 0, 88 commits, `verify: 27 passed, 0 failed`, nothing skipped, RQ-INI-008
  PASS (block alone 2 of 2, 0 changes after a new call). Re-checked here: demo HEAD f85c790, `CLAUDE.md` and `AGENTS.md` identical and
  holding the re-invocation order, demo working tree clean.
- **Assumptions**: no change to the demo's scenario or content was needed.

### TASK-INI-019: Align guide tier table
- **Tier**: S
- **Status**: Done
- **Description**: Set the Tier S written plan to No in the guide's tier table, and say a Tier S task may still be listed in a plan.
- **Requirement refs**: RQ-PLG-022
- **ADR refs**: None
- **Acceptance Criteria**: Given the guide, Then its tier table matches TASK TIERS of the instructions.
- **Dependencies**: None
- **Assignee**: Human
- **Verification**: N/A (Tier S)
- **Assumptions**: None
