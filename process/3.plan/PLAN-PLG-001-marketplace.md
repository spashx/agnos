# PLAN-PLG-001: AGNOS Marketplace

## Overview
Build the marketplace of FTR-PLG-001 locally and prove it by a real install. No push at any step. The order follows the risks: the wording
and the systems first, then the output, then the install.

## References
- **Requirements**: RQ-PLG-001 to RQ-PLG-011
- **ADRs**: ADR-PLG-001, ADR-MTA-001, ADR-MTA-002, ADR-INI-001

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-PLG-001: Feature, decisions and plan
- **Tier**: L
- **Status**: Done
- **Description**: Record the trial's results and the decisions, and mark what they amend in ADR-MTA-001 and ADR-INI-001.
- **Requirement refs**: RQ-PLG-001 to RQ-PLG-009
- **ADR refs**: ADR-PLG-001
- **Acceptance Criteria**: Given the owner's approval, Then ADR-PLG-001 is Accepted, And DEC-MTA-004, DEC-MTA-005, DEC-INI-003, DEC-INI-004 and DEC-INI-005 name what amends them; Given the index, Then it has no duplicate.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: ADR-PLG-001 Accepted; the five DECs each name what amends them (re-read in the edits); `agnos-index` on commit reports no duplicate.
- **Assumptions**: the trial's results stand for Copilot in VS Code until TASK-PLG-007.

### TASK-PLG-002: Skills name their files from their own folder
- **Tier**: L
- **Status**: Done
- **Description**: Rewrite the delivered `SKILL.md` files and the tests that read them, with no `.github/skills/` path and no plugin variable.
- **Requirement refs**: RQ-PLG-005
- **ADR refs**: ADR-PLG-001
- **Acceptance Criteria**: Given the delivered `SKILL.md` files, Then none holds `.github/skills/` or `CLAUDE_`; Given a project and a skill's script called from the project's root, Then its output lands in the project; Given the full suite, Then it passes.
- **Dependencies**: TASK-PLG-001
- **Assignee**: AI
- **Verification**: `test_skill_paths.py`: 2 wording tests failing before the rewrite, 4 OK after, the index and the perf center copied away write in the project only. Suites: meta-release 46, init 16, meta-demo 12, docs-sync 16, perf-center 364 OK (3 skipped), `test-build-index.ps1` all passed. Found and fixed on the way: with WSL running, `bash` on Windows is WSL's, which could not read the path given by `parse_error` in `release.py`; it now gets the bytes on its input (one first fix sent CRLF in text mode, seen in the test's output).
- **Assumptions**: agnos-init's own scripts and templates stay in `LEFT_TO_THE_BLOCK_TASK` until TASK-PLG-004.

### TASK-PLG-003: Delivered scripts on Linux
- **Tier**: M
- **Status**: Done
- **Description**: Run the delivered suites on Ubuntu 24.04 under WSL and fix what fails, including `python3` where only that name exists.
- **Requirement refs**: RQ-PLG-008
- **ADR refs**: ADR-PLG-001
- **Acceptance Criteria**: Given WSL, When the delivered suites run on a copy of the repository, Then they pass with the Windows results unchanged.
- **Dependencies**: TASK-PLG-002
- **Assignee**: AI
- **Verification**: Ubuntu 24.04, Python 3.12.3, git 2.43, no PowerShell, on a copy of the tree: `test-build-index.sh` all passed, `validate-ids.sh` 5 of 5 as expected, init 16 OK, skill paths 4 OK, perf-center 366 run OK with 237 skipped (no Chromium, no tree-sitter there, so the page and call-graph tests did not run on Linux). Windows: perf-center 366 run OK, 3 skipped. Real defects found: dates depended on git's version (`+00:00` before 2.46, `Z` after), now one form in `history.py`, with a test. Test defects found: `test_init` needed PowerShell, `RQ-TRC-062` had no browser guard, `RQ-TRC-081` called no browser when cdnjs was down, and the cdnjs probe read a redirect of its root as an outage, which had silently skipped 192 page tests.
- **Assumptions**: the page of `agnos-perf-center` is tested in a browser on Windows only, as the WSL image has none.

