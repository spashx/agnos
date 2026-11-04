---
name: agnos-meta-docs-sync
description: Updates CHANGELOG.md, AGENTS.md, CLAUDE.md and the user's guide AGNOS-GETTING-STARTED.md, agnos-init's template, from what changed in the repository since each was last changed. Use before a release or after a series of tasks. Edits those four files only and never commits.
tools: Read, Grep, Glob, Edit, Bash
model: haiku
---

<!-- FTR-DOC-001; RQ-DOC-003 -->
Read `.github/agents/agnos-meta-docs-sync.agent.md` and follow it literally. It is this agent's single definition, shared with GitHub Copilot.
