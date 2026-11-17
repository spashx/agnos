# PLAN-WEB-012: Marketplace links of the site

## Overview
Link the AGNOS marketplace from the header and the install step, show its address in the install command, lead the footer's
developer link to the marketplace's getting-started section, with every address declared once in `assets/site.json`; and correct the
spacing of an English tour question (owner request of 2026-11-18).

## References
- **Requirements**: RQ-WEB-004, RQ-WEB-006, RQ-WEB-009, RQ-WEB-020
- **ADRs**: ADR-WEB-001 (DEC-WEB-003, DEC-WEB-008)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-WEB-025: Record marketplace link decisions
- **Tier**: M
- **Status**: Done
- **Description**: Add RQ-WEB-020, amend RQ-WEB-004 and RQ-WEB-009, add DEC-WEB-008 to ADR-WEB-001 with its diagrams, and write this plan.
- **Requirement refs**: RQ-WEB-004, RQ-WEB-009, RQ-WEB-020
- **ADR refs**: ADR-WEB-001 (DEC-WEB-008)
- **Acceptance Criteria** (Gherkin): Given the index, When it is rebuilt, Then RQ-WEB-020, DEC-WEB-008, PLAN-WEB-012 and TASK-WEB-025 to
  TASK-WEB-027 are listed with no duplicate ID.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `agnos-index`: exit 0 (no duplicate), 963 entries; RQ-WEB-020, DEC-WEB-008, PLAN-WEB-012, TASK-WEB-025 to 027 listed. No code: no test.
- **Assumptions**: None

### TASK-WEB-026: Implement marketplace links and buttons
- **Tier**: M
- **Status**: Not Started
- **Description**: Add `assets/site.json`; make `build_site.py` read it into the template's values and replace declared `{{link.<name>}}`
  in the fields; add the two "AGNOS marketplace" buttons and the footer link to the template; write the install command and the
  button label in `en.md` and `fr.md`; rebuild the site into `agnos-website` and commit it there.
- **Requirement refs**: RQ-WEB-004, RQ-WEB-009, RQ-WEB-020
- **ADR refs**: ADR-WEB-001 (DEC-WEB-008)
- **Acceptance Criteria** (Gherkin): Given RQ-WEB-020's criteria, When the tests run, Then each holds; Given an undeclared link in a
  field or the template, When `build` runs, Then it fails naming it and exits 1; Given the skill's tests, Then all pass, none
  skipped; Given a build into `agnos-website`, Then it exits 0 And no `TODO` nor `<marketplace>` is left in `index.html`.
- **Dependencies**: TASK-WEB-025
- **Assignee**: AI
- **Verification**: Not yet run
- **Assumptions**: None

### TASK-WEB-027: Fix English tour question spacing
- **Tier**: S
- **Status**: Not Started
- **Description**: Remove the space before `?` in the English Matrix question of `en.md`, and any other space before `?`, `!`, `;` or `:`
  in the English text.
- **Requirement refs**: RQ-WEB-006
- **ADR refs**: None
- **Acceptance Criteria** (Gherkin): Given `en.md`, Then no `?`, `!`, `;` or `:` follows a space outside code.
- **Dependencies**: TASK-WEB-026
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: None
