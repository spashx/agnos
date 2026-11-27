# PLAN-FIX-001: Process consistency fixes

## Overview
Implements FTR-FIX-001: design-system dependencies of the UI requirements and the tier of TASK-DSY-002.

## References
- **Requirement refs**: RQ-FIX-001 to RQ-FIX-004
- **ADR refs**: ADR-FIX-001 (DEC-FIX-001, DEC-FIX-002)

---

## Tasks

### TASK-FIX-001: Design-system dependencies and TASK-DSY-002 tier
- **Tier**: M
- **Status**: Done
- **Description**: Add RQ-TRC-018 and ADR-TRC-002 to the Dependencies of 14 UI requirements of FTR-TRC-001
  and FTR-TRC-002, and re-tier TASK-DSY-002 from S to M with its Verification filled.
- **Requirement refs**: RQ-FIX-001, RQ-FIX-002, RQ-FIX-003
- **ADR refs**: ADR-FIX-001 (DEC-FIX-001, DEC-FIX-002)
- **Acceptance Criteria** (Gherkin):
  - **Given** the 14 UI requirements and TASK-DSY-002
  - **When** their documents are read
  - **Then** each requirement lists RQ-TRC-018 and ADR-TRC-002, TASK-DSY-002 is Tier M with tool output
  - **And** no file under `.github/skills/agnos-trace/` changed
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `git diff` of the two FTR files: 14 Dependencies lines now start with `RQ-TRC-018,
  ADR-TRC-002,`; PLAN-DSY-001 TASK-DSY-002 `Tier: M` with grep counts as Verification;
  `git diff --name-only` lists no path under `.github/skills/agnos-trace/`; `agnos-index`: exit 0, no
  duplicate.
- **Assumptions**: The 14 requirements are the ones judged UI by ADR-TRC-002 (RQ-TRC-011 to RQ-TRC-016)
  and by reading (the others). No unit test: documentation only (`unit_tests=false`).

### TASK-FIX-002: Re-tier rule for a task whose scope grows
- **Tier**: S
- **Status**: Done
- **Description**: Add the re-tier rule to TASK TIERS (recursive self-improvement, iteration 1/1), and record the owner's
  lowering of the instructions file's line budget from 800 to 400.
- **Requirement refs**: RQ-FIX-004
- **ADR refs**: None
- **Acceptance Criteria** (Gherkin):
  - **Given** the instructions file
  - **When** it is read
  - **Then** TASK TIERS holds the rule and the file is within 400 lines
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: FTR-FIX-001 hosts the rule, being the feature of process corrections; the owner's "ajoute" covers the
  pending budget change and the session's metrics row in this commit.
