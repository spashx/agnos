# FTR-PLG-006: The Process Folder is `agnos-process/`, Its Index `process.idx.md`, Named Once

## Overview
The folder AGNOS owns in a project, and in this repository, is renamed from `process/` to `agnos-process/`, and its index from
`INDEX.idx.md` to `process.idx.md`. Its name, its subfolders
and the names of the files AGNOS writes there are declared once, in one layout file; the scripts read generated copies of it, and the
Markdown that cites a path of the folder is checked against it. The generated skill holding the process is renamed, so that
`agnos-process` names one thing only. Projects with a `process/` folder are migrated by `agnos-init`.

Source: the owner's session of 2026-11-06. On that day, outside `process/` itself, 263 occurrences of `process/` stood in 62 tracked
files (26 scripts in Python, PowerShell and bash), with the subfolder and file names written out again: `1.requirements` 59 times,
`INDEX.idx.md` 56, `_sessionstate` 40, `session.yaml` 24; the demo held 52 more.

The owner asked the same day for the index to be named `process.idx.md`.

Out of scope: renaming the subfolders or the other files; making the folder's name a user's choice; the perf center's `--process`
default.

## Stakeholders
- **Owner**: the repository owner (maintainer of AGNOS).
- **Consumers**: developers using the AGNOS plugin and their agents; every AGNOS skill that reads or writes the folder; the demo.

---

## Functional Requirements

### RQ-PLG-034: The process folder is `agnos-process/`
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: AGNOS SHALL keep its artifacts in a folder named `agnos-process/` at the project's root, its generated index named `process.idx.md` in that folder, the other subfolders and files unchanged in name; this repository and the demo SHALL use the same folder and index. Amends RQ-IDX-013 and the index's name wherever a requirement states it.
- **Rationale**: `process/` is a common name a project may already use for something else; the prefix says the folder is AGNOS's.
- **Priority**: Must
- **Acceptance Criteria**: Given a project after `agnos-init`, Then `agnos-process/` holds the four subfolders And no `process/` was created; Given `agnos-index` run on it, Then it writes `agnos-process/process.idx.md` And no `INDEX.idx.md`; Given this repository and the demo at HEAD, Then their artifacts are under `agnos-process/` And the index, the perf center and the release run on them; Given the delivered files, Then none cites `process/` as AGNOS's folder nor `INDEX.idx.md` as its index.
- **Dependencies**: RQ-INI-005, RQ-PLG-036

### RQ-PLG-035: The generated process skill is `agnos-instructions`
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: `agnos-meta-release` SHALL name the skill it generates from the instructions file `agnos-instructions`, and SHALL deliver no skill named `agnos-process`.
- **Rationale**: a folder and a skill both named `agnos-process` would make a search or a sentence such as "read agnos-process" ambiguous.
- **Priority**: Must
- **Acceptance Criteria**: Given a rehearsal, Then the marketplace holds `plugins/agnos/skills/agnos-instructions/SKILL.md` whose name is `agnos-instructions` And no `agnos-process` skill; Given the proof, Then every line passes.
- **Dependencies**: RQ-PLG-003

### RQ-PLG-036: The layout is declared once
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The repository SHALL declare the process folder's name, its subfolders and the names of the files AGNOS writes in it (the index, the session state, the metrics log, the subfolders' `readme.md`) in one file, `layout.json` among `agnos-init`'s assets; every script that needs one of them SHALL read it from a copy generated from that file, in its own language, and SHALL hold no such name otherwise.
- **Rationale**: a name written in 62 files changes in 62 places; written once, a rename is one edit and a generation.
- **Priority**: Must
- **Acceptance Criteria**: Given `layout.json` with another folder name, When the copies are generated, Then the index, the init, the perf center and the release use the new name with no other edit; Given a script of a delivered skill, Then it holds no literal of the layout outside its generated copy; Given the Windows and the Linux scripts, Then they read the same values.
- **Dependencies**: None

### RQ-PLG-037: A copy that differs from the layout is refused
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: IF a generated copy differs from what `layout.json` generates, or a Markdown file of a delivered skill, of the instructions file or of the entry points cites a path of the process folder that the layout does not declare, THEN the test suite SHALL fail and `agnos-meta-release` SHALL exit 1, naming the file and the line.
- **Rationale**: generated copies and prose drift unless a check reads them; the release is where a drift would reach users.
- **Priority**: Must
- **Acceptance Criteria**: Given a copy edited by hand, Then the test fails And the release exits 1 naming the copy; Given a SKILL.md citing `process/3.plan/`, Then both fail naming its line; Given the files as generated, Then both pass.
- **Dependencies**: RQ-PLG-036, RQ-MTA-006

### RQ-PLG-038: `agnos-init` migrates a `process/` folder
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN `agnos-init` runs on a project holding `process/INDEX.idx.md` and no `agnos-process/`, it SHALL rename `process/` to `agnos-process/` and its `INDEX.idx.md` to `process.idx.md` (with `git mv` when they are tracked, so that their history follows) and report the folder `moved`; IF both folders exist, THEN it SHALL change nothing and exit 1, naming both.
- **Rationale**: a project initialised before would otherwise stop working with the new version, its artifacts in a folder no skill reads.
- **Priority**: Must
- **Acceptance Criteria**: Given a git project with a tracked `process/` of AGNOS, When `agnos-init` runs, Then `git status` shows renames to `agnos-process/` And `agnos-process/process.idx.md` And the folder is reported `moved`; Given an untracked `process/` of AGNOS, Then it is renamed And reported `moved`; Given a `process/` without `INDEX.idx.md`, Then it is left untouched; Given both folders, Then the init exits 1 And nothing changed; Given the Windows and the Linux scripts, Then they behave the same.
- **Dependencies**: RQ-PLG-034, RQ-INI-004
