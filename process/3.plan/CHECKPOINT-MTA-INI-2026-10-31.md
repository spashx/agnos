# Checkpoint: Sessions MTA, INI, QLT and TRC, refreshed on 2026-10-31

Read this first when resuming. <!-- PLAN-MTA-001, PLAN-INI-001, PLAN-INI-002, PLAN-QLT-001, PLAN-TRC-011, PLAN-TRC-013 / ADR-MTA-001, ADR-INI-001, ADR-QLT-001, ADR-TRC-011, ADR-TRC-013 -->

## State
- **Branch**: `feature/TRC`, kept for this work at the owner's request. Local only: it has no upstream.
- **Standing constraint**: push nothing until the owner lifts it (DEC-MTA-004).
- **Last task commit**: `3f15239`. Demo beside this repository at HEAD `17ede12`, 23 checks of 23 with `-SkipRebuild`, so RQ-DMO-021 skipped.
- **Open tasks**: none. All 150 indexed tasks are Done.

## Completed
| Task | Tier | Result |
|---|---|---|
| TASK-MTA-001 | L | Meta skills renamed `agnos-meta-*`; the prefix is the only criterion |
| TASK-MTA-002 | M | The three layers stated in `CONTRIBUTING.md` |
| TASK-MTA-003 | L | The demo holds the project only; skills run on it from this repository |
| TASK-INI-001 | L | `agnos-init`: PowerShell and bash scripts, templates, one test suite for both |
| TASK-INI-002 | M | The call stated in `agnos-index`'s error, START SESSION, `README.md`, `GETTING_STARTED.MD` |
| TASK-INI-003 | L | The demo is an initialised project |
| TASK-QLT-001 to TASK-QLT-007 | L, M, S | `agnos-meta-qa` writes a quality report on request; no open finding left |
| TASK-TRC-089 | L | `agnos-trace` renamed `agnos-perf-center` |
| TASK-INI-004 | L | The blocks order only to read the instructions; the user starts a session |
| TASK-IDX-003, TASK-TRC-090 | M | `agnos-index` and `agnos-perf-center` show the time a run took |
| TASK-TRC-091 | M | The Rework and Friction marks stand out from every background of Points over time |

## Key decisions
- One repository, three layers: toolkit, public repository, meta (DEC-MTA-001, DEC-MTA-002).
- A release is the output of a build, and `main` receives snapshots, not merges (DEC-MTA-004).
- A project holds no toolkit: a block in `CLAUDE.md` and `AGENTS.md` points to it (DEC-MTA-006, DEC-INI-002, DEC-INI-005).
- No implicit setup and no `SessionStart` hook: `agnos-init` is an explicit, scripted call (DEC-INI-001).
- The toolkit path is a mandatory input, written as given, preferably relative (DEC-INI-004).
- The blocks hold no `@` import: an order to read the instructions, and a session starts when the user asks (RQ-INI-010).

## Validated since the first checkpoint
- The owner ran two control sessions in the demo: asked to list the tasks, the agent only listed them; asked to start a session, it regenerated the index, wrote `session.yaml` and created the branch.
- The question of an approval for an `@` import is moot, as the blocks no longer import anything.

## Not yet validated
1. A change request in the demo with no open session: it relies on the existing branch rule, untested.
2. `init.sh` and the `agnos-index` bash version ran under Git Bash on Windows only, not on Linux or macOS.
3. The demo's `verify` assumes this repository's folder is named `agnos-lightweight-process`, beside the demo. Not checked again in this refresh.

## Next steps, none approved yet
1. Test point 1 above in `agnos-lightweight-process.demo`.
2. Plan `agnos-meta-release --dry-run` (DEC-MTA-004): select the delivered layers, remove the IDs found in the workshop's index, leave examples such as `RQ-EXP-001`, and fail on any defined ID left. Its requirements are still to write.
3. Test the bash scripts on Linux or macOS before the first release (point 2 above).
4. When publishing: `dev` and `origin/dev` are both at `a4d44fd`; it is `feature/TRC` that has diverged from them, 159 commits ahead and 5 behind. `dev`'s 5 commits hold nothing to recover. The recommendation is a new branch name rather than a force push.
5. Afterwards, the `plugin` target (DEC-MTA-005, DEC-INI-005): how the installed path reaches `agnos-init` is still to design, since it is probably neither relative nor stable across versions.

## Practices to keep
For every skill, follow the documented practices: a focused capability, a description of what and when within 1,024 characters, `SKILL.md` under 500 lines, references one level deep, and no `disable-model-invocation` on a skill the process invokes. Use `skill-creator` when writing one.
