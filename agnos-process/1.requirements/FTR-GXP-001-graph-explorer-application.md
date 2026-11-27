# FTR-GXP-001: Graph explorer application

## Overview
The graph explorer of FTR-TRC-014 shows a project's state in one page with facets, a query, a 2D graph and two tables. This
feature makes it an application whose purpose is to view and explore AGNOS graphs: a menu bar that reaches every setting by
its purpose, a help dialog with licences and an About section copied from the performance center, a period of time that
filters every view and plays in a loop, a colour per relation kind chosen by the reader, and a 3D view in which the reader
chooses what each dimension shows, under a perspective, orthographic or isometric camera.

The 3D view also serves communication: it shows at a glance the size and growth of a software project.

Source: the owner's session of 2026-11-24 (session TRC, then GXP): a 3D mockup on this repository's real data, judged "very
visual"; flat tabs Graph 2D, Graph 3D, Nodes, Relations; delivery in two lots, A (application, time, colours, on the 2D view)
then B (3D); a hand-written orbit controller; the 3D view usable without history, the history being one dimension among
others; the node colours kept; the help and About copied from the performance center.

Lot A: RQ-GXP-001 to RQ-GXP-009 (PLAN-GXP-001). Lot B: RQ-GXP-010 to RQ-GXP-019, planned in a later session. RQ-GXP-020 to RQ-GXP-022 (PLAN-GXP-003). Lot B2: RQ-GXP-016, RQ-GXP-017 (PLAN-GXP-004); RQ-GXP-018 cancelled by the owner on 2026-11-27.

Out of scope: nodes deleted before the graph's commit (the graph is the state at one commit, so the time filter shows when
today's nodes first appeared, not what was removed); a choice of node type colours (owner: "en gardant la couleur des
nœuds"); a dark theme; editing the graph; a server.

## Stakeholders
- **Owner**: the repository owner (maintainer of AGNOS).
- **Consumers**: the readers of a project's state; the people a project's complexity is shown to; the demo and the website,
  which may show the explorer.

---

## Functional Requirements

### RQ-GXP-001: Explorer menu bar
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The explorer SHALL show a menu bar of the menus File, View, Filter, Time, Appearance, Dimensions and Help, each opened by a click or the keyboard, and SHALL disable each item whose action does not apply to the loaded graph or the current view.
- **Rationale**: every setting is reached by its purpose, as in a desktop application (owner, 2026-11-24).
- **Priority**: Must
- **Acceptance Criteria**: Given the explorer, When File is clicked, Then its items "Open graph file…", "Import saved queries…" and "Export saved queries…" are listed; When a menu is open And the right arrow key is pressed, Then the next menu opens; When Escape is pressed, Then the menu closes And the focus returns to its title; Given a menu whose actions are not delivered yet, Then it is absent from the bar.
- **Dependencies**: RQ-TRC-164, RQ-TRC-155, RQ-TRC-018

### RQ-GXP-002: Explorer help dialog
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the reader chooses Help in the menu bar or the help button, the explorer SHALL open a resizable dialog listing its topics, one per view and per menu with the topics Licenses and About, showing first the topic of the current view, as the performance center's help does.
- **Rationale**: the reader learns each view where it is used; the pattern is the one the owner knows (RQ-TRC-101).
- **Priority**: Must
- **Acceptance Criteria**: Given the Nodes tab shown, When the help opens, Then the topic Nodes is shown And the list names every topic; When a topic is clicked, Then its text replaces the former; When Escape is pressed, Then the dialog closes.
- **Dependencies**: RQ-TRC-101, RQ-GXP-001

### RQ-GXP-003: Explorer licence list
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The help's Licenses topic SHALL show a badge of AGNOS's licence and one badge per library the explorer loads, with its name, version and licence, each tabled licence linked to its SPDX page, as the performance center does.
- **Rationale**: a page that loads libraries names their licences (RQ-TRC-111, RQ-TRC-112).
- **Priority**: Must
- **Acceptance Criteria**: Given the explorer, When the Licenses topic is shown, Then a badge reads AGNOS AGPL-3.0 And a badge reads Cytoscape.js 3.30.2 MIT linked to the MIT page of SPDX.
- **Dependencies**: RQ-TRC-111, RQ-TRC-112, RQ-GXP-002

