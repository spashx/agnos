# FTR-TRC-003: Traceability Quality Scorecard

## Overview
The "Gaps" view of the traceability page (FTR-TRC-001) lists nine breaches of the AGNOS traceability rules, one list
after the other. It answers a technician who wants the IDs to fix, but it gives a manager nothing to read: no verdict,
no measure of how bad each breach is, no comparison between features, and the last list ("Untraced functions") lies
below the fold. This feature replaces it with a **quality scorecard**, in the manner of the OpenSSF Scorecard: each
rule becomes a **check** scored from 0 to 10 against the population it applies to, the checks are weighted by risk,
and the page gives one overall **score** and **grade** (A to E) for the project and for each feature area (trigram).

The page has two kinds of reader, and the scorecard serves both from the same data:
- the **decision maker**, who reads the grade, a few charts and the three things to fix first, in under ten seconds,
  with no jargon and no scrolling;
- the **technician**, who opens a check (a chevron, compact or detailed) to see its rule, its figures and the elements
  that fail it, and clicks through to them.

The word "gap" disappears from the page, the generator's summary line, the data file and the documentation: it is
replaced by **Quality** (the view), **check** (a rule scored 0 to 10) and **finding** (an element that fails a check).
The checks are the existing rules of RQ-TRC-009 and RQ-TRC-035; no rule is added or removed, only scored and presented.
Out of scope: failing the generator's exit code on a low score (a CI gate), history of scores between runs, and
configuring the checks per project.

## Stakeholders
- **Owner**: the repository owner.
- **Consumers**: managers and product owners judging the state of a project's traceability; reviewers and developers
  fixing findings; agents reporting the score at the end of a session; the page (FTR-TRC-001) and its data file.

---

## Functional Requirements

### RQ-TRC-057: Quality vocabulary replaces "gap"
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The page, the generator's summary line, the data file and the skill's documentation SHALL call the
  former gap view the "Quality" view, a rule scored from 0 to 10 a "check", and an element that fails a check a
  "finding"; the word "gap" SHALL appear in none of them.
- **Rationale**: "gap" names a defect list, not a measure, and cannot carry a score that a manager reads.
- **Priority**: Must
- **Acceptance Criteria**: Given the generated page, its data file, its summary line and `SKILL.md`, When they are
  searched for "gap" without regard to case, Then there is no match; Given the page, Then the view tab, the sidebar
  section and the overview card are named Quality, and a check's failing elements are called findings.
- **Dependencies**: RQ-TRC-009, RQ-TRC-015, RQ-TRC-017, RQ-TRC-035, RQ-TRC-045

### RQ-TRC-058: Each rule is a scored check
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The trace generator SHALL compute, for each of the nine rules (requirements covered; requirements with
  a task; tasks with a requirement; ADRs with a requirement; IDs defined; containers not empty; elements connected;
  source files traced; functions traced, with a call graph), the size of its population, its count of findings, and a
  score from 0 to 10 equal to ten times the share of the population that is not a finding, rounded to one decimal; a
  check whose population is empty SHALL have no score and SHALL count for nothing.
- **Rationale**: a share of the population is comparable between projects of any size; a raw count is not.
- **Priority**: Must
- **Acceptance Criteria**: Given a fixture with 10 requirements of which 2 are uncovered, When the checks are computed,
  Then "requirements covered" has population 10, 2 findings and score 8.0; Given a fixture with no task, Then
  "tasks with a requirement" has no score.
- **Dependencies**: RQ-TRC-008, RQ-TRC-009, RQ-TRC-035

### RQ-TRC-059: Overall score and grade
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The trace generator SHALL give each check a risk level (critical, high, medium or low, as in the OpenSSF
  Scorecard, or informational for "functions traced"), compute the overall score as the average of the checks' scores
  weighted by their risk (10, 7.5, 5, 2.5, and 0 for informational), and map it to a grade A to E by thresholds; the
  same SHALL be computed for each trigram from its own elements; the weights and thresholds SHALL be data of one file,
  not of the code.
