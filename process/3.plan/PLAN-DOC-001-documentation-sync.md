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
- **Status**: Done
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
- **Verification**: `python -m unittest discover -s .github/skills/agnos-docs-sync/tests`: 12 tests, 0 failure. `SkillTest`: the skill is a maintainer skill whose body names the four documents, "Keep a Changelog", "Unreleased", "maintainer", `changes_since.py`, "never commit" and the ban on unsupported statements; the `.claude/skills` pointer has the same name and description and points to the canonical file; AGENTS.md and CLAUDE.md do not list it. `AgentTest`: `.claude/agents/agnos-docs-sync.md` has model haiku, tools within Read, Grep, Glob, Edit, Bash (no Write), a prompt that sends it to the skill, names the four files and says never commit, never push, only these four files. Not run end to end: the agent was not launched on the repository.
- **Assumptions**: the skill is a maintainer skill like `agnos-demo`: not listed in `AGENTS.md` or `CLAUDE.md`.

### TASK-DOC-003: First run of the sub-agent on the repository
- **Tier**: S
- **Status**: Done
- **Description**: Run the `agnos-docs-sync` sub-agent on the repository and keep its edits of `CHANGELOG.md` and
  `GETTING_STARTED.MD` (an `[Unreleased]` section from 81 commits; the Quality wording in the trace stage).
- **Requirement refs**: RQ-DOC-003
- **ADR refs**: None
- **Acceptance Criteria**: Given the sub-agent run, Then only the four documents differ and nothing is committed by it.
- **Dependencies**: TASK-DOC-002
- **Assignee**: AI
- **Verification**: N/A (Tier S). After the run `git status` showed only CHANGELOG.md and GETTING_STARTED.MD modified; AGENTS.md and CLAUDE.md needed nothing.
- **Assumptions**: None

### TASK-DOC-004: The sub-agent defined once, in .github
- **Tier**: M
- **Status**: Done
- **Description**: Move the sub-agent's definition to `.github/agents/`, read by GitHub Copilot, and leave in `.claude/agents/` a pointer with what Claude Code requires.
- **Requirement refs**: RQ-DOC-003, RQ-MTA-008
- **ADR refs**: None
- **Acceptance Criteria**: Given the test suite, Then the criteria of RQ-DOC-003 as amended hold; Given the release rehearsal, Then neither file is delivered and it exits 0; Given a new Claude Code session, Then the agent is offered and runs on Haiku.
- **Dependencies**: TASK-DOC-002
- **Assignee**: AI
- **Verification**: `agnos-meta-docs-sync/tests` 16 OK, `agnos-meta-demo/tests` 12 OK, `agnos-meta-release/tests` 42 OK, 5 of these failing before the change. Rehearsal on a throwaway clone of these files: 62 files delivered, both agent files left out, both checks true, exit 0. The new session is the owner's check, not run yet.
- **Assumptions**: the agent stays undelivered, as approved by the owner; the definition leaves out `model`, since Copilot's values were not verified, and the pointer sets Haiku; the Copilot tool aliases come from its documentation, not yet run.