### RQ-GXP-004: Explorer about section
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The help's About topic SHALL show the AGNOS mark with the name, the version of the version file and the tagline, a sentence naming `agnos-graph` as the page's author, and the owner's links, as the performance center's About does.
- **Rationale**: both pages of AGNOS present the same identity (RQ-TRC-114, RQ-TRC-116).
- **Priority**: Must
- **Acceptance Criteria**: Given a version file holding one SemVer line, When the About topic is shown, Then it reads "AGNOS v.<major>.<minor>" and "Agentic efficiency by traceability" And names agnos-graph; Given no version file, Then it reads "AGNOS" alone.
- **Dependencies**: RQ-TRC-114, RQ-TRC-116, RQ-GXP-002

### RQ-GXP-005: Relation colour choice
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the reader chooses a colour for a relation kind in the Appearance menu or from the legend, the explorer SHALL draw that kind's relations and legend line in that colour in every graph view, keep the choice in the browser, and restore the design-system colour of every kind on "Reset colours".
- **Rationale**: the reader brings forward the relations under study (owner, 2026-11-24); the design system stays the default.
- **Priority**: Must
- **Acceptance Criteria**: Given the graph view, When `code` is given a green colour, Then every `code` relation and the legend's `code` line are green; When the page is reloaded, Then they stay green; When "Reset colours" is chosen, Then they take the `relation-code` token's colour again.
- **Dependencies**: RQ-TRC-165, RQ-TRC-018, RQ-GXP-001

### RQ-GXP-006: Time period filter
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE the loaded graph holds a history, the explorer SHALL show a time bar whose start and end handles select a period, and SHALL show in every view only the nodes whose date lies in that period and the relations whose two ends are shown, a node's date being the date of its first commit in the history.
- **Rationale**: the reader sees what was created in a period, and the project's growth (owner, 2026-11-24).
- **Priority**: Must
- **Acceptance Criteria**: Given this repository's graph with history, When the period is set from 2026-11-01 to the last commit, Then the node table lists only nodes first changed in that period And the graph view shows only them; Given a node with no commit in the history read, Then it is dated the history's first commit.
- **Dependencies**: RQ-TRC-138, RQ-TRC-146, RQ-TRC-151

### RQ-GXP-007: Time playback loop
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the reader presses Play, the explorer SHALL move a cursor from the period's start to its end at the chosen speed, showing the nodes dated up to the cursor, restart from the start WHILE Loop is checked, and SHALL stop on Pause, keeping the cursor, or on Stop, showing the whole period again.
- **Rationale**: the graph grows before the reader's eyes, in a loop for a presentation (owner, 2026-11-24).
- **Priority**: Must
- **Acceptance Criteria**: Given a period, When Play is pressed, Then the shown node count grows until the end; Given Loop checked, When the cursor reaches the end, Then it starts again from the start; When Pause is pressed, Then the cursor stays; When Stop is pressed, Then the whole period is shown.
- **Dependencies**: RQ-GXP-006

### RQ-GXP-008: Sliding time window
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE the window mode is chosen, the explorer SHALL show only the nodes dated between the cursor minus the chosen window width and the cursor, instead of the nodes dated from the period's start.
- **Rationale**: the reader sees where the activity moves over time.
- **Priority**: Should
- **Acceptance Criteria**: Given the window mode with a width of 7 days, When the cursor is at 2026-11-20, Then only the nodes dated from 2026-11-13 to 2026-11-20 are shown.
- **Dependencies**: RQ-GXP-007

### RQ-GXP-009: Explorer without history
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: IF the loaded graph holds no history, THEN the explorer SHALL hide the time bar, disable the Time menu with a tooltip naming `--history`, and disable every dimension drawn from the history, keeping every other view and action usable.
- **Rationale**: the history is one dimension among others, never a condition of use (owner, 2026-11-24).
- **Priority**: Must
- **Acceptance Criteria**: Given a graph built without `--history`, When it is loaded, Then no time bar is shown And the Time menu is disabled with a tooltip naming `--history` And the graph view and the tables show every node.
- **Dependencies**: RQ-GXP-006

### RQ-GXP-010: Flat view tabs
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The explorer SHALL show the tabs Graph 2D, Graph 3D, Nodes and Relations side by side, Graph 2D being the former graph view unchanged.
- **Rationale**: each view is one click away (owner, 2026-11-24).
- **Priority**: Must
- **Acceptance Criteria**: Given the explorer, Then four tabs read Graph 2D, Graph 3D, Nodes and Relations; When Graph 2D is clicked, Then the former graph view is shown with its layouts.
- **Dependencies**: RQ-TRC-150, RQ-GXP-011