- **Rationale**: one verdict for the project and one per feature area lets a manager compare and decide where to act.
- **Priority**: Must
- **Acceptance Criteria**: Given the checks of the fixture, When the overall score is computed, Then it equals the
  weighted average of the scored checks by hand; Given the thresholds A 9, B 7.5, C 6, D 4, Then 9.0 is A, 8.9 is B and
  3.9 is E; Given two trigrams, Then each has its own score and grade.
- **Dependencies**: RQ-TRC-058, RQ-TRC-018

### RQ-TRC-060: A report card for the decision maker
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE the Quality view is open, the page SHALL show at its top a report card holding the project's grade
  as a large letter on the A to E scale with the current grade marked, its score out of 10, a one-sentence verdict in
  plain words (for example "Good: 2 checks need attention"), the grade of each trigram, and the three lowest-scored
  checks as "Fix first", each linking to its check.
- **Rationale**: a manager must be able to read the state and the next action without opening a single check.
- **Priority**: Must
- **Acceptance Criteria**: Given the fixture, When the Quality view opens, Then the report card shows a grade letter,
  a score, a verdict sentence, one grade per trigram and three "Fix first" links; When a "Fix first" link is clicked,
  Then the matching check is shown opened.
- **Dependencies**: RQ-TRC-059, RQ-TRC-062

### RQ-TRC-061: Charts with tooltips
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The Quality view SHALL draw, as inline SVG with no library, a radar of the checks' scores (one axis per
  check), a bar of each trigram's score, and the requirement coverage as covered, indirect and uncovered shares, each
  with a tooltip on hover and on keyboard focus that gives the item's name, its score or share, its population and its
  count of findings.
- **Rationale**: a shape is read faster than a table, and a tooltip answers "what is this point" without leaving it.
- **Priority**: Should
- **Acceptance Criteria**: Given the fixture, When the Quality view opens, Then it holds a radar with one axis per scored
  check, a bar per trigram and a coverage chart; When the pointer rests on a radar point, Then a tooltip gives the
  check's name, score, population and findings count; When a radar axis is clicked, Then the matching check is shown
  opened.
- **Dependencies**: RQ-TRC-018, RQ-TRC-045, RQ-TRC-058

### RQ-TRC-062: Checks, compact or detailed
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the user presses the chevron of a check (or "Expand all" or "Collapse all"), the page SHALL
  switch it between its compact form (name, risk level, score bar and count of findings, on one line) and its
  detailed form (the rule in words, the formula with its population and findings, the KPIs of the check, and the
  findings, the first sixty at first and the rest on request, each linking to its element); the checks SHALL stand
  in a grid, the lowest score first (the informational check last), all compact when the view opens.
- **Rationale**: the technician needs the detail of one check at a time, and the overview of all of them at once.
- **Priority**: Must
- **Acceptance Criteria**: Given the Quality view, When it opens, Then every check is compact; When a chevron is pressed,
  Then that check shows its rule, figures and findings and the others stay compact; When "Expand all" is pressed, Then
  every check is detailed; When a finding is clicked, Then its element is selected.
- **Dependencies**: RQ-TRC-009, RQ-TRC-016, RQ-TRC-058

### RQ-TRC-063: No scrolling to see everything that matters
- **Category**: Non-Functional
- **NFR Type**: Usability
- **EARS Type**: Ubiquitous
- **Statement**: The Quality view SHALL show, without vertical scrolling in a 1440 by 900 window, the report card, the
  charts and all the checks in compact form, "functions traced" included.
- **Metric**: no scroll height in the Quality view's main area at 1440 by 900 with the call graph on (nine checks).
- **Measurement Method**: headless browser at that window size on the fixture and on a project with five trigrams; the
  main area's scroll height does not exceed its client height.
