# PLAN-INI-002: An Order to Read the Instructions

## Overview
Replace the `@` import of the `CLAUDE.md` block by the order the `AGENTS.md` block already gives, leave starting a session to the user, rebuild the demo, and check on real sessions that this is followed. Everything stays local.

## References
- **Requirements**: RQ-INI-010; amended: RQ-INI-005, RQ-INI-006
- **ADRs**: ADR-INI-001 (DEC-INI-007); amended: DEC-INI-003

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-INI-004: The CLAUDE.md block orders the agent to read the instructions
- **Tier**: L
- **Status**: Done
- **Description**: Change the tests first, then both templates, the instructions file, `AGENTS.md`, `README.md` and the changelog, rebuild the demo, and have the owner run sessions to check the order is followed. Scope grown with the owner's approval on 2026-10-31: START SESSION runs only when the user asks.
- **Requirement refs**: RQ-INI-006, RQ-INI-010
- **ADR refs**: ADR-INI-001 (DEC-INI-003, DEC-INI-007)
- **Acceptance Criteria**: Given the test suite, When it runs both scripts, Then the criteria of RQ-INI-006 and RQ-INI-010 hold; Given the demo, When `agnos-meta-demo build -Verify` runs, Then every check passes; Given a new session in the demo, When it starts, Then its first action reads the instructions file; Given a read-only request, When it is answered, Then the agent has written nothing; Given the request to start a session, When it is received, Then the agent runs START SESSION in full.
- **Dependencies**: TASK-INI-001
- **Assignee**: AI
- **Verification**: `agnos-init/tests`: 15 OK, the new RQ-INI-010 test failing before the template changed, both scripts run. The RQ-INI-006 test no longer expects the `@` import, as amended. `agnos-meta-demo/tests`: 7 OK. `build -Verify`: 23 passed, 0 failed, HEAD 17ede12 after START SESSION left to the user, new sentence read in both demo blocks. The `agnos-init` test failed before the templates changed, then 15 OK. Instructions file: 295 non-empty lines, within 400. First session (log e704095a, former block): first action read the instructions, START SESSION not run. Read-only request (log 76ce30d6, final block): first action read the instructions, then only reads, answered. Request to start a session (log f36020f7, final block): first action read the instructions, then platform, unit tests question, `session.yaml`, `agnos-index` exit 0, `validate-ids` exit 0, `feature/CTL` created, conflict check reported. Demo rebuilt after: 23 passed, 0 failed, on `main`. Before commit: `agnos-meta-docs-sync` 14 OK, `agnos-meta-qa` 32 OK, `agnos-index` all checks passed, `agnos-perf-center` 361 run, OK, 3 skipped; a first run of that suite gave 1 error, not captured, while the demo rebuilt and another run went on in a worktree; it did not recur alone.
- **Assumptions**: the demo's former history is saved in a bundle outside the repositories before the rebuild; the plugin's path stays to design (DEC-INI-005), no change for it now.

### TASK-INI-005: A readme in each process folder
- **Tier**: M
- **Status**: Done
- **Description**: `agnos-init` writes in each `process/` folder it creates a `readme.md` saying what the folder holds, instead of a `.gitkeep`, from a template of each folder.
- **Requirement refs**: RQ-INI-005, RQ-MTA-011
- **ADR refs**: ADR-INI-001
- **Acceptance Criteria**: Given the test suite, When it runs both scripts, Then the criteria of RQ-INI-005 as amended hold; Given the demo, When `agnos-meta-demo build -Verify` runs, Then every check passes; Given the release rehearsal, Then it compares the `readme.md` files and exits 0.
- **Dependencies**: TASK-MTA-008
- **Assignee**: AI
- **Verification**: `agnos-init/tests`: 16 OK, both scripts run, the readme test failing before the scripts changed. `agnos-meta-release/tests`: 41 OK, the test of the compared files failing first; `agnos-meta-demo/tests`: 12 OK. `build -Verify`: 23 passed, 0 failed, HEAD c3efb8a, status clean, the first commit touching `process/` holds the 4 `readme.md`, no `.gitkeep`. Rehearsal on a throwaway clone of this task's files: 62 files, 1,104 IDs removed, both checks true, exit 0, no file of `process/` delivered.
- **Assumptions**: a template per folder, flat in `assets/templates/`, so that its line-ending rule applies; a project already initialised does not receive the files, its folders belonging to it; `agnos-perf-center`'s suite not re-run, as none of its files changed since its last pass.
