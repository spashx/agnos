# FTR-PLG-009: Plugin listing metadata

## Overview
The marketplace and the plugin agnos describe themselves as a published plugin does: a metadata block in the catalogue,
the project's links, an author, keywords, a category and a logo. On 2026-11-15 the owner compared the delivered files with
those of a Microsoft plugin installed from GitHub Copilot, whose `.claude-plugin/plugin.json` declares a `logo`, and whose
catalogue holds a `metadata` block with a version at the marketplace's level and in its plugin entry.

Choices of the owner on 2026-11-15: the owner's email is GitHub's private address `25369377+spashx@users.noreply.github.com`;
the category is `software development`; the keywords add `agentic`, `ears`, `claude-code` and `copilot`; the logo is the
website's brand mark, in the brand colours of the perf center's tokens.

## Stakeholders
- **Owner**: the repository owner (maintainer of AGNOS).
- **Consumers**: developers browsing or installing the plugin from Claude Code or GitHub Copilot.

---

## Functional Requirements

### RQ-PLG-044: Catalogue metadata block
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The release SHALL write the catalogue's description and version in a `metadata` block, and the owner's email under `owner`.
- **Rationale**: the catalogue format of both tools holds the marketplace's description and version in `metadata`.
- **Priority**: Must
- **Acceptance Criteria**: Given a release, When the marketplace is written, Then `.claude-plugin/marketplace.json` holds `metadata.description` And `metadata.version` equal to `VERSION.txt` And `owner.email` And no `description` at its root.
- **Dependencies**: RQ-PLG-002, RQ-PLG-032, RQ-PLG-043

### RQ-PLG-045: Plugin listing fields
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The release SHALL write the author's URL, the homepage, the repository and the keywords in both manifests and in the catalogue's plugin entry, and the license and the category in that entry.
- **Rationale**: a tool shows these fields to a user choosing a plugin.
- **Priority**: Must
- **Acceptance Criteria**: Given a release, When the marketplace is written, Then both manifests and the catalogue's plugin entry hold `author.url`, `homepage`, `repository` and `keywords` with the values of `assets/marketplace.json` And the entry holds `license` And `category` `software development`.
- **Dependencies**: RQ-PLG-044

### RQ-PLG-046: Plugin logo
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The release SHALL write the brand mark as `plugins/agnos/assets/agnos.svg`, in the brand colours of the perf center's tokens, and declare it as `logo` in both manifests.
- **Rationale**: GitHub Copilot shows a plugin's logo, and the brand mark already exists with its colours as tokens.
- **Priority**: Should
- **Acceptance Criteria**: Given a release, When the marketplace is written, Then `plugins/agnos/assets/agnos.svg` exists And its five fill colours equal the `color.brand-*` tokens of `tokens.json` And both manifests hold `logo` `assets/agnos.svg`; Given the plugin proof, When `claude plugin validate --strict` warns only that `logo` is an unknown field, Then the check passes and says the warning was accepted (owner, 2026-11-15: Claude Code ignores the field and installs).
- **Dependencies**: RQ-PLG-045, RQ-PLG-017
