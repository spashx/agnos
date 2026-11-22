# PLAN-PLG-011: Plugin listing metadata and logo

## Overview
Deliver the catalogue's metadata block, the plugin's listing fields and its logo, then prove the install in both tools.

## References
- **Requirement refs**: RQ-PLG-044, RQ-PLG-045, RQ-PLG-046
- **ADR refs**: ADR-PLG-009

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-PLG-071: Record listing metadata decisions
- **Tier**: L
- **Status**: Done
- **Description**: Write FTR-PLG-009, ADR-PLG-009 and this plan from the owner's choices of 2026-11-15.
- **Requirement refs**: RQ-PLG-044, RQ-PLG-045, RQ-PLG-046
- **ADR refs**: ADR-PLG-009
- **Acceptance Criteria**: Given the index, When it is rebuilt, Then RQ-PLG-044 to RQ-PLG-046, DEC-PLG-035, DEC-PLG-036 and TASK-PLG-071 to TASK-PLG-074 are listed with no duplicate.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `agnos-index`: exit 0, 933 entries; RQ-PLG-044 to 046, DEC-PLG-035, DEC-PLG-036, TASK-PLG-071 to 074 listed, no duplicate.
- **Assumptions**: None

### TASK-PLG-072: Write catalogue and manifest metadata
- **Tier**: L
- **Status**: Done
- **Description**: Add the listing fields to `assets/marketplace.json`, write them and `metadata` from `write_marketplace`, and check `metadata.version` in `manifest_problems`, test first.
- **Requirement refs**: RQ-PLG-044, RQ-PLG-045
- **ADR refs**: ADR-PLG-009
- **Acceptance Criteria**: Given a release, When the marketplace is written, Then the catalogue holds `metadata.version` equal to `VERSION.txt` and no root `description` And both manifests and the plugin entry hold `homepage`, `repository` and `author.url`; Given a catalogue whose `metadata.version` differs, When it is checked, Then a problem is reported.
- **Dependencies**: TASK-PLG-071
- **Assignee**: AI
- **Verification**: `test_manifests` 19/19 (`ListingTest` metadata, owner email, listing fields, category; `RefusedTest` metadata version, root description, homepage); agnos-meta-release suite 145 run, 143 passed, 2 skipped (`test_proof`, `test_determinism`: the demo is not built beside the scratchpad copy).
- **Assumptions**: The entry-only fields sit under an `entry` key of `assets/marketplace.json`.

### TASK-PLG-073: Generate plugin logo from brand tokens
- **Tier**: L
- **Status**: Done
- **Description**: Write `plugins/agnos/assets/agnos.svg` from the brand mark and the `color.brand-*` tokens, declare it as `logo` in both manifests, and check the file exists, test first.
- **Requirement refs**: RQ-PLG-046
- **ADR refs**: ADR-PLG-009
- **Acceptance Criteria**: Given a release, When the marketplace is written, Then the SVG exists And its five fill colours equal the tokens And both manifests hold `logo` `assets/agnos.svg`; Given a manifest whose logo file is absent, When it is checked, Then a problem is reported.
- **Dependencies**: TASK-PLG-072
- **Assignee**: AI
- **Verification**: agnos-meta-release suite 150 run: 146 passed, 2 failed (`test_console` file counts 10/11, +2 for the fixture's tokens.json and the logo; expectations set to 12/13, then `test_console` 5/5), 2 skipped (`test_proof`, `test_determinism`: no demo beside the scratchpad copy); `LogoTest` 3/3, `LogoFromCommitTest` 2/2.
- **Assumptions**: The brand mark's shapes sit in `assets/logo-template.svg`, its colours as placeholders; a commit without the brand tokens is refused.

### TASK-PLG-074: Prove listing metadata install
- **Tier**: M
- **Status**: Done
- **Description**: Rehearse a release and install it with `agnos-meta-plugin-proof` in Claude Code and GitHub Copilot.
- **Requirement refs**: RQ-PLG-044, RQ-PLG-045, RQ-PLG-046
- **ADR refs**: ADR-PLG-009
- **Acceptance Criteria**: Given the rehearsed marketplace, When it is installed in both tools, Then each install succeeds And the result of each is recorded.
- **Dependencies**: TASK-PLG-073, TASK-PLG-075
- **Assignee**: AI
- **Verification**: `release.py --dry-run` at e427411 with the demo: exit=0, 72 files, 0 problems; catalogue `metadata.version` 3.6.0, both manifests `logo`, `agnos.svg` in the five brand colours; `plugin_proof.py`: exit=0, claude validate-plugin/catalogue pass (logo accepted), marketplace-add, install, skills 8/8 pass in Claude Code and Copilot. Models not asked (`--with-models` not run, it costs credits).
- **Assumptions**: None

### TASK-PLG-075: Accept logo warning in strict validation
- **Tier**: L
- **Status**: Done
- **Description**: Make the plugin proof count a strict validation whose only warnings are the unknown field `logo` as passed, saying so, test first.
- **Requirement refs**: RQ-PLG-046
- **ADR refs**: ADR-PLG-009
- **Acceptance Criteria**: Given a validation output whose only warning is the unknown field `logo`, When it is judged, Then it passes and its detail says accepted; Given a second warning or an error beside it, Then it fails.
- **Dependencies**: TASK-PLG-073
- **Assignee**: AI
- **Verification**: plugin-proof tests 22/22, 0 skipped (`StrictValidationTest` 6/6: logo only, logo + warning, logo + error, no warning, clean, real output with directory warnings and advice); first real run failed `validate-plugin` (the directory and advice blocks counted), one fix then passed.
- **Assumptions**: The blocks "plugin directory" and "Advice" are outside the verdict, as the validator's output says.

### TASK-PLG-076: Relocate overview image into assets
- **Tier**: M
- **Status**: Done
- **Description**: Deliver the README's image at `assets/agnos-overview.png`, where the owner moved it in a2a65fd, by its layer rule and the selection test.
- **Requirement refs**: RQ-PLG-008
- **ADR refs**: None
- **Acceptance Criteria**: Given a commit holding `assets/agnos-overview.png`, When the release is rehearsed, Then the file is delivered at that path And the README's link leads to it And the agnos-meta-release suite passes.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: agnos-meta-release suite 150 run, 148 passed, 2 skipped (`test_proof`, `test_determinism`: no demo beside the copy); agnos-meta-demo suite 18/18; the delivered path is proved again by the 3.6.1 rehearsal.
- **Assumptions**: The demo verifier's toolkit pattern follows the image to `assets/`.

### TASK-PLG-077: Prepare version 3.6.1 release
- **Tier**: S
- **Status**: Done
- **Description**: Record the version 3.6.1 the owner approved, with the changelog docs-sync wrote, by agnos-meta-release-prep.
- **Requirement refs**: RQ-PLG-032
- **ADR refs**: None
- **Acceptance Criteria**: Given the approved diff, When the version is set, Then `VERSION.txt` holds 3.6.1 And the changelog's `[Unreleased]` is `[3.6.1]`.
- **Dependencies**: TASK-PLG-076
- **Assignee**: AI
- **Verification**: N/A (Tier S)
- **Assumptions**: The owner chose 3.6.1 over the proposed 3.7.0.
