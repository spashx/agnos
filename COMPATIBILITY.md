# Compatibility

<!-- RQ-PLG-008, RQ-PLG-009, RQ-PLG-023 / DEC-PLG-006, DEC-PLG-018 -->
What was tested of the plugin `agnos`, per tool and system, and what was not. Each row states only what was observed; this file is
updated after each check.

| Tool or system | Result |
|---|---|
| Claude Code, Windows | Installed from a local folder; `agnos-init` and `agnos-index` run; the block loads the process; an agent found and run. A full session on a new repository ran as the process says, with a marketplace built before `AGNOS-GETTING-STARTED.md`: START SESSION with its question, the index and the branch, a requirement and a plan, the task approved, test first, `commit-task`, the end of the session, and `agnos-perf-center`. |
| GitHub Copilot CLI, Windows | Installed from a local folder; `agnos-init` and `agnos-index` run; the block loads the process on a work question, not on a trivial one; an agent found and run. A full session is not tested yet. |
| GitHub Copilot in VS Code | Not tested. |
| OpenAI Codex | Not tested: its catalogue and manifest follow its documentation. |
| Linux | Scripts and their tests pass on Ubuntu 24.04, except the tests that need a browser or tree-sitter, not run there. No agent tool was run on it. |
| macOS | Not tested: it shares the Linux scripts. |
| Install from a remote Git repository | Not tested. |

**Scripts for:** Windows (PowerShell 5.1), Linux and macOS (bash).
