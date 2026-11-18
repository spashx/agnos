# FTR-DOC-003: AGNOS repository addresses

## Overview
AGNOS lives in several public places: the process repository, the marketplace holding the plugin, the website and its
repository, the demo's Performance Center page and the demo repository. The Markdown documents of this repository, the
demo's README and the website each wrote these addresses by hand, and one of them, the process repository named in the
marketplace's manifest, was wrong. This feature declares every address once and has each document link the places its
reader needs (owner request of 2026-11-18).

Out of scope: the README of the website repository, which is the owner's file and already links the website; publishing
any repository.

## Stakeholders
- **Owner**: the repository owner (maintainer of AGNOS).
- **Consumers**: plugin users reading the README and the guide; readers of the demo; the website build; the release.

---

## Functional Requirements

### RQ-DOC-007: Repository address declaration
- **Category**: Functional
- **EARS Type**: Complex
- **Statement**: The repository SHALL declare each public AGNOS address once, in `assets/links.json`; every checked Markdown
  document SHALL write a declared address only as a Markdown reference definition `[<name>]: <address>` whose value is the
  declared one; the website build SHALL take the addresses it names from that file; IF a checked document holds a declared
  address outside its reference definition, or a definition whose value differs, THEN the check SHALL fail naming the document
  and the address.
- **Rationale**: one address changed in one place reaches every document, and a wrong or stale copy is found by a test.
- **Priority**: Must
- **Acceptance Criteria**: Given `assets/links.json`, Then it declares `process`, `marketplace`, `getting-started`, `guide`,
  `website`, `website-repository`, `perf-center` and `demo-repository`; Given a checked document with `[marketplace]: <another
  address>`, When the check runs, Then it fails naming the document and `marketplace`; Given a checked document holding a
  declared address in its text, When the check runs, Then it fails naming the document; Given the marketplace's manifest, Then its
  `homepage` and `repository` are the `process` address; Given the website's `site.json` naming `marketplace`, When `build`
  runs, Then the page holds the `marketplace` address of `links.json`.
- **Dependencies**: RQ-WEB-020, RQ-PLG-008

### RQ-DOC-008: Document links to AGNOS places
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The README SHALL link the demo's Performance Center and the marketplace, and SHALL name the guide in the
  marketplace as the guide's source; the demo's README SHALL link the demo's Performance Center, the marketplace and the process
  repository, and SHALL name the AGNOS Performance Center where it names what shows the links; the guide's table of what the user
  types SHALL name the Performance Center, with its options `--call-graph` and `--history`.
- **Rationale**: a reader reaches each AGNOS place from the document in hand, and no document names the former
  traceability skill.
- **Priority**: Must
- **Acceptance Criteria**: Given the README, Then it links `perf-center` and `marketplace`, And its guide-source link is `guide`;
  Given the demo's README, as built, Then it links `perf-center`, `marketplace` and `process`, And it holds no "traceability
  skill"; Given the guide's table "What you actually type, all together", Then its row 8 names the Performance Center,
  `--call-graph` and `--history`, And no row names a trace or a traceability matrix.
- **Dependencies**: RQ-DOC-007