### TASK-PLG-004: The block with no path
- **Tier**: L
- **Status**: Done
- **Description**: `agnos-init` writes the block naming `agnos-process`, with no toolkit input; its requirements are amended, its two scripts and `agnos-meta-demo` follow, and the demo is rebuilt.
- **Requirement refs**: RQ-PLG-004, RQ-INI-001, RQ-INI-006, RQ-INI-008
- **ADR refs**: ADR-PLG-001, ADR-INI-001
- **Acceptance Criteria**: Given RQ-PLG-004's criteria, Then they hold on both scripts; Given the rebuilt demo, Then its checks pass.
- **Dependencies**: TASK-PLG-002
- **Assignee**: AI
- **Verification**: `test_init.py`: 20 failures and errors before the change, 16 OK after, on both scripts; meta-release 45, meta-demo 12, docs-sync 16 OK. Demo rebuilt by a background Haiku subagent: `verify` 23 passed, 0 failed, HEAD `36f221f`; its `CLAUDE.md` re-read: names `agnos-process`, holds no path; its tree is clean.
- **Assumptions**: the block adds one line the trial did not run: if the skill is not available, stop and tell the user to install the plugin. The scenario's `init` becomes `true`.

### TASK-PLG-005: The marketplace target
- **Tier**: L
- **Status**: Done
- **Description**: `agnos-meta-release` gains the target: tree, four manifests, generated `agnos-process`, the existing removal and proof applied to the output, `claude plugin validate --strict` when the binary is present.
- **Requirement refs**: RQ-PLG-001, RQ-PLG-002, RQ-PLG-003, RQ-PLG-007
- **ADR refs**: ADR-PLG-001, ADR-MTA-002
- **Acceptance Criteria**: Given RQ-PLG-001, RQ-PLG-002, RQ-PLG-003 and RQ-PLG-007's criteria, Then they hold on a real run from HEAD; Given the mentions in the report (`agnos-meta-` in delivered files), Then each is removed or read and kept.
- **Dependencies**: TASK-PLG-004
- **Assignee**: AI
- **Verification**: meta-release 61 OK, including `test_marketplace.py` and a rehearsal of this repository with `claude plugin validate --strict` on the plugin and the catalogue; demo checked to stay unchanged. A first real run gave 49 files, 1,088 IDs removed, `noIdLeft` and `sameBehaviour` true, and showed the instructions' own `applyTo` header in the skill, now removed with a test. Mentions read: `agnos-meta-` in `CHANGELOG.md`, which is history, and two perf test names in `references/maintaining.md`, which describes a maintainer's tests: both kept. The generation of agents is in this commit's code; TASK-PLG-006 proves it.
- **Assumptions**: there is one output, so no `--target` option: the rehearsal writes the marketplace. Plugin `agnos`, marketplace `agnos-marketplace`, version from `CHANGELOG.md`'s latest release, license AGPL-3.0-only as in `LICENSE.md`. `README.md` and `GETTING_STARTED.MD` address plugin users, and the build translates their links. The `.gitattributes` is the marketplace's own.

### TASK-PLG-006: Agents generated per tool
- **Tier**: M
- **Status**: Done
- **Description**: The target generates each delivered agent for Claude Code and Copilot from a table of frontmatter values, proved on a test agent.
- **Requirement refs**: RQ-PLG-006
- **ADR refs**: ADR-PLG-001
- **Acceptance Criteria**: Given RQ-PLG-006's criteria, Then they hold, And the test agent is run once from an install in each tool.
- **Dependencies**: TASK-PLG-005
- **Assignee**: AI
- **Verification**: `AgentTest` 4 OK, failing before the code. A marketplace built with a test agent, from a clean local clone: Claude Code lists it and its subagent `agnos:agnos-helper` returned `AGENT-MARKER-GENERATED` on Haiku; Copilot CLI, with no read tool, quoted the same from `--agent agnos:agnos-helper`. Found on the way, by the same proof: `init.ps1` failed on an absolute `-Target`, and the release passes one, so the comparison of `agnos-init` had compared two failures. Both fixed, with tests: the target is combined with the current folder, and `compare_runs` names a skill that fails from the workshop's own files.
- **Assumptions**: Codex receives no agent (DEC-PLG-005). The test agent is not in the repository: AGNOS delivers no agent today.

