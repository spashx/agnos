# FTR-PLG-001: AGNOS Marketplace for Claude Code, GitHub Copilot and OpenAI Codex

## Overview
AGNOS reaches a project through one marketplace holding one plugin, `agnos`, installed from the tool the developer already uses.
The marketplace is an output of `agnos-meta-release`: this feature builds it in a local folder and proves it by a real install.
Publishing it is a later decision of the owner.

Source: the study `plugin-dual-harness-instructions.md` in this folder, checked against the official documentation and a throwaway
trial on 2026-10-31 (ADR-PLG-001, Context). What differs from the study is decided in ADR-PLG-001, Alternatives Considered.

Out of scope: pushing, publishing or listing in a public catalogue; hooks, MCP servers and commands, which AGNOS does not need; the
copy format of DEC-MTA-005, abandoned by the owner on 2026-10-31.

## Stakeholders
- **Owner**: the repository owner (maintainer of AGNOS).
- **Consumers**: developers installing AGNOS from Claude Code, GitHub Copilot (CLI and VS Code) or OpenAI Codex.

---

## Functional Requirements

### RQ-PLG-001: A marketplace target
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN `agnos-meta-release` is run with the marketplace target, it SHALL write to the output folder a marketplace holding the plugin `agnos`, without commit, tag or push.
- **Rationale**: the marketplace is built, never edited by hand, so it stays what the workshop holds.
- **Priority**: Must
- **Acceptance Criteria**: Given a commit of the workshop, When the target runs, Then the output holds the tree of DEC-PLG-001 and the repository has no new commit, tag or remote change.
- **Dependencies**: RQ-MTA-006, RQ-MTA-011

### RQ-PLG-002: One catalogue readable by the three tools
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The marketplace SHALL declare the plugin in `.claude-plugin/marketplace.json`, read by Claude Code and Copilot, and in `.agents/plugins/marketplace.json`, read by Codex; the plugin SHALL hold a root `plugin.json` with the Agent Plugins schema and a `.claude-plugin/plugin.json`, with the same name, version and description.
- **Rationale**: each tool has its documented place, and the trial showed the two manifests coexist.
- **Priority**: Must
- **Acceptance Criteria**: Given the output, When `claude plugin validate --strict` runs on the plugin and on the marketplace, Then both pass; Given the four files, Then name, version and description are equal.
- **Dependencies**: RQ-PLG-001

### RQ-PLG-003: The process delivered as a skill
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The plugin SHALL hold a skill `agnos-process` whose body is the content of the process instructions, generated when the marketplace is built.
- **Rationale**: a plugin's `CLAUDE.md` is not loaded, and a skill is what all three tools load from a plugin.
- **Priority**: Must
- **Acceptance Criteria**: Given the output, When `agnos-process/SKILL.md` is read, Then its body is the instructions file with the workshop's IDs removed, And it has a `name` and a `description`.
- **Dependencies**: RQ-PLG-001, RQ-MTA-009

### RQ-PLG-004: A block with no path
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: `agnos-init` SHALL write in `CLAUDE.md` and `AGENTS.md` a block that names the skill `agnos-process` and holds no path, and SHALL take no toolkit path as input.
- **Rationale**: a plugin's folder changes with each version, so a path written in a project would break at the next update.
- **Priority**: Must
- **Acceptance Criteria**: Given a project, When `agnos-init` runs, Then both blocks name `agnos-process`, And neither holds a path; Given a project with an earlier block, When it runs again, Then the block is replaced and every other byte is preserved.
- **Dependencies**: RQ-INI-002, RQ-INI-003, RQ-INI-006
- **Amended by**: RQ-PLG-018 — the block may name a path inside the project, `process/project-rules.md`; it holds no path outside it.

### RQ-PLG-005: Scripts found from the skill's own folder
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: Each delivered `SKILL.md` SHALL name its scripts and assets relative to its own folder, SHALL hold no `.github/skills/` path, no plugin root variable, and SHALL run its commands from the project's root.
- **Rationale**: in the trial this wording found the script in Claude Code and Copilot, and `${CLAUDE_SKILL_DIR}` was left empty by Copilot.
- **Priority**: Must
- **Acceptance Criteria**: Given the delivered `SKILL.md` files, When they are searched, Then none holds `.github/skills/` or `CLAUDE_`; Given an installed plugin and a project, When `agnos-index` runs, Then `process/INDEX.idx.md` is written in the project.
- **Dependencies**: RQ-PLG-001

