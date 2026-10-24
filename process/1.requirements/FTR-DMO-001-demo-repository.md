# FTR-DMO-001: Demo repository

## Overview
A second repository, `agnos-lightweight-process.demo`, shows the AGNOS process applied to a software
project, so that the process can be validated and its capabilities demonstrated. The repository looks
like a clone of this one, stripped of this repository's own process data, in which the development of a
small software product has started: its source code in two languages, the process artifacts that led to
that code, and the traceability between both. The history that makes it look worked on by several people
over two months is specified by FTR-DMO-002.

The demo is the standing reference for demonstrating and testing AGNOS. Its generator is therefore kept in
this repository as a maintainer skill, `agnos-demo`, so the demo can be rebuilt and checked again whenever
AGNOS evolves.

The source code is an illustration: it follows the AGNOS code rules but is not required to compile or run.
The demo software, its trigrams and its domain are chosen in the planning phase; its trigrams SHALL differ
from the trigrams of this repository (TRC, IDX, DSY, AGT, FIX, DMO).

## Stakeholders
- **Owner**: AGNOS process maintainer (this repository)
- **Consumers**: People evaluating the AGNOS process; AI agents run against the demo to check the process

---

## Functional Requirements

### RQ-DMO-001: Sibling independent repository
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The demo repository SHALL be a new git repository named `agnos-lightweight-process.demo`,
  located in the same parent directory as the `agnos-lightweight-process` directory.
- **Rationale**: The demo is a separate product repository, not a folder of this one.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** the parent directory of `agnos-lightweight-process`
  - **When** its entries are listed and `git rev-parse --show-toplevel` is run in the demo directory
  - **Then** `agnos-lightweight-process.demo` is a sibling directory
  - **And** its top-level directory is itself, not `agnos-lightweight-process`
- **Dependencies**: None

### RQ-DMO-002: AGNOS toolkit without process data
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The demo repository SHALL contain the AGNOS toolkit of this repository (the instructions
  file, the four skills with their `.claude` entry points, `CLAUDE.md`, `AGENTS.md` and the getting-started
  guide) and SHALL NOT contain any artifact of this repository's own `process/` folder, nor the
  `agnos-demo` skill that generates it.
- **Rationale**: The demo must look like a fresh clone of AGNOS in which a project was started, with no
  trace of how AGNOS itself was built.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** the demo repository at its last commit
  - **When** the file list is compared with this repository
  - **Then** every toolkit file is present
  - **And** no ID with a trigram TRC, IDX, DSY, AGT, FIX or DMO appears under `process/`
  - **And** no `agnos-demo` skill folder is present
- **Dependencies**: RQ-DMO-001

### RQ-DMO-003: Source code in two languages
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The demo repository SHALL contain the source code of a software product written in two
  different programming languages, each with at least 4 source files and a build or dependency manifest,
  arranged as a real project.
- **Rationale**: Two languages show that the process and the traceability do not depend on a language.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** the demo repository at its last commit
  - **When** the source files are grouped by language
  - **Then** two languages each have at least 4 source files
  - **And** each has a manifest (for example `pom.xml`, `package.json`, `pyproject.toml`)
- **Dependencies**: RQ-DMO-001

### RQ-DMO-004: Code follows the AGNOS code rules
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The source and test code of the demo SHALL follow the code rules of the AGNOS
  instructions: SOLID, named constants instead of duplicated literals, requirement and decision IDs in
  comments, and a Gherkin-named unit test for each function of the Tier M and L tasks.
- **Rationale**: The demo illustrates the process, so its code is what the process asks for.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** the source and test files of the demo
  - **When** they are reviewed against the code rules of the instructions file
  - **Then** every source and test file cites at least one RQ ID in a comment
  - **And** every Tier M or L task has at least one test whose name follows Given/When/Then
  - **And** no string or numeric literal is duplicated inline
- **Dependencies**: RQ-DMO-003, RQ-DMO-005

### RQ-DMO-005: Process artifacts that led to the code
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The `process/` folder of the demo SHALL hold the artifacts that led to its code, following
  the templates of the instructions file: at least 3 features, 12 requirements, 3 ADRs with `DEC-` headings
  and a mermaid diagram, and 3 plans with tasks.
- **Rationale**: The process is demonstrated by its artifacts, not only by the code they produced.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** the `process/` folder of the demo
  - **When** its artifacts are counted and read
  - **Then** at least 3 features, 12 requirements, 3 ADRs and 3 plans exist
  - **And** each follows its template and a unique `<TYPE>-<TRI>-<NNN>` ID
- **Dependencies**: RQ-DMO-001

### RQ-DMO-006: The process mechanisms are showcased
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The demo's process artifacts SHALL exercise these mechanisms at least once: the four EARS
  types, Gherkin criteria, tasks of tier S, M and L with Verification and Assumptions filled, an ADR with
  alternatives considered, a session state file and a metrics log with one row per session.
- **Rationale**: A demonstration must show the capabilities of the process, not only a typical path.
- **Priority**: Should
- **Acceptance Criteria** (Gherkin):
  - **Given** the demo's `process/` folder
  - **When** it is searched for each mechanism
  - **Then** a requirement of each EARS type exists
  - **And** a task of each tier exists, the M and L ones with Verification and Assumptions filled
  - **And** `process/_sessionstate/METRICS_LOG.md` has one row per session branch
- **Dependencies**: RQ-DMO-005

### RQ-DMO-007: The index is produced by the skill
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The `process/INDEX.idx.md` of the demo SHALL be produced by the `agnos-index` skill at each
  task commit and SHALL NOT be written by hand.
