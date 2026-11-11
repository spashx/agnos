# PLAN-PLG-009: Harness and model attribution in commits

## Overview
Name the agent's tool and model in the co-author trailer of each task commit, so the performance center tells which
tool and model made each change.

## References
- **Requirements**: RQ-HST-030, RQ-HST-005
- **ADRs**: None

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
