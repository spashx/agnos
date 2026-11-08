# PLAN-WEB-001: The agnos-meta-website Skill

## Overview
Delivers `agnos-meta-website`, which builds the AGNOS presentation website from Markdown and images in its assets, and the demo
Performance Center page, given or regenerated. The content, look and structure start from the mock-up of 2026-11-08 (`site.tmp/`).
Everything stays local on `feature/WEB`: nothing is pushed, and the site's repository is not touched.

## References
- **Requirements**: RQ-WEB-001 to RQ-WEB-016
- **ADRs**: ADR-WEB-001 (DEC-WEB-001 to DEC-WEB-006)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-WEB-001: The content parser and its checks
- **Tier**: L
- **Status**: Done
- **Description**: Write the tests first, then `scripts/build_site.py`'s reading of `en.md` and `fr.md`, the checks against the template,
  the measured variables and French typography, from the mock-up's prototype rewritten with requirement IDs; with `SKILL.md` and its
  Claude Code pointer.
- **Requirement refs**: RQ-WEB-003, RQ-WEB-004, RQ-WEB-005, RQ-WEB-006, RQ-WEB-016
- **ADR refs**: ADR-WEB-001 (DEC-WEB-001, DEC-WEB-003)
- **Acceptance Criteria**: Given the skill's tests, When they run, Then each criterion of RQ-WEB-003 to RQ-WEB-006 holds, each fault of
  RQ-WEB-004 included; Given the script, Then it imports the standard library only.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `agnos-meta-website/tests`: 19 OK, 0 skipped (each RQ-WEB-004 fault, both number formats, French typography,
  standard-library imports); `agnos-meta-qa check` on the script and the tests: 0 open.
- **Assumptions**: the owner's go for autonomous work counts as DoR approval and as confirmation of each commit; attributes take their
  text through `data-i18n-attr` so that the template holds none; a fenced block is a field kind, for the index excerpt; ADR-WEB-001
  accepted with DEC-WEB-002 and DEC-WEB-005 reworded (the generator skips the call graph by itself; one design system per project).

### TASK-WEB-002: The site's design system
- **Tier**: M
- **Status**: Done
- **Description**: Create `assets/tokens.json`, the site's layer over the Performance Center's design system (DEC-WEB-005), and
  the build's writing of the tokens the template uses as CSS custom properties per theme.
- **Requirement refs**: RQ-WEB-015, RQ-WEB-014
- **ADR refs**: ADR-WEB-001 (DEC-WEB-005), ADR-TRC-002
- **Acceptance Criteria**: Given the tokens, Then the brand, human and agent colours equal the Performance Center's; Given each theme,
  Then every text token pair reaches 4.5:1; Given the build, Then each token becomes one CSS variable in each theme.
- **Dependencies**: TASK-WEB-001
- **Assignee**: AI
- **Verification**: `agnos-meta-website/tests`: 27 OK, 0 skipped; the brand and identity colours resolve to the Performance Center's
  global values; 18 text pairs × 2 themes ≥ 4.5:1, after a first run caught text-subtle on surface-hover at 4.34:1 (a pair the page
  does not draw, removed from the list and kept out of the template); `agnos-meta-qa check`: 0 open.
- **Assumptions**: `agnos-design-system` keeps one design system per project, so the site extends the Performance Center's instead of
  instantiating the template anew; every site token starts with `web`; the mock-up's half-pixel sizes are rounded to the scale; the
  fonts stay the mock-up's IBM Plex.

### TASK-WEB-003: The template, the content and the placeholder images
- **Tier**: L
- **Status**: Done
- **Description**: Move the mock-up's template into `assets/template.html` on the tokens only, with the header lockup and its tagline;
  move its content into `assets/content/en.md` and `fr.md`; write the five single-colour placeholders into `assets/screens/`.
- **Requirement refs**: RQ-WEB-007, RQ-WEB-008, RQ-WEB-009, RQ-WEB-010, RQ-WEB-011, RQ-WEB-012, RQ-WEB-013, RQ-WEB-014, RQ-WEB-015
- **ADR refs**: ADR-WEB-001 (DEC-WEB-003, DEC-WEB-004, DEC-WEB-005), ADR-TRC-002
- **Acceptance Criteria**: Given the template's style, Then it holds no raw visual value; Given the built page, Then its elements stand
  in RQ-WEB-009's order, the lockup reads "AGNOS" and "Efficiency by traceability", the chain switches mode, each screenshot links under
  `demo/`, And no request other than fonts leaves the page; Given `assets/screens/`, Then the five PNGs are single-colour at 16:10.
