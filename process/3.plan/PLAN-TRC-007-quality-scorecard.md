# PLAN-TRC-007: Quality Scorecard

## Overview
Implement RQ-TRC-057 to RQ-TRC-066 after ADR-TRC-008, in six steps that each leave the page and its tests working: the
scoring and the data first, then the vocabulary and the page reading the new block, the check cards, the report card
and its palette, the charts, and last the fit in the window, the speed and the wording of the older requirements.

## References
- **Requirements**: RQ-TRC-057 to RQ-TRC-067; RQ-TRC-009, RQ-TRC-015, RQ-TRC-017, RQ-TRC-035, RQ-TRC-045 (reworded)
- **ADRs**: ADR-TRC-008 (DEC-TRC-032 to DEC-TRC-035)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-TRC-046: Scoring of the checks and the `quality` data
- **Tier**: L
- **Status**: Done
- **Description**: Add `assets/scoring.json` (checks, risk weights, grade thresholds, attention threshold), compute each
  check's population, findings and score, the overall and per-trigram score and grade in the generator (the
  untraced-functions check from the call graph), write them as `quality` in place of `gaps` and `gapKinds`, change the
  summary line, re-pin the RQ-TRC-026 sentinel, and document the formulas and keys in `SKILL.md`. The page reads the new
  keys without changing its look yet.
- **Requirement refs**: RQ-TRC-058, RQ-TRC-059, RQ-TRC-064, RQ-TRC-057
- **ADR refs**: ADR-TRC-008 (DEC-TRC-032, DEC-TRC-033)
- **Acceptance Criteria**: Given a fixture with 10 requirements of which 2 are uncovered, Then the check "requirements
  covered" has population 10, 2 findings and score 8.0; Given a fixture with no task, Then "tasks with a requirement" has
  no score; Given the checks, Then the overall score is their weighted average and 9.0 is A, 8.9 is B, 3.9 is E; Given two
  trigrams, Then each has its own score; Given a run, Then the last line gives the grade, the score and each check's score
  and the data file holds the same numbers.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `python -m unittest discover -s tests` (skill folder): 149 tests, 0 failure, 1 skipped. `test_scorecard.py` (13 tests): 10 requirements with 2 findings score 8.0; empty population has no score; 8 of 1 finding rounds half up to 8.8; weights (10 x 10 + 7.5 x 0) / 17.5 = 5.7, informational weighs 0; 9.0 is A, 8.9 B, 3.9 E; the fixture gives covered 5 / 3 findings / 4.0, defined 8 / 2 / 7.5, overall C 6.1, a trigram DEM score without files-traced; the summary line and `quality` in the data file hold the same figures, `gaps` is gone, two runs give equal data. Generator on the fixture: "quality: C 6.1/10; checks: covered 4.0, defined 7.5, tasked 6.0, task-rq 6.7, adr-rq 5.0, filled 5.0, connected 7.3, files-traced 7.5; findings 17". The page reads the new block (tab count unchanged). The RQ-TRC-026 sentinel, failing before this plan, is re-pinned on purpose (8656b86a...). `IndependenceTest` now allows the sibling `scorecard.py` and checks it is standard library only.
- **Assumptions**: None

### TASK-TRC-047: Quality vocabulary in the page
- **Tier**: M
- **Status**: Not Started
- **Description**: Rename the Gaps tab, sidebar section, overview card and their identifiers to Quality, checks and
  findings, draw the findings of each check from the `quality` block, and reword RQ-TRC-009, RQ-TRC-015, RQ-TRC-017,
  RQ-TRC-035 and RQ-TRC-045 and the documentation so that "gap" appears nowhere.
- **Requirement refs**: RQ-TRC-057
- **ADR refs**: ADR-TRC-008 (DEC-TRC-034)
- **Acceptance Criteria**: Given the generated page, its data file, its summary line and `SKILL.md`, When searched for
  "gap" without regard to case, Then there is no match; Given the page, Then the tab, the sidebar section and the overview
  card are named Quality.
- **Dependencies**: TASK-TRC-046
- **Assignee**: AI
- **Verification**: Pending.
- **Assumptions**: None

### TASK-TRC-048: Check cards, compact or detailed
- **Tier**: M
- **Status**: Not Started
- **Description**: Draw the checks as a grid of cards, lowest score first, compact (name, risk, score bar, findings) and
  opened by a chevron to the rule, formula, KPIs and findings (sixty at first), with "Expand all" and "Collapse all".
