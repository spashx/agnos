# PLAN-TRC-020: Deep links to a view

## Overview
Let the Performance Center open on the view named by a `#view=<name>` fragment, resolved against the tabs the page shows, so
that any later view is linkable with no code change (owner request of 2026-11-12).

## References
- **Requirements**: RQ-TRC-121, RQ-TRC-016
- **ADRs**: ADR-TRC-019 (DEC-TRC-066), ADR-TRC-003 (DEC-TRC-007)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-TRC-108: Open the view named in the URL fragment
- **Tier**: L
- **Status**: Done
- **Description**: Accept ADR-TRC-019; in `assets/matrix.js`, resolve `#view=<name>` against the shown tabs at opening and on
  `hashchange`, falling back to the Overview; test it in a real browser first; document the address in the skill.
- **Requirement refs**: RQ-TRC-121, RQ-TRC-016
- **ADR refs**: ADR-TRC-019 (DEC-TRC-066), ADR-TRC-003 (DEC-TRC-007)
- **Acceptance Criteria** (Gherkin): Given the fixture page and `#view=matrix`, When it opens, Then the Matrix tab is selected and
  `view-matrix` shown; Given each tab the page shows, Then `#view=<its name>` opens it; Given `#view=history` without history or
  `#view=unknown`, Then the Overview opens; Given `#RQ-DEM-002`, Then the RQ-TRC-016 test still passes; Given the skill's suite,
  Then all pass.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: before the change, `-k RQ_TRC_121 -k RQ_TRC_016`: 4 run, 4 failures (`#view=matrix`, `graph`, `quality` opened
  `overview`); fallback and RQ-TRC-016 tests passing. After: 4 run, OK. Full suite `python -m unittest discover -s tests`: 412 run,
  OK, 3 skipped (the opt-in performance tests of RQ-TRC-036 to 038, RQ-TRC-078 and RQ-HST-013, which need
  `AGNOS_PERF_CENTER_PERF=1`; not measured). History tab unhidden at script evaluation, before `openInitialView`.
- **Assumptions**: a named view takes precedence over an element key, which cannot start with `view=`; `#view=` with an empty
  name falls back like an unknown one; the tab click still leaves the URL unchanged (not asked, ADR-TRC-019).
