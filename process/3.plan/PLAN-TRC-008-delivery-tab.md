# PLAN-TRC-008: Delivery Tab

## Overview
A correction of the history's summary line first, then the Delivery tab of the traceability page: the tasks delivered
(their status turned to Done in git) counted by period, tier and identity, weighted by tier and divided by the active
days, compared between two periods chosen within the history read. Each step leaves the page and its tests working:
the data first, then the figures, the tab, the charts, the table, and last the speed and the documentation.

## References
- **Requirements**: RQ-HST-006 (TASK-TRC-055); RQ-TRC-068 to RQ-TRC-079
- **ADRs**: ADR-HST-001 (DEC-HST-004); ADR-TRC-009 (DEC-TRC-036 to DEC-TRC-039); ADR-TRC-002 (design system)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-TRC-055: One human, one agent, one commit in the history's summary line
- **Tier**: S
- **Status**: Done
- **Description**: The generator's last line wrote "1 humans" and "1 agents"; each count of the history's summary is now
  followed by its noun in the singular for one, in the plural otherwise.
- **Requirement refs**: RQ-HST-006
- **ADR refs**: ADR-HST-001 (DEC-HST-004)
- **Acceptance Criteria**: Given a history with 2 commits, 2 humans and 1 agent, When the generator ends, Then its last
  line holds "history: 2 commits, 2 humans, 1 agent".
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: N/A (Tier S). `python -m unittest discover -s tests` (skill folder): 254 tests, OK, 2 skipped.
- **Assumptions**: the expected line of `test_history.py` changed to "1 agent", as the corrected behaviour.

### TASK-TRC-056: The Delivery tab specified and decided
- **Tier**: M
- **Status**: Done
- **Description**: Write FTR-TRC-004 (RQ-TRC-068 to RQ-TRC-079) and ADR-TRC-009 (DEC-TRC-036 to DEC-TRC-039) from the
  owner's choices of 2026-10-27: throughput, not duration; periods within the history read; calendar grains, no session.
- **Requirement refs**: RQ-TRC-068 to RQ-TRC-079
- **ADR refs**: ADR-TRC-009 (DEC-TRC-036 to DEC-TRC-039)
- **Acceptance Criteria**: Given the two documents, When `agnos-index` runs, Then it lists RQ-TRC-068 to RQ-TRC-079 and
  DEC-TRC-036 to DEC-TRC-039 with no duplicate; Given the owner's review, Then ADR-TRC-009 is Accepted.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `agnos-index`: 360 entries, 45 documents, exit 0, the 12 RQ and 4 DEC listed; owner approval of
  2026-10-27 (AskUserQuestion), status Accepted. No code: no unit test.
- **Assumptions**: thresholds proposed without owner figures: points S 1, M 3, L 8; rework window 14 days; month grain
  beyond 12 weeks; RQ-TRC-078 limits (2 s, 300 KB, 300 ms, 50 ms).

### TASK-TRC-057: Deliveries and the `delivery` block from the history's log
- **Tier**: L
- **Status**: Done
- **Description**: In `history.py`, read the `**Status**` and `**Tier**` lines in each task's followed hunks, find each
  delivery, re-tier, reason set aside, commit type, rework and the active days; add `assets/delivery.json` and write the
  `delivery` block (tests first, on a fixture repository of four tasks).
- **Requirement refs**: RQ-TRC-068, RQ-TRC-069, RQ-TRC-071
- **ADR refs**: ADR-TRC-009 (DEC-TRC-036, DEC-TRC-037)
- **Acceptance Criteria**: Given the fixture where TASK-A turns Done in commit 3 by an agent and a human, When the
  generator runs with `--history`, Then `delivery` holds TASK-A with commit 3, its tier, its lines and type; Given TASK-B
  created Done, TASK-C reopened, TASK-D "Done (by the human)", Then each is set aside with its reason; Given a `fix`
  commit citing TASK-A's requirement 4 days later, Then TASK-A is reworked; Given no `--history`, Then the data file is
  unchanged.
- **Dependencies**: TASK-TRC-056
- **Assignee**: AI
- **Verification**: `tests/test_delivery.py` written first (8 failures, `KeyError: 'delivery'`), then 9 tests OK: TASK-A
  commit "feat(ABC): TASK-ABC-001 one" by Alice and Claude, `("L", True, 2, "feat", None)`; created-done, reopened,
  annotated; active days per identity; settings equal to `delivery.json`; no `delivery` without `--history`; reworked
  on day 5, not on day 25. Whole suite: 263 tests OK, 2 skipped. XS56K, 6 weeks: 266 tasks (213 counted: M 166, L 36,
  S 11; created-done 52, annotated 1), whole run 2.6 s.
