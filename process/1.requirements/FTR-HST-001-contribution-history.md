# FTR-HST-001: Contribution History in the Traceability Page

## Overview
The traceability page (FTR-TRC-001) shows what is linked to what, at one moment. It does not show **who** made each
element and each piece of code, **when**, and whether a human, an agent, or both together did it. On a project run with
AGNOS, where humans and agents write requirements, decisions, plans and code side by side, that is the question a lead,
a reviewer or an auditor asks first: who worked on this requirement over time, and who wrote the code that implements
it?

This feature adds a **History** view to the page, built from the repository's git history, read from two angles:
1. **Requirements angle**: who worked on each process element (FTR, RQ, ADR, DEC, PLAN, TASK), and when; an
   intervention is a commit that changed the lines of the element's definition.
2. **Code angle**: who worked on each source file, or function with a call graph, and through the IDs that code cites,
   on which requirements.

Each angle is a navigable **timeline** of the interventions, filterable by identity and by kind (human or agent). The
view is reached from a new "History" tab of the main area, from a "History" section of the sidebar that lists the
identities, and from a "History" button of the detail panel that shows the history of the selected element. The
generator builds the view only when asked (`--history`), over a depth of history given as a duration, a number of
commits, or both.

An identity is the **author** of a commit (not its committer, who may be the person or service that merged or rebased
it), with the identities of one person merged; the co-authors named by the `Co-Authored-By` trailers are identities
too, and each identity is classed as a **human** or an **agent**, so that the interactions between humans and agents
can be analysed. Out of scope: statistics of productivity or ranking of people, editing the history, history of
uncommitted changes, configuring the classification per project from the command line, and the history of the scores
of FTR-TRC-003.

## Stakeholders
- **Owner**: the repository owner.
- **Consumers**: leads and product owners analysing how humans and agents collaborate on a project; reviewers and
  auditors tracing who wrote a requirement or its code; the page (FTR-TRC-001) and its data file; agents reporting at
  the end of a session.

---

## Functional Requirements

### RQ-HST-001: History options of the generator
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the trace generator is given `--history`, it SHALL build the history of the repository holding the
  process folder; WHEN it is also given `--history-since <date or duration>` (a form git accepts, such as `6.months`,
  `2.weeks` or `2026-01-01`), it SHALL read only the commits authored since then; WHEN it is given
  `--history-depth <n>`, it SHALL read only the `n` most recent commits; WHEN both are given, it SHALL apply both, the
  stricter one deciding; IF `--history-since` or `--history-depth` is given without `--history`, or `n` is not a
  positive integer, THEN it SHALL exit with code 1 and a message naming the option.
- **Rationale**: a duration is what a person reads; a number of commits bounds the generation time on a large
  repository; the history costs time and size, so it is built only when asked, as the call graph is.
- **Priority**: Must
- **Acceptance Criteria**: Given a repository of 30 commits over 3 months, When the generator runs with `--history
  --history-depth 10`, Then the history holds 10 commits; When it runs with `--history --history-since 1.month`, Then
  it holds only the commits of the last month; When both are given, Then it holds the commits that satisfy both; When
  `--history-depth 5` is given without `--history`, Then the exit code is 1 and the message names `--history`.
- **Dependencies**: RQ-TRC-001, RQ-TRC-002

### RQ-HST-002: Interventions on the process elements
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The trace generator SHALL count as an intervention on a process element every non-merge commit, within
  the history read, that added, changed or removed a line of the element's own definition (its line range in
  `INDEX.idx.md`), following the element's lines back through earlier versions of its file, across renames of the
  file and through merges, with the number of lines the commit changed in that range; a merge commit SHALL count for no
  element, and lines changed but not committed SHALL count for none.
- **Rationale**: one feature file holds many requirements; counting the commits of the whole file would credit everyone
  who touched any requirement of it with all of them.
- **Priority**: Must
- **Acceptance Criteria**: Given a feature file with RQ-A on lines 5 to 10 and RQ-B on lines 12 to 20, and a commit by
  Alice that changed line 7 only, When the history is built, Then Alice has one intervention on RQ-A and none on RQ-B;
  Given a later commit that inserted 3 lines above RQ-A, Then Alice's intervention is still on RQ-A; Given the file
  renamed by a third commit, Then Alice's intervention is kept; Given a merge commit, Then it is the intervention of no
  element; Given an uncommitted change, Then it is no intervention.
- **Dependencies**: RQ-HST-001, RQ-TRC-003, RQ-TRC-004

### RQ-HST-003: Interventions on the code
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The trace generator SHALL count as an intervention on a scanned source file every non-merge commit,
  within the history read, that changed the file, with its number of changed lines; WHILE a call graph is built
  (`--call-graph`), it SHALL also count as an intervention on a function every non-merge commit that changed a line of
  the function's range, as in RQ-HST-002; and the page SHALL attribute the interventions on a file, or a function when
  there is one, to each ID that this file or function cites.
