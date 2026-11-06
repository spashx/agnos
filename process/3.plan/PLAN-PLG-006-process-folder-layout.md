# PLAN-PLG-006: The Process Folder is `agnos-process/`, Its Index `process.idx.md`, Named Once

## Overview
Declare the layout once, move every script and text onto it, then rename the folder by one edit of the layout (FTR-PLG-006).
Runs before PLAN-PLG-005, whose files then go into the renamed folder. No push at any step (DEC-PLG-007).

## References
- **Requirements**: RQ-PLG-034, RQ-PLG-035, RQ-PLG-036, RQ-PLG-037, RQ-PLG-038
- **ADRs**: ADR-PLG-006, ADR-PLG-001, ADR-INI-001, ADR-IDX-001

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-PLG-038: Feature, decisions and plan
- **Tier**: L
- **Status**: Done
- **Description**: Write FTR-PLG-006, ADR-PLG-006 and this plan, and mark PLAN-PLG-005 as depending on it.
- **Requirement refs**: RQ-PLG-034, RQ-PLG-035, RQ-PLG-036, RQ-PLG-037, RQ-PLG-038
- **ADR refs**: ADR-PLG-006
- **Acceptance Criteria**: Given the owner's approval, Then ADR-PLG-006 is Accepted; Given the index, Then it has no duplicate.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: ADR-PLG-006 Status set to Accepted on the owner's word (2026-11-06); `agnos-index` exit 0, no duplicate.
- **Assumptions**: None

### TASK-PLG-039: The layout and its generator
- **Tier**: L
- **Status**: Not Started
- **Description**: Write `layout.json` (folder still `process`), `layout.py --write` and `--check`, and their tests.
- **Requirement refs**: RQ-PLG-036, RQ-PLG-037
- **ADR refs**: ADR-PLG-006 (DEC-PLG-027, DEC-PLG-028)
- **Acceptance Criteria**: Given RQ-PLG-036's and RQ-PLG-037's criteria on fixtures, Then they hold, tested first.
- **Dependencies**: TASK-PLG-038
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-PLG-040: `agnos-index` reads the layout
- **Tier**: L
- **Status**: Not Started
- **Description**: Generate the index's copies; `build-index.ps1` and `build-index.sh` take the folder, subfolders and index name from them.
- **Requirement refs**: RQ-PLG-036
- **ADR refs**: ADR-PLG-006 (DEC-PLG-027), ADR-IDX-001
- **Acceptance Criteria**: Given the index's golden tests on both platforms, Then they pass unchanged; Given a fixture layout with another folder, Then both scripts index it.
- **Dependencies**: TASK-PLG-039
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-PLG-041: `agnos-init` reads the layout and migrates `process/`
- **Tier**: L
- **Status**: Not Started
- **Description**: Generate the init's copies; `init.ps1` and `init.sh` create the layout's folders and move an AGNOS `process/`.
- **Requirement refs**: RQ-PLG-036, RQ-PLG-038
- **ADR refs**: ADR-PLG-006 (DEC-PLG-027, DEC-PLG-031), ADR-INI-001
- **Acceptance Criteria**: Given RQ-PLG-038's criteria, Then they hold on both scripts, tested first; Given the init's suite, Then it passes.
- **Dependencies**: TASK-PLG-039
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-PLG-042: The perf center and the other delivered skills read the layout
- **Tier**: L
- **Status**: Not Started
- **Description**: Generate the copies of `agnos-perf-center` and of any other delivered skill whose scripts cite the layout; move their SKILL.md texts onto the layout's paths.
- **Requirement refs**: RQ-PLG-036, RQ-PLG-037
- **ADR refs**: ADR-PLG-006 (DEC-PLG-027, DEC-PLG-028)
- **Acceptance Criteria**: Given their suites, Then they pass; Given `layout.py --check`, Then it reports nothing for these skills.
- **Dependencies**: TASK-PLG-039
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-PLG-043: The release reads the layout, checks it, and renames the generated skill
- **Tier**: L
- **Status**: Not Started
- **Description**: `release.py` and the maintainer skills take the layout from their copies, run `layout.py --check` on the rehearsed commit, and generate `agnos-instructions`.
- **Requirement refs**: RQ-PLG-035, RQ-PLG-036, RQ-PLG-037
- **ADR refs**: ADR-PLG-006 (DEC-PLG-028, DEC-PLG-030), ADR-PLG-001
- **Acceptance Criteria**: Given RQ-PLG-035's and RQ-PLG-037's criteria, Then they hold, tested first; Given the suites of the release, the proof and the demo, Then they pass.
- **Dependencies**: TASK-PLG-040, TASK-PLG-041, TASK-PLG-042
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-PLG-044: The instructions file and the entry points cite the layout's paths
- **Tier**: M
- **Status**: Not Started
- **Description**: Bring the instructions file, the AGNOS block, `AGENTS.md`, `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`, the templates and the guide in line with the layout and the skill's new name.
- **Requirement refs**: RQ-PLG-035, RQ-PLG-037
- **ADR refs**: ADR-PLG-006 (DEC-PLG-028, DEC-PLG-030)
- **Acceptance Criteria**: Given `layout.py --check`, Then it reports nothing; Given the instructions file, Then its line count is reported.
- **Dependencies**: TASK-PLG-043
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-PLG-045: The rename
- **Tier**: L
- **Status**: Not Started
- **Description**: Set `folder` to `agnos-process` and `index` to `process.idx.md`, regenerate the copies, `git mv process agnos-process` and the index in this repository, update `.gitignore` and `.gitattributes`, and regenerate the index.
- **Requirement refs**: RQ-PLG-034, RQ-PLG-036
- **ADR refs**: ADR-PLG-006 (DEC-PLG-029)
- **Acceptance Criteria**: Given the layout's edit, Then no other script changes by hand; Given every suite of the repository, Then it passes; Given `agnos-index` and the perf center on this repository, Then they run on `agnos-process/` And the index is `agnos-process/process.idx.md`.
- **Dependencies**: TASK-PLG-044
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-PLG-046: The demo rebuilt on `agnos-process/`
- **Tier**: M
- **Status**: Not Started
- **Description**: Move `agnos-meta-demo`'s scenario and checks onto the layout, rebuild the demo and verify it.
- **Requirement refs**: RQ-PLG-034
- **ADR refs**: ADR-PLG-006 (DEC-PLG-029)
- **Acceptance Criteria**: Given the rebuilt demo, Then its artifacts are under `agnos-process/` And `agnos-meta-demo`'s checks pass.
- **Dependencies**: TASK-PLG-045
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-PLG-047: The release rehearsed and proved after the rename
- **Tier**: M
- **Status**: Not Started
- **Description**: Rehearse HEAD into an empty scratchpad folder and prove it; migrate a copy of `agnos-trial-copilot` with the new init.
- **Requirement refs**: RQ-PLG-034, RQ-PLG-035, RQ-PLG-038
- **ADR refs**: ADR-PLG-006
- **Acceptance Criteria**: Given a rehearsal, Then the exit is 0 And no delivered file cites `process/` as AGNOS's folder; Given the proof, Then every line passes; Given the copy of `agnos-trial-copilot`, Then its folder and index are moved And `agnos-index` runs on it.
- **Dependencies**: TASK-PLG-046
- **Assignee**: AI
- **Verification**:
- **Assumptions**:
