# PLAN-FIX-002: Linux proof of version 4.0.0

## Overview
Records the real run of plugin 4.0.0 on Linux and corrects the statements that said Linux was simulated only.

## References
- **Requirements**: RQ-PLG-008, RQ-PLG-009, RQ-INI-013
- **ADRs**: ADR-INI-002 (Consequences only; no DEC amended)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-FIX-003: Record real Linux run
- **Tier**: M
- **Status**: Done
- **Description**: Record the real run on Linux Mint of plugin 4.0.0, then correct the Consequences of ADR-INI-002 and the Linux
  statement of COMPATIBILITY.md. The dated records of TASK-INI-006, PLAN-INI-001 and PLAN-PLG-005 stay unchanged.
- **Requirement refs**: RQ-PLG-008, RQ-PLG-009, RQ-INI-013
- **ADR refs**: ADR-INI-002
- **Acceptance Criteria** (Gherkin):
  - **Given** ADR-INI-002, **When** its Consequences are read, **Then** Linux is proven by a real run and macOS by simulation only
  - **Given** COMPATIBILITY.md, **When** read, **Then** it names Linux Mint, the VS Code extensions and plugin 4.0.0, and macOS stays not tested
  - **Given** the dated records of TASK-INI-006, PLAN-INI-001 and PLAN-PLG-005, **When** read, **Then** they are unchanged
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: Documentation only; no test run, at the owner's request. The run itself was reported by the owner, not observed
  in this session.
- **Assumptions**: the complete session covers `agnos-session`, `agnos-index` and `agnos-git-workflow`; the delivered suites, the
  CLIs and the `agnos-perf-center` page are not declared tested on Linux. DEC-INI-010 still says only Windows PowerShell 5.1 runs
  for real, left unchanged since amending a DEC is Tier L.
