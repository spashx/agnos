# FTR-TRC-005: Charts from an Online Library
<!-- Amended on 2026-10-31: the skill, its script and its outputs carry their current names (RQ-TRC-104, RQ-TRC-105, DEC-TRC-055). -->
<!-- Amended on 2026-11-06: RQ-TRC-082's notice of the libraries, their versions and licences stands in the Help dialog's Licenses topic, no longer in the foot of the page (RQ-TRC-109, RQ-TRC-111, RQ-TRC-112, DEC-TRC-058). -->

## Overview
The charts of the traceability page are drawn by hand in inline SVG (DEC-TRC-035, DEC-TRC-039). At the owner's review of
2026-10-28, the Delivery band of figures was kept, but its three charts were found hard to read: fonts too large, tiers
written S, M, L with no meaning, a "Lines per task" chart nobody could read; the Quality radar "Checks" is no clearer; in
the History timeline, marks of several commits close in time overlap and hide each other. This feature draws the
Delivery charts and the Quality radar with a recognised charting library, Apache ECharts, loaded with the graph library
(Cytoscape.js) from an online CDN (cdnjs) at pinned versions checked by their integrity hash, instead of copying a
library into the skill and the page (owner decision of 2026-10-28); and it merges overlapping History marks.

Unchanged: Overview, Graph (but for how Cytoscape.js is loaded), Matrix, the History timeline (but for its overlapping
marks), the Delivery band of figures, the rest of the Quality view, the data files.
Out of scope: a local copy of the libraries as a fallback; any other chart.

## Stakeholders
- **Owner**: the repository owner.
- **Consumers**: readers of the Delivery and Quality views; readers of the History timeline; anyone opening the page.

---

## Functional Requirements

### RQ-TRC-080: Libraries from an online CDN
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The page SHALL load Cytoscape.js and Apache ECharts from `cdnjs.cloudflare.com`, each at one exact
  version with its Subresource Integrity hash and `crossorigin="anonymous"`, before its own script; besides these two
  scripts and its sibling `<page>.data.js`, the page SHALL request nothing. Amends RQ-TRC-010.
- **Rationale**: a recognised library draws readable charts; loading it online keeps the skill and the page light
  (owner decision of 2026-10-28).
- **Priority**: Must
- **Acceptance Criteria**: Given a generated page, When its `<script src` are listed, Then they are the two cdnjs URLs,
  each with an `integrity` and `crossorigin="anonymous"`, and `<page>.data.js`; and no `<link` nor `url(http` is found.
- **Dependencies**: RQ-TRC-010, RQ-TRC-082

### RQ-TRC-081: Without the network
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: IF a library cannot be loaded (no network, CDN unreachable, integrity mismatch), THEN the page SHALL show,
  in place of each view or chart that needs it, a message naming the library and saying that a connection is needed,
  and every other view (Overview, Matrix, the History timeline, the Delivery figures and table, the Quality checks, the
  detail panel) SHALL work.
- **Rationale**: a page opened without network must still answer what it can, and say plainly what it cannot.
- **Priority**: Must
- **Acceptance Criteria**: Given a page whose library URLs fail, When it opens, Then the Graph view and each library
  chart show the message naming its library, and the Matrix, the Delivery figures and the Quality checks are filled.
- **Dependencies**: RQ-TRC-080

### RQ-TRC-082: Library record
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The skill SHALL record in one data file, for each library, its name, exact version, URL, integrity hash
  and licence, and the generator SHALL write the page's library scripts and the licence notice from that file only.
  Replaces RQ-TRC-024.
- **Rationale**: one place to read and to change what the page loads.
- **Priority**: Must
- **Acceptance Criteria**: Given the data file, When a page is generated, Then each library script of the page carries
  the recorded URL and hash, and the page names each library with its version and licence; Given a version changed in
  the data file only, Then the page loads that version.
- **Dependencies**: RQ-TRC-080

