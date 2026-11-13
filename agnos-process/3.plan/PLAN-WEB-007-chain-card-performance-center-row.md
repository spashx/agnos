# PLAN-WEB-007: Performance Center row of the chain card

## Overview
In the chain card, remove the demo's name beside "Performance Center" and start the supervision text at the icon's left edge
(owner request of 2026-11-13).

## References
- **Requirements**: RQ-WEB-010, RQ-WEB-015
- **ADRs**: ADR-WEB-001 (DEC-WEB-003, DEC-WEB-005)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-WEB-019: Align the Performance Center row of the chain card
- **Tier**: M
- **Status**: Done
- **Description**: Remove the `chain.measure-id` field from `en.md` and `fr.md` and its element from the template; place the
  `chain.measure-text` element as a direct child of `.chain-pc`, spanning the whole row under the icon and its label.
- **Requirement refs**: RQ-WEB-010, RQ-WEB-015
- **ADR refs**: ADR-WEB-001 (DEC-WEB-003, DEC-WEB-005)
- **Acceptance Criteria** (Gherkin): Given the chain card, Then its Performance Center row shows the icon and its label without
  "Roombook"; And the supervision text spans the row from the icon's left edge, in both languages; Given the skill's tests, Then
  all pass.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: test first, red before the code: `TestTheChainPerformanceCenter` 1 failure; after: `python -m unittest
  discover -s tests`: 65 OK, 0 skipped; `measure-id` found nowhere in the assets; the row ends on
  `<span class="t" data-i18n="chain.measure-text">`, outside `.st`, under `.chain-pc .t{grid-column:1 / -1}`.
- **Assumptions**: the left alignment is checked by the template's structure and CSS; the owner checks the rendering visually.