- **Rationale**: the code angle answers "who wrote the code of this requirement", which the IDs cited by the code tell.
- **Priority**: Must
- **Acceptance Criteria**: Given a file citing RQ-A in a function `f` and RQ-B in a function `g`, and a commit by Bob
  that changed only `g`, When the history is built with a call graph, Then Bob has an intervention on the file, on `g`
  and, through `g`, on RQ-B, and none on `f` or RQ-A; When it is built without a call graph, Then Bob's intervention is
  on the file and through it on RQ-A and RQ-B.
- **Dependencies**: RQ-HST-001, RQ-TRC-006, RQ-TRC-007, RQ-TRC-031

### RQ-HST-004: One identity per person
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The trace generator SHALL take the author of a commit, not its committer, apply the repository's
  `.mailmap` when there is one, and merge into one identity all the human authors and co-authors that share an e-mail
  address (ignoring case), and the agents that share a name and an e-mail address (ignoring case), since the models of
  one vendor share a no-reply address (found on this repository on 2026-10-24), keeping every name and address seen for it, its most frequent name as its display name, and the way
  it was merged (by e-mail, by `.mailmap`).
- **Rationale**: the same person often commits under two names, and a merge made by a hosting service has that service
  as committer; counting either as a person would mislead the reader.
- **Priority**: Must
- **Acceptance Criteria**: Given commits by "spashx <x@users.noreply.github.com>" and by
  "x@users.noreply.github.com <X@users.noreply.github.com>", When the history is built, Then they are one identity named
  "spashx" with both names kept; Given a merge whose committer is "GitHub", Then "GitHub" is no identity; Given a
  `.mailmap` mapping "nina <n@old>" to "Nina Dev <n@new>", Then their commits are one identity; Given "Claude Opus 5.5
  <noreply@anthropic.com>" and "Claude Sonnet 5.5 <noreply@anthropic.com>", Then they are two identities.
- **Dependencies**: RQ-HST-001

### RQ-HST-005: Humans and agents
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The trace generator SHALL count each co-author named by a `Co-Authored-By` trailer of a commit as a
  contributor of that commit, beside its author, and SHALL class each identity as an **agent** when its name or e-mail
  matches one of the patterns of a data file of the skill (AI assistants and bots, such as `noreply@anthropic.com`,
  `Claude`, `Copilot`, `[bot]`), and as a **human** otherwise; a commit SHALL be marked as made by a human, by an agent,
  or by both together.
- **Rationale**: telling humans from agents, and seeing what they made together, is the purpose of this view on an
  AGNOS project.
- **Priority**: Must
- **Acceptance Criteria**: Given a commit by "spashx" with the trailer "Co-Authored-By: Claude Opus 5.5
  <noreply@anthropic.com>", When the history is built, Then the commit has two contributors, spashx (human) and Claude
  Opus 5.5 (agent), and is marked "together"; Given a commit by "dependabot[bot]", Then it is marked "agent"; Given the
  patterns file changed, Then the classification follows with no change of code.
- **Dependencies**: RQ-HST-004

### RQ-HST-006: History data in the data file
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE the history is built, the trace generator SHALL write in the data file a `history` block holding
  the limits applied (since, depth, number of commits read, first and last dates, whether the history was cut by a
  shallow clone), the identities (display name, names, e-mails, way of merging, kind, counts), the commits (short hash,
  author date, author, co-authors, subject) and the interventions of each element, file and function (commit and number
  of lines changed), sorted so that two runs on the same repository write the same bytes, and SHALL end its summary line
  with `history: <commits> commits, <humans> humans, <agents> agents`.
- **Rationale**: the page computes no history itself, and another tool or an agent can read the same figures.
- **Priority**: Must
- **Acceptance Criteria**: Given a run with `--history`, When the data file is read, Then it holds the `history` block
  with the keys listed and the summary line ends with the history counts; When the generator runs twice on the same
  repository with the same `--generated-at`, Then the two data files are equal byte for byte.
- **Dependencies**: RQ-HST-001 to RQ-HST-005, RQ-TRC-010, RQ-TRC-023

