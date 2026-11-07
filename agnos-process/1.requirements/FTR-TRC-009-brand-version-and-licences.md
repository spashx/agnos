# FTR-TRC-009: Brand, Version and Licences in the Page

## Overview
At the owner's review of 2026-11-06, the page of the performance center was found to say too little of itself where a
reader looks, and too much where nobody does. The foot of the left panel lists the libraries and their licences in a line
of small text, while it could name the application and its version; the licences belong in the Help dialog, in a topic of
their own, drawn as coloured badges in the manner of the GitHub badges of a README (grey label, coloured value); the About
topic shows the author's name as the label of its links where it could show their addresses, and says "this page" of an
application; and the brand mark, three dots in one accent colour, is neither distinctive nor coloured. After three
mock-ups, the owner retained on 2026-11-06 the design "Spans": a grey tile holding four horizontal bars, a light one across
the top and three coloured ones stepping to the right, in blue, green and yellow close to Google's.

The application's version is that of AGNOS, which the performance center is a skill of; it is read from the one place
RQ-PLG-032 gives it, so it is never copied.

Unchanged: the data files, the views and their tabs, the Help dialog's other topics, the libraries and how they are loaded.
Out of scope: a favicon; showing the patch number; a third-party notice file.

## Stakeholders
- **Owner**: the repository owner.
- **Consumers**: readers of the generated page; maintainers adding a library to the library record.

---

## Functional Requirements

### RQ-TRC-109: Title and version at the foot of the left panel
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The page SHALL show, at the bottom of its left panel, the application's title, "AGNOS Performance Center", followed by its version as `v.<major>.<minor>`, both taken at generation from the `VERSION.txt` file of RQ-PLG-032 (the patch number is not shown), in place of the notice of the libraries and their licences. Amends RQ-TRC-082 on where the notice stands.
- **Rationale**: a reader of a page found in a report or a chat should know which tool and which version made it; the notice of the libraries moves to the Licenses topic (RQ-TRC-111).
- **Priority**: Must
- **Acceptance Criteria**: Given a `VERSION.txt` holding `3.1.0`, When a page is generated, Then the foot of the left panel reads "AGNOS Performance Center v.3.1" And names no library; Given `3.12.4`, Then it reads "v.3.12"; Given only `VERSION.txt` changed, Then the next page shows the new version without any other file changed.
- **Dependencies**: RQ-PLG-032, RQ-TRC-082, RQ-TRC-010

### RQ-TRC-110: A version that cannot be read
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: IF the `VERSION.txt` file is absent, or is not one line holding a SemVer 2.0.0 version, THEN the generator SHALL still write the page, whose foot shows the title alone, with no `v.`.
- **Rationale**: a page is more useful without its version than not generated; the file stands beside the skill's, and a layout without it is a packaging problem the page need not break on.
- **Priority**: Must
- **Acceptance Criteria**: Given no `VERSION.txt` file, When a page is generated, Then the generator exits 0 And the foot reads "AGNOS Performance Center" with no `v.`; Given a `VERSION.txt` holding `v3.2`, Then the same.
- **Dependencies**: RQ-TRC-109, RQ-PLG-032

### RQ-TRC-111: A Licenses topic in the Help dialog
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The Help dialog SHALL hold a Licenses topic, listed between "Search and details" and "About", showing the application's own licence, a link to its text opening in a new tab, and each library of the library record with its name, its version and its licence; the About topic SHALL no longer show the licence. Amends RQ-TRC-103.
- **Rationale**: the licences of what the page is and of what it loads belong together, in a place of their own; the licence was a link among the author's (owner request of 2026-11-06).
- **Priority**: Must
- **Acceptance Criteria**: Given a page, When the Help topics are listed, Then Licenses stands after "Search and details" and before "About", on a page with or without history; When Licenses is chosen, Then the application's licence and Cytoscape.js 3.30.2 and Apache ECharts 6.1.0 of the record each show with their licence; When About is chosen, Then no licence link shows; Given a version changed in the library record only, Then the topic shows that version.
- **Dependencies**: RQ-TRC-101, RQ-TRC-103, RQ-TRC-082

