# PLAN-DSY-001: Design-system template as a skill

## Overview
Implements FTR-DSY-001: the `agnos-design-system` skill and the update of every reference to the
former template path.

## References
- **Requirements**: RQ-DSY-001
- **ADRs**: ADR-DSY-001 (DEC-DSY-001)

---

## Tasks

### TASK-DSY-001: agnos-design-system skill and reference updates
- **Tier**: L
- **Status**: Done
- **Description**: Move the template into the new skill, write its canonical and Claude Code entry
  points, and update the instructions file, CLAUDE.md, GETTING_STARTED.MD and ADR-TRC-002.
- **Requirement refs**: RQ-DSY-001
- **ADR refs**: ADR-DSY-001 (DEC-DSY-001)
- **Acceptance Criteria** (Gherkin):
  - **Given** the repository
  - **When** the former path is searched for
  - **Then** it appears only in test fixtures and backups
  - **And** the instructions file stays within 800 lines
  - **And** the index rebuilds with no duplicate
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `git grep -n design-system-template`: only the 3 updated references to the new
  path remain (GETTING_STARTED.MD:696, :728, ADR-TRC-002:12); the agnos-index fixture copy is its
  own test file. Template moved by `git mv` (status `R`). Instructions file: 381 lines (≤ 800).
  `build-index.ps1`: 156 entries, 17 documents, exit 0. Skill listed by Claude Code.
- **Assumptions**: Trigram DSY approved by the user. No unit test: no production code, only
  documentation and a file move (`unit_tests=true` but nothing executable to test). The
  agnos-index test fixture `design-system-template.md` is left as is (tests the `template.md`
  exclusion).

### TASK-DSY-002: README and GETTING_STARTED aligned with the current process and skills
- **Tier**: S
- **Status**: Done
- **Description**: Rewrite README.md (positioning, components, tiers) and update GETTING_STARTED.MD
  (agnos-index at session start, DEC headings, commit-time index refresh, new agnos-trace stage,
  agnos-design-system skill).
- **Requirement refs**: RQ-DSY-001
- **ADR refs**: ADR-DSY-001 (DEC-DSY-001)
- **Acceptance Criteria** (Gherkin):
  - **Given** README.md and GETTING_STARTED.MD
  - **When** they are compared with the instructions file and the skills
  - **Then** they describe the four skills and the current procedures without contradiction
- **Dependencies**: TASK-DSY-001
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: Documentation-only task, traced to RQ-DSY-001 since it documents the new skill;
  approved by the user. Tier S kept as no code, no new file, no API.
