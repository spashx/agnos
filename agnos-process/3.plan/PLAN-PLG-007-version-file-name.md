# PLAN-PLG-007: The Version File is `VERSION.txt`

## Overview
Rename the version file `VERSION` to `VERSION.txt` everywhere AGNOS names it, per DEC-PLG-032.

## References
- **Requirements**: RQ-PLG-032, RQ-PLG-033, RQ-PLG-036
- **ADRs**: ADR-PLG-007 (DEC-PLG-032), ADR-PLG-005 (DEC-PLG-025, DEC-PLG-026), ADR-PLG-006

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-PLG-051: Rename `VERSION` to `VERSION.txt`
- **Tier**: L
- **Status**: Done
- **Description**: Amend RQ-PLG-032, RQ-PLG-033, DEC-PLG-025, DEC-PLG-026 on the name; set `layout.json`'s `version` to `VERSION.txt` and regenerate the copies; rename the template; update the scripts, tests and documents citing the name. Tests first.
- **Requirement refs**: RQ-PLG-032, RQ-PLG-033, RQ-PLG-036
- **ADR refs**: ADR-PLG-007 (DEC-PLG-032)
- **Acceptance Criteria**: Given the repository, Then `templates/VERSION.txt` holds one SemVer line And no `templates/VERSION` exists; Given a rehearsal, Then the manifests take their version from `VERSION.txt`; Given `agnos-init` on a project, Then `agnos-process/VERSION.txt` is `created`; Given `layout.py --check`, Then 0 findings; Given a grep of the bare name `VERSION` as a file name in live files, Then only history (changelog, Done tasks, superseded text) cites it.
- **Dependencies**: TASK-PLG-050
- **Assignee**: AI
- **Verification**: `layout.py --write` then `--check`: 0 findings; copies hold `VERSION = 'VERSION.txt'`; template renamed by `git mv`. Suites in place: release-prep 25 OK, init 32 OK, perf-center 399 run, 396 OK, 3 skipped (performance tests, `AGNOS_PERF_CENTER_PERF=1` unset); release 133 run, 131 OK, `test_proof` DemoTest and `test_determinism` ThisRepositoryTest fail because they rehearse HEAD, which still holds `VERSION`: re-run after the commit. Bare `VERSION` left only in history (Done tasks, amended ADR text, changelog) and unrelated names (`<VERSION>` placeholder, a test constant). RQ-TRC-109 and RQ-TRC-110 also renamed in their text.
- **Assumptions**: The demo is rebuilt later with `agnos-meta-demo`, not in this task.
