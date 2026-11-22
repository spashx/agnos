# PLAN-TRC-017: What is Scanned and Excluded, Always Shown

## Overview
Make the default and user-given scan and exclusion lists visible in the help, on every run and in the skill's report
(owner request, 2026-11-07, after `--exclude "*.md"` silently dropped the default exclusions).

## References
- **Requirement refs**: RQ-TRC-119
- **ADR refs**: None (no architectural choice; DEC-TRC-001 unchanged)

---

## Tasks

### TASK-TRC-104: Scan and exclusion lists in help, run output and skill report
- **Tier**: M
- **Status**: Done
- **Description**: `--help` lists the default extensions and exclusions; each run prints the lists in effect, default or
  user, before the summary line; `SKILL.md` has them reported; `maintaining.md` stops copying the list.
- **Requirement refs**: RQ-TRC-119
- **ADR refs**: None
- **Acceptance Criteria**: see RQ-TRC-119 (help, default run, user run, SKILL.md Report).
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `ScanListsShownTest` (4 tests) written first, 4 failures, then OK; `test_perf_center` + `test_skill_name`
  in the repo: 65 OK. Full suite on a copy: 408 run, 0 failures, 1 error (`test_skill_name` needs `.git`, OK in the repo),
  3 skipped (perf budgets, need `AGNOS_PERF_CENTER_PERF=1`). `SKILL.md`: 46 lines (≤ 50, DEC-TRC-050).
- **Assumptions**: The scan lines go to stdout before the summary, which stays the last line, unchanged.

### TASK-TRC-105: The RQ-TRC-119 citation of maintaining.md in a comment
- **Tier**: S
- **Status**: Done
- **Description**: `references/maintaining.md` cited RQ-TRC-119 as plain text, failing `agnos-meta-demo`'s citation test
  (RQ-MTA-014); the citation becomes a comment.
- **Requirement refs**: RQ-TRC-119
- **ADR refs**: None
- **Acceptance Criteria**: Given `maintaining.md`, When the demo's citation test runs, Then no ID shows outside a comment.
- **Dependencies**: TASK-TRC-104
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: None
