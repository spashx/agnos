# FTR-QLT-001: A Code Quality Report Before the Pull Request
<!-- Amended on 2026-10-31: the skill, its script and its outputs carry their current names (RQ-TRC-104, RQ-TRC-105, DEC-TRC-055). -->

## Overview
The maintainer, or an agent told to, asks `agnos-meta-qa` for a report on the code of this repository. Its findings are corrected
before the commit or the push, rather than in the pull request. The report is written for whoever corrects them: an AI or a tool.
`agnos-perf-center`'s code is brought to a report with nothing left open.

Out of scope: hooks, blocking anything, correcting the code from the skill, a SonarQube Cloud project, the tests' own code.

## Stakeholders
- **Owner**: the repository owner (maintainer of AGNOS).
- **Consumers**: the maintainer; the agents working in this repository; any tool reading the report.

---

## Functional Requirements

### RQ-QLT-001: Called explicitly, blocking nothing
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: `agnos-meta-qa` SHALL run only when a human calls it or an instruction tells an agent to, and no hook, commit or push
  SHALL depend on it.
- **Rationale**: the owner wants a tool to call, with neither hook nor blocking.
- **Priority**: Must
- **Acceptance Criteria**: Given the repository, When its hook and workflow files are read, Then none calls the skill; Given the skill's
  description, Then it says it runs on an explicit request only.
- **Dependencies**: ADR-QLT-001

### RQ-QLT-002: A report for an AI or a tool
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN `check` completes, it SHALL write one JSON report with a versioned schema, each finding having the same fields
  whichever analyser found it: file, line, column, end line, end column, tool, rule, severity, message, fixable and exception; and it
  SHALL print a short summary naming the report's path.
- **Rationale**: a consumer can correct the findings without knowing each analyser's format.
- **Priority**: Must
- **Acceptance Criteria**: Given findings of the three analysers, When they are normalised, Then each has exactly these fields; Given a
  completed `check`, Then the report holds `schemaVersion`, its scope, its files and its counts, And the summary names its path.
- **Dependencies**: RQ-QLT-001

### RQ-QLT-003: What is analysed
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN `check` is called without an argument, it SHALL analyse the changed Python and JavaScript files, staged or not,
  untracked included; with `--all`, every such file not ignored by git; with paths, those files or the files of those folders. Except
  for a file named directly, it SHALL leave out the tests, fixtures, vendored files and the demo's content.
- **Rationale**: a report on what is about to be committed stays short, and the whole remains reachable.
- **Priority**: Must
- **Acceptance Criteria**: Given a change in a script, a test and a `.md` file, When `check` runs, Then only the script is analysed;
  Given `--all`, Then a clean tracked script is analysed; Given a fixture named directly, Then it is analysed.
- **Dependencies**: RQ-QLT-002

### RQ-QLT-004: Justified exceptions stay visible
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN a finding's line or the line above it holds the comment `agnos-qa-exception: <rule> <reason>` for its rule, the
  report SHALL keep the finding, marked with that reason, and SHALL count it apart from the open findings.
- **Rationale**: a consumer must not correct a decision again, and a reader must still see that it exists.
- **Priority**: Must
- **Acceptance Criteria**: Given such a comment, When the finding is reported, Then `exception` holds the reason, And it is not open; Given
  a comment without a reason or for another rule, Then the finding stays open.
- **Dependencies**: RQ-QLT-002

### RQ-QLT-005: The exit code tells whether the analysis ran
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: IF an analysis cannot complete, THEN `check` SHALL exit 1, name the cause and leave no report; findings alone SHALL
  exit 0.
- **Rationale**: findings block nothing, but a stale or partial report must not be read as a true one.
- **Priority**: Must
- **Acceptance Criteria**: Given findings, When `check` ends, Then it exits 0; Given a missing analyser and an old report, When it runs, Then
  it exits 1, names `setup`, And the old report is gone.
- **Dependencies**: RQ-QLT-002

### RQ-QLT-006: Pinned analysers, installed on request
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN `setup` is called, the skill SHALL install the exact analyser versions its assets record into `.agnos-qa/`, a folder
  git ignores; no other sub-command SHALL install anything.
- **Rationale**: the same code gives the same report on each machine, and nothing is installed by surprise.
- **Priority**: Must
- **Acceptance Criteria**: Given the assets, Then each analyser has an exact version; Given `.agnos-qa/`, Then git ignores it; Given a
  `check` without the analysers, Then nothing is installed.
- **Dependencies**: ADR-QLT-001

### RQ-QLT-007: The skill never changes the code
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: `agnos-meta-qa` SHALL write only inside `.agnos-qa/` or at the path given by `--out`.
- **Rationale**: correcting belongs to whoever reads the report, which keeps the skill simple and free of surprises.
- **Priority**: Must
- **Acceptance Criteria**: Given a repository with fixable findings, When `check` runs, Then `git status` shows nothing new.
- **Dependencies**: RQ-QLT-002

### RQ-QLT-008: A maintainer skill with its complement
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The skill SHALL be named with the prefix `agnos-meta-`, with its Claude Code pointer, and its procedure SHALL tell an agent
  in VS Code to read the editor's diagnostics of the changed files as a complement reported apart, since they depend on the editor.
- **Rationale**: the command line does not cover HTML and a few SonarQube rules, and the report must stay reproducible.
- **Priority**: Must
- **Acceptance Criteria**: Given both `SKILL.md` files, Then each has the prefixed name; Given the procedure, Then it states the complement,
  And that it stays out of the report.
- **Dependencies**: RQ-MTA-001, RQ-QLT-002

---

## Non-Functional Requirements

### RQ-QLT-009: agnos-perf-center's code has nothing left open
- **Category**: Non-Functional
- **NFR Type**: Maintainability
- **EARS Type**: Ubiquitous
- **Statement**: The report on the scripts and assets of `agnos-perf-center` SHALL hold no open finding, with no change of behaviour.
- **Metric**: 0 open findings; the suite of `agnos-perf-center` as passing as before (356 tests, 3 skipped).
- **Measurement Method**: `agnos-meta-qa check .github/skills/agnos-perf-center/scripts .github/skills/agnos-perf-center/assets`, and the skill's unit tests.
- **Priority**: Must
- **Acceptance Criteria**: Given the corrected code, When both run, Then the report's `open` count is 0, And the suite has no failure.
- **Dependencies**: RQ-QLT-002, RQ-QLT-004

### RQ-QLT-010: The page's skeleton answers its accessibility findings
- **Category**: Non-Functional
- **NFR Type**: Accessibility
- **EARS Type**: Ubiquitous
- **Statement**: Each SonarQube finding of `agnos-perf-center/assets/matrix.html` SHALL be corrected, or recorded as a justified decision in
  `PLAN-QLT-001`, with no visual change.
- **Metric**: 20 findings at the start, each one corrected or recorded.
- **Measurement Method**: VS Code's diagnostics of the file, and the skill's page tests.
- **Priority**: Should
- **Acceptance Criteria**: Given the file's diagnostics, When they are read, Then each one left is recorded with its reason, And the page tests pass.
- **Dependencies**: DEC-QLT-007