- **Assumptions**: rework read in the fix commit's subject only (ADR-TRC-009 DEC-TRC-036 amended); the tier is read
  with `- **Tier**: S|M|L` at the head of a line, else the task is set aside `no-tier`; the lines of a delivery are
  those of the scanned source files.

### TASK-TRC-058: Points, throughput, rework rate and periods in the page
- **Tier**: M
- **Status**: Done
- **Description**: Pure functions of `matrix.js` computing, from the `delivery` block and the filters, the points, the
  active days, the throughput, the rework rate and the grains of a period, and the bounds, defaults and refusals of the
  periods A and B.
- **Requirement refs**: RQ-TRC-070, RQ-TRC-071, RQ-TRC-072, RQ-TRC-073
- **ADR refs**: ADR-TRC-009 (DEC-TRC-038)
- **Acceptance Criteria**: Given one L and two S tasks over 2 active days, Then points 10 and throughput 5.0; Given a
  history from 2026-09-15 to 2026-10-27, Then A is the last week, B the one before, "last 90 days" disabled and
  2026-09-01 refused; Given 6 weeks, Then grains day and week only.
- **Dependencies**: TASK-TRC-057
- **Assignee**: AI
- **Verification**: `tests/test_delivery_page.py`, 8 tests OK in the headless browser: A 10 points over 3 active days,
  throughput 3.333, rework 0.333; B 3 over 1 day; variation 0.111; tag L "1,8,3,2.667"; text TASK-DEM-103 kept alone;
  per identity Alice L 8 over 1 day, Claude 10 over 3; bounds from 2026-09-16 (cut history) to 2026-10-27, A
  10-21..10-27, B 10-14..10-20; halves of a short history; "last-90" disabled, "last-30" enabled; 2026-09-01 refused,
  2026-13-45 not a date; grains "day,week" over 6 weeks, "day,week,month" over 21; Monday 2026-10-19 and month 2026-10.
  Whole suite: 271 tests OK, 2 skipped. Deviation: the functions were written before their tests (test-first rule not
  followed); the tests were written from the acceptance criteria and the figures computed by hand, not read from the code.
- **Assumptions**: a period's active days are the calendar days on which any identity kept by the filters worked (not
  person-days); a kind filter keeps the identities of that kind, "together" all of them; when the history read is cut
  (`since`, `depth`, shallow) its first day is left out of the periods; the default periods come from
  `delivery.json` (`defaultPeriods`).

### TASK-TRC-059: The Delivery tab, its toolbar, filters and figures
- **Tier**: M
- **Status**: Done
- **Description**: The tab between History and Quality, absent without `delivery`; its toolbar (periods, grain, text,
  tags, identities, re-tiered switch), the statement of the history read, and the band of four figures for A, B and
  their variation; tokens for every visual value.
- **Requirement refs**: RQ-TRC-072, RQ-TRC-074, RQ-TRC-076, RQ-TRC-079
- **ADR refs**: ADR-TRC-009 (DEC-TRC-039); ADR-TRC-002 (DEC-TRC-009, DEC-TRC-010)
- **Acceptance Criteria**: Given the fixture page, Then the tabs read History, Delivery, Quality and the band shows four
  figures for A, B and their variation; When tag L alone is on, Then the band counts L tasks only; Given a page without
  `--history`, Then there is no Delivery tab.
- **Dependencies**: TASK-TRC-058
- **Assignee**: AI
- **Verification**: `DeliveryTabTest` written first (6 failing), then 8 tests OK: tabs "overview,graph,matrix,history,delivery,
  quality"; no tab on a page without `delivery`; band tasks "3|1|2.000", points "10|3|2.333", throughput "3.333|3.000|
  0.111" written "+11 %", rework "0.333|0.000|" (no variation from zero); tag L "1|0|"; type tags "feat,fix,none";
  2026-09-01 refused, the first day kept at 2026-10-21, min/max 2026-09-16/2026-10-27; "last-90" disabled "beyond the
  history read"; every control named. Whole suite: 279 tests OK, 2 skipped (literal and token tests included).
  Screenshot of XS56K (6 weeks): the band A 57 tasks / 186 points / 31.0 per active day / 5 %, B 55 / 199 / 28.4 / 4 %;
  it first showed no band, a delivery commit with no type broke the tags: caught, fixed (type "none") and tested.
- **Assumptions**: variation from B to A as (A − B) / B, none when B is 0; for the rework a rise is worse; arrows and
  signs are written beside the colour; a reversed period (first day after last) is refused like a date outside.

### TASK-TRC-060: The three charts of the delivery
- **Tier**: M
- **Status**: Done
- **Description**: Inline-SVG charts: throughput per identity stacked by tier for A and B, points over time in the
  grain with A and B highlighted, lines per task by tier; History's identity colours and icons; rich tooltips, keyboard.
