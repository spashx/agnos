# PLAN-WEB-005: Index card without measures

## Overview
Remove from the site's index card the figures measured on the demo (documents and index sizes, their ratio, the index's speed) and
their bars, which the owner judges of no use; the card keeps its title, text, excerpt and caption (owner request of 2026-11-13).
RQ-WEB-005 is deprecated; the check of a variable left in a field stays, under RQ-WEB-004.

## References
- **Requirements**: RQ-WEB-005 (deprecated 2026-11-13), RQ-WEB-001, RQ-WEB-004, RQ-WEB-018 (amended 2026-11-13), RQ-WEB-015
- **ADRs**: ADR-WEB-001 (DEC-WEB-002 amended 2026-11-13, DEC-WEB-003, DEC-WEB-005)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-WEB-017: Remove the index card measures
- **Tier**: L
- **Status**: Done
- **Description**: Remove the `documents` and `index` fields and the `{{index.*}}` variables from `en.md` and `fr.md`, the bars and
  their token from the template and `tokens.json`, the measurement code from `build_site.py`, and the ratio from the summary line;
  deprecate RQ-WEB-005, amend RQ-WEB-001, RQ-WEB-004, RQ-WEB-018, DEC-WEB-002 and the skill's `SKILL.md`.
- **Requirement refs**: RQ-WEB-005, RQ-WEB-001, RQ-WEB-004, RQ-WEB-018, RQ-WEB-015
- **ADR refs**: ADR-WEB-001 (DEC-WEB-002, DEC-WEB-003, DEC-WEB-005)
- **Acceptance Criteria** (Gherkin): Given the built page, Then the index card holds its title, text, excerpt and caption, and no
  figure, bar or `{{` in either language; Given a field holding `{{x}}`, When `build` runs, Then the error names the file, the field
  and the variable, And the exit code is 1; Given a build, Then its summary line states no index ratio; Given the skill's tests,
  Then all pass.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: tests first: `test_content` (field kept, `{{index.ratio}}` left in a field reported as
  `en.md: hero.figure: unknown variable {{index.ratio}}`), `test_page` (index card slots `text`, `excerpt`, `caption` only, no
  `bar-row`, no `{{`, no digit, KB or Ko in either language), `test_build` (summary `… 8 images, demo page copied; … written`).
  Copy run by a sub-agent: 62 run, 2 errors (two `render` calls still passing the removed `values`), 1 skipped (demo absent beside
  the copy); after fixing those calls, in the repository `python -m unittest discover -s tests`: 62 OK, 0 skipped.
- **Assumptions**: `--demo` stays required (the CLI is unchanged); the site is not rebuilt into the owner's `agnos.site` copy; the
  owner's uncommitted edits of `fr.md` stay out of this task's commit (only this task's lines are staged); the variable check
  moves to RQ-WEB-004.