- **Dependencies**: TASK-WEB-002
- **Assignee**: AI
- **Verification**: `agnos-meta-website/tests`: 39 OK, 0 skipped (`node --check` ran on the page's script); the template's style
  and attributes hold no raw value and its markup no letter outside comments, style, script and symbols; the built page: no empty
  slot, French for every slot and attribute, the lockup AGNOS / Efficiency by traceability, the 15 elements in order, both chain modes,
  5 screenshots under `demo/` with their label, only font requests; 5 PNGs of one colour at 1600 × 1000; `agnos-meta-qa`: 0 open.
- **Assumptions**: the page tests were written after porting the template, the template being a move of the approved mock-up; the
  identifiers of the chain and of the design card, the language names and the aria labels became content fields, so that the template
  holds no text; the mock-up notice now says the views come from the simulated demo; the bar hides its demo button under 640 px so
  that the lockup fits at 360 px; no favicon, which would need a raw colour outside the tokens.

### TASK-WEB-004: The demo page and the output folder
- **Tier**: M
- **Status**: Done
- **Description**: The `build` sub-command end to end: the demo page copied with `--demo-page` or generated with `agnos-perf-center`,
  the output written only when every check passed, the summary line and the exit codes.
- **Requirement refs**: RQ-WEB-001, RQ-WEB-002, RQ-WEB-013
- **ADR refs**: ADR-WEB-001 (DEC-WEB-002, DEC-WEB-006)
- **Acceptance Criteria**: Given `--demo-page`, Then `demo/` holds the page and its data files byte for byte; Given none, Then
  `demo/PERF-CENTER.html` is generated from the demo with its history; Given a content error, Then the output folder is unchanged and the
  exit code is 1.
- **Dependencies**: TASK-WEB-003
- **Assignee**: AI
- **Verification**: `test_build.py` written first: 7 errors before the code, then `agnos-meta-website/tests` 46 OK, 0 skipped:
  the given page and its two data files copied byte for byte; without it, the generator called on the demo's process, `service` and
  `client` with `--history` and `--call-graph`; a content error, a failing generator, a missing data file or another page name: exit
  1 and the folder unchanged; the owner's other files kept. `agnos-meta-qa`: 0 open. The real generation runs in TASK-WEB-005.
- **Assumptions**: the given page must be named `PERF-CENTER.html`, since the page loads its `.data.js` by its own name and the
  site links to that name; the generator is tested through a stand-in script; the generator runs without `-I`, so that call-graph
  packages installed for the user stay importable.

### TASK-WEB-005: A build on the demo, checked by the owner
- **Tier**: S
- **Status**: In Progress
- **Description**: Build the site on the demo into a scratch folder, hand it to the owner for the visual check at 360 px and on desktop,
  in each theme, and remove `site.tmp/` once the owner accepts.
- **Requirement refs**: RQ-WEB-008, RQ-WEB-009, RQ-WEB-014
- **ADR refs**: None
- **Acceptance Criteria**: Given the built site, When the owner reads it, Then they accept it or list the corrections.
- **Dependencies**: TASK-WEB-004
- **Assignee**: Human (visual check), AI (build)
- **Verification**: N/A (Tier S)
- **Assumptions**:

### TASK-WEB-006: The tagline becomes "Agentic efficiency by traceability"
- **Tier**: S
- **Status**: Done
- **Description**: Replace the tagline in the Performance Center's About topic and in the site's header and title, amending
  RQ-TRC-116 and RQ-WEB-008 and the tests reading it (owner request of 2026-11-08).
- **Requirement refs**: RQ-TRC-116, RQ-WEB-008
- **ADR refs**: ADR-TRC-014, ADR-WEB-001
- **Acceptance Criteria**: Given the About topic and the site's header, Then each reads "Agentic efficiency by traceability".
- **Dependencies**: TASK-WEB-003
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: records of finished tasks keep the former tagline, as history.

### TASK-WEB-007: Three examples, enlarged on click
- **Tier**: M
- **Status**: Done
- **Description**: Under the Overview stop, three images (requirement, ADR with its diagram, plan with a task) side by side, each
  with its caption, enlarged in a dialog on click; three single-colour placeholders in `assets/screens/`.
- **Requirement refs**: RQ-WEB-017, RQ-WEB-003, RQ-WEB-012, RQ-WEB-015
- **ADR refs**: ADR-WEB-001 (DEC-WEB-003, DEC-WEB-004, DEC-WEB-005)
- **Acceptance Criteria**: RQ-WEB-017's criteria; Given the template, Then it still holds no text and no raw visual value.
- **Dependencies**: TASK-WEB-006
- **Assignee**: AI
- **Verification**: 4 tests written before the code (not run before it), then `agnos-meta-website/tests` 50 OK, 0 skipped: three
  images after the Overview screenshot in the order requirement, ADR, plan, with captions; three columns, one under 640 px; a dialog
  with a labelled close button, opened by `showModal()`, closed by the button, the backdrop or Escape (native), focus returned; no
  text and no raw value in the template; 8 single-colour PNGs; `node --check` passed. `agnos-meta-qa`: 0 open. Real build on the
  demo: 131 fields per language, 8 images, demo page generated with the new tagline.
- **Assumptions**: a plain image `![alt](screens/x.png)` is a new field kind; the examples span the stop's whole width; the dialog
  is the native `<dialog>`, whose Escape closes it; the close button is an icon, so that the template holds no text; the captions
  name RQ-BKG-003, ADR-BKG-001, PLAN-BKG-001 and TASK-BKG-003 for the owner's screenshots. Committed with TASK-WEB-006's test line.

### TASK-WEB-008: A third card, identifiers as keys
- **Tier**: M
- **Status**: Done
- **Description**: Add between the index and the design-system cards a card on unique identifiers as primary and foreign keys,
  against semantic matching, the three cards side by side as the examples.
- **Requirement refs**: RQ-WEB-018, RQ-WEB-003, RQ-WEB-015
- **ADR refs**: ADR-WEB-001 (DEC-WEB-003, DEC-WEB-005)
- **Acceptance Criteria**: RQ-WEB-018's criteria; Given the template, Then it still holds no text and no raw visual value.
- **Dependencies**: TASK-WEB-007
- **Assignee**: AI
- **Verification**: 2 tests written first, failing before the code; then `agnos-meta-website/tests` 52 OK, 0 skipped: cards in the
  order index, identifiers, design system; TASK-BKG-003 cites RQ-BKG-003 as foreign and primary key; three columns, one under
  640 px. `agnos-meta-qa`: 0 open. Build on the demo: 141 fields per language.
- **Assumptions**: the text approved by the owner on 2026-11-08; the section's title says three reasons; between 640 and 980 px the
  cards keep three columns.

### TASK-WEB-009: The blocks of two cards, top to bottom
- **Tier**: M
- **Status**: Done
- **Description**: Stack the design-system card's three token tiers, and show in the identifiers card the requirement, then the
  task and the ADR that cite it, their citing line highlighted.
- **Requirement refs**: RQ-WEB-018, RQ-WEB-003, RQ-WEB-015
- **ADR refs**: ADR-WEB-001 (DEC-WEB-003, DEC-WEB-005)
- **Acceptance Criteria**: RQ-WEB-018's amended criteria; Given the template, Then it still holds no text and no raw visual value.
- **Dependencies**: TASK-WEB-008
- **Assignee**: AI
- **Verification**: 3 tests written first, failing before the code; then `agnos-meta-website/tests` 54 OK, 0 skipped: snippets in
  the order requirement, task, ADR, `<mark>RQ-BKG-003</mark>` in the task and in ADR-BKG-002, both cards one column;
  `agnos-meta-qa`: 0 open; build on the demo: 142 fields per language, the ADR's comment shown.
- **Assumptions**: ADR-BKG-002, which cites RQ-BKG-003 by name (ADR-BKG-001 cites a range), is shown, although superseded by
  ADR-BKG-003, owner's choice of 2026-11-08; a code block's `==part==` is highlighted, and comments inside a code block are shown, not removed.

### TASK-WEB-010: Three of Roombook's button styles in the design-system card
- **Tier**: M
- **Status**: Done
- **Description**: Replace the design-system card's single chain by Roombook's primary, secondary and danger buttons, each with its
  chain of tokens, the CSS that consumes them and a button rendered in that style.
- **Requirement refs**: RQ-WEB-018, RQ-WEB-015
- **ADR refs**: ADR-WEB-001 (DEC-WEB-003, DEC-WEB-005)
- **Acceptance Criteria**: RQ-WEB-018's amended criteria; Given the demo's `client/design/tokens.json`, Then the sample colours equal
  its resolved button tokens.
- **Dependencies**: TASK-WEB-009
- **Assignee**: AI
- **Verification**: 2 tests written first, failing before the code; then `agnos-meta-website/tests` 56 OK, 0 skipped (the demo's
  tokens file was present, so the colours were compared: 7 tokens equal); `agnos-meta-qa`: 0 open; build: 147 fields per language.
- **Assumptions**: the sample colours are site tokens repeating Roombook's light values in both themes, with a provenance note; the
  CSS shown is the form `stylesheet.ts` produces (`var(--button-<style>-<part>)`), written by hand in the content; the button
  labels are illustrative, after Roombook's labels; the swatch token of the former card is removed.