- **Requirement refs**: RQ-TRC-062
- **ADR refs**: ADR-TRC-008 (DEC-TRC-034)
- **Acceptance Criteria**: Given the Quality view, When it opens, Then every check is compact; When a chevron is pressed,
  Then that check shows its rule, figures and findings and the others stay compact; When "Expand all" is pressed, Then
  every check is detailed; When a finding is clicked, Then its element is selected.
- **Dependencies**: TASK-TRC-047
- **Assignee**: AI
- **Verification**: Pending.
- **Assumptions**: None

### TASK-TRC-049: Report card and grade palette
- **Tier**: M
- **Status**: Not Started
- **Description**: Add the five grade colour tokens with their text tokens, and the report card (grade letter on the A–E
  scale, score, verdict, grade of each trigram, three "Fix first" links); show the grade in the tab, the sidebar and the
  overview card.
- **Requirement refs**: RQ-TRC-060, RQ-TRC-064, RQ-TRC-065
- **ADR refs**: ADR-TRC-008 (DEC-TRC-034, DEC-TRC-035)
- **Acceptance Criteria**: Given the fixture, When the Quality view opens, Then the report card shows a grade letter, a
  score, a verdict sentence, one grade per trigram and three "Fix first" links, and a link opens its check; Given the
  tokens of both themes, Then each grade letter on its background has a contrast of at least 4.5:1; Given the page, Then
  the tab, the sidebar and the overview show the same grade and score as the data file.
- **Dependencies**: TASK-TRC-048
- **Assignee**: AI
- **Verification**: Pending.
- **Assumptions**: None

### TASK-TRC-050: Charts with tooltips
- **Tier**: M
- **Status**: Not Started
- **Description**: Draw the radar of the checks, the bars per trigram and the coverage shares as inline SVG with a title,
  a description, focusable items and the page's tooltip; a radar axis opens its check.
- **Requirement refs**: RQ-TRC-061, RQ-TRC-065, RQ-TRC-045
- **ADR refs**: ADR-TRC-008 (DEC-TRC-035)
- **Acceptance Criteria**: Given the fixture, When the Quality view opens, Then it holds a radar with one axis per scored
  check, a bar per trigram and a coverage chart, each with a title and a description; When a radar point is pointed at,
  Then a tooltip gives the check's name, score, population and findings; When an axis is clicked, Then its check opens.
- **Dependencies**: TASK-TRC-049
- **Assignee**: AI
- **Verification**: Pending.
- **Assumptions**: None

### TASK-TRC-051: Fit in the window, speed, final documentation
- **Tier**: M
- **Status**: Not Started
- **Description**: Lay the three bands out so that the report card, the charts and all compact checks fit a 1440 by 900
  window, measure the scorecard's cost on the 20,000-function project, and complete `SKILL.md` (view, vocabulary,
  scoring).
- **Requirement refs**: RQ-TRC-063, RQ-TRC-066, RQ-TRC-017
- **ADR refs**: ADR-TRC-008 (DEC-TRC-034)
- **Acceptance Criteria**: Given a 1440 by 900 window and the fixture with the call graph, When the Quality view opens,
  Then its main area has no vertical scrollbar and the "functions traced" check is visible; Given the 20,000-function
  tree, Then the generator's time grows by less than 5 %, the page's size by less than 2 % and the view draws in less
  than 200 ms.
- **Dependencies**: TASK-TRC-050
- **Assignee**: AI
- **Verification**: Pending.
- **Assumptions**: None

### TASK-TRC-052: Remediation: named constants in the skill's code
- **Tier**: M
- **Status**: Not Started
- **Description**: Remove the duplicated string and number literals from the skill's scripts (`trace_matrix.py`,
  `callgraph.py`, `scorecard.py`) and page script (`matrix.js`) by naming them, and add the test that lists the repeated
  literals of each. Done after TASK-TRC-051, on the code as it then stands (owner remark of 2026-10-24).
- **Requirement refs**: RQ-TRC-067
- **ADR refs**: None
- **Acceptance Criteria**: Given the skill's scripts and page script, When the test lists their repeated literals, Then the
  list is empty; Given the whole test suite, Then it passes unchanged in behaviour.
- **Dependencies**: TASK-TRC-051
- **Assignee**: AI
- **Verification**: Pending.
- **Assumptions**: Tier M: the work stays inside one skill and adds no public behaviour; "duplicated" read as written more
  than once, with the exceptions of RQ-TRC-067.
