# Checkpoint 2026-11-23, session TRC

Written under CONTEXT MANAGEMENT rule 1, during PLAN-TRC-026 (graph explorer). Session state: tri TRC, tests true, platform
windows. The owner ordered on 2026-11-23 to implement every task of the plan and commit each ("fais le plan et implémente").

## Completed tasks
- TASK-TRC-130 (L) `117c828`, `a92a72c`: FTR-TRC-014 (RQ-TRC-142 to RQ-TRC-158), ADR-TRC-025 Accepted (DEC-TRC-084 to DEC-TRC-093), PLAN-TRC-026; 13 features and ADRs aligned.
- TASK-TRC-131 (L) `0430d39`: graph file in `4.knowledge/graph/agnos-graph.json` (layout `graphFile`).
- TASK-TRC-132 (L) `eeaab0e`: performance center outputs `perf-center.html`, `.json`, `.data.js` (layout `perfCenterPage`).
- TASK-TRC-133 (L) `988ece2`: `agnos-graph --explorer` writes `graph-explorer.html` and `agnos-graph.data.js`; `scripts/explorer.py`, `assets/explorer/` (template, CSS, JS, tokens); tables, detail panel, splitters, file loading.
- TASK-TRC-134 (M) `dd43616`: Cytoscape graph view (column per type, draggable, zoom, fit, hide, isolate, widen with circle layout); AGNOS brand mark in the header (owner's request).

## Open tasks
- TASK-TRC-135 query language and facets; TASK-TRC-136 saved query buttons; TASK-TRC-137 call graph and history in the explorer; TASK-TRC-138 verification on repository and demo, changelog.

## Blockers
None. Pre-existing failures, not caused by the plan, reported to the owner: `agnos-session/tests/test_session.py` imports `history` from the perf center's scripts (moved to agnos-graph); `agnos-meta-demo` `test_citations` finds RQ IDs as text in `agnos-perf-center/references/data-format.md`.

## Key decisions
- Option A: the explorer copies the perf center's token values and Cytoscape record; no file shared.
- Visibility (hidden types, hidden nodes, isolated set) is one state read by every view (`isShown`); the facets of TASK-TRC-135 set `hiddenTypes`.
- Shown graph nodes are read from the `hidden` class: Cytoscape caches `visible()`.
- Test hooks: `window.agnosExplorer` (`showView`, `select`, `loadText`, `hideTypes`, `hide`, `unhide`, `isolate`, `widen`, `showAll`, `counts`, `graph.*`).
- The owner edited `.github/instructions/agnos-sw-eng.instructions.md` (Mermaid diagrams with clear titles); it is left out of the task commits.

## Practical notes
- Explorer tests: `python -m unittest discover -s .github/skills/agnos-graph/tests -p test_explorer.py` (headless Edge; graph view tests need cdnjs).
- Long suites (perf center about 8 min, demo build about 2.5 min) run in a subagent, model sonnet, effort low.
