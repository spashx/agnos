# Checkpoint: Session MTA and INI, closed on 2026-10-31

Read this first when resuming. <!-- PLAN-MTA-001, PLAN-INI-001 / ADR-MTA-001, ADR-INI-001 -->

## State
- **Branch**: `feature/TRC`, kept for this work at the owner's request. Local only: it has no upstream.
- **Standing constraint**: push nothing until the owner lifts it (DEC-MTA-004).
- **Last task commit**: `5bed371`. Demo rebuilt beside this repository at HEAD `2ca06f3`, 23 checks of 23.
- **Open tasks**: none. PLAN-MTA-001 and PLAN-INI-001 are entirely Done.

## Completed
| Task | Tier | Result |
|---|---|---|
| TASK-MTA-001 | L | Meta skills renamed `agnos-meta-*`; the prefix is the only criterion |
| TASK-MTA-002 | M | The three layers stated in `CONTRIBUTING.md` |
| TASK-MTA-003 | L | The demo holds the project only; skills run on it from this repository |
| TASK-INI-001 | L | `agnos-init`: PowerShell and bash scripts, templates, one test suite for both |
| TASK-INI-002 | M | The call stated in `agnos-index`'s error, START SESSION, `README.md`, `GETTING_STARTED.MD` |
| TASK-INI-003 | L | The demo is an initialised project |

## Key decisions
- One repository, three layers: toolkit, public repository, meta (DEC-MTA-001, DEC-MTA-002).
- A release is the output of a build, and `main` receives snapshots, not merges (DEC-MTA-004).
- A project holds no toolkit: a block in `CLAUDE.md` and `AGENTS.md` points to it (DEC-MTA-006, DEC-INI-002, DEC-INI-005).
- No implicit setup and no `SessionStart` hook: `agnos-init` is an explicit, scripted call (DEC-INI-001).
- The toolkit path is a mandatory input, written as given, preferably relative (DEC-INI-004).

## Not yet validated
1. No agent session has been run in the demo: nothing proves an agent follows the block to the end, including the skill paths.
2. Claude Code may ask for approval when `CLAUDE.md` imports a file outside the project. This is unverified, and it would touch the owner's determinism requirement.
3. `init.sh` and the `agnos-index` bash version ran under Git Bash on Windows only, not on Linux or macOS.
4. The demo's `verify` assumes this repository's folder is named `agnos-lightweight-process`, beside the demo.

## Next steps, none approved yet
1. Run a real session in `agnos-lightweight-process.demo` and record what happens (points 1 and 2 above).
2. Plan `agnos-meta-release --dry-run` (DEC-MTA-004): select the delivered layers, remove the IDs found in the workshop's index, leave examples such as `RQ-EXP-001`, and fail on any defined ID left. Its requirements are still to write.
3. Afterwards, the `plugin` target (DEC-MTA-005, DEC-INI-005): how the installed path reaches `agnos-init` is still to design, since it is probably neither relative nor stable across versions.
4. When publishing: `dev` and `origin/dev` have diverged, and `dev`'s 5 commits hold nothing to recover. The recommendation is a new branch name rather than a force push.

## Practices to keep
For every skill, follow the documented practices: a focused capability, a description of what and when within 1,024 characters, `SKILL.md` under 500 lines, references one level deep, and no `disable-model-invocation` on a skill the process invokes. Use `skill-creator` when writing one.
