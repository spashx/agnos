# FTR-HST-002: Consistent Tooltips and Wording of the Traceability Page

## Overview
The traceability page (FTR-TRC-001, FTR-TRC-003, FTR-HST-001) explains what it shows through tooltips of several kinds:
the browser's own (`title`), the search's, the charts' and the History tab's. They differ in form for the same kind of
information, two of them sometimes show at once (a chart's SVG title under the chart's tooltip; the timeline frame's
help under a commit's card), and one of them cites a requirement ID, an implementation detail that AGNOS keeps in the
comments. This feature, asked by the owner on 2026-10-24, sets one rule for the whole page:
- a **rich tooltip** (a bold first line, its details below) for every piece of business information: an element, a
  file, a function, a relation, a figure, a grade, an identity, a commit;
- a **plain tooltip** (the browser's text) only to say what a control does: a tab, a button, a toggle, a filter;
- never two tooltips at once, and no requirement, decision or task ID in the page's own wording.

The content of each rich tooltip is listed in RQ-HST-017, as agreed with the owner. Out of scope: the data shown in the
page (an element's own title may of course hold IDs), and the wording of the generator's command line.

## Stakeholders
- **Owner**: the repository owner.
- **Consumers**: every reader of the page; the page (FTR-TRC-001) and its History tab (FTR-HST-001).

---

## Functional Requirements

### RQ-HST-016: Two kinds of tooltip, never two at once
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The page SHALL show business information in one rich tooltip component (a bold first line, its
  details below, the design tokens' card style and delay, shown on hover and on keyboard focus, kept inside the window),
  SHALL keep the browser's plain tooltip for what a control does, and SHALL never show two tooltips at once: no element
  holding a rich tooltip SHALL carry, itself or through a container or an SVG title, a plain one.
- **Rationale**: one form per kind of information reads as one product; two tooltips at once hide each other (owner
  request of 2026-10-24).
- **Priority**: Must
- **Acceptance Criteria**: Given the page, When the pointer rests on a radar point, a commit mark, a graph node or an
  identity, Then one rich tooltip shows and no `title` attribute nor SVG `<title>` lies on the element or its
  containers; Given a button or a filter chip, Then it has a plain `title` saying what it does; Given a rich tooltip,
  Then its first line is bold and it stays inside the window.
- **Dependencies**: RQ-TRC-018, ADR-TRC-002, RQ-TRC-049, RQ-HST-014

### RQ-HST-017: The content of the rich tooltips
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The rich tooltips SHALL hold, bold line first:
  - a graph element node: its type, **its ID**, its title, its status, its coverage for a requirement, its document
    and lines, its number of links;
  - a graph file node: **its file name**, its path, the number of IDs it cites, its number of functions;
  - a graph function node: **its qualified name**, its file and lines, its language, its callers and callees, the IDs
    it cites;
  - a graph box: **its name**, its kind (namespace or class), its number of functions;
  - a graph relation: **the relation** (cites, contains, implements, defines, calls), its source and target, its first
    two lines of proof;
  - a graph legend item: **the relation or box kind**, what it means;
  - an element ID in the matrix, a finding, a search result: its type, **its ID**, its title, its location, its status;
  - a coverage badge or bar: **covered, indirect or uncovered**, the count out of the total and its share, its
    definition;
  - a header item: **its label**, its whole value;
  - a quality shortcut, a "Fix first" link: **the check**, its score out of 10, its risk, its number of findings, its
    rule;
  - a check's score, risk and findings: **"Score s / 10"** and its formula; **"Risk r"** and its weight; **"n
    findings"** and what a finding is;
  - a grade chip, a step of the A to E scale, a trigram's grade: **"Grade g"**, its verdict and its range of scores; for a
    trigram, **the trigram**, its score and grade and its checks under the attention threshold;
  - a History row label: its type, **its ID or path**, its title, its number of changes and of identities, its last
    change (date and author);
  - an identity, wherever it shows: **its name and kind**, its commits as author and co-author, its names, its e-mails,
    and how it was merged only when it was;
  - the History limits: **"History read"**, its period, depth, commits, and "cut" for a shallow clone;
  - a commit mark, an activity bar, a quality chart item, a search result: as they are today, in this form;
  - a call-site count, the "ambiguous" and "no function" badges of the detail panel: **the label**, its explanation.
- **Rationale**: the reader gets, where the pointer is, the facts a decision needs, named the same everywhere (content
  agreed with the owner on 2026-10-24).
- **Priority**: Must
- **Acceptance Criteria**: Given the fixture page, When the pointer rests on a requirement node of the graph, Then the
  tooltip's bold line is its ID and it shows its title, coverage and location; Given a file node, Then its bold line is
  the file name and its path is below; Given a matrix ID, Then its tooltip has the form of the search's; Given an
  identity that merged nothing, Then its tooltip says nothing of a merge.
- **Dependencies**: RQ-HST-016, RQ-TRC-012, RQ-TRC-014, RQ-TRC-015, RQ-TRC-060, RQ-TRC-062, RQ-HST-010

### RQ-HST-018: No implementation ID in the page's wording
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The page's own visible text (labels, tooltips, messages, accessible names) SHALL hold no ID of a
  feature, requirement, decision, plan or task of the skill's own process; such IDs SHALL stay in the code's comments.
- **Rationale**: AGNOS traces its implementation in comments; an ID in the interface means nothing to its reader (owner
  request of 2026-10-24).
- **Priority**: Must
- **Acceptance Criteria**: Given the page script and skeleton, When their string literals and visible texts are read,
  comments aside, Then none holds an ID of the AGNOS grammar; Given the rendered fixture page, Then the IDs it shows are
  those of the fixture's data only.
- **Dependencies**: RQ-HST-016
