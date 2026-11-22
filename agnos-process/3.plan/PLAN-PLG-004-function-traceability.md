# PLAN-PLG-004: Function Traceability Counts, and is Asked for Plainly

## Overview
Make "Functions traced" weigh in the perf center's score and name functions in the Definition of Done (FTR-PLG-004), then rehearse
the release again for the next owner's checks. No push at any step (DEC-PLG-007).

## References
- **Requirement refs**: RQ-PLG-024, RQ-PLG-025, RQ-PLG-026, RQ-TRC-035 and RQ-TRC-059 (amended)
- **ADR refs**: ADR-PLG-004, ADR-TRC-008

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
- **Status**: Done
- **Description**: Add the DoD item of RQ-PLG-025 to the instructions file, tested on the skill the release generates.
- **Requirement refs**: RQ-PLG-025
- **ADR refs**: ADR-PLG-004 (DEC-PLG-020)
- **Acceptance Criteria**: Given RQ-PLG-025's criteria, Then they hold, tested first; Given the instructions file, Then its line count is reported.
- **Dependencies**: TASK-PLG-026
- **Assignee**: AI
- **Verification**: `DefinitionOfDoneTest` written first: 1 != 0 rows, then OK on `release.process_skill`'s output, the row ✓ for S, M and L. agnos-meta-release suite: 104 tests OK, 0 skipped. Instructions file: 386 lines (budget 400).
- **Assumptions**: the example DoD table of `AGNOS-GETTING-STARTED.md` is left to `agnos-meta-docs-sync`, planned after PLAN-PLG-004.

### TASK-PLG-029: The release rehearsed again, and proved
- **Tier**: M
- **Status**: Done
- **Description**: Rebuild the demo if its checks require it, rehearse HEAD into `C:\dev\repos\spashx\agnos-marketplace`, run `agnos-meta-plugin-proof`, and run the perf center again on `agnos-trial-copilot` to show the new score.
- **Requirement refs**: RQ-PLG-007, RQ-PLG-010, RQ-PLG-024
- **ADR refs**: ADR-PLG-002, ADR-PLG-004
- **Acceptance Criteria**: Given a rehearsal of the last commit, Then the exit is 0 and the lines to read are judged; Given the proof, Then every line it runs passes; Given `agnos-trial-copilot`, Then its score is below 10 with 3 untraced functions.
- **Dependencies**: TASK-PLG-027, TASK-PLG-028
- **Assignee**: AI
- **Verification**: Demo not rebuilt: agnos-meta-demo suite 12 OK, 0 skipped. Rehearsal of `f543199`: `exit=0, 55 files, 1199 IDs removed, 2 lines to read`, both false alarms (no ID: START SESSION's intro, a docstring of `perf_center.py`). Proof with `AGNOS_CLAUDE` (claude-code 2.1.318): exit 0, 8 lines pass. `agnos-marketplace` emptied with the owner's approval and regenerated: its 55 files identical by SHA256 to the proved copy. `agnos-trial-copilot` with `--call-graph`: `quality: B 8.7/10` (was A 10/10), `functions-traced 0.0` medium, 7 of its 9 findings. Discrepancy: 7 untraced functions, not 3 as the criterion said: the 3 functions of the code and the 4 tests, named `test_RQ_SLG_001_...`, an underscore form the perf center does not read as an ID.
- **Assumptions**: the proof ran on the scratchpad copy, then the marketplace was compared to it file by file instead of being proved again.

### TASK-PLG-030: A test's ID in its doc comment, not in its name
- **Tier**: L
- **Status**: Done
- **Description**: Write RQ-PLG-026 and DEC-PLG-021, then replace "and test case names" in MANDATORY TRACEABILITY by "those of test functions included", tested on the skill the release generates.
- **Requirement refs**: RQ-PLG-026
- **ADR refs**: ADR-PLG-004 (DEC-PLG-021)
- **Acceptance Criteria**: Given RQ-PLG-026's criteria, Then they hold, tested first; Given the instructions file, Then its line count is reported; Given the index, Then it has no duplicate.
- **Dependencies**: TASK-PLG-028
- **Assignee**: AI
- **Verification**: DEC-PLG-021 approved by the owner on 2026-11-05. `TestTraceabilityTest` written first: 2 failures ("those of test functions included" not found; "test case names" found), then OK. agnos-meta-release 106 OK (before and after commit `dd2eb22`), agnos-meta-demo 12 OK, agnos-init 25 OK, 0 skipped. Instructions file: 386 lines. `agnos-index` exit 0, 650 entries, no duplicate.
- **Assumptions**: None.

### TASK-PLG-031: The release rehearsed again with the new rule
- **Tier**: M
- **Status**: Done
- **Description**: Rehearse HEAD into an empty scratchpad folder, prove it, then empty `C:\dev\repos\spashx\agnos-marketplace` and regenerate it, compared file by file with the proved copy.
- **Requirement refs**: RQ-PLG-007, RQ-PLG-010, RQ-PLG-026
- **ADR refs**: ADR-PLG-002, ADR-PLG-004
- **Acceptance Criteria**: Given a rehearsal of the last commit, Then the exit is 0 and the lines to read are judged; Given the proof, Then every line passes; Given the marketplace, Then its files equal the proved copy's.
- **Dependencies**: TASK-PLG-030
- **Assignee**: AI
- **Verification**: Rehearsal of `b8445e9`: `exit=0, 55 files, 1201 IDs removed, 2 lines to read`, the same two false alarms as TASK-PLG-029. Proof with `AGNOS_CLAUDE`: exit 0, 8 lines pass. `agnos-marketplace` emptied and regenerated: 55 files, identical by SHA256 to the proved copy. Its `agnos-process/SKILL.md` holds "those of test functions included" (line 89) and the DoD item for functions (line 280).
- **Assumptions**: None.
