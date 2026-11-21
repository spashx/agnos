# PLAN-PLG-013: Version 4.0.0 release

## Overview
Release version 4.0.0: regenerate the demo, then the presentation website from it, then prepare the version, rehearse and
prove the marketplace, and regenerate the marketplace folder from the proved output. The demo, website and marketplace
repositories are committed locally; the merge, tag and push stay with the owner.

## References
- **Requirements**: RQ-DMO-020, RQ-DMO-021, RQ-WEB-001, RQ-WEB-002, RQ-PLG-001, RQ-PLG-002, RQ-PLG-027, RQ-PLG-028, RQ-PLG-029, RQ-PLG-030, RQ-PLG-031, RQ-PLG-032
- **ADRs**: ADR-DMO-001, ADR-WEB-001, ADR-PLG-001, ADR-PLG-005

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-PLG-081: Regenerate demo repository
- **Tier**: S
- **Status**: Done
- **Description**: Rebuild `agnos-lightweight-process.demo` with `agnos-meta-demo build -Verify` from this working tree.
- **Requirement refs**: RQ-DMO-020, RQ-DMO-021
- **ADR refs**: ADR-DMO-001
- **Acceptance Criteria**: Given this working tree, When `build -Verify` runs, Then every demo requirement prints PASS And the exit code is 0.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: None

### TASK-PLG-082: Regenerate presentation website
- **Tier**: S
- **Status**: Done
- **Description**: Build the site with `agnos-meta-website build` from the regenerated demo into `agnos-website`, and commit it there locally.
- **Requirement refs**: RQ-WEB-001, RQ-WEB-002
- **ADR refs**: ADR-WEB-001
- **Acceptance Criteria**: Given the regenerated demo, When the site is built into `agnos-website`, Then the exit code is 0 And only `index.html`, `screens/` and `demo/` change.
- **Dependencies**: TASK-PLG-081
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: None

### TASK-PLG-086: Remove covered plan checkpoint
- **Tier**: S
- **Status**: Done
- **Description**: Delete `CHECKPOINT-PLG-2026-11-06.md`, whose completed and open items are all Done or Accepted, at the owner's request.
- **Requirement refs**: RQ-PLG-027
- **ADR refs**: None
- **Acceptance Criteria**: Given the checkpoint's items, When each is Done or Accepted in the index, Then the file is deleted And the index no longer lists it.
- **Dependencies**: TASK-PLG-081
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: No requirement covers checkpoints; the cleanup is cited under RQ-PLG-027, the check before release preparation.

### TASK-PLG-087: Name repository default branch
- **Tier**: S
- **Status**: Done
- **Description**: In this repository's `AGENTS.md`, a Meta file never delivered, name `dev`, the default branch of AGNOS's development, in place of `main`.
- **Requirement refs**: RQ-DOC-006
- **ADR refs**: None
- **Acceptance Criteria**: Given `AGENTS.md` section 2, Then it names `dev` as the default branch; Given `layers.json`, Then `AGENTS.md` is Meta.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: None

### TASK-PLG-088: Rebuild presentation website
- **Tier**: S
- **Status**: Done
- **Description**: Build the site again with `agnos-meta-website build` into `agnos-website`, its links now read from `assets/links.json`, and commit it there locally.
- **Requirement refs**: RQ-WEB-001, RQ-WEB-002, RQ-WEB-020
- **ADR refs**: ADR-WEB-001
- **Acceptance Criteria**: Given the regenerated demo, When the site is built into `agnos-website`, Then the exit code is 0 And only `index.html`, `screens/` and `demo/` change.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: The commit in `agnos-website` is named `4.0.0: links from links.json`.

