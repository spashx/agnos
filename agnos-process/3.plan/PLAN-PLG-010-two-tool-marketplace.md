# PLAN-PLG-010: Two-tool marketplace with plugin README

## Overview
Withdraw OpenAI Codex from what the release delivers, and deliver a README in the plugin's folder, which VS Code shows.

## References
- **Requirements**: RQ-PLG-042, RQ-PLG-043
- **ADRs**: ADR-PLG-008

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-PLG-065: Record two-tool marketplace decisions
- **Tier**: L
- **Status**: Done
- **Description**: Write FTR-PLG-008, ADR-PLG-008 and this plan from the owner's choices of 2026-11-15.
- **Requirement refs**: RQ-PLG-042, RQ-PLG-043
- **ADR refs**: ADR-PLG-008
- **Acceptance Criteria**: Given the index, When it is rebuilt, Then RQ-PLG-042, RQ-PLG-043, DEC-PLG-033, DEC-PLG-034 and TASK-PLG-065 to TASK-PLG-069 are listed with no duplicate.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `agnos-index`: exit 0, 920 entries; RQ-PLG-042, RQ-PLG-043, DEC-PLG-033, DEC-PLG-034, TASK-PLG-065 to 069 listed, no duplicate.
- **Assumptions**: None

### TASK-PLG-066: Remove Codex catalogue from release
- **Tier**: L
- **Status**: Done
- **Description**: Remove `.agents/plugins/marketplace.json` and the `codex` values from `agnos-meta-release`, its skill and its tests, test first.
- **Requirement refs**: RQ-PLG-043
- **ADR refs**: ADR-PLG-008 (DEC-PLG-033)
- **Acceptance Criteria**: Given a release, When the marketplace is written, Then `.agents/plugins/marketplace.json` is absent And `assets/marketplace.json` holds no `codex` key And the release's tests pass.
- **Dependencies**: TASK-PLG-065
- **Assignee**: AI
- **Verification**: New RQ-PLG-043 test failed first (2 failures), then passed. Full release suite: 134 run, 132 OK, 2 failed in `test_console` (file count one lower, the Codex catalogue gone); expected counts corrected to 9 and 10, `test_console` 5 OK; 0 skipped. No "codex" left in the release's scripts, assets or SKILL.md.
- **Assumptions**: The missing-folder manifest test now edits the Claude catalogue's source.

### TASK-PLG-067: Deliver plugin folder README
- **Tier**: M
- **Status**: Not Started
- **Description**: Add `assets/plugin-README.md`, copied by the release to `plugins/agnos/README.md`, and a check that its relative links lead to files of the plugin, test first.
- **Requirement refs**: RQ-PLG-042
- **ADR refs**: ADR-PLG-008 (DEC-PLG-034)
- **Acceptance Criteria**: Given a release, Then `plugins/agnos/README.md` exists; Given a README link to an absent file, When the release checks it, Then a problem names the link.
- **Dependencies**: TASK-PLG-066
- **Assignee**: AI
- **Verification**: Filled at closure.
- **Assumptions**: None

### TASK-PLG-068: Remove Codex from delivered documents
- **Tier**: M
- **Status**: Not Started
- **Description**: Remove Codex from `README.md`, `COMPATIBILITY.md` and `CHANGELOG.md`, past entries included, and add the change to the changelog's Unreleased section.
- **Requirement refs**: RQ-PLG-043
- **ADR refs**: ADR-PLG-008 (DEC-PLG-033)
- **Acceptance Criteria**: Given the three documents, When searched for "codex" ignoring case, Then none is found.
- **Dependencies**: TASK-PLG-066
- **Assignee**: AI
- **Verification**: Filled at closure.
- **Assumptions**: None

### TASK-PLG-069: Rehearse two-tool marketplace release
- **Tier**: M
- **Status**: Not Started
- **Description**: Run `agnos-meta-release` on the session's last commit and search its output for Codex.
- **Requirement refs**: RQ-PLG-042, RQ-PLG-043
- **ADR refs**: ADR-PLG-008
- **Acceptance Criteria**: Given the release output, Then its checks pass And "codex" is found only in `agnos-perf-center`'s author patterns And `plugins/agnos/README.md` exists.
- **Dependencies**: TASK-PLG-067, TASK-PLG-068
- **Assignee**: AI
- **Verification**: Filled at closure.
- **Assumptions**: None
