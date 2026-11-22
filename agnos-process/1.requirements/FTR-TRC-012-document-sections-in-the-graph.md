# FTR-TRC-012: Document sections in the graph

## Overview
`agnos-graph` gives a feature, an ADR and a plan as one element each, and their requirements, decisions and tasks as its
children; an ID cited in the rest of the document, its Overview, Context or Alternatives, is a link of the whole document. This
feature gives the graph the sections of those documents that hold no requirement, decision or task, and their subsections,
as nodes citing the IDs their lines hold.

Source: the owner's request of 2026-11-22: the rule is what a section contains, not a fixed list; no new ID; the perf center
is out of scope, and SHALL see no side effect.

Out of scope: `agnos-perf-center` (its page, coverage and score), headings below `###`, documents other than FTR, ADR and PLAN.

## Stakeholders
- **Owner**: the repository owner (maintainer of AGNOS).
- **Consumers**: agents and tools reading `agnos-graph.json`; later, `agnos-perf-center`.

---

## Functional Requirements

### RQ-TRC-134: Document section nodes
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The graph skill SHALL write, for every `##` heading of a feature, ADR or plan document whose line range holds no requirement, decision or task the index defines, one section node of type `SEC`, level 2, child of its document, with its line range and its title.
- **Rationale**: the context, consequences and references of a document are where its reasoning is written, and today a reader cannot tell them apart.
- **Priority**: Must
- **Acceptance Criteria**: Given an ADR holding `## Context` and `## Decision` with one DEC, When the graph is built, Then `ADR-ABC-001#Context` is a section node And no node is written for `## Decision`; Given a feature holding a `## Glossary` heading absent from the template, Then `FTR-ABC-001#Glossary` is a section node.
- **Dependencies**: RQ-TRC-129, RQ-TRC-130

### RQ-TRC-135: Document subsection nodes
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The graph skill SHALL write, for every `###` heading inside a section node, one section node of type `SEC`, level 3, child of that section; a deeper heading SHALL stay inside its subsection.
- **Rationale**: a long context or a list of alternatives is split by its author into subsections, which the reader cites apart.
- **Priority**: Must
- **Acceptance Criteria**: Given `## Overview` holding `### Scope` and `#### Detail`, When the graph is built, Then `FTR-ABC-001#Overview/Scope` is a level 3 node whose parent is `FTR-ABC-001#Overview` And no node is written for `#### Detail`.
- **Dependencies**: RQ-TRC-134

### RQ-TRC-136: Section identifier and citations
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The graph skill SHALL identify a section as `<document ID>#<section title>` and a subsection as `<document ID>#<section title>/<subsection title>`, suffixed `.2`, `.3` for a repeated title under one parent, and SHALL give each section node the IDs cited in its own lines, outside its subsections, with their line and text.
- **Rationale**: an identifier derived from the document needs no new ID in the process documents nor in the index.
- **Priority**: Must
- **Acceptance Criteria**: Given `## Context` citing `RQ-ABC-002` on line 9, When the graph is built, Then `ADR-ABC-001#Context` cites `RQ-ABC-002` with proof `[9, <line text>]`; Given two `### Note` under one section, Then their identifiers end in `/Note` and `/Note.2`; Given the same inputs and `--generated-at`, Then two runs write the same bytes.
- **Dependencies**: RQ-TRC-134, RQ-TRC-135

---

## Non-Functional Requirements

### RQ-TRC-137: Unchanged graph consumers
- **Category**: Non-Functional
- **NFR Type**: Maintainability
- **EARS Type**: Ubiquitous
- **Statement**: The graph skill SHALL write the section nodes in a `sections` block of their own, leaving every other block of `agnos-graph.json` byte-identical to the one written without sections.
- **Metric**: 0 byte of difference in `elements`, `edges`, `files` and `tasks`, and in the perf center's data, before and after the change.
- **Measurement Method**: build the graph and the perf center's data of this repository and of the demo at the base commit and after the change, and compare.
- **Priority**: Must
- **Acceptance Criteria**: Given this repository and the demo, When the graph and the perf center's data are built before and after the change, Then every block but `sections` is identical And the perf center's data is identical.
- **Dependencies**: RQ-TRC-129, RQ-TRC-130
