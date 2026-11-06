# FTR-DOC-001: Documentation Sync Sub-Agent
<!-- Amended on 2026-10-31: the skill, its script and its outputs carry their current names (RQ-TRC-104, RQ-TRC-105, DEC-TRC-055). -->

## Overview
The repository's entry-point documents drift from the code: `CHANGELOG.md` lists what changed in releases, `AGENTS.md`
and `CLAUDE.md` tell an agent which skills exist and how to use them, `GETTING_STARTED.MD` walks a user through the
process. Each is edited by hand, long after the change that made it stale (the changelog's last entry predates six
features). This feature gives the maintainer a small, cheap helper: a **skill** that lists, for each of these four
documents, what changed in the repository since the document was last changed, and a **Claude Code sub-agent on the
Haiku model** that reads that list and updates the four documents accordingly, without committing. The maintainer reviews
the result and commits it through the usual workflow.

Out of scope: running the sub-agent automatically (a hook or a schedule), editing any other document, and deciding a
release number.

## Stakeholders
- **Owner**: the repository owner (maintainer of AGNOS).
- **Consumers**: the maintainer, who runs it before a release; readers of the four documents; agents that load
  `AGENTS.md` and `CLAUDE.md` at the start of a session.

---

## Functional Requirements

### RQ-DOC-001: What changed since each document's last change
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the skill's report script is run on a repository, it SHALL print, for each of `CHANGELOG.md`,
  `AGENTS.md`, `CLAUDE.md` and `GETTING_STARTED.MD`, the commit that last changed it and the non-merge commits made since,
  each with its subject and its changed files, leaving out the commits that touch only generated or session files
  (`process/INDEX.idx.md`, `process/_sessionstate/`); and SHALL list the repository's skills with their name, their
  description and whether they are maintainer skills.
- **Rationale**: a model told exactly what changed, document by document, neither re-reads the history nor guesses.
- **Priority**: Must
- **Acceptance Criteria**: Given a repository where `CHANGELOG.md` was last changed by commit A and two commits followed,
  one of them touching only `process/INDEX.idx.md`, When the report is run, Then it gives A as the changelog's last change
  and the other commit only, with its files; Given a document that was never committed, Then its last change is null and
  every commit is listed.
- **Dependencies**: None
- **Amended by**: RQ-PLG-022 — the fourth document is `agnos-init`'s template `AGNOS-GETTING-STARTED.md`, in place of `GETTING_STARTED.MD`.

### RQ-DOC-002: Rules for each document
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The skill SHALL state, for each of the four documents, what the update changes and what it leaves alone:
  the changelog gets entries under an "Unreleased" heading in the Keep a Changelog format, from the commits since its
  last change, without touching a released section; `AGENTS.md` and `CLAUDE.md` list a skill when it is added and drop it
  when it is removed, never a maintainer skill; `GETTING_STARTED.MD` changes only the passages that describe a behaviour
  the commits changed; and no document gets a statement that no commit or file supports.
- **Rationale**: an updater without rules rewrites style, invents features or lists a maintainer tool as a process skill.
- **Priority**: Must
- **Acceptance Criteria**: Given the skill's procedure, When it is read, Then it names the four documents, the changelog
  format, the maintainer-skill exclusion and the ban on unsupported statements.
- **Dependencies**: RQ-DOC-001
- **Amended by**: RQ-PLG-022 — the rules given to `GETTING_STARTED.MD` apply to `agnos-init`'s template `AGNOS-GETTING-STARTED.md`.

### RQ-DOC-003: A cheap sub-agent that edits and never commits
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The repository SHALL provide a sub-agent, defined once in `.github/agents/` (amended on 2026-10-31, TASK-DOC-004) with a
  pointer for Claude Code on the Haiku model, that follows the skill, reads the report, edits only the four documents, and ends with a
  summary of what it changed in each and what it left; it SHALL have no tool to commit, push or write another file.
- **Rationale**: the work is mechanical and frequent, so it runs on the cheapest model; the maintainer keeps the commit. Claude Code has no documented path to `.github/agents/`, hence its pointer.
- **Priority**: Must
- **Acceptance Criteria**: Given the Claude Code pointer, When it is read, Then its model is haiku, its tools are limited
  to reading, searching, editing and shell for read-only git, it names the definition, and it holds none of its procedure; Given the definition,
  Then its prompt sends it to the skill, And its name and description are the pointer's; Given the skill, Then it is
  discoverable under `.claude/skills/` and its canonical procedure stands under `.github/skills/`.
- **Dependencies**: RQ-DOC-001, RQ-DOC-002

---

## Non-Functional Requirements

### RQ-DOC-004: Reproducible report
- **Category**: Non-Functional
- **NFR Type**: Maintainability
- **EARS Type**: Ubiquitous
- **Statement**: The report script SHALL be Python 3.9 or later with the standard library only, SHALL give the same output
  for the same repository, and SHALL declare every repeated literal as a named constant.
- **Metric**: two runs on one repository give equal output; the script has no repeated literal.
- **Measurement Method**: a test that runs the script twice on a temporary repository and compares; the literal test of
  the agnos-perf-center skill applied to the script.
- **Priority**: Should
- **Acceptance Criteria**: Given a temporary repository, When the script runs twice, Then the outputs are equal.
- **Dependencies**: RQ-DOC-001
