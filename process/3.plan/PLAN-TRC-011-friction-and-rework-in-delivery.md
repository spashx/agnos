# PLAN-TRC-011: Friction and Rework in the Delivery Tab

## Overview
Read the friction log from git, show its figure and the words on the variations, and draw friction and rework over the
points over time, behind two tags. Each step leaves the page and its tests working. Page tests need the network.

## References
- **Requirements**: RQ-TRC-090 to RQ-TRC-096; amended: RQ-TRC-074, RQ-TRC-076, RQ-TRC-083
- **ADRs**: ADR-TRC-011 (DEC-TRC-045 to DEC-TRC-049); ADR-TRC-002 (design system); extended: DEC-TRC-037, DEC-TRC-043

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-TRC-081: The friction specified and decided
- **Tier**: M
- **Status**: Done
- **Description**: Accept FTR-TRC-006 and ADR-TRC-011 after the owner's review, and mark the requirements and decisions
  they amend or extend with a note naming them.
- **Requirement refs**: RQ-TRC-090 to RQ-TRC-096
- **ADR refs**: ADR-TRC-011
- **Acceptance Criteria**: Given the documents, When `agnos-index` runs, Then RQ-TRC-090 to RQ-TRC-096 and DEC-TRC-045 to
  DEC-TRC-049 are listed with no duplicate; Given RQ-TRC-074, RQ-TRC-076, RQ-TRC-083, DEC-TRC-037, DEC-TRC-043, Then each
  names what changes it; Given the owner's approval, Then ADR-TRC-011 is Accepted.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `agnos-index`: 424 entries, exit 0, no duplicate; a note added to RQ-TRC-074, 076, 083, DEC-TRC-037, 043; owner approval of 2026-10-30, ADR-TRC-011 Accepted.
- **Assumptions**: None

### TASK-TRC-082: The log read from git into the delivery block
- **Tier**: L
- **Status**: Done
- **Description**: Read the log at HEAD with `git blame`, write `delivery.friction`, report the rows left out, and document
  the block in `SKILL.md`.
- **Requirement refs**: RQ-TRC-090, RQ-TRC-091
- **ADR refs**: ADR-TRC-011 (DEC-TRC-045)
- **Acceptance Criteria**: Given a test repository, Then each criterion of RQ-TRC-090 and RQ-TRC-091 holds in Gherkin-named
  tests; Given this repository, When generating with `--history`, Then 8 rows are read and exit 0.
- **Dependencies**: TASK-TRC-081
- **Assignee**: AI
- **Verification**: `test_friction.py`: 8 tests OK; full suite 335 tests OK, 3 skipped; this repository with `--history`: exit 0, 8 rows read.
- **Assumptions**: a row of a merge is named on the error stream; a malformed row is named even if outside the history read.

### TASK-TRC-083: The figure, its filters and the words
- **Tier**: M
- **Status**: Done
- **Description**: Add the friction figure and its tooltip, apply the filters of DEC-TRC-048, write "better" or "worse" on
  every variation, and fit the band to five figures.
- **Requirement refs**: RQ-TRC-092, RQ-TRC-093, RQ-TRC-094
- **ADR refs**: ADR-TRC-011 (DEC-TRC-046, DEC-TRC-047, DEC-TRC-048), ADR-TRC-002
- **Acceptance Criteria**: Given the fixture, Then each criterion of RQ-TRC-092, RQ-TRC-093 and RQ-TRC-094 holds in
  Gherkin-named page tests.
- **Dependencies**: TASK-TRC-082
- **Assignee**: AI
- **Verification**: `DeliveryFrictionTest`, RQ-TRC-092 to 094 tests OK within the full suite (335 tests OK, 3 skipped). Visual check left to the owner.
- **Assumptions**: a variation that cannot be computed reads "—" on every figure, replacing "no variation"; the words are in English like the page.

### TASK-TRC-084: The marks and the tags on the points over time
- **Tier**: L
- **Status**: Done
- **Description**: Add the two tokens through the design system, the circle and diamond series on a second axis with their
  tooltips and keyboard path, and the tags Rework and Friction; check the speed thresholds still hold.
- **Requirement refs**: RQ-TRC-095, RQ-TRC-096, RQ-TRC-085, RQ-TRC-087, RQ-TRC-088
- **ADR refs**: ADR-TRC-011 (DEC-TRC-049), ADR-TRC-002
- **Acceptance Criteria**: Given the fixture, Then each criterion of RQ-TRC-095 and RQ-TRC-096 holds in Gherkin-named page
  tests; Given `AGNOS_TRACE_PERF=1`, Then the thresholds of RQ-TRC-088 hold; Given the script, Then it holds no raw visual
  value for the marks.
- **Dependencies**: TASK-TRC-083
- **Assignee**: AI
- **Verification**: RQ-TRC-095, 096 tests OK within the full suite. `AGNOS_TRACE_PERF=1`: P95 66-77 ms against the former 50 ms limit, 64-73 ms on the previous commit; owner set the limit to 100 ms on 2026-10-31 (RQ-TRC-078, RQ-TRC-088); the fixture of the speed test holds no friction row. Visual check left to the owner.
- **Assumptions**: the marks reuse the History mark size; a tag keeps the chart's zoom; series order Rework then Friction, as in the tags.

### TASK-TRC-085: Corrections of the owner's review
- **Tier**: L
- **Status**: Done
- **Description**: Period A in violet, period B in teal and rework in blue, the better direction in each figure's tooltip, the friction's definition in its tooltip, the marks off by default, their icons in the tags as their only legend.
- **Requirement refs**: RQ-TRC-083, RQ-TRC-093, RQ-TRC-096
- **ADR refs**: ADR-TRC-011 (DEC-TRC-049), ADR-TRC-010 (DEC-TRC-043), ADR-TRC-002
- **Acceptance Criteria**: Given the tab, Then no mark is drawn until its tag is on; Given a tag, Then it shows its mark's icon; Given a points figure or a friction figure, Then its tooltip says which way is better.
- **Dependencies**: TASK-TRC-084
- **Assignee**: AI
- **Verification**: full suite: 336 tests OK, 3 skipped; `AGNOS_TRACE_PERF=1` alone, 5 runs: P95 66.3 to 121.2 ms, 2 runs over the 100 ms limit, cause not established at this commit. Owner's visual check: accepted on 2026-10-31.
- **Assumptions**: violet and teal are the pair farthest apart that avoids red, teal staying nearer the green of "better"; teal-700 added for white text on B in light theme; the title "Friction per session" is kept, the figure being an average per session within the period.
