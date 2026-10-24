# FTR-DMO-002: Simulated team and history

## Overview
The history of the demo repository (FTR-DMO-001) shows several people working over about two months. The
people are fictitious. Each one has a role (product owner, architect, developer, tester/QA, and a UX designer for
the interface, amended by the owner on 2026-10-24) readable in
their identity, so the history can be filtered by role. Dates follow human working time: no weekend, no
public holiday, working hours. As the history is simulated, the public holidays MAY be fictitious but
SHALL be declared in the demo.

## Stakeholders
- **Owner**: AGNOS process maintainer (this repository)
- **Consumers**: People reading the git history of the demo to see who does what in the process

---

## Functional Requirements

### RQ-DMO-011: Identities encode the role
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The demo history SHALL use at least 5 distinct identities named `<firstname>-<role>`, in
  lowercase, where `<role>` is `po` (product owner), `arch` (architect), `dev` (developer), `qa` (tester) or
  `ux` (UX designer, amended by the owner on 2026-10-24), with at least one identity per role among `po`, `arch`,
  `dev` and `qa`, and at least two `dev`; the e-mail of each identity SHALL start with the same
  `<firstname>-<role>`.
- **Rationale**: A fixed suffix lets anyone find the role of a person by filtering, with no other file.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** the demo history
  - **When** `git log --format=%an` is listed without duplicates
  - **Then** every name matches `^[a-z]+-(po|arch|dev|qa|ux)$`
  - **And** `git log --author=-qa` returns only commits of `qa` identities
- **Dependencies**: RQ-DMO-001

### RQ-DMO-012: Each role authors its own artifacts
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN an artifact is first committed, the demo history SHALL attribute it to the matching
  role: features and requirements to `po`, ADRs to `arch`, plans and production code to `dev`, and unit
  tests to `qa`; for each Tier M or L task, the commit of its tests SHALL precede the commit of its
  production code.
- **Rationale**: The history then shows who does what and the test-first rule of the instructions.
- **Priority**: Should
- **Acceptance Criteria** (Gherkin):
  - **Given** the demo history
  - **When** the first commit of each FTR, ADR, plan, source and test file is read
  - **Then** its author has the matching role suffix
  - **And** for every Tier M or L task the test commit is older than the production-code commit
- **Dependencies**: RQ-DMO-011, RQ-DMO-005

### RQ-DMO-013: Simulated dates on every commit
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: Every commit of the demo SHALL carry the simulated date as both its author date and its
  committer date, and its author and committer SHALL be the same identity.
- **Rationale**: Tools and filters read one or the other date; both must tell the same story.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** the demo history
  - **When** `git log --format=%ad%n%cd%n%an%n%cn` is read for each commit
  - **Then** author date equals committer date and author equals committer
- **Dependencies**: RQ-DMO-011

### RQ-DMO-014: Two months of irregular activity
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The demo history SHALL span 56 to 64 days between its first and last commit, contain at
  least 50 commits, and not show every identity on every working day: each identity SHALL commit on at
  least 5 days and on no more than 80% of the working days of the period.
- **Rationale**: Real teams are not all active every day; a flat pattern looks generated.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** the demo history
  - **When** the first and last commit dates and the active days per identity are computed
  - **Then** the span is between 56 and 64 days and there are at least 50 commits
  - **And** every identity is active on 5 or more days and on at most 80% of working days
- **Dependencies**: RQ-DMO-013

### RQ-DMO-015: No weekend and no public holiday
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: IF a date is a Saturday, a Sunday or a public holiday declared in the demo's calendar file,
  THEN the demo history SHALL NOT contain any commit on that date; the period SHALL include at least two
  declared public holidays on working days.
- **Rationale**: Human working time is the realism the demo is asked for; the holidays prove the rule.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** the demo history and its calendar file
  - **When** the commit dates are compared with weekends and the declared holidays
  - **Then** 0 commit falls on a Saturday, a Sunday or a declared holiday
  - **And** at least two declared holidays fall on a Monday to Friday inside the period
- **Dependencies**: RQ-DMO-014

### RQ-DMO-016: Commits in working hours
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: Every commit of the demo SHALL be dated between 09:00 and 18:00 in one time zone, the same
  for all commits and recorded in the dates' UTC offset.
- **Rationale**: A commit at 03:00 or with changing offsets breaks the working-time illusion.
- **Priority**: Should
- **Acceptance Criteria** (Gherkin):
  - **Given** the demo history
  - **When** the time and offset of each commit are read
  - **Then** every time is between 09:00 and 18:00
  - **And** the UTC offset is identical on all commits unless a declared daylight-saving change applies
- **Dependencies**: RQ-DMO-013

### RQ-DMO-017: History order follows the process order
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The demo history SHALL commit an artifact after the artifacts it depends on: requirements
  before the ADRs and plans citing them, plans before the code of their tasks, and no commit SHALL cite an
  ID whose definition is committed later.
- **Rationale**: A reader following the history must meet the process in the order the process defines.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** the demo history in chronological order
  - **When** each commit's cited IDs are checked against the definitions committed up to it
  - **Then** 0 commit cites an ID that is not yet defined
- **Dependencies**: RQ-DMO-005, RQ-DMO-013

### RQ-DMO-018: Commit messages and session branches follow the git workflow
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: Every task commit of the demo SHALL use the message format of the `agnos-git-workflow`
  skill, `<type>(<TRI>): <ADR-ID>/<TASK-ID> <description>`, and each session SHALL be developed on a
  `feature/<TRI>` branch merged into the default branch by a merge commit; the demo SHALL have at least 3
  such session branches.
- **Rationale**: The commit and branch conventions are part of the process being demonstrated.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** the demo history
  - **When** the task commit messages and the merge commits are listed
  - **Then** every task commit message matches the format of the skill
  - **And** at least 3 `feature/<TRI>` branches are merged into the default branch
- **Dependencies**: RQ-DMO-005

---

## Non-Functional Requirements

### RQ-DMO-019: The simulated history is a valid git history
- **Category**: Non-Functional
- **NFR Type**: Reliability
- **EARS Type**: Ubiquitous
- **Statement**: The demo history SHALL be a valid git repository in which no commit is dated after the
  day of its creation and no commit is dated before its parent.
- **Metric**: `git fsck` exit code 0; 0 commit dated in the future; 0 commit older than its parent.
- **Measurement Method**: `git fsck --strict`; `git log --format=%H %P %ct` compared line by line with the
  creation date.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** the finished demo repository
  - **When** `git fsck --strict` is run and the parent and child dates are compared
  - **Then** the exit code is 0
  - **And** 0 commit is dated after the creation day or before its parent
- **Dependencies**: RQ-DMO-013
