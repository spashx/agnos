# AGNOS — Lightweight Software Engineering Process for Agentic AI

**AGNOS is an ultra-lightweight engineering process for tiger teams and solo experts who build
software with agentic AI.** It puts two things first — **end-to-end traceability** and
**deterministic indexing** — so that AI-driven development stays controllable as the codebase grows.

Every requirement can be followed, by a single `grep`, from its definition through its
architecture decisions, its tasks and its Git commits, down to the functions that implement it.

![AGNOS overview](agnos-overview.png)

> This README is an overview for human readers and is not normative. The AI agent executes the
> process from [`.github/instructions/agnos-sw-eng.instructions.md`](.github/instructions/agnos-sw-eng.instructions.md).
> New to AGNOS? Start with **[GETTING_STARTED.MD](GETTING_STARTED.MD)**, a complete worked session.

---

## What AGNOS Provides

| Component | What it does |
|---|---|
| **The process** | Requirements (EARS) → Architecture Decision Records → Plans and tasks (Gherkin), each artifact with a unique ID and explicit links to the others. |
| **`agnos-init`** | Adds AGNOS to a project: one explicit call completes its `CLAUDE.md` and `AGENTS.md` with a delimited block, leaving every other byte untouched, and creates its `process/` folders. |
| **`agnos-index`** | Deterministically regenerates `process/INDEX.idx.md`, the index of every artifact (ID, line range, status, title), so the agent reads only what it needs. |
| **`agnos-git-workflow`** | One session branch, one commit per task, with the artifact IDs validated and written into every commit message: the traceability is unique and permanent in the Git history. |
| **`agnos-design-system`** | Template and procedure for the design system every UI project defines before its first UI requirement: all visual values become traceable tokens. |
| **`agnos-perf-center`** | Generates a complete offline application to monitor the process's execution on a project and explore its traceability matrix — coverage, quality score and grade, interactive graph — down to the implementing functions and their call graph, and, with `--history`, who (humans and agents) changed each requirement and its code over time. |

**Delivered as:** one marketplace holding the plugin `agnos`, for Claude Code, GitHub Copilot and OpenAI Codex.
**Scripts for:** Windows (PowerShell 5.1), Linux and macOS (bash).

---

## Adding AGNOS to a Project

**1. Install the plugin**, where `<marketplace>` is this marketplace's folder or Git address:

| Tool | Commands |
|---|---|
| Claude Code | `claude plugin marketplace add <marketplace>`, then `claude plugin install agnos@agnos-marketplace` |
| GitHub Copilot CLI | `copilot plugin marketplace add <marketplace>`, then `copilot plugin install agnos@agnos-marketplace` |
| OpenAI Codex | `codex plugin marketplace add <marketplace>`, then install the plugin from the ChatGPT desktop app, as Codex's documentation says |

**2. Ask your agent to call the `agnos-init` skill once**, from your project's root. This step is required: until it runs, an agent in your project does not know about AGNOS.

Commit the result and start a new agent session. Your own content stays as it is: AGNOS only owns the lines between its `AGNOS:BEGIN` and `AGNOS:END` markers. To update a project after AGNOS changes, call it again.

**What was tested** <!-- RQ-PLG-008 -->

| Tool or system | Result |
|---|---|
| Claude Code, Windows | Installed from a local folder; `agnos-init` and `agnos-index` run; the block loads the process; an agent found and run. A full session is not tested yet. |
| GitHub Copilot CLI, Windows | Installed from a local folder; `agnos-init` and `agnos-index` run; the block loads the process on a work question, not on a trivial one; an agent found and run. A full session is not tested yet. |
| GitHub Copilot in VS Code | Not tested. |
| OpenAI Codex | Not tested: its catalogue and manifest follow its documentation. |
| Linux | Scripts and their tests pass on Ubuntu 24.04, except the tests that need a browser or tree-sitter, not run there. No agent tool was run on it. |
| macOS | Not tested: it shares the Linux scripts. |
| Install from a remote Git repository | Not tested. |

---

## How a Session Runs

1. **Load the process** — in an initialised project, the `agnos-init` block orders the agent to invoke the skill
   `agnos-process`, which holds the process, before any other action.
