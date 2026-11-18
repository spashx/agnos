# PLAN-DOC-003: Unified AGNOS repository addresses

## Overview
Declare the public AGNOS addresses once in `assets/links.json`, check every document against it, have the website read it, and
make the README, the guide and the demo's README link the AGNOS places (owner request of 2026-11-18). The demo is then rebuilt and
imported into the local clone `../agnos-demo`; nothing is pushed.

## References
- **Requirements**: RQ-DOC-007, RQ-DOC-008, RQ-WEB-020
- **ADRs**: ADR-DOC-001 (DEC-DOC-001), ADR-WEB-001 (DEC-WEB-008)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-DOC-006: Declare AGNOS addresses once
- **Tier**: L
- **Status**: Done
- **Description**: Write FTR-DOC-003, ADR-DOC-001 and this plan, amend RQ-WEB-020 and DEC-WEB-008; add `assets/links.json`, the
  links test, `site.json` as names read from it, and the process address of the marketplace's manifest.
- **Requirement refs**: RQ-DOC-007, RQ-WEB-020
- **ADR refs**: ADR-DOC-001 (DEC-DOC-001), ADR-WEB-001 (DEC-WEB-008)
- **Acceptance Criteria** (Gherkin): Given RQ-DOC-007's criteria, When the tests run, Then each holds; Given the website's suite,
  Then all pass; Given the release's suite, Then all pass.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: Website tests first, red before the code (30 errors: no `LINKS_FILE`, no `links_file`); after: 83 run, OK, 1 skipped
  (the demo's `tokens.json` absent). `test_links.py`: 16 run, 15 OK, 1 failed as expected: README.md hard-codes `marketplace` 5 times
  (TASK-DOC-007). `test_marketplace.py`: 26 run, 2 failed outside this task: `## Repository Map` vs CONTRIBUTING.md's `## Repository
  map` (since TASK-DOC-005), and `| macOS | Not tested` vs the new layout of COMPATIBILITY.md (owner's Tier S edit of 2026-11-18).
- **Assumptions**: A URL outside a reference definition that equals a declared address, or extends one by `#`, `/` or `?`, is a
  hard-coded copy; the links file of the website build is injectable, defaulting to the repository's `assets/links.json`.

### TASK-DOC-007: Link process documents to addresses
- **Tier**: M
- **Status**: Done
- **Description**: Make the README and the guide's template write their AGNOS addresses as checked reference definitions; link the
  Performance Center from the README, the guide in the marketplace as its source; rename the guide's row 8 to the Performance Center.
- **Requirement refs**: RQ-DOC-007, RQ-DOC-008
- **ADR refs**: ADR-DOC-001 (DEC-DOC-001)
- **Acceptance Criteria** (Gherkin): Given RQ-DOC-008's criteria on the README and the guide, When the tests run, Then each holds;
  Given the links test, Then it passes on both files.
- **Dependencies**: TASK-DOC-006
- **Assignee**: AI
- **Verification**: Tests first: `TestProcessDocumentLinks` 4 of 4 failed, and the hard-coded check failed on README.md (5 copies).
  After: `test_links.py` 20 run, OK, none skipped; `agnos-init` 42 run, OK; `test_marketplace.py` 26 run, the same 2 failures as
  TASK-DOC-006 (TASK-DOC-009), no new one.
- **Assumptions**: The CLI commands, in code where no reference link works, name the marketplace by its GitHub shorthand
  `spashx/agnos-marketplace`, which both CLIs accept; not yet proved by an install.

### TASK-DOC-008: Link demo README to addresses
- **Tier**: M
- **Status**: Done
- **Description**: Make both READMEs of the demo's content link the Performance Center, the marketplace and the process repository
  and name the Performance Center; rebuild and verify the demo, then import it into `../agnos-demo`.
- **Requirement refs**: RQ-DOC-007, RQ-DOC-008
- **ADR refs**: ADR-DOC-001 (DEC-DOC-001)
- **Acceptance Criteria** (Gherkin): Given the demo built, When its `README.md` is read, Then it links the three places And holds no
  "traceability skill"; Given `agnos-meta-demo verify`, Then every line is PASS; Given `../agnos-demo`, Then its `main` is the
  build's HEAD And its `origin` is unchanged.
- **Dependencies**: TASK-DOC-006
- **Assignee**: AI
- **Verification**: Tests first: `TestDemoReadmeLinks` 2 of 2 failed; after: `test_links.py` 22 run, OK; `agnos-meta-demo` tests 18 run,
  OK; none skipped. `build -Verify`: exit 0, 27 PASS, 0 FAIL, demo HEAD `f2943d0`; its `README.md` holds `## AGNOS` and the three
  definitions, no "traceability skill". `../agnos-demo`: `main` at `f2943d0`, `feature/*` imported, `origin` unchanged, not pushed.
- **Assumptions**: The demo's READMEs carry no comment citing RQ-DOC-007 or RQ-DOC-008: the demo's verification refuses the IDs of
  AGNOS's own development (RQ-INI-008).

### TASK-DOC-009: Align release tests with current documents
- **Tier**: S
- **Status**: Done
- **Description**: Make the release's tests read COMPATIBILITY.md's matrix layout ("macOS is not tested") and CONTRIBUTING.md's
  heading `## Repository map`, both changed on purpose (owner's matrix of 2026-11-18, TASK-DOC-005).
- **Requirement refs**: RQ-PLG-008, RQ-PLG-023
- **ADR refs**: None
- **Acceptance Criteria** (Gherkin): Given the current COMPATIBILITY.md and CONTRIBUTING.md, When `test_marketplace.py` runs, Then
  both tests pass.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: None
