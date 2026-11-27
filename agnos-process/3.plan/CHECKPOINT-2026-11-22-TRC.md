# Checkpoint 2026-11-22, session TRC

Written under CONTEXT MANAGEMENT rule 1, at the owner's request, before the perf center reads the graph's `links` block.
Next session's subject: support of `links` in `agnos-perf-center`. This file gives the context only, no solution: the
requirements, decision and plan are to be written in that session.

## Completed tasks
- TASK-TRC-127 (M) `759359e`: FTR-TRC-013 (RQ-TRC-138 to RQ-TRC-141), ADR-TRC-024 Accepted (DEC-TRC-081 to DEC-TRC-083), PLAN-TRC-025.
- TASK-INI-020 (S) `92b66b4`: FTR-INI-003 (RQ-INI-022, RQ-INI-023), ADR-INI-004 Accepted (DEC-INI-016, DEC-INI-017), PLAN-INI-005.
- TASK-INI-021 (L) `1b6710f`: `agnos-init` converts `Requirements`/`ADRs` to `Requirement refs`/`ADR refs` in a plan's `## References`.
- TASK-INI-022 (L) `21cf6d1`: template, guide, 76 plans of this repository, 6 of the demo, 2 fixtures converted.
- TASK-TRC-128 (L) `644e58a`: `links` block in `graph.py`, documented in `agnos-graph/references/graph-format.md`.
- TASK-TRC-129 (M) `37af068`: graph minus `links` and perf center outputs byte-identical before and after, repository and demo.
PLAN-TRC-025 and PLAN-INI-005 are done.

## Open tasks
None. The perf center support of `links` has no FTR, RQ, ADR nor plan yet; FTR-TRC-013 put the perf center out of scope.

## Blockers
None.

## Key decisions (owner, 2026-11-22)
- The graph holds explicit links only: no link is removed, none is inferred. A feature and an ADR are linked only through
  the chain of their children (ADR → DEC → RQ ← FTR) or when one cites the other on its own lines; the owner finds that
  more readable than an implicit link.
- Typing applies to the links whose source is an RQ, a DEC, a TASK or a PLAN; features and ADRs keep untyped links (their
  templates hold no link field) and have no row in `links`.
- Link fields: RQ `Dependencies`; DEC `Requirement refs`, `Dependencies`; TASK `Requirement refs`, `ADR refs`,
  `Dependencies`; PLAN `Requirement refs`, `ADR refs` (under `## References`). Any other place is `text`.
- The decisions written before TASK-PLG-096 (181 of 194) cite their requirements in prose: their links are `text`. Their
  migration is a separate subject, not to be mixed with the typing (owner).

## Context for the perf center support
- **Graph file** (`agnos-process/4.knowledge/agnos-graph.json`): `edges` `[source, target, kind, proofs]`, `kind`
  `contains | refs | code`, `proofs` `[[line, text]]`, unchanged; `links` `[[source, target, [[line, field]]]]`, one row per
  `refs` edge of an RQ/DEC/TASK/PLAN source, in `edges` order, one field per proof line (an edge may mix fields and `text`).
- **What the perf center reads today** (DEC-TRC-075): `elements`, `edges`, `files`, `tasks` only; it ignores `sections`
  (DEC-TRC-078) and `links` (DEC-TRC-081).
- **Rules reading `refs` without regard to its origin**, in `agnos-perf-center/scripts/perf_center.py`:
  - `Links` (about line 157): `refs_out`/`refs_in` built from every `refs` edge.
  - `rate` (about line 186, RQ-TRC-008, DEC-TRC-004): a requirement is `indirect` when a `refs` neighbour or a `contains`
    ancestor of type DEC, TASK, ADR, PLAN or FTR (`COVERING_TYPES`) is cited in code.
  - `is_untasked` (RQ with no TASK citing it), `is_adr_without_rq` (ADR or its DECs citing no RQ), `refs_to_type`, the
    `task-no-rq` rule; the rule keys are `RULE_KEYS`; the quality score is in `scorecard.py`, the rules in `references/rules.md`.
  - `tasks.requirements` in the graph file: the requirement IDs a task cites, on any of its lines.
- **Page** (`agnos-perf-center/assets/matrix.js`): `EDGE_LOOK` (about line 642) gives one look per relation (`contains`,
  `refs` "cites", `code`, call graph kinds), from design-system tokens; the graph view walks the neighbourhood, one hop per
  level, both directions (`neighbourhood`, about line 881); the detail panel shows the proofs.
- **Measured on 2026-11-22**: this repository, 5073 `links` rows: `Requirement refs` 1565, `ADR refs` 1302, `Dependencies`
  1110, `text` 1989 (mostly the prose of the former DECs); the demo, 266 rows, `text` 21.
- **Tests to expect touched**: `agnos-perf-center/tests/test_callgraph.py` pins the fixture page's data hash
  (`DATA_BEFORE_PLAN_SHA256`, re-pinned at each intended data change, with a comment naming the task); the fixture
  `tests/fixtures/repo` of each skill; the demo's checks (`agnos-meta-demo/scripts/verify.ps1`, RQ-DMO-*), which read the
  perf center's figures (e.g. RQ-DMO-026 "Functions traced").
- **Requirements a change would touch** (to list under "Requirements handed to another component", project rule "Plan
  split"): RQ-TRC-008 (coverage rating), RQ-TRC-131 (perf center fed by the graph), RQ-TRC-141 (consumers unaffected by
  link fields, its metric names the perf center's data), the finding rules of FTR-TRC-001 and the scorecard of FTR-TRC-003.

## Open questions for the next session (owner's to answer)
- Which perf center results use the field: display only, coverage, findings, score, or several.
- Whether `text` links keep counting where they count today.
- What the page shows of a field: the edge's look, the detail panel, a filter.
- How the former DECs, all `text`, are treated, given their migration is a separate subject.

## Practical notes
- Long suites (perf-center about 7 min, demo build about 2.5 min) run in a subagent, model sonnet, effort low.
- Count lines with `[IO.File]::ReadAllLines(...).Count`: `Measure-Object -Line` skips blank lines.
- Run every command from the repository root: a `cd` into a skill folder moves the shell's working directory.
