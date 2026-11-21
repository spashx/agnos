# PLAN-TRC-021: Call graph measurement

## Overview
Make the call graph's weaknesses measurable before improving its resolution: score the files tree-sitter cannot parse, and
count the unresolved calls by cause (recommendations R1 and R2 of `insights/callgraph-operational-analysis.md`, owner choice of
2026-11-21).

## References
- **Requirements**: RQ-TRC-122, RQ-TRC-123, RQ-TRC-030, RQ-TRC-035, RQ-PLG-024
- **ADRs**: ADR-TRC-020 (DEC-TRC-067, DEC-TRC-068), ADR-TRC-004 (DEC-TRC-015), ADR-TRC-008 (DEC-TRC-032)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-TRC-109: Specify call graph measurement
- **Tier**: M
- **Status**: Done
- **Description**: Write RQ-TRC-122 and RQ-TRC-123 in FTR-TRC-002, ADR-TRC-020 and this plan.
- **Requirement refs**: RQ-TRC-122, RQ-TRC-123
- **ADR refs**: ADR-TRC-020
- **Acceptance Criteria** (Gherkin): Given the owner's scope, When the artifacts are written, Then the index lists RQ-TRC-122,
  RQ-TRC-123, ADR-TRC-020, DEC-TRC-067, DEC-TRC-068 and TASK-TRC-109 to TASK-TRC-111 with no duplicate.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `build-index.ps1`: exit 0, 992 entries, 157 documents; the index lists RQ-TRC-122, RQ-TRC-123, ADR-TRC-020,
  DEC-TRC-067, DEC-TRC-068, TASK-TRC-109 to TASK-TRC-111; no duplicate reported.
- **Assumptions**: the causes `unnamed` and `top-level` stay outside the external total, as they were never counted there; the
  check's population is the files the call graph read, not every scanned file.

### TASK-TRC-110: Score files that fail to parse
- **Tier**: L
- **Status**: Not Started
- **Description**: Record `has_error` files in `callgraph.py`, add the `files-parsed` check to `scoring.json` and its population
  to `scorecard.py`, an "Unparsed files" figure to the page's call graph card, one broken fixture per language, documentation.
- **Requirement refs**: RQ-TRC-122, RQ-PLG-024
- **ADR refs**: ADR-TRC-020 (DEC-TRC-067), ADR-TRC-008 (DEC-TRC-032)
- **Acceptance Criteria** (Gherkin): the acceptance criteria of RQ-TRC-122; Given the skill's suite, Then all pass.
- **Dependencies**: TASK-TRC-109
- **Assignee**: AI
- **Verification**: pending
- **Assumptions**: pending

### TASK-TRC-111: Count unresolved calls by cause
- **Tier**: M
- **Status**: Not Started
- **Description**: Classify unresolved calls in `callgraph.py` into `library`, `constructor`, `cross-language`, `unnamed`,
  `top-level`, expose them in `callGraph.counts.unresolved`, show them in the "External calls" tooltip, documentation.
- **Requirement refs**: RQ-TRC-123, RQ-TRC-030
- **ADR refs**: ADR-TRC-020 (DEC-TRC-068), ADR-TRC-004 (DEC-TRC-015)
- **Acceptance Criteria** (Gherkin): the acceptance criteria of RQ-TRC-123; Given the skill's suite, Then all pass.
- **Dependencies**: TASK-TRC-109
- **Assignee**: AI
- **Verification**: pending
- **Assumptions**: pending
