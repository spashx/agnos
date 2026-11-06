# PLAN-PLG-003: The Process Speaks to a Plugin User, and a New Release

## Overview
Correct the three findings of the owner's Claude Code session of 2026-11-04 (FTR-PLG-003), bring the entry-point documents up to date,
and rehearse the release again for the Copilot checks of TASK-PLG-007. No push at any step (DEC-PLG-007).

## References
- **Requirements**: RQ-PLG-018 to RQ-PLG-023, RQ-PLG-004, RQ-DOC-001, RQ-DOC-002, RQ-INI-007 (amended), RQ-PLG-008, RQ-PLG-009
- **ADRs**: ADR-PLG-003, ADR-PLG-001, ADR-PLG-002

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-PLG-018: Feature, decisions and plan
- **Tier**: L
- **Status**: Done
- **Description**: Write FTR-PLG-003, ADR-PLG-003 and this plan, and mark the requirements it amends.
- **Requirement refs**: RQ-PLG-018 to RQ-PLG-022
- **ADR refs**: ADR-PLG-003
- **Acceptance Criteria**: Given the owner's approval, Then ADR-PLG-003 is Accepted; Given the index, Then it has no duplicate.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: ADR-PLG-003 Accepted, owner's "d'accord pour tout" of 2026-11-04; RQ-PLG-004, RQ-DOC-001, RQ-DOC-002 and RQ-INI-007 hold "Amended by"; `agnos-index` exit 0, no duplicate. No test: documents only.
- **Assumptions**: the file is named `AGNOS-GETTING-STARTED.md`, the prefix keeping a developer's own guide untouched; the target of self-improvement is named by the block, after the owner found "the project's folder" unclear.

### TASK-PLG-019: The improvement target, and "this file"
- **Tier**: M
- **Status**: Done
- **Description**: Define the improvement target in the RECURSIVE SELF-IMPROVEMENT section, refer to it from END SESSION step 3, and drop the file name from the line budget.
- **Requirement refs**: RQ-PLG-018, RQ-PLG-019
- **ADR refs**: ADR-PLG-003 (DEC-PLG-013, DEC-PLG-014)
- **Acceptance Criteria**: Given RQ-PLG-018's and RQ-PLG-019's criteria, Then they hold, tested on the skill `process_skill` generates; Given the instructions file, Then its line count is at most 400 and is reported.
- **Dependencies**: TASK-PLG-018
- **Assignee**: AI
- **Verification**: `test_process_text.py` written first, 3 of 3 failed, then 3 OK (target named by the AGNOS block in RECURSIVE SELF-IMPROVEMENT, END SESSION refers to it, no `agnos-sw-eng.instructions.md` in the delivered skill); one failure on the way came from a line break inside "improvement target", fixed by rewrapping the text, the test unchanged. Instructions file: 385 lines. meta-release 95 OK, meta-demo 12 OK, 0 skipped.
- **Assumptions**: the line budget stays on this file only; in a plugin project the lines the user allows bound the addition. "NEVER edit a file of an installed plugin" added as the rule's explicit guard.

### TASK-PLG-020: The block reads the project's rules, and the init's last words in two steps
- **Tier**: M
- **Status**: Done
- **Description**: Add the line reading `process/project-rules.md` to both block templates, reword the success step of `agnos-init`'s SKILL.md, and rebuild the demo with the new block.
- **Requirement refs**: RQ-PLG-018, RQ-PLG-020, RQ-PLG-004
- **ADR refs**: ADR-PLG-003 (DEC-PLG-013, DEC-PLG-015)
- **Acceptance Criteria**: Given RQ-PLG-018's block criterion and RQ-PLG-020's criteria, Then they hold, tested first in `agnos-init`'s suite; Given `agnos-meta-demo`'s suite, Then it passes.
- **Dependencies**: TASK-PLG-018
- **Assignee**: AI
- **Verification**: two tests written first in `test_init.py`, both failed (1 failure, 1 error), then the full init suite 19 OK, both scripts, 0 skipped; the existing RQ-PLG-004 test (no path outside the project) still passes. Demo rebuilt: `build.ps1 -Verify` exit 0, 23 passed, 0 failed, demo HEAD `bc688b8`, its `CLAUDE.md` holds the new line. meta-demo suite 12 OK.
- **Assumptions**: the block names the file twice, once to read it and once as the improvement target, so the process's "the file the AGNOS block names for improvements" has one clear referent.

### TASK-PLG-021: The getting-started file written by init
- **Tier**: M
- **Status**: Done
- **Description**: Reword `GETTING_STARTED.MD` for a plugin user into the template `AGNOS-GETTING-STARTED.md`, and make both init scripts write and report it; the init's skill points to it.
- **Requirement refs**: RQ-PLG-021, RQ-PLG-020, RQ-PLG-022
- **ADR refs**: ADR-PLG-003 (DEC-PLG-016, DEC-PLG-017)
- **Acceptance Criteria**: Given RQ-PLG-021's criteria, Then they hold, tested first in `agnos-init`'s suite on both scripts; Given the template, Then it names no file of this repository a plugin user lacks; Given `agnos-meta-demo`'s suite, Then it passes.
- **Dependencies**: TASK-PLG-020
- **Assignee**: AI
- **Verification**: `GuideTest` written first, 5 of 5 failed; then 1 failure left, an example import `../orders/...` caught as a path outside the project, the example's import changed to `./orderRepository`, the test unchanged; then the init suite 24 OK, both scripts, 0 skipped (created, updated, unchanged, the seven steps named, no path, only `EXP` IDs). Demo rebuilt: verify 23 passed, 0 failed, HEAD `0c281c5`, `AGNOS-GETTING-STARTED.md` at its root. meta-demo suite 12 OK.
- **Assumptions**: the guide keeps the former worked example (`EXP`) and adds what `agnos-init` wrote, the two steps before a session, `process/project-rules.md`, and the `.gitignore` left to the user; links to `.github/` became skill names; the file's first line is a comment saying it is AGNOS's.

### TASK-PLG-022: The guide leaves the root
- **Tier**: L
- **Status**: Done
- **Description**: Remove `GETTING_STARTED.MD`; `agnos-meta-docs-sync` keeps the template as its fourth document; the release stops delivering the guide; links in `README.md`, `CONTRIBUTING.md` and the issue template follow.
- **Requirement refs**: RQ-PLG-022, RQ-DOC-001, RQ-DOC-002, RQ-INI-007
- **ADR refs**: ADR-PLG-003 (DEC-PLG-017)
- **Acceptance Criteria**: Given RQ-PLG-022's criteria, Then they hold, the docs-sync and release ones tested first in their suites.
- **Dependencies**: TASK-PLG-021
- **Assignee**: AI
- **Verification**: new tests written first: docs-sync 4 failures, release 2 failures; then docs-sync 18 OK, meta-demo 12 OK. Before the commit, three release tests reading HEAD failed (every tracked file has a layer, the proof on the demo, the determinism of HEAD), HEAD still holding the guide; after commit `35e8ba7`, meta-release 97 OK, 0 skipped. No `GETTING_STARTED` left outside `process/`.
- **Assumptions**: the README's installation paragraph also lost its "start a new agent session", for RQ-PLG-020's two steps; `AGENTS.md` was edited here rather than by docs-sync, its row naming a file that no longer existed. The demo's check of toolkit paths keeps `GETTING_STARTED.MD`: it still forbids that file in the demo.

