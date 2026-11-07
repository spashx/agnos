# FTR-PLG-005: Release Preparation

## Overview
A maintainer skill, `agnos-meta-release-prep`, runs the steps that come before `agnos-meta-release`: it brings the documents up
to date, shows the maintainer what will be released, asks for a review and a version, records them, and states the steps that follow.
The release takes its version from one file, in SemVer 2.0.0, and says when the changelog holds entries no version names yet.

Source: the owner's session of 2026-11-05. `agnos-meta-docs-sync` is described as "before a release", but nothing runs it: the
marketplace regenerated that day delivered a user's guide and a changelog behind the process (RQ-PLG-025, RQ-PLG-026 absent).

The owner asked, the same session, for the version in SemVer 2.0.0 and in one place, to be reused by the documents or the perf center, and for the user's guide
and the version to be in the project's `agnos-process/` folder once the plugin is installed.

Out of scope: publishing (merge, tag, push stay the owner's); choosing the version in the owner's place; showing the version in the
documents or the perf center (made possible by RQ-PLG-032 and RQ-PLG-033, not done here).

## Stakeholders
- **Owner**: the repository owner (maintainer of AGNOS).
- **Consumers**: the maintainer preparing a release; `agnos-meta-release`, which reads the prepared commit; `agnos-init`, which writes the
  guide and the version into each project.

---

## Functional Requirements

### RQ-PLG-027: The preparation checks the repository first
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: IF the working tree holds changes, or `agnos-index` reports duplicate IDs, THEN `agnos-meta-release-prep` SHALL stop before any edit, naming each changed file or duplicate ID; otherwise it SHALL list the tasks whose status is not Done, from the index.
- **Rationale**: the documents are synced from the commits; uncommitted work would be released without being described.
- **Priority**: Must
- **Acceptance Criteria**: Given a changed tracked file, When the check runs, Then it exits 1 and names the file, And no file is edited; Given a duplicate ID, Then it exits 1 and names it; Given a clean repository, Then it exits 0 And lists each task In Progress, Not Started or Blocked with its status.
- **Dependencies**: RQ-IDX-013

### RQ-PLG-028: The documents are synced, then shown for review
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the check passes, `agnos-meta-release-prep` SHALL run `agnos-meta-docs-sync`, then show the maintainer the list of changed files and their diff, the content of `## [Unreleased]`, and a proposed version in SemVer 2.0.0, from the version of RQ-PLG-032: the next major when `[Unreleased]` holds a `### Removed` section, the next minor when it holds `### Added` or `### Changed`, the next patch when it holds `### Fixed` only.
- **Rationale**: the maintainer reviews what will be released in one place, with a version derived from it rather than recalled.
- **Priority**: Must
- **Acceptance Criteria**: Given the version `3.1.0` and an `[Unreleased]` with Added and Changed, Then the proposal is `3.2.0`; Given a `### Removed` section, Then it is `4.0.0`; Given `### Fixed` only, Then it is `3.1.1`; Given an empty `[Unreleased]`, Then the preparation says there is nothing to release And proposes no version; Given a file changed outside the four of docs-sync, Then it is named as unexpected.
- **Dependencies**: RQ-PLG-027, RQ-PLG-032, RQ-DOC-001, RQ-DOC-002

### RQ-PLG-029: Nothing is recorded without the maintainer's approval
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the maintainer approves the diff and a version, `agnos-meta-release-prep` SHALL write that version into the version file of RQ-PLG-032 and rename `## [Unreleased]` to `## [<version>]`, leaving every other line of the changelog unchanged, and commit through `agnos-git-workflow`'s `commit-task`; IF the maintainer does not approve, THEN it SHALL leave the working tree as docs-sync left it and commit nothing.
- **Rationale**: the version and the documents are the maintainer's decision; the commit is the one `agnos-meta-release` reads.
- **Priority**: Must
- **Acceptance Criteria**: Given an approved version `3.2.0`, Then the version file holds `3.2.0` And the changelog's heading is `## [3.2.0]` And every other line is unchanged; Given a version that is not SemVer 2.0.0, or not above the current one by SemVer precedence, Then it is refused And neither file changes; Given no approval, Then no commit is made.
- **Dependencies**: RQ-PLG-028, RQ-PLG-032

### RQ-PLG-030: The steps that follow are stated
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the preparation is committed, `agnos-meta-release-prep` SHALL print, in order, the steps left: `agnos-meta-release` into an empty folder, `agnos-meta-plugin-proof`, the regeneration of the marketplace folder, and the merge, tag and push, which are the maintainer's; it SHALL run none of them.
- **Rationale**: the order of the release steps is written once rather than remembered; publishing stays a human act (DEC-PLG-007).
- **Priority**: Must
- **Acceptance Criteria**: Given a committed preparation, Then the four steps are printed in that order with the commit's short SHA And no command of theirs was run.
- **Dependencies**: RQ-PLG-029

### RQ-PLG-031: The release says when versions lag behind the changelog
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE the changelog at the rehearsed commit holds entries under `## [Unreleased]`, `agnos-meta-release` SHALL print `unreleased: <n> entries, version <VERSION> delivered` and record the count in its report, failing nothing.
- **Rationale**: a rehearsal during development is legitimate, but a release from an unprepared commit must not pass unnoticed.
- **Priority**: Should
- **Acceptance Criteria**: Given a commit whose `[Unreleased]` holds 3 bullets, Then the line says 3 entries And the exit code is unchanged; Given no `[Unreleased]` entry, Then no such line is printed.
- **Dependencies**: RQ-MTA-006, RQ-PLG-014, RQ-PLG-032

### RQ-PLG-032: One version, in SemVer 2.0.0, in one file
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The repository SHALL hold its version in one file, `VERSION.txt`, among `agnos-init`'s templates (`.github/skills/agnos-init/assets/templates/VERSION.txt`), as a SemVer 2.0.0 version on a single line; `agnos-meta-release` SHALL take the manifests' version from it and refuse a commit whose `VERSION.txt` is absent or not SemVer 2.0.0. The changelog's headings record the released versions; they are not read as the version. It replaces the changelog's latest release as the source of the manifests' version, which no requirement stated. <!-- amended by DEC-PLG-032 (2026-11-07): the file is `VERSION.txt` -->
- **Rationale**: a version read from one place can be shown by the documents and the perf center without being copied, and never disagrees with itself; among the init's templates it is delivered with the plugin and written into each project (RQ-PLG-033), as the user's guide is (RQ-PLG-022).
- **Priority**: Must
- **Acceptance Criteria**: Given `VERSION.txt` holding `3.2.0`, When the release is rehearsed, Then the four manifests hold `3.2.0` And the delivered `agnos-init` skill holds the same `VERSION.txt`; Given `VERSION.txt` absent or holding `v3.2`, Then the release exits 1 before writing anything, naming the file; Given the changelog's latest release `[v3.1]`, Then it is left as it is.
- **Dependencies**: RQ-PLG-001, RQ-PLG-022

### RQ-PLG-033: The guide and the version are written into the project's process folder
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN `agnos-init` runs on a project, it SHALL write `AGNOS-GETTING-STARTED.md` and `VERSION.txt` into the project's process folder (`agnos-process/`, RQ-PLG-034), each reported `created`, `updated` or `unchanged`; IF an `AGNOS-GETTING-STARTED.md` is at the project's root and its first line is the one AGNOS writes, THEN it SHALL remove it and report it `moved`, leaving any other root file untouched. Amends RQ-PLG-021 and DEC-PLG-016 on the guide's location. <!-- amended by DEC-PLG-032 (2026-11-07): the file is `VERSION.txt` -->
- **Rationale**: the files AGNOS owns in a project stay in its `agnos-process/` folder, away from the developer's root; the version installed in a project can be read there.
- **Priority**: Must
- **Acceptance Criteria**: Given a project, When `agnos-init` runs, Then `agnos-process/AGNOS-GETTING-STARTED.md` and `agnos-process/VERSION.txt` equal the templates And are reported `created`; Given a second run, Then both are `unchanged`; Given a root `AGNOS-GETTING-STARTED.md` written by a former init, Then it is removed and reported `moved`; Given a root file of that name with another first line, Then it is untouched; Given the Windows and the Linux scripts, Then they write the same bytes; Given `agnos-index`, Then neither file adds an entry; Given the README and the init's success step, Then they name `agnos-process/AGNOS-GETTING-STARTED.md`.
- **Dependencies**: RQ-PLG-021, RQ-PLG-022, RQ-PLG-032, RQ-PLG-034, RQ-INI-007
