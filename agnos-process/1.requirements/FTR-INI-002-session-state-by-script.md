# FTR-INI-002: Session State Written by a Script

## Overview
The session state (`session.yaml`) and the friction-metrics row are written by a script of a dedicated skill, `agnos-session`,
instead of by the agent. Its content is the trigram the user gives, whether tests run, and the detected platform; it is rewritten
whole at every session start and is no longer version-controlled. The process asks the user about tests, then calls the script.

Out of scope: migrating existing projects (a major release, possibly breaking, says what changes), checking the trigram against
the branch, recording when a session started or whether one was left open.

## Stakeholders
- **Owner**: the repository owner (maintainer of AGNOS).
- **Consumers**: the agents running START SESSION and END SESSION; `agnos-perf-center`, which reads `METRICS_LOG.md`; `agnos-init`;
  `agnos-meta-demo`.

---

## Functional Requirements

### RQ-INI-011: `init` rewrites the session state
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN `agnos-session init --tri <TRI> --tests <true|false>` is called from a project's root, the script SHALL
  overwrite `agnos-process/_sessionstate/session.yaml` with exactly the keys `tri`, `tests` and `platform`, in that order, keeping
  no key of the former file, and SHALL print a table of the three names and values; its PowerShell 5.1 and sh versions SHALL write
  the same bytes.
- **Rationale**: the state then comes from a script, not from what an agent writes, and a stale key of an earlier session cannot survive.
- **Priority**: Must
- **Acceptance Criteria**: Given a `session.yaml` holding `unit_tests: true` and a key `extra`, When `init --tri ABC --tests false`
  runs, Then the file holds only `tri: ABC`, `tests: false` and `platform: <detected>`, And the table shows the same three values;
  Given the same arguments and platform, When each version runs, Then the files are byte-identical.
- **Dependencies**: ADR-INI-002, RQ-INI-013

### RQ-INI-012: Invalid arguments write nothing
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: IF `--tri` or `--tests` is missing, IF the trigram is not three uppercase letters, or IF `--tests` is not `true` or
  `false`, THEN `agnos-session init` SHALL name the argument on the error stream, SHALL leave `session.yaml` unchanged and SHALL exit 1.
- **Rationale**: a session must not start on a default the user did not choose.
- **Priority**: Must
- **Acceptance Criteria**: Given an existing `session.yaml`, When `init --tri abc --tests true`, `init --tests true` or
  `init --tri ABC --tests yes` runs, Then it exits 1, And the error names the argument, And the file's bytes are unchanged.
- **Dependencies**: RQ-INI-011

### RQ-INI-013: The platform is detected by the script
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The PowerShell version SHALL set `platform` to `linux` when the variable `IsLinux` exists and is true, to `macos`
  when `IsMacOS` exists and is true, and otherwise to `windows`; the sh version SHALL map `uname -s` `Linux` to `linux`, `Darwin`
  to `macos` and a value starting with `MINGW`, `MSYS` or `CYGWIN` to `windows`, and SHALL exit 1 writing nothing on any other value.
- **Rationale**: Windows PowerShell 5.1 has no `IsLinux`, PowerShell 7 exists on Linux and macOS, and sh runs on Windows under Git Bash.
- **Priority**: Must
- **Acceptance Criteria**: Given `uname -s` simulated as `Linux`, `Darwin`, `MINGW64_NT-10.0` or `SunOS`, When the sh version runs,
  Then `platform` is `linux`, `macos`, `windows`, or it exits 1 and writes nothing; Given `IsLinux` or `IsMacOS` simulated as true,
  When the PowerShell version runs, Then `platform` is `linux` or `macos`; Given Windows PowerShell 5.1, Then it is `windows`.
- **Dependencies**: ADR-INI-002

### RQ-INI-014: `show` prints the session state
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: WHEN `agnos-session show` is called, the script SHALL print the values of `session.yaml` on one line; IF the file
  is absent, THEN it SHALL say so on the error stream and exit 1.
