# PLAN-DMO-003: Agent collaboration in the demo history

## Overview
Give the demo's history agent co-authors and a few agent-only commits, so that the History view of the Performance
Center shows humans and agents working together. The engine gains agent identities and the `with` key, the scenario
assigns them, `verify` checks them; the rebuild itself is TASK-DMO-018 (PLAN-DMO-004).

## References
- **Requirements**: RQ-DMO-023, RQ-DMO-024, RQ-DMO-025; amended RQ-DMO-011, RQ-DMO-014; RQ-DMO-021; RQ-HST-005, RQ-HST-030
- **ADRs**: ADR-DMO-002 (DEC-DMO-008, DEC-DMO-009); ADR-DMO-001 (DEC-DMO-002, DEC-DMO-005)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-DMO-015: Support agent identities in the replay engine
- **Tier**: L
- **Status**: Done
- **Description**: Accept ADR-DMO-002; give `replay.ps1` the `kind` and `trailer` of an identity and the `with` key of a
  step, with its refusals (DEC-DMO-008); give `verify.ps1` the checks of RQ-DMO-023 to RQ-DMO-025 and the agent
  exemptions of RQ-DMO-011 and RQ-DMO-014; document both in `SKILL.md`.
- **Requirement refs**: RQ-DMO-023, RQ-DMO-024, RQ-DMO-025, RQ-DMO-011, RQ-DMO-014
- **ADR refs**: ADR-DMO-002 (DEC-DMO-008), ADR-DMO-001 (DEC-DMO-002, DEC-DMO-005)
- **Acceptance Criteria** (Gherkin): Given a three-step scenario in a scratch folder with a step `with` Claude Code and a
  step `by` `Copilot SDK in VS Code/auto`, When it is replayed, Then the first commit ends with the Claude Code trailer
  and the second has `Copilot SDK in VS Code/auto` as author and committer and no trailer; Given `with` on a merge, `with` naming a human, or an agent `by`
  adding a file, Then the replay fails naming the step and writes nothing more; Given the current scenario, When
  `build` runs, Then the history is byte-identical to before (no step uses the new keys yet).
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `test_replay_agents.py` 6 tests failed 5 before the change, OK after; skill suite 18 OK, 0 skipped. HEAD's
  scenario and content replayed by the old and the new engine: both `c95238e`, 84 commits. `verify.ps1 -SkipRebuild` on
  the current demo: no script error, RQ-DMO-024 and RQ-DMO-025 PASS, RQ-DMO-023 and RQ-DMO-026 FAIL as expected before
  TASK-DMO-016 to TASK-DMO-018.
- **Assumptions**: an agent's trailer is built from its identity's name and e-mail, not a separate field; the
  RQ-DMO-026 check is added to `verify.ps1` here, beside RQ-DMO-023 to RQ-DMO-025, since it reads the same Performance
  Center run.

### TASK-DMO-016: Assign agents in the demo scenario
- **Tier**: M
- **Status**: Done
- **Description**: Add the Claude Code and Copilot agent identities to `scenario.json`, set `with` on the commits of
  `omar-arch`, `nina-dev`, `rob-ux` (Claude Code with Opus, Sonnet and Haiku 5.5, per DEC-DMO-009) and `paul-dev`, `john-qa`
  (`Copilot SDK in VS Code/auto`), add 3 to 6 steps by `Copilot SDK in VS Code/auto` alone that edit committed files on
  working days, every agent named `<Harness>/<Model>` (RQ-HST-030), and state in the demo's README that the agents are simulated.
- **Requirement refs**: RQ-DMO-023, RQ-DMO-024, RQ-DMO-025, RQ-DMO-009
- **ADR refs**: ADR-DMO-002 (DEC-DMO-009)
- **Acceptance Criteria** (Gherkin): Given the scenario, When its steps are counted, Then the non-merge steps with
  `with` are 40% to 70%, those without it by a human at least 20%, Claude Code and Copilot co-author at least 5 each,
  Opus and Sonnet at least 3 each, Haiku 1 or 2, and the agent-only
  steps are 3 to 6, none adding a file; Given the README, Then its first section says the agents are simulated.
- **Dependencies**: TASK-DMO-015
- **Assignee**: AI
- **Verification**: scenario replayed into a scratch folder, 88 commits; `verify.ps1 -SkipRebuild` on it: RQ-DMO-023 PASS (83
  non-merge: together 38 = 46%, human alone 41 = 49%, agent alone 4; Claude Code 23: Opus 10, Sonnet 11, Haiku 2; Copilot
  15; 4 agents counted), RQ-DMO-024, RQ-DMO-025 PASS (Copilot merged into one identity), RQ-DMO-009, RQ-DMO-011,
  RQ-DMO-014, RQ-DMO-017 PASS; RQ-DMO-001 and RQ-DMO-010 FAIL only from the scratch location without `build.ps1`.
- **Assumptions**: each of the four Copilot-only commits adds the missing requirement comment of one test, the test file
  being first committed without it by an `edits` draft; both READMEs (initial and web) carry the agents' notice.
