# FTR-MTA-002: A Release Rehearsed Without Publishing

## Overview
DEC-MTA-004 decided that a release is the output of a build. This feature builds that output in a folder, on request, and proves
it: only the delivered layers, none of the IDs defined by AGNOS's own development, and the same behaviour as the workshop. Today
48 of the 58 files to deliver hold 1,094 citations of defined IDs, and removing them by hand is what `dev`'s commits did.

Out of scope: publishing (a commit on `main`, a tag, a push), the `plugin` target, and any change to the files of the workshop.

## Stakeholders
- **Owner**: the repository owner (maintainer of AGNOS).
- **Consumers**: the maintainer, who reads the rehearsal's report before deciding to publish; the later publishing step.

---

## Functional Requirements

### RQ-MTA-006: The rehearsal changes nothing but its output
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN `agnos-meta-release --dry-run --output <folder>` runs, the skill SHALL write only under `<folder>` and to its
  report `<folder>.report.json`, and SHALL NOT change the repository's files, branches, tags or commits, nor reach the network.
- **Rationale**: the owner's constraint stands: nothing is published until the owner lifts it (DEC-MTA-004).
- **Priority**: Must
- **Acceptance Criteria**: Given a repository, When the rehearsal runs, Then `git status`, its branches, tags and HEAD are the same as
  before; Given a `<folder>` inside the repository or not empty, When it runs, Then it exits 1 and writes nothing; Given no
  `--dry-run`, When it runs, Then it exits 1, says that only the rehearsal exists, and writes nothing.
- **Dependencies**: ADR-MTA-002

### RQ-MTA-007: The output comes from a commit
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The skill SHALL build from the files tracked at HEAD, as committed, and SHALL write the commit's hash in its report.
- **Rationale**: a release has to be traced to one commit, whatever lies uncommitted in the working tree.
- **Priority**: Must
- **Acceptance Criteria**: Given an untracked file and an uncommitted edit, When the rehearsal runs, Then neither is in the output;
  Given one commit, When the rehearsal runs twice, Then both outputs are identical byte for byte, And the report gives the hash.
- **Dependencies**: RQ-MTA-006

### RQ-MTA-008: Every tracked file has a layer
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: The skill SHALL decide what is delivered from the rules of `assets/layers.json` and the prefix `agnos-meta-`; IF a tracked
  file matches no rule, THEN it SHALL exit 1, naming the file, and deliver nothing.
- **Rationale**: a new file must be classified by a person, neither leaked nor silently lost.
- **Priority**: Must
- **Acceptance Criteria**: Given this repository, When the rehearsal runs, Then the output holds no `process/`, no `agnos-meta-*`, no
  folder `tests/` or `test/` and no `.claude/settings.json`, And it holds the toolkit and public repository files of DEC-MTA-008;
  Given a tracked file matching no rule, Then it exits 1 and names it.
- **Dependencies**: RQ-MTA-002, RQ-MTA-004, ADR-MTA-002

### RQ-MTA-009: The defined IDs are removed, the examples stay
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The skill SHALL remove from the delivered text files, in comments as in visible text, every ID whose trigram appears in
  the commit's `process/INDEX.idx.md`, defined there or not, written in full or abbreviated, with the punctuation that served only that citation, and
  SHALL leave IDs of any other trigram unchanged.
- **Rationale**: a project's `grep` must hit its own artifacts only, while examples such as `RQ-EXP-001` teach the format.
- **Priority**: Must
- **Acceptance Criteria**: Given `(RQ-ABC-001, DEC-ABC-002)` of defined IDs, spread over one or two lines, Then the parentheses go too;
  Given `<!-- RQ-ABC-001 / ADR-ABC-001 -->` alone on a line, Then the line goes; Given `# RQ-ABC-001: the order` or
  `RQ-ABC-001 to RQ-ABC-004: the order`, Then `# The order` or `The order` remains; Given the visible text `## Rules (ADR-ABC-001: DEC-ABC-001; RQ-ABC-001)`,
  Then `## Rules` remains; Given `(1,000 tasks delivered; RQ-ABC-001)`, Then `(1,000 tasks delivered)` remains; Given `TASK-ABC-073, 074`, Then both go;
  Given `RQ-ABC-999`, undefined but of a trigram of the index, Then it goes; Given `RQ-EXP-001` or `DEC-USR-001`, of a trigram absent from the
  index, Then it is unchanged; Given a line with no defined ID, Then its bytes are unchanged, its line ending included.
- **Dependencies**: RQ-IDX-001, ADR-MTA-002

