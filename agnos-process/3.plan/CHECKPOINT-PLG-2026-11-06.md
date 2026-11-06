# Checkpoint PLG — 2026-11-06 <!-- PLAN-PLG-006, PLAN-PLG-005; ADR-PLG-006, ADR-PLG-005 -->

## Completed
- PLAN-PLG-006 done: TASK-PLG-038 to TASK-PLG-047, commits `3f9357d` to `55f52f0` on `feature/PLG`, local only, no push.
- The process folder is `agnos-process/`, its index `process.idx.md`, declared once in
  `.github/skills/agnos-init/assets/layout.json`; `layout.py --write` (in `agnos-meta-release/scripts/`) regenerates the copies,
  `--check` refuses a differing copy, a layout name in a delivered script, or an undeclared path in the delivered Markdown.
- The generated process skill is `agnos-instructions`.

## Key decisions
- ADR-PLG-006 Accepted (owner, 2026-11-06).
- RQ-MTA-013 and RQ-PLG-010 amended (owner): the standard library and the modules of the script's own `scripts/` folder,
  nothing to install. RQ-HST-015 unchanged: the perf center's history gets the friction log's path from its caller.

## Open
- TASK-PLG-007 (PLAN-PLG-001) In Progress, unchanged.
- ADR-PLG-005 Proposed; PLAN-PLG-005 (TASK-PLG-032 In Progress, TASK-PLG-033 to TASK-PLG-037 Not Started) is next, in a new
  session; its files now go under `agnos-process/` (the plan's paths may need the new names).

## Blockers
- None.
