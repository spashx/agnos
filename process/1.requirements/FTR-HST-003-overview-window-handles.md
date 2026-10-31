# FTR-HST-003: Handles on the Overview Window of the History

## Overview
The History timeline has an overview strip whose window can only be moved (RQ-HST-007); changing the period in view takes
the wheel or the keyboard over the timeline. The Delivery chart "Points over time" has a slider with a handle at each end
(RQ-TRC-083). This feature gives the History's window the same handles, so that both tabs are handled alike (owner
decision of 2026-10-31).

Unchanged: the timeline stays the page's own inline SVG (DEC-HST-005), its wheel, drag and keyboard zoom, the activity
band and the figures, which already follow the period in view.
Out of scope: moving the History timeline or its strip to the charting library.

## Stakeholders
- **Owner**: the repository owner.
- **Consumers**: readers of the History tab.

---

## Functional Requirements

### RQ-HST-027: A window resized by its handles
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the user drags a handle at either end of the overview window, the page SHALL move that end of the
  period in view, the other end staying in place, and SHALL redraw at once the timeline, the axis, the activity band and
  the figures; the handles SHALL not cross, and the window SHALL keep the shortest period the timeline's zoom allows.
- **Rationale**: choosing a period directly on the whole history is quicker than zooming then panning, and matches the
  slider of the Delivery tab.
- **Priority**: Must
- **Acceptance Criteria**: Given a window from day 10 to day 20, When its left handle is dragged to day 5, Then the
  period in view is day 5 to day 20 and the figures count it; When its right handle is dragged before its left one, Then
  the window stops at the shortest period.
- **Dependencies**: RQ-HST-007, RQ-HST-008, RQ-HST-013

### RQ-HST-028: A window moved without jumping
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the user drags the body of the overview window, the page SHALL move the period in view by the
  distance dragged, keeping its length; WHEN the user presses the strip outside the window, the page SHALL centre the
  window there, as it does today.
- **Rationale**: a window that jumps to the pointer when grabbed off-centre loses the reader's place.
- **Priority**: Must
- **Acceptance Criteria**: Given a window from day 10 to day 20, When its body is dragged by 5 days from near its left
  end, Then the period in view is day 15 to day 25; When the strip is pressed at day 50, Then the window is centred on
  day 50.
- **Dependencies**: RQ-HST-007

### RQ-HST-029: Handles for every reader
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: Each handle SHALL be reached with Tab and named with the date it stands on, and WHEN a focused handle
  receives the left or right arrow key, the page SHALL move that end of the period by the timeline's pan step; the handles
  SHALL consume design-system tokens only and SHALL raise a tooltip giving their date (RQ-HST-016).
- **Rationale**: the page's charts can all be used from the keyboard (RQ-TRC-087).
- **Priority**: Must
- **Acceptance Criteria**: Given the left handle focused, When the right arrow is pressed, Then the period in view starts
  later and the handle's accessible name gives the new date; Given the script and the style, Then they hold no raw visual
  value for the handles.
- **Dependencies**: RQ-HST-016, RQ-HST-027, RQ-TRC-087, ADR-TRC-002
