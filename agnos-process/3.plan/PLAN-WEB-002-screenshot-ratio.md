# PLAN-WEB-002: Screenshot frames at the capture ratio

## Overview
Frame the site's screenshots at 1291:720, the ratio of the owner's captures, through a design-system token, check every
image's ratio at build, and rebuild the site from the demo of PLAN-DMO-004.

## References
- **Requirements**: RQ-WEB-019, RQ-WEB-012, RQ-WEB-015, RQ-WEB-001
- **ADRs**: ADR-WEB-001 (DEC-WEB-004, DEC-WEB-005, DEC-WEB-007); ADR-TRC-002 (design system)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-WEB-012: Frame screenshots at the capture ratio
- **Tier**: M
- **Status**: Done
- **Description**: Accept DEC-WEB-007; add `web.ratio-shot` to `assets/tokens.json` and use it in the template's two
  frames; make `build_site.py` read each PNG's size and refuse a wrong ratio or width; rewrite the eight placeholders at
  1936 × 1080; update `SKILL.md`.
- **Requirement refs**: RQ-WEB-019, RQ-WEB-012, RQ-WEB-015
- **ADR refs**: ADR-WEB-001 (DEC-WEB-007, DEC-WEB-005), ADR-TRC-002
- **Acceptance Criteria** (Gherkin): Given the template, Then no frame holds `16/10` and both use the token; Given
  images of 1291 × 720, 1936 × 1080 and 2582 × 1440, When `build` runs, Then it succeeds; Given one of 1600 × 1000 or
  1000 × 558, Then it fails naming the file and writes nothing; Given the placeholders, Then each is one colour at
  1936 × 1080; Given the skill's tests, Then all pass.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `TestTheFrames` and `TestTheScreenSize` failed before the change; `python -m unittest discover -s tests` in
  the skill: 62 OK, 0 skipped (1291×720, 1936×1080, 2582×1440 accepted; 1600×1000 and 1000×558 refused, exit 1, output
  unchanged). Template diff: both frames `aspect-ratio:var(--s-web-ratio-shot)`. Build into a scratch folder: exit 0, 8 images.
- **Assumptions**: the 0.5% is relative to 1291/720; the check sits in `screen_files`, so `build_page` stays pure;
  each placeholder keeps its colour; `TestThePlaceholders` now asserts 1936 × 1080 instead of 16:10 (RQ-WEB-012 amended).

### TASK-WEB-013: Rebuild the site from the new demo
- **Tier**: S
- **Status**: Not Started
- **Description**: Run `agnos-meta-website build` on the rebuilt demo into `C:\dev\repos\spashx`, and record its summary.
- **Requirement refs**: RQ-WEB-001, RQ-WEB-002
- **ADR refs**: ADR-WEB-001 (DEC-WEB-002, DEC-WEB-006)
- **Acceptance Criteria** (Gherkin): Given the rebuilt demo, When `build` runs, Then it exits 0 and its summary line
  is recorded here.
- **Dependencies**: TASK-WEB-012, TASK-DMO-018
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: 