### RQ-TRC-112: Licences drawn as coloured badges
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The Licenses topic SHALL draw each licence as a two-part badge in the manner of the GitHub README badges: a grey label holding the name (for a library, its name and version; for the application, "AGNOS") and, against it, a value holding the licence, filled with a brand colour that depends on the licence; the badge SHALL be drawn by the page itself and request nothing from any site.
- **Rationale**: a coloured badge is read at a glance and is what readers know from repositories (owner request of 2026-11-06, with a sample); drawing it locally keeps RQ-TRC-080's promise that the page requests nothing else.
- **Priority**: Must
- **Acceptance Criteria**: Given the Licenses topic, When a badge is inspected, Then it has a label part and a value part side by side, the label grey and the value filled with one of the brand blue, green, yellow or light tokens; Given two libraries of different licences, Then their values have different fills; Given the page's requests, Then none goes to a badge service.
- **Dependencies**: RQ-TRC-111, RQ-TRC-080, ADR-TRC-002

### RQ-TRC-113: The About topic says "app" and shows the addresses
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The About topic SHALL say "This app is generated by agnos-perf-center, a skill of the AGNOS process.", and each of its link buttons SHALL show the address it opens, with the icon of its site, and SHALL NOT show the author's name as its label. Amends RQ-TRC-103.
- **Rationale**: a reader sees where a link goes before following it, and the page is the application's output, not the application (owner request of 2026-11-06).
- **Priority**: Should
- **Acceptance Criteria**: Given the About topic, When its text is read, Then it starts "This app is generated by" And does not say "This page"; When its link buttons are read, Then the first reads `https://github.com/spashx` and the second `https://www.linkedin.com/in/64493197`, each beside an icon, And none reads "spashx" alone as its label.
- **Dependencies**: RQ-TRC-103, RQ-TRC-111

### RQ-TRC-114: A distinctive, coloured brand mark
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The page's brand mark SHALL be the "Spans" design, in the header in place of the three dots: a grey rounded tile holding four horizontal bars, a light one across its top and, below it, a blue, a green and a yellow one, each starting further right than the one above; and the About topic SHALL show the same mark, several times larger, above its text.
- **Rationale**: the brand should be recognised and remembered: a mark of its own, in colours of its own, shown large where the reader learns who made the page (owner request of 2026-11-06, design retained the same day).
- **Priority**: Must
- **Acceptance Criteria**: Given the page, When the header and the About topic are read in a browser, Then each holds the mark, its tile and four bars filled with the brand grey, light, blue, green and yellow; And the About mark is at least three times the header mark's width; Given the light and the dark themes, Then the mark is the same in both.
- **Dependencies**: RQ-TRC-103, ADR-TRC-002

### RQ-TRC-116: The name and the tagline beside the mark in About
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The About topic SHALL show, to the right of the large mark and centred on it, the name "AGNOS" in capital letters, bold and widely spaced, and below it the tagline "Efficiency by traceability", smaller, of medium weight and in the muted text colour, both from design-system tokens and following the theme; the mark, the name and the tagline SHALL stand above the About text.
- **Rationale**: the mark alone does not say whose it is; the lockup of the retained design names it where the reader learns who made the page (owner request of 2026-11-06, from the design's lockup, with this tagline in place of the design's).
- **Priority**: Must
- **Acceptance Criteria**: Given the About topic, When it is read in a browser, Then the name reads "AGNOS" and the tagline "Efficiency by traceability", the name to the right of the mark, the tagline below the name and aligned with it on the left, the pair centred on the mark, all above the text; And the name is 30 px, bold, with a letter-spacing of 0.12 em, and the tagline 13 px, weight 500, with 0.02 em; And their colours are those of the text and the muted-text tokens, in each theme; Given the style and the script, Then they hold no raw visual value.
- **Dependencies**: RQ-TRC-114, RQ-TRC-018, ADR-TRC-002

## Non-Functional Requirements

### RQ-TRC-115: Brand and badge colours from the design system, readable
- **Category**: Non-Functional
- **NFR Type**: Accessibility
- **EARS Type**: Ubiquitous
- **Statement**: Every colour of the mark and of the badges SHALL come from design-system tokens, and the text of a badge SHALL keep a contrast of at least 4.5:1 with its fill, in both themes.
- **Metric**: contrast ratio of each badge text over its fill, at least 4.5:1; raw visual values in the page's style, script and template: 0.
- **Measurement Method**: a unit test computing the ratios from the token file; the existing test of RQ-TRC-018, which finds no raw visual value in `matrix.css`, `matrix.js` and `matrix.html`.
- **Priority**: Must
- **Acceptance Criteria**: Given the token file, When the contrast of each badge text over its fill is computed, Then none is below 4.5; Given the page's style, script and template, Then they hold no raw colour.
- **Dependencies**: RQ-TRC-018, RQ-TRC-112, RQ-TRC-114, ADR-TRC-002
