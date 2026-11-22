# PLAN-TRC-013: The Skill Named after its Role, agnos-perf-center

## Overview
Rename the skill, its script and its outputs, and align every live file, with a test guarding the result.

## References
- **Requirement refs**: RQ-TRC-104 to RQ-TRC-107; amended: RQ-TRC-001
- **ADR refs**: ADR-TRC-013 (DEC-TRC-053 to DEC-TRC-055)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-TRC-089: Rename agnos-trace to agnos-perf-center
- **Tier**: L
- **Status**: Done
- **Description**: Write the guarding test first, `git mv` the skill folders, script and test, replace the names in live files, rewrite the description, rebuild the demo and regenerate this repository's page.
- **Requirement refs**: RQ-TRC-104, RQ-TRC-105, RQ-TRC-106
- **ADR refs**: ADR-TRC-013 (DEC-TRC-053, DEC-TRC-054, DEC-TRC-055)
- **Acceptance Criteria**: Given the repository, When the skill's tests run, Then each criterion of RQ-TRC-104 to RQ-TRC-106 holds and the suites pass; Given a renamed `SKILL.md`, When `git log --follow` runs after the commit, Then it reaches the earlier history; Given the demo, When `agnos-meta-demo build -Verify` runs, Then every check passes.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `agnos-perf-center/tests`: 361 run, OK, 3 skipped, including `test_skill_name.py` (5), whose RQ-TRC-106 test failed on an injected former name. Not failing-first: its run before the rename was a malformed command. `agnos-meta-qa`: 0 open. `build -Verify`: 23 passed, 0 failed, HEAD 2b359a4. `SKILL.md`: 46 lines. `git log --follow` checked after the commit.
- **Assumptions**: `scripts/perf_center.py`, `tests/test_perf_center.py` and `PERF-CENTER.*` as names; `assets/matrix.*` and the Matrix tab stay; the RQ-TRC-026 hash re-pinned with the owner's approval, since only `meta.summary`'s prefix changes; the local page regenerated with `--sources . --call-graph --history`, as it had been, and the three former generated files removed.

### TASK-TRC-090: Duration on the generator's last output line
- **Tier**: M
- **Status**: Done
- **Description**: `perf_center.py` ends its stdout line with the elapsed time, kept out of the page and its data files; SKILL.md describes it.
- **Requirement refs**: RQ-TRC-107
- **ADR refs**: None
- **Acceptance Criteria**: Given a process folder and a source folder, When the generator runs, Then its last stdout line ends with ` written in <s>.<mmm> s`, And the page and `.json` hold no duration.
- **Dependencies**: TASK-TRC-089
- **Assignee**: AI
- **Verification**: `test_RQ_TRC_107_...` failed first (line ended with `page.html written`), then passed. `agnos-perf-center/tests`: 362 run, OK, 3 skipped. Real run on this repository: `... page.html written in 0.533 s`.
- **Assumptions**: The duration is appended to the existing last line, not a new line, because the existing summary test and callers read the last line; seconds with three decimals from `time.perf_counter`.
