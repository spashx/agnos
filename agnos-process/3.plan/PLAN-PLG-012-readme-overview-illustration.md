# PLAN-PLG-012: README overview illustration

## Overview
Replace the README's overview image by the proposal the owner chose (AC v2), keep the four SVG proposals as sources in
`assets/`, and keep those sources out of the marketplace.

## References
- **Requirements**: RQ-PLG-047
- **ADRs**: None

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-PLG-078: Replace README overview illustration
- **Tier**: M
- **Status**: Done
- **Description**: Store the SVG proposals A, C, AC v1 and AC v2 in `assets/`, convert AC v2 into `assets/agnos-overview.png`, and class `assets/*.svg` as Meta in agnos-meta-release's layers.
- **Requirement refs**: RQ-PLG-047
- **ADR refs**: None
- **Acceptance Criteria**: Given `README.md`, Then its image link leads to `assets/agnos-overview.png`, a 1536x1024 conversion of AC v2; Given `assets/agnos-overview-AC-v2.svg`, Then it parses as XML, And holds no `BKG` identifier other than the traceability example, And none of the removed claims; Given a rehearsal, Then the PNG is delivered and no `assets/*.svg` is, And the agnos-meta-release suite passes.
- **Dependencies**: None
- **Assignee**: Human, AI
- **Verification**: New test RQ_PLG_047 failed before the layer rule, passes after; agnos-meta-release suite 151 run, 151 OK, 0 skipped; 4 SVGs parse as XML, 0 removed claims, `BKG` only in the example; PNG 1536x1024 by headless Edge, checked visually by the owner; README link unchanged.
- **Assumptions**: AC v1 restored from the owner's copy; the SVGs' prototype header replaced by the RQ-PLG-047 comment.

### TASK-PLG-079: Prepare version 3.6.2 release
- **Tier**: S
- **Status**: Done
- **Description**: Record the version 3.6.2 the owner approved, with the changelog and user's guide docs-sync wrote, by agnos-meta-release-prep.
- **Requirement refs**: RQ-PLG-032
- **ADR refs**: None
- **Acceptance Criteria**: Given the approved diff, When the version is set, Then `VERSION.txt` holds 3.6.2 And the changelog's `[Unreleased]` is `[3.6.2]`.
- **Dependencies**: TASK-PLG-078
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: The owner chose 3.6.2 over the proposed 3.7.0.
