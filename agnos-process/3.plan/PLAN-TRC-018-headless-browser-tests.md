# PLAN-TRC-018: The Perf Center's Headless-Browser Tests Fail

## Overview
On 2026-11-07, during TASK-INI-006, the `agnos-perf-center` suite gave 408 tests run, failures=36, errors=168, 3 skipped. The failing
tests are those that render the page in a headless Chromium-family browser and read values back (`KeyError` on the values read,
`AttributeError` on a match of `None`). They fail alike on a clean worktree of HEAD 7791c9e (`test_brand.py`: failures=5, errors=14),
so the cause predates FTR-INI-002; TASK-INI-004 had recorded 361 run, OK, on 2026-10-31. The cause was not investigated.

## References
- **Requirements**: the requirements of the failing tests, among them RQ-TRC-089, RQ-TRC-101, RQ-TRC-109, RQ-TRC-111, RQ-TRC-113,
  RQ-TRC-114, RQ-TRC-116, RQ-HST-016
- **ADRs**: None (no architectural choice expected; to be reassessed once the cause is known)

---

## Tasks

### TASK-TRC-106: Find why the headless-browser tests read nothing, and fix it
- **Tier**: M
- **Status**: Not Started
- **Description**: Reproduce on one failing test of `test_brand.py`, find what the browser run returns (browser found by
  `find_browser()` of `test_perf_center.py`, its version, its output), fix the root cause in the tests' harness or in the page, then
  re-run the whole suite. Re-tier to L if the fix changes the page's public behaviour or a DEC.
- **Requirement refs**: RQ-TRC-089, RQ-TRC-101, RQ-TRC-109, RQ-TRC-111, RQ-TRC-113, RQ-TRC-114, RQ-TRC-116, RQ-HST-016
- **ADR refs**: None
- **Acceptance Criteria**: Given the cause, When it is stated, Then it is evidenced by a command's output; Given the fix, When the
  `agnos-perf-center` suite runs, Then it reports 0 failures and 0 errors, And each skipped test is listed with its reason; Given a
  failing test, Then it was not modified only to pass.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**:
- **Assumptions**:
