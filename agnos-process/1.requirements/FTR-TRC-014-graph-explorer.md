# FTR-TRC-014: Graph explorer

## Overview
A reader of `agnos-graph.json` sees today a sorted JSON document of several thousand rows. This feature gives the graph skill
an explorer: one web page, written beside the graph file when asked, that loads the graph and shows every node, relation and
property, filters them by facets and by a text query, saves queries as buttons, hides or isolates a selection, and lets the
reader move the nodes of the graph view. The explorer shows the state and judges nothing: no coverage, finding nor score.

The graph file moves with it into a folder of its own, `4.knowledge/graph/`, and the performance center's outputs take
lowercase names, as the explorer's do.

Source: the owner's session of 2026-11-22: an application to understand the graph in depth before the performance center
reads its `links` block; the explorer is a goal distinct from the performance center's, written only on request; the page
names are lowercase; the interface is in English; every block of the graph file is shown; option A, no code shared with the
performance center at first, its values copied.

Out of scope: the performance center reading `links`; a code base shared by both pages; a dark theme of the explorer; editing
the graph; a server.

## Stakeholders
- **Owner**: the repository owner (maintainer of AGNOS).
- **Consumers**: the owner and any reader of a project's state; `agnos-perf-center`, whose input path and output names change;
  the demo, the release and the website, which run or copy both.

---

## Functional Requirements

### RQ-TRC-142: Graph file in the graph folder
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The graph skill SHALL write the graph file to `agnos-process/4.knowledge/graph/agnos-graph.json` by default, and `agnos-perf-center` SHALL read it there by default.
- **Rationale**: the graph and its explorer are one set of outputs, kept apart from the other knowledge files. Amends RQ-TRC-129 and RQ-TRC-131.
- **Priority**: Must
- **Acceptance Criteria**: Given a project, When `agnos-graph` runs without `--out`, Then `agnos-process/4.knowledge/graph/agnos-graph.json` exists; Given that file, When `agnos-perf-center` runs without `--graph`, Then it reads it And does not rebuild it.
- **Dependencies**: RQ-TRC-129, RQ-TRC-131, RQ-PLG-049

### RQ-TRC-143: Lowercase performance center outputs
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The performance center SHALL write its page to `<process>/perf-center.html` by default, with `perf-center.json` and `perf-center.data.js` beside it.
- **Rationale**: both pages of AGNOS carry lowercase names, as files of a web site do (owner, 2026-11-22). Amends RQ-TRC-105.
- **Priority**: Must
- **Acceptance Criteria**: Given a process folder and a graph, When `agnos-perf-center` runs without `--out`, Then `process/perf-center.html`, `process/perf-center.json` and `process/perf-center.data.js` exist; Given the tracked files other than plans, `CHANGELOG.md` and the index, Then none names `PERF-CENTER.html`, `PERF-CENTER.json` nor `PERF-CENTER.data.js` but as a former name.
- **Dependencies**: RQ-TRC-105, RQ-TRC-106

### RQ-TRC-144: Explorer written on request
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN `--explorer` is given, the graph skill SHALL write `graph-explorer.html` and `agnos-graph.data.js` beside the graph file; without it, the graph skill SHALL write neither, and `agnos-perf-center` SHALL NOT give `--explorer` when it builds the graph.
- **Rationale**: exploring the state and judging it are two goals; a reader asks for the explorer, the performance center never needs it (owner, 2026-11-22).
- **Priority**: Must
- **Acceptance Criteria**: Given a project, When `agnos-graph --explorer` runs, Then `graph/graph-explorer.html` and `graph/agnos-graph.data.js` exist beside `graph/agnos-graph.json`; Given a run without `--explorer`, Then neither is written; Given no graph, When `agnos-perf-center --sources S` builds it, Then no explorer file is written.
- **Dependencies**: RQ-TRC-142, RQ-TRC-132

### RQ-TRC-145: Explorer graph loading
- **Category**: Functional
- **EARS Type**: Complex
- **Statement**: WHEN the explorer is opened from the disk, it SHALL show the graph of `agnos-graph.data.js` beside it; WHEN the reader drops or chooses a graph file, it SHALL show that graph instead; IF that file is not JSON or holds no `elements` list, THEN it SHALL name the file and the cause and keep the graph shown.
- **Rationale**: a page opened from the disk fetches no file, so the graph comes as a script; a reader also compares graphs of other commits or projects.
- **Priority**: Must
- **Acceptance Criteria**: Given `graph-explorer.html` and its data script, When the page is opened, Then the header shows the graph's `generatedAt` in the reader's date and time with its UTC value in a tooltip, as the performance center does, and its counts, and no commit, since the graph is read from the working tree, not from a commit <!-- amended 2026-11-25, TASK-GXP-008 (owner) -->; Given a valid graph file dropped on the page, Then its elements are shown; Given a file holding `{}`, Then a message names the file and "no elements list" And the former graph stays shown.
- **Dependencies**: RQ-TRC-144, RQ-TRC-010

### RQ-TRC-146: Whole graph content shown
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The explorer SHALL show as nodes the elements, the sections, the scanned files and the call graph's functions, as relations the `edges` with the link field of each proof joined from `links` and the call graph's calls, and as properties every key of `meta`, of each node and relation, of `tasks`, of `history` and of `delivery`.
- **Rationale**: the reader explores the whole state before deciding what the performance center does with it (owner, 2026-11-22: "on inclut tout").
- **Priority**: Must
- **Acceptance Criteria**: Given a graph built with `--call-graph` and `--history`, When it is loaded, Then the nodes count the elements, sections, files and functions of the file And the relations count its edges and calls; Given a task, Then its detail shows `tier`, `requirements` and its history; Given a `refs` relation of a task, Then each proof shows its line, text and field; Given a relation of a feature, Then it shows no field.
- **Dependencies**: RQ-TRC-129, RQ-TRC-134, RQ-TRC-138, RQ-TRC-145

### RQ-TRC-147: Type colours shared by views
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The explorer SHALL give each node type one colour, taken from design-system tokens, to its nodes in the graph view and to its type labels in the tables, the facets and the detail panel.
- **Rationale**: a reader finds a type by its colour in every view at once.
- **Priority**: Must
- **Acceptance Criteria**: Given a requirement shown in the graph and in the node table, Then its node and its type label use the token of type RQ; Given the token of a type changed, When the page is rebuilt, Then every view of that type changes.
- **Dependencies**: RQ-TRC-018, RQ-TRC-157, RQ-TRC-146

### RQ-TRC-148: Resizable explorer panels
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The explorer SHALL place the facets, the central view and the detail panel side by side, separated by two splitters that the reader drags with the mouse or moves with the arrow keys, each step and width from design-system tokens.
- **Rationale**: the reader gives room to the view in use, as in the performance center.
- **Priority**: Must
- **Acceptance Criteria**: Given the explorer, When the left splitter is dragged by 100 px, Then the facets panel widens by 100 px And the central view narrows by as much; Given the right splitter focused, When the left arrow key is pressed, Then the detail panel widens by one step; Given a width below the central view's minimum, Then the splitter stops.
- **Dependencies**: RQ-TRC-025, RQ-TRC-018

### RQ-TRC-149: Node and relation tables
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The explorer SHALL show a node table and a relation table, each scrolling vertically inside the central view under a fixed header row and sorted by the column the reader clicks.
- **Rationale**: several thousand rows stay readable in a table where a drawing no longer is.
- **Priority**: Must
- **Acceptance Criteria**: Given this repository's graph, When the relation table is shown, Then it scrolls inside the central view And its header stays visible; When the `field` header is clicked, Then the rows are sorted by field And a second click reverses the order.
- **Dependencies**: RQ-TRC-146, RQ-TRC-148

### RQ-TRC-150: Graph view navigation
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The explorer's graph view SHALL let the reader drag a node, zoom with the wheel and with buttons, fit the graph to the view and pan the view, with the zoom bounds and the wheel sensitivity of the performance center's tokens, and SHALL keep a moved node's position when the filters change.
- **Rationale**: the reader arranges the nodes under study; the gestures are those of the performance center's graph.
- **Priority**: Must
- **Acceptance Criteria**: Given the graph view, When a node is dragged, Then it stays where it is dropped; When a facet hides then shows another type, Then the moved node keeps its position; When the fit button is clicked, Then every shown node is in the view; Given the wheel, Then the zoom stays within the tokens' bounds.
- **Dependencies**: RQ-TRC-056, RQ-TRC-146

