# PLAN-TRC-014: Brand, Version and Licences in the Page

## Overview
Give the page a coloured brand mark in the design system, a foot naming the application and its version, a Licenses topic of local badges in the Help dialog, and About links showing their addresses. Each task writes its Gherkin-named tests first.

## References
- **Requirements**: RQ-TRC-109 to RQ-TRC-115; amended: RQ-TRC-082, RQ-TRC-103
- **ADRs**: ADR-TRC-014 (DEC-TRC-056 to DEC-TRC-058); uses ADR-TRC-002 (the design system), ADR-TRC-012 (the Help dialog)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-TRC-092: Brand and badge tokens
- **Tier**: M
- **Status**: Done
- **Description**: Add the five brand colours of the "Spans" design, the large mark's size and the component tokens of the mark and the badges (label, ink, tones) to `assets/tokens.json`.
- **Requirement refs**: RQ-TRC-114, RQ-TRC-115
- **ADR refs**: ADR-TRC-014 (DEC-TRC-056), ADR-TRC-002
- **Acceptance Criteria**: Given the token file, When it is resolved, Then `--s-brand-tile`, `--s-brand-light`, `--s-brand-blue`, `--s-brand-green` and `--s-brand-yellow` hold `#3C4043`, `#E8EAED`, `#4285F4`, `#34A853` and `#FBBC05` in both themes; Given the badge ink over each brand tone (blue, green, yellow, light), and white over the label, Then no ratio is below 4.5; Given `matrix.css`, `matrix.js` and `matrix.html`, Then they hold no raw visual value.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `test_brand.py` (new): 3 run, failed first (1 failure, 2 errors, tokens absent), then 3 OK, 0 skipped. `test_perf_center.py -k RQ_TRC_018`: 3 OK (no raw visual value in the page files). `test_literals.py`: 2 OK. `tokens.json` loads as JSON.
- **Assumptions**: Badge ink is the existing `color.slate-950` and the label `color.slate-600` with white text; the About mark is 96px, three times the control height; badge height 24px; the brand colours have one value for both themes.

### TASK-TRC-093: The brand mark in the header and, larger, in About
- **Tier**: M
- **Status**: Not Started
- **Description**: Draw the "Spans" mark as one symbol of the template's sprite, use it in the header in place of the three dots and above the About text at a larger size, its colours set from the component tokens.
- **Requirement refs**: RQ-TRC-114, RQ-TRC-115
- **ADR refs**: ADR-TRC-014 (DEC-TRC-056)
- **Acceptance Criteria**: Given the page, When the header and the About topic are read in a browser, Then each holds the mark, whose tile and four bars are filled with the brand tile, light, blue, green and yellow tokens, the three coloured bars each starting further right than the one above; And the About mark is at least three times as wide as the header's; Given the light and the dark themes, Then the filled colours are equal.
- **Dependencies**: TASK-TRC-092
- **Assignee**: AI
- **Verification**: (at closure)
- **Assumptions**: (at closure)

### TASK-TRC-094: The foot names the application and its version
- **Tier**: M
- **Status**: Not Started
- **Description**: Read `VERSION` at generation, replace a `@VERSION@` marker of the template by `v.<major>.<minor>` or by nothing, write the foot as static text of the template, and remove the footer's library line from the page script.
- **Requirement refs**: RQ-TRC-109, RQ-TRC-110
- **ADR refs**: ADR-TRC-014 (DEC-TRC-057)
- **Acceptance Criteria**: Given a `VERSION` of `3.1.0`, When a page is generated, Then its foot reads "AGNOS Performance Center v.3.1" and names no library; Given `3.12.4`, Then `v.3.12`; Given no `VERSION`, or `v3.2`, Then the run exits 0 and the foot reads the title alone; Given the data files, Then they are unchanged: the hash of RQ-TRC-026 stays.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: (at closure)
- **Assumptions**: (at closure)

### TASK-TRC-095: The Licenses topic and its badges
- **Tier**: M
- **Status**: Not Started
- **Description**: Add the Licenses topic between "Search and details" and "About": the application's licence and the link to its text, written in the template, and the libraries of `meta.libraries` listed by the script, each licence a two-part badge from the component tokens, its tone (green, blue, yellow or light) from a table keyed by licence; remove the licence link from About; write the topic's guide text; align RQ-TRC-082 and RQ-TRC-103 with a dated comment; note the tone table in `references/maintaining.md`.
- **Requirement refs**: RQ-TRC-111, RQ-TRC-112, RQ-TRC-115
- **ADR refs**: ADR-TRC-014 (DEC-TRC-058), ADR-TRC-012
- **Acceptance Criteria**: Given a page with and without history, When the Help topics are listed, Then Licenses stands after "Search and details" and before "About"; When Licenses is chosen, Then the application's licence and each library of the record show as a badge with a label and a value, the values of two different licences filled differently; When About is chosen, Then no licence link shows; Given a licence of the record absent from the tone table, Then a test fails naming it; Given the page's requests, Then none goes to a badge service.
- **Dependencies**: TASK-TRC-092, TASK-TRC-093
- **Assignee**: AI
- **Verification**: (at closure)
- **Assumptions**: (at closure)

### TASK-TRC-096: The About topic says "app" and shows the addresses
- **Tier**: S
- **Status**: Not Started
- **Description**: Say "This app" in place of "This page" in the About text, and show the address each About link opens, beside its icon, in place of "GitHub: spashx" and "LinkedIn: spashx".
- **Requirement refs**: RQ-TRC-113
- **ADR refs**: ADR-TRC-014 (DEC-TRC-058)
- **Acceptance Criteria**: Given the About topic, When its text and link buttons are read, Then the text starts "This app is generated by" and the buttons read `https://github.com/spashx` and `https://www.linkedin.com/in/64493197`, each beside an icon, and none reads "spashx" alone.
- **Dependencies**: TASK-TRC-095
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: None
