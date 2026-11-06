# FTR-TRC-004: Delivery Tab
<!-- Amended on 2026-10-31: the skill, its script and its outputs carry their current names (RQ-TRC-104, RQ-TRC-105, DEC-TRC-055). -->

## Overview
With `--history` (FTR-HST-001), the traceability page tells who changed what, but not what was **delivered**. The owner
wants to compare how much was delivered between two periods (last week against three weeks ago, before and after a
change of agent or of practice), by tier of task and by identity, human or agent. The measure is **throughput**, not
time: git records when a task is closed (its status turns to Done in the commit of `commit-task`), never when its
execution began, since an AGNOS task is committed once, at its end; any duration read from git would count pauses,
waits and the DoR discussion (owner decision of 2026-10-27). The tab therefore counts the tasks delivered, weighs them
by tier, divides them by the days the identity was active, and shows the size and the rework of what was delivered.

Periods are chosen within the history the generator read (`--history-since`, `--history-depth`), never beyond, and in
calendar grains (day, week, month): a session is not a usable unit, since one branch may hold several sessions of any
size and trigram (owner decision of 2026-10-27).
Out of scope: any duration or workload per task; a new commit or field to record a task's start; comparison of
projects with each other; a score or a grade of delivery.

## Stakeholders
- **Owner**: the repository owner.
- **Consumers**: developers and leads comparing their delivery between periods, agents and practices; agents reporting
  what a session delivered; the page (FTR-TRC-001, FTR-HST-001) and its data file.

---

## Functional Requirements

### RQ-TRC-068: A delivered task, read from git
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: With `--history`, the trace generator SHALL take as the **delivery** of a task the first commit of the
  history read that turns the `**Status**` line of the task's definition to `Done`; its date SHALL be that commit's
  author date, its **deliverers** the commit's identities (author and co-authors, as merged by RQ-HST-004), its **tier**
  the task's `**Tier**` line, marked **re-tiered** when a commit of the history changed that line; a task whose status
  later left `Done`, whose status line carries more than its value, or that was `Done` from the commit that created it
  SHALL be **set aside** with that reason and counted in no figure.
- **Rationale**: the close of a task is the only event git records without ambiguity; what cannot be measured is shown,
  not guessed.
- **Priority**: Must
- **Acceptance Criteria**: Given a fixture where TASK-A turns from Not Started to Done in commit 3 by an agent with a
  human co-author, When the generator runs with `--history`, Then TASK-A is delivered on commit 3's date by both
  identities with its tier; Given TASK-B created Done, TASK-C turned Done then In Progress, TASK-D "Done (by the human)",
  Then each is set aside with its reason.
- **Dependencies**: RQ-HST-002, RQ-HST-004, RQ-HST-005, ADR-HST-001

### RQ-TRC-069: Delivery data in the data file
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE `--history` is given, the data file SHALL hold a `delivery` block with each delivered or set-aside
  task (ID, tier, re-tiered, delivery commit, lines changed by it, commit type read from its subject, rework, reason
  set aside) and the active days of each identity (the days, in the history read, with at least one commit it authored
  or co-authored); without `--history` the data file SHALL be unchanged.
- **Rationale**: an agent or another tool can report the delivery without the page, and the page filters without
  running the generator again.
- **Priority**: Must
- **Acceptance Criteria**: Given the fixture, When the generator runs with `--history`, Then `delivery` lists TASK-A to
  TASK-D and each identity's active days; When it runs without `--history`, Then the data file is byte-identical to the
  one before this feature.
- **Dependencies**: RQ-TRC-068, RQ-HST-006

### RQ-TRC-070: Points and throughput
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The page SHALL weigh each delivered task by the points of its tier (S 1, M 3, L 8 by default, data of
  one file of the skill, not of the code) and SHALL compute, for a period and an identity, the **throughput** as the
  points delivered divided by the active days in that period; a day at the edge of the history read that the history
  may cover only in part SHALL not count as an active day.
- **Rationale**: ten S tasks are not three L tasks, and a week of two working days must not read as a slow week.
- **Priority**: Must
- **Acceptance Criteria**: Given an identity delivering one L and two S tasks over 2 active days, When the period holds
  them, Then its points are 10 and its throughput 5.0; Given the weight of L changed to 5 in the data file, Then its
  points are 7 with no code change.
