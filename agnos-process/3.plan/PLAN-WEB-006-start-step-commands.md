# PLAN-WEB-006: Example commands in the start steps

## Overview
Show under each of the three start steps of the site's close an example of what to run or type, in a console style, the French
addressing the reader with "vous" (owner request of 2026-11-13).

## References
- **Requirements**: RQ-WEB-009 (amended 2026-11-13), RQ-WEB-003, RQ-WEB-014, RQ-WEB-015
- **ADRs**: ADR-WEB-001 (DEC-WEB-003, DEC-WEB-005)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-WEB-018: Add example commands to the start steps
- **Tier**: M
- **Status**: Done
- **Description**: Add the fields `step1-command` to `step3-command` to `en.md` and `fr.md` as code blocks, render them in the
  template as `pre.console` under each step's text, styled by design-system tokens with a new semantic `web-console` background;
  amend RQ-WEB-009.
- **Requirement refs**: RQ-WEB-009, RQ-WEB-003, RQ-WEB-014, RQ-WEB-015
- **ADR refs**: ADR-WEB-001 (DEC-WEB-003, DEC-WEB-005)
- **Acceptance Criteria** (Gherkin): Given the built page, Then each of the three step cards holds a non-empty `pre.console`, in
  English and in French; Given the template, Then the `.console` style holds no raw visual value; Given each theme, Then the
  console text reaches 4.5:1 on its background; Given the skill's tests, Then all pass.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: tests first, red before the code: `TestTheStartSteps` (1 failure, 1 error) and `TestContrast` (1 error,
  no `web-console` token); after: `python -m unittest discover -s tests`: 64 OK, 0 skipped. Each step card holds a non-empty
  `pre.console` in both languages; the `.console` rule consumes `--s-web-console` and no raw value; `web-band-text` on `web-console`
  reaches 4.5:1 in both themes.
- **Assumptions**: step 1 shows the Claude Code commands of the README with its `<marketplace>` placeholder; steps 2 and 3 show
  the request typed to the agent, step 3 the guide's `Start a new AGNOS session, trigram EXP.`; no `$` prompt, steps 2 and 3
  being no shell commands.
