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
- **Status**: Done
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
- **Verification**: `python -m unittest discover -s tests` (skill folder): 189 tests, 0 failure, 1 skipped; `test_history.py` run with `-W error::ResourceWarning`: 28 tests OK. `LineTrackingTest` (11): Alice's commit on line 7 credits RQ-A (2 lines) not RQ-B; still on RQ-A after 3 lines inserted above; kept after `git mv`; side-branch commit credited to RQ-B, merge author walked never credited; uncommitted edits credit no one; a range added by a commit stops there; `g` and the whole file credited, `f` not; `depth=2` reads 2 commits; `since` filters on the author date; two runs equal; lines looking like `+++ b/` and holding `\r` counted right. Against `git log -L` on 25 random elements of this repository and 25 of the demo: 50 equal, 0 different. This repository's process folder: 91 commits read, 301 elements credited, 0.30 s. `test_literals.py`: 0 repeated literal.
- **Assumptions**: `--since` is passed to git (committer date) to bound the walk, and the author date is then checked against the cutoff git computes (`git rev-parse --since`), since RQ-HST-001 speaks of commits authored since. A hunk's removed lines count in proportion of its added lines in the range; a pure removal counts when it lies strictly inside the range. Two children carrying one range back differently give the parent the span of both.

### TASK-HST-003: Generator options, `history` data and summary line
- **Tier**: M
- **Status**: Done
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
- **Verification**: `python -m unittest discover -s tests` (skill folder): 197 tests, 0 failure, 1 skipped; `test_history.py`: 36 OK. `GeneratorTest` (8): `--history-depth 5` or `--history-since` without `--history` exit 1 naming `--history`; depth `0`, `-3`, `ten` exit 1 naming `--history-depth`; with `--history` the data holds `limits` (2 commits, first and last dates, not shallow), `people` (Alice, Carol, Claude Opus 5.5), `commits` (second `together`), `interventions` (RQ-ABC-001 `[[0, 6], [1, 2]]`, files keyed as the data file's files) and the line ends with `history: 2 commits, 2 humans, 1 agents`; depth 1 and since applied and written; two runs give equal bytes; without `--history` the history module is not loaded and no key is written; a process folder outside git prints `warning: no history: the process folder is not inside a git working tree`, exit 0, no key; with `--call-graph`, `g` is credited to Bob and Carol, `f` to Carol. RQ-TRC-026 sentinel unchanged (passes as pinned). This repository with `--call-graph`: 0.93 s without, 1.93 s with `--history` (100 commits, 1 human, 2 agents), data 1,029,111 to 1,112,083 bytes. Demo: 53 commits, 6 humans, interventions for 54 elements, 50 files, 219 functions. `SKILL.md`: options, exit line, History section.
- **Assumptions**: A depth that is not a positive integer is an input error (exit 1) rather than argparse's exit 2, as RQ-HST-001 asks. The history reads the process folder and the source folders only; a source folder outside the repository is left out. git writes UTC author dates with `Z`, which `datetime.fromisoformat` reads only from Python 3.11: the date is read with `+00:00` in its place, for the skill's Python 3.9.

### TASK-HST-004: History tab, timeline and overview strip
- **Tier**: L
- **Status**: Done
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
- **Verification**: `python -m unittest discover -s tests` (skill folder): 206 tests, 0 failure, 1 skipped. `test_history_page.py` (9, headless Edge, synthetic `history` block): no History tab without history; requirements angle has elements + type headings as rows, RQ-DEM-001 shows marks of commits 0, 2, 5; code angle rows are the files; a wheel notch over the marks narrows the period and keeps the time under the pointer (< 1 % drift); `+` zooms, `→` pans, `0` fits back; a focused mark's tooltip gives hash, Alice, Claude Opus 5.5, subject and "2 lines", a click pins the card; a row label selects RQ-DEM-001; marks are agent:path, human:circle, together:circle, each focusable and named; 2,002 rows (1,999 requirements) leave fewer than 100 rows in the document before and after scrolling to the middle. `test_literals.py` OK, and a direct count of the history section shows no repeated literal (the test's tokenizer misses some occurrences after template literals). Screenshots of this repository's page (100 commits, 2,429 code rows) in both themes checked by eye: rows, axis, ringed together-marks in the agent's colour, overview ticks, pinned card listing the 9 files of a commit. Identity colours: the twelve tokens give at least 3.09:1 on the raised surface of both themes, the golden-angle hues at least 3.44:1 (computed). `test_scorecard.py` RQ-TRC-060 test: its DOM reading took the last `data-view` of the page, now the History tab's; it reads the root element's, its expectation unchanged.
- **Assumptions**: The wheel zooms over the marks and scrolls the rows over the labels, so both stay reachable. The overview strip is drawn but its keyboard path is the timeline's keys. Group headings are rows (one per type), counted in the total. The legend shows the shapes in a neutral colour, so that it is not read as identity colours.

