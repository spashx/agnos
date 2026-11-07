# Changelog

All notable changes to this repository are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [3.2.0]

### Added
- `agnos-self-improvement` skill: the procedure of a recursive self-improvement effort, and `budget.ps1` / `budget.sh` giving the declared target's ceiling, line count and lines left; a rules file other than the instructions file gets 100 lines unless declared `at most <N> lines` <!-- ADR-RSI-001, TASK-RSI-002, TASK-RSI-003, RQ-RSI-001, RQ-RSI-003, RQ-RSI-004 -->
- `agnos-init` writes `AGNOS-GETTING-STARTED.md` at the project's root, the user's guide for a plugin user, and reports it created, updated or unchanged <!-- ADR-PLG-003, TASK-PLG-021, RQ-PLG-021, RQ-PLG-022 -->
- `agnos-meta-release` writes `<folder>.report.html` beside its JSON report: one self-contained page, its data embedded and escaped, drawn as text only, its styles from the perf center's design tokens <!-- ADR-PLG-002, TASK-PLG-015, TASK-PLG-016, RQ-PLG-016, RQ-PLG-017 -->
- `agnos-meta-release` checks the four manifests and catalogues by script, with no AI tool: required fields, plugin folders, the same name, version and description everywhere <!-- ADR-PLG-002, TASK-PLG-014, RQ-PLG-015 -->
- `agnos-meta-release` console: the problems, the lines to read, the mentions and the IDs outside comments, each with its file and line, and a last line giving `exit=` whatever the outcome <!-- ADR-PLG-002, TASK-PLG-013, RQ-PLG-014 -->
- `agnos-meta-plugin-proof` maintainer skill: proves a built marketplace by a real install in isolated Claude Code and GitHub Copilot configurations, on request with questions to their models and the delivered suites on Linux, publishing nothing <!-- ADR-PLG-001, TASK-PLG-008, RQ-PLG-010 -->
- `agnos-meta-release` writes a marketplace holding the plugin `agnos`, with its generated skill `agnos-process` and its agents, for Claude Code, GitHub Copilot and OpenAI Codex <!-- ADR-PLG-001, TASK-PLG-005, TASK-PLG-006, RQ-PLG-001, RQ-PLG-002, RQ-PLG-003, RQ-PLG-006, RQ-PLG-007 -->
- `agnos-meta-release` maintainer skill: rehearses a release in a folder, from a commit, without AGNOS's own IDs, and proves it behaves as the repository does, publishing nothing <!-- ADR-MTA-002, TASK-MTA-005 to TASK-MTA-008, RQ-MTA-006 to RQ-MTA-013 -->
- `agnos-index` and `agnos-perf-center` show on their output line the time the run took, never written into the generated files <!-- TASK-IDX-003, TASK-TRC-090, RQ-IDX-018, RQ-TRC-107 -->
- `agnos-meta-qa` maintainer skill: a code quality report on request, as normalised JSON from pinned analysers, blocking
  nothing <!-- ADR-QLT-001, TASK-QLT-001, RQ-QLT-001 to RQ-QLT-008 -->
- `agnos-init` skill: adds AGNOS to a project with one block in its `CLAUDE.md` and `AGENTS.md`, every other byte
  preserved, and its `process/` folders <!-- ADR-INI-001, TASK-INI-001, RQ-INI-001 to RQ-INI-006 -->
- `agnos-index` skill: the index generators (PowerShell and bash) with shared golden tests
  <!-- ADR-IDX-001, TASK-IDX-001 -->
- `agnos-index` skill packaged and integrated into the process <!-- ADR-IDX-001, TASK-IDX-002 -->
- `agnos-perf-center` skill: the process model, with elements from the index, containment and the
  references of each element's own lines <!-- ADR-TRC-001, TASK-TRC-001 -->
- `agnos-perf-center` skill: the source scanner, with default or given extensions and exclusions
  <!-- ADR-TRC-001, TASK-TRC-002 -->
- `agnos-perf-center` skill: coverage and gaps, with the summary line <!-- ADR-TRC-001, TASK-TRC-003 -->
- `agnos-perf-center` skill: offline page assembly, with design tokens in three tiers and Cytoscape.js
  vendored <!-- ADR-TRC-003, TASK-TRC-004 -->
- `agnos-perf-center` page: overview, search, filters, sortable matrix with CSV export, gaps, detail
  panel and deep links <!-- ADR-TRC-003, TASK-TRC-005 -->
