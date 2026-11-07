# PLAN-TRC-016: Dark Theme in Layers

## Overview
Lighten the dark theme into four surfaces of increasing lightness and adjust the colours that would lose contrast, as the
owner retained from the mock-up of 2026-11-07 (candidate "P2", fragile colours adjusted).

## References
- **Requirements**: RQ-TRC-117, RQ-TRC-118
- **ADRs**: ADR-TRC-017 (DEC-TRC-063, DEC-TRC-064), ADR-TRC-002

---

## Tasks

### TASK-TRC-103: Dark surfaces in layers and dark variants of the fragile colours
- **Tier**: L
- **Status**: Done
- **Description**: Add the dark surface and colour tokens of DEC-TRC-063 and DEC-TRC-064 to `tokens.json` and point the
  dark side of the semantic tokens at them; a test checks layering and contrast from the tokens.
- **Requirement refs**: RQ-TRC-117, RQ-TRC-118
- **ADR refs**: ADR-TRC-017, ADR-TRC-002
- **Acceptance Criteria**: Given the dark tokens, When the surfaces are compared, Then fields < page < raised < hover in
  luminance And the graph background is the page; Given each colour and dark surface, Then text ≥ 4.5:1 and marks and field
  border ≥ 3:1; Given the light theme, Then no value changed; Given the existing contrast tests, Then they pass unmodified.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `test_dark_theme.py` written first, red on the old tokens (2 failures), then 3/3 OK (layers, light
  unchanged, contrast on 4 dark surfaces). First token pass left identities 5/7/12, `border-strong`, `text-subtle` under
  threshold on hover/selected: one targeted fix applied. `test_history_page.ContrastTest` (RQ-HST-014) then failed on its
  "one value for both themes" assumption; adapted, with the owner's approval, to read each theme's identity (DEC-TRC-064).
  Full suite on a copy: 404 run, 0 failures, 1 error (`test_skill_name` needs `.git`; re-run in the repo: OK), 3 skipped
  (perf budgets, need `AGNOS_PERF_CENTER_PERF=1`). Demo page regenerated; owner checked the render: OK.
- **Assumptions**: Variants tuned by hand from the mock-up; `color.blue-900` corrected to Tailwind's `#1E3A8A`; seven
  identities (not four) needed dark variants to hold 3:1 on hover and selected rows.
