# PLAN-INI-002: An Order to Read the Instructions

## Overview
Replace the `@` import of the `CLAUDE.md` block by the order the `AGENTS.md` block already gives, rebuild the demo, and check on a real session that the order is followed. Everything stays local.

## References
- **Requirements**: RQ-INI-010; amended: RQ-INI-006
- **ADRs**: ADR-INI-001 (DEC-INI-007); amended: DEC-INI-003

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-INI-004: The CLAUDE.md block orders the agent to read the instructions
- **Tier**: L
- **Status**: In Progress
- **Description**: Change the tests first, then the `CLAUDE.md` template, `README.md` and the changelog, rebuild the demo, and have the owner run a session to check the order is followed.
- **Requirement refs**: RQ-INI-006, RQ-INI-010
- **ADR refs**: ADR-INI-001 (DEC-INI-003, DEC-INI-007)
- **Acceptance Criteria**: Given the test suite, When it runs both scripts, Then the criteria of RQ-INI-006 and RQ-INI-010 hold; Given the demo, When `agnos-meta-demo build -Verify` runs, Then every check passes; Given a new session in the demo, When it starts, Then its first action reads the instructions file.
- **Dependencies**: TASK-INI-001
- **Assignee**: AI
- **Verification**: `agnos-init/tests`: 15 OK, the new RQ-INI-010 test failing before the template changed, both scripts run. The RQ-INI-006 test no longer expects the `@` import, as amended. `agnos-meta-demo/tests`: 7 OK. `build -Verify`: 23 passed, 0 failed, HEAD d75e079, block read in the demo's `CLAUDE.md`. Session check: pending, to be run by the owner.
- **Assumptions**: the demo's former history is saved in a bundle outside the repositories before the rebuild; the plugin's path stays to design (DEC-INI-005), no change for it now.
