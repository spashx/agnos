# Changelog

All notable changes to this repository are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- `agnos-index` skill: the index generators (PowerShell and bash) with shared golden tests
  (ADR-IDX-001, TASK-IDX-001)
- `agnos-index` skill packaged and integrated into the process (ADR-IDX-001, TASK-IDX-002)
- `agnos-trace` skill: the process model, with elements from the index, containment and the
  references of each element's own lines (ADR-TRC-001, TASK-TRC-001)
- `agnos-trace` skill: the source scanner, with default or given extensions and exclusions
  (ADR-TRC-001, TASK-TRC-002)
- `agnos-trace` skill: coverage and gaps, with the summary line (ADR-TRC-001, TASK-TRC-003)
- `agnos-trace` skill: offline page assembly, with design tokens in three tiers and Cytoscape.js
  vendored (ADR-TRC-003, TASK-TRC-004)
- `agnos-trace` page: overview, search, filters, sortable matrix with CSV export, gaps, detail
  panel and deep links (ADR-TRC-003, TASK-TRC-005)
- `agnos-trace` page: interactive graph of the selection's links as a traceability flow
  (ADR-TRC-003, TASK-TRC-006)
- `agnos-trace` skill packaged as `SKILL.md`, with its Claude Code pointer (ADR-TRC-003, TASK-TRC-007)
- `agnos-trace` page: resizable panels, with widths remembered (ADR-TRC-003, TASK-TRC-008)
- `agnos-trace` page: the data beside it, as `<page>.json` and `<page>.data.js` (ADR-TRC-003,
  TASK-TRC-031, RQ-TRC-010)
- `agnos-trace` call graph: optional module behind `--call-graph`, with the tree-sitter adapter and
  the C and C++ queries (ADR-TRC-004, TASK-TRC-009, TASK-TRC-010)
- `agnos-trace` call graph: call resolution by name, with callers, callees, ambiguous and external
  counts (ADR-TRC-004, TASK-TRC-011)
- `agnos-trace` call graph: C#, Java, JavaScript and Node.js, Python and Rust (ADR-TRC-004,
  TASK-TRC-032 to TASK-TRC-036, RQ-TRC-050)
- `agnos-trace` call graph: functions in the trace page, in the graph and in the matrix (ADR-TRC-004,
  TASK-TRC-012, TASK-TRC-013, TASK-TRC-015)
- `agnos-trace` graph: namespace and class boxes, enclosing boxes, and the box panel and deep links
  (ADR-TRC-005, TASK-TRC-023 to TASK-TRC-026)
- `agnos-trace` graph: toolbar groups Depth, Display and Implementation detail, and a search result's
  tooltip (TASK-TRC-029, TASK-TRC-030, RQ-TRC-048, RQ-TRC-049)
- `agnos-trace` page: scrollbars for the central views (ADR-TRC-003, TASK-TRC-016)
- `agnos-trace` matrix: resizable columns (ADR-TRC-003, TASK-TRC-018)
- `agnos-trace` graph: readable relations with arrows, a drawn legend and explanatory tooltips
  (ADR-TRC-004, TASK-TRC-019)
- `agnos-trace` graph: a colour per relation, finer links and selection frame (ADR-TRC-002, TASK-TRC-020)
- `agnos-trace` matrix: columns from one model, Feature first by default (ADR-TRC-006, TASK-TRC-039,
  RQ-TRC-051)
- `agnos-trace` matrix: movable columns, order remembered, Reset columns (ADR-TRC-006, TASK-TRC-040,
  RQ-TRC-052)
- `agnos-trace` matrix: feature title under its ID (ADR-TRC-007, TASK-TRC-041, RQ-TRC-053)
- `agnos-trace` detail panel: fixed band, and tags that filter the groups of links (ADR-TRC-007,
  TASK-TRC-042, TASK-TRC-043, RQ-TRC-054, RQ-TRC-055)
- `agnos-trace` graph: finer wheel zoom from a design token (ADR-TRC-007, TASK-TRC-044, RQ-TRC-056)
- `agnos-trace` Quality view: scored checks, overall score and grade, quality data block
  (ADR-TRC-008, TASK-TRC-046, RQ-TRC-058, RQ-TRC-059, RQ-TRC-064)
- `agnos-trace` Quality view: check cards compact or detailed, expand and collapse all
  (ADR-TRC-008, TASK-TRC-048, RQ-TRC-062)
- `agnos-trace` Quality view: report card, grade palette, grade in tab, sidebar and overview
  (ADR-TRC-008, TASK-TRC-049, RQ-TRC-060, RQ-TRC-064)
- `agnos-trace` Quality view: radar, feature-area bars and coverage shares as SVG with tooltips
  (ADR-TRC-008, TASK-TRC-050, RQ-TRC-061)
- `agnos-trace` Quality view: fits a 1440x900 window (ADR-TRC-008, TASK-TRC-051, RQ-TRC-063, RQ-TRC-066)
- `agnos-trace` Quality view: grade colours follow the green-to-red scale of the Nutri-Score and DPE
  labels (ADR-TRC-008, TASK-TRC-053, RQ-TRC-065)
- `agnos-docs-sync` skill: the report of the changes since each entry-point document's last change
  (TASK-DOC-001, RQ-DOC-001, RQ-DOC-004)
- `agnos-docs-sync` skill, its Claude Code pointer and the Haiku sub-agent (TASK-DOC-002, RQ-DOC-002,
  RQ-DOC-003)
- `agnos-design-system` skill: the design-system template packaged as a skill (ADR-DSY-001,
  TASK-DSY-001, RQ-DSY-001)
- `AGENTS.md`: the entry point for every AI agent (TASK-AGT-001, RQ-AGT-001)
- `agnos-demo` demo: replay engine, process documents of the three sessions, Python service,
  TypeScript client and command-line tool, README, cast and scenario (ADR-DMO-001, TASK-DMO-001,
  TASK-DMO-003 to TASK-DMO-007)
- `agnos-demo` demo: verification script for RQ-DMO-001 to RQ-DMO-021, and the `agnos-demo` skill
  with build and verify sub-commands (ADR-DMO-001, TASK-DMO-008, TASK-DMO-009)

### Changed
- The demo holds the project only, with no AGNOS file, and `agnos-meta-demo` runs the skills on it from this
  repository (TASK-MTA-003, RQ-MTA-005)
- Maintainer skills renamed `agnos-meta-demo` and `agnos-meta-docs-sync`, with the sub-agent; the prefix `agnos-meta-` is
  the only criterion that marks them (TASK-MTA-001, RQ-MTA-001, RQ-MTA-002)
- `agnos-trace` graph and legend styling: thicker relation samples, triangle arrows on contains links,
  opaque legend samples, group labels and faint frames (TASK-TRC-021, TASK-TRC-022, TASK-TRC-030)
- `README.md` rewritten and `GETTING_STARTED.MD` aligned with `agnos-index`, `agnos-trace` and
  `agnos-design-system` (ADR-DSY-001, TASK-DSY-002, RQ-DSY-001)
- `CLAUDE.md` aligned on the four skills (TASK-AGT-001, RQ-AGT-001)
- Design-system dependencies on UI requirements; TASK-DSY-002 re-tiered to M (ADR-FIX-001,
  TASK-FIX-001, RQ-FIX-001)

### Fixed
- `agnos-trace` matrix: headers of the list columns aligned left with their cells (ADR-TRC-002,
  TASK-TRC-017)
- `agnos-trace` graph: one global box for what stands in no named namespace, instead of one box per
  file (ADR-TRC-005, TASK-TRC-028)
- `agnos-trace` Untraced functions list: long function names end in an ellipsis (TASK-TRC-038, RQ-TRC-035)
- `agnos-trace` graph: relation tooltip delay halved to 1 s (TASK-TRC-045, RQ-TRC-046)

### Removed
- `agnos-trace` "gaps" view and wording in the page, data and docs, replaced by the Quality view,
  checks and findings (ADR-TRC-008, TASK-TRC-047, RQ-TRC-057)

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