### RQ-HST-007: The History tab and its timeline
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE the data file holds a history, the page SHALL show a "History" tab in its main area, which SHALL
  show a timeline of interventions with a switch between the requirements angle (one row per process element, in index
  order, grouped by type) and the code angle (one row per file, its functions below it with a call graph, or grouped by
  the requirement the code cites), a time axis, and one mark per intervention whose shape tells human, agent or both,
  whose colour tells the identity, and whose size tells the number of changed lines; the timeline SHALL zoom with the
  wheel and the keyboard, pan by dragging and with the arrow keys, show an overview strip whose window can be dragged,
  and fit the whole history in one action; hovering a mark SHALL show its commit (hash, date, author, co-authors,
  subject, lines changed), and clicking it SHALL pin that card; clicking a row's label SHALL select the element in the
  detail panel. WHILE the data file holds no history, the page SHALL show no History tab and no History section.
- **Rationale**: a timeline shows at a glance who worked on what and when, and lets the reader go from the overview of
  the project to one commit.
- **Priority**: Must
- **Acceptance Criteria**: Given a page with history, When the History tab opens, Then the requirements angle shows one
  row per element with its marks; When the switch is set to code, Then the rows are files with their functions; When
  the wheel turns over the timeline, Then the time scale zooms around the pointer; When a mark is hovered, Then its
  commit card shows; Given a page without history, Then there is no History tab.
- **Dependencies**: RQ-HST-006, RQ-TRC-011, RQ-TRC-012, RQ-TRC-018, ADR-TRC-002, RQ-TRC-049

### RQ-HST-008: Activity summary above the timeline
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE the History tab is open, the page SHALL show above the timeline the key figures of what is shown
  (commits, humans, agents, share of commits made by an agent or together, period) and an activity band of the commits
  per period, stacked by human, agent and together, whose period (day, week or month) follows the zoom of the timeline,
  all updated when a filter or the scope changes.
- **Rationale**: the reader sees the balance between humans and agents and how it moves over time before reading rows.
- **Priority**: Must
- **Acceptance Criteria**: Given a history of 100 commits of which 60 have an agent co-author, When the tab opens, Then
  the figures read 100 commits and 60 % with an agent; When the filter keeps one person, Then the figures and the band
  count only that person's commits; When the timeline zooms from a year to two weeks, Then the band's period changes
  from month to day.
- **Dependencies**: RQ-HST-007

### RQ-HST-009: Filters by identity and by kind
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the reader selects one or more identities, or the kind "humans" or "agents", in the History tab's
  filter bar, the page SHALL keep in the timeline, the figures and the band only the interventions of a commit having
  one of them as contributor, SHALL hide the rows left with no intervention (an option shows them again), SHALL show the
  number of rows and commits kept, and SHALL return to the whole history in one action.
- **Rationale**: the reader analyses one person, one agent, or the share of agents, without the others' noise.
- **Priority**: Must
- **Acceptance Criteria**: Given a history with Alice, Bob and Claude, When Alice and Claude are selected, Then only the
  commits with Alice or Claude as contributor are marked and the rows without them are hidden; When the kind "agents" is
  chosen, Then only the commits with an agent contributor stay; When the filter is reset, Then every commit shows again.
- **Dependencies**: RQ-HST-007, RQ-HST-005

### RQ-HST-010: History section of the sidebar
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHILE the data file holds a history, the sidebar SHALL show a "History" section below the Quality
  section listing the identities, by number of commits from the highest, each with its kind marked by an icon and its
  number of commits; WHEN the pointer rests on an identity, the page SHALL show a tooltip with its names and e-mails and
  how they were merged into it; WHEN an identity is clicked, the page SHALL open the History tab filtered on that
  identity alone.
- **Rationale**: the people of the project are one click away from what they did, and the merging of identities is
  explained where it shows.
- **Priority**: Must
- **Acceptance Criteria**: Given a history with spashx (two names merged by e-mail) and Claude Opus 5.5, When the page
  opens, Then the sidebar's History section lists both with their counts and kinds; When the pointer rests on spashx,
  Then the tooltip lists both names and says "merged by e-mail"; When spashx is clicked, Then the History tab opens
  filtered on spashx.
- **Dependencies**: RQ-HST-009, RQ-TRC-015, RQ-TRC-049

### RQ-HST-011: History of the selected element
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHILE the data file holds a history, the detail panel SHALL show a "History" button for a process
  element, a file or a function; WHEN it is pressed, the page SHALL open the History tab scoped to that element: for a
  process element, its row and the rows of the elements it contains in the requirements angle, and the code that cites
  them in the code angle; for a file or a function, its row and those of its functions in the code angle; the scope
  SHALL show as a removable chip, and removing it SHALL return to the whole history with the filters kept.
- **Rationale**: the reader looking at one requirement asks who wrote it and who wrote its code, without searching for
  it in the timeline.
- **Priority**: Must
- **Acceptance Criteria**: Given FTR-A containing RQ-A1 and RQ-A2, When FTR-A is selected and its History button is
  pressed, Then the History tab shows the rows FTR-A, RQ-A1 and RQ-A2 and a chip "FTR-A"; When the angle is switched to
  code, Then the rows are the files and functions citing them; When the chip is removed, Then every row shows again.
