# PLAN-RSI-001: Recursive self-improvement as a skill

<!-- PLAN-RSI-001: RQ-RSI-001 to RQ-RSI-004 / ADR-RSI-001 -->

## Overview
Implements FTR-RSI-001: the `agnos-self-improvement` skill, its budget script, and the reduction of
the RECURSIVE SELF-IMPROVEMENT SESSIONS section of the instructions file.

## References
- **Requirement refs**: RQ-RSI-001, RQ-RSI-002, RQ-RSI-003, RQ-RSI-004
- **ADR refs**: ADR-RSI-001 (DEC-RSI-001, DEC-RSI-002, DEC-RSI-003)

---

## Tasks

### TASK-RSI-001: Feature, ADR and plan
- **Tier**: M
- **Status**: Done
- **Description**: Write FTR-RSI-001, ADR-RSI-001 and this plan, then rebuild the index.
- **Requirement refs**: RQ-RSI-001, RQ-RSI-002, RQ-RSI-003, RQ-RSI-004
- **ADR refs**: ADR-RSI-001
- **Acceptance Criteria** (Gherkin):
  - **Given** the three documents
  - **When** `agnos-index` runs
  - **Then** it exits 0 and indexes FTR-RSI-001, RQ-RSI-001 to 004, ADR-RSI-001, DEC-RSI-001 to 003,
    PLAN-RSI-001 and TASK-RSI-001 to 005
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `build-index.ps1`: 762 entries, 110 documents, exit 0; FTR-RSI-001, RQ-RSI-001
  to 004, ADR-RSI-001, DEC-RSI-001 to 003, PLAN-RSI-001, TASK-RSI-001 to 005 indexed, no duplicate.
- **Assumptions**: The line-budget sentence of the instructions file carries the marker RQ-PLG-019,
  which is about the process naming itself, not the budget: the ceiling is read from the sentence,
  not from a marker. The ceiling override in a declaration is written `at most <N> lines`. No unit
  test: documents only.

### TASK-RSI-002: Budget script and its tests
- **Tier**: L
- **Status**: Done
- **Description**: Write `scripts/budget.ps1` and `scripts/budget.sh` (target resolution, ceiling,
  budget) and their unit tests, tests first. First written in Python, rewritten as shell scripts on
  the owner's decision (RQ-RSI-004 amended).
- **Requirement refs**: RQ-RSI-002, RQ-RSI-003, RQ-RSI-004
- **ADR refs**: ADR-RSI-001 (DEC-RSI-002, DEC-RSI-003)
- **Acceptance Criteria** (Gherkin): those of RQ-RSI-002, RQ-RSI-003 and RQ-RSI-004, one test each
- **Dependencies**: TASK-RSI-001
- **Assignee**: AI
- **Verification**: before the scripts: 9 tests, FAILED (failures=9). After: `unittest discover`
  Ran 9 tests, OK, 0 skipped, each case running both scripts with identical output. `budget.ps1` and
  `budget.sh` on this repository: exit 1, same "no declaration" message (expected until TASK-RSI-004).
- **Assumptions**: CLAUDE.md is read before AGENTS.md, the first declaration wins. "Outside the
  project" is checked on the path's text (absolute, or `..` above the root), symbolic links not
  followed: the target may not exist yet. bash counts lines with `awk`, as PowerShell counts a last
  line without line ending. Files read as UTF-8. `.gitattributes` keeps `budget.sh` LF.

### TASK-RSI-003: The skill's entry points
- **Tier**: M
- **Status**: Done
- **Description**: Write `.github/skills/agnos-self-improvement/SKILL.md`, following the skill
  authoring practices, and its `.claude/skills/` pointer.
- **Requirement refs**: RQ-RSI-001
- **ADR refs**: ADR-RSI-001 (DEC-RSI-001)
- **Acceptance Criteria** (Gherkin): those of RQ-RSI-001 on the skill
- **Dependencies**: TASK-RSI-002
- **Assignee**: AI
- **Verification**: SKILL.md re-read: steps 2 (budget across the effort), 3 (one theme at a time),
  4 (structure kept, any rule revisable), 5 (conflict check), 7 (`Iteration` trailer); both `.github`
  and `.claude` entry points exist; Claude Code lists `agnos-self-improvement` among its skills.
