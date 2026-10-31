# FTR-INI-001: Adding AGNOS to a Project

## Overview
A developer adds AGNOS to an existing or new repository by one explicit call, `agnos-init`. It completes the agent entry-point
files without touching what the developer wrote, keeps what belongs to AGNOS clearly apart, and gives the same result each time.
It works from a toolkit on disk, and needs no plugin.

Out of scope: the plugin itself, removing AGNOS from a project, and copying the toolkit into a project.

## Stakeholders
- **Owner**: the repository owner (maintainer of AGNOS).
- **Consumers**: developers adding AGNOS to their repository; the agents working in it; `agnos-meta-demo`.

---

## Functional Requirements

### RQ-INI-001: An explicit, scripted initialisation
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN `agnos-init` is called with a target folder and the path of the toolkit as seen from that folder, its script
  SHALL write the result from the templates of its `assets/`, the agent writing none of the content, with a PowerShell 5.1 and a
  bash version giving the same bytes.
- **Rationale**: the owner wants no non-deterministic behaviour, so the setup cannot depend on what an agent writes or a harness does.
- **Priority**: Must
- **Acceptance Criteria**: Given the same target and toolkit path, When either script runs, Then the files written are byte-identical;
  Given a toolkit path without the instructions file, When it runs, Then it exits 1 and writes nothing.
- **Dependencies**: ADR-INI-001

### RQ-INI-002: Existing files are completed
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: `agnos-init` SHALL write in `CLAUDE.md` and `AGENTS.md` only one block between the lines `<!-- AGNOS:BEGIN` and
  `<!-- AGNOS:END -->`: it creates an absent file with the block alone, adds the block at the end of a file without one, and replaces
  only the block of a file that has one, every other byte of the file being preserved, and the block taking the file's line ending.
- **Rationale**: a developer can add AGNOS without breaking their files, and tell their content from AGNOS's at a glance.
- **Priority**: Must
- **Acceptance Criteria**: Given a CRLF file with a UTF-8 BOM and no final newline, When `agnos-init` runs, Then its original bytes
  are unchanged before the block, And the block uses CRLF; Given a file with a block and text on both sides, When its block is
  outdated, Then only the block changes.
- **Dependencies**: RQ-INI-001

### RQ-INI-003: A second call changes nothing
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE a project is already initialised with the same toolkit path and templates, `agnos-init` SHALL rewrite no file,
  and SHALL report each entry-point file as `created`, `added`, `updated` or `unchanged`.
- **Rationale**: the call is safe to repeat, and an update of AGNOS is the same call.
- **Priority**: Must
- **Acceptance Criteria**: Given an initialised project, When `agnos-init` runs again, Then no file's content or modification time
  changes, And each file is reported `unchanged`.
- **Dependencies**: RQ-INI-002

### RQ-INI-004: A damaged block stops the call
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: IF an entry-point file holds a `BEGIN` without an `END`, an `END` without a `BEGIN`, an `END` before its `BEGIN`, or
  more than one of either, THEN `agnos-init` SHALL write no file at all, SHALL name the file on the error stream and SHALL exit with code 1.
- **Rationale**: guessing the limits of the block could destroy what the developer wrote.
- **Priority**: Must
- **Acceptance Criteria**: Given a valid `CLAUDE.md` and an `AGENTS.md` with two `BEGIN` lines, When `agnos-init` runs, Then it exits 1,
  And the error names `AGENTS.md`, And neither file changes.
- **Dependencies**: RQ-INI-002

### RQ-INI-005: The process folder
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: `agnos-init` SHALL create, each only when absent, `process/1.requirements/`, `process/2.architecture/`,
  `process/3.plan/` and `process/_sessionstate/`, with a `.gitkeep` in a folder it creates, and SHALL change nothing else in `process/`.
- **Rationale**: `agnos-index` needs `process/`, and git keeps no empty folder; once created, the folder belongs to the project.
- **Priority**: Must
- **Acceptance Criteria**: Given a new project, When `agnos-init` then `agnos-index` run, Then both exit 0; Given a project with
  `process/3.plan/PLAN-X.md`, When `agnos-init` runs, Then that folder gets no `.gitkeep`, And that file is unchanged.