### TASK-PLG-083: Prepare version 4.0.0 release
- **Tier**: M
- **Status**: Done
- **Description**: Run `agnos-meta-release-prep` and record version 4.0.0 with the documents docs-sync updates, in one commit.
- **Requirement refs**: RQ-PLG-027, RQ-PLG-028, RQ-PLG-029, RQ-PLG-030, RQ-PLG-032
- **ADR refs**: ADR-PLG-005
- **Acceptance Criteria**: Given the approved diff and version 4.0.0, When `set-version` runs, Then `VERSION.txt` holds 4.0.0 And the changelog's `[Unreleased]` heading becomes `[4.0.0]` And the release-prep suite passes.
- **Dependencies**: TASK-PLG-082
- **Assignee**: AI
- **Verification**: `release_prep.py check`: passed (open: TASK-PLG-083 to 085); docs-sync: no edit; `review`: `current: 3.6.2`, `proposed: 3.7.0`, 4.0.0 approved by the owner; `set-version 4.0.0`: exit 0, `VERSION.txt` reads 4.0.0, the first changelog heading reads `## [4.0.0]`; release-prep suite: Ran 25 tests, OK, 0 skipped.
- **Assumptions**: The owner removed the TASK-INI-020 line of `[3.6.2]` with the requirement it implemented; `[4.0.0]` adds TASK-DOC-006, TASK-DOC-007 and the demo fix, at the owner's request.

### TASK-PLG-089: Assign links file to meta layer
- **Tier**: S
- **Status**: Done
- **Description**: Add `assets/links.json`, read only by maintainer skills, to the Meta layer of `layers.json`, which the comment already announced; the changelog's entry no longer names that file.
- **Requirement refs**: RQ-MTA-008, RQ-DOC-007
- **ADR refs**: ADR-MTA-002 (DEC-MTA-008)
- **Acceptance Criteria**: Given the commit of this task, When the rehearsal runs, Then it passes the layer check.
- **Dependencies**: TASK-PLG-083
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: None

### TASK-PLG-090: Parse validator provides section
- **Tier**: S
- **Status**: Done
- **Description**: In `plugin_proof.py`, end a block of the strict validation's output at any unindented line, so that the `Provides:` list of Claude Code 2.1.327 is not read as warnings; a test reproduces that output.
- **Requirement refs**: RQ-PLG-010, RQ-PLG-046
- **ADR refs**: ADR-PLG-009 (DEC-PLG-037)
- **Acceptance Criteria**: Given the logo warning followed by a `Provides:` list, When the validation is judged, Then it passes.
- **Dependencies**: TASK-PLG-089
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: None

### TASK-PLG-084: Rehearse marketplace release
- **Tier**: S
- **Status**: Done
- **Description**: Rehearse the release of the version commit with `agnos-meta-release --dry-run` into an empty folder outside the repository, then prove it with `agnos-meta-plugin-proof`.
- **Requirement refs**: RQ-PLG-001, RQ-PLG-002, RQ-PLG-031, RQ-PLG-032
- **ADR refs**: ADR-PLG-001
- **Acceptance Criteria**: Given the version commit, When the rehearsal and the proof run, Then both end with exit 0 And the manifests hold version 4.0.0.
- **Dependencies**: TASK-PLG-083
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: None

### TASK-PLG-085: Regenerate marketplace folder
- **Tier**: S
- **Status**: Done
- **Description**: Replace the content of `agnos-marketplace`, `.git` excepted, by the proved output, and commit it there locally as `4.0.0`.
- **Requirement refs**: RQ-PLG-001, RQ-PLG-032
- **ADR refs**: ADR-PLG-001
- **Acceptance Criteria**: Given the proved output, When it replaces the marketplace content, Then the folder equals the output And its catalogue holds version 4.0.0.
- **Dependencies**: TASK-PLG-084
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: None

### TASK-PLG-091: Remove release plan checkpoint
- **Tier**: S
- **Status**: Done
- **Description**: Delete `CHECKPOINT-PLG-2026-11-18.md`, whose open items are all Done, at the owner's request.
- **Requirement refs**: RQ-PLG-027
- **ADR refs**: None
- **Acceptance Criteria**: Given the checkpoint's items, When each is Done in the index or confirmed by the owner, Then the file is deleted And the index no longer lists it.
- **Dependencies**: TASK-PLG-085
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: The website rebuild, not a task, is confirmed done by the owner; cited under RQ-PLG-027, as TASK-PLG-086.
