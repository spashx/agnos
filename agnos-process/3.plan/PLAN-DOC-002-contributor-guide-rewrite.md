# PLAN-DOC-002: Contributor guide rewrite

## Overview
Implement RQ-DOC-005 and RQ-DOC-006 in one task: replace `CONTRIBUTING.md` with the rewritten guide that states the rule
"a pull request is accepted only if it was made with AGNOS" and the branch roles.

## References
- **Requirements**: RQ-DOC-005, RQ-DOC-006
- **ADRs**: None (Tier M task)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-DOC-005: Rewrite contributor guide
- **Tier**: M
- **Status**: Done
- **Description**: Replace `CONTRIBUTING.md` with the rewritten guide: the acceptance rule, what "made with AGNOS" means in six
  steps, the grounds on which a reviewer declines, what needs no AGNOS, the branch roles, and the existing sections on the
  repository's layers, map and process-file rules.
- **Requirement refs**: RQ-DOC-005, RQ-DOC-006
- **ADR refs**: None
- **Acceptance Criteria**: Given the rewritten `CONTRIBUTING.md`, When a contributor reads it, Then the rule, the six steps,
  the grounds of refusal, the exemption for issues and security reports, and the roles of `feature/<TRI>`, `dev` and
  `release` are all stated; Given the guide's links, Then each one resolves to an existing file or folder of the repository.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: re-run link check on `CONTRIBUTING.md`: 14 relative links, 0 missing (incl. `.github/ISSUE_TEMPLATE.md`, `.github/PULL_REQUEST_TEMPLATE.md`). Re-read sections: rule quote, "What you can do without AGNOS" (issues, discussions, private security report), six numbered steps, six grounds of refusal, branch table (`feature/<TRI>`, `dev`, `release`; PR targets `dev`), kept layers, map and process-file rules. Tests: none (session `tests` false, documentation only); skipped 0 run.
- **Assumptions**: the session runs with `tests` false (documentation only, no function written); the new IDs are the next
  free of the `DOC` prefix per the index; the rewrite keeps the layers table, the repository map and the process-file rules
  of the former guide; `.github/ISSUE_TEMPLATE/` and the pull request template are named as in the former guide.
