# FTR-TRC-010: Dark Theme Readability

## Overview
At the owner's review of 2026-11-07, the dark theme of the performance center page was found too dark. The page, the cards,
the left panel and the detail panel all share one surface, `#0F172A`, so no plane stands out; the fields are darker than
their container; the borders hardly show (1.22:1); and the subtle text (`text-subtle`, 3.75:1) is under WCAG AA. After a
mock-up of three candidates, the owner retained on 2026-11-07 the candidate "P2" with the fragile colours adjusted.

Unchanged: the light theme, the layout, the views. Out of scope: a theme switch, a high-contrast theme.

## Stakeholders
- **Owner**: the repository owner.
- **Consumers**: readers of the generated page in a dark colour scheme.

---

## Functional Requirements

### RQ-TRC-117: Surfaces in layers in the dark theme
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE the dark theme applies, the page SHALL draw its fields, its page background, its raised surfaces (header, left panel, cards, detail panel) and its hover surface on four distinct design-system tokens of strictly increasing luminance in that order, the graph's background being the page background.
- **Rationale**: in a dark theme, a plane brought forward is lighter; one surface for all makes the page read as a single dark mass.
- **Priority**: Must
- **Acceptance Criteria**: Given the tokens of the dark theme, When the luminance of `control-bg`, `page-bg`, `card-bg` and `table-row-hover` is computed, Then each is strictly greater than the previous one; And `graph-bg` equals `page-bg`; Given the light theme, Then none of its token values changed.
- **Dependencies**: RQ-TRC-018, ADR-TRC-002, ADR-TRC-017

---

## Non-Functional Requirements

### RQ-TRC-118: Contrast on every dark surface
- **Category**: Non-Functional
- **NFR Type**: Accessibility
- **EARS Type**: State-driven
- **Statement**: WHILE the dark theme applies, every text colour of the page (text, muted, subtle, accent, status) SHALL reach 4.5:1 and every mark colour (element types, the twelve identity tokens) and the field border SHALL reach 3:1, on each of the page, raised, hover and selected surfaces.
- **Metric**: WCAG 2.2 contrast ratio — 4.5:1 for text (SC 1.4.3), 3:1 for graphical objects and component boundaries (SC 1.4.11).
- **Measurement Method**: unit test computing the WCAG relative-luminance ratio of each pair from `tokens.json`.
- **Priority**: Must
- **Acceptance Criteria**: Given the tokens of the dark theme, When the contrast of each listed colour is computed on each of the four surfaces, Then no text is under 4.5:1 And no mark or field border is under 3:1.
- **Dependencies**: RQ-TRC-117, RQ-HST-014, ADR-TRC-017
