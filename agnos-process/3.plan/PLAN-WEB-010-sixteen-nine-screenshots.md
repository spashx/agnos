# PLAN-WEB-010: Screenshots at 16:9

## Overview
Frame and check the site's screenshots at 16:9, 1920 × 1080 px, instead of 1291:720 (owner request of 2026-11-13).

## References
- **Requirements**: RQ-WEB-012, RQ-WEB-019
- **ADRs**: ADR-WEB-001 (DEC-WEB-007)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-WEB-023: Switch the screenshot ratio to 16:9
- **Tier**: L
- **Status**: Done
- **Description**: Amend RQ-WEB-019, RQ-WEB-012 and DEC-WEB-007 to the ratio 16:9 and a 1920 px minimum width; set the token
  `web.ratio-shot` to `16 / 9` and `build_site.py` to 1920 × 1080; crop the eight placeholders to 1920 × 1080; update `SKILL.md`.
- **Requirement refs**: RQ-WEB-012, RQ-WEB-019
- **ADR refs**: ADR-WEB-001 (DEC-WEB-007)
- **Acceptance Criteria** (Gherkin): Given images of 1920 × 1080 and 3840 × 2160, When `build` runs, Then it succeeds; Given one of
  1936 × 1080, 1600 × 1000 or 1280 × 720, When `build` runs, Then it fails naming the file, its size and the ratio 16:9, and writes
  nothing; Given the page, Then it holds `--s-web-ratio-shot: 16 / 9;`; Given the placeholders, Then each is one colour at
  1920 × 1080; Given the skill's tests, Then all pass.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: test first, red before the code: `python -m unittest discover -s tests` 7 failures; after: 66 OK, 0 skipped;
  the eight placeholders rewritten 1936 × 1080 → 1920 × 1080, each keeping its colour.
- **Assumptions**: the placeholders are cropped by rewriting them in their single colour (owner: they are coloured backgrounds);
  3840 × 2160 is the second accepted size; the tolerance stays 0.5%.
