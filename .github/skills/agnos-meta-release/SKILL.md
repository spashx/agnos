---
name: agnos-meta-release
description: "AGNOS maintainer skill. Rehearses a release of this repository in a folder: selects the delivered layers of a commit, writes them as a marketplace holding the plugin agnos, removes the IDs of AGNOS's own development, checks none is left, and proves on the demo that the output behaves as the repository does. USE FOR: checking what a release would hold before deciding to publish. It publishes nothing: no commit on main, no tag, no push."
argument-hint: "--dry-run --output <folder> [--demo <folder>] [--repo <folder>]"
---

<!-- FTR-MTA-002; RQ-MTA-006 to RQ-MTA-013 / ADR-MTA-002 (DEC-MTA-007 to DEC-MTA-011); RQ-PLG-001 to RQ-PLG-003, RQ-PLG-007 / ADR-PLG-001 (DEC-PLG-001, DEC-PLG-002) -->
# AGNOS Release Rehearsal

Canonical procedure, shared by GitHub Copilot (`.github/skills/agnos-meta-release/`) and Claude Code
(`.claude/skills/agnos-meta-release/`, which points here). It is a **maintainer tool**: it serves the development of AGNOS and is
not delivered.

## Procedure

1. Commit first: the rehearsal reads the files tracked at HEAD and ignores the working tree. Build the demo with `agnos-meta-demo`
   if it is absent.
2. Run, from the repository root, on all platforms:

   ```
   python .github/skills/agnos-meta-release/scripts/release.py --dry-run --output <folder>
   ```

   `<folder>` must be outside the repository and empty. The report is written beside it, as `<folder>.report.json`. The demo is
   looked for beside the repository; `--demo <folder>` names another. Without `--dry-run` the script refuses: publishing does not exist yet.
3. Check the exit code:
   - `0`: every check passed. The last line gives the files, the IDs removed, the lines to read and the duration.
   - `1`: nothing is to be published. Each problem is on the error stream and in the report's `problems`. Report them to the maintainer.
4. Give the maintainer the report's `toRead` and `mentions`. They fail nothing: a person judges them.

## What it writes

| Path | What |
|---|---|
| `.claude-plugin/marketplace.json` | The catalogue read by Claude Code and Copilot |
| `.agents/plugins/marketplace.json` | The catalogue read by Codex |
| `plugins/agnos/plugin.json`, `plugins/agnos/.claude-plugin/plugin.json` | The manifests, with the version of the changelog's latest release |
| `plugins/agnos/skills/<name>/` | Each delivered skill |
| `plugins/agnos/skills/agnos-process/SKILL.md` | The process instructions as a skill, generated |
| `README.md`, `LICENSE.md`, `CHANGELOG.md`, `GETTING_STARTED.MD`, `agnos-overview.png`, `.gitignore` | From the repository |
| `.gitattributes` | The marketplace's own, from `assets/marketplace.gitattributes.txt` |

What the manifests say comes from `assets/marketplace.json`.

## What it checks

| Check | How | On failure |
|---|---|---|
| Every tracked file has a layer | `assets/layers.json`, and the prefix `agnos-meta-` for skills and sub-agents | Exit 1 before writing anything: add a rule |
| No ID of the repository is left | Reads the output: contents, binary files and paths | Exit 1, with file and line |
| The output behaves as the repository | Parses its Python, JSON, JavaScript, PowerShell and bash; compares what `agnos-index`, `agnos-perf-center` and `agnos-init` write | Exit 1, naming the file or the skill |
| Claude Code accepts the marketplace | `claude plugin validate --strict` on the plugin and the catalogue, with `claude` on the PATH or named by `AGNOS_CLAUDE`; its absence is said on the error stream | Exit 1, with the end of its output |
| The plugin has what it needs | The instructions file and a released version in `CHANGELOG.md` at HEAD | Exit 1 before writing anything |

An ID belongs to the repository when its trigram appears in the commit's `process/INDEX.idx.md`, defined there or not. Examples
such as `RQ-EXP-001` use another trigram, and stay: keep it that way when writing an example.

The comparison uses the demo through a temporary clone, so the demo does not change. A language whose parser is absent is said on the error stream and not parsed.

## The report

| Key | Holds |
|---|---|
| `commit` | The commit rehearsed |
| `delivered`, `leftOut` | The files of each side |
| `removed` | The IDs removed per file |
| `toRead` | Lines a removal may have left reading badly; some are false alarms. Correct a real one by rewording it in the repository |
| `mentions` | Mentions of `agnos-meta-` or of a test the release leaves out |
| `idsOutsideComments` | IDs the commit's Markdown shows outside a comment, which the traceability rule forbids |
| `checks`, `problems` | Each check's result, and what failed |

## Tests

`python -m unittest discover -s .github/skills/agnos-meta-release/tests -v` from the repository root. One test rehearses this repository on the
demo, reads HEAD, and is skipped when the demo is not built.
