# PLAN-DMO-001: Demo repository with a simulated two-month history

## Overview
Builds `agnos-lightweight-process.demo`: the generator, the content (process documents, Python and
TypeScript code, README and state files), the scenario of about 55 commits, then the repository and its
verification. Session variable `unit_tests=false`: no unit test is written for the generator; the demo's
own tests are deliverable content (RQ-DMO-004). The generator is the maintainer skill `agnos-demo`
(`.github/skills/agnos-demo/`: `scripts/`, `assets/content/`, `assets/scenario.json`), so the demo can be
rebuilt and verified again when AGNOS evolves.

## References
- **Requirements**: RQ-DMO-001 to RQ-DMO-021
- **ADRs**: ADR-DMO-001 (DEC-DMO-001 to DEC-DMO-006)

---

## Tasks

### TASK-DMO-001: Replay engine
- **Tier**: M
- **Status**: Done
- **Description**: Write the PowerShell 5.1 script `.github/skills/agnos-demo/scripts/replay.ps1` that
  creates a repository and replays scenario steps (add files, close a task, refresh the index, branch,
  merge), with identity and dates from environment variables, and the date and time of each commit fixed in the scenario.
- **Requirement refs**: RQ-DMO-010, RQ-DMO-013, RQ-DMO-018, RQ-DMO-007, RQ-DMO-021
- **ADR refs**: ADR-DMO-001 (DEC-DMO-002, DEC-DMO-006)
- **Acceptance Criteria** (Gherkin):
  - **Given** a scenario of three steps in a temporary directory
  - **When** the engine replays it
  - **Then** the repository has three commits with the given identities and dates, author equal to committer
  - **And** `git remote` is empty and `git config --global --list` is unchanged
  - **And** the engine refuses to rebuild a directory it did not create
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: Toy scenario of 3 steps replayed to a temp dir: 3 commits, identities and dates as given, author = committer; `git remote` empty; `git config --global --list` identical before/after; second run on the same dir gives the same HEAD; a dir without the marker is refused (exit 1). Real scenario: 57 commits in 27 s.
- **Assumptions**: Stored in the skill folder, changed from the session scratchpad at the user's request;
  PowerShell only (`session.platform=windows`), no bash version; no unit test (`unit_tests=false`),
  checked by the toy scenario above.

### TASK-DMO-002: Toolkit baseline step
- **Tier**: M
- **Status**: Done
- **Description**: Build the root-commit content: the tracked files of this repository outside `process/`
  and outside the `agnos-demo` skill folders, with the README replaced by the demo's.
- **Requirement refs**: RQ-DMO-002, RQ-DMO-020
- **ADR refs**: ADR-DMO-001 (DEC-DMO-002, DEC-DMO-006)
- **Acceptance Criteria** (Gherkin):
  - **Given** the tracked files of this repository
  - **When** the baseline content is built
  - **Then** every toolkit file is present and nothing from `process/` or `agnos-demo` is
  - **And** no TRC, IDX, DSY, AGT, FIX or DMO ID is found under the demo's `process/`
- **Dependencies**: TASK-DMO-001
- **Assignee**: AI
- **Verification**: `verify.ps1` RQ-DMO-002: PASS, 0 toolkit file missing, 0 TRC/IDX/DSY/AGT/FIX/DMO ID under `process/`, 0 `agnos-demo` file in the demo.
- **Assumptions**: The toolkit is the state of `feature/DMO` HEAD; the `process/_sessionstate/` folder
  comes from the demo's own state files (TASK-DMO-006).

### TASK-DMO-003: Process documents of the three sessions
- **Tier**: M
- **Status**: Done
- **Description**: Write, under `assets/content/process/` of the skill, the demo's process artifacts in
  final form: FTR-BKG-001, FTR-NTF-001,
  FTR-CLI-001 (about 14 requirements covering the four EARS types), ADR-BKG-001 (Superseded),
  ADR-BKG-002, ADR-NTF-001, ADR-CLI-001, PLAN-BKG-001, PLAN-NTF-001, PLAN-CLI-001 with tasks of tier S, M
  and L, Verification and Assumptions filled.
- **Requirement refs**: RQ-DMO-005, RQ-DMO-006, RQ-DMO-008
- **ADR refs**: ADR-DMO-001 (DEC-DMO-001, DEC-DMO-003)
- **Acceptance Criteria** (Gherkin):
  - **Given** the written documents
  - **When** they are counted and read against the templates
  - **Then** at least 3 features, 12 requirements, 3 ADRs with DEC headings and a diagram, 3 plans exist
  - **And** a requirement of each EARS type and a task of each tier exist
  - **And** no ID is duplicated and every cited ID is defined
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `verify.ps1` RQ-DMO-005/006/017: PASS, 4 features, 16 requirements, 5 ADRs (all with DEC and diagram), 4 plans, 0 duplicate ID; 4 EARS types and tiers S, M, L present; first run found 2 citations before definition (FTR-BKG-002 in FTR-BKG-001, RQ-BKG-007 in two docstrings), fixed, re-run PASS.
- **Assumptions**: The demo's own trigrams are BKG, NTF, CLI (DEC-DMO-001); the plan task statuses are
  written in their final state, and the engine replays them one task at a time.

