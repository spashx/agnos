# PLAN-PLG-008: Writing-format alignment of the demo

## Overview
Record the owner's writing rules (FTR-PLG-007), correct the title range, align the demo and the website on them, then release
3.4.0, rebuild the demo on it and rehearse its marketplace.

## References
- **Requirement refs**: RQ-PLG-039, RQ-PLG-040, RQ-PLG-041, RQ-DMO-005, RQ-DMO-008, RQ-DMO-021, RQ-PLG-027 to RQ-PLG-033, RQ-PLG-012, RQ-WEB-003, RQ-WEB-005
- **ADR refs**: ADR-DMO-001, ADR-PLG-005, ADR-PLG-002, ADR-WEB-001

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-PLG-053: Record artifact writing-format requirements
- **Tier**: M
- **Status**: Done
- **Description**: Write FTR-PLG-007 (RQ-PLG-039 to RQ-PLG-041) and this plan.
- **Requirement refs**: RQ-PLG-039, RQ-PLG-040, RQ-PLG-041
- **ADR refs**: None
- **Acceptance Criteria**: Given `agnos-index`, When run, Then it indexes FTR-PLG-007, its 3 RQs and this plan with no duplicate ID.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `agnos-index` exit 0, 843 entries, 119 documents; FTR-PLG-007, RQ-PLG-039 to 041, PLAN-PLG-008, TASK-PLG-053 to 061 indexed. No code: tests N/A.
- **Assumptions**: The owner's edit of `197f33c` is recorded as RQs without an ADR: it changes rules, not architecture.

### TASK-PLG-054: Correct title word range
- **Tier**: S
- **Status**: Done
- **Description**: Replace "3-8 words" by "2-8 words" in MANDATORY TITLE FORMAT and cite RQ-PLG-039 to RQ-PLG-041 in comments.
- **Requirement refs**: RQ-PLG-039, RQ-PLG-040, RQ-PLG-041
- **ADR refs**: None
- **Acceptance Criteria**: Given the instructions file, Then it states 2-8 words And stays within 400 lines.
- **Dependencies**: TASK-PLG-053
- **Assignee**: AI
- **Verification**: N/A (Tier S); post-edit line count 396 (≤ 400).
- **Assumptions**: None

### TASK-PLG-055: Restructure demo decisions
- **Tier**: M
- **Status**: Done
- **Description**: Rewrite each DEC of the demo's ADRs as a one-sentence Statement and a Rationale, in `agnos-meta-demo/assets/content/`.
- **Requirement refs**: RQ-PLG-040, RQ-DMO-005
- **ADR refs**: ADR-DMO-001
- **Acceptance Criteria**: Given each demo ADR, Then each DEC holds a Statement "The … SHALL …" And a Rationale; Given the scenario's `edits`, Then each still finds its text.
- **Dependencies**: TASK-PLG-053
- **Assignee**: AI
- **Verification**: Re-count on the 7 ADRs: 12 `### DEC-`, 12 `- **Statement**: … SHALL …`, 12 `- **Rationale**:`. The scenario's ADR `edits` target `## Status` lines only, unchanged; "amber 50, 600" is in FTR-DSN-001, untouched. Rebuild check in TASK-PLG-059.
- **Assumptions**: Details the old prose held (routes, statuses, tiers) stay in the one-sentence Statement; the reasons move to the Rationale.

### TASK-PLG-056: Move demo ADR citations to plain text
- **Tier**: M
- **Status**: Done
- **Description**: Turn the `<!-- Motivated by: … -->` comments of the demo's ADRs into plain text.
- **Requirement refs**: RQ-PLG-041, RQ-DMO-008
- **ADR refs**: ADR-DMO-001
- **Acceptance Criteria**: Given the demo's `agnos-process/`, Then no artifact file holds an ID in an HTML comment.
- **Dependencies**: TASK-PLG-053
- **Assignee**: AI
- **Verification**: 7 comments turned into a plain "Motivated by: …." line; grep `<!--` in the demo's `agnos-process/`: 0 matches. Only the demo's own IDs, no AGNOS ID.
- **Assumptions**: `client/design/SCREENS.md`, outside `agnos-process/`, keeps its comment.

