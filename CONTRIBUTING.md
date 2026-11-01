# Contributing to AGNOS

Thanks for taking the time to contribute. This repository defines the **AGNOS Software
Engineering Process** — the instructions, skills, and templates that an AI coding agent (GitHub
Copilot or Claude Code) follows. Read
[README.md](README.md) and [GETTING_STARTED.MD](GETTING_STARTED.MD) first if you haven't already;
they explain what the process does before you change how it does it.

By participating, you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).

## What you can contribute

- **Process changes** — edits to
  [`.github/instructions/agnos-sw-eng.instructions.md`](.github/instructions/agnos-sw-eng.instructions.md),
  the `agnos-git-workflow` skill, or the requirement/ADR/plan templates.
- **Documentation** — `README.md`, `GETTING_STARTED.MD`, this file, or comments inside the
  templates.
- **Tooling** — the `validate-ids` scripts (`.github/skills/agnos-git-workflow/scripts/`), kept
  exit-code-equivalent between the PowerShell and bash versions.

## The layers of this repository

<!-- RQ-MTA-004 / ADR-MTA-001 (DEC-MTA-002, DEC-MTA-003) -->

AGNOS is developed with AGNOS, so this tree holds three layers:

| Layer | What it holds | Delivered |
|---|---|---|
| **Toolkit** | The instructions file, the process skills, `README.md`, `GETTING_STARTED.MD`, `CHANGELOG.md`, `LICENSE.md` | Yes, in the marketplace |
| **Public repository** | `SECURITY.md`, `CODE_OF_CONDUCT.md`, this file, the GitHub templates | No: they address this repository's contributors |
| **Meta** | `process/`, `CLAUDE.md`, `AGENTS.md`, `.claude/`, the `agnos-meta-*` skills and sub-agents, the tests of every skill | No |

A skill or sub-agent that serves only the development of AGNOS takes the prefix `agnos-meta-`. The prefix is the
only criterion: tools read it, and no list of names is kept.

## Before you open a pull request

1. **Read before editing.** Don't propose a change to a file you haven't actually read in full —
   the same rule the process itself enforces on the agent.
2. **Keep the two entry points in sync.** GitHub Copilot and Claude Code share one canonical
   instruction file and one canonical `agnos-git-workflow/SKILL.md` under `.github/`; the
   `.claude/` copies are thin pointers. Don't fork the content between them.
3. **Respect the instructions-file line budget.** `agnos-sw-eng.instructions.md` must stay at or
   under 400 lines. If your change would exceed it, trim an existing section in the same change
   rather than deferring cleanup.
4. **Traceability stays in comments, not prose.** If you reference a requirement, ADR, or decision
   ID from process-definition files under `.github/`, keep the citation out of the file's own
   normative text — this is the convention this repository has settled on for its own process
   files (see recent history for the rationale).
5. **Ask for a quality report on code you changed.** The `agnos-meta-qa` skill reports on Python and JavaScript as JSON, for
   you or an agent to correct before the pull request. You call it: no hook runs it and it blocks nothing. <!-- RQ-QLT-001, RQ-QLT-008 -->
6. **If you're using this process to build a real feature** (not editing AGNOS itself), follow the
   full session workflow: open a session with a trigram, author the requirement, get the plan
   approved, then commit through the `agnos-git-workflow` skill's `commit-task` sub-command so the
   Conventional-Commits message is computed for you, not typed by hand.

## Commit messages

Whether or not you're running a full AGNOS session, commits in this repository follow
[Conventional Commits](https://www.conventionalcommits.org/) with a scope:

```
<type>(<scope>): <description>
```

`<type>` is one of `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `build`, `ci`,
`style`. `<scope>` is the trigram of the area touched (e.g. `GIT` for the git-workflow skill,
`REC` for process self-improvement work) or a short free-text scope for repo-wide changes (e.g.
`repo`). If your change implements a tracked `TASK-*`/`ADR-*` artifact, include its ID in the
description per the skill's own `commit-task` grammar.

## Pull requests

Use the PR template — it asks for the same traceability information the process asks of every
task: what changed, why, which requirement/ADR/task IDs (if any) it relates to, and how it was
verified. A PR that touches the instructions file should state its new line count.

## Reporting bugs and proposing features

Use the issue template. For a security issue, do **not** open a public issue — see
[SECURITY.md](SECURITY.md).

## Code of Conduct

This project and everyone participating in it is governed by the
[Code of Conduct](CODE_OF_CONDUCT.md). Report unacceptable behavior as described there.
