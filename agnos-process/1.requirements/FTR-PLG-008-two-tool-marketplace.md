# FTR-PLG-008: Two-tool marketplace

## Overview
The marketplace serves Claude Code and GitHub Copilot only, and its plugin folder holds a README that the tools show. On
2026-11-15, installed in VS Code from the marketplace, the plugin showed "no README": VS Code reads the README from the
installed plugin's folder, and the release wrote one at the marketplace's root only. The same day the owner withdrew OpenAI
Codex from what is delivered, to deliver it later.

Choices of the owner on 2026-11-15: the changelog's past entries are rewritten without Codex; the perf center keeps
recognising a commit made by Codex, which names an author and promises no support; the website, which says Codex support
is coming, is out of scope.

## Stakeholders
- **Owner**: the repository owner (maintainer of AGNOS).
- **Consumers**: developers installing the plugin from Claude Code or GitHub Copilot, in VS Code or the CLI.

---

## Functional Requirements

### RQ-PLG-042: Plugin folder README
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The release SHALL write a `README.md` in the plugin's folder, whose relative links all lead to a file of the plugin.
- **Rationale**: VS Code shows the README of the installed plugin's folder, and reported none.
- **Priority**: Must
- **Acceptance Criteria**: Given a release, When the marketplace is written, Then `plugins/agnos/README.md` exists And every relative link it holds leads to a file of `plugins/agnos/`.
- **Dependencies**: RQ-PLG-001, RQ-PLG-023

### RQ-PLG-043: Marketplace without Codex
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The release SHALL write no catalogue, manifest field or user-document text for OpenAI Codex, except the perf center's recognition of a Codex commit author.
- **Rationale**: Codex is untested, and the owner delivers it later.
- **Priority**: Must
- **Acceptance Criteria**: Given a release, When the marketplace is written, Then `.agents/plugins/marketplace.json` is absent And no delivered file holds "codex", ignoring case, outside `agnos-perf-center`'s author patterns.
- **Dependencies**: RQ-PLG-002, RQ-PLG-008
