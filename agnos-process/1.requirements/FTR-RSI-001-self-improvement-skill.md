# FTR-RSI-001: Recursive self-improvement as a skill

<!-- FTR-RSI-001: RQ-RSI-001 to RQ-RSI-003 / ADR-RSI-001 -->

## Overview
The RECURSIVE SELF-IMPROVEMENT SESSIONS section of the instructions file holds a procedure that only
matters while a session improves the process, yet it is loaded in every session, in a file 14 lines
under its ceiling. This feature moves that procedure into a skill, `agnos-self-improvement`, as was
done for the design system (FTR-DSY-001). The skill resolves the improvement target from an explicit
declaration, in AGNOS's own development as in a plugin user's project, and measures the line budget
of that target with a script.

## Stakeholders
- **Owner**: AGNOS process maintainer (this repository)
- **Consumers**: AI agents running a recursive self-improvement session, in this repository or in a
  project where the AGNOS plugin is installed

---

## Functional Requirements

### RQ-RSI-001: The self-improvement procedure is provided by a skill
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE a session runs numbered iterations to improve the process, the agent SHALL
  follow the procedure of the `agnos-self-improvement` skill; the instructions file SHALL keep only
  the trigger of that section, the pointer to the skill and the rule never to edit a file of an
  installed plugin, and its END SESSION step 3 SHALL point to the skill.
- **Rationale**: A procedure used only in some sessions should not take lines from a file loaded in
  all of them.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** the instructions file and `.github/skills/agnos-self-improvement/SKILL.md`
  - **When** the RECURSIVE SELF-IMPROVEMENT SESSIONS section is read
  - **Then** it holds the trigger, the pointer to the skill and the rule on plugin files, and no
    other rule of the procedure
  - **And** the skill holds the iteration tagging, the budget across the effort, one theme at a
    time, the conflict check and the rule to keep the target's structure
  - **And** both `.github` and `.claude` entry points of the skill exist
- **Dependencies**: RQ-PLG-018, RQ-DSY-001

### RQ-RSI-002: The improvement target is always declared
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: The skill SHALL take the improvement target from the sentence
  `` `<path>` is the improvement target `` in the project's `CLAUDE.md` or `AGENTS.md`; IF no such
  declaration is found, or the declared path lies outside the project's git root, THEN the skill
  SHALL stop with an error and SHALL NOT fall back to any other file. Amends RQ-PLG-018: the clause
  "this file otherwise" is removed.
- **Rationale**: A fallback on the instructions file would, in a plugin user's project with a
  missing block, direct improvements to a file of the plugin.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** a project whose `CLAUDE.md` declares `` `agnos-process/project-rules.md` is the improvement target ``
  - **When** the skill resolves the target
  - **Then** it gives `agnos-process/project-rules.md`
  - **Given** a project with no declaration
  - **When** the skill resolves the target
  - **Then** it exits with an error naming the missing declaration
  - **Given** a declaration of a path outside the git root
  - **When** the skill resolves the target
  - **Then** it exits with an error naming that path
- **Dependencies**: RQ-PLG-018

### RQ-RSI-003: The line budget of the target is measured
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the budget is requested, the skill SHALL print the target, its ceiling, its
  current line count and the lines left, and SHALL exit with an error if the count exceeds the
  ceiling; the ceiling SHALL be the one stated by the instructions file's sentence
  "SHALL NOT exceed <N> lines" when the target is the instructions file, otherwise the value given
  by the declaration as `` `<path>` is the improvement target, at most <N> lines ``, otherwise 100.
- **Rationale**: A project's rules file is loaded in every session too, and had no ceiling.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** the target is the instructions file, which states a ceiling of 400 lines
  - **When** the budget is requested
  - **Then** the ceiling printed is 400
  - **Given** the target is `agnos-process/project-rules.md` with no ceiling declared
  - **When** the budget is requested
  - **Then** the ceiling printed is 100
  - **Given** a target over its ceiling
  - **When** the budget is requested
  - **Then** the skill exits with an error
- **Dependencies**: RQ-RSI-002, RQ-PLG-019

---

## Non-Functional Requirements

### RQ-RSI-004: One portable script
- **Category**: Non-Functional
- **NFR Type**: Portability
- **EARS Type**: Ubiquitous
- **Statement**: The skill's script SHALL be a single Python file using the standard library only,
  run unchanged on Windows, Linux and macOS.
- **Metric**: one `.py` file, zero third-party import
- **Measurement Method**: unit tests run on Windows; review of the imports
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** the skill's `scripts/` folder
  - **When** its files and imports are listed
  - **Then** there is one Python file and every import is from the standard library
- **Dependencies**: RQ-RSI-003
