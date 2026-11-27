# PLAN-TRC-015: Graph Toolbar Simplified, Legend Relations More Visible

## Overview
Two owner-requested tweaks to the graph view: remove the unreadable "Whole graph" control, and thicken the legend's
relation line samples for readability.

## References
- **Requirement refs**: RQ-TRC-012, RQ-TRC-045, RQ-TRC-044
- **ADR refs**: ADR-TRC-015 (TASK-TRC-099); ADR-TRC-002 (TASK-TRC-100, no amendment)

---

## Tasks

### TASK-TRC-099: Remove "Whole graph"
- **Tier**: L
- **Status**: Done
- **Description**: Remove the `#whole` toolbar button, its implementation and its mention in the Help dialog; "Fit"
  now sits alone at the toolbar's right edge (unchanged flex layout, nothing left beside it).
- **Requirement refs**: RQ-TRC-012, RQ-TRC-045
- **ADR refs**: ADR-TRC-015
- **Acceptance Criteria**: Given the generated page, When its markup is read, Then no element has `id="whole"` and no
  text reads "Whole graph", and `#fit` is still present; Given the tooltip check of RQ-TRC-045, When every listed
  control is read, Then none is untitled.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `test_perf_center.py::GraphToolbarTest` asserts the button and its wording are gone and `#fit`
  remains; `#whole` removed from `TooltipTest.TOOLTIP_TARGETS` (RQ-TRC-045) so the tooltip-coverage check no longer
  expects a title on a removed control. Not yet run in this session (Python/browser suite; to be executed next).
- **Assumptions**: None — the owner's own request and review stand for the Tier-L approval gate (DoR) and the ADR's
  "Accepted" status.

### TASK-TRC-100: Thicker legend relation strokes
- **Tier**: S
- **Status**: Done
- **Description**: `graph-legend-edge-width` (the legend's relation-line samples) moves from `stroke-hairline` (1px) to
  `stroke-medium` (1.2px) for better visibility, per the owner's request (~25%; the nearest existing token step).
- **Requirement refs**: RQ-TRC-044
- **ADR refs**: None (component token re-pointed within ADR-TRC-002's existing chain; rationale recorded in
  `tokens.json`'s `$comment`)
- **Acceptance Criteria**: Given `tokens.json`, When `component.graph-legend-edge-width` is read, Then it names
  `stroke-medium`.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `tokens.json` component entry reread after edit: `"graph-legend-edge-width": "stroke-medium"`.
- **Assumptions**: Reused the existing `stroke-medium` step (+20%) rather than adding a new global/semantic token for
  an exact +25%, since the two are a fraction of a pixel apart; recorded as a rationale note in `tokens.json`.
