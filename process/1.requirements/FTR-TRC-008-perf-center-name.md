# FTR-TRC-008: The Skill Named after its Role, agnos-perf-center

## Overview
The skill `agnos-trace` no longer only traces: with its quality score, history, deliveries and friction, it monitors how the
AGNOS process performs on a given project. It becomes `agnos-perf-center`, and what it produces carries that name. "Performance"
means the execution of the process, not the speed of the code. The IDs `*-TRC-*` do not change (ADR-TRC-013).

## Stakeholders
- **Owner**: the repository owner.
- **Consumers**: agents choosing the skill from its description; readers of the page; projects ignoring its outputs.

---

## Functional Requirements

### RQ-TRC-104: The skill's name and description
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The skill SHALL be named `agnos-perf-center` in its folders and entry points, and its description SHALL say that it monitors the execution of the process, not the speed of the code.
- **Rationale**: an agent chooses a skill from its name and description, and "performance" alone would suggest code speed.
- **Priority**: Must
- **Acceptance Criteria**: Given the repository, When the two `SKILL.md` files are read, Then each is under a folder `agnos-perf-center` and carries that name, And each description contains "not code speed".
- **Dependencies**: RQ-TRC-017, RQ-TRC-102, DEC-TRC-053

### RQ-TRC-105: What the skill produces carries the name
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The generator SHALL be `scripts/perf_center.py`, its default output `<process>/PERF-CENTER.html`, with `PERF-CENTER.json` and `PERF-CENTER.data.js` beside it, and the page's title SHALL start with "Performance center".
- **Rationale**: a reader of the outputs meets the same name as the agent running the skill. Amends RQ-TRC-001.
- **Priority**: Must
- **Acceptance Criteria**: Given a process folder and a source folder, When the generator runs without `--out`, Then it exits 0 and `process/PERF-CENTER.html` exists with its two data files.
- **Dependencies**: RQ-TRC-001, RQ-TRC-010, DEC-TRC-054

### RQ-TRC-106: No live file keeps the former names
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: IF a tracked file other than a plan, `CHANGELOG.md`, the index or this feature's artifacts holds the skill's former name, its former script or its former outputs, THEN the skill's tests SHALL fail.
- **Rationale**: a name left behind leads an agent to a path that no longer exists; plans and the changelog are history and keep theirs.
- **Priority**: Must
- **Acceptance Criteria**: Given the repository, When the skill's tests run, Then no such file holds a former name, And the rule MANDATORY TRACEABILITY of the instructions is still there.
- **Dependencies**: DEC-TRC-055