### RQ-MTA-010: A defined ID left fails the rehearsal
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: IF an ID of a trigram of the index remains in the output, in a file's content or its path, in a text or binary file, or a
  file of the Meta layer is there, THEN the skill SHALL exit 1, naming each file and line.
- **Rationale**: a user's tool parsing the release must find no ID from AGNOS's development; the check reads the output, so that it does not depend on the removal having worked.
- **Priority**: Must
- **Acceptance Criteria**: Given an output with such an ID left, in a comment, in visible text, in a form the removal does not know, or undefined
  in the index, When the check runs, Then it exits 1 and names the file and the line; Given an output holding only `RQ-EXP-001`, Then it passes.
- **Dependencies**: RQ-MTA-009

### RQ-MTA-011: The output behaves as the workshop does
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the output is written, the skill SHALL run `agnos-index` and `agnos-perf-center` from the workshop and from the output
  on the demo, and `agnos-init` from both on an empty folder, compare what they write, and exit 1 on any difference or on a delivered
  Python, JavaScript, JSON, PowerShell or bash file that no longer parses. IF the demo is absent, THEN it SHALL exit 1.
- **Rationale**: the removal edits 48 files including their code, and the tests of the skills are not delivered.
- **Priority**: Must
- **Acceptance Criteria**: Given the demo, When the rehearsal runs, Then its `process/INDEX.idx.md`, its `PERF-CENTER.json` generated with a
  fixed `--generated-at`, and the `CLAUDE.md` and `AGENTS.md` of `agnos-init`, are the same from both, the toolkit's path aside; Given a removal that breaks
  a delivered script, Then it exits 1 and names the script; Given no demo, Then it exits 1 and says to build it with `agnos-meta-demo`.
- **Dependencies**: RQ-MTA-005, RQ-MTA-009, DEC-MTA-010

### RQ-MTA-012: The report says what to read
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The skill SHALL write in its report the commit, the files delivered and left out, the IDs removed per file, the
  lines to read and each check's result, and SHALL print one summary line with its duration; the lines to read, which are removed
  citations whose sentence may no longer read well, IDs found outside a comment in the workshop's Markdown (RQ-MTA-014), and mentions of
  `agnos-meta-` or of an undelivered path, SHALL NOT fail the rehearsal.
- **Rationale**: text rules cannot judge a sentence such as "justified in TASK-QLT-006", and the owner decides before publishing.
- **Priority**: Must
- **Acceptance Criteria**: Given a sentence left ending in "in" by a removal, Then it is listed with its file and line, And the exit is 0
  if nothing else fails; Given `CONTRIBUTING.md`'s mention of `agnos-meta-qa`, Then it is listed, And the file is delivered; Given an ID
  outside a comment in a Markdown file of the commit, Then it is listed with its file and line, And the exit is 0 if nothing else fails.
- **Dependencies**: RQ-MTA-009, RQ-MTA-014

### RQ-MTA-013: A maintainer skill like the others
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: `agnos-meta-release` SHALL be packaged as `.github/skills/agnos-meta-release/SKILL.md` with its Claude Code pointer, its
  tests under its `tests/` folder, and it SHALL run from one Python script using the standard library only.
- **Rationale**: the same command on all three platforms, and the `SKILL.md` practices the owner keeps for every skill.
- **Priority**: Must
- **Acceptance Criteria**: Given the skill, Then its description says what and when within 1,024 characters, And `SKILL.md` is under 500
  lines, And the script imports nothing outside the standard library, And `CHANGELOG.md` names the skill.
- **Dependencies**: RQ-MTA-001, DEC-MTA-007

### RQ-MTA-014: The workshop's citations stay in comments
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The repository's Markdown files outside `process/`, and the help and console texts of its scripts, SHALL show no artifact ID
  of this repository outside a comment, and `agnos-meta-docs-sync` SHALL write a `CHANGELOG.md` entry's IDs in an HTML comment. The output of
  `agnos-meta-demo`'s `verify.ps1`, which reports on each requirement by its ID, is excepted.
- **Rationale**: MANDATORY TRACEABILITY puts references in comments, never as plain text, and `agnos-meta-docs-sync` ordered the contrary.
- **Priority**: Must
- **Acceptance Criteria**: Given the Markdown files outside `process/`, When HTML comments are set aside, Then none shows such an ID; Given
  `perf_center.py`, `changes_since.py` and `qa.py`, When run with `--help`, Then none shows an ID; Given `CHANGELOG.md`, When an ID of a
  previous entry is searched, Then it is still found; Given a skill's `SKILL.md`, When `agnos-meta-docs-sync`'s is read, Then it asks for the comment form.
- **Dependencies**: RQ-DOC-002
