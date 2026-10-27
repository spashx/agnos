# PLAN-TRC-008: Delivery Tab

## Overview
A correction of the history's summary line first, then the Delivery tab of the traceability page: the tasks delivered
(their status turned to Done in git) counted by period, tier and identity, weighted by tier and divided by the active
days, compared between two periods chosen within the history read. The tasks of the Delivery tab are added once
FTR-TRC-004 and ADR-TRC-009 are approved.

## References
- **Requirements**: RQ-HST-006 (TASK-TRC-055); FTR-TRC-004 (to be written)
- **ADRs**: ADR-HST-001 (DEC-HST-004); ADR-TRC-009 (to be written)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-TRC-055: One human, one agent, one commit in the history's summary line
- **Tier**: S
- **Status**: Done
- **Description**: The generator's last line wrote "1 humans" and "1 agents"; each count of the history's summary is now
  followed by its noun in the singular for one, in the plural otherwise.
- **Requirement refs**: RQ-HST-006
- **ADR refs**: ADR-HST-001 (DEC-HST-004)
- **Acceptance Criteria**: Given a history with 2 commits, 2 humans and 1 agent, When the generator ends, Then its last
  line holds "history: 2 commits, 2 humans, 1 agent".
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: N/A (Tier S). `python -m unittest discover -s tests` (skill folder): 254 tests, OK, 2 skipped.
- **Assumptions**: the expected line of `test_history.py` changed to "1 agent", as the corrected behaviour.