2. **Resolve the session state** — when you ask to start a session, the agent detects the platform,
   asks whether unit tests are required, and writes `process/_sessionstate/session.yaml`.
3. **Index and scan** — `agnos-index` rebuilds the index; the agent reviews open requirements,
   ADRs and plans from it.
4. **Open the branch** — `agnos-git-workflow start-session <TRI>` creates `feature/<TRI>`. Nothing
   is ever committed to `main`.
5. **Plan and execute** — each task is tiered, approved by you (Definition of Ready), then delivered
   against the Definition of Done.
6. **Commit** — `agnos-git-workflow commit-task` builds and validates the commit message.
7. **Close** — the agent reports the work done and the process friction metrics.

---

## Core Concepts

### Artifacts and identifiers

| Phase | Location | Artifacts | Format |
|---|---|---|---|
| Requirements | `process/1.requirements/` | `FTR-*` features, `RQ-*` requirements | EARS statements, Gherkin acceptance criteria |
| Architecture | `process/2.architecture/` | `ADR-*` records, `DEC-*` decisions | Context, Decision, Consequences, Alternatives, Mermaid diagram |
| Planning | `process/3.plan/` | `PLAN-*` plans, `TASK-*` tasks | Tier, Gherkin criteria, Verification, Assumptions |
| Session state | `process/_sessionstate/` | `session.yaml`, `METRICS_LOG.md` | Version-controlled |

Every identifier follows `<TYPE>-<TRI>-<NNN>` — for example `RQ-USR-001`, `ADR-USR-002`,
`TASK-USR-003` — where `<TRI>` is a three-letter uppercase trigram for the functional area.
IDs appear, as comments, in every related document, source file, test name and commit message.

### Task tiers — flexible ceremony, zero-tolerance traceability

The tier scales the ceremony to the size of the change: a small fix goes straight to code, a
cross-cutting change gets an ADR and a plan. What never scales down is traceability — every tier,
including S, references its requirement ID and passes the same Definition of Done.

| Tier | Scope | Tests | ADR | Plan |
|---|---|:-:|:-:|:-:|
| **S** | Edit of 5 lines or fewer, no new file, no new public API | — | — | — |
| **M** | New method, class or file, contained in one module | ✓ | — | — |
| **L** | Cross-cutting change, new public API or new dependency | ✓ | ✓ | ✓ |

When in doubt, a task is tiered M. A Tier S task that turns out to need a new file is re-tiered
before work continues. Tests apply while `session.unit_tests` is `true`.

### Definition of Done (all tiers)

- Every new artifact references a requirement ID.
- No string or numeric literal is duplicated inline.
- No failing test is modified to force it to pass.
- UI code consumes design-system tokens only.
- Code compiles and passes static analysis.

Tier M and L tasks are **test-first**, and close with a **Verification** field built from tool
output produced in the session, and an **Assumptions** field listing every inference made.

### Session variables

```yaml
unit_tests: true     # user variable — asked at every session start
platform: windows    # system variable — detected: windows | macos | linux
```

New variables are added to the schema in the instructions file; existing keys are never renamed
or removed.

---

## Continuous Improvement

- **Friction metrics** — at session close the agent reports four counters (user questions, error
  recoveries, re-tiered tasks, discrepancies caught by verification) and appends them to
  `METRICS_LOG.md`.
- **Recursive self-improvement** — when a counter is non-zero, the agent proposes improvements to
  the instructions file, run as numbered iterations under an 800-line budget, one confirmed theme at
  a time. This mode is only ever started by you.
- **Context management** — beyond 10 tasks, the agent writes a checkpoint in `process/3.plan/` and
  recommends a new session.

---

## Repository Map

| Path | Content |
|---|---|
| [GETTING_STARTED.MD](GETTING_STARTED.MD) | Worked example — start here |
| [.github/instructions/agnos-sw-eng.instructions.md](.github/instructions/agnos-sw-eng.instructions.md) | The normative process |
| [.github/skills/](.github/skills/) | The skills: `agnos-init`, `agnos-index`, `agnos-git-workflow`, `agnos-design-system`, `agnos-perf-center` |
