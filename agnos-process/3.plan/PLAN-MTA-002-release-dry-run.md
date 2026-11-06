# PLAN-MTA-002: The Release Rehearsal

## Overview
Correct the workshop's citations first, then build `agnos-meta-release --dry-run` in the order of its risks: select, remove, check, compare. Each step leaves its tests working.
Everything stays local on `feature/TRC`, nothing is published (DEC-MTA-004).

## References
- **Requirements**: RQ-MTA-006 to RQ-MTA-014
- **ADRs**: ADR-MTA-002 (DEC-MTA-007 to DEC-MTA-011); adjusted: DEC-MTA-002, DEC-MTA-004, DEC-MTA-006

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-MTA-004: The specification accepted
- **Tier**: M
- **Status**: Done
- **Description**: Accept FTR-MTA-002 and ADR-MTA-002 after the owner's review, and mark DEC-MTA-002, DEC-MTA-004 and DEC-MTA-006 with a note naming what adjusts them.
- **Requirement refs**: RQ-MTA-006 to RQ-MTA-014
- **ADR refs**: ADR-MTA-002
- **Acceptance Criteria**: Given the documents, When `agnos-index` runs, Then RQ-MTA-006 to RQ-MTA-014 and DEC-MTA-007 to DEC-MTA-011 are listed with no duplicate; Given the owner's approval, Then ADR-MTA-002 is Accepted.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `agnos-index`: 558 entries, exit 0, no duplicate; 9 of RQ-MTA-006 to RQ-MTA-014 and 5 of DEC-MTA-007 to DEC-MTA-011 listed; owner approval of 2026-10-31, ADR-MTA-002 Accepted; notes added to DEC-MTA-002, DEC-MTA-004, DEC-MTA-006.
- **Assumptions**: None

### TASK-MTA-009: The workshop's citations moved into comments
- **Tier**: M
- **Status**: Done
- **Description**: Move the IDs shown in Markdown outside `process/` and in scripts' help texts into comments, and make `agnos-meta-docs-sync` ask for the comment form. The IDs stay searchable.
- **Requirement refs**: RQ-MTA-014
- **ADR refs**: None
- **Acceptance Criteria**: Given the repository, Then each criterion of RQ-MTA-014 holds in a Gherkin-named test that failed before the change.
- **Dependencies**: TASK-MTA-004
- **Assignee**: AI
- **Verification**: `test_citations.py`: 4 tests failed before the change, the 5th failed on comments nested by the first pass of the move, then repaired; `agnos-meta-demo/tests` 12 OK; `agnos-meta-docs-sync` 14, `agnos-meta-qa` 32, `agnos-init` 15 OK; `agnos-perf-center` 364 run, OK, 3 skipped; demo `verify -SkipRebuild` 23 passed, 0 failed; no line of `CHANGELOG.md`'s released section changed.
- **Assumptions**: the tests live with `agnos-meta-demo`'s, beside those of RQ-MTA-001; the demo's own content under `assets/` and test files are out of the check; a sentence citing IDs inline was reworded where a comment alone would have broken it.

### TASK-MTA-005: Select the delivered files from a commit
- **Tier**: L
- **Status**: Done
- **Description**: Write the skill's script, `assets/layers.json`, the arguments and refusals, and the copy of the delivered files from HEAD; tests first.
- **Requirement refs**: RQ-MTA-006, RQ-MTA-007, RQ-MTA-008
- **ADR refs**: ADR-MTA-002 (DEC-MTA-007, DEC-MTA-008, DEC-MTA-011)
- **Acceptance Criteria**: Given a test repository and this one, Then each criterion of RQ-MTA-006, RQ-MTA-007 and RQ-MTA-008 holds in Gherkin-named tests.
- **Dependencies**: TASK-MTA-009
- **Assignee**: AI
- **Verification**: `test_select.py`: 11 OK, 10 failing against a stub before the code, the 11th added with its case. This repository at `7699553`: 58 delivered, 265 left out, every tracked file with a layer, exit 0, `git status` unchanged but for this task's files. No `--dry-run`: exit 1.
- **Assumptions**: the output holds each blob's committed bytes, so with its line endings as stored; the executable bit is kept; a folder that is no repository exits 1; the tests inject the proof instead of a command-line option, so that no flag can skip it.

