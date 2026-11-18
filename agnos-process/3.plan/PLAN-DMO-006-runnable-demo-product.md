# PLAN-DMO-006: Runnable demo product

## Overview
Make the demo's product run from its README: `verify` starts the service, the web interface and the command-line tool
as the README says, the service gets its entry point and a rooms file in the demo's CLI session, and the demo, its
import and the website are rebuilt. Owner request of 2026-11-18, before the 4.0.0 release.

## References
- **Requirements**: RQ-DMO-027, RQ-DMO-003, RQ-DMO-008, RQ-DMO-009, RQ-DMO-021, RQ-DMO-022
- **ADRs**: ADR-DMO-001

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-DMO-021: Check demo product run in verify
- **Tier**: M
- **Status**: Done
- **Description**: Add to `verify.ps1` the check of RQ-DMO-027: it starts the service and the web interface with the README's commands, reads the page and runs the command-line tool's `rooms`, then stops them.
- **Requirement refs**: RQ-DMO-027, RQ-DMO-020
- **ADR refs**: ADR-DMO-001 (DEC-DMO-005)
- **Acceptance Criteria** (Gherkin):
  - **Given** the demo built before this plan, whose service has no entry point
  - **When** `verify` runs
  - **Then** it prints `FAIL RQ-DMO-027` with the reason
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `verify.ps1 -SkipRebuild` on the demo `f2943d0`: `FAIL RQ-DMO-027 README commands missing: cd service && python -m roombook | cd client && node src/cli.ts rooms; run: no room in service/rooms.json; service does not answer http://127.0.0.1:8080/rooms (exited: True)`; `27 passed, 1 failed`. No test skipped.
- **Assumptions**: None

### TASK-DMO-022: Add service entry point to demo
- **Tier**: M
- **Status**: Not Started
- **Description**: In the demo's content and scenario, add RQ-CLI-006 and TASK-CLI-006 to its CLI session, the service's entry point `python -m roombook` reading `service/rooms.json`, its tests written first, and the README commands of the service and the command-line tool.
- **Requirement refs**: RQ-DMO-027, RQ-DMO-003, RQ-DMO-008, RQ-DMO-009
- **ADR refs**: ADR-DMO-001 (DEC-DMO-002, DEC-DMO-004)
- **Acceptance Criteria** (Gherkin):
  - **Given** the content of the service
  - **When** its tests run
  - **Then** the entry point's tests pass with the others
  - **Given** the scenario
  - **When** it is read
  - **Then** the test commit of TASK-CLI-006 precedes its code commit, both in the CLI session before its merge
- **Dependencies**: TASK-DMO-021
- **Assignee**: AI
- **Verification**: Not yet run
- **Assumptions**: The rooms come from a versioned JSON file; the service listens on 127.0.0.1:8080, the client's default.

### TASK-DMO-023: Rebuild demo with product run
- **Tier**: S
- **Status**: Not Started
- **Description**: Run `build -Verify`, import the demo into `../agnos-demo` without push, rebuild the website and commit it there locally.
- **Requirement refs**: RQ-DMO-027, RQ-DMO-021
- **ADR refs**: ADR-DMO-001
- **Acceptance Criteria** (Gherkin):
  - **Given** TASK-DMO-022 done
  - **When** `build -Verify` runs
  - **Then** every requirement prints PASS And the exit code is 0
- **Dependencies**: TASK-DMO-022
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: None
