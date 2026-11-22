# FTR-PLG-010: Process folder content classes

## Overview
The process folder gains two standard subfolders. `0.facts/` holds the project's facts: normative input documents, immutable and
always true (a protocol stack's specification, a device's technical specification, a user's guide), that the project complies with.
The user decides what goes in it; AGNOS skills may later transform a fact technically (a conversion to Markdown, for example) and
generate from the facts a deterministic index of unique IDs that the project's artifacts cite.
`4.knowledge/` holds the project's knowledge: dynamic, of uneven maturity, such as the state of the AGNOS project at a given time
written by a tool. The word "fact" names the content of `0.facts/` only.

Source: the owner's session of 2026-11-22.

Out of scope: the skills that transform facts and the facts index with its ID schema, a later feature; what a given tool writes
in `4.knowledge/` (FTR-TRC-011 for the graph).

## Stakeholders
- **Owner**: the repository owner (maintainer of AGNOS).
- **Consumers**: developers using the AGNOS plugin and their agents; `agnos-init`, `agnos-index`; the skills writing knowledge; the demo.

---

## Functional Requirements

### RQ-PLG-048: Facts folder for normative inputs
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: AGNOS SHALL provide a `0.facts/` subfolder of the process folder for the normative input documents the user places there, SHALL never change a fact's content, and SHALL not read a fact into the artifact index `process.idx.md`.
- **Rationale**: a specification the project must comply with is an input, true whatever the project decides, and needs a known place apart from what the project writes; a later technical transformation or facts index keeps the original intact.
- **Priority**: Must
- **Acceptance Criteria**: Given a project after `agnos-init`, Then `agnos-process/0.facts/` exists with its `readme.md`; Given a Markdown document in `0.facts/` holding `RQ-ABC-001`, When `agnos-index` runs, Then `process.idx.md` holds no row for it; Given the instructions file, Then it states that the user places the facts, that AGNOS never changes their content, and that a skill may transform them technically and index them.
- **Dependencies**: RQ-PLG-036, RQ-IDX-013

### RQ-PLG-049: Knowledge folder for dynamic project knowledge
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: AGNOS SHALL provide a `4.knowledge/` subfolder of the process folder for the project's dynamic knowledge, SHALL not index its content, and every file an AGNOS skill writes there SHALL state when it was produced.
- **Rationale**: knowledge such as the state of the project at a given time is true only at its date; a known place and a date keep it from being read as a fact.
- **Priority**: Must
- **Acceptance Criteria**: Given a project after `agnos-init`, Then `agnos-process/4.knowledge/` exists with its `readme.md`; Given a Markdown document in `4.knowledge/` holding `RQ-ABC-001`, When `agnos-index` runs, Then the index holds no row for it; Given the instructions file, Then it states that knowledge is dynamic, of uneven maturity, and dated.
- **Dependencies**: RQ-PLG-036, RQ-IDX-013

### RQ-PLG-050: Folder descriptions aligned on the layout
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: `layout.json` SHALL declare `0.facts` and `4.knowledge` among the subfolders, with the subfolders the index scans declared apart; every Markdown file describing the process folder's subfolders (the instructions file, the entry points, the guide, the contributors' guide, the demo, the website's content) SHALL list both, and the suites testing the layout SHALL cover them.
- **Rationale**: a folder named in the layout but missing from a description would leave the user's agent ignorant of it.
- **Priority**: Must
- **Acceptance Criteria**: Given `layout.json`, Then it lists `0.facts` and `4.knowledge` And declares the indexed subfolders apart; Given each file describing the subfolders, Then it lists both with their nature; Given `agnos-init` on an existing AGNOS project, Then both folders are added And nothing else changes; Given the suites of `agnos-init`, `agnos-index` and `agnos-meta-release`, Then they pass on Windows and Linux.
- **Dependencies**: RQ-PLG-036, RQ-PLG-037, RQ-PLG-048, RQ-PLG-049