### TASK-MTA-006: Remove the defined IDs and check the output
- **Tier**: L
- **Status**: Done
- **Description**: Write the removal rules and the check that reads the output, and the report's lines to read; tests first, including real forms taken from this repository.
- **Requirement refs**: RQ-MTA-009, RQ-MTA-010, RQ-MTA-012
- **ADR refs**: ADR-MTA-002 (DEC-MTA-009)
- **Acceptance Criteria**: Given the forms of the criteria, Then each criterion of RQ-MTA-009, RQ-MTA-010 and RQ-MTA-012 holds in Gherkin-named tests; Given this repository, When the rehearsal runs, Then no defined ID is left.
- **Dependencies**: TASK-MTA-005
- **Assignee**: AI
- **Verification**: Module tests failed before the code; the first rehearsal then showed cleaning rules altering text away from a removal (`.a .b` to `.a.b`, `: ../SKILL.md`), covered by 6 further tests that failed first, then fixed by anchoring every rule on the removal. `agnos-meta-release/tests`: 26 OK. This repository at `5ee2425`: 58 files, 1,096 IDs removed in 45 files, 0 problem, exit 0; every delivered Python and JSON file parses; 7 lines to read, 10 mentions, 0 ID outside a comment.
- **Assumptions**: a number followed by a lowercase word is a quantity, not an abbreviated ID; a comment left with only its labels goes whole; mentions cover meta skills and tests only, as a project has its own `process/` and settings; the 7 lines to read, 2 of them false alarms, are handed over in TASK-MTA-008.

### TASK-MTA-007: Prove the output on the demo
- **Tier**: L
- **Status**: Done
- **Description**: Add the parse of each delivered script and the comparison of what the workshop's and the output's skills write on the demo; tests first.
- **Requirement refs**: RQ-MTA-011
- **ADR refs**: ADR-MTA-002 (DEC-MTA-010)
- **Acceptance Criteria**: Given the demo, Then each criterion of RQ-MTA-011 holds in Gherkin-named tests; Given this repository, When the rehearsal runs, Then it exits 0.
- **Dependencies**: TASK-MTA-006
- **Assignee**: AI
- **Verification**: The proof first named one real difference: `agnos-perf-center` copied `delivery.json`'s `_comment`, with its IDs, into its data. By the owner's choice the generator no longer does; `test_delivery.py` amended to expect it, failing first; `agnos-perf-center/tests` OK, 3 skipped. A first run also showed the page of one run read as a source by the next, and a relative `--demo` failing, both fixed. Unit tests of the proof: 9 OK. Rehearsal on a throwaway clone holding this task's changes: 58 files, 1,097 IDs removed, `noIdLeft` and `sameBehaviour` true, exit 0, demo unchanged. The test on this repository reads HEAD, so it is re-run after this commit.
- **Assumptions**: the proof works in a temporary folder and clone, removed afterwards, which RQ-MTA-006's output rule does not count as a repository change; a language whose parser is absent is said on the error stream and not checked; `--call-graph` and `--history` are both used, to exercise the query files and the history reader.

### TASK-MTA-008: The skill packaged and said
- **Tier**: M
- **Status**: Done
- **Description**: Write `SKILL.md` and its pointer with `skill-creator`'s practices, name the skill in `CHANGELOG.md`, and hand the report's lines to read to the owner.
- **Requirement refs**: RQ-MTA-013, RQ-MTA-012
- **ADR refs**: ADR-MTA-002 (DEC-MTA-007)
- **Acceptance Criteria**: Given the skill, Then the criterion of RQ-MTA-013 holds; Given the rehearsal on this repository, Then the owner has its report.
- **Dependencies**: TASK-MTA-007
- **Assignee**: AI
- **Verification**: `test_skill.py`: 4 OK, failing before the files. `agnos-meta-release/tests` 40 OK; `agnos-meta-demo` 12, `agnos-meta-docs-sync` 14 OK; `agnos-perf-center/tests` OK, 3 skipped. Rehearsal on a throwaway clone of this task's files: 58 files, 1,102 IDs removed, both checks true, exit 0; 11 mentions and 2 lines to read, both false alarms, handed to the owner.
- **Assumptions**: 5 lines the removal left reading badly were reworded in the repository, in comments and docstrings only, moving their citations into parentheses; the skill is added to `test_meta_prefix.py`'s names; `CONTRIBUTING.md` and `AGENTS.md` stay unchanged, as a maintainer skill is not listed there.