- `agnos-perf-center` page: interactive graph of the selection's links as a traceability flow
  <!-- ADR-TRC-003, TASK-TRC-006 -->
- `agnos-perf-center` skill packaged as `SKILL.md`, with its Claude Code pointer <!-- ADR-TRC-003, TASK-TRC-007 -->
- `agnos-perf-center` page: resizable panels, with widths remembered <!-- ADR-TRC-003, TASK-TRC-008 -->
- `agnos-perf-center` page: the data beside it, as `<page>.json` and `<page>.data.js` <!-- ADR-TRC-003,
  TASK-TRC-031, RQ-TRC-010 -->
- `agnos-perf-center` call graph: optional module behind `--call-graph`, with the tree-sitter adapter and
  the C and C++ queries <!-- ADR-TRC-004, TASK-TRC-009, TASK-TRC-010 -->
- `agnos-perf-center` call graph: call resolution by name, with callers, callees, ambiguous and external
  counts <!-- ADR-TRC-004, TASK-TRC-011 -->
- `agnos-perf-center` call graph: C#, Java, JavaScript and Node.js, Python and Rust <!-- ADR-TRC-004,
  TASK-TRC-032 to TASK-TRC-036, RQ-TRC-050 -->
- `agnos-perf-center` call graph: functions in the page, in the graph and in the matrix <!-- ADR-TRC-004,
  TASK-TRC-012, TASK-TRC-013, TASK-TRC-015 -->
- `agnos-perf-center` graph: namespace and class boxes, enclosing boxes, and the box panel and deep links
  <!-- ADR-TRC-005, TASK-TRC-023 to TASK-TRC-026 -->
- `agnos-perf-center` graph: toolbar groups Depth, Display and Implementation detail, and a search result's
  tooltip <!-- TASK-TRC-029, TASK-TRC-030, RQ-TRC-048, RQ-TRC-049 -->
- `agnos-perf-center` page: scrollbars for the central views <!-- ADR-TRC-003, TASK-TRC-016 -->
- `agnos-perf-center` matrix: resizable columns <!-- ADR-TRC-003, TASK-TRC-018 -->
- `agnos-perf-center` graph: readable relations with arrows, a drawn legend and explanatory tooltips
  <!-- ADR-TRC-004, TASK-TRC-019 -->
- `agnos-perf-center` graph: a colour per relation, finer links and selection frame <!-- ADR-TRC-002, TASK-TRC-020 -->
- `agnos-perf-center` matrix: columns from one model, Feature first by default <!-- ADR-TRC-006, TASK-TRC-039,
  RQ-TRC-051 -->
- `agnos-perf-center` matrix: movable columns, order remembered, Reset columns <!-- ADR-TRC-006, TASK-TRC-040,
  RQ-TRC-052 -->
- `agnos-perf-center` matrix: feature title under its ID <!-- ADR-TRC-007, TASK-TRC-041, RQ-TRC-053 -->
- `agnos-perf-center` detail panel: fixed band, and tags that filter the groups of links <!-- ADR-TRC-007,
  TASK-TRC-042, TASK-TRC-043, RQ-TRC-054, RQ-TRC-055 -->
- `agnos-perf-center` graph: finer wheel zoom from a design token <!-- ADR-TRC-007, TASK-TRC-044, RQ-TRC-056 -->
- `agnos-perf-center` Quality view: scored checks, overall score and grade, quality data block
  <!-- ADR-TRC-008, TASK-TRC-046, RQ-TRC-058, RQ-TRC-059, RQ-TRC-064 -->
- `agnos-perf-center` Quality view: check cards compact or detailed, expand and collapse all
  <!-- ADR-TRC-008, TASK-TRC-048, RQ-TRC-062 -->
- `agnos-perf-center` Quality view: report card, grade palette, grade in tab, sidebar and overview
  <!-- ADR-TRC-008, TASK-TRC-049, RQ-TRC-060, RQ-TRC-064 -->
- `agnos-perf-center` Quality view: radar, feature-area bars and coverage shares as SVG with tooltips
  <!-- ADR-TRC-008, TASK-TRC-050, RQ-TRC-061 -->
- `agnos-perf-center` Quality view: fits a 1440x900 window <!-- ADR-TRC-008, TASK-TRC-051, RQ-TRC-063, RQ-TRC-066 -->
- `agnos-perf-center` Quality view: grade colours follow the green-to-red scale of the Nutri-Score and DPE
  labels <!-- ADR-TRC-008, TASK-TRC-053, RQ-TRC-065 -->