- **Rationale**: The instructions reserve the index to the skill; the demo must follow that rule.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** the demo repository at its last commit
  - **When** the `agnos-index` script is run
  - **Then** it exits with code 0, reports no duplicate and leaves `INDEX.idx.md` unchanged
- **Dependencies**: RQ-DMO-005

### RQ-DMO-008: Traceability between process and code
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The demo SHALL be traceable end to end: every requirement SHALL be cited by at least one
  other artifact or code file, and every ID cited in code SHALL be defined.
- **Rationale**: Traceability is the main promise of the process, so the demo has to prove it.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** the demo repository at its last commit
  - **When** the `agnos-trace` skill is run on its `process/` folder and source folders
  - **Then** the report lists 0 undefined ID
  - **And** 0 uncovered Must requirement and 0 task without requirement
- **Dependencies**: RQ-DMO-004, RQ-DMO-005

### RQ-DMO-009: README declares the demo synthetic
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The README of the demo SHALL state that the history and the identities are simulated, and
  SHALL describe the scenario, the roles and identities, the timeline, how to filter the history by role,
  and how to run `agnos-index` and `agnos-trace`.
- **Rationale**: A reader must not take the simulated people and dates for real ones, and must be able to
  explore the demo alone.
- **Priority**: Should
- **Acceptance Criteria** (Gherkin):
  - **Given** the README of the demo
  - **When** it is read
  - **Then** its first section says the history is simulated
  - **And** it gives the command that lists the commits of one role
- **Dependencies**: RQ-DMO-001, RQ-DMO-011

### RQ-DMO-020: The generator is kept as the `agnos-demo` skill
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: This repository SHALL contain the generator of the demo as a skill named `agnos-demo`,
  canonical under `.github/skills/agnos-demo/` with an entry point under `.claude/skills/agnos-demo/`, with
  the sub-commands `build` (create or rebuild the demo from its scenario and content, using the toolkit of
  the current checkout of this repository) and `verify` (check the requirements of FTR-DMO-001 and
  FTR-DMO-002 on the demo).
- **Rationale**: The demo is the permanent reference to demonstrate and test AGNOS, so it must be updated
  whenever AGNOS evolves, by anyone who maintains it.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** a change made to a toolkit file of this repository
  - **When** `build` then `verify` are run through the skill
  - **Then** the demo is rebuilt with the changed toolkit file in its first commit
  - **And** `verify` reports one pass or fail line per requirement of FTR-DMO-001 and FTR-DMO-002
- **Dependencies**: RQ-DMO-001, RQ-DMO-002

---

### RQ-DMO-022: A user interface built on a design system
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The demo SHALL contain, as two simulated sessions of its history, a design system made with the
  `agnos-design-system` skill (its own requirements, ADR, plan and tokens file, session DSN) and a web interface of the
  product whose every visual value comes from those tokens (session WEB), designed by a `ux` identity, built from the
  scenario like the rest of the demo, so that the demo shows the MANDATORY DESIGN SYSTEM rule of AGNOS applied.
- **Rationale**: the design-system rule is part of AGNOS and had no example in the demo (owner request of 2026-10-24).
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** the demo rebuilt by `build`
  - **When** its process index and history are read
  - **Then** it holds FTR-DSN-001, ADR-DSN-001, PLAN-DSN-001, FTR-WEB-001, ADR-WEB-001 and PLAN-WEB-001, the UI tasks
    citing the design-system IDs
  - **And** a `ux` identity authors the design-system work, and the UI code holds no raw visual literal
  - **And** the client's tests pass
- **Dependencies**: RQ-DMO-010, RQ-DMO-011, RQ-DMO-012, RQ-DMO-004

---

## Non-Functional Requirements

### RQ-DMO-010: Creating the demo leaves the user's environment untouched
- **Category**: Non-Functional
- **NFR Type**: Security
- **EARS Type**: Unwanted-behavior
- **Statement**: IF the demo repository is created or rebuilt, THEN the operation SHALL NOT push anything,
  configure a remote, modify the global or system git configuration, or modify `agnos-lightweight-process`;
  the files of this repository changed to deliver the feature are only the `process/` artifacts of DMO and
  the `agnos-demo` skill folders.
- **Metric**: 0 remote in the demo; global git configuration unchanged; 0 modified file in this repository
  outside the DMO artifacts and the `agnos-demo` skill folders.
- **Measurement Method**: `git remote` in the demo; `git config --global --list` before and after;
  `git status` and `git diff --name-only` in this repository.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** the global git configuration saved before the creation
  - **When** the demo is created
  - **Then** `git remote` of the demo is empty
  - **And** the global configuration is identical
  - **And** this repository changed only under `process/` for the DMO artifacts and in the `agnos-demo`
    skill folders
- **Dependencies**: RQ-DMO-001

### RQ-DMO-021: Rebuilding is reproducible
- **Category**: Non-Functional
- **NFR Type**: Reliability
- **EARS Type**: Ubiquitous
- **Statement**: The `build` sub-command SHALL produce the same history each time it runs on the same
  toolkit: same authors, dates, messages, file contents and commit IDs.
- **Metric**: 2 consecutive builds give the same HEAD commit ID.
- **Measurement Method**: Run `build`, read `git rev-parse HEAD` in the demo, run `build` again, compare.
- **Priority**: Should
- **Acceptance Criteria** (Gherkin):
  - **Given** an unchanged checkout of this repository
  - **When** `build` is run twice
  - **Then** both runs end on the same HEAD commit ID
- **Dependencies**: RQ-DMO-020, RQ-DMO-013
