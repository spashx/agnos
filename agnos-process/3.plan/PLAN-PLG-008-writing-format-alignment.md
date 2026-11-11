# PLAN-PLG-008: Writing-format alignment of the demo

## Overview
Record the owner's writing rules (FTR-PLG-007), correct the title range, align the demo and the website on them, then release
3.4.0, rebuild the demo on it and rehearse its marketplace.

## References
- **Requirements**: RQ-PLG-039, RQ-PLG-040, RQ-PLG-041, RQ-DMO-005, RQ-DMO-008, RQ-DMO-021, RQ-PLG-027 to RQ-PLG-033, RQ-PLG-012, RQ-WEB-003, RQ-WEB-005
- **ADRs**: ADR-DMO-001, ADR-PLG-005, ADR-PLG-002, ADR-WEB-001

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-PLG-053: Record artifact writing-format requirements
- **Tier**: M
- **Status**: Done
- **Description**: Write FTR-PLG-007 (RQ-PLG-039 to RQ-PLG-041) and this plan.
- **Requirement refs**: RQ-PLG-039, RQ-PLG-040, RQ-PLG-041
- **ADR refs**: None
- **Acceptance Criteria**: Given `agnos-index`, When run, Then it indexes FTR-PLG-007, its 3 RQs and this plan with no duplicate ID.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `agnos-index` exit 0, 843 entries, 119 documents; FTR-PLG-007, RQ-PLG-039 to 041, PLAN-PLG-008, TASK-PLG-053 to 061 indexed. No code: tests N/A.
- **Assumptions**: The owner's edit of `197f33c` is recorded as RQs without an ADR: it changes rules, not architecture.

### TASK-PLG-054: Correct title word range
- **Tier**: S
- **Status**: Not Started
- **Description**: Replace "3-8 words" by "2-8 words" in MANDATORY TITLE FORMAT and cite RQ-PLG-039 to RQ-PLG-041 in comments.
- **Requirement refs**: RQ-PLG-039, RQ-PLG-040, RQ-PLG-041
- **ADR refs**: None
- **Acceptance Criteria**: Given the instructions file, Then it states 2-8 words And stays within 400 lines.
- **Dependencies**: TASK-PLG-053
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: 

### TASK-PLG-055: Restructure demo decisions
- **Tier**: M
- **Status**: Not Started
- **Description**: Rewrite each DEC of the demo's ADRs as a one-sentence Statement and a Rationale, in `agnos-meta-demo/assets/content/`.
- **Requirement refs**: RQ-PLG-040, RQ-DMO-005
- **ADR refs**: ADR-DMO-001
- **Acceptance Criteria**: Given each demo ADR, Then each DEC holds a Statement "The … SHALL …" And a Rationale; Given the scenario's `edits`, Then each still finds its text.
- **Dependencies**: TASK-PLG-053
- **Assignee**: AI
- **Verification**: 
- **Assumptions**: 

### TASK-PLG-056: Move demo ADR citations to plain text
- **Tier**: M
- **Status**: Not Started
- **Description**: Turn the `<!-- Motivated by: … -->` comments of the demo's ADRs into plain text.
- **Requirement refs**: RQ-PLG-041, RQ-DMO-008
- **ADR refs**: ADR-DMO-001
- **Acceptance Criteria**: Given the demo's `agnos-process/`, Then no artifact file holds an ID in an HTML comment.
- **Dependencies**: TASK-PLG-053
- **Assignee**: AI
- **Verification**: 
- **Assumptions**: 

### TASK-PLG-057: Retitle demo artifacts
- **Tier**: M
- **Status**: Not Started
- **Description**: Retitle the demo's FTR, RQ, ADR, DEC, PLAN and TASK per RQ-PLG-039, keeping their IDs; a title joining two concerns becomes one covering title; the drafts and the scenario follow.
- **Requirement refs**: RQ-PLG-039, RQ-DMO-005
- **ADR refs**: ADR-DMO-001
- **Acceptance Criteria**: Given every demo artifact title, Then it complies with MANDATORY TITLE FORMAT; Given the scenario's `edits` and commit messages, Then they match the new text.
- **Dependencies**: TASK-PLG-055, TASK-PLG-056
- **Assignee**: AI
- **Verification**: 
- **Assumptions**: 

### TASK-PLG-058: Prepare version 3.4.0 release
- **Tier**: M
- **Status**: Not Started
- **Description**: Run `agnos-meta-release-prep`: repository checks, docs-sync, changelog, version 3.4.0 approved by the owner, commit.
- **Requirement refs**: RQ-PLG-027 to RQ-PLG-033
- **ADR refs**: ADR-PLG-005
- **Acceptance Criteria**: Given `VERSION.txt`, Then it holds 3.4.0; Given the changelog, Then a 3.4.0 section lists this plan's changes.
- **Dependencies**: TASK-PLG-054, TASK-PLG-057
- **Assignee**: AI
- **Verification**: 
- **Assumptions**: 

### TASK-PLG-059: Rebuild demo on version 3.4.0
- **Tier**: M
- **Status**: Not Started
- **Description**: Run `agnos-meta-demo build -Verify` and the generator's tests.
- **Requirement refs**: RQ-DMO-005, RQ-DMO-008, RQ-DMO-021
- **ADR refs**: ADR-DMO-001
- **Acceptance Criteria**: Given the rebuilt demo, When `verify` runs, Then every requirement is PASS; Given the generator's tests, Then they pass.
- **Dependencies**: TASK-PLG-058
- **Assignee**: AI
- **Verification**: 
- **Assumptions**: 

### TASK-PLG-060: Align website with renamed demo
- **Tier**: M
- **Status**: Not Started
- **Description**: Update `en.md` and `fr.md` where they quote the demo's titles, excerpts and index lines, then rebuild the site; the owner checks it visually.
- **Requirement refs**: RQ-WEB-003, RQ-WEB-005
- **ADR refs**: ADR-WEB-001
- **Acceptance Criteria**: Given the site's text, Then every demo title, excerpt and line range it quotes matches the rebuilt demo; Given `agnos-meta-website`, Then its content check passes.
- **Dependencies**: TASK-PLG-059
- **Assignee**: AI (text), Human (visual check)
- **Verification**: 
- **Assumptions**: 

### TASK-PLG-061: Rehearse 3.4.0 marketplace release
- **Tier**: M
- **Status**: Not Started
- **Description**: Run `agnos-meta-release` on the 3.4.0 commit; nothing is published.
- **Requirement refs**: RQ-PLG-012, RQ-PLG-031
- **ADR refs**: ADR-PLG-002
- **Acceptance Criteria**: Given the rehearsal, Then its manifests hold 3.4.0 And both checks are true And exit is 0.
- **Dependencies**: TASK-PLG-058
- **Assignee**: AI
- **Verification**: 
- **Assumptions**: 