- **Dependencies**: RQ-INI-001, RQ-IDX-008

### RQ-INI-006: The block leads the agent to the toolkit
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The block SHALL give the toolkit path as passed, with `/` separators, and SHALL state the instructions file to load,
  where each skill's `SKILL.md` is, and that the procedures' `.github/skills/` paths are relative to the toolkit while commands run from
  the project's root. It SHALL hold no artifact ID of AGNOS's own development.
- **Rationale**: the project holds no skill, so nothing else tells the agent where they are; a relative path keeps a committed block valid for each clone.
- **Priority**: Must
- **Acceptance Criteria**: Given the toolkit path `..\agnos`, When `agnos-init` runs, Then `CLAUDE.md` and `AGENTS.md` each name
  `../agnos/.github/instructions/agnos-sw-eng.instructions.md` to read, And neither holds an artifact ID. (amended on 2026-10-31; RQ-INI-010)
- **Dependencies**: RQ-INI-002

### RQ-INI-010: Reading the instructions is an order, in every entry point
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: Each entry-point block SHALL order the agent, before any other action, to read the instructions file in full and to run its START SESSION ACTION, and SHALL NOT rely on an `@` import.
- **Rationale**: a session in the demo received the `@` line without the file's content and without any order to read it; it followed the process only because the agent chose to read the file.
- **Priority**: Must
- **Acceptance Criteria**: Given the toolkit path `../agnos`, When `agnos-init` runs, Then both blocks hold the same order naming that path, And no line of a block starts with `@`.
- **Dependencies**: RQ-INI-006

### RQ-INI-007: The call is stated where it is needed
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: `README.md` and `GETTING_STARTED.MD` SHALL give `agnos-init` as the step that adds AGNOS to a project; and IF a project
  has no `process/` folder, THEN the instructions file and the error of `agnos-index` SHALL both say to call `agnos-init`.
- **Rationale**: an uninitialised project does not load the instructions, so the rule there cannot be the only one; the script's error holds whatever the agent read.
- **Priority**: Must
- **Acceptance Criteria**: Given no `process/`, When `agnos-index` runs in either version, Then it exits 1 with
  `agnos-index: 'process' folder not found - run from the repository root, or call agnos-init to add AGNOS to this project`; Given
  the instructions file, Then START SESSION says to stop and ask for `agnos-init` in that case, And it stays within 400 lines.
- **Dependencies**: RQ-IDX-008, RQ-INI-001

### RQ-INI-008: The demo is an initialised project
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The demo's first commit SHALL contain the `CLAUDE.md` and `AGENTS.md` written by `agnos-init` with the toolkit path
  `../agnos-lightweight-process`, and `agnos-meta-demo verify` SHALL fail if a new `agnos-init` call on the demo would change a file.
- **Rationale**: the demo then shows what a project receives, and fails when the templates change and it was not rebuilt.
- **Priority**: Must
- **Acceptance Criteria**: Given the rebuilt demo, When `verify` runs, Then every check passes, And `CLAUDE.md` and `AGENTS.md` hold the
  block alone, And no other toolkit file is in its history; Given two builds, Then their HEAD is the same.
- **Dependencies**: RQ-INI-002, RQ-MTA-005

---

## Non-Functional Requirements

### RQ-INI-009: The skill follows the documented practices
- **Category**: Non-Functional
- **NFR Type**: Maintainability
- **EARS Type**: Ubiquitous
- **Statement**: `agnos-init` SHALL be a process skill, without the `agnos-meta-` prefix, with its Claude Code pointer, listed in `CLAUDE.md`
  and `AGENTS.md`, its `name` equal to its folder, and its `description` saying what it does and when.
- **Metric**: description at most 1,024 characters; `SKILL.md` under 500 lines; references one level deep.
- **Measurement Method**: a unit test reads the front matter, the line count and the two lists.
- **Priority**: Should
- **Acceptance Criteria**: Given the skill, When its test runs, Then each metric holds, And `disable-model-invocation` is absent.
- **Dependencies**: RQ-MTA-001