### RQ-GXP-011: 3D graph view
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the Graph 3D tab is shown, the explorer SHALL draw the shown nodes as points in their type's colour and the shown relations as lines in their kind's colour, in three dimensions that the reader rotates, zooms and pans with the mouse, under the same facets, query, hidden nodes, isolation and time period as the other views.
- **Rationale**: a 3D view shows the size and growth of a project at a glance (owner, 2026-11-24).
- **Priority**: Must
- **Acceptance Criteria**: Given this repository's graph, When the Graph 3D tab is shown, Then it shows as many points as the node table has rows; When type FN is unchecked, Then no function point is shown; When the view is dragged, Then it rotates around its centre.
- **Dependencies**: RQ-TRC-147, RQ-TRC-151, RQ-TRC-154, RQ-GXP-005, RQ-GXP-006, RQ-GXP-010

### RQ-GXP-012: 3D node interaction
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the reader clicks, hovers or right-clicks a point of the 3D view, the explorer SHALL select its node in the detail panel, show its tooltip after the tooltip delay, or open the node actions of the graph context menu, as the 2D view does.
- **Rationale**: the 3D view is explored as the 2D one is (RQ-TRC-154, RQ-TRC-163, RQ-TRC-167).
- **Priority**: Must
- **Acceptance Criteria**: Given the 3D view, When a point is clicked, Then the detail panel shows its node; When the pointer rests on a point, Then its tooltip is shown after the delay; When a point is right-clicked And "Neighbours, 1 hop" is chosen, Then only it and its neighbours are shown.
- **Dependencies**: RQ-TRC-154, RQ-TRC-163, RQ-TRC-167, RQ-GXP-011

### RQ-GXP-013: 3D dimension mapping
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the reader chooses in the Dimensions menu what the height, the angle, the radius, the colour and the size show, among the first or last commit date, the commit count, the changed lines, the relation count, the trigram, the type, the status, the main author, the author kind, the task tier and the layer, the explorer SHALL place and draw the 3D view's points by those choices, the default being height by first commit date, angle by trigram, radius by layer, colour by type and size by type.
- **Rationale**: the reader chooses what each dimension shows (owner, 2026-11-24).
- **Priority**: Must
- **Acceptance Criteria**: Given the 3D view, When the height is set to the changed lines, Then the most changed nodes are the highest; Given a graph without history, Then the history's dimensions are disabled And the height defaults to the relation count.
- **Dependencies**: RQ-GXP-011, RQ-GXP-009

### RQ-GXP-014: 3D camera projections
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the reader chooses a projection in the View menu, the explorer SHALL draw the 3D view in perspective, orthographic or isometric projection, or from the top, the front or the side, keeping the points readable at every zoom.
- **Rationale**: an orthographic or isometric view compares heights without perspective (owner, 2026-11-24).
- **Priority**: Must
- **Acceptance Criteria**: Given the 3D view, When "Isometric" is chosen, Then a given height difference is drawn with the same screen length wherever it lies; When "Front" is chosen, Then two points of the same height are drawn at the same height on the screen; When "Top" is chosen, Then the angle sectors are seen from above. (Amended by TASK-GXP-016, owner, 2026-11-25: an isometric view looks down, so equal heights at different depths differ on screen.)
- **Dependencies**: RQ-GXP-011

### RQ-GXP-015: 3D reference planes
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The 3D view SHALL show, each on the reader's choice, a ring per month at its date's height labelled with the month, a grid plane at the cursor's date, and the labels of the angle's categories.
- **Rationale**: the reader reads dates and sectors without a tooltip; the plane sweeps the graph during playback.
- **Priority**: Should
- **Acceptance Criteria**: Given the 3D view with height by first commit date, Then a ring labelled 2026-08 lies at that month's height; When Play is pressed, Then the grid plane rises with the cursor.
- **Dependencies**: RQ-GXP-013, RQ-GXP-007

### RQ-GXP-016: Explorer view files
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the reader exports the view, the explorer SHALL write to a JSON file the tab, the query, the facets, the hidden and isolated nodes, the period, the dimensions, the projection and the relation colours, and WHEN the reader imports a view file, SHALL restore them all, keeping no view in the browser. (Amended by TASK-GXP-030, owner, 2026-11-27: a view is a file only, the saved views of the browser removed.)
- **Rationale**: a reader returns to a prepared view and shares it.
- **Priority**: Should
- **Acceptance Criteria**: Given a 3D view in isometric projection with a period, When it is exported, the state reset and the file imported, Then the same tab, projection, period and shown nodes are restored; Given the explorer, Then the browser's storage holds no view.
- **Dependencies**: RQ-TRC-153, RQ-GXP-005, RQ-GXP-013, RQ-GXP-014

