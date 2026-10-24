# PLAN-HST-001: Contribution History

## Overview
Implement RQ-HST-001 to RQ-HST-015 after ADR-HST-001, in six steps that each leave the generator, the page and their
tests working: the history module first (identities, then line tracking), then the generator's options and data, the
History tab and its timeline, the figures and filters, the entry points of the sidebar and the detail panel, and last
the speed, the accessibility and the documentation. Unit tests build small git repositories in a temporary folder.

## References
- **Requirements**: RQ-HST-001 to RQ-HST-015; RQ-TRC-018, RQ-TRC-021, RQ-TRC-026, RQ-TRC-067 (design system, standard
  library, sentinel, literals)
- **ADRs**: ADR-HST-001 (DEC-HST-001 to DEC-HST-006); ADR-TRC-002 (design system), ADR-TRC-004 (opt-in loading)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-HST-001: Identities and agents from git
- **Tier**: M
- **Status**: Done
- **Description**: Start `scripts/history.py` with the checks of the repository (git, working tree, first commit,
  shallow) and the reading of authors and `Co-Authored-By` co-authors through `.mailmap`, their merging by e-mail into
  identities, and their classing as human or agent from the patterns of a new `assets/agents.json`.
- **Requirement refs**: RQ-HST-004, RQ-HST-005, RQ-HST-012, RQ-HST-015
- **ADR refs**: ADR-HST-001 (DEC-HST-001, DEC-HST-003)
- **Acceptance Criteria**: Given commits by "spashx <x@u>" and "x@u <X@U>", Then they are one identity "spashx" merged
  by e-mail; Given a merge committed by "GitHub", Then "GitHub" is no identity; Given a `.mailmap` entry, Then the mapped
  commits are one identity merged by mailmap; Given a "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" trailer,
  Then Claude Opus 5.5 is an agent co-author and the commit is "together"; Given a folder outside git, or a repository
  with no commit, Then the check reports the cause; Given a shallow clone, Then it is reported shallow; Given the module,
  Then it imports only the standard library.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `python -m unittest discover -s tests` (skill folder): 178 tests, 0 failure, 1 skipped. `test_history.py` (17 tests, temporary repositories with an empty global git config): two names of one e-mail are one identity `spashx` merged by `email`; a merge committed by `GitHub` gives no identity; a `.mailmap` entry merges by `mailmap`; a name tie is stable; `Co-Authored-By: Claude Opus 5.5` makes an agent co-author and a `together` commit, a lower-case trailer too; `dependabot[bot]` is an agent commit; other patterns class with no code change; Claude Opus 5.5 and Claude Sonnet 5.5 sharing `noreply@anthropic.com` are two identities; outside git, no commit, no git command each give their cause; a `--depth 1` clone is shallow; `history.py` imports the standard library only. `test_literals.py` now covers `history.py`: 0 repeated literal. On this repository: 101 non-merge commits, spashx (human, 101, merged by email), Claude Opus 5.5 (agent, 50), Claude Sonnet 5.5 (agent, 35); 85 commits together, 16 human.
- **Assumptions**: An agent identity is its name and e-mail, not its e-mail alone: the run on this repository merged Claude Opus 5.5 and Claude Sonnet 5.5, which share `noreply@anthropic.com`; RQ-HST-004 and DEC-HST-003 amended accordingly. The no-reply addresses of `agents.json` are the vendors' no-reply ones only (`noreply@anthropic.com`, not `@anthropic.com`), so that a vendor's employees stay humans. Merge commits give no identity at all, not only no intervention.

### TASK-HST-002: Line ranges tracked back through the history
- **Tier**: L
- **Status**: Not Started
- **Description**: In `history.py`, map the ranges of the working tree to the last commit, read one `git log -p -U0 -M
  -m --parents --topo-order` over the scanned folders within `--since` and `--max-count`, track every range back through
  the commits and their parents (renames and merges included), and credit each non-merge commit whose hunks overlap a
  range, with its changed lines.
- **Requirement refs**: RQ-HST-001, RQ-HST-002, RQ-HST-003
- **ADR refs**: ADR-HST-001 (DEC-HST-002)
- **Acceptance Criteria**: Given RQ-A on lines 5 to 10 and RQ-B on 12 to 20 and a commit by Alice changing line 7, Then
  Alice has one intervention on RQ-A and none on RQ-B; Given 3 lines inserted above RQ-A later, Then it stays on RQ-A;
  Given the file renamed, Then it is kept; Given a side branch merged, Then the branch's commits are credited and the
  merge is not; Given an uncommitted change, Then it credits no one; Given functions `f` and `g` and a commit changing
  `g`, Then it is credited to `g` and to the file, not to `f`; Given a depth of 10 or a since date, Then only those
  commits are read; Given the same repository twice, Then the result is equal.
- **Dependencies**: TASK-HST-001
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-HST-003: Generator options, `history` data and summary line
- **Tier**: M
- **Status**: Not Started
- **Description**: Add `--history`, `--history-since` and `--history-depth` to `trace_matrix.py`, load `history.py`
  only with `--history`, write the `history` block of DEC-HST-004 and the summary line part, warn and go on without
  history when the repository cannot be read, and document the options and keys in `SKILL.md`.
