# PLAN-PLG-004: Function Traceability Counts, and is Asked for Plainly

## Overview
Make "Functions traced" weigh in the perf center's score and name functions in the Definition of Done (FTR-PLG-004), then rehearse
the release again for the next owner's checks. No push at any step (DEC-PLG-007).

## References
- **Requirements**: RQ-PLG-024, RQ-PLG-025, RQ-TRC-035 and RQ-TRC-059 (amended)
- **ADRs**: ADR-PLG-004, ADR-TRC-008

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-PLG-026: Feature, decisions and plan
- **Tier**: L
- **Status**: Done
- **Description**: Write FTR-PLG-004, ADR-PLG-004 and this plan, and mark the requirements and the decision they amend.
- **Requirement refs**: RQ-PLG-024, RQ-PLG-025
- **ADR refs**: ADR-PLG-004
- **Acceptance Criteria**: Given the owner's approval, Then ADR-PLG-004 is Accepted, And RQ-TRC-035, RQ-TRC-059 and DEC-TRC-032 name their amendment; Given the index, Then it has no duplicate.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: ADR-PLG-004 Accepted, owner's "oui" of 2026-11-05; RQ-TRC-035 and RQ-TRC-059 hold "Amended by: RQ-PLG-024", DEC-TRC-032 "Amended by DEC-PLG-019"; `agnos-index` exit 0, no duplicate. No test: documents only.
- **Assumptions**: the weight medium and the DoD line were the owner's choices; the perf center before each commit and a test with a chosen model were not chosen.

### TASK-PLG-027: "Functions traced" weighs medium
- **Tier**: M
- **Status**: Done
- **Description**: Set the check's risk to medium in `scoring.json`, let the page read the risk from the data, update `rules.md`, and the perf center's tests that expected informational.
- **Requirement refs**: RQ-PLG-024, RQ-TRC-035, RQ-TRC-059
- **ADR refs**: ADR-PLG-004 (DEC-PLG-019), ADR-TRC-008 (DEC-TRC-032)
- **Acceptance Criteria**: Given RQ-PLG-024's criteria, Then they hold, tested first; Given the perf center's full suite, Then it passes, the skipped tests stated with why.
- **Dependencies**: TASK-PLG-026
- **Assignee**: AI
- **Verification**: 3 tests written first, failing (`informational` != `medium`; score 6.5 not below 6.5; page hint), then OK. Fixture with call graph: `functions-traced 3.6`, risk medium, `quality: C 6.3/10`, `findings 26` in the summary, functions' findings included. Without call graph the check stays absent (`test_RQ_TRC_058_given_no_call_graph...` OK). The page's hint reads `citing no ID · ${risk}` from the data. Full suite: 367 tests OK, 3 skipped (the measurements gated by `AGNOS_PERF_CENTER_PERF`). No "informational" left about functions outside `process/`.
- **Assumptions**: the generic `informational` level and its filters stay in `scoring.json`, `scorecard.py` and `matrix.js`: no check uses it now, but removing it was not asked. My own new test first expected `findings: N`; the summary writes `findings N;`, the test was corrected to the real format.

### TASK-PLG-028: The DoD line for functions
- **Tier**: M
- **Status**: Not Started
- **Description**: Add the DoD item of RQ-PLG-025 to the instructions file, tested on the skill the release generates.
- **Requirement refs**: RQ-PLG-025
- **ADR refs**: ADR-PLG-004 (DEC-PLG-020)
- **Acceptance Criteria**: Given RQ-PLG-025's criteria, Then they hold, tested first; Given the instructions file, Then its line count is reported.
- **Dependencies**: TASK-PLG-026
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-PLG-029: The release rehearsed again, and proved
- **Tier**: M
- **Status**: Not Started
- **Description**: Rebuild the demo if its checks require it, rehearse HEAD into `C:\dev\repos\spashx\agnos-marketplace`, run `agnos-meta-plugin-proof`, and run the perf center again on `agnos-trial-copilot` to show the new score.
- **Requirement refs**: RQ-PLG-007, RQ-PLG-010, RQ-PLG-024
- **ADR refs**: ADR-PLG-002, ADR-PLG-004
- **Acceptance Criteria**: Given a rehearsal of the last commit, Then the exit is 0 and the lines to read are judged; Given the proof, Then every line it runs passes; Given `agnos-trial-copilot`, Then its score is below 10 with 3 untraced functions.
- **Dependencies**: TASK-PLG-027, TASK-PLG-028
- **Assignee**: AI
- **Verification**:
- **Assumptions**:
