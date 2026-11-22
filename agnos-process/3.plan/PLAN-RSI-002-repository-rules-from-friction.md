# PLAN-RSI-002: Repository rules from friction metrics

## Overview
Turns the friction of session TRC of 2026-11-22 into two rules of this repository, kept in `agnos-process/project-rules.md`
and read by every agent through `CLAUDE.md` and `AGENTS.md`. The declared improvement target (DEC-RSI-002) is unchanged
(owner, 2026-11-22).

## References
- **Requirements**: RQ-PLG-018, RQ-RSI-001
- **ADRs**: None

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-RSI-007: Add repository rules from session friction
- **Tier**: M
- **Status**: Done
- **Description**: Create `agnos-process/project-rules.md` with the rules on moving code between skills and on the plan split, and make `CLAUDE.md` import it and `AGENTS.md` say to read it after the instructions file.
- **Requirement refs**: RQ-PLG-018, RQ-RSI-001
- **ADR refs**: None
- **Acceptance Criteria**:
  - Given `agnos-process/project-rules.md`, Then each rule cites the METRICS_LOG row that motivates it
  - Given `CLAUDE.md` and `AGENTS.md`, Then the first imports the file And the second says to read it after the instructions file
  - Given `layout.py --check` and the budget script, Then the first has 0 findings And the second exits 0 with an unchanged target
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `project-rules.md` re-read: two rules, each citing METRICS_LOG 2026-11-22 TRC; `CLAUDE.md` imports it after the instructions file, `AGENTS.md` section 1 says to read it; `layout.py --check` 0 findings; `budget.ps1` exit 0, `target=.github/instructions/agnos-sw-eng.instructions.md ceiling=400 lines=395 left=5`; suites `agnos-meta-release`, `agnos-self-improvement`, `agnos-meta-docs-sync` OK. No unit test: no code.
- **Assumptions**: None