### TASK-HST-005: Figures, activity band and filters
- **Tier**: M
- **Status**: Done
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
- **Verification**: `python -m unittest discover -s tests` (skill folder): 211 tests, 0 failure, 1 skipped. `FiguresAndFiltersTest` (5, headless Edge): the figures of the synthetic history read 5 commits, 2 humans, 1 agent, 40 % with an agent (commits 2 and 4 of 5 shown); Bob selected keeps only TASK-DEM-001 and its heading (2 rows), 1 commit, "1 row" kept, and "Rows without changes" shows the others again; the kind Agents keeps commits 2 and 4 only, Reset brings every row and commits 0, 1, 2, 4, 5 back; the band is drawn week by week at fit (79 days) and day by day on a 10-day period, with bars; 20 identities give 20 chips with 20 different swatch colours and the agent icon on the 4 agents. `test_literals.py` OK and a direct count of the history section shows no repeated literal. Screenshot of this repository on 30 days: figures 76 commits, 1 human, 2 agents, 100 % with an agent, 29 days; chips spashx 102, Claude Opus 5.5 54, Claude Sonnet 5.5 35; day bars stacked.
- **Assumptions**: The figures count the commits on the rows shown (angle, scope, filters), over the whole history, not only the period in view; the band and the status count the period in view. "Humans" keeps the commits with a human contributor (human or together), "Agents" those with an agent (agent or together). Empty rows hide only while a filter is on, so the unfiltered timeline lists every element. A day bucket up to 45 days in view, a week up to 270, else a month.

### TASK-HST-006: Sidebar History section and detail panel History button
- **Tier**: M
- **Status**: Done
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
- **Verification**: `python -m unittest discover -s tests` (skill folder): 218 tests, 0 failure, 1 skipped. `EntryPointsTest` (7, headless Edge): the sidebar's History section lists Alice, Bob, Claude Opus 5.5 with 3, 2, 3 commits and the human, human, agent icons; focusing Alice shows a tooltip with "Alice", "alice", "alice@example.com" and "merged by e-mail"; clicking Bob opens the History tab with Bob's chip pressed and TASK-DEM-001 only; FTR-DEM-001's History button opens the tab on FTR-DEM-001 and RQ-DEM-001 to 005 with a "Scope: FTR-DEM-001" chip, and the code angle then lists exactly the files citing them; removing the chip of RQ-DEM-001's scope keeps the Humans filter and Reset brings every row back; a file's button opens the code angle on that file; without history, neither the section nor the button exists. `test_literals.py` OK; a direct count of the history section shows no repeated literal; `"undefined"`, `"kpi-label"`, `"kpi-value"`, `"chip-count"`, `"quality-shortcut"`, `"rect"`, `"commits"` named once at the top of the script (two of them were already written twice before this task). Screenshots: scope chip, sidebar identities with icons and counts, identity tooltip kept inside the window.
- **Assumptions**: The page tooltip moved out of the History view, so that it shows from the sidebar too. A function's scope is its own row; a file's scope is its row and its functions. An element's scope opens the requirements angle, a file's or function's the code angle by file.

### TASK-HST-008: Quality tab last
- **Tier**: S
- **Status**: Done
- **Description**: Put the Quality tab last in the tabs of the main area, after History (owner request of 2026-10-24).
- **Requirement refs**: RQ-HST-007, RQ-TRC-057
- **ADR refs**: ADR-HST-001 (DEC-HST-005)
- **Acceptance Criteria**: Given the page, When its tabs are read in order, Then they are Overview, Graph, Matrix, History
  (when the data hold a history) and Quality.
- **Dependencies**: TASK-HST-004
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: None

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