### TASK-PLG-023: The entry-point documents brought up to date
- **Tier**: M
- **Status**: Done
- **Description**: Record the Claude Code full session in the README's "What was tested" table, then run `agnos-meta-docs-sync` and review what it changes.
- **Requirement refs**: RQ-PLG-008, RQ-PLG-009
- **ADR refs**: ADR-PLG-001 (DEC-PLG-006)
- **Acceptance Criteria**: Given the README, Then the Claude Code row states the full session observed on 2026-11-04 and only that; Given `CHANGELOG.md`, Then `[Unreleased]` holds PLAN-PLG-002 and PLAN-PLG-003 changes; Given `agnos-meta-demo`'s suite, Then it passes.
- **Dependencies**: TASK-PLG-019, TASK-PLG-022
- **Assignee**: AI
- **Verification**: README's Claude Code row states the session of 2026-11-04, on a marketplace built before the guide. `agnos-meta-docs-sync` on Haiku: `git status` shows only `CHANGELOG.md` changed by it (with the README row of this task); `git diff` read: 10 bullets under `[Unreleased]`, each with the IDs of a real commit (TASK-PLG-009, TASK-PLG-011, TASK-PLG-013 to 016, TASK-PLG-019 to 022), no released section touched. meta-demo 12 OK, `test_marketplace.py` OK, 0 skipped.
- **Assumptions**: older `[Unreleased]` bullets naming `GETTING_STARTED.MD` stay: they record what was true when written. This run of docs-sync on Haiku is the owner's check 5 of TASK-PLG-007 seen from this side only: the owner's own run in a Claude Code session remains theirs.

### TASK-PLG-025: The README as a landing page
- **Tier**: M
- **Status**: Done
- **Description**: Reduce `README.md` to what AGNOS is, its skills, its requirements per platform and getting started; move what was tested into a delivered `COMPATIBILITY.md`, the artifacts table into the guide and the repository map into `CONTRIBUTING.md`.
- **Requirement refs**: RQ-PLG-023, RQ-PLG-008, RQ-INI-007
- **ADR refs**: ADR-PLG-003 (DEC-PLG-018)
- **Acceptance Criteria**: Given RQ-PLG-023's criteria, Then they hold, tested first; Given the suites of `agnos-meta-release` and `agnos-init`, Then they pass.
- **Dependencies**: TASK-PLG-023
- **Assignee**: AI
- **Verification**: tests written first, twice: the landing page (5 marketplace failures, 1 guide failure), then, at the owner's request, the Requirements section and no word of what was tested (2 failures, 1 error); then `test_marketplace.py` OK. After commit `4d73dbc`: meta-release 101 OK, init OK, 0 skipped, the layer test passing once `COMPATIBILITY.md` was at HEAD. Demo rebuilt: 23 passed, HEAD `4347a66`. meta-demo 12 OK.
- **Assumptions**: the requirements were read from the skills: Python 3.9+ only for `agnos-perf-center` (its SKILL.md and scripts), PowerShell 5.1 or bash for the others, tree-sitter never fetched, the page's libraries from cdnjs. Scope grown at the owner's request during the task: the Requirements section and the removal of the last "tested" sentence.

### TASK-PLG-024: The release rehearsed again, and proved
- **Tier**: M
- **Status**: Done
- **Description**: Rehearse HEAD into `C:\dev\repos\spashx\agnos-marketplace`, then run `agnos-meta-plugin-proof` on it.
- **Requirement refs**: RQ-PLG-007, RQ-PLG-010, RQ-PLG-012 to RQ-PLG-017
- **ADR refs**: ADR-PLG-002, ADR-PLG-001
- **Acceptance Criteria**: Given a rehearsal of the last commit, Then the exit is 0 and the lines to read are judged; Given the proof, Then every line it runs passes, And the lines it skips are stated with why.
- **Dependencies**: TASK-PLG-025
- **Assignee**: AI
- **Verification**: rehearsal of `25869d8`: `exit=0, 55 files, 1195 IDs removed, 2 lines to read`; both read in the output and judged false alarms (a sentence whole once its comment left, a docstring); 15 mentions, all in `CHANGELOG.md` and the perf center's `maintaining.md`; `COMPATIBILITY.md` and the guide template present, no `GETTING_STARTED.MD`, no `__pycache__`. Proof with `AGNOS_CLAUDE` naming the VS Code extension's `claude.exe` 2.1.318: exit 0, 8 lines pass: claude validate-plugin, validate-catalogue, marketplace-add, install, skills 6 of 6; copilot marketplace-add, install, skills 6 of 6. Not run: `--with-models` (costs credits, not asked) and `--linux`.
- **Assumptions**: the earlier output and its two reports were removed with the owner's approval of 2026-11-04. The proof's working folder `C:\pp` could not be removed by the agent: the owner's to delete.
