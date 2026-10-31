# FTR-TRC-007: A Skill Limited to its Contract, a Guide in the Page

## Overview
`.github/skills/agnos-trace/SKILL.md` has grown to 295 lines, about 7,200 tokens loaded each time the skill runs, six times
the next largest AGNOS skill. About 69 % of it is needed neither to run the skill nor to report its result: it describes
the page, the rules and the data format. An agent only has to run the script; the owner decided on 2026-10-31 that the
skill holds its contract, that what an agent may need when asked moves to files read on demand, and that the reader's
guide moves into the page, the only place humans read it.

Unchanged: the generator's behaviour, its arguments and outputs, the page's views.
Out of scope: a compact summary or queries for an agent at session start (a later feature); any change to the AGNOS
instructions file.

## Stakeholders
- **Owner**: the repository owner.
- **Consumers**: agents running the skill; agents asked about a result; readers of the page; tools reading `<page>.json`.

---

## Functional Requirements

### RQ-TRC-098: The skill holds its contract
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: `SKILL.md` SHALL hold only when to use the skill, its prerequisites, its command and parameters, its outputs,
  its exit codes, the meaning of its summary line, what to report to the user, and where to find the rest. Refines
  RQ-TRC-017, which it keeps.
- **Rationale**: running the skill should not load what only explaining a result needs.
- **Priority**: Must
- **Acceptance Criteria**: Given an agent with `SKILL.md` alone, When it follows the procedure, Then it produces the page and
  reports the quality score and the check scores printed by the generator; Given `SKILL.md`, Then it describes no view of the
  page, no algorithm and no data format.
- **Dependencies**: RQ-TRC-017, RQ-AGT-001

### RQ-TRC-099: The rest read on demand
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN an agent is asked why a result reads as it does or how to maintain the skill, `SKILL.md` SHALL send it to
  one file of the skill's `references/` folder: the rules and scoring, the data format, or the maintenance; each fact of the
  former `SKILL.md` that is not about the page SHALL be kept in one of them.
- **Rationale**: `process/` is not delivered with the toolkit, so a link to a requirement or an ADR would break in a host
  project (RQ-DMO-002); the information stays relevant, only not at each run.
- **Priority**: Must
- **Acceptance Criteria**: Given `SKILL.md` alone and the question "what does an `undefined` finding mean?", When an agent
  answers, Then it reads one reference and gives the rule, including that an ID quoted as an example counts as a citation; Given
  the former text, Then its rules, formats and maintenance facts are found in `references/`.
- **Dependencies**: RQ-TRC-098, RQ-DMO-002

### RQ-TRC-100: The data format is a contract
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: `references/data-format.md` SHALL describe every top-level block of `<page>.json` and the fields of each,
  `history` and `delivery` included, as the contract for any other tool.
- **Rationale**: a later feature may let agents read these data; tools already may (SKILL.md promised it to "any other tool").
- **Priority**: Must
- **Acceptance Criteria**: Given a page generated with `--call-graph` and `--history`, When its top-level keys and those of
  `history` and `delivery` are listed, Then a test finds each named in the document.
- **Dependencies**: RQ-TRC-099, RQ-TRC-010

### RQ-TRC-101: The guide in the page
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the reader activates the Help control of the page's header, the page SHALL open, over the current
  view, the guide of the current tab alone, with a list of the other tabs the page holds to read theirs, in the design system;
  a guide longer than the dialog SHALL scroll inside the dialog, its list and its close control staying in view, and
  the reader SHALL be able to resize the dialog, above a minimum size.
- **Rationale**: no reader's guide exists outside `SKILL.md`, which readers do not open; `--history` views are not described
  anywhere else.
- **Priority**: Should
- **Acceptance Criteria**: Given a page with history, When Help is activated on the Delivery tab, Then only the Delivery guide
  shows; When Graph is chosen in its list, Then the Graph guide replaces it and the current view stays Delivery; When Escape is
  pressed, Then it closes and the focus returns to the control; Given a page without history, Then the list has no History nor
  Delivery; Given a guide longer than the dialog, Then only the guide scrolls; Given the style and the script, Then they hold no raw visual value for it.
- **Dependencies**: RQ-TRC-018, RQ-HST-016, ADR-TRC-002

### RQ-TRC-103: About the author
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The Help dialog SHALL hold an About topic, linking to the GitHub and LinkedIn profiles of spashx and to the
  repository's licence, each opening in a new tab; the page SHALL request nothing from them until a link is followed.
- **Rationale**: a reader of a generated page should find who made the tool (owner request of 2026-10-31).
- **Priority**: Could
- **Acceptance Criteria**: Given the Help dialog, When About is chosen, Then the three links show, each opening in a new tab.
- **Dependencies**: RQ-TRC-101, RQ-TRC-080

## Non-Functional Requirements

### RQ-TRC-102: The skill stays small
- **Category**: Non-Functional
- **NFR Type**: Maintainability
- **EARS Type**: Ubiquitous
- **Statement**: `SKILL.md` SHALL not exceed 50 lines and its front-matter description 400 characters.
- **Metric**: lines of the file; characters of the description.
- **Measurement Method**: a unit test of the skill.
- **Priority**: Must
- **Acceptance Criteria**: Given a `SKILL.md` of 51 lines or a description of 401 characters, When the test runs, Then it fails
  and names the limit.
- **Dependencies**: RQ-TRC-098