### RQ-PLG-006: An agent defined once, delivered per tool
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE a delivered agent is defined in `.github/agents/<name>.agent.md`, the marketplace target SHALL generate `agents/<name>.md` for Claude Code and `com.github.copilot/agents/<name>.agent.md` for Copilot, translating its frontmatter by a table.
- **Rationale**: each tool reads a plugin's agents in one folder only, and frontmatter values differ, so a single source needs a generated output.
- **Priority**: Should
- **Acceptance Criteria**: Given a test agent with tools and a model, When the target runs, Then both files exist with that tool's values and the same body; Given a tool or value missing from the table, Then the build stops and names it; Given a Meta agent such as `agnos-meta-docs-sync`, Then it is not delivered.
- **Dependencies**: RQ-PLG-001, RQ-DOC-003

### RQ-PLG-007: The same proof as any release
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: IF the marketplace output holds an ID of AGNOS's development, or its skills write on the demo something other than the repository's skills, THEN the target SHALL fail and report it.
- **Rationale**: the guarantees of the rehearsal must hold for what users really install.
- **Priority**: Must
- **Acceptance Criteria**: Given the target's report, Then `noIdLeft` and `sameBehaviour` are true, measured on the marketplace's skills; Given an ID left in a test input, Then the target exits non-zero.
- **Dependencies**: RQ-MTA-009, RQ-MTA-010, RQ-MTA-011

---

## Non-Functional Requirements

### RQ-PLG-008: What is tested is stated
- **Category**: Non-Functional
- **NFR Type**: Portability
- **EARS Type**: Ubiquitous
- **Statement**: The delivered scripts SHALL run on Windows and Linux, and the marketplace's `README.md` SHALL state, per tool and system, what was tested and what was not.
- **Metric**: the delivered test suites pass on Windows and on Ubuntu 24.04 under WSL; macOS and Codex are stated as not tested until they are.
- **Measurement Method**: run of the suites on both systems; reading of the README.
- **Priority**: Must
- **Acceptance Criteria**: Given Windows and WSL, When the delivered suites run, Then they pass on both; Given the README, Then it says macOS and Codex are not tested.
- **Dependencies**: RQ-PLG-001

### RQ-PLG-009: A real install proves the marketplace
- **Category**: Non-Functional
- **NFR Type**: Reliability
- **EARS Type**: Event-driven
- **Statement**: WHEN a marketplace is built for delivery, it SHALL be installed from a clean git clone in Claude Code and Copilot, on a project with no AGNOS file, and carry out a session up to its first commit.
- **Metric**: `agnos-init`, `agnos-index` and `agnos-git-workflow` run from the installed plugin, in each tool.
- **Measurement Method**: a session run by the owner on a copy of the demo, in an isolated tool configuration.
- **Priority**: Must
- **Acceptance Criteria**: Given a clean clone of the output, When it is added as a marketplace in a configuration with no other plugin, Then the session starts, reads the process, and commits one task.
- **Dependencies**: RQ-PLG-001 to RQ-PLG-005

### RQ-PLG-010: The proof can be run again
- **Category**: Non-Functional
- **NFR Type**: Maintainability
- **EARS Type**: Event-driven
- **Statement**: WHEN a maintainer runs the skill `agnos-meta-plugin-proof` on a built marketplace, it SHALL install it from a clean copy in a configuration isolated from the maintainer's, for each tool present, SHALL report per tool what it observed and what it did not, and, only when asked, SHALL put questions to the tools' models and run the delivered suites on Linux.
- **Metric**: a run changes neither the maintainer's tool configurations nor the marketplace; no model is called without its option.
- **Measurement Method**: unit tests on the commands and the isolation; a real run.
- **Priority**: Should
- **Acceptance Criteria**: Given a marketplace and no option, When the skill runs, Then it installs and lists the plugin in each tool present, calling no model; Given a tool absent, Then it says so and goes on; Given a failed install, Then it exits 1; Given a model that did not do what was asked, Then the report says not observed, without failing.
- **Dependencies**: RQ-PLG-009, RQ-MTA-002

### RQ-PLG-011: A skipped test is not a passed test
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: IF a test run skips tests, THEN the agent SHALL state their number and cause in the task's `Verification` field, and SHALL NOT present the skipped tests as passed.
- **Rationale**: a faulty CDN probe silently skipped 192 page tests during TASK-PLG-003 while the suite reported success.
- **Priority**: Should
- **Acceptance Criteria**: Given the instructions file, Then it holds the rule And it has at most 400 lines; Given the generated skill `agnos-process`, Then it holds the rule.
- **Dependencies**: None
