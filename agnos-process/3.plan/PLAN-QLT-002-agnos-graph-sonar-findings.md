# PLAN-QLT-002: Corrected agnos-graph scripts

## Overview
Corrects the 4 SonarQube findings VS Code reports on the scripts of `agnos-graph`, in one task, with no change of behaviour.

## References
- **Requirement refs**: RQ-QLT-011
- **ADR refs**: ADR-QLT-001 (DEC-QLT-007)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-QLT-008: Correct Sonar findings of agnos-graph scripts
- **Tier**: S
- **Status**: Done
- **Description**: In `history.py`, write `ID_RE` with `\d` (and `re.ASCII`) instead of `[0-9]` (python:S6353, 2 findings); in `graph.py`, keep each `# noqa: E402` alone on its line so SonarQube reads it, the traceability moving to a comment above (python:S7632, 2 findings).
- **Requirement refs**: RQ-QLT-011
- **ADR refs**: ADR-QLT-001 (DEC-QLT-007)
- **Acceptance Criteria**: Given both scripts, When their VS Code diagnostics are read, Then none is left, And both still parse.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: `re.ASCII` keeps `[0-9]`'s ASCII-only matching; the traceability comment of the two imports stays in `graph.py`, above them.