### RQ-GXP-017: Graph image export
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the reader chooses "Export image" in the File menu, the explorer SHALL save the current graph view, 2D or 3D, as a PNG file at the view's size.
- **Rationale**: the image goes into a presentation or a document.
- **Priority**: Should
- **Acceptance Criteria**: Given the 3D view, When "Export image" is chosen, Then a PNG file of the view's width and height is saved.
- **Dependencies**: RQ-GXP-011

### RQ-GXP-018: Presentation mode
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE the presentation mode is on, the explorer SHALL show the current graph view alone over the whole window, with the 3D view rotating slowly, until Escape is pressed.
- **Rationale**: the graph shows the complexity of a project to an audience (owner, 2026-11-24).
- **Priority**: Won't (cancelled by the owner, 2026-11-27, TASK-GXP-026: kept defined so that its citations stay resolved)
- **Acceptance Criteria**: Given the 3D view, When the presentation mode is chosen, Then the menus and panels are hidden And the view rotates; When Escape is pressed, Then the layout is restored.
- **Dependencies**: RQ-GXP-011

### RQ-GXP-020: 3D axis indicator
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE the axis indicator is checked in the View menu, the 3D view SHALL show in its bottom left corner three axes turning with the camera, each labelled with the dimension it shows, the indicator being checked by default.
- **Rationale**: the reader knows what each direction shows without opening the Dimensions menu (owner, 2026-11-26).
- **Priority**: Should
- **Acceptance Criteria**: Given the 3D view, Then the indicator's height axis reads the first commit date; When the height is set to the changed lines, Then it reads the changed lines; When the axis indicator is unchecked, Then the indicator is hidden.
- **Dependencies**: RQ-GXP-013, RQ-GXP-014, RQ-GXP-021

### RQ-GXP-021: 3D cartesian layout
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the reader chooses the cartesian layout in the View menu, the 3D view SHALL place each point at the x, y and z given by the angle, height and radius dimensions, without month rings or angle labels, its height, angle and radius choices named Y, X and Z in the X, Y, Z order, and SHALL show, while the axes are checked in the View menu, three graduated axes from the origin labelled with their dimensions; WHEN the cylindrical layout is chosen, the 3D view SHALL return to RQ-GXP-013's placement, the axes choice disabled.
- **Rationale**: a traditional trihedron reads three quantities directly, where the cylinder shows sectors (owner, 2026-11-26).
- **Priority**: Should
- **Acceptance Criteria**: Given the 3D view, When the cartesian layout is chosen, Then no month ring is drawn And the node of greatest angle value has the greatest x; When the axes are unchecked, Then the trihedron is hidden; When the cylindrical layout is chosen, Then the axes choice is disabled. (Amended by TASK-GXP-025, owner, 2026-11-26: Given the cartesian layout, Then the toolbar and the Dimensions menu read X, Y, Z, Colour, Size; When the cylindrical layout is chosen, Then they read Height, Angle, Radius again.)
- **Dependencies**: RQ-GXP-013, RQ-GXP-015

### RQ-GXP-022: 3D date scale on the period
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE a period is selected, the 3D view SHALL scale each date dimension, its month rings and its graduations from the period's start to its end, a date outside it drawn at the nearest end; WHILE no period is selected, from the history's first to last commit.
- **Rationale**: the dates outside the period take room for nothing (owner, 2026-11-26).
- **Priority**: Should
- **Acceptance Criteria**: Given height by first commit date And the period from 2026-10-01 to the last commit, Then the only ring is 2026-11 at that month's height in the period And every shown point lies within the cylinder; When the whole history is selected again, Then the former positions return.
- **Dependencies**: RQ-GXP-006, RQ-GXP-013, RQ-GXP-015, RQ-GXP-021

---

## Non-Functional Requirements

### RQ-GXP-019: 3D view draw time
- **Category**: Non-Functional
- **NFR Type**: Performance
- **EARS Type**: Event-driven
- **Statement**: WHEN the Graph 3D tab is first shown, the explorer SHALL draw this repository's graph, built with `--call-graph` and `--history`, in less than 3 seconds, without delaying the first view of RQ-TRC-158.
- **Metric**: time from the click on the tab to the first drawn 3D frame < 3 s; RQ-TRC-158's time unchanged within 10 %.
- **Measurement Method**: a headless browser test timing the first 3D frame on this repository's graph, and RQ-TRC-158's test before and after.
- **Priority**: Should
- **Acceptance Criteria**: Given this repository's graph, When the Graph 3D tab is clicked in a headless browser, Then its first frame is drawn in less than 3 s And the page's first view is drawn in less than 5 s.
- **Dependencies**: RQ-TRC-158, RQ-GXP-011