### RQ-TRC-151: Facet filters with counts
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The explorer SHALL show facets of the node type, the trigram, the status, the relation kind and the link field, each value with its count in the loaded graph, and SHALL hide the nodes or relations of an unchecked value in every view.
- **Rationale**: the reader narrows the graph by the values it actually holds.
- **Priority**: Must
- **Acceptance Criteria**: Given the loaded graph, Then each facet value shows the number of its nodes or relations; When `text` is unchecked, Then no relation of field `text` is shown in the graph nor in the relation table; When a facet value is clicked with the query field focused, Then its term is written into the query.
- **Dependencies**: RQ-TRC-146, RQ-TRC-152

### RQ-TRC-152: Text query language
- **Category**: Functional
- **EARS Type**: Complex
- **Statement**: The explorer SHALL apply a query made of space-separated terms, all of which a node meets: `key:value`, `key:a,b` (one of), `key:!value` (not), `key:~text` (contains), `cites:TYPE[field]` and `cited-by:TYPE[field]` (a relation to or from a node of that type, by that field if given), each negated by a leading `!`, and a query starting with `edge` SHALL select relations by `kind`, `field`, `from` and `to`; IF a term does not parse, THEN the explorer SHALL name it and keep the former result.
- **Rationale**: a short grammar of facet-like terms is read at a glance; existence terms answer questions such as the requirements no task cites.
- **Priority**: Must
- **Acceptance Criteria**: Given this grammar, When `type:RQ tri:TRC status:!Done` is run, Then only TRC requirements not Done are shown; When `type:RQ !cited-by:TASK[Requirement refs]` is run, Then only requirements no task cites in `Requirement refs` are shown; When `edge kind:refs field:text from:DEC` is run, Then only those relations and their ends are shown; When `type:` is run, Then a message names `type:` And the former result stays.
- **Dependencies**: RQ-TRC-146

### RQ-TRC-153: Saved query buttons
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The explorer SHALL show saved queries as buttons under the query field, which run their query when clicked, and SHALL let the reader create, edit, delete and reorder them, keep them in the browser, export them to a JSON file and import them from one; the default buttons SHALL come from a file of the skill.
- **Rationale**: the questions a reader asks again become one click (owner, 2026-11-22).
- **Priority**: Must
- **Acceptance Criteria**: Given the explorer opened for the first time, Then the default buttons are shown; When a button is created with a label and a query, And the page is reloaded, Then it is still shown And runs its query; When it is edited, moved or deleted, Then the change is kept after a reload; When the buttons are exported then imported in another browser, Then the same buttons are shown in the same order.
- **Dependencies**: RQ-TRC-152

### RQ-TRC-154: Node selection actions
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the reader selects a node, the explorer SHALL show in the detail panel every property of the node and its incoming and outgoing relations with their kind, field and proofs, and SHALL let the reader hide it, isolate its neighbourhood, widen that neighbourhood by one hop and show the hidden nodes again from a list.
- **Rationale**: the reader studies one element and its links without the rest of the graph.
- **Priority**: Must
- **Acceptance Criteria**: Given a selected task, Then the detail panel lists its properties And each relation with its other end, kind, field and proof lines; When a relation is clicked, Then its other end is selected; When the node is hidden, Then it is listed as hidden And clicking it there shows it again; When its neighbourhood is isolated then widened, Then the nodes at one then two hops are shown.
- **Dependencies**: RQ-TRC-146

### RQ-TRC-155: English explorer interface
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The explorer SHALL write every label, message, keyword of its query language and default button in English.
- **Rationale**: AGNOS, its artifacts and its pages are in English (owner, 2026-11-22).
- **Priority**: Must
- **Acceptance Criteria**: Given the explorer's assets and default buttons, Then every text shown to the reader is English And the query keywords are `cites`, `cited-by` and `edge`.
- **Dependencies**: RQ-TRC-152, RQ-TRC-153