- **Assumptions**: No unit test: documentation only. Exit code 2 stops the iteration rather than
  the effort: the next iteration compresses first.

### TASK-RSI-004: Instructions file and entry points
- **Tier**: L
- **Status**: Done
- **Description**: Reduce the RECURSIVE SELF-IMPROVEMENT SESSIONS section and END SESSION step 3; add
  the improvement-target declaration and the skill to this repository's `CLAUDE.md` and `AGENTS.md`.
- **Requirement refs**: RQ-RSI-001, RQ-RSI-002
- **ADR refs**: ADR-RSI-001 (DEC-RSI-001, DEC-RSI-002)
- **Acceptance Criteria** (Gherkin): those of RQ-RSI-001 on the instructions file; the script resolves
  this repository's target to the instructions file; `agnos-init` tests pass unchanged; post-edit line
  count reported
- **Dependencies**: TASK-RSI-003
- **Assignee**: AI
- **Verification**: instructions file 380 lines (was 386, ceiling 400). `budget.ps1` and `budget.sh`
  on this repository: `target=.github/instructions/agnos-sw-eng.instructions.md ceiling=400 lines=380
  left=20`, exit 0. Full suite on a copy: agnos-init 32 OK; agnos-meta-release 133 OK, 2 skipped (demo
  not built); agnos-self-improvement 9 OK; agnos-meta-docs-sync 18, -plugin-proof 16, -qa 32,
  -release-prep 25 OK; agnos-perf-center 408 OK, 3 skipped (1 named: perf test needs
  AGNOS_PERF_CENTER_PERF=1). agnos-meta-demo: 1 failure from 048ad30 (RQ-TRC-119 outside a comment in
  agnos-perf-center/references/maintaining.md), not in this task's files; the demo's sample service
  tests not importable by this discovery command (`roombook`). agnos-index tests are .ps1/.sh, not run:
  its scripts are unchanged.
- **Assumptions**: The declaration is written once, in `AGENTS.md`, which `CLAUDE.md` imports.
  `agnos-meta-release`'s `test_process_text.py` (RQ-PLG-018) changed to the amended behaviour
  (RQ-RSI-001, RQ-RSI-002): the section names the skill, the target and the plugin rule, END SESSION
  names the skill, instead of "AGNOS block" and "improvement target".

### TASK-RSI-005: Changelog entry
- **Tier**: S
- **Status**: Done
- **Description**: Add the new skill and the amended target rule to `CHANGELOG.md`.
- **Requirement refs**: RQ-RSI-001, RQ-RSI-002
- **ADR refs**: ADR-RSI-001
- **Acceptance Criteria** (Gherkin): Given `CHANGELOG.md`, When its unreleased entries are read, Then
  they name the skill and the removed fallback
- **Dependencies**: TASK-RSI-004
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: None

### TASK-RSI-006: Documents synced for the release
- **Tier**: M
- **Status**: Done
- **Description**: Run `agnos-meta-docs-sync` (CHANGELOG, guide) and add the skill to README and CONTRIBUTING; move the
  citation of the skill's `SKILL.md` into a comment.
- **Requirement refs**: RQ-RSI-001
- **ADR refs**: ADR-RSI-001
- **Acceptance Criteria** (Gherkin): Given the documents, When they are compared with the skills, Then each names
  `agnos-self-improvement`, And the demo's citation test (RQ-MTA-014) passes
- **Dependencies**: TASK-RSI-005
- **Assignee**: AI
- **Verification**: docs-sync edited CHANGELOG.md (missing TRC/PLG entries) and the guide (stage 9, skill row); AGENTS.md
  and CLAUDE.md already complete. `agnos-meta-demo` tests: OK; `agnos-self-improvement` tests: OK. Demo `build -Verify`:
  23 passed, 0 failed.
- **Assumptions**: Older Unreleased bullets naming `process/` or `agnos-process` (the skill) are left: they record steps
  that line "The process folder is `agnos-process/`" supersedes. `METRICS_LOG.md`, the owner's change, is in this commit
  at the owner's request.
