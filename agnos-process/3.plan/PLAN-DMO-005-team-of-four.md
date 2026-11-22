# PLAN-DMO-005: Demo team of four at Acme

## Overview
Replace the demo's seven human identities by four people of the fictitious company Acme, `linda-pm`, `john-ux`,
`andy-tech` and `sachin-tech`, each working mostly with an agent, then rebuild and verify the demo (owner request of
2026-11-12).

## References
- **Requirement refs**: amended RQ-DMO-011, RQ-DMO-012, RQ-DMO-023; RQ-DMO-009, RQ-DMO-014, RQ-DMO-021, RQ-DMO-022
- **ADR refs**: ADR-DMO-001 (amended DEC-DMO-003, DEC-DMO-007); ADR-DMO-002 (amended DEC-DMO-009)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-DMO-019: Check the team of four in verify
- **Tier**: L
- **Status**: Done
- **Description**: Accept the amended DEC-DMO-003, DEC-DMO-007 and DEC-DMO-009; make `verify.ps1` check the roles
  `pm`, `ux` and `tech` (RQ-DMO-011), their artifacts (RQ-DMO-012), the `--author=-tech` filter of the README
  (RQ-DMO-009) and the share of agent commits per human and overall (RQ-DMO-023); update the skill's tests and
  `SKILL.md`.
- **Requirement refs**: RQ-DMO-011, RQ-DMO-012, RQ-DMO-023, RQ-DMO-009
- **ADR refs**: ADR-DMO-001 (DEC-DMO-003, DEC-DMO-007), ADR-DMO-002 (DEC-DMO-009)
- **Acceptance Criteria** (Gherkin): Given the current demo of seven people, When `verify.ps1 -SkipRebuild` runs, Then
  RQ-DMO-011, RQ-DMO-012 and RQ-DMO-023 FAIL naming the cause, with no script error; Given a demo of the four Acme
  identities, Then they PASS; Given the skill's tests, Then all pass.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `verify.ps1 -SkipRebuild` on the seven-people demo: 23 passed, 4 failed, no script error; RQ-DMO-009 FAIL
  (no `--author=-tech`), RQ-DMO-011 FAIL (7 of 4 identities, e-mails not `@acme.example` 7, pm=0, tech=0), RQ-DMO-012
  FAIL (e.g. `clock.py` by nina-dev, expected tech), RQ-DMO-023 FAIL (linda-po 0 %, sara-qa 0 %, paul-dev 57 %). The
  PASS on the four Acme identities is evidenced by TASK-DMO-020. Skill suite: 18 OK, 0 skipped.
- **Assumptions**: `verify.ps1` has no unit test of its own, so the before-run on the current demo stands as the failing
  test; the README filter example becomes `--author=-tech`; RQ-DMO-022 keeps its `-ux` check unchanged.

### TASK-DMO-020: Recast the demo scenario for Acme
- **Tier**: M
- **Status**: Done
- **Description**: In `scenario.json`, map the steps of `linda-po` to `linda-pm`, `rob-ux` to `john-ux`, `omar-arch`,
  `nina-dev` and `sara-qa` to `andy-tech`, `paul-dev` and `john-qa` to `sachin-tech`, with e-mails `@acme.example`;
  add `with` so each human has at least 60% of its commits with its agent (DEC-DMO-009); update both READMEs of the
  content library; rebuild the demo twice and verify it.
- **Requirement refs**: RQ-DMO-011, RQ-DMO-012, RQ-DMO-023, RQ-DMO-009, RQ-DMO-014, RQ-DMO-021
- **ADR refs**: ADR-DMO-001 (DEC-DMO-003, DEC-DMO-007), ADR-DMO-002 (DEC-DMO-009)
- **Acceptance Criteria** (Gherkin): Given the scenario, Then its human identities are the four of RQ-DMO-011 and the
  dates and contents of its steps are unchanged; Given the rebuilt demo, When `verify` runs, Then every line is PASS;
  Given two builds, Then both end on the same HEAD; Given `agnos-perf-center --history`, Then its summary counts 4
  humans and 4 agents.
- **Dependencies**: TASK-DMO-019
- **Assignee**: AI
- **Verification**: scenario rewritten by script (round-trip identical before the change, no old name or
  `agnos-demo.example` left, 14 `with` added on commits that had none, dates and contents unchanged). `build.ps1 -Verify`:
  replay 88 commits, HEAD `ef0041c`; verify 27 passed, 0 failed; RQ-DMO-011 4 of 4 (andy-tech, john-ux, linda-pm,
  sachin-tech), RQ-DMO-012 PASS, RQ-DMO-014 andy-tech=28, linda-pm=10, sachin-tech=20, john-ux=5 of 43 days, RQ-DMO-023
  together 52 (63 %), human alone 27 (33 %), agent alone 4, Opus 19, Sonnet 14, Haiku 2, Copilot 17, per human 64 % to
  68 %; RQ-DMO-021 second build same HEAD. `agnos-perf-center --history`: `history: 81 commits, 4 humans, 4 agents`.
- **Assumptions**: the generic "Product owner of Roombook" and "testers" of the demo's feature files are left as they
  are, being stakeholder wording, not identities; the initial README lists `pm` and `tech`, the UX designer joining in
  the later README as before; the 81 commits of the history line are the non-merge commits touching the scanned folders.