- **Requirement refs**: RQ-HST-001, RQ-HST-006, RQ-HST-012, RQ-HST-015
- **ADR refs**: ADR-HST-001 (DEC-HST-001, DEC-HST-004)
- **Acceptance Criteria**: Given `--history-depth 5` without `--history`, Then the exit code is 1 and the message names
  `--history`; Given `--history-depth 0`, Then the exit code is 1; Given a run with `--history`, Then the data file holds
  `history` with limits, people, commits and interventions, and the summary line ends with the history counts; Given two
  runs, Then the data files are equal; Given a run without `--history`, Then the RQ-TRC-026 sentinel holds unchanged and
  git is not run; Given a process folder outside git, Then a warning is printed, there is no `history` key and the exit
  code is 0.
- **Dependencies**: TASK-HST-002
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-HST-004: History tab, timeline and overview strip
- **Tier**: L
- **Status**: Not Started
- **Description**: Add the History tab (only with history data) and its timeline: angle switch, code grouping, rows by
  type or by file and function, time axis, marks by shape, colour and size, virtualised rows, zoom, pan, fit, overview
  strip, hover tooltip and pinned commit card, row label selecting the element; one colour per identity (twelve
  categorical tokens, then golden-angle hues from tokens) and a human or agent icon beside each name; new tokens
  (identity colours, mark shapes and sizes, kind icons, row metrics) in the tiers of ADR-TRC-002.
- **Requirement refs**: RQ-HST-007, RQ-HST-014; RQ-TRC-018
- **ADR refs**: ADR-HST-001 (DEC-HST-005, DEC-HST-006); ADR-TRC-002
- **Acceptance Criteria**: Given a page without history, Then there is no History tab; Given a page with history, When
  the tab opens, Then the requirements angle shows one row per element with its marks; When the switch is set to code,
  Then files and their functions show; When the wheel turns over the timeline, Then it zooms around the pointer; When a
  mark is hovered, Then its commit card shows, and When clicked, Then it is pinned; When a row label is clicked, Then the
  element is selected in the detail panel; Given 2,000 rows, Then fewer than 100 row elements are in the document.
- **Dependencies**: TASK-HST-003
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-HST-005: Figures, activity band and filters
- **Tier**: M
- **Status**: Not Started
- **Description**: Draw above the timeline the key figures and the activity band stacked by human, agent and together,
  with its period following the zoom, and add the filter bar (identities, kind, empty rows, reset, counts kept).
- **Requirement refs**: RQ-HST-008, RQ-HST-009, RQ-HST-014; RQ-TRC-018
- **ADR refs**: ADR-HST-001 (DEC-HST-005, DEC-HST-006); ADR-TRC-002
- **Acceptance Criteria**: Given 100 commits of which 60 with an agent, Then the figures read 100 commits and 60 %;
  When one identity is selected, Then the figures, the band and the marks count only its commits and empty rows hide;
  When the kind "agents" is chosen, Then only commits with an agent stay; When reset, Then all show; When the zoom goes
  from a year to two weeks, Then the band's period goes from month to day.
- **Dependencies**: TASK-HST-004
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-HST-006: Sidebar History section and detail panel History button
- **Tier**: M
- **Status**: Not Started
- **Description**: Add the sidebar's History section below Quality (identities by commits, kind icon, tooltip of merged
  names and e-mails, click opening the tab filtered) and the detail panel's History button scoping the tab to the
  selected element, with its removable chip.
- **Requirement refs**: RQ-HST-010, RQ-HST-011, RQ-HST-014; RQ-TRC-018
- **ADR refs**: ADR-HST-001 (DEC-HST-006); ADR-TRC-002
- **Acceptance Criteria**: Given spashx merged from two names and Claude Opus 5.5, Then the section lists both with
  their counts and kinds; When the pointer rests on spashx, Then the tooltip lists both names and "merged by e-mail";
  When spashx is clicked, Then the tab opens filtered on spashx; Given FTR-A containing RQ-A1 and RQ-A2, When its History
  button is pressed, Then the rows are FTR-A, RQ-A1, RQ-A2 with a chip "FTR-A"; When the angle is code, Then the rows are
  the code citing them; When the chip is removed, Then all rows show with the filters kept.
- **Dependencies**: TASK-HST-005
- **Assignee**: AI
- **Verification**:
- **Assumptions**:

### TASK-HST-007: Speed, accessibility, documentation and the demo's page
- **Tier**: M
- **Status**: Not Started
- **Description**: Measure RQ-HST-013 on a generated repository of 2,000 commits, check the contrast, keyboard paths and
  literals of RQ-HST-014 and RQ-TRC-067, complete `SKILL.md`, the README and the `.claude` pointer's description, and
  generate the demo's page with `--call-graph --history` to check it by eye.
- **Requirement refs**: RQ-HST-013, RQ-HST-014; RQ-TRC-067
- **ADR refs**: ADR-HST-001 (DEC-HST-002, DEC-HST-005)
- **Acceptance Criteria**: Given the generated repository, Then the history adds less than 20 s and 3 MB, the tab draws
  in less than 300 ms and each zoom, pan or filter step redraws in less than 50 ms at P95; Given the tokens of both
  themes, Then the marks meet 3:1 and the texts 4.5:1; Given the view driven by the keyboard only, Then every control and
  mark is reached; Given the skill's code, Then the literal test passes; Given the demo, Then its page shows its six
  identities in the History section.
- **Dependencies**: TASK-HST-006
- **Assignee**: AI
- **Verification**:
- **Assumptions**:
