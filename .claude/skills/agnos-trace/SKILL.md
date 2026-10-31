---
name: agnos-trace
description: "AGNOS traceability matrix skill. From an AGNOS process folder and source folders, writes an HTML page and its data: every artifact, what cites it, coverage, a quality score and findings. USE FOR: checking MANDATORY TRACEABILITY at session end or before a release; what cites a requirement; with --call-graph, its functions; with --history, who changed what and what was delivered."
argument-hint: "--process <dir> --sources <dir> [--sources <dir>...] [--out <file>] [--ext <.x>...] [--exclude <pattern>...] [--title <t>] [--generated-at <t>] [--call-graph] [--history [--history-since <date|duration>] [--history-depth <n>]]"
---

# AGNOS Traceability Matrix (Claude Code entry point)

<!-- RQ-TRC-017, DEC-TRC-008 -->

This is a thin pointer, kept in sync with the canonical procedure so the process has a single source of truth. Read and
follow the procedure (command, parameters, exit codes, where to find the rest) at:

`.github/skills/agnos-trace/SKILL.md`

Do not duplicate that procedure here; if it and this file ever disagree, the `.github` version is authoritative.
