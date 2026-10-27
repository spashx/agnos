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
- **Status**: Not Started
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
- **Verification**: 
- **Assumptions**: 

### TASK-TRC-058: Points, throughput, rework rate and periods in the page
- **Tier**: M
- **Status**: Not Started
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
- **Verification**: 
- **Assumptions**: 

### TASK-TRC-059: The Delivery tab, its toolbar, filters and figures
- **Tier**: M
- **Status**: Not Started
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
- **Verification**: 
- **Assumptions**: 

### TASK-TRC-060: The three charts of the delivery
- **Tier**: M
- **Status**: Not Started
- **Description**: Inline-SVG charts: throughput per identity stacked by tier for A and B, points over time in the
  grain with A and B highlighted, lines per task by tier; History's identity colours and icons; rich tooltips, keyboard.
- **Requirement refs**: RQ-TRC-075, RQ-TRC-079
- **ADR refs**: ADR-TRC-009 (DEC-TRC-039); ADR-TRC-002 (DEC-TRC-009, DEC-TRC-010)
- **Acceptance Criteria**: Given the fixture, When the tab opens, Then three charts are drawn, each identity in its
  History colour, and focusing a bar shows its identity, period, tier, tasks and points.
- **Dependencies**: TASK-TRC-059
- **Assignee**: AI
- **Verification**: 
- **Assumptions**: 

### TASK-TRC-061: The table, its CSV and the delivery in the detail panel
- **Tier**: M
- **Status**: Not Started
- **Description**: The sortable table of delivered tasks with its CSV and the set-aside rows; a click or Enter selects
  the task in the detail panel, whose band states its delivery.
- **Requirement refs**: RQ-TRC-077, RQ-TRC-079
- **ADR refs**: ADR-TRC-009 (DEC-TRC-039)
- **Acceptance Criteria**: Given the fixture, Then the table lists TASK-A and, below, TASK-B to TASK-D with their reasons;
  When TASK-A is clicked, Then the detail panel selects it and states its date, deliverers, tier and points.
- **Dependencies**: TASK-TRC-059
- **Assignee**: AI
- **Verification**: 
- **Assumptions**: 

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
