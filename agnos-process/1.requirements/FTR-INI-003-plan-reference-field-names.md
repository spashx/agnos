# FTR-INI-003: Plan reference field names

## Overview
The plan template names the fields of its `## References` section `Requirements` and `ADRs`, while the task template names
the same links `Requirement refs` and `ADR refs`. This feature gives the plan the task's names, so that one link field names
one kind of link whatever the element, and has `agnos-init` convert the plans of a project it updates, so that a project
initialised before keeps its plans readable by the tools that read those fields (FTR-TRC-013).

Source: the owner's request of 2026-11-22: the same names as the tasks, with a converter for the next release.

Out of scope: the `Requirements handed to another component` field of a plan, which keeps its name; the fields of the other
artifact types; any file outside `agnos-process/3.plan/`.

## Stakeholders
- **Owner**: the repository owner (maintainer of AGNOS).
- **Consumers**: authors of plans; `agnos-graph` (FTR-TRC-013); projects updated by `agnos-init`.

---

## Functional Requirements

### RQ-INI-022: Plan reference fields named as task fields
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The process file SHALL name the fields of the plan template's `## References` section `Requirement refs` and `ADR refs`.
- **Rationale**: a link field bearing one name in every template is read by one rule, by an author and by a tool alike.
- **Priority**: Must
- **Acceptance Criteria**: Given the process file, When its plan template is read, Then its `## References` section holds `- **Requirement refs**:` and `- **ADR refs**:` And no `- **Requirements**:` nor `- **ADRs**:` line.
- **Dependencies**: None

### RQ-INI-023: Plan reference field conversion
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN `agnos-init` runs on a project, the skill SHALL rename, in the `## References` section of every `PLAN-*.md` of its plan folder, a `- **Requirements**:` line to `- **Requirement refs**:` and a `- **ADRs**:` line to `- **ADR refs**:`, every other byte preserved, and SHALL report each file it changed as `converted <path>`.
- **Rationale**: a project initialised before the rename holds plans with the old names, which its author would otherwise convert by hand at the next release.
- **Priority**: Must
- **Acceptance Criteria**: Given a plan holding `- **Requirements**: RQ-ABC-001` and `- **ADRs**: ADR-ABC-001` under `## References`, in CRLF, When either script runs, Then both lines carry the new names And every other byte is unchanged And `converted agnos-process/3.plan/<file>` is reported; Given a `- **Requirements**:` line under a task of the same plan, Then it is unchanged; Given a converted project, When run again, Then nothing is written And no `converted` line is reported; Given a project in the legacy `process/` folder, When run, Then it is moved, then converted.
- **Dependencies**: RQ-INI-022, RQ-INI-002, RQ-PLG-038
