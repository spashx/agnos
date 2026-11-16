# Contributing to AGNOS

<!-- RQ-DOC-005, RQ-DOC-006 / TASK-DOC-005 -->

AGNOS is developed with AGNOS. Every requirement, decision, plan and line of code in this repository was
produced by following the process this repository defines. The same rule applies to you:

> **A pull request is accepted only if it was made with AGNOS.**

This is not a formality. The process is the product, and a change to it that skipped it cannot be checked
against it. If you want to contribute, run the process on your own change, as the maintainers do.

By participating, you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).

## What you can do without AGNOS

Only pull requests need AGNOS. You are welcome, without it, to:

- report a bug or propose a feature, with the [issue template](.github/ISSUE_TEMPLATE.md);
- discuss a design in an issue before writing any code;
- report a security issue, privately: see [SECURITY.md](SECURITY.md). Never open a public issue for it.

## What "made with AGNOS" means

The rule covers every change, however small: a typo fix is a Tier S task. In your fork:

1. **Open your agent on the repository.** GitHub Copilot and Claude Code both load the process from
   [`AGENTS.md`](AGENTS.md) and [`CLAUDE.md`](CLAUDE.md). Read the [README](README.md) and the
   [user's guide](.github/skills/agnos-init/assets/templates/AGNOS-GETTING-STARTED.md) first: they show
   a whole session.
2. **Start a session.** Ask the agent to start one. It asks you a trigram `<TRI>` and whether tests run,
   then the `agnos-git-workflow` skill creates the branch `feature/<TRI>` from `dev`. Reuse an existing
   trigram when your change belongs to its area; otherwise pick a new one.
3. **Write the requirement first.** New or changed behaviour is a requirement (EARS statement, Gherkin
   criteria) in `agnos-process/1.requirements/`. A cross-cutting choice is an ADR with its decisions in
   `agnos-process/2.architecture/`. The work is planned as tasks in `agnos-process/3.plan/`.
4. **Let every task be tiered and approved.** The agent presents each task (tier S, M or L) and waits for
   your approval before the first edit.
5. **Commit through the skill.** Commits come from `agnos-git-workflow commit-task`, which validates the
   artifact IDs, regenerates the index and computes the message. A hand-typed `git commit` is not accepted.
6. **Close the session.** The agent summarises it and appends the friction-metrics row to
   `agnos-process/_sessionstate/METRICS_LOG.md`. That row is part of your pull request.

Any agent that follows these steps is fine. What matters is the result, which a reviewer can see.

## How a reviewer checks it

A pull request is declined, with the reason given, when one of these is visible:

- a commit that does not follow the `commit-task` format, or has no task and requirement ID;
- a code or documentation change with no requirement, task or plan under `agnos-process/`;
- an artifact without its ID, or a code file that does not cite its requirement in a comment;
- a hand-edited `agnos-process/process.idx.md`, which only the `agnos-index` skill writes;
- a task never presented, tiered or approved, or tests missing for a Tier M or L task;
- no friction-metrics row for the session.

The [`agnos-perf-center`](.github/skills/agnos-perf-center/SKILL.md) skill produces the traceability matrix
that shows these gaps. You can run it on your branch before opening the pull request.

## Branches

| Branch | Role | Who pushes |
|---|---|---|
| `feature/<TRI>` | Working branch of one session | You, in your fork |
| `dev` | Validation: where pull requests land and are checked | Maintainers, by merging |
| `release` | Snapshots of releases only | Maintainers, at release time |

Open your pull request against `dev`, never against `release`.

## The layers of this repository

<!-- RQ-MTA-004 / ADR-MTA-001 (DEC-MTA-002, DEC-MTA-003) -->

AGNOS is developed with AGNOS, so this tree holds three layers:

| Layer | What it holds | Delivered |
|---|---|---|
| **Toolkit** | The instructions file, the process skills (the user's guide among `agnos-init`'s templates), `README.md`, `COMPATIBILITY.md`, `CHANGELOG.md`, `LICENSE.md` | Yes, in the marketplace |
| **Public repository** | `SECURITY.md`, `CODE_OF_CONDUCT.md`, this file, the GitHub templates | No: they address this repository's contributors |
| **Meta** | `agnos-process/`, `CLAUDE.md`, `AGENTS.md`, `.claude/`, the `agnos-meta-*` skills and sub-agents, the tests of every skill | No |

A skill or sub-agent that serves only the development of AGNOS takes the prefix `agnos-meta-`. The prefix is the
only criterion: tools read it, and no list of names is kept.

## Repository map

<!-- RQ-PLG-023 / DEC-PLG-018 -->

| Path | Content |
|---|---|
| [.github/instructions/agnos-sw-eng.instructions.md](.github/instructions/agnos-sw-eng.instructions.md) | The normative process, delivered as the skill `agnos-instructions` |
| [.github/skills/](.github/skills/) | The skills: `agnos-init`, `agnos-index`, `agnos-git-workflow`, `agnos-design-system`, `agnos-self-improvement`, `agnos-perf-center`, and the `agnos-meta-*` maintainer skills |
| [.github/skills/agnos-init/assets/templates/AGNOS-GETTING-STARTED.md](.github/skills/agnos-init/assets/templates/AGNOS-GETTING-STARTED.md) | The user's guide, a worked session, written into each project by `agnos-init` |
| [README.md](README.md), [COMPATIBILITY.md](COMPATIBILITY.md), [CHANGELOG.md](CHANGELOG.md) | The plugin user's landing page, what was tested, what each release holds |
| [agnos-process/](agnos-process/) | AGNOS's own requirements, decisions and plans |

## Rules that come with the process files

These apply on top of the process, to a change in the instructions file, the skills or their scripts:

1. **Read before editing.** Don't change a file you haven't read in full: the process enforces the same rule on the agent.
2. **Keep the two entry points in sync.** GitHub Copilot and Claude Code share one canonical instructions file and one
   canonical `agnos-git-workflow/SKILL.md` under `.github/`; the `.claude/` copies are thin pointers. Don't fork the content.
3. **Respect the instructions-file line budget.** `agnos-sw-eng.instructions.md` stays at or under 400 lines. If your
   change would exceed it, trim an existing section in the same change, and state the new line count in the task's `Verification`.
4. **Keep traceability in comments, not prose.** Cite requirement, ADR and decision IDs in comments of the files under
   `.github/`, never in their normative text.
5. **Keep the two script flavours equivalent.** The PowerShell and bash versions of a script stay exit-code-equivalent.
6. **Ask for a quality report on code you changed.** The `agnos-meta-qa` skill reports on Python and JavaScript as JSON, for
   you or your agent to correct before the pull request. You call it: no hook runs it and it blocks nothing. <!-- RQ-QLT-001, RQ-QLT-008 -->

## Pull requests

Use the [pull request template](.github/PULL_REQUEST_TEMPLATE.md). It asks what the process already holds: what changed, why, which requirement,
ADR and task IDs, and how it was verified. A pull request that touches the instructions file states its new line count.

## Code of Conduct

This project and everyone participating in it is governed by the [Code of Conduct](CODE_OF_CONDUCT.md).
Report unacceptable behavior as described there.
