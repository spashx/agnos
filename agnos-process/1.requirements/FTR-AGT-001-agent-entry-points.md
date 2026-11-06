# FTR-AGT-001: Agent entry points
<!-- Amended on 2026-10-31: the skill, its script and its outputs carry their current names (RQ-TRC-104, RQ-TRC-105, DEC-TRC-055). -->

## Overview
Every AI coding agent working on the repository must load the whole AGNOS process. GitHub Copilot
reads `.github/instructions/`, Claude Code reads `CLAUDE.md`; this feature adds `AGENTS.md`, the
cross-tool convention read by other agents, and keeps all entry points aligned on the same skills.

## Stakeholders
- **Owner**: AGNOS process maintainer (this repository)
- **Consumers**: AI coding agents (Codex, Cursor, Gemini, Windsurf, Aider, Copilot, Claude Code)

---

## Functional Requirements

### RQ-AGT-001: Every agent entry point loads the whole process
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The repository SHALL provide an entry point for each supported agent family
  (`.github/instructions/` for Copilot, `CLAUDE.md` for Claude Code, `AGENTS.md` for others) that
  directs the agent to the normative instructions file and lists every AGNOS skill with its
  canonical `SKILL.md` path.
- **Rationale**: An agent that misses the process or a skill breaks traceability silently.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** `AGENTS.md` and `CLAUDE.md`
  - **When** they are read
  - **Then** each references `.github/instructions/agnos-sw-eng.instructions.md`
  - **And** each names the skills `agnos-index`, `agnos-git-workflow`, `agnos-design-system` and `agnos-perf-center`
- **Dependencies**: RQ-DSY-001

### RQ-AGT-002: Every entry point restates the approval gate explicitly
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: Each agent entry point SHALL restate, in its own text (not only by reference to the imported
  instructions file), that every task is tiered, presented to the user, and started only after explicit approval.
- **Rationale**: an entry point's own wording is what an agent attends to most directly; a rule stated once, deep in
  the imported file, is easier to lose under a "keep going" default than one restated locally.
- **Priority**: Should
- **Acceptance Criteria** (Gherkin):
  - **Given** `CLAUDE.md`
  - **When** it is read
  - **Then** it carries `AGENTS.md`'s own restatement of the approval gate, loaded through `CLAUDE.md`'s own
    mechanism rather than copied as a second source of the same text
- **Dependencies**: RQ-AGT-001
