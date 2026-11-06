# PLAN-HST-004: Handles on the Overview Window of the History

## Overview
Give the History's overview window a handle at each end, as the Delivery slider has. Page tests need the network.

## References
- **Requirements**: RQ-HST-027 to RQ-HST-029
- **ADRs**: ADR-HST-002 (DEC-HST-012); ADR-TRC-002 (design system)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-HST-021: Handles, body drag and keyboard on the overview strip
- **Tier**: M
- **Status**: Done
- **Description**: Accept ADR-HST-002; add the tokens and the two handles to the strip, the drag of each handle, the drag
  of the window's body without a jump, and the keyboard path; document them in `SKILL.md`.
- **Requirement refs**: RQ-HST-027, RQ-HST-028, RQ-HST-029
- **ADR refs**: ADR-HST-002 (DEC-HST-012), ADR-TRC-002
- **Acceptance Criteria**: Given the fixture, Then each criterion of RQ-HST-027, RQ-HST-028 and RQ-HST-029 holds in
  Gherkin-named page tests; Given `AGNOS_TRACE_PERF=1`, Then the History thresholds of RQ-HST-013 hold.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `OverviewHandlesTest` OK within the full suite with `AGNOS_TRACE_PERF=1`: 343 tests OK; RQ-HST-013: tab drawn in 36 ms, P95 12.0 ms. Owner's visual check: accepted on 2026-10-31.
- **Assumptions**: the arrow step is the timeline's pan fraction of the period in view; a tooltip on each handle gives its date; handles styled after the Delivery slider at the owner's review.
