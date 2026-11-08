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
- **Status**: Not Started
- **Description**: Build the site on the demo into a scratch folder, hand it to the owner for the visual check at 360 px and on desktop,
  in each theme, and remove `site.tmp/` once the owner accepts.
- **Requirement refs**: RQ-WEB-008, RQ-WEB-009, RQ-WEB-014
- **ADR refs**: None
- **Acceptance Criteria**: Given the built site, When the owner reads it, Then they accept it or list the corrections.
- **Dependencies**: TASK-WEB-004
- **Assignee**: Human (visual check), AI (build)
- **Verification**: N/A (Tier S)
- **Assumptions**:
