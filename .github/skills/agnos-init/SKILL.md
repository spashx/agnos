---
name: agnos-init
description: "AGNOS process initialisation skill. Adds AGNOS to a project by completing its CLAUDE.md and AGENTS.md with one delimited block and creating its process/ folders, without touching what the developer wrote. USE FOR: adding AGNOS to a new or existing repository, updating the block after AGNOS changes, or whenever agnos-index reports that process/ is missing."
argument-hint: "<project folder> <toolkit path as seen from the project>"
---

<!-- RQ-INI-001 to RQ-INI-006, RQ-INI-009 / ADR-INI-001 (DEC-INI-001 to DEC-INI-004) -->
# AGNOS Init

A script does all the work, so that the same call always gives the same files: do not write or edit
the block yourself. `<skill-folder>` is the folder holding this file. <!-- RQ-PLG-005 -->

## Procedure

1. Get both inputs from the user if they did not give them: the project folder, and the toolkit's path as
   seen from that folder. Prefer a relative path (`../agnos-lightweight-process`), because the block is
   committed and has to hold in other clones.
2. Run the script matching the platform, with its path taken from the toolkit:

   | Platform | Command |
   |---|---|
   | Windows | `powershell -NoProfile -File <skill-folder>/scripts/init.ps1 -Target <project> -Toolkit <path>` |
   | Linux / macOS | `bash <skill-folder>/scripts/init.sh --target <project> --toolkit <path>` |

   Use `powershell` (Windows PowerShell 5.1), never `pwsh`: PowerShell 7 is not guaranteed to be installed.

3. Check the exit code:
   - `0`: done. Report each line to the user, then tell them to start a new session so the agent loads the block.
   - `1`: error, nothing written. Report the message. For a damaged block, the user repairs its lines: do not guess its limits.

## What it does

| State of `CLAUDE.md` or `AGENTS.md` | Action | Reported |
|---|---|---|
| Absent | Creates it with the block alone | `created` |
| Without a block | Adds the block at the end | `added` |
| With a block that differs | Replaces only the block | `updated` |
| With the same block | Writes nothing | `unchanged` |
| With a damaged block | Stops before any write, naming the file | Exit 1 |

Every byte outside the block is preserved, and the block takes the file's line ending. It also creates
each folder of `process/` that is absent, with a `readme.md` saying what it holds. It changes nothing else in the project.

To update a project after AGNOS changes, call it again.

## Layout

| Path | Role |
|---|---|
| `scripts/init.ps1`, `scripts/init.sh` | The two versions, giving the same bytes |
| `assets/templates/` | One block per entry-point file; `{{TOOLKIT}}` is the only placeholder |
