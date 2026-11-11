# PLAN-PLG-009: Harness and model attribution in commits

## Overview
Name the agent's tool and model in the co-author trailer of each task commit, so the performance center tells which
tool and model made each change.

## References
- **Requirements**: RQ-HST-030, RQ-HST-005
- **ADRs**: ADR-HST-003

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-PLG-063: Add agent co-author trailer
- **Tier**: M
- **Status**: Done
- **Description**: Add to `commit-task` the rule of one `Co-Authored-By: <Harness>/<Model> <e-mail>` trailer, as the tool gives them, `auto` for an unseen model; test first that the performance center classes such co-authors as agents.
- **Requirement refs**: RQ-HST-030, RQ-HST-005
- **ADR refs**: None
- **Acceptance Criteria**: Given a commit by an agent, When `commit-task` builds the message, Then it holds one single `Co-Authored-By: <Harness>/<Model> <e-mail>` trailer; Given a model the agent cannot see, Then `<Model>` is `auto`; Given "Claude Code/Claude Opus 5.5" and "Copilot SDK in VS Code/auto" trailers, When the history is built, Then each commit is "together" and the two are distinct agent identities.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: SKILL.md re-read: one-trailer rule, `auto`, message trailers at step 7 (RQ-HST-030). `test_history`: 46 run, 46 OK, 0 skipped, the new RQ-HST-030 test included; it passed with no code change, the agent patterns already matching both names. The trailer itself is checked on this task's own commit.
- **Assumptions**: The tool's own attribution is replaced by the skill's rule only; `settings.json` is left unchanged.

### TASK-PLG-064: Add commit-task script
- **Tier**: L
- **Status**: Done
- **Description**: Write `commit-task.ps1` and `commit-task.sh`, which build the commit message and its co-author trailer from arguments and run `git commit`, with a dry run for the confirmation; `commit-task` calls them.
- **Requirement refs**: RQ-HST-030, RQ-HST-005
- **ADR refs**: ADR-HST-003 (DEC-HST-013)
- **Acceptance Criteria**: Given valid arguments, When the script runs, Then the commit holds exactly one `Co-Authored-By: <Harness>/<Model> <e-mail>` trailer; Given a missing harness, model or e-mail, Then the exit code is 1 and nothing is committed; Given `-DryRun`, Then the message is printed and HEAD is unchanged; Given the same arguments, Then both versions give the same message.
- **Dependencies**: TASK-PLG-063
- **Assignee**: AI
- **Verification**: `test_commit_task`: 8 run, 8 OK, 0 skipped, both versions: one trailer, ADR subject, Iteration trailer, dry run leaves HEAD, missing/empty/invalid values exit 1 without commit, same bytes from ps1 and sh. SKILL.md steps 5-7 call the script; this task's own commit is made by it.
- **Assumptions**: The script stages nothing (explicit staging replaces `git add .`); it validates the IDs through `validate-ids`.
