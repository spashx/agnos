# FTR-INI-001: Adding AGNOS to a Project

## Overview
A developer adds AGNOS to an existing or new repository by one explicit call, `agnos-init`. It completes the agent entry-point
files without touching what the developer wrote, keeps what belongs to AGNOS clearly apart, and gives the same result each time.
It runs from the installed AGNOS plugin (amended on 2026-11-01, DEC-PLG-003).

Out of scope: the plugin itself, removing AGNOS from a project, and copying AGNOS into a project.

## Stakeholders
- **Owner**: the repository owner (maintainer of AGNOS).
- **Consumers**: developers adding AGNOS to their repository; the agents working in it; `agnos-meta-demo`.

---

## Functional Requirements

### RQ-INI-001: An explicit, scripted initialisation
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN `agnos-init` is called with a target folder (amended on 2026-11-01, DEC-PLG-003: no toolkit path), its script
  SHALL write the result from the templates of its `assets/`, the agent writing none of the content, with a PowerShell 5.1 and a
  bash version giving the same bytes.
- **Rationale**: the owner wants no non-deterministic behaviour, so the setup cannot depend on what an agent writes or a harness does.
- **Priority**: Must
- **Acceptance Criteria**: Given the same target, When either script runs, Then the files written are byte-identical;
  Given a target that does not exist, When it runs, Then it exits 1 and writes nothing.
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
- **Statement**: WHILE a project is already initialised with the same templates, `agnos-init` SHALL rewrite no file,
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
  `process/3.plan/` and `process/_sessionstate/`, with a `readme.md` saying what it holds in a folder it creates (amended on 2026-10-31,
  TASK-INI-005: it replaces a `.gitkeep`), and SHALL change nothing else in `process/`.
- **Rationale**: `agnos-index` needs `process/`, git keeps no empty folder, and a user needs a minimal guide; once created, the folder belongs to the project.
- **Priority**: Must
- **Acceptance Criteria**: Given a new project, When `agnos-init` then `agnos-index` run, Then both exit 0, And the index has 0 entries, And each
  folder holds only its `readme.md`, with no artifact ID, the same bytes from both scripts; Given a project with `process/3.plan/PLAN-X.md`, When
  `agnos-init` runs, Then that folder gets no `readme.md`, And that file is unchanged; Given a `readme.md` the user changed, When `agnos-init` runs again, Then it stays.
- **Dependencies**: RQ-INI-001, RQ-IDX-008

### RQ-INI-006: The block leads the agent to the process skill
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The block SHALL name the skill `agnos-process`, SHALL say what to do if it is not available, and that commands run from
  the project's root. It SHALL hold no path and no artifact ID of AGNOS's own development. (amended on 2026-11-01, RQ-PLG-004, DEC-PLG-003)
- **Rationale**: the project holds no skill, so nothing else tells the agent the process exists; an installed plugin's folder changes with each version, so a path would not hold.
- **Priority**: Must
- **Acceptance Criteria**: Given a project, When `agnos-init` runs, Then `CLAUDE.md` and `AGENTS.md` each name `agnos-process`, And neither holds a path or an artifact ID. (amended on 2026-11-01; RQ-INI-010)
- **Dependencies**: RQ-INI-002

### RQ-INI-010: Loading the process is an order, in every entry point
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: Each entry-point block SHALL order the agent, before any other action, to invoke the process skill and follow it (amended on 2026-11-01, DEC-PLG-003), SHALL state that START SESSION ACTION runs only when the user asks to start a session, and SHALL NOT rely on an `@` import.
- **Rationale**: a session in the demo received the `@` line without the file's content and without any order to read it; it followed the process only because the agent chose to read the file. The user owns starting a session, as they own closing it.
- **Priority**: Must
- **Acceptance Criteria**: Given a project, When `agnos-init` runs, Then both blocks hold the same order naming `agnos-process` and the same statement on START SESSION ACTION, And no line of a block starts with `@`. (amended on 2026-11-01)
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
- **Amended by**: RQ-PLG-022 — the guide is `agnos-init`'s template `AGNOS-GETTING-STARTED.md`, no longer `GETTING_STARTED.MD`.

### RQ-INI-008: The demo is an initialised project
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The demo's first commit SHALL contain the `CLAUDE.md` and `AGENTS.md` written by `agnos-init` (amended on 2026-11-01,
  DEC-PLG-003: with no toolkit path), and `agnos-meta-demo verify` SHALL fail if a new `agnos-init` call on the demo would change a file.
- **Rationale**: the demo then shows what a project receives, and fails when the templates change and it was not rebuilt.
- **Priority**: Must
- **Acceptance Criteria**: Given the rebuilt demo, When `verify` runs, Then every check passes, And `CLAUDE.md` and `AGENTS.md` hold the
  block alone, And no other toolkit file is in its history; Given two builds, Then their HEAD is the same.
- **Dependencies**: RQ-INI-002, RQ-MTA-005

### RQ-INI-019: Single block for both entry points
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: `agnos-init` SHALL write the same block, from one template, into `CLAUDE.md` and `AGENTS.md`, its question line naming
  `askQuestion` for GitHub Copilot and `AskUserQuestion` for Claude Code, with a question in chat as the fallback.
- **Rationale**: GitHub Copilot reads both files, and two blocks gave it two different orders for the same question.
- **Priority**: Must
- **Acceptance Criteria**: Given a new project, When either script runs, Then the blocks of `CLAUDE.md` and `AGENTS.md` are byte-identical,
  And their question line names `askQuestion` and `AskUserQuestion`; Given the templates folder, Then it holds one block template.
- **Dependencies**: RQ-INI-006, RQ-INI-010, ADR-INI-003

### RQ-INI-020: Context behaviour notes in the block
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The block SHALL explain, in HTML comments only, how Claude Code and GitHub Copilot load the block and the process skill
  at session start, after a clear and after a compaction, and SHALL order the agent to invoke the process skill again after a compaction.
- **Rationale**: the process skill lives only in the conversation, and a compaction can cut it, which a developer does not know.
- **Priority**: Must
- **Acceptance Criteria**: Given the written block, Then its comments name Claude Code and GitHub Copilot, session start, clear and
  compaction, And no text outside its marker lines and comments is longer than before but the re-invocation order; Given the block, Then
  it holds no artifact ID.
- **Dependencies**: RQ-INI-019, ADR-INI-003

### RQ-INI-021: Context-loss risks in the README
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: `README.md`, and the user's guide `AGNOS-GETTING-STARTED.md` in short (amended on 2026-11-14), SHALL explain, for Claude Code and GitHub Copilot, what happens to the process after a clear, an automatic
  compaction and a manual compaction, the risks of each, and what the user does to keep the process loaded.
- **Rationale**: these behaviours depend on the tool and are not widely known, while losing the process silently breaks a session.
- **Priority**: Must
- **Acceptance Criteria**: Given `README.md`, Then one section names both tools, clear, automatic and manual compaction, their risks, and
  the action to take, And it states what the tools' documentation leaves unsaid.
- **Dependencies**: RQ-INI-020, RQ-PLG-023

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
