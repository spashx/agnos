# FTR-PLG-003: The Process Speaks to a Plugin User

## Overview
In a project using the AGNOS plugin, the process and its skills name only what that project has, and tell the user plainly what to do.

Source: the owner's full Claude Code session of 2026-11-04 on a new repository, `agnos-trial`, installed from the marketplace rehearsed at
`2afc76e`. The session reached `commit-task` as the procedure says, but:
- its end proposed adding rules to the plugin's process file, which an update of the plugin overwrites;
- the process named itself `agnos-sw-eng.instructions.md`, a file the project does not have;
- `agnos-init` ended with "start a new session", which reads as an AGNOS session while it means a new conversation of the tool;
- the owner needed the agent to tell them the steps of a first session: nothing in the project said what AGNOS lets them do;
- the user's guide, `GETTING_STARTED.MD`, sat at the root of this repository, where it reads as a guide to developing the process;
- the README mixed the plugin user's steps, the process's concepts and this repository's map.

Out of scope, by the owner's decision of 2026-11-04: what `commit-task` stages, the project's `.gitignore`, and commits made outside a
task (`METRICS_LOG.md`, the output of `agnos-init`, which runs outside an AGNOS session).

## Stakeholders
- **Owner**: the repository owner (maintainer of AGNOS).
- **Consumers**: developers using the AGNOS plugin in their projects, and their agents.

---

## Functional Requirements

### RQ-PLG-018: Self-improvement goes into the project's own rules file
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: The block `agnos-init` writes in `CLAUDE.md` and `AGENTS.md` SHALL tell the agent to read `process/project-rules.md` when it exists and SHALL name that file as the target of the process's improvements; WHILE the project's AGNOS block names such a target, the process SHALL direct a recursive self-improvement follow-up to it, creating it if absent, and SHALL NOT direct it to a file of the plugin. Amends RQ-PLG-004: the block holds no path outside the project.
- **Rationale**: on 2026-11-04 the agent proposed to edit the plugin's process file, which the next update of the plugin overwrites; a dedicated file keeps the project's rules apart from what the developer writes in `CLAUDE.md` and `AGENTS.md`.
- **Priority**: Must
- **Acceptance Criteria**: Given the process skill the release generates, Then its RECURSIVE SELF-IMPROVEMENT section makes the target the file the AGNOS block names, this file otherwise, And its END SESSION step refers to that target; Given this repository, whose `CLAUDE.md` holds no block, Then the target stays the process file; Given a project, When `agnos-init` runs, Then both blocks tell the agent to read `process/project-rules.md` when it exists, name it as the improvement target, And name no path outside the project.
- **Dependencies**: RQ-PLG-003, RQ-PLG-004, RQ-INI-001

### RQ-PLG-019: The process names itself without its repository file name
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The process instructions SHALL refer to themselves as "this file", without the file name `agnos-sw-eng.instructions.md`, so that the generated process skill names no file the project lacks.
- **Rationale**: the line budget named `agnos-sw-eng.instructions.md`, which a plugin user's project does not have; the release replaces the path, not the bare name.
- **Priority**: Should
- **Acceptance Criteria**: Given the process skill the release generates, Then it does not contain `agnos-sw-eng.instructions.md`.
- **Dependencies**: RQ-PLG-003

### RQ-PLG-020: After init, two separate steps
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN `agnos-init` succeeds, its skill SHALL tell the user, as two separate steps, first to open a new conversation in their tool so that it reads the block, then to ask the agent, in that conversation, to start an AGNOS session.
- **Rationale**: "start a new session so the agent loads the block", followed by the process's own sessions, read as one AGNOS session started twice.
- **Priority**: Should
- **Acceptance Criteria**: Given `agnos-init`'s SKILL.md, Then its success step names a new conversation of the tool and, as a second step, an AGNOS session, And it does not say "new session" for the conversation.
- **Dependencies**: RQ-INI-009

### RQ-PLG-021: A getting-started file written by init
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN `agnos-init` runs on a project, it SHALL write `AGNOS-GETTING-STARTED.md` at the project's root, the user's guide to AGNOS, stating the steps a user takes after the install: a new conversation in the tool, starting an AGNOS session, asking for a first feature, approving its task, the task's commit, ending the session, and the perf center; and it SHALL report the file as `created`, `updated` or `unchanged`, as it reports the block.
- **Rationale**: after `agnos-init` the user does not know what AGNOS lets them do; on 2026-11-04 the owner needed those steps from the agent to run a first session. The `AGNOS-` prefix keeps a `GETTING_STARTED.MD` of the developer's own untouched.
- **Priority**: Should
- **Acceptance Criteria**: Given a project without the file, When `agnos-init` runs, Then `AGNOS-GETTING-STARTED.md` is created and reported `created`; Given the file with other content, When it runs, Then the file is rewritten and reported `updated`; Given the same file, Then nothing is written and it is reported `unchanged`; Given the Windows and the Linux scripts, Then they write the same bytes; Given the file, Then it names each step of the statement, And holds no path outside the project.
- **Dependencies**: RQ-INI-001, RQ-PLG-020

