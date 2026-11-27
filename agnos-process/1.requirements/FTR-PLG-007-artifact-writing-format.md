# FTR-PLG-007: Artifact writing format

## Overview
The process states how every artifact is written: a title format, a decision statement with its rationale, and IDs held as
plain text inside `agnos-process/`. The demo, which shows the process applied, follows these rules, and so does the website
that quotes it.

Source: the owner's edit of the instructions file in commit `197f33c` (2026-11-11), written without requirement IDs; this
feature records it. On 2026-11-11 the owner chose a range of 2 to 8 words, since the rule's own examples ("User
authentication") have 2, and chose to retitle the demo's artifacts that join two concerns rather than split them.

Out of scope: retitling this repository's own artifacts.

## Stakeholders
- **Owner**: the repository owner (maintainer of AGNOS).
- **Consumers**: developers using the AGNOS plugin and their agents; readers of the demo and of the website.

---

## Functional Requirements

### RQ-PLG-039: Artifact title format
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The process SHALL require every artifact title to hold 2 to 8 words, as a noun phrase, except a TASK title, which is one base-form action verb and its object.
- **Rationale**: the rule stated 3 to 8 words while its own examples have 2; the owner chose the examples.
- **Priority**: Must
- **Acceptance Criteria**: Given the instructions file, When MANDATORY TITLE FORMAT is read, Then it states 2-8 words And its examples comply; Given the demo, Then every FTR, RQ, ADR, DEC, PLAN and TASK title complies; Given the instructions file, Then it stays within 400 lines.
- **Dependencies**: RQ-PLG-019, RQ-DMO-005

### RQ-PLG-040: Decision statement with rationale
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The process SHALL require every DEC to hold a **Statement** of one sentence in active voice, a **Rationale** citing its evidence, its **Requirement refs** and its **Dependencies** on other DECs or "None".
- **Rationale**: a decision written as prose mixes the choice and its reasons, which a reader then cannot cite apart; a decision naming its requirements and the decisions it builds on is traced without reading its ADR's context. Amended by the owner's edit of the instructions file on 2026-11-22 (TASK-PLG-096), for new decisions only: existing DECs are not rewritten.
- **Priority**: Must
- **Acceptance Criteria**: Given the ADR template of the instructions file, Then each DEC holds a Statement, a Rationale with no "None", Requirement refs and Dependencies; Given the demo and the user's guide, Then each of their DECs holds all four.
- **Dependencies**: RQ-DMO-005

### RQ-PLG-041: Plain-text IDs in process artifacts
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The process SHALL require traceability references in comments in every file outside `agnos-process/`, and as plain text in the artifact files of `agnos-process/`.
- **Rationale**: an ID in an HTML comment is hidden from the reader of a rendered process document.
- **Priority**: Must
- **Acceptance Criteria**: Given the demo's `agnos-process/`, Then no artifact file holds an ID in an HTML comment; Given the demo's code, Then its IDs stay in comments.
- **Dependencies**: RQ-DMO-008