### TASK-DMO-004: Python service and tests
- **Tier**: M
- **Status**: Done
- **Description**: Have a Haiku sub-agent generate, under `assets/content/` of the skill, the Python
  booking and notification code and its Gherkin-named tests from a written contract, then review it.
- **Requirement refs**: RQ-DMO-003, RQ-DMO-004, RQ-DMO-008
- **ADR refs**: ADR-DMO-001 (DEC-DMO-001, DEC-DMO-004)
- **Acceptance Criteria** (Gherkin):
  - **Given** the contract and the process documents
  - **When** the generated files are reviewed
  - **Then** there are at least 4 source files and a manifest
  - **And** every source and test file cites at least one RQ ID of the demo, all defined
  - **And** each function of a Tier M or L task has a Given/When/Then-named test
  - **And** no duplicated inline literal is found
- **Dependencies**: TASK-DMO-003
- **Assignee**: AI
- **Verification**: `python -m unittest discover -s tests -t .` in `service/` of the built demo: Ran 93 tests, OK; `verify.ps1` RQ-DMO-003/004: PASS (23 sources, all cite an RQ, tests Gherkin-named, no repeated literal).
- **Assumptions**: Delegation to Haiku authorised by the user; the code is not required to compile.

### TASK-DMO-005: TypeScript client, command-line tool and tests
- **Tier**: M
- **Status**: Done
- **Description**: Same as TASK-DMO-004 for the TypeScript API client and command-line tool.
- **Requirement refs**: RQ-DMO-003, RQ-DMO-004, RQ-DMO-008
- **ADR refs**: ADR-DMO-001 (DEC-DMO-001, DEC-DMO-004)
- **Acceptance Criteria** (Gherkin):
  - **Given** the contract and the process documents
  - **When** the generated files are reviewed
  - **Then** there are at least 4 source files and a manifest
  - **And** every source and test file cites at least one RQ ID of the demo, all defined
  - **And** each function of a Tier M or L task has a Given/When/Then-named test
- **Dependencies**: TASK-DMO-003
- **Assignee**: AI
- **Verification**: `node --test "tests/*.test.ts"` in `client/` of the built demo: 24 pass, 0 fail; `verify.ps1` RQ-DMO-003/004: PASS (6 sources).
- **Assumptions**: Same as TASK-DMO-004.

### TASK-DMO-006: README, working calendar and state files
- **Tier**: M
- **Status**: Done
- **Description**: Write, under `assets/content/` of the skill, the demo's README (simulation notice,
  scenario, roles, timeline, filter and tool commands), `docs/WORKING_CALENDAR.md` with the two fictitious
  holidays, `session.yaml` and `METRICS_LOG.md` with one row per session.
- **Requirement refs**: RQ-DMO-009, RQ-DMO-015, RQ-DMO-006
- **ADR refs**: ADR-DMO-001 (DEC-DMO-003)
- **Acceptance Criteria** (Gherkin):
  - **Given** the written files
  - **When** the README is read
  - **Then** its first section says the history is simulated
  - **And** it gives the command listing the commits of one role
  - **And** the calendar declares 2026-09-14 and 2026-10-12, and the log has 3 session rows
- **Dependencies**: TASK-DMO-003
- **Assignee**: AI
- **Verification**: `verify.ps1` RQ-DMO-006/009/015: PASS, README opens with the simulation notice and gives `git log --author=-qa`, calendar declares 2026-09-14 and 2026-10-12, METRICS_LOG has 3 rows for 3 sessions.
- **Assumptions**: Session end dates 2026-09-18, 2026-10-02, 2026-10-23 for the log rows; the demo's
  `session.yaml` has `unit_tests: true`, `platform: windows`.

### TASK-DMO-007: Cast, schedule and scenario
- **Tier**: M
- **Status**: Done
- **Description**: Write `assets/scenario.json` of the skill: the six identities, the date, hour,
  identity, branch and files of each of at least 55 commits, in an order that follows the process.
- **Requirement refs**: RQ-DMO-011, RQ-DMO-012, RQ-DMO-014, RQ-DMO-015, RQ-DMO-016, RQ-DMO-017,
  RQ-DMO-018
- **ADR refs**: ADR-DMO-001 (DEC-DMO-003)
- **Acceptance Criteria** (Gherkin):
  - **Given** the scenario file
  - **When** it is checked without building the repository
  - **Then** every date is a working day inside the period, not a declared holiday, between 09:00 and 18:00
  - **And** every identity is active on 5 or more days and on at most 80% of working days
  - **And** every artifact is committed by the matching role, tests before code, definitions before citations