- `agnos-docs-sync` skill: the report of the changes since each entry-point document's last change
  <!-- TASK-DOC-001, RQ-DOC-001, RQ-DOC-004 -->
- `agnos-docs-sync` skill, its Claude Code pointer and the Haiku sub-agent <!-- TASK-DOC-002, RQ-DOC-002,
  RQ-DOC-003 -->
- `agnos-design-system` skill: the design-system template packaged as a skill <!-- ADR-DSY-001,
  TASK-DSY-001, RQ-DSY-001 -->
- `AGENTS.md`: the entry point for every AI agent <!-- TASK-AGT-001, RQ-AGT-001 -->
- `agnos-demo` demo: replay engine, process documents of the three sessions, Python service,
  TypeScript client and command-line tool, README, cast and scenario <!-- ADR-DMO-001, TASK-DMO-001,
  TASK-DMO-003 to TASK-DMO-007 -->
- `agnos-demo` demo: verification script of its requirements <!-- RQ-DMO-001 to RQ-DMO-021 -->, and the `agnos-demo` skill
  with build and verify sub-commands <!-- ADR-DMO-001, TASK-DMO-008, TASK-DMO-009 -->
- `agnos-perf-center` page: the Spans brand mark in the header, an About topic with the design's lockup and the addresses of this app and its link buttons, a Licenses topic whose licences are coloured local badges, and the foot of the left panel naming the application and its version <!-- ADR-TRC-014, TASK-TRC-092 to TASK-TRC-097, RQ-TRC-109, RQ-TRC-110, RQ-TRC-111 to RQ-TRC-116 -->
- `agnos-perf-center` page: one `AGNOS v.<major>.<minor>` label in the foot and in About, and the licence badges link to their SPDX entries <!-- ADR-TRC-016, TASK-TRC-102, RQ-TRC-109 to RQ-TRC-112, RQ-TRC-116 -->
- `agnos-perf-center` page: dark theme in four surface layers, with the fragile colours given dark variants and their contrast tested <!-- ADR-TRC-017, TASK-TRC-103, RQ-TRC-117, RQ-TRC-118 -->
- `agnos-perf-center` shows the scanned extensions, scanned names and excluded names on every run, each marked as the default or the user's list, and `--help` prints the default lists <!-- TASK-TRC-104, RQ-TRC-119 -->
- `agnos-meta-release-prep` maintainer skill: checks the working tree and the index, syncs the documents with `agnos-meta-docs-sync`, shows the diff, the unreleased entries and a proposed SemVer 2.0.0 version, records the approved version and commits it, publishing nothing <!-- ADR-PLG-005, TASK-PLG-033, TASK-PLG-034, RQ-PLG-027 to RQ-PLG-030 -->
- `agnos-perf-center` score: the "Functions traced" check weighs medium in the quality score <!-- ADR-PLG-004, TASK-PLG-027, RQ-PLG-024 -->
- The Definition of Done gains, for S, M and L, the item that every new function, method and class cites its requirement ID in its doc comment or in the comment just above it <!-- ADR-PLG-004, TASK-PLG-028, RQ-PLG-025 -->
- `agnos-meta-release` reads the version from the version file, in SemVer 2.0.0 (refused when absent or invalid), and reports the changelog's unreleased entries without failing <!-- ADR-PLG-005, TASK-PLG-035, RQ-PLG-031, RQ-PLG-032 -->
- `agnos-init` writes `agnos-process/AGNOS-GETTING-STARTED.md` and the version file `agnos-process/VERSION.txt` <!-- ADR-PLG-005, ADR-PLG-007, TASK-PLG-037, TASK-PLG-051, RQ-PLG-021, RQ-PLG-033 -->