<!-- RQ-TRC-159 to RQ-TRC-165: the owner's review of the explorer, 2026-11-23 (PLAN-TRC-027) -->
### RQ-TRC-159: Resizable table columns
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The explorer SHALL let the reader resize every column of the node and relation tables by dragging the right edge of its header, within the minimum width of a design token.
- **Rationale**: a title or a proof cut by its column is read only once the column is widened (owner, 2026-11-23).
- **Priority**: Must
- **Acceptance Criteria**: Given the node table, When the right edge of the Title header is dragged to the right, Then the Title column is wider And sorting the table keeps that width; When it is dragged far to the left, Then the column keeps the token's minimum width.
- **Dependencies**: RQ-TRC-149, RQ-TRC-018

### RQ-TRC-160: Facet bulk selection
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the reader clicks a facet's "All" or "None" control, the explorer SHALL check or uncheck every value of that facet in one operation and apply it to every view.
- **Rationale**: keeping one type among ten takes one click and one tick instead of nine (owner, 2026-11-23).
- **Priority**: Must
- **Acceptance Criteria**: Given the Node types facet, When "None" is clicked, Then every type is unchecked And no node is shown; When "All" is clicked, Then every type is checked And every node is shown again.
- **Dependencies**: RQ-TRC-151

### RQ-TRC-161: Panel content clear of scrollbars
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE a list of the facets panel or the panel itself shows a vertical scrollbar, the explorer SHALL keep every right-aligned count fully visible beside it.
- **Rationale**: the trigram list's scrollbar hid its counts (owner, 2026-11-23).
- **Priority**: Must
- **Acceptance Criteria**: Given the Trigrams facet with more values than its height, When its scrollbar is shown, Then the right edge of every count lies left of the scrollbar.
- **Dependencies**: RQ-TRC-151

### RQ-TRC-162: Automatic graph layouts
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the reader chooses a layout, the explorer SHALL arrange the shown nodes of the graph view with that layout among the type columns and Cytoscape.js's grid, circle, concentric, breadth-first and force-directed layouts, keep the resulting positions as moved positions and fit them to the view.
- **Rationale**: the structure of a selection reads best under a layout suited to it (owner, 2026-11-23).
- **Priority**: Must
- **Acceptance Criteria**: Given the graph view, When "Circle" is chosen, Then the shown nodes are placed on a circle And all of them are in the view; When a filter then changes, Then they keep those positions.
- **Dependencies**: RQ-TRC-150

### RQ-TRC-163: Graph context menu
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the reader right-clicks the graph view, the explorer SHALL show a menu of the layouts and of fitting the view, and, on a node, of selecting it, hiding it and showing only its neighbours at one, two or three hops.
- **Rationale**: the actions on a node are reached where the node is (owner, 2026-11-23).
- **Priority**: Must
- **Acceptance Criteria**: Given the graph view, When a node is right-clicked And "Neighbours, 2 hops" is chosen, Then only the nodes at most two relations away from it are shown; When the background is right-clicked, Then the menu lists the layouts And no node action; When Escape is pressed or the page is clicked elsewhere, Then the menu closes.
- **Dependencies**: RQ-TRC-154, RQ-TRC-162

### RQ-TRC-164: Labelled controls with tooltips
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The explorer SHALL give every control a visible text label or an accessible name, and a tooltip saying what it does.
- **Rationale**: the pen, arrow and cross of the saved queries did not say what they did (owner, 2026-11-23).
- **Priority**: Must
- **Acceptance Criteria**: Given the explorer with the buttons being edited, Then every button, tab, checkbox and field has a non-empty `title` And the saved query tools read "Edit", "Move left", "Move right" and "Delete".
- **Dependencies**: RQ-TRC-153, RQ-TRC-155

### RQ-TRC-165: Graph legend
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The explorer's graph view SHALL show, as a horizontal band along its bottom edge, a legend of the colour of each node type and the look of each relation kind present in the loaded graph, drawn from the same tokens as the graph, which the reader can fold. <!-- amended 2026-11-23, TASK-TRC-148: a band at the bottom, as the performance center's legend (owner) -->
- **Rationale**: the colours and the dashed or plain lines were read without a key (owner, 2026-11-23).
- **Priority**: Must
- **Acceptance Criteria**: Given the graph view of a graph with requirements and `contains` relations, Then the legend lists RQ with its type colour And `contains` with a dashed line of its colour, on one wrapped row at the bottom of the view; When the legend is folded, Then only its title stays.
- **Dependencies**: RQ-TRC-147, RQ-TRC-018

