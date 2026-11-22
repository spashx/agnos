# FTR-TRC-013: Typed element links

## Overview
`agnos-graph` writes one `refs` edge per ID cited on the lines of an element, whatever the line: a requirement cited in a
task's `Requirement refs` and one named in its `Description` give the same link. This feature gives each citation of a
requirement, a decision, a task or a plan the link field of its element that holds it, such as `Dependencies`, or `text`
when it is cited outside those fields, so that a reader tells a declared link from a mention.

Source: the owner's request of 2026-11-22: typing applies to the links whose source is an RQ, a DEC, a TASK or a PLAN; the links
of features and ADRs stay as they are; the graph holds explicit links only: no link is removed, none is inferred.

Out of scope: the links whose source is a feature, an ADR or a section; `agnos-perf-center` (its page, coverage and
score); the decisions written before their template gained link fields, whose citations stay `text`.

## Stakeholders
- **Owner**: the repository owner (maintainer of AGNOS).
- **Consumers**: agents and tools reading `agnos-graph.json`; later, `agnos-perf-center`.

---

## Functional Requirements

### RQ-TRC-138: Link field of element citations
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The graph skill SHALL give each line proving a `refs` edge whose source is a requirement, a decision, a task or a plan the link field of the source's template holding that line, or `text` when no link field holds it.
- **Rationale**: a link declared in a dedicated field is a commitment of its author, a mention in a description is not, and today a reader cannot tell them apart.
- **Priority**: Must
- **Acceptance Criteria**: Given a task citing `RQ-ABC-001` in `- **Requirement refs**:` on line 5 and `RQ-ABC-002` in `- **Description**:` on line 4, When the graph is built, Then the proof of line 5 has field `Requirement refs` And the proof of line 4 has field `text`; Given an ADR citing `FTR-ABC-001` in its `## Context`, Then its link is kept And no field is given to it.
- **Dependencies**: RQ-TRC-129, RQ-TRC-130

### RQ-TRC-139: Link field list per element type
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The graph skill SHALL retain as link fields `Dependencies` for a requirement, `Requirement refs` and `Dependencies` for a decision, `Requirement refs`, `ADR refs` and `Dependencies` for a task, and `Requirement refs` and `ADR refs` for a plan, and SHALL give `text` to a citation in any other field.
- **Rationale**: fields such as `Statement`, `Rationale`, `Acceptance Criteria` or `Verification` cite IDs to explain, not to declare a link; a closed list follows the templates of the process.
- **Priority**: Must
- **Acceptance Criteria**: Given a requirement citing `RQ-ABC-002` in `- **Statement**:` and `RQ-ABC-003` in `- **Dependencies**:`, When the graph is built, Then their fields are `text` and `Dependencies`; Given a decision citing `DEC-ABC-001` in `- **Rationale**:`, Then its field is `text`; Given a requirement holding `- **ADR refs**:`, a field of tasks only, Then its citations are `text`; Given a plan citing `RQ-ABC-001` in `- **Requirement refs**:` under `## References` and `RQ-ABC-002` in its `## Overview`, Then their fields are `Requirement refs` and `text`.
- **Dependencies**: RQ-TRC-138, RQ-INI-022

### RQ-TRC-140: Wrapped field line extent
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The graph skill SHALL hold in a field its own line and the lines that follow it up to the next field line, the next heading or the end of the element.
- **Rationale**: an author wraps a long `Dependencies` or `Requirement refs` list over several lines, which belong to the same field.
- **Priority**: Must
- **Acceptance Criteria**: Given `- **Dependencies**: RQ-ABC-002,` on line 7 and `  RQ-ABC-003` on line 8 followed by `- **Assignee**: AI`, When the graph is built, Then both citations have field `Dependencies`.
- **Dependencies**: RQ-TRC-138

---

## Non-Functional Requirements

### RQ-TRC-141: Graph consumers unaffected by link fields
- **Category**: Non-Functional
- **NFR Type**: Maintainability
- **EARS Type**: Ubiquitous
- **Statement**: The graph skill SHALL write the link fields in a block of their own, leaving every other block of `agnos-graph.json` byte-identical to the one written without them.
- **Metric**: 0 byte of difference in every block but the new one, and in the perf center's data, before and after the change.
- **Measurement Method**: build the graph and the perf center's data of this repository and of the demo at the base commit and after the change, and compare.
- **Priority**: Must
- **Acceptance Criteria**: Given this repository and the demo, When the graph and the perf center's data are built before and after the change, Then every block but the new one is identical And the perf center's data is identical.
- **Dependencies**: RQ-TRC-129, RQ-TRC-130, RQ-TRC-137