- **Priority**: Must
- **Acceptance Criteria**: Given a 1440 by 900 window and the fixture with the call graph, When the Quality view opens,
  Then the main area has no vertical scrollbar and the "Functions traced" check is visible.
- **Dependencies**: RQ-TRC-060, RQ-TRC-061, RQ-TRC-062

### RQ-TRC-064: One score everywhere
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The score and grade SHALL be computed once, by the generator, and written to the data file; the page
  SHALL read them from there for the Quality view, the overview card, the sidebar section and the view tab (which shows
  the grade), and the generator's summary line SHALL end with them and with the checks' scores.
- **Rationale**: a page, a CSV reader and an agent must never show two different scores.
- **Priority**: Must
- **Acceptance Criteria**: Given the fixture, When the generator runs, Then its last line gives the grade, the score and
  the score of each check, the data file holds the same numbers, and the page shows them unchanged in the overview, the
  sidebar and the Quality view.
- **Dependencies**: RQ-TRC-010, RQ-TRC-017, RQ-TRC-059, RQ-TRC-015

---

## Non-Functional Requirements

### RQ-TRC-065: Grades readable by everyone
- **Category**: Non-Functional
- **NFR Type**: Accessibility
- **EARS Type**: Ubiquitous
- **Statement**: The Quality view SHALL never convey a grade or a score by colour alone (the letter or the figure is
  always written), SHALL use a five-step grade palette from the design tokens that follows the green-to-red scale of the French
  food (Nutri-Score) and energy (DPE) labels, which everybody reads (amended by the owner on 2026-10-24; the letter
  always written keeps it readable by colour-blind readers), SHALL meet the contrast of WCAG 2.1 AA in both themes, and SHALL give every chart a text alternative and every control a keyboard
  path.
- **Metric**: contrast ratio of at least 4.5:1 for the grade letters and the figures in both themes; no information
  carried by hue only.
- **Measurement Method**: contrast computed from the resolved tokens of both themes; a test that every chart holds a
  title and description and that every chevron and chart item is focusable.
- **Priority**: Must
- **Acceptance Criteria**: Given the tokens of both themes, When the contrast of each grade letter on its background is
  computed, Then it is at least 4.5:1; Given the charts, Then each has an accessible name and description.
- **Dependencies**: RQ-TRC-018, ADR-TRC-002

### RQ-TRC-066: The scorecard stays fast
- **Category**: Non-Functional
- **NFR Type**: Performance
- **EARS Type**: Ubiquitous
- **Statement**: The scorecard SHALL add less than 5 % to the generator's time and less than 2 % to the page's size on
  the 20,000-function project of RQ-TRC-037, and the Quality view SHALL be drawn in less than 200 ms on it.
- **Metric**: generator time and page size growth; time to draw the Quality view.
- **Measurement Method**: the skill's performance test (`AGNOS_TRACE_PERF=1`) before and after, and the page's drawing time
  measured in the headless browser.
- **Priority**: Should
- **Acceptance Criteria**: Given the generated 20,000-function tree, When the generator runs and the Quality view opens,
  Then the growth and the drawing time are below the metrics.
- **Dependencies**: RQ-TRC-037, RQ-TRC-038, RQ-TRC-064

### RQ-TRC-067: No duplicated literal in the skill's code
- **Category**: Non-Functional
- **NFR Type**: Maintainability
- **EARS Type**: Ubiquitous
- **Statement**: The scripts and the page script of the skill SHALL declare as a named constant every string of four
  characters or more and every number other than 0, 1 and 2 that they write more than once, apart from docstrings,
  comments, user-facing text of one place and test files.
- **Metric**: number of repeated string or number literals per script; 0.
- **Measurement Method**: a test that reads each script (Python by syntax tree, the page script by a tokenizer) and lists
  the repeated literals.
- **Priority**: Must
- **Acceptance Criteria**: Given the skill's scripts and page script, When the test lists their repeated literals, Then the
  list is empty.
- **Dependencies**: RQ-TRC-021