### RQ-TRC-166: Layout direction choice
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the reader chooses the left-to-right or top-to-bottom direction, the explorer SHALL arrange the type columns, tree and grid layouts in that direction, and SHALL disable the choice for the layouts that have none.
- **Rationale**: a chain of types or a tree reads across or down depending on the graph's shape (owner, 2026-11-23).
- **Priority**: Must
- **Acceptance Criteria**: Given the type columns layout, When "Top to bottom" is chosen, Then the nodes of one type share one row And the types follow one another downwards; When "Circle" is chosen, Then the direction choice is disabled.
- **Dependencies**: RQ-TRC-162

### RQ-TRC-167: Node hover tooltip
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the pointer rests on a node of the graph view for the performance center's tooltip delay, the explorer SHALL show beside it a tooltip holding the head of the node's detail (type, ID, title, undefined note) and every property as the detail panel lists them, without changing the selection, and SHALL hide it when the pointer leaves the node or the view moves.
- **Rationale**: the reader compares a hovered node with the selected one shown on the right (owner, 2026-11-23).
- **Priority**: Must
- **Acceptance Criteria**: Given RQ-DEM-002 selected, When the pointer rests on RQ-DEM-001, Then no tooltip is shown before the delay And after it the tooltip lists the same properties as RQ-DEM-001's detail And the detail panel still shows RQ-DEM-002; When the pointer leaves the node, Then the tooltip is hidden.
- **Dependencies**: RQ-TRC-154, RQ-TRC-150

---

## Non-Functional Requirements

### RQ-TRC-156: Graph file unchanged by the explorer
- **Category**: Non-Functional
- **NFR Type**: Maintainability
- **EARS Type**: Ubiquitous
- **Statement**: The graph skill SHALL write the same `agnos-graph.json` bytes with and without `--explorer`, and the performance center's data SHALL differ from the data of before this feature by its output names and its graph path only.
- **Metric**: 0 byte of difference in the graph file between a run with and without `--explorer`; 0 byte of difference in the performance center's `.json` once its names and the graph path are restored.
- **Measurement Method**: build the graph of this repository and of the demo with and without `--explorer` at a fixed `--generated-at`, and the performance center's data at the base commit and after the change, and compare.
- **Priority**: Must
- **Acceptance Criteria**: Given this repository and the demo, When the graph is built with and without `--explorer`, Then the two graph files are byte-identical; Given the performance center's data before and after the change, Then they are identical but for the names and the graph path.
- **Dependencies**: RQ-TRC-129, RQ-TRC-141, RQ-TRC-144

### RQ-TRC-157: Type label contrast ratio
- **Category**: Non-Functional
- **NFR Type**: Accessibility
- **EARS Type**: Ubiquitous
- **Statement**: The explorer SHALL draw the text of each type label with a contrast ratio of at least 4.5:1 on its background.
- **Metric**: WCAG 2.1 contrast ratio ≥ 4.5:1 for each type's text token on the background it is drawn on.
- **Measurement Method**: a test computing the WCAG contrast ratio of each `type-*-text` token on the page and panel background tokens.
- **Priority**: Must
- **Acceptance Criteria**: Given the explorer's tokens, When each type's text colour is compared with the backgrounds it is drawn on, Then every ratio is at least 4.5:1.
- **Dependencies**: RQ-TRC-018, RQ-TRC-115

### RQ-TRC-158: Explorer load time
- **Category**: Non-Functional
- **NFR Type**: Performance
- **EARS Type**: Ubiquitous
- **Statement**: The explorer SHALL show this repository's graph, built with `--call-graph` and `--history`, in less than 5 seconds after the page is opened.
- **Metric**: time from the page's opening to the first view drawn < 5 s, on the maintainer's workstation.
- **Measurement Method**: a headless browser test opening the explorer on this repository's graph and timing the first drawn view, as the performance center's headless tests do.
- **Priority**: Should
- **Acceptance Criteria**: Given this repository's graph with call graph and history, When the explorer is opened in a headless browser, Then the first view is drawn in less than 5 s.
- **Dependencies**: RQ-TRC-145, RQ-TRC-146