- **Dependencies**: TASK-DMO-002, TASK-DMO-003, TASK-DMO-004, TASK-DMO-005, TASK-DMO-006
- **Assignee**: AI
- **Verification**: `verify.ps1` RQ-DMO-011/012/013/014/016/018: PASS, 6 identities, 57 commits over 60 days, active days 6 to 13 of 43 working days, 0 commit outside 09:00-18:00 or on a weekend/holiday, tests precede code for every M/L task, 3 session branches merged.
- **Assumptions**: Hours and minutes are written in the scenario (no random draw) so that rebuilds are identical; the period is 2026-08-24 to 2026-10-23.

### TASK-DMO-008: Verification script
- **Tier**: M
- **Status**: Done
- **Description**: Write `scripts/verify.ps1` of the skill, which checks each Gherkin criterion of
  RQ-DMO-001 to RQ-DMO-021 on the built demo and reports one pass or fail line per requirement.
- **Requirement refs**: RQ-DMO-001, RQ-DMO-019, RQ-DMO-008, RQ-DMO-020
- **ADR refs**: ADR-DMO-001 (DEC-DMO-005, DEC-DMO-006)
- **Acceptance Criteria** (Gherkin):
  - **Given** a deliberately wrong toy repository (a Saturday commit, a name without role)
  - **When** the script runs on it
  - **Then** it reports the failing requirements and exits with a non-zero code
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `verify.ps1` on the built demo: 21 passed, 0 failed (second run after the fixes); on a deliberately wrong toy repo (Saturday 23:30 commit by `bob`): 14 FAIL lines incl. RQ-DMO-011, 015, 016, exit 1. First run exposed a vacuous RQ-DMO-017 (argument precedence bug), fixed.
- **Assumptions**: None

### TASK-DMO-009: Skill entry points and sub-commands
- **Tier**: L
- **Status**: Done
- **Description**: Package the engine and the verification as the skill `agnos-demo`: canonical
  `SKILL.md` (sub-commands `build` and `verify`, evolution procedure) under `.github/skills/agnos-demo/`,
  entry point under `.claude/skills/agnos-demo/`; the skill is not listed in CLAUDE.md or AGENTS.md.
- **Requirement refs**: RQ-DMO-020, RQ-DMO-010
- **ADR refs**: ADR-DMO-001 (DEC-DMO-006)
- **Acceptance Criteria** (Gherkin):
  - **Given** the skill folders
  - **When** Claude Code lists its skills and `build` and `verify` are described
  - **Then** `agnos-demo` is discovered, its entry point points to the canonical file
  - **And** neither CLAUDE.md nor AGENTS.md mentions it
- **Dependencies**: TASK-DMO-001, TASK-DMO-008
- **Assignee**: AI
- **Verification**: Skill listed by Claude Code (`agnos-demo`); `.claude/skills/agnos-demo/SKILL.md` points to the canonical file; `verify.ps1` RQ-DMO-020: PASS; `git grep agnos-demo CLAUDE.md AGENTS.md`: no match.
- **Assumptions**: Tier L as a new set of sub-commands, a public interface for maintainers; follows the
  layout of the other skills.

### TASK-DMO-010: Build and verify the demo repository
- **Tier**: L
- **Status**: Done
- **Description**: Run the skill's `build` on the scenario to create `agnos-lightweight-process.demo`,
  then `verify`, `agnos-index` and `agnos-trace`; fix the scenario or the content and rebuild until
  every check passes; build a second time to check reproducibility.
- **Requirement refs**: RQ-DMO-001 to RQ-DMO-021
- **ADR refs**: ADR-DMO-001 (DEC-DMO-002, DEC-DMO-005, DEC-DMO-006)
- **Acceptance Criteria** (Gherkin):
  - **Given** the skill, the scenario and the content
  - **When** the demo is built twice and the verification run
  - **Then** all 21 requirements report pass, `git fsck --strict` exits 0
  - **And** both builds end on the same HEAD commit ID
  - **And** `agnos-trace` reports 0 undefined ID and 0 uncovered Must requirement
  - **And** this repository changed only in the DMO artifacts and the `agnos-demo` skill folders, and
    nothing was pushed
- **Dependencies**: TASK-DMO-001, TASK-DMO-007, TASK-DMO-008, TASK-DMO-009
- **Assignee**: AI
- **Verification**: `build.ps1 -Verify`: 57 commits, global git configuration unchanged, `verify.ps1`: 21 passed, 0 failed; RQ-DMO-021 second build same HEAD (b8257e7); `git fsck --strict` exit 0; `agnos-trace`: uncovered 0, task-no-rq 0, undefined 0; no push, no remote.
- **Assumptions**: The demo directory is created next to this repository, at the parent of its root.