### RQ-TRC-083: Readable Delivery charts
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE the Delivery tab is open, the page SHALL draw with the charting library: the points per active
  day of each identity stacked by tier, A beside B; the points delivered over time in the chosen grain, stacked by tier,
  with A and B marked and a zoom on the time axis; and the tasks delivered per tier, A beside B. Every tier SHALL be
  named in full in the legends and the tooltips (its letter, its meaning and its points, such as "S, small task, 1
  point"), and every text of the charts SHALL use the page's caption and small sizes. Amends RQ-TRC-075 (the "lines
  changed per task" chart is removed; the lines stay in the table).
- **Rationale**: a reader must understand a chart without knowing the AGNOS tiers or the data file.
- **Priority**: Must
- **Acceptance Criteria**: Given the fixture, When the tab opens, Then three library charts are drawn, their legends
  read "S, small task, 1 point", "M, medium task, 3 points", "L, large task, 8 points", the third chart has one A and
  one B value per tier, and the font size of their texts is the page's caption or small size.
- **Dependencies**: RQ-TRC-075, RQ-TRC-080, RQ-TRC-085
- **Amendment**: owner review of 2026-10-28 (TASK-TRC-070): period A and period B each have one colour of the design
  system, shown first in the tab's header (the period marks and the band of figures) and reused by the charts; a
  tier is a shade of its period's colour (light S, medium M, full L); the points over time keep their form, their
  columns neutral and the A and B areas in the periods' colours; no identity colour and no pattern in these charts.

- **Amendment**: Amended by RQ-TRC-095 and RQ-TRC-096 (FTR-TRC-006, 2026-10-30): friction and rework marks over the points over time.

### RQ-TRC-084: Readable checks radar
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE the Quality view is open, the page SHALL draw the checks radar with the charting library: one axis
  per scored check named by its short title, the scores out of 10, a tooltip giving the check, its score, its risk and
  its findings, and a click on an axis or a point opening that check. Amends RQ-TRC-061 for the radar; its bars and
  shares stay as they are.
- **Rationale**: the radar is the decision maker's first chart; its labels and values must be read at a glance.
- **Priority**: Must
- **Acceptance Criteria**: Given the fixture, When the Quality view opens, Then the radar has one indicator per scored
  check with its score, and choosing a check's point opens that check.
- **Dependencies**: RQ-TRC-061, RQ-TRC-080, RQ-TRC-085

### RQ-TRC-085: Library charts in the design system
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: The page SHALL give the charting library its colours, font family, font sizes and strokes from the
  design tokens of the page, in the current theme, and WHEN the theme changes, the page SHALL draw the library charts
  again in the new theme. Identities SHALL keep their History colour.
- **Rationale**: a library chart must look like the rest of the page (RQ-TRC-018).
- **Priority**: Must
- **Acceptance Criteria**: Given the light theme then the dark one, When a library chart is drawn, Then its text colour
  and font family equal the page's resolved tokens in each theme; Given the code, Then no raw colour, size or duration
  is written for the library.
- **Dependencies**: RQ-TRC-018, RQ-HST-026

### RQ-TRC-086: Overlapping History marks merged
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN two or more marks of one row of the History timeline would overlap at the current zoom, the page
  SHALL draw them as one group mark showing the count of its commits, of the kind of its commits (human, agent or
  together, or mixed when they differ), whose tooltip lists its commits and whose activation zooms on them; zooming in
  SHALL split a group as its marks stop overlapping. The count SHALL be written beside the symbol, in the text colour,
  never on a mark's colour, and all marks of a kind SHALL have one size, the lines changed being read in the tooltip
  (owner decision of 2026-10-30). A group SHALL take the colours of its identities only when its
  commits all have the same contributors of its kind, and neutral design-system colours otherwise. A group of mixed kinds
  SHALL be a rounded square, a shape used for nothing else. IF the view cannot zoom further on a group, THEN activating
  it SHALL select its newest commit.
- **Rationale**: overlapping marks hide each other, and a colour must always name someone.
- **Priority**: Should
- **Acceptance Criteria**: Given a row with three commits within one hour and the whole history in view, Then one group
  mark reading 3 is drawn; When the view is zoomed on that hour, Then three marks are drawn. Given a group of two humans,
  Then its mark is neutral; Given a group of one human, Then it has that human's colour; Given a human commit and an agent
  commit grouped, Then the mark is the mixed rounded square.
- **Dependencies**: RQ-HST-007, RQ-HST-014, RQ-TRC-089

### RQ-TRC-089: A "together" mark a circle holding a diamond
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: The page SHALL draw a commit made by a human and an agent together as a circle in the human's colour
  holding a diamond in the agent's colour, outlined, with no ring and within the mark's radius, whichever of them is the
  git author. IF the two colours differ by less than a design-system threshold in OKLab, THEN the diamond SHALL take the
  design-system ink that contrasts most with the circle.
- **Rationale**: the two known shapes read without a legend, and a ring enlarges a mark and tangles with its neighbours.
- **Priority**: Should
- **Acceptance Criteria**: Given a commit by a human and an agent, Then a circle of the human's colour and a diamond of the
  agent's are drawn with no ring, also when the agent is the author; Given the two identities with the same colour, Then
  the diamond's colour differs from the circle's by at least the threshold, in both themes.
- **Dependencies**: RQ-HST-014, ADR-HST-001

---

## Non-Functional Requirements

### RQ-TRC-087: Accessible library charts
- **Category**: Non-Functional
- **NFR Type**: Accessibility
- **EARS Type**: Ubiquitous
- **Statement**: Each library chart SHALL have an accessible name and a description of its data, SHALL tell its series
  by pattern as well as by colour, SHALL be reached with the Tab key, and SHALL move between its data items with the
  arrow keys, each showing its tooltip, Enter activating it where a click does. Amends RQ-TRC-061 and RQ-TRC-079 for
  the library charts.
- **Metric**: accessible name and description present; pattern per series; every data item reached by keyboard.
- **Measurement Method**: page test in the headless browser: focus each chart, press the arrow keys, read the tooltip.
- **Priority**: Must
- **Acceptance Criteria**: Given the Delivery tab, When the first chart is focused and the right arrow pressed, Then the
  tooltip of its first data item shows; When Enter is pressed on a radar point, Then its check opens.
- **Dependencies**: RQ-TRC-061, RQ-TRC-079, RQ-TRC-083, RQ-TRC-084
- **Amendment**: owner review of 2026-10-28 (TASK-TRC-070): patterns were found unreadable; a series is told by its
  legend's text, its fixed place (A before B) and the value written on its bar, as well as by its colour.

### RQ-TRC-088: Speed with the libraries
- **Category**: Non-Functional
- **NFR Type**: Performance
- **EARS Type**: Ubiquitous
- **Statement**: With the libraries in the browser's cache, the page SHALL keep the thresholds of RQ-TRC-078 for the
  Delivery tab, and the Quality view SHALL be drawn in less than 300 ms.
- **Metric**: drawing time of the Delivery tab and of the Quality view; P95 of the redraw time over 50 filter changes.
- **Measurement Method**: the skill's performance tests (`AGNOS_PERF_CENTER_PERF=1`), times measured in the headless browser
  after a first load.
- **Priority**: Should
- **Acceptance Criteria**: Given 1,000 delivered tasks, Then the tab is drawn in less than 300 ms and the P95 is under
  100 ms; Given the fixture, Then the Quality view is drawn in less than 300 ms.
- **Dependencies**: RQ-TRC-078, RQ-TRC-080
- **Amendment**: owner decision of 2026-10-31 (TASK-TRC-084): the P95 limit goes from 50 ms to 100 ms; 64 to 77 ms were measured with the libraries on 1,000 tasks.
