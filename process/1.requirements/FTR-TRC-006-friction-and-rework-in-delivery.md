# FTR-TRC-006: Friction and Rework in the Delivery Tab

## Overview
Each AGNOS session closes by appending its friction counters to `process/_sessionstate/METRICS_LOG.md`, a file under
version control, but no view shows them. This feature adds a fifth figure to the Delivery band, the friction per session;
says in words whether each variation is better or worse; and draws the friction and the rework over the "Points over
time" chart, each behind a tag that shows or hides it (owner decisions of 2026-10-30).

Unchanged: the format of the log and how a session writes it, the definition of rework (RQ-TRC-071), the other charts,
the table of delivered tasks.
Out of scope: linking a task to a session (sessions were not all logged, so the commits between two rows are not one
session's work); weighting the counters; a filter of the friction by tier, commit type, kind or text.

## Stakeholders
- **Owner**: the repository owner.
- **Consumers**: readers of the Delivery tab.

---

## Functional Requirements

### RQ-TRC-090: The friction log read from git
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE the generator reads the history and the log `_sessionstate/METRICS_LOG.md` of the process folder
  is committed at HEAD, the generator SHALL write in the `delivery` block one entry per row of the log at HEAD: its
  date, its trigram, its four counters read by position, and the commit that added the row; a row whose commit is outside
  the history read SHALL be left out.
- **Rationale**: the same commit gives the same page, and the commit tells who closed the session.
- **Priority**: Must
- **Acceptance Criteria**: Given a log whose second row was added by commit C, When the page is generated with
  `--history`, Then the block holds both rows and the second names C; Given headers named differently but the same
  column order, Then the counters are the same; Given a row removed in a later commit, Then it is absent; Given a row
  not committed, Then it is absent.
- **Dependencies**: RQ-TRC-069, RQ-HST-001

### RQ-TRC-091: A log that cannot be read
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: IF a row of the log does not hold a date, a trigram and four whole numbers, or its commit is a merge,
  THEN the generator SHALL leave it out and name it on its error stream, without failing; IF no log is committed, THEN
  the `delivery` block SHALL hold no friction entry and the generator SHALL still succeed.
- **Rationale**: an unreadable row counted as zero would read as a session without friction.
- **Priority**: Must
- **Acceptance Criteria**: Given a row `| 2026-10-30 | TRC | x | 1 | 0 | 1 |`, When generating, Then exit 0, the row is
  absent and the error stream names it; Given no log, Then exit 0 and no friction entry.
- **Dependencies**: RQ-TRC-090

### RQ-TRC-092: The friction figure
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE the `delivery` block holds a friction entry, the Delivery band SHALL show after Rework a fifth
  figure, "Friction per session": the sum of the four counters of the sessions of a period divided by those sessions,
  for A, for B and as a variation from B to A, a fall being better; a period without a session SHALL read "—"; its
  tooltip SHALL give the sessions and each counter of A and B. Without any entry, the band SHALL keep its four figures.
  Amends RQ-TRC-074.
- **Rationale**: per session rather than per task, because a task cannot be linked to a session.
- **Priority**: Must
- **Acceptance Criteria**: Given 7 sessions totalling 47 events in A and none in B, Then the figure reads 6.7 for A, "—"
  for B and "—" as variation; Given a log with no row, Then the band has four figures.
- **Dependencies**: RQ-TRC-074, RQ-TRC-090, RQ-HST-016

### RQ-TRC-093: A variation said in words
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The Delivery band SHALL write beside each non-zero variation the word "better" or "worse", from what the
  figure measures and not from its sign: a rise is better for the tasks, the points and the throughput, a fall is better
  for the rework and the friction; a variation that is zero or cannot be computed SHALL have no word.
- **Rationale**: the two families of figures read in opposite directions, and colour alone does not say so.
- **Priority**: Must
- **Acceptance Criteria**: Given points rising, Then "better"; Given rework rising, Then "worse"; Given friction falling,
  Then "better"; Given no period B value, Then no word.
- **Dependencies**: RQ-TRC-074, RQ-TRC-087

### RQ-TRC-094: What filters the friction
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the user changes the periods, the trigram tags or the identities, the page SHALL apply them to the
  friction, an identity meaning the author of the row's commit; WHEN any other filter of the tab is on, the friction SHALL
  not change and the tooltip of its figure SHALL say which filters it ignores. Amends RQ-TRC-076.
- **Rationale**: the log knows a session, not its tiers or commit types; a count that seems filtered and is not would mislead.
- **Priority**: Must
- **Acceptance Criteria**: Given the tag TRC on, Then only TRC sessions count; Given the tag L on, Then the friction is
  unchanged and its tooltip names the tier filter.
- **Dependencies**: RQ-TRC-076, RQ-TRC-090

### RQ-TRC-095: Friction and rework over time
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE the Delivery tab is open, the chart "Points over time" SHALL draw on a second axis, per bucket of
  the grain, a circle for the friction events of its sessions and a diamond for its delivered tasks later reworked, placed
  at their delivery date and kept by every filter; a bucket without a value SHALL show no mark; a mark SHALL raise a
  tooltip giving, for the friction, each session's trigram, counters, author and commit. Amends RQ-TRC-083.
- **Rationale**: the cost of a delivery is read best beside that delivery.
- **Priority**: Must
- **Acceptance Criteria**: Given friction on 2026-10-29 and none on 2026-10-28, When the grain is day, Then one circle
  on the 29th and none on the 28th; Given a task delivered on day 1 and reworked on day 5, Then the diamond is on day 1;
  When the grain is week, Then the values add up per week.
- **Dependencies**: RQ-TRC-071, RQ-TRC-083, RQ-TRC-085, RQ-TRC-087, RQ-TRC-090, RQ-TRC-094

### RQ-TRC-096: Tags of the overlays
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the user toggles the tag Rework or Friction in the header of "Points over time", on by default, the
  page SHALL show or hide those marks and fit the second axis to what stays shown, without changing the figures or the
  table; IF no friction entry exists, THEN the tag Friction SHALL be disabled and its tooltip SHALL say why.
- **Rationale**: friction peaks would otherwise flatten the rework on a shared axis.
- **Priority**: Must
- **Acceptance Criteria**: Given friction peaking at 20 and rework at 3, When Friction is off, Then the axis ends near 3
  and the band is unchanged; Given no log, Then Friction is disabled with a tooltip.
- **Dependencies**: RQ-TRC-095, RQ-HST-009