### Changed
- The RECURSIVE SELF-IMPROVEMENT SESSIONS section and END SESSION step 3 invoke `agnos-self-improvement`; the improvement target is always declared by the project, with no fallback on the instructions file, and rules older than the effort may be revised <!-- ADR-RSI-001, TASK-RSI-004, RQ-RSI-001, RQ-RSI-002 -->
- `agnos-init`'s success step gives two steps: open a new conversation, so that it reads the block, then ask it for an AGNOS session; the step names `AGNOS-GETTING-STARTED.md` as the guide to read meanwhile <!-- ADR-PLG-003, TASK-PLG-020, TASK-PLG-021, RQ-PLG-020, RQ-PLG-021 -->
- The `agnos-init` block tells the agent to read `process/project-rules.md` when it exists, and names it the improvement target. Initialised projects call `agnos-init` again to update <!-- ADR-PLG-003, TASK-PLG-020, RQ-PLG-018 -->
- The process's self-improvement goes into the improvement target, the file the project's AGNOS block names (created if absent), and into the instructions file otherwise, never into a file of an installed plugin <!-- ADR-PLG-003, TASK-PLG-019, RQ-PLG-018, RQ-PLG-019 -->
- A test run's `Verification` field states how many tests were skipped and why: a skipped test is not a passed test <!-- TASK-PLG-009, RQ-PLG-011 -->
- `README.md` and `GETTING_STARTED.MD` address plugin users, and the README states what was tested per tool and system <!-- ADR-PLG-001, TASK-PLG-005, TASK-PLG-007, RQ-PLG-008, RQ-PLG-009 -->
- `agnos-init` writes a block naming the skill `agnos-process`, with no path, and no longer takes a toolkit input. Initialised projects install the plugin and call `agnos-init` again to update <!-- ADR-PLG-001, TASK-PLG-004, RQ-PLG-004, RQ-INI-006 -->
- The delivered skills name their files from their own folder, with no `.github/skills/` path <!-- ADR-PLG-001, TASK-PLG-002, RQ-PLG-005 -->
- The sub-agent of `agnos-meta-docs-sync` is defined once in `.github/agents/`, read by GitHub Copilot, and `.claude/agents/` holds a pointer to it for Claude Code <!-- TASK-DOC-004, RQ-DOC-003 -->
- `agnos-init` writes a `readme.md` saying what each `process/` folder it creates holds, instead of a `.gitkeep` <!-- TASK-INI-005, RQ-INI-005 -->
- The citations of `CHANGELOG.md`, of the skills' documents and of the scripts' help are in comments, as MANDATORY TRACEABILITY asks, and `agnos-meta-docs-sync` writes them so <!-- TASK-MTA-009, RQ-MTA-014 -->
- `agnos-perf-center` Delivery: the Rework and Friction marks of "Points over time" are amber and red with a dark outline, so they
  stand out inside and outside periods A and B <!-- TASK-TRC-091, RQ-TRC-108 -->
- `agnos-init`: the `CLAUDE.md` block orders the agent to read the instructions first, as the `AGENTS.md` block does, instead
  of an `@` import that may not load. Initialised projects call `agnos-init` again to update <!-- ADR-INI-001, TASK-INI-004,
  RQ-INI-010 -->
- A session starts when the user asks for it, as it already closed: START SESSION no longer runs by itself <!-- ADR-INI-001,
  TASK-INI-004, RQ-INI-010 -->
- The skill `agnos-trace` is now `agnos-perf-center`, since it monitors the process's execution on a project. Its script is
  `perf_center.py`, its outputs `PERF-CENTER.*`, its page title "Performance center". Projects must update their ignore rules,
  and a reader's saved page preferences reset once. <!-- ADR-TRC-013, TASK-TRC-089,
  RQ-TRC-104 to RQ-TRC-106 -->
- `agnos-perf-center` scripts and page script: no open quality finding, with the same data generated <!-- TASK-QLT-002 to
  TASK-QLT-005, RQ-QLT-009 -->
- `agnos-perf-center` page skeleton: a plain `div` for the tabs and `fieldset` for the filter groups <!-- TASK-QLT-006, RQ-QLT-010 -->
- `agnos-index`'s error without `process/`, START SESSION, `README.md` and `GETTING_STARTED.MD` say to call `agnos-init`
  <!-- TASK-INI-002, RQ-INI-007, RQ-IDX-008 -->
- The demo is an initialised project: its first commit holds the `CLAUDE.md` and `AGENTS.md` written by `agnos-init`
  <!-- TASK-INI-003, RQ-INI-008 -->
- The demo holds the project only, with no other AGNOS file, and `agnos-meta-demo` runs the skills on it from this
  repository <!-- TASK-MTA-003, RQ-MTA-005 -->
- Maintainer skills renamed `agnos-meta-demo` and `agnos-meta-docs-sync`, with the sub-agent; the prefix `agnos-meta-` is
  the only criterion that marks them <!-- TASK-MTA-001, RQ-MTA-001, RQ-MTA-002 -->
