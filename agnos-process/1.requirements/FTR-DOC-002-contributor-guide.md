# FTR-DOC-002: Contributor guide

## Overview
AGNOS is developed with AGNOS: every requirement, decision, plan and line of code of this repository was produced by
following the process it defines. A change to the process that skipped the process cannot be checked against it. This
feature makes `CONTRIBUTING.md` say so: a pull request is accepted only if it was made with AGNOS, and the guide tells a
contributor what that means, what a reviewer declines, and which branch to target.

The branch model is the owner's decision of 2026-11-16: `feature/<TRI>` working branches, `dev` as the validation and
default branch, `release` for snapshots of releases only. Aligning the other process documents, which still name `main`,
is out of scope of this feature.

Out of scope: the pull request template, the code of conduct, the security policy, and any check run by a tool on a pull
request.

## Stakeholders
- **Owner**: the repository owner (maintainer of AGNOS).
- **Consumers**: contributors who want to open a pull request; the maintainer, who reviews it.

---

## Functional Requirements

### RQ-DOC-005: Pull request acceptance rule
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The contributor guide SHALL state that a pull request is accepted only if it was made with AGNOS, SHALL list
  the steps that make a change "made with AGNOS" (session start, requirement first, tiered and approved tasks, commits
  through `commit-task`, session close with its metrics row), SHALL list the grounds on which a reviewer declines a pull
  request, and SHALL state that issues, design discussions and private security reports need no AGNOS.
- **Rationale**: a contributor who knows the rule before writing code does not lose a pull request to it.
- **Priority**: Must
- **Acceptance Criteria**: Given the guide, When a contributor reads it, Then it says that a pull request not made with
  AGNOS is not accepted, and that this covers every change however small; Given the guide, Then each of the six steps and
  each ground of refusal is listed; Given the guide, Then it says that a bug report, a proposal and a security report
  are welcome without AGNOS.
- **Dependencies**: None

### RQ-DOC-006: Branch role description
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The contributor guide SHALL state the role of the branches `feature/<TRI>`, `dev` and `release`, who may push
  to each, and that a pull request targets `dev`.
- **Rationale**: a contributor opens the pull request against the right branch the first time.
- **Priority**: Must
- **Acceptance Criteria**: Given the guide, When a contributor looks for where to open a pull request, Then it names `dev`
  and says that `release` is for the maintainers' release snapshots only; Given the guide, Then each of the three
  branches has its role and its authorised pushers.
- **Dependencies**: RQ-DOC-005
