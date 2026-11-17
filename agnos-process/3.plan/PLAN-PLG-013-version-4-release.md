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
- **Status**: Not Started
- **Description**: Build the site with `agnos-meta-website build` from the regenerated demo into `agnos-website`, and commit it there locally.
- **Requirement refs**: RQ-WEB-001, RQ-WEB-002
- **ADR refs**: ADR-WEB-001
- **Acceptance Criteria**: Given the regenerated demo, When the site is built into `agnos-website`, Then the exit code is 0 And only `index.html`, `screens/` and `demo/` change.
- **Dependencies**: TASK-PLG-081
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: None

### TASK-PLG-083: Prepare version 4.0.0 release
- **Tier**: M
- **Status**: Not Started
- **Description**: Run `agnos-meta-release-prep` and record version 4.0.0 with the documents docs-sync updates, in one commit.
- **Requirement refs**: RQ-PLG-027, RQ-PLG-028, RQ-PLG-029, RQ-PLG-030, RQ-PLG-032
- **ADR refs**: ADR-PLG-005
- **Acceptance Criteria**: Given the approved diff and version 4.0.0, When `set-version` runs, Then `VERSION.txt` holds 4.0.0 And the changelog's `[Unreleased]` heading becomes `[4.0.0]` And the release-prep suite passes.
- **Dependencies**: TASK-PLG-082
- **Assignee**: AI
- **Verification**: Not yet run
- **Assumptions**: None

### TASK-PLG-084: Rehearse marketplace release
- **Tier**: S
- **Status**: Not Started
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
- **Status**: Not Started
- **Description**: Replace the content of `agnos-marketplace`, `.git` excepted, by the proved output, and commit it there locally as `4.0.0`.
- **Requirement refs**: RQ-PLG-001, RQ-PLG-032
- **ADR refs**: ADR-PLG-001
- **Acceptance Criteria**: Given the proved output, When it replaces the marketplace content, Then the folder equals the output And its catalogue holds version 4.0.0.
- **Dependencies**: TASK-PLG-084
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: None
