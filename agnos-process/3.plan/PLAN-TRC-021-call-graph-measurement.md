# PLAN-TRC-021: Call graph measurement

## Overview
Make the call graph's weaknesses measurable before improving its resolution: score the files tree-sitter cannot parse, and
count the unresolved calls by cause (recommendations R1 and R2 of `insights/callgraph-operational-analysis.md`, owner choice of
2026-11-21).

## References
- **Requirement refs**: RQ-TRC-122, RQ-TRC-123, RQ-TRC-030, RQ-TRC-035, RQ-PLG-024
- **ADR refs**: ADR-TRC-020 (DEC-TRC-067, DEC-TRC-068), ADR-TRC-004 (DEC-TRC-015), ADR-TRC-008 (DEC-TRC-032)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-TRC-109: Specify call graph measurement
- **Tier**: M
- **Status**: Done
- **Description**: Write RQ-TRC-122 and RQ-TRC-123 in FTR-TRC-002, ADR-TRC-020 and this plan.
- **Requirement refs**: RQ-TRC-122, RQ-TRC-123
- **ADR refs**: ADR-TRC-020
- **Acceptance Criteria** (Gherkin): Given the owner's scope, When the artifacts are written, Then the index lists RQ-TRC-122,
  RQ-TRC-123, ADR-TRC-020, DEC-TRC-067, DEC-TRC-068 and TASK-TRC-109 to TASK-TRC-111 with no duplicate.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `build-index.ps1`: exit 0, 992 entries, 157 documents; the index lists RQ-TRC-122, RQ-TRC-123, ADR-TRC-020,
  DEC-TRC-067, DEC-TRC-068, TASK-TRC-109 to TASK-TRC-111; no duplicate reported.
- **Assumptions**: the causes `unnamed` and `top-level` stay outside the external total, as they were never counted there; the
  check's population is the files the call graph read, not every scanned file.

### TASK-TRC-110: Score files that fail to parse
- **Tier**: L
- **Status**: Done
- **Description**: Record `has_error` files in `callgraph.py`, add the `files-parsed` check to `scoring.json` and its population
  to `scorecard.py`, an "Unparsed files" figure to the page's call graph card, one broken fixture per language, documentation.
- **Requirement refs**: RQ-TRC-122, RQ-PLG-024
- **ADR refs**: ADR-TRC-020 (DEC-TRC-067), ADR-TRC-008 (DEC-TRC-032)
- **Acceptance Criteria** (Gherkin): the acceptance criteria of RQ-TRC-122; Given the skill's suite, Then all pass.
- **Dependencies**: TASK-TRC-109
- **Assignee**: AI
- **Verification**: tests first: `ParseFailureTest` and the `files-parsed` page test failed (`no attribute 'unparsed'`,
  `'unparsed 7' not found`). After: `test_callgraph test_scorecard test_languages` 117 run, OK, 1 skipped; full suite
  `python -m unittest discover -s tests` 418 run, OK, 3 skipped (opt-in performance tests, `AGNOS_PERF_CENTER_PERF=1`, not
  measured); `node --check assets/matrix.js` exit 0. Re-pinned on purpose: `counts` gains `parsed` 8, `unparsed` 0; ten checks
  with the call graph; RQ-TRC-038 amended by the owner (fixed 1,024 bytes; the fixture's call graph grew from 1,657 to 1,940 bytes).
- **Assumptions**: the broken sources are written by the test in a temporary folder, not committed as fixtures, so the
  repository's own QA and call graph read no syntax error; the check's label is "Parsed"; the card's hint reads "a syntax error
  in the file".

### TASK-TRC-111: Count unresolved calls by cause
- **Tier**: M
- **Status**: Done
- **Description**: Classify unresolved calls in `callgraph.py` into `library`, `constructor`, `cross-language`, `unnamed`,
  `top-level`, expose them in `callGraph.counts.unresolved`, show them in the "External calls" tooltip, documentation.
- **Requirement refs**: RQ-TRC-123, RQ-TRC-030
- **ADR refs**: ADR-TRC-020 (DEC-TRC-068), ADR-TRC-004 (DEC-TRC-015)
- **Acceptance Criteria** (Gherkin): the acceptance criteria of RQ-TRC-123; Given the skill's suite, Then all pass.
- **Dependencies**: TASK-TRC-109
- **Assignee**: AI
- **Verification**: tests first: the five RQ-TRC-123 tests and the counts test failed (`no attribute 'unresolved'`,
  `KeyError: 'unresolved'`, tooltip without the causes). After: `test_callgraph test_languages test_scorecard` 122 run, OK,
  1 skipped; full suite 423 run, OK, 3 skipped (opt-in performance tests, `AGNOS_PERF_CENTER_PERF=1`, not measured);
  `node --check assets/matrix.js` exit 0. Python fixture: library 1, constructor 1, external 2 unchanged; C/C++ fixture:
  library 2, unnamed 1. During the task, `callgraph.py` lost TASK-TRC-110's lines on disk (not by this agent); restored
  from commit 74a4976 with the owner's consent, the diff to HEAD re-read.
- **Assumptions**: a constructor is the last part of a scope declared in a scanned file of the caller's language; the
  causes are shown in the "External calls" tooltip, not in the summary line, which RQ-TRC-123 does not ask for.
