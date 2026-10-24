# PLAN-DOC-001: Documentation Sync Sub-Agent

## Overview
Implement RQ-DOC-001 to RQ-DOC-004 in two tasks: the report script with its tests, then the skill, its Claude Code pointer
and the Haiku sub-agent. Done on the current branch at the owner's request (no new session).

## References
- **Requirements**: RQ-DOC-001, RQ-DOC-002, RQ-DOC-003, RQ-DOC-004
- **ADRs**: None (Tier M tasks)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-DOC-001: Report of the changes since each document's last change
- **Tier**: M
- **Status**: Done
- **Description**: A Python script, `changes_since.py`, that prints as JSON, for each of the four documents, its last
  change and the commits since (without the generated and session files' commits), and the repository's skills with their
  maintainer flag; with tests on a temporary repository.
- **Requirement refs**: RQ-DOC-001, RQ-DOC-004
- **ADR refs**: None
- **Acceptance Criteria**: Given a temporary repository whose changelog was last changed by commit A, followed by one
  commit that touches only the index and one that changes a skill, When the script runs, Then it gives A as the
  changelog's last change and the skill's commit only; Given a document never committed, Then its last change is null;
  Given two runs, Then the outputs are equal.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `python -m unittest discover -s .github/skills/agnos-docs-sync/tests`: 7 tests, 0 failure. On a temporary repository: the changelog last changed by commit A gives A and only the later commit with real changes (the index-and-session-only commit is left out, the commit's files listed); a document never committed has a null last change and every commit; a merge commit is not listed; skills carry name, description, path and the maintainer flag (agnos-demo true); two runs give equal JSON; a folder that is not a repository exits 1 with "not a git repository"; no repeated literal (detector of the agnos-trace skill). On this repository: CHANGELOG.md last changed 11ecffc, 78 commits since; AGENTS.md and CLAUDE.md c373abd, 25; GETTING_STARTED.MD fa8f7aa, 26; 5 skills, agnos-demo flagged maintainer.
- **Assumptions**: the script lives in the skill's folder, `.github/skills/agnos-docs-sync/scripts/`.

### TASK-DOC-002: The skill, its pointer and the Haiku sub-agent
- **Tier**: M
- **Status**: Not Started
- **Description**: The skill `agnos-docs-sync` (canonical procedure under `.github/skills/`, pointer under
  `.claude/skills/`) with the rules for each document, and the sub-agent `agnos-docs-sync` on the Haiku model under
  `.claude/agents/`.
- **Requirement refs**: RQ-DOC-002, RQ-DOC-003
- **ADR refs**: None
- **Acceptance Criteria**: Given the skill, When it is read, Then it names the four documents, the changelog format, the
  maintainer-skill exclusion and the ban on unsupported statements; Given the agent, Then its model is haiku, its tools
  cannot commit or write another file, and it follows the skill.
- **Dependencies**: TASK-DOC-001
- **Assignee**: AI
- **Verification**: Pending.
- **Assumptions**: the skill is a maintainer skill like `agnos-demo`: not listed in `AGENTS.md` or `CLAUDE.md`.