### TASK-PLG-008: The proof can be run again
- **Tier**: M
- **Status**: Done
- **Description**: The throwaway scripts of the trial and of the install proof become the maintainer skill `agnos-meta-plugin-proof`, asked for by the owner on 2026-11-01.
- **Requirement refs**: RQ-PLG-010
- **ADR refs**: ADR-PLG-001
- **Acceptance Criteria**: Given RQ-PLG-010's criteria, Then they hold; Given a real run on a built marketplace, Then each present tool installs it in an isolated configuration, And the maintainer's configurations do not change.
- **Dependencies**: TASK-PLG-005
- **Assignee**: AI
- **Verification**: `test_plugin_proof.py` 16 OK. Real run with `--with-models --linux` on a marketplace built from `cf28eb8`: exit 0; Claude Code and Copilot CLI each pass install, 6 skills of 6, init, process, index, agent, and Claude Code both validations; `linux-suites` pass (init 17, skill paths 4, perf-center 366 with 237 skipped, index all passed). `plugin list` of both tools equal before and after in the maintainer's configuration; the marketplace has no change.
- **Assumptions**: the test agent is added to the clean copy from a fixed text, not generated: `AgentTest` covers the generation.

### TASK-PLG-009: A skipped test is not a passed test
- **Tier**: M
- **Status**: Done
- **Description**: Recursive self-improvement, iteration 1/1: the `Verification` field states the tests skipped and why.
- **Requirement refs**: RQ-PLG-011
- **ADR refs**: None
- **Acceptance Criteria**: Given RQ-PLG-011's criteria, Then they hold.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: instructions file 383 lines, unchanged as the rule extends an existing line; `process_skill` output holds the rule; meta-release 63 OK, meta-demo 12 OK, 0 skipped. The demo suite also found a visible ID in `agnos-meta-plugin-proof/SKILL.md`, left by TASK-PLG-008, now in a comment.
- **Assumptions**: "1" read as theme 1, one iteration.

### TASK-PLG-007: Install proof and user documents
- **Tier**: M
- **Status**: In Progress
- **Description**: Install from a clean clone in Claude Code, Copilot CLI and VS Code, run a session up to its first commit, and write the install commands and the tested / not tested table in `README.md` and `GETTING_STARTED.MD`.
- **Requirement refs**: RQ-PLG-008, RQ-PLG-009
- **ADR refs**: ADR-PLG-001
- **Acceptance Criteria**: Given RQ-PLG-009's criteria, Then they hold in each tool on Windows; Given the README, Then every cell of the table states a result actually observed; Given the release, Then the final report's checks are true.
- **Dependencies**: TASK-PLG-006, TASK-PLG-003
- **Assignee**: Human (sessions), AI (the rest)
- **Verification**: Partial, the sessions are the owner's. Rehearsal from `be7793c`: 49 files, 1,090 IDs removed, both checks true, exit 0. Isolated install from a clean local clone: Claude Code and Copilot CLI list 6 skills, `claude plugin validate --strict` passes on both. Copilot CLI on a new project: `agnos-init`, `agnos-index` ran and wrote there, the block loaded `agnos-process`; its call of `validate-ids.ps1` was denied, with nobody to approve. Claude Code headless: its calls of the scripts were held for approval at first, then ran in `agnos-meta-plugin-proof` (TASK-PLG-008), which grants it `bash` and `python` too. Neither `file://`, `http://` from a dumb server nor `git://` could stand for a remote (DEC-PLG-007), so both tools read the folder in place and the per-version folder is not exercised. Not run: Copilot in VS Code, Codex, a tool on Linux, macOS. Owner's sessions on new repositories: Claude Code on 2026-11-04 (`agnos-trial`, marketplace of `2afc76e`) up to `commit-task` and the perf center; Copilot in VS Code on 2026-11-05 (`agnos-trial-copilot`, marketplace of `25869d8`, installed from Copilot CLI) up to commit `79538fe` and the perf center, `validate-ids` run for the trigram and the task; three departures recorded in `COMPATIBILITY.md`. Still open: a full session in Copilot CLI, and docs-sync on Haiku in a session of the owner's.
- **Assumptions**: a Linux run of a tool needs Claude Code or Copilot installed in WSL by the owner; without it the table states scripts tested, tool not run.