- **Rationale**: an agent reloads the state with one command before applying a guard, without parsing YAML itself.
- **Priority**: Must
- **Acceptance Criteria**: Given a `session.yaml` written by `init`, When `show` runs, Then it prints `tri=ABC tests=false
  platform=windows` and exits 0; Given no `session.yaml`, When `show` runs, Then it exits 1.
- **Dependencies**: RQ-INI-011

### RQ-INI-015: `close` appends the metrics row
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN `agnos-session close <questions> <recoveries> <re-tiered> <verification>` is called with four non-negative
  integers, the script SHALL read the trigram from `session.yaml`, SHALL append `| <date> | <TRI> | <q> | <r> | <t> | <v> |` to
  `agnos-process/_sessionstate/METRICS_LOG.md`, creating the file with its title and header first if absent, and SHALL print the row;
  IF a counter is not a non-negative integer or `session.yaml` is absent, THEN it SHALL write nothing and exit 1.
- **Rationale**: the row is read by `agnos-perf-center` with a fixed pattern; a script keeps it in that format.
- **Priority**: Must
- **Acceptance Criteria**: Given `tri: ABC` and no `METRICS_LOG.md`, When `close 1 0 0 2` runs, Then the file holds the header and
  one row matching `FRICTION_ROW_RE` of `agnos-perf-center` with `ABC`, `1`, `0`, `0`, `2`; Given an existing log, When `close` runs
  again, Then only one line is added at its end; Given `close 1 x 0 0`, Then it exits 1, And the log is unchanged.
- **Dependencies**: RQ-INI-011, DEC-TRC-045

### RQ-INI-016: The session state is not version-controlled
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE `agnos-process/_sessionstate/session.yaml` is not ignored by git in the target, `agnos-init` SHALL add that
  path to the target's `.gitignore`, creating it if absent; WHILE it is already ignored, it SHALL leave `.gitignore` unchanged; in a
  target that is not a git repository, it SHALL compare the lines of `.gitignore` instead. `METRICS_LOG.md` SHALL stay version-controlled.
- **Rationale**: the state belongs to one session on one machine; the metrics log is read from the history by `agnos-perf-center`.
- **Priority**: Must
- **Acceptance Criteria**: Given a git target without `.gitignore`, When `agnos-init` runs, Then `.gitignore` holds the path, And
  `git check-ignore` confirms it; Given a `.gitignore` already ignoring `agnos-process/_sessionstate/`, When it runs, Then the file is
  unchanged; Given a second run, Then nothing changes; Given both script versions, Then they write the same bytes.
- **Dependencies**: RQ-INI-001, RQ-INI-003

### RQ-INI-017: The process calls the skill
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The instructions file SHALL have START SESSION ask the user whether tests run, then call `agnos-session init`;
  SHALL have the state reloaded with `agnos-session show` before a Tier M or L task; SHALL have END SESSION persist the metrics with
  `agnos-session close`; SHALL name the session variable `tests`; and SHALL stay within 400 lines.
- **Rationale**: the agent asks and decides, the script writes; one name for one key in every document.
- **Priority**: Must
- **Acceptance Criteria**: Given the instructions file, Then `unit_tests` appears nowhere, And START SESSION and END SESSION name the
  three sub-commands, And the file has at most 400 lines.
- **Dependencies**: RQ-INI-011, RQ-INI-014, RQ-INI-015, RQ-PLG-019

---

## Non-Functional Requirements

### RQ-INI-018: The skill follows the documented practices
- **Category**: Non-Functional
- **NFR Type**: Maintainability
- **EARS Type**: Ubiquitous
- **Statement**: `agnos-session` SHALL be a process skill with its Claude Code pointer, listed in `CLAUDE.md` and `AGENTS.md`, its
  `name` equal to its folder, its `description` saying what it does and when, and its paths read from the generated layout copies.
- **Metric**: description at most 1,024 characters; `SKILL.md` under 500 lines; no path literal of `agnos-process/` in its scripts.
- **Measurement Method**: a unit test reads the front matter, the line count, the two lists and the scripts.
- **Priority**: Should
- **Acceptance Criteria**: Given the skill, When its test runs, Then each metric holds, And `disable-model-invocation` is absent.
- **Dependencies**: RQ-INI-009, DEC-PLG-027