### TASK-PLG-057: Retitle demo artifacts
- **Tier**: M
- **Status**: Done
- **Description**: Retitle the demo's FTR, RQ, ADR, DEC, PLAN and TASK per RQ-PLG-039, keeping their IDs; a title joining two concerns becomes one covering title; the drafts and the scenario follow.
- **Requirement refs**: RQ-PLG-039, RQ-DMO-005
- **ADR refs**: ADR-DMO-001
- **Acceptance Criteria**: Given every demo artifact title, Then it complies with MANDATORY TITLE FORMAT; Given the scenario's `edits` and commit messages, Then they match the new text.
- **Dependencies**: TASK-PLG-055, TASK-PLG-056
- **Assignee**: AI
- **Verification**: One-off script (scratchpad) on headings only: 68 IDs retitled of 68, none missing, 23 files (19 process documents, 4 drafts), 84 lines changed. No scenario `edits` targets a title. 6 `docs` commit messages restating an ADR title updated; `scenario.json` parses. No demo code quotes a title. Rebuild in TASK-PLG-059.
- **Assumptions**: 12 titles kept as compliant (FTR-BKG-001/002, FTR-NTF/DSN/WEB-001, RQ-CLI-001/002, RQ-DSN-001, RQ-NTF-004, PLAN-BKG-001/002, PLAN-NTF/DSN/WEB-001). Commit messages are descriptions, kept unless they restate an ADR title. File names unchanged.