- **Requirement refs**: RQ-TRC-075, RQ-TRC-079
- **ADR refs**: ADR-TRC-009 (DEC-TRC-039); ADR-TRC-002 (DEC-TRC-009, DEC-TRC-010)
- **Acceptance Criteria**: Given the fixture, When the tab opens, Then three charts are drawn, each identity in its
  History colour, and focusing a bar shows its identity, period, tier, tasks and points.
- **Dependencies**: TASK-TRC-059
- **Assignee**: AI
- **Verification**: `DeliveryChartsTest` written first (5 failing), then 5 tests OK: charts "throughput,timeline,size", each
  `role="img"` and named; Claude's A bar `var(--c-history-identity-2)`, 10 points, 3.333, focusable, tooltip "Claude Opus
  5.5 / Period A / L: 1 task, 8 points / S: 2 tasks, 2 points / 3 active days"; Alice's B bar hatched; timeline 42 day
  columns, 7 weeks, last week 2026-10-26 with 1 point, spans a and b; S A quartiles 3.5:4:4.5 over 2 tasks, L A median
  40, M B 12, L B count 0; tag S leaves Claude's A bar 2 points. Delivery tests 30 OK; literal test OK. Screenshots of
  XS56K in both themes read: first version too small, names over the bars and tiers in L, M, S order (sorted keys of
  the data file): fixed (two columns, timeline full width, names cut at 20 characters, `tiers` order in `delivery.json`).
- **Assumptions**: a tier is told by the opacity of the identity's colour (tokens `delivery-tier-*-opacity`), with the
  legend and the tooltip writing it; the size chart shows the quartiles without whiskers; the timeline has no click
  (not required by RQ-TRC-075).

### TASK-TRC-061: The table, its CSV and the delivery in the detail panel
- **Tier**: M
- **Status**: Done
- **Description**: The sortable table of delivered tasks with its CSV and the set-aside rows; a click or Enter selects
  the task in the detail panel, whose band states its delivery.
- **Requirement refs**: RQ-TRC-077, RQ-TRC-079
- **ADR refs**: ADR-TRC-009 (DEC-TRC-039)
- **Acceptance Criteria**: Given the fixture, Then the table lists TASK-A and, below, TASK-B to TASK-D with their reasons;
  When TASK-A is clicked, Then the detail panel selects it and states its date, deliverers, tier and points.
- **Dependencies**: TASK-TRC-059
- **Assignee**: AI
- **Verification**: `DeliveryTableTest` written first (5 failing), then 5 tests OK: rows "TASK-DEM-101, TASK-DEM-001,
  TASK-DEM-103, TASK-DEM-104" by date, TASK-DEM-001's cells (title, L, 8, Alice, Claude Opus 5.5, 2026-10-22, A, 40);
  set aside "TASK-DEM-105:created-done", "Done from its creation"; Points sorted ascending (TASK-DEM-103 first,
  `aria-sort` ascending) then descending (TASK-DEM-001); click and Enter select TASK-DEM-001, the detail panel reads
  "Delivered on 2026-10-22 by Alice, Claude Opus 5.5: tier L, 8 points"; CSV header "Task,Title,Tier,Points,Delivered
  by,Date,Period,Lines,Reworked,Commit type", 4 lines, tag S leaves TASK-DEM-103 and 104. Whole suite: 289 tests OK, 2
  skipped. Screenshot of XS56K: 112 tasks in A and B, a row selected, its delivery in the detail panel.
- **Assumptions**: the table lists the tasks of A and B together, with a Period column; the set-aside rows follow the
  same periods and filters (reason aside); the fixture's TASK-DEM-102 became TASK-DEM-001, a task of the fixture's
  index, so that it can be selected; a sort header is reached with Tab and sorted with Enter.

### TASK-TRC-062: Speed, documentation and a run on XS56K
- **Tier**: M
- **Status**: Not Started
- **Description**: Extend the performance test to 1,000 delivered tasks, document the Delivery tab and `delivery.json`
  in `SKILL.md`, and generate the page of XS56K with `--call-graph --history --history-since 6.weeks`.
- **Requirement refs**: RQ-TRC-078, RQ-TRC-017
- **ADR refs**: ADR-TRC-009
- **Acceptance Criteria**: Given `AGNOS_TRACE_PERF=1`, Then each measure of RQ-TRC-078 is under its threshold; Given
  `SKILL.md`, Then it describes the tab, its rules and `delivery.json`; Given the XS56K run, Then exit 0 and the tab shows.
- **Dependencies**: TASK-TRC-060, TASK-TRC-061
- **Assignee**: AI
- **Verification**: 
- **Assumptions**: 
