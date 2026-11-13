# PLAN-WEB-009: Tour stops in the Performance Center order

## Overview
Order the site's tour stops as the Performance Center orders its views: Matrix, Graph, History, Delivery, Quality; and carry the
owner's new chain-card title into both languages (owner request of 2026-11-13).

## References
- **Requirements**: RQ-WEB-001, RQ-WEB-003, RQ-WEB-010
- **ADRs**: ADR-WEB-001 (DEC-WEB-003)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-WEB-021: Order the tour stops like the Performance Center
- **Tier**: M
- **Status**: Done
- **Description**: Move the Quality stop after Delivery in the template and renumber the stops; amend RQ-WEB-001 with the new
  order; write the chain title "The agentic loop, from need to commit" and *AI-native* in the hero text of both languages.
- **Requirement refs**: RQ-WEB-001, RQ-WEB-003, RQ-WEB-010
- **ADR refs**: ADR-WEB-001 (DEC-WEB-003)
- **Acceptance Criteria** (Gherkin): Given the built page, Then its stops stand in the order Matrix, Graph, History, Delivery,
  Quality, numbered 1 / 5 to 5 / 5; Given both languages, Then the chain title states the agentic loop; Given the skill's tests,
  Then all pass.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: test first, red before the code: `python -m unittest discover -s tests` 2 failures; after: 65 OK, 0 skipped;
  template stops: matrix 1 / 5, graph 2 / 5, history 3 / 5, delivery 4 / 5, quality 5 / 5.
- **Assumptions**: the `fr.md` restored from HEAD after the owner's overwrite of an older copy keeps only the owner's two intended
  changes.

### TASK-WEB-022: Remove the History stop note
- **Tier**: M
- **Status**: Done
- **Description**: Remove the `history.note` field from `en.md`, its element and the `.note` rule from the template, the owner having
  moved its sentence into the French `history.see`; carry that sentence into the English `history.see`.
- **Requirement refs**: RQ-WEB-001, RQ-WEB-003
- **ADR refs**: ADR-WEB-001 (DEC-WEB-003)
- **Acceptance Criteria** (Gherkin): Given the built page, Then it holds no `class="note"` and no `history.note`; And the History text
  states that every commit can be traced through a requirement view or an implementation view, in both languages; Given the skill's
  tests, Then all pass.
- **Dependencies**: TASK-WEB-021
- **Assignee**: AI
- **Verification**: test first, red before the code: `TestThePage` 1 error (build stopped on `history.note`); after: `python -m
  unittest discover -s tests`: 66 OK, 0 skipped; `note` found nowhere in the template nor `en.md`.
- **Assumptions**: None