- **Dependencies**: RQ-HST-007, RQ-TRC-013

### RQ-HST-012: A repository the generator cannot read
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: IF `--history` is given and git is not installed, or the process folder is not inside a git working
  tree, or the repository has no commit, THEN the trace generator SHALL write a warning naming the cause, build the page
  without history, and exit with code 0; IF the repository is a shallow clone, THEN it SHALL build the history it has and
  mark it as cut, and the page SHALL say so beside the limits.
- **Rationale**: the matrix stays usable where the history is not, and a cut history is never shown as the whole one.
- **Priority**: Must
- **Acceptance Criteria**: Given a process folder outside any git repository, When the generator runs with `--history`,
  Then it prints a warning, the page has no History tab and the exit code is 0; Given a shallow clone of depth 5, Then
  the History tab reads that the history is cut.
- **Dependencies**: RQ-HST-001, RQ-HST-006

---

## Non-Functional Requirements

### RQ-HST-013: The history stays fast and light
- **Category**: Non-Functional
- **NFR Type**: Performance
- **EARS Type**: Ubiquitous
- **Statement**: On a generated repository of 2,000 commits by 12 identities, 300 process elements and 500 source files,
  building the history SHALL take less than 20 seconds and add less than 3 MB to the data file, the History tab SHALL be
  drawn in less than 300 ms, and each step of zoom, pan or filter SHALL be redrawn in less than 50 ms.
- **Metric**: generation time added by `--history`; size added to the data file; drawing time of the tab; P95 of the
  redraw time over 50 zoom, pan and filter steps.
- **Measurement Method**: the skill's performance test (`AGNOS_TRACE_PERF=1`) on a generated repository, with and
  without `--history`; times measured in the headless browser.
- **Priority**: Should
- **Acceptance Criteria**: Given the generated repository, When the generator runs with and without `--history` and the
  History tab is opened and driven, Then the added time, the added size and the drawing times are below the metrics.
- **Dependencies**: RQ-HST-006, RQ-HST-007, RQ-TRC-037, RQ-TRC-038

### RQ-HST-014: A readable and professional view
- **Category**: Non-Functional
- **NFR Type**: Usability
- **EARS Type**: Ubiquitous
- **Statement**: The History view SHALL take every colour, size, spacing, stroke and duration from the design tokens of
  the page, in both themes; SHALL give each identity a colour of its own, the same wherever it shows (mark, legend,
  filter, sidebar), distinct from the others' however many there are; SHALL tell a human from an agent by an icon of its
  own (a person, an agent) beside every identity's name and by the shape of its marks (amended by the owner on
  2026-10-24); SHALL never tell an identity or its kind by colour alone (the name is written in the tooltip, the legend
  and the filter); SHALL meet the contrast of WCAG 2.1 AA; and SHALL give every control, row and mark a keyboard path
  and an accessible name.
- **Metric**: contrast of at least 4.5:1 for text and 3:1 for marks in both themes; no raw visual literal in the page's
  code for the view.
- **Measurement Method**: contrast computed from the resolved tokens; the literal test of RQ-TRC-067; a test that every
  control and mark of the view is focusable and named.
- **Priority**: Must
- **Acceptance Criteria**: Given the tokens of both themes, When the contrast of the marks and texts of the view is
  computed, Then it meets the metric; Given 20 identities, Then they have 20 different colours, each the same in the
  marks, the legend, the filter and the sidebar; Given a human and an agent, Then each name shows with its kind's icon
  and their marks have different shapes; Given the view, When it is driven by the keyboard only, Then the switch, the
  filters, the zoom, the pan and every mark can be reached.
- **Dependencies**: RQ-TRC-018, ADR-TRC-002, RQ-TRC-065, RQ-TRC-067

### RQ-HST-015: No change without the history
- **Category**: Non-Functional
- **NFR Type**: Maintainability
- **EARS Type**: State-driven
- **Statement**: WHILE `--history` is not given, the trace generator SHALL not run git, SHALL not load the history code,
  and SHALL write a data file equal byte for byte to the one written before this feature; the history SHALL need nothing
  beyond the Python standard library and the git command.
- **Metric**: sentinel hash of the data file without `--history`; imports of the history code.
- **Measurement Method**: the sentinel test of RQ-TRC-026 kept unchanged; a test that the history code imports only the
  standard library and is loaded only with `--history`.
- **Priority**: Must
- **Acceptance Criteria**: Given the fixture, When the generator runs without `--history`, Then the data file's hash is
  the sentinel of RQ-TRC-026; Given the history code, Then it imports only the standard library.
- **Dependencies**: RQ-TRC-021, RQ-TRC-026
