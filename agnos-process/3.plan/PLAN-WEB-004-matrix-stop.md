# PLAN-WEB-004: Matrix stop of the tour

## Overview
Make the first stop of the tour the Matrix view, name each content section after its view without the `stop-` prefix, link the
Matrix screenshot to the demo's Matrix (RQ-TRC-121), and rebuild the site (owner request of 2026-11-12).

## References
- **Requirement refs**: RQ-WEB-009, RQ-WEB-011, RQ-WEB-012, RQ-WEB-017 (amended 2026-11-12); RQ-TRC-121; RQ-WEB-001, RQ-WEB-002
- **ADR refs**: ADR-WEB-001 (DEC-WEB-004, DEC-WEB-005); ADR-TRC-019 (DEC-TRC-066)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-WEB-015: Rename the tour sections after their views
- **Tier**: M
- **Status**: Done
- **Description**: In `template.html`, the two content files and the tests, rename `stop-overview` to `matrix` and the other
  `stop-<view>` sections to `<view>`, the stop's `id` to `matrix`; rewrite the English Matrix stop from the owner's French text;
  link the Matrix screenshot to `demo/PERF-CENTER.html#view=matrix`.
- **Requirement refs**: RQ-WEB-009, RQ-WEB-011, RQ-WEB-012, RQ-WEB-017
- **ADR refs**: ADR-WEB-001 (DEC-WEB-004, DEC-WEB-005), ADR-TRC-019 (DEC-TRC-066)
- **Acceptance Criteria** (Gherkin): Given the template and both content files, Then no key starts with `stop-` and the first stop
  is `matrix` with `id="matrix"`; Given the English Matrix stop, Then it names the Matrix view and `screens/matrix.png`; Given the
  page, Then the Matrix screenshot links to `demo/PERF-CENTER.html#view=matrix`; Given the skill's tests, Then all pass.
- **Dependencies**: TASK-TRC-108
- **Assignee**: AI
- **Verification**: before the rename, after the owner's `matrix.png`: the skill's suite 62 run, 4 failures, 1 error (`overview.png`
  expected). Script check after the rename: no `stop-overview|graph|quality|history|delivery` key and no `id="overview"` left in
  `template.html`, `fr.md`, `en.md`; both Matrix shots link to `demo/PERF-CENTER.html#view=matrix`. `python -m unittest discover -s
  tests`: 62 OK, 0 skipped.
- **Assumptions**: the CSS classes `stop` and `stop-n` stay, being layout names, not content keys; the French corrections and the
  first English translation of the owner's text were made by a sub-agent at the owner's request of 2026-11-12, in this task's
  commit; the tests asserting the old English question and History note follow the new text (RQ-WEB-009 amended).

### TASK-WEB-016: Rebuild the site with the Matrix stop
- **Tier**: S
- **Status**: Done
- **Description**: Regenerate the demo's Performance Center with `--call-graph --history` and run `agnos-meta-website build` on the
  demo into `C:\dev\repos\spashx\website`.
- **Requirement refs**: RQ-WEB-001, RQ-WEB-002
- **ADR refs**: ADR-WEB-001 (DEC-WEB-002, DEC-WEB-006)
- **Acceptance Criteria** (Gherkin): Given TASK-TRC-108 and TASK-WEB-015 done, When `build` runs, Then it exits 0 and its summary
  line is recorded here: `agnos-meta-website: 152 fields in each language, 8 images, index 1/14, demo page generated;
  C:\dev\repos\spashx\website written`.
- **Dependencies**: TASK-WEB-015
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: None
