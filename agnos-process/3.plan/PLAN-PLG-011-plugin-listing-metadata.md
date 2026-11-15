# PLAN-PLG-011: Plugin listing metadata and logo

## Overview
Deliver the catalogue's metadata block, the plugin's listing fields and its logo, then prove the install in both tools.

## References
- **Requirements**: RQ-PLG-044, RQ-PLG-045, RQ-PLG-046
- **ADRs**: ADR-PLG-009

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-PLG-071: Record listing metadata decisions
- **Tier**: L
- **Status**: Done
- **Description**: Write FTR-PLG-009, ADR-PLG-009 and this plan from the owner's choices of 2026-11-15.
- **Requirement refs**: RQ-PLG-044, RQ-PLG-045, RQ-PLG-046
- **ADR refs**: ADR-PLG-009
- **Acceptance Criteria**: Given the index, When it is rebuilt, Then RQ-PLG-044 to RQ-PLG-046, DEC-PLG-035, DEC-PLG-036 and TASK-PLG-071 to TASK-PLG-074 are listed with no duplicate.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `agnos-index`: exit 0, 933 entries; RQ-PLG-044 to 046, DEC-PLG-035, DEC-PLG-036, TASK-PLG-071 to 074 listed, no duplicate.
- **Assumptions**: None

### TASK-PLG-072: Write catalogue and manifest metadata
- **Tier**: L
- **Status**: Not Started
- **Description**: Add the listing fields to `assets/marketplace.json`, write them and `metadata` from `write_marketplace`, and check `metadata.version` in `manifest_problems`, test first.
- **Requirement refs**: RQ-PLG-044, RQ-PLG-045
- **ADR refs**: ADR-PLG-009
- **Acceptance Criteria**: Given a release, When the marketplace is written, Then the catalogue holds `metadata.version` equal to `VERSION.txt` and no root `description` And both manifests and the plugin entry hold `homepage`, `repository` and `author.url`; Given a catalogue whose `metadata.version` differs, When it is checked, Then a problem is reported.
- **Dependencies**: TASK-PLG-071
- **Assignee**: AI
- **Verification**: Pending
- **Assumptions**: None

### TASK-PLG-073: Generate plugin logo from brand tokens
- **Tier**: L
- **Status**: Not Started
- **Description**: Write `plugins/agnos/assets/agnos.svg` from the brand mark and the `color.brand-*` tokens, declare it as `logo` in both manifests, and check the file exists, test first.
- **Requirement refs**: RQ-PLG-046
- **ADR refs**: ADR-PLG-009
- **Acceptance Criteria**: Given a release, When the marketplace is written, Then the SVG exists And its five fill colours equal the tokens And both manifests hold `logo` `assets/agnos.svg`; Given a manifest whose logo file is absent, When it is checked, Then a problem is reported.
- **Dependencies**: TASK-PLG-072
- **Assignee**: AI
- **Verification**: Pending
- **Assumptions**: None

### TASK-PLG-074: Prove listing metadata install
- **Tier**: M
- **Status**: Not Started
- **Description**: Rehearse a release and install it with `agnos-meta-plugin-proof` in Claude Code and GitHub Copilot.
- **Requirement refs**: RQ-PLG-044, RQ-PLG-045, RQ-PLG-046
- **ADR refs**: ADR-PLG-009
- **Acceptance Criteria**: Given the rehearsed marketplace, When it is installed in both tools, Then each install succeeds And the result of each is recorded.
- **Dependencies**: TASK-PLG-073
- **Assignee**: AI
- **Verification**: Pending
- **Assumptions**: None
