# FTR-FIX-001: Process consistency fixes

## Overview
The process artifacts inherited from the project where the agnos-trace feature was first built contain
two inconsistencies with the AGNOS instructions: user-interface requirements that do not list the
design-system artifacts they depend on, and a task whose tier does not match its size. This feature
corrects them without changing the traceability page itself.

## Stakeholders
- **Owner**: AGNOS process maintainer (this repository)
- **Consumers**: AI agents and reviewers reading the process; the agnos-trace matrix

---

## Functional Requirements

### RQ-FIX-001: UI requirements list the design-system artifacts
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: Every GUI, UX or user-workflow requirement of FTR-TRC-001 and FTR-TRC-002 SHALL list
  RQ-TRC-018 and ADR-TRC-002, the design system of the traceability page, in its **Dependencies** field.
- **Rationale**: The instructions require UI requirements to list the design-system IDs, so that a UI
  artifact never bypasses the design system.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** the requirements RQ-TRC-011 to RQ-TRC-016, RQ-TRC-045, RQ-TRC-046, RQ-TRC-049,
    RQ-TRC-033, RQ-TRC-034, RQ-TRC-041, RQ-TRC-047 and RQ-TRC-048
  - **When** their Dependencies fields are read
  - **Then** each contains RQ-TRC-018 and ADR-TRC-002
- **Dependencies**: RQ-TRC-018, ADR-TRC-002

### RQ-FIX-002: A task's tier matches the size of its edits
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: IF a task edits more than 5 lines, THEN its plan SHALL tag it Tier M or L, never S, and
  its Verification field SHALL hold tool output instead of "N/A (Tier S)".
- **Rationale**: Tier S is defined by edits of 5 lines or fewer; TASK-DSY-002 rewrites a README.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** TASK-DSY-002, which rewrites README.md
  - **When** its tier and Verification are read
  - **Then** the tier is M and the Verification cites tool output
- **Dependencies**: None

---

### RQ-FIX-004: A task whose scope grows is re-tiered
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN a task's scope grows or it comes to amend an ADR decision, the process instructions SHALL require
  re-tiering it and getting approval before continuing, Tier L at least when it amends a decision.
- **Rationale**: TASK-TRC-068 grew to amend DEC-HST-005 and was re-tiered only by judgment.
- **Priority**: Should
- **Acceptance Criteria** (Gherkin):
  - **Given** the instructions file
  - **When** its TASK TIERS section is read
  - **Then** it states the rule, and the file stays within its line budget
- **Dependencies**: None

---

## Non-Functional Requirements

### RQ-FIX-003: The traceability page is unchanged
- **Category**: Non-Functional
- **NFR Type**: Maintainability
- **EARS Type**: Ubiquitous
- **Statement**: The corrections of this feature SHALL NOT modify the traceability page's design tokens,
  style sheet, scripts or generated appearance.
- **Metric**: 0 modified file under `.github/skills/agnos-trace/`.
- **Measurement Method**: `git diff --name-only` of the session branch against its base lists no path
  under `.github/skills/agnos-trace/`.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** the session branch of this feature
  - **When** its changed files are listed
  - **Then** none lies under `.github/skills/agnos-trace/`
- **Dependencies**: RQ-FIX-001
