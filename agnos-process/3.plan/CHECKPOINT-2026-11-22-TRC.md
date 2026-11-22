# Checkpoint 2026-11-22, session TRC

Written under CONTEXT MANAGEMENT rule 1 (context pressure), at the owner's request, before TASK-TRC-117.

## Completed tasks
- TASK-PLG-092 (L) `748eeb4`: `layout.json` declares `0.facts`, `4.knowledge` and `process_indexed`; `agnos-index` scans `process_indexed` only.
- TASK-PLG-093 (M) `6412cef`: `agnos-init` creates `0.facts/` and `4.knowledge/` with their readme.
- TASK-PLG-094 (L) `ee2a762`: the folders described in the instructions (395 lines), `AGENTS.md`, the guide, `CONTRIBUTING.md`.
- TASK-PLG-095 (M) `5ba0077`: demo rebuilt and verified (28/28), suites green.
PLAN-PLG-014 is done (FTR-PLG-010, ADR-PLG-010 Accepted).

## Open tasks
PLAN-TRC-023 (FTR-TRC-011, RQ-TRC-129 to RQ-TRC-133; ADR-TRC-022 Accepted, DEC-TRC-074 to DEC-TRC-077), all Not Started:
TASK-TRC-117 (L), TASK-TRC-118 (L), TASK-TRC-119 (M), TASK-TRC-120 (M), TASK-TRC-121 (M), TASK-TRC-122 (M). Start with TASK-TRC-117.

## Blockers
None.

## Key decisions (owner, 2026-11-22)
- "Fact" names the content of `0.facts/` only; the content of `agnos-graph.json` is the project's **state**.
- The graph holds only the state (elements, edges, files, task tiers, call graph, history, delivery); coverage, findings and
  quality stay in `agnos-perf-center`.
- Skill name `agnos-graph`; graph at `agnos-process/4.knowledge/agnos-graph.json`, declared as `graphFile` in the layout.
- `agnos-perf-center` runs `agnos-graph` only when the graph is absent or `--rebuild` is given.
- Tests: new graph-file tests and the pure unit tests of `callgraph`/`history` go to `agnos-graph/tests`; page tests stay in
  `agnos-perf-center` and load the moved modules from `agnos-graph/scripts`. The perf-center tests are highly cross-imported
  (`test_perf_center.generate`, `rendered_dom_after`, `BROWSER`; `test_history` helpers used by page tests).
- Long suites (perf-center about 8 min, meta-release about 2.5 min, demo build) run in a subagent, model sonnet, effort low.
- Count lines with `[IO.File]::ReadAllLines(...).Count`: `Measure-Object -Line` skips blank lines.
