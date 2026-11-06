# FTR-DSY-001: Design-system template as a skill

## Overview
The design-system template used to be a loose `.md` file in `process/1.requirements/`, a folder
meant for the project's own artifacts. This feature packages it as a skill, `agnos-design-system`,
invocable from GitHub Copilot and Claude Code, which owns the template and the procedure to
instantiate it in a UI project (MANDATORY DESIGN SYSTEM).

## Stakeholders
- **Owner**: AGNOS process maintainer (this repository)
- **Consumers**: AI agents running the AGNOS process on UI projects; human readers of
  `GETTING_STARTED.MD`

---

## Functional Requirements

### RQ-DSY-001: Design-system template provided by a skill
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN a UI project needs its design system, the `agnos-design-system` skill SHALL
  provide the template from its own `assets/` folder and the procedure to instantiate it into
  `process/1.requirements/` with its own RQ and ADR IDs.
- **Rationale**: Process tooling belongs in skills, not among the project's artifacts.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** the repository
  - **When** `process/1.requirements/design-system-template.md` is searched for
  - **Then** no reference remains outside test fixtures and backups
  - **And** the template exists at `.github/skills/agnos-design-system/assets/design-system-template.md`
  - **And** both `.github` and `.claude` entry points of the skill exist
- **Dependencies**: None
