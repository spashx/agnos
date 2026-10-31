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
