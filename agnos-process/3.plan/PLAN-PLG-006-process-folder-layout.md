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
- **Status**: Done
- **Description**: Write `layout.json` (folder still `process`), `layout.py --write` and `--check`, and their tests.
- **Requirement refs**: RQ-PLG-036, RQ-PLG-037
- **ADR refs**: ADR-PLG-006 (DEC-PLG-027, DEC-PLG-028)
- **Acceptance Criteria**: Given RQ-PLG-036's and RQ-PLG-037's criteria on fixtures, Then they hold, tested first.
- **Dependencies**: TASK-PLG-038
- **Assignee**: AI
- **Verification**: `test_layout.py` written first: 8 fixture tests passed, the working-tree one failed (9 copies missing) until `--write`; then `--check` exit 0, 0 findings. Suite of `agnos-meta-release` on a copy: 115 run, 113 OK, 2 skipped (the demo was not in the copy).
- **Assumptions**: `layout.json` also declares `projectRules` and `perfCenterPage`, the two files at the folder's root that the Markdown cites; the copies carry no requirement ID, being generated (the generator carries them); the folder the index scans is every subfolder but the session state's; copies forced LF in `.gitattributes`.

### TASK-PLG-040: `agnos-index` reads the layout
- **Tier**: L
- **Status**: Done
- **Description**: Generate the index's copies; `build-index.ps1` and `build-index.sh` take the folder, subfolders and index name from them.
- **Requirement refs**: RQ-PLG-036
- **ADR refs**: ADR-PLG-006 (DEC-PLG-027), ADR-IDX-001
- **Acceptance Criteria**: Given the index's golden tests on both platforms, Then they pass unchanged; Given a fixture layout with another folder, Then both scripts index it.
- **Dependencies**: TASK-PLG-039
- **Assignee**: AI
- **Verification**: New scenario "another folder" written first: 2 FAIL on each suite against the old scripts; after the change `test-build-index.sh` (default and POSIX) and `.ps1`: "All checks passed", golden files unchanged; both generators on this repository: 693 entries, index unchanged.
- **Assumptions**: The tests take the folder from the layout copy and rename the fixtures' `process` folder to it, so the rename needs no test edit.

### TASK-PLG-041: `agnos-init` reads the layout and migrates `process/`
- **Tier**: L
- **Status**: Done
- **Description**: Generate the init's copies; `init.ps1` and `init.sh` create the layout's folders and move an AGNOS `process/`.
- **Requirement refs**: RQ-PLG-036, RQ-PLG-038
- **ADR refs**: ADR-PLG-006 (DEC-PLG-027, DEC-PLG-031), ADR-INI-001
- **Acceptance Criteria**: Given RQ-PLG-038's criteria, Then they hold on both scripts, tested first; Given the init's suite, Then it passes.
- **Dependencies**: TASK-PLG-039
- **Assignee**: AI
- **Verification**: 4 `MigrationTest` cases (tracked, untracked, no index, both folders; PowerShell and bash) written first: 6 FAIL, 25 existing OK; after the change: 29 run, OK, 0 skipped.
- **Assumptions**: The migration tests run on a temporary copy of the skill whose layout copies name `agnos-process`/`process.idx.md`, the repository's layout still saying `process`; the report line is `moved process to agnos-process`; exit 1 for both folders only when `process/` is AGNOS's (holds the legacy index).

### TASK-PLG-042: The perf center and the other delivered skills read the layout
- **Tier**: L
- **Status**: Done
- **Description**: Generate the copies of `agnos-perf-center` and of any other delivered skill whose scripts cite the layout; move their SKILL.md texts onto the layout's paths.
- **Requirement refs**: RQ-PLG-036, RQ-PLG-037
- **ADR refs**: ADR-PLG-006 (DEC-PLG-027, DEC-PLG-028)
- **Acceptance Criteria**: Given their suites, Then they pass; Given `layout.py --check`, Then it reports nothing for these skills.
- **Dependencies**: TASK-PLG-039
- **Assignee**: AI
- **Verification**: `--check` extended to delivered scripts, tested first (1 FAIL, then 11 OK); it found 5 lines of the perf center, then 0. Perf-center suite on a copy: 367 run, 363 OK, 3 skipped (opt-in perf tests, `AGNOS_PERF_CENTER_PERF`), 1 FAIL RQ-HST-015 (history imported the copy): fixed, the log's path given by `perf_center.py`; `test_history` 45 OK, `test_friction` 8 OK, `test_delivery` 9 OK.
- **Assumptions**: The perf center's tests take the index and log names from the copy; its fixture `tests/fixtures/repo/process/INDEX.idx.md` is renamed with the rename (TASK-PLG-045).

