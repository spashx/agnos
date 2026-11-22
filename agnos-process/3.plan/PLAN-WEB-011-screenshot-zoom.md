# PLAN-WEB-011: Tour screenshots enlarged on click

## Overview
Enlarge each tour screenshot on click, as the three examples of the Matrix stop, instead of opening the demo; check the screens by
their presence and size only, the owner's real screenshots replacing the placeholders (owner request of 2026-11-14).

## References
- **Requirement refs**: RQ-WEB-011, RQ-WEB-012, RQ-WEB-017
- **ADR refs**: ADR-WEB-001 (DEC-WEB-004)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-WEB-024: Enlarge the tour screenshots on click
- **Tier**: L
- **Status**: Done
- **Description**: Amend RQ-WEB-011, RQ-WEB-012 and DEC-WEB-004; make each tour screenshot the examples' zoom button in the
  template; write the shots as plain images in `en.md` and `fr.md` and remove `labels.open`; remove the linked-image parsing, the
  `.shot-link` and `.shot-open` rules; check the screens at 1920 × 1080 without a single colour.
- **Requirement refs**: RQ-WEB-011, RQ-WEB-012, RQ-WEB-017
- **ADR refs**: ADR-WEB-001 (DEC-WEB-004)
- **Acceptance Criteria** (Gherkin): Given the five tour stops, Then each screenshot is an `example-open` button holding its image,
  with no `shot-link`, `shot-open`, "Open in the demo" nor `demo/PERF-CENTER.html#` link; When one is activated, Then the dialog of
  RQ-WEB-017 enlarges it; Given the assets, Then each view and example is a PNG at 1920 × 1080; Given the skill's tests, Then all
  pass; Given a build, Then it exits 0.
- **Dependencies**: TASK-WEB-023
- **Assignee**: AI
- **Verification**: test first, red before the code: `python -m unittest discover -s tests` 2 failures (zoom, placeholders); after:
  66 OK, 0 skipped; `build` exit 0, "150 fields in each language, 8 images"; the demo stays linked by the nav, hero and closing
  buttons (`{{v:link.demo}}`, template lines 225, 237, 424).
- **Assumptions**: the zoom reuses the examples' dialog and script unchanged; the owner's screenshots in the working tree are
  committed by the owner, not by this task.