### RQ-PLG-022: The user's guide lives in the init's template only
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The repository SHALL hold the user's guide only as `agnos-init`'s template `AGNOS-GETTING-STARTED.md`, reworded from the former `GETTING_STARTED.MD` for a user of the plugin, and SHALL hold no `GETTING_STARTED.MD` at its root; `agnos-meta-docs-sync` SHALL keep that template up to date in place of `GETTING_STARTED.MD`, under the same rules; and `README.md` SHALL send the user to the file `agnos-init` writes. Amends RQ-DOC-001, RQ-DOC-002 and RQ-INI-007 on the guide's location.
- **Rationale**: a guide for plugin users at the root of the repository where the process is developed reads as a guide to that repository; one guide, written into each project, avoids two versions.
- **Priority**: Should
- **Acceptance Criteria**: Given HEAD, Then no `GETTING_STARTED.MD` is at the root, And the template walks the steps of RQ-PLG-021 with a worked example; Given a rehearsal, Then the marketplace holds no `GETTING_STARTED.MD` at its root and no link to it, And the template inside the `agnos-init` skill; Given `agnos-meta-docs-sync`, Then its fourth document is the template; Given the suites of `agnos-meta-docs-sync`, `agnos-meta-release` and `agnos-meta-demo`, Then they pass.
- **Dependencies**: RQ-PLG-021, RQ-DOC-001, RQ-DOC-002, RQ-INI-007

### RQ-PLG-023: The README is a landing page for a plugin user
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: `README.md` SHALL hold, in this order, what AGNOS is, what it provides, its requirements per platform (the AI tool and the settings of it AGNOS relies on (amended on 2026-11-07, TASK-PLG-049), git, the shell of the scripts, Python and its version for the skills that need it, and which dependencies are fetched automatically or installed by the user), and how to get started (install the plugin, call `agnos-init`, open a new conversation and ask for an AGNOS session, read `AGNOS-GETTING-STARTED.md`), and SHALL name `COMPATIBILITY.md`; it SHALL NOT hold what was tested, how a session runs, the process's concepts or the map of this repository. What was tested, per tool and system, SHALL be stated in `COMPATIBILITY.md` at the root, delivered in the marketplace, and nowhere else; how a session runs and the concepts are the guide's; the map is `CONTRIBUTING.md`'s. Amends RQ-PLG-008 on where what was tested is stated.
- **Rationale**: on 2026-11-04 the owner found the README silent on what to install, Python above all, and mixing the plugin user's steps, the process's concepts, a state that changes with each check, and this repository's map. The changelog only says what each release holds, and the guide is copied into projects, so neither carries what was tested.
- **Priority**: Should
- **Acceptance Criteria**: Given `README.md`, Then its second-level headings are, in order, "What AGNOS Provides", "Requirements", "Getting Started" and "License", And its Requirements section names git, PowerShell 5.1, bash, Python 3.9 and `requirements-callgraph.txt` as installed by the user, And the VS Code settings `chat.useAgentsMdFile` and `chat.useAgentSkills` (amended on 2026-11-07, TASK-PLG-049), And it names `COMPATIBILITY.md`, And it says nothing of what was tested, And it holds no "What was tested", "How a Session Runs", "Core Concepts", "Continuous Improvement" or "Repository Map"; Given `COMPATIBILITY.md`, Then it says macOS and Codex are not tested; Given a rehearsal, Then the marketplace holds `COMPATIBILITY.md`; Given `CONTRIBUTING.md`, Then it holds the repository map; Given the guide, Then it holds the table of artifacts and the identifier format `<TYPE>-<TRI>-<NNN>`.
- **Dependencies**: RQ-PLG-008, RQ-PLG-022, RQ-INI-007

### RQ-PLG-047: README overview illustration content
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The README's overview image `assets/agnos-overview.png` SHALL show the brand and its tagline "Agentic efficiency by traceability", the agentic loop under human control, the five views of the Performance Center, why AGNOS holds at scale, and the get-started steps, SHALL hold no identifier of the demo other than one traceability example, and no outdated claim; its SVG sources SHALL be kept in `assets/` and SHALL NOT be delivered.
- **Rationale**: on 2026-11-15 the owner found the former image dated (cloning, a test template, a verbosity setting, a project-size limit) and silent on the Performance Center; one image must explain AGNOS at a glance.
- **Priority**: Should
- **Acceptance Criteria**: Given `README.md`, Then its image link leads to `assets/agnos-overview.png`; Given `assets/agnos-overview-AC-v2.svg`, the source of the PNG, Then it parses as XML, And holds no `BKG` identifier other than the traceability example, And none of "git clone", "verbosity", "small to medium", "self-contained"; Given a rehearsal, Then the marketplace holds the PNG and no `assets/*.svg`, And the agnos-meta-release suite passes.
- **Dependencies**: RQ-PLG-023, RQ-PLG-008