- **Dependencies**: RQ-TRC-069

### RQ-TRC-071: Rework
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN a commit of type `fix` cites a delivered task, or a requirement that task cites, within the days
  after its delivery given by the skill's delivery data file (14 by default), the trace generator SHALL mark that task
  as **reworked**, and the page SHALL show the rework rate of a period as the reworked tasks divided by the delivered
  tasks.
- **Rationale**: a throughput gained at the cost of corrections must show.
- **Priority**: Should
- **Acceptance Criteria**: Given TASK-A delivered on day 1 citing RQ-X and a `fix(...)` commit citing RQ-X on day 5,
  Then TASK-A is reworked; Given the same commit on day 20, Then it is not.
- **Dependencies**: RQ-TRC-068

### RQ-TRC-072: Two periods within the history read
- **Category**: Functional
- **EARS Type**: Complex
- **Statement**: The Delivery tab SHALL compare a period A with a period B, each chosen among ready-made ranges (last 7
  days, previous week, last 30 days…) or as two dates; WHILE a ready-made range reaches beyond the first or the last
  commit read, the page SHALL disable it and say why in its tooltip; IF a date entered lies outside the history read,
  THEN the page SHALL refuse it and say so, never move it silently; by default A SHALL be the last week read and B the
  week before, or the two halves of the history read when it is shorter than two weeks; the tab SHALL state the history
  read (its first and last dates, and the generator's limits, shallow clone included).
- **Rationale**: a period beyond the history read would show deliveries as missing that were simply not read.
- **Priority**: Must
- **Acceptance Criteria**: Given a history read from 2026-09-15 to 2026-10-27, When the tab opens, Then A is
  2026-10-21 to 2026-10-27 and B 2026-10-14 to 2026-10-20, "last 90 days" is disabled with a tooltip, and a date of
  2026-09-01 is refused with a message.
- **Dependencies**: RQ-HST-001, RQ-TRC-069

### RQ-TRC-073: Calendar grain
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The Delivery tab SHALL group deliveries over time by day, by week, or by month, the month being offered
  only when the history read spans more than 12 weeks.
- **Rationale**: a calendar is the only unit that means the same for every repository; a session or a branch does not.
- **Priority**: Must
- **Acceptance Criteria**: Given a history read of 6 weeks, Then the grain offers day and week only; Given 20 weeks, Then
  it offers month too.
- **Dependencies**: RQ-TRC-072

### RQ-TRC-074: The Delivery tab and its figures
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE the data file holds a `delivery` block, the page SHALL show a Delivery tab after History and
  before Quality, whose top band gives, for A, for B and as a variation from B to A, the tasks delivered, the points,
  the throughput and the rework rate; without the block, the tab SHALL not show.
- **Rationale**: the answer to "did I deliver more" must be readable before any chart.
- **Priority**: Must
- **Acceptance Criteria**: Given the fixture page, Then the tabs read History, Delivery, Quality in that order and the
  band shows four figures for A, B and their variation; Given a page generated without `--history`, Then there is no
  Delivery tab.
- **Dependencies**: RQ-TRC-070, RQ-TRC-071, RQ-TRC-072
- **Amendment**: Amended by RQ-TRC-092 and RQ-TRC-093 (FTR-TRC-006, 2026-10-30): a fifth figure, a variation said in words.

### RQ-TRC-075: Charts of the delivery
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE the Delivery tab is open, the page SHALL draw the throughput of each identity stacked by tier for
  A and B side by side, the points delivered over time in the chosen grain stacked by tier with A and B highlighted,
  and the lines changed per delivered task for each tier (median and quartiles) for A and B; each identity SHALL keep
  its colour and icon of the History tab (RQ-HST-026), and each mark SHALL raise a rich tooltip (RQ-HST-016).
- **Rationale**: the comparison is read at a glance only when the same identity looks the same everywhere.
- **Priority**: Must
- **Acceptance Criteria**: Given the fixture, When the tab opens, Then three charts are drawn, each identity's bars in
  its History colour, and hovering or focusing a bar shows its identity, period, tier, tasks and points.
- **Dependencies**: RQ-TRC-074, RQ-HST-016, RQ-HST-017, RQ-HST-026
- **Amendment**: Amended by RQ-TRC-083 (FTR-TRC-005, 2026-10-28): drawn by the charting library; tasks per tier replace lines per task.

### RQ-TRC-076: Filters of the delivery
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the user changes a filter of the Delivery tab (a text on the task's ID, title, plan and
  requirements; tags for the tiers, the kinds human, agent and together, the trigrams and the commit types; one or more
  identities; the inclusion of re-tiered tasks), the page SHALL apply it at once to the figures, the charts and the table.
- **Rationale**: the comparison is only fair on the same kind of work, such as features against fixes or one trigram.
- **Priority**: Must
- **Acceptance Criteria**: Given the fixture, When the tag L alone is on, Then the band, the charts and the table count
  L tasks only; When the text "TASK-A" is typed, Then only TASK-A is counted.
- **Dependencies**: RQ-TRC-074, RQ-HST-009
- **Amendment**: Amended by RQ-TRC-094 (FTR-TRC-006, 2026-10-30): the friction follows only the periods, trigrams and identities.

### RQ-TRC-077: The table of delivered tasks
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: The Delivery tab SHALL list the delivered tasks of A and B (ID, title, tier, deliverers, date, lines,
  rework), sortable and exportable as CSV, followed by the set-aside tasks with their reason; WHEN a task is clicked or
  chosen with the keyboard, the page SHALL select it in the detail panel, whose band SHALL then state its delivery
  (date, deliverers, tier, points).
- **Rationale**: every figure must lead to the tasks behind it.
- **Priority**: Must
- **Acceptance Criteria**: Given the fixture, Then the table lists TASK-A with its figures and TASK-B to TASK-D below
  with their reasons; When TASK-A is clicked, Then the detail panel selects it and states its delivery.
- **Dependencies**: RQ-TRC-074, RQ-TRC-013

---

## Non-Functional Requirements

### RQ-TRC-078: The delivery stays fast
- **Category**: Non-Functional
- **NFR Type**: Performance
- **EARS Type**: Ubiquitous
- **Statement**: On the generated repository of RQ-HST-013 with 1,000 delivered tasks, the delivery SHALL add less than
  2 seconds to the generation and less than 300 KB to the data file, the Delivery tab SHALL be drawn in less than 300
  ms, and a change of filter or period SHALL be redrawn in less than 100 ms.
- **Metric**: generation time and data size added by the delivery; drawing time of the tab; P95 of the redraw time over
  50 filter and period changes.
- **Measurement Method**: the skill's performance test (`AGNOS_PERF_CENTER_PERF=1`), times measured in the headless browser.
- **Priority**: Should
- **Acceptance Criteria**: Given the generated repository, When the performance test runs, Then each measure is under
  its threshold.
- **Dependencies**: RQ-HST-013, RQ-TRC-069
- **Amendment**: owner decision of 2026-10-31 (TASK-TRC-084): the redraw limit goes from 50 ms to 100 ms.

### RQ-TRC-079: A readable delivery view
- **Category**: Non-Functional
- **NFR Type**: Usability
- **EARS Type**: Ubiquitous
- **Statement**: The Delivery tab SHALL take every colour, size, spacing, stroke and duration from the design tokens of
  the page (RQ-TRC-018, ADR-TRC-002), in both themes; SHALL never tell a tier, a period or an identity by colour alone;
  SHALL meet the contrast of WCAG 2.1 AA; and SHALL give every control, bar and row a keyboard path and an accessible
  name.
- **Metric**: no raw visual literal in the page's code for the tab; contrast of at least 4.5:1 for text and 3:1 for marks.
- **Measurement Method**: the skill's literal test on `matrix.css` and `matrix.js`; the contrast test on the resolved
  tokens; a keyboard walk in the page test.
- **Priority**: Must
- **Acceptance Criteria**: Given the page code, Then no raw colour, `px` or `ms` is found; Given both themes, Then every
  text and mark of the tab meets its contrast; Given the keyboard only, Then every control and bar is reached.
- **Dependencies**: RQ-TRC-018, RQ-HST-014, ADR-TRC-002
- **Amendment**: Amended by RQ-TRC-087 (FTR-TRC-005, 2026-10-28) for the charts drawn by the library.