### TASK-PLG-043: The release reads the layout, checks it, and renames the generated skill
- **Tier**: L
- **Status**: Done
- **Description**: `release.py` and the maintainer skills take the layout from their copies, run `layout.py --check` on the rehearsed commit, and generate `agnos-instructions`.
- **Requirement refs**: RQ-PLG-035, RQ-PLG-036, RQ-PLG-037
- **ADR refs**: ADR-PLG-006 (DEC-PLG-028, DEC-PLG-030), ADR-PLG-001
- **Acceptance Criteria**: Given RQ-PLG-035's and RQ-PLG-037's criteria, Then they hold, tested first; Given the suites of the release, the proof and the demo, Then they pass.
- **Dependencies**: TASK-PLG-040, TASK-PLG-041, TASK-PLG-042
- **Assignee**: AI
- **Verification**: `ReleaseTest` (3) and the `agnos-instructions` expectations written first: 3 ERROR, 2 FAIL, then OK. On a copy committed as HEAD: release 120 OK, plugin-proof 16 OK, init 29 OK, docs-sync 18 OK, 0 skipped; `--check` 0 findings. Two stdlib-only tests failed on the copy imports: RQ-MTA-013 and RQ-PLG-010 amended by the owner (standard library and the modules of the script's own folder), tests following.
- **Assumptions**: A rehearsed commit holding no `layout.json` (the tests' synthetic repositories) has no layout to check; the AGNOS block and the guide take the new skill name here, with the release, since the plugin delivers it; `tarfile`'s `filter="data"` needs Python 3.12 or a patched 3.10/3.11.

### TASK-PLG-044: The instructions file and the entry points cite the layout's paths
- **Tier**: M
- **Status**: Done
- **Description**: Bring the instructions file, the AGNOS block, `AGENTS.md`, `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`, the templates and the guide in line with the layout and the skill's new name.
- **Requirement refs**: RQ-PLG-035, RQ-PLG-037
- **ADR refs**: ADR-PLG-006 (DEC-PLG-028, DEC-PLG-030)
- **Acceptance Criteria**: Given `layout.py --check`, Then it reports nothing; Given the instructions file, Then its line count is reported.
- **Dependencies**: TASK-PLG-043
- **Assignee**: AI
- **Verification**: `layout.py --check`: 0 findings; no `agnos-process` skill named in the entry points, the instructions file or the SKILL.md files; instructions file: 386 lines.
- **Assumptions**: The block and the guide took the new name in TASK-PLG-043; the folder's paths in the prose, still declared while the layout says `process`, change with the rename (TASK-PLG-045), where `--check` names each one.

### TASK-PLG-045: The rename
- **Tier**: L
- **Status**: Done
- **Description**: Set `folder` to `agnos-process` and `index` to `process.idx.md`, regenerate the copies, `git mv process agnos-process` and the index in this repository, update `.gitignore` and `.gitattributes`, and regenerate the index.
- **Requirement refs**: RQ-PLG-034, RQ-PLG-036
- **ADR refs**: ADR-PLG-006 (DEC-PLG-029)
- **Acceptance Criteria**: Given the layout's edit, Then no other script changes by hand; Given every suite of the repository, Then it passes; Given `agnos-index` and the perf center on this repository, Then they run on `agnos-process/` And the index is `agnos-process/process.idx.md`.
- **Dependencies**: TASK-PLG-044
- **Assignee**: AI
- **Verification**: One edit of `layout.json`, `--write`, no script edited by hand. `git mv` of the folder, its index and the perf center's fixture. `--check` named 50 lines of prose, rewritten, then 0 findings. Both index generators: 693 entries on `agnos-process/process.idx.md`; perf center on `agnos-process`: A 9.5/10. On a committed copy: perf center 367 run, 364 OK, 3 skipped (opt-in perf tests); init 29, plugin-proof 16, docs-sync 18, demo 12, qa 32 OK; both index suites passed; release 118 of 120: the 2 rehearsals proved on the demo fail until the demo is rebuilt (TASK-PLG-046).
- **Assumptions**: Maintainer files that wrote the folder out (`layers.json`, tests of the perf center, the release, docs-sync, the demo) were moved onto the layout here; the demo's own scenario stays for TASK-PLG-046.

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
