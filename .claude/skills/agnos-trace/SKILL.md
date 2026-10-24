---
name: agnos-trace
description: "AGNOS traceability matrix skill. From an AGNOS process folder (the one holding INDEX.idx.md) and one or more source folders, writes one self-contained HTML page: every FTR/RQ/ADR/DEC/PLAN/TASK, the source files and lines that cite them, coverage of each requirement, a quality score and grade, with the findings of each check (uncovered requirements, tasks without requirement, undefined IDs...), searchable, with an interactive graph. USE FOR: checking MANDATORY TRACEABILITY at the end of a session or before a release; answering 'what implements / cites this requirement'. Independent of the product developed."
argument-hint: "--process <dir> --sources <dir> [--sources <dir>...] [--out <file>] [--ext <.x>...] [--exclude <pattern>...] [--title <t>] [--generated-at <t>]"
---

# AGNOS Traceability Matrix (Claude Code entry point)

<!-- RQ-TRC-017, DEC-TRC-008 -->

This is a thin pointer, kept in sync with the canonical procedure so the process has a single source of truth. Read and
follow the full procedure (command, arguments, exit codes, rules behind the numbers, tests) at:

`.github/skills/agnos-trace/SKILL.md`

Do not duplicate that procedure here; if it and this file ever disagree, the `.github` version is authoritative.