### TASK-PLG-058: Prepare version 3.4.0 release
- **Tier**: M
- **Status**: Done
- **Description**: Run `agnos-meta-release-prep`: repository checks, docs-sync, changelog, version 3.4.0 approved by the owner, commit.
- **Requirement refs**: RQ-PLG-027 to RQ-PLG-033
- **ADR refs**: ADR-PLG-005
- **Acceptance Criteria**: Given `VERSION.txt`, Then it holds 3.4.0; Given the changelog, Then a 3.4.0 section lists this plan's changes.
- **Dependencies**: TASK-PLG-054, TASK-PLG-057
- **Assignee**: AI
- **Verification**: `check` exit 0 (open: TASK-PLG-007 and this plan's tasks, continued). docs-sync changed `CHANGELOG.md` and the guide template only; `review`: no unexpected file, proposed 3.4.0, approved by the owner (2026-11-11). `set-version 3.4.0` exit 0: `VERSION.txt` reads 3.4.0, `## [3.4.0]` above `## [3.3.0]`. No code: tests N/A.
- **Assumptions**: docs-sync left two flags for later: the guide's Stage 8 still says the guide is at the project's root, and AGENTS.md section 2 says "in comments" for every artifact (RQ-PLG-041).

### TASK-PLG-062: Add demo ADR diagrams
- **Tier**: M
- **Status**: Done
- **Description**: Give each of the demo's 7 ADRs a `classDiagram` of its entities and a `sequenceDiagram` of their interactions, as the ADR template requires; added by the owner on 2026-11-11.
- **Requirement refs**: RQ-DMO-005
- **ADR refs**: ADR-DMO-001
- **Acceptance Criteria**: Given each demo ADR, Then its `## Diagram` holds a `classDiagram` And a `sequenceDiagram`, scoped to the requirements it cites.
- **Dependencies**: TASK-PLG-057
- **Assignee**: AI
- **Verification**: Count per ADR: 1 `classDiagram` and 1 `sequenceDiagram` in each of the 7. Class names taken from the demo's code (grep); the DSN sequence corrected after reading `server.ts:68` (stylesheet built at start), the factory named `create_repository` from `repository_factory.py:17`. Not checked: Mermaid rendering, no `mmdc` installed; the owner's visual check covers it.
- **Assumptions**: The existing flowchart of each ADR is kept as an extra diagram. Sequence messages are descriptive where the method name was not read.

### TASK-PLG-059: Rebuild demo on version 3.4.0
- **Tier**: M
- **Status**: Done
- **Description**: Run `agnos-meta-demo build -Verify` and the generator's tests.
- **Requirement refs**: RQ-DMO-005, RQ-DMO-008, RQ-DMO-021
- **ADR refs**: ADR-DMO-001
- **Acceptance Criteria**: Given the rebuilt demo, When `verify` runs, Then every requirement is PASS; Given the generator's tests, Then they pass.
- **Dependencies**: TASK-PLG-058, TASK-PLG-062
- **Assignee**: AI
- **Verification**: `build.ps1 -Verify` exit 0 (Sonnet sub-agent): 84 commits, HEAD `c95238e`, "23 passed, 0 failed" (RQ-DMO-005: 7 ADRs with DEC and diagram; RQ-DMO-008: uncovered 0; RQ-DMO-021: second build same HEAD). Generator tests: 12 run, 12 OK, 0 skipped. Re-read in the demo: HEAD `c95238e`; index `RQ-BKG-003|42-56||Double booking rejection`, `TASK-BKG-003|50-66|Done|Implement overlap rule`; TASK-BKG-003's feat commit `12dc6e4`.
- **Assumptions**: None

### TASK-PLG-060: Align website with renamed demo
- **Tier**: M
- **Status**: Done
- **Description**: Update `en.md` and `fr.md` where they quote the demo's titles, excerpts and index lines, then rebuild the site; the owner checks it visually.
- **Requirement refs**: RQ-WEB-003, RQ-WEB-005
- **ADR refs**: ADR-WEB-001
- **Acceptance Criteria**: Given the site's text, Then every demo title, excerpt and line range it quotes matches the rebuilt demo; Given `agnos-meta-website`, Then its content check passes.
- **Dependencies**: TASK-PLG-059
- **Assignee**: AI (text), Human (visual check)
- **Verification**: In both languages: RQ-BKG-003, TASK-BKG-003, ADR-BKG-002 and DEC-BKG-003 titles, the ADR excerpt's citation as plain text, and the commit `3aec803` → `12dc6e4` (TASK-BKG-003's feat commit in the rebuilt demo); line ranges 42-56 and 50-66 unchanged. `test_page.py`'s expected graph title follows the new RQ title. Build into the scratchpad exit 0: 152 fields per language, 8 images, demo page generated. Website tests: 59 run, 59 OK, 0 skipped. Re-counted in the built `index.html`: "No double booking" 0, "Double booking rejection" 8, `3aec803` 0, `12dc6e4` 2. Visual check: the owner's.
- **Assumptions**: The screenshots in `assets/screens/` were not re-captured: `graph.png` may still show the old title. `test_content.py`'s fixtures (a fake index) keep their old text, which they do not read from the demo.

### TASK-PLG-061: Rehearse 3.4.0 marketplace release
- **Tier**: M
- **Status**: Done
- **Description**: Run `agnos-meta-release` on the 3.4.0 commit; nothing is published.
- **Requirement refs**: RQ-PLG-012, RQ-PLG-031
- **ADR refs**: ADR-PLG-002
- **Acceptance Criteria**: Given the rehearsal, Then its manifests hold 3.4.0 And both checks are true And exit is 0.
- **Dependencies**: TASK-PLG-058
- **Assignee**: AI
- **Verification**: Rehearsal of `94ef69f` into the scratchpad (Sonnet sub-agent): `exit=0, 70 files, 1571 IDs removed, 4 lines to read`; no `problems:`, no `idsOutsideComments:`, no `unreleased:` line. Re-read: `plugin.json` version 3.4.0; report checks `noIdLeft`, `manifests`, `sameBehaviour` all true. The 4 lines to read are lines whose ID comment was removed, reading well (e.g. "Every ADR File SHALL use the following structure exactly:"). Mentions: `agnos-meta-` in the changelog and 3 test names, as in earlier releases.
- **Assumptions**: The `agnos-marketplace` folder (3.3.0) is replaced only on the owner's word.
