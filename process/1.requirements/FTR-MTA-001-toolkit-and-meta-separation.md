# FTR-MTA-001: The Toolkit Apart from its Own Development

## Overview
This repository holds both the AGNOS toolkit, which projects reuse, and the workshop that develops it with AGNOS itself:
its `process/` folder, its maintainer skills and its tests. Nothing in the tree tells them apart, and each tool that needs to
know holds its own list. This feature gives the workshop a name and a single criterion, and states which layer each part
of the repository belongs to.

Out of scope: building a release, removing artifact IDs from delivered files, delivering as an agent plugin (each comes in
a later feature, after ADR-MTA-001), and pushing anything to a remote.

## Stakeholders
- **Owner**: the repository owner (maintainer of AGNOS).
- **Consumers**: the maintainer and the agents working in this repository; `agnos-meta-demo` and `agnos-meta-docs-sync`,
  which need to tell the layers apart.

---

## Functional Requirements

### RQ-MTA-001: Meta skills carry a prefix
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: Each skill and sub-agent that serves the development of AGNOS, and not its use in a project, SHALL be named
  with the prefix `agnos-meta-`, in its canonical folder, its Claude Code pointer and its front matter: `agnos-demo` becomes
  `agnos-meta-demo`, and `agnos-docs-sync` becomes `agnos-meta-docs-sync`, skill and sub-agent.
- **Rationale**: agents discover skills only in `.github/skills/` and `.claude/skills/`, so a subfolder cannot separate them and the name has to.
- **Priority**: Must
- **Acceptance Criteria**: Given the repository, When its skills and sub-agents are listed, Then `agnos-meta-demo` and
  `agnos-meta-docs-sync` are present in each location, And no folder or front matter is still named `agnos-demo` or `agnos-docs-sync`.
- **Dependencies**: ADR-MTA-001

### RQ-MTA-002: The prefix is the only criterion
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN a tool of this repository decides whether a skill or sub-agent belongs to the workshop, it SHALL decide
  from the prefix `agnos-meta-` alone, without a list of names and without reading its description.
- **Rationale**: the docs-sync report, the demo's exclusions and its verification each hold their own definition today, and a third meta skill would have to be added to each.
- **Priority**: Must
- **Acceptance Criteria**: Given a skill `agnos-meta-other` whose description does not say maintainer, When the docs-sync report runs,
  Then it is flagged as a maintainer skill; Given a skill `agnos-other` whose description starts with "AGNOS maintainer skill", Then
  it is not; Given the demo's baseline exclusions and its verification, When they are read, Then they name the prefix and no skill.
- **Dependencies**: RQ-MTA-001

### RQ-MTA-003: An existing demo can still be rebuilt
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: IF a demo generated before the renaming exists, THEN `agnos-meta-demo build` SHALL rebuild it instead of refusing it.
- **Rationale**: the build recognises its own folder by the marker `.git/agnos-demo-generated`; these internal names and the demo's e-mail addresses identify the generated demo, not the skill, and stay.
- **Priority**: Must
- **Acceptance Criteria**: Given `agnos-lightweight-process.demo` as built before the renaming, When `build -Verify` runs, Then the
  demo is rebuilt, And every check passes, And its toolkit contains no `agnos-meta-` file.
- **Dependencies**: RQ-MTA-001, RQ-MTA-002

### RQ-MTA-004: The layers are stated
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: `CONTRIBUTING.md` SHALL state the three layers of the repository (toolkit, public repository, meta), what each
  holds, and the rule that a new skill serving only the development of AGNOS takes the prefix.
- **Rationale**: the rule concerns who develops AGNOS, so it stays out of the generic process instructions.
- **Priority**: Should
- **Acceptance Criteria**: Given `CONTRIBUTING.md`, When it is read, Then it gives the three layers and the prefix rule, And it gives
  the instructions file's line budget as 400 lines, And `agnos-sw-eng.instructions.md` is unchanged.
- **Dependencies**: ADR-MTA-001