- `agnos-perf-center` graph and legend styling: thicker relation samples, triangle arrows on contains links,
  opaque legend samples, group labels and faint frames <!-- TASK-TRC-021, TASK-TRC-022, TASK-TRC-030 -->
- `README.md` rewritten and `GETTING_STARTED.MD` aligned with `agnos-index`, `agnos-perf-center` and
  `agnos-design-system` <!-- ADR-DSY-001, TASK-DSY-002, RQ-DSY-001 -->
- `CLAUDE.md` aligned on the four skills <!-- TASK-AGT-001, RQ-AGT-001 -->
- Design-system dependencies on UI requirements; one task re-tiered to M <!-- TASK-DSY-002, ADR-FIX-001,
  TASK-FIX-001, RQ-FIX-001 -->
- The process folder is `agnos-process/`, with its index `process.idx.md`, in place of `process/`; `agnos-init` moves an existing `process/` with `git mv` when it is tracked, and exits 1 when both folders exist <!-- ADR-PLG-006, TASK-PLG-041, TASK-PLG-045, TASK-PLG-046, RQ-PLG-034, RQ-PLG-038 -->
- The generated process skill is `agnos-instructions`; `layout.json` declares the process folder once, `layout.py` writes its copies and checks them, and the scripts read those copies <!-- ADR-PLG-006, TASK-PLG-039, TASK-PLG-040, TASK-PLG-042, TASK-PLG-043, RQ-PLG-035 to RQ-PLG-037 -->

### Fixed
- `agnos-meta-release` output holds what is declared: no bytecode written by its checks, and a stray file fails the rehearsal <!-- ADR-PLG-002, TASK-PLG-011, RQ-PLG-012 -->
- `agnos-init` accepts an absolute target on Windows, and `agnos-meta-release` no longer takes two failures for the same behaviour <!-- ADR-PLG-001, TASK-PLG-006, RQ-PLG-006, RQ-MTA-011 -->
- `agnos-perf-center` writes dates in one form whatever git's version, and the delivered suites run on Linux <!-- ADR-PLG-001, TASK-PLG-003, RQ-PLG-008 -->
- `agnos-perf-center` matrix: headers of the list columns aligned left with their cells <!-- ADR-TRC-002,
  TASK-TRC-017 -->
- `agnos-perf-center` graph: one global box for what stands in no named namespace, instead of one box per
  file <!-- ADR-TRC-005, TASK-TRC-028 -->
- `agnos-perf-center` Untraced functions list: long function names end in an ellipsis <!-- TASK-TRC-038, RQ-TRC-035 -->
- `agnos-perf-center` graph: relation tooltip delay halved to 1 s <!-- TASK-TRC-045, RQ-TRC-046 -->
- `agnos-perf-center` graph: the unreadable Whole graph control removed from the toolbar <!-- ADR-TRC-015, DEC-TRC-060, TASK-TRC-099 -->
- `agnos-perf-center` reads the version from the layout's copy, and the layout check accepts `agnos_layout.<NAME>` <!-- TASK-TRC-101, TASK-PLG-050, RQ-PLG-036, RQ-PLG-037 -->

### Removed
- `GETTING_STARTED.MD` leaves the repository root and the release: the user's guide is `AGNOS-GETTING-STARTED.md`, which `agnos-init` writes into each project, and README, CONTRIBUTING and the issue template link to it <!-- ADR-PLG-003, TASK-PLG-022, RQ-PLG-022 -->
- `agnos-perf-center` "gaps" view and wording in the page, data and docs, replaced by the Quality view,
  checks and findings <!-- ADR-TRC-008, TASK-TRC-047, RQ-TRC-057 -->

## [v3.1]

### Changed
- Section 4 ("Code Implementation and Quality") rewording: "All" → "ALL" and "Every" → "EVERY"
  for emphasis consistency with the rest of the file's SHALL/MANDATORY language.

### Removed
- `chat_mode` session state variable and all references to it (session-start question, schema,
  variable-kind table, "Chat Verbosity" guidance) from
  `.github/instructions/agnos-sw-eng.instructions.md`, `README.md`, `GETTING_STARTED.MD`, and
  `process/_sessionstate/session.yaml`.
Consider using a dedicated harness like [caveman](https://github.com/juliusbrussee/caveman) to manage chat verbosity.
- redondant "versions" removed almost everywhere. only CHANGELOG.md and releases relate to version.



