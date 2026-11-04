# AGNOS — Lightweight Software Engineering Process for Agentic AI

**AGNOS is an ultra-lightweight engineering process for tiger teams and solo experts who build
software with agentic AI.** It puts two things first — **end-to-end traceability** and
**deterministic indexing** — so that AI-driven development stays controllable as the codebase grows.

Every requirement can be followed, by a single `grep`, from its definition through its
architecture decisions, its tasks and its Git commits, down to the functions that implement it.

![AGNOS overview](agnos-overview.png)

> This README is an overview for human readers and is not normative. The AI agent executes the
> process from [`.github/instructions/agnos-sw-eng.instructions.md`](.github/instructions/agnos-sw-eng.instructions.md).

<!-- RQ-PLG-023 / DEC-PLG-018: this page addresses the plugin user; the guide holds the session and the concepts,
COMPATIBILITY.md the tools and systems checked, CONTRIBUTING.md the map of this repository. -->

---

## What AGNOS Provides

| Component | What it does |
|---|---|
| **The process** | Requirements (EARS) → Architecture Decision Records → Plans and tasks (Gherkin), each artifact with a unique ID and explicit links to the others. |
| **`agnos-init`** | Adds AGNOS to a project: one explicit call completes its `CLAUDE.md` and `AGENTS.md` with a delimited block, leaving every other byte untouched, creates its `process/` folders and writes the guide `AGNOS-GETTING-STARTED.md`. |
| **`agnos-index`** | Deterministically regenerates `process/INDEX.idx.md`, the index of every artifact (ID, line range, status, title), so the agent reads only what it needs. |
| **`agnos-git-workflow`** | One session branch, one commit per task, with the artifact IDs validated and written into every commit message: the traceability is unique and permanent in the Git history. |
| **`agnos-design-system`** | Template and procedure for the design system every UI project defines before its first UI requirement: all visual values become traceable tokens. |
| **`agnos-perf-center`** | Generates a complete application, opened from disk, to monitor the process's execution on a project and explore its traceability matrix — coverage, quality score and grade, interactive graph — down to the implementing functions and their call graph, and, with `--history`, who (humans and agents) changed each requirement and its code over time. |

**Delivered as:** one marketplace holding the plugin `agnos`, for Claude Code, GitHub Copilot and OpenAI Codex. Tested on Windows
with Claude Code and GitHub Copilot CLI: see [COMPATIBILITY.md](COMPATIBILITY.md) for each tool and system. <!-- RQ-PLG-008 -->

---

## Getting Started

**1. Install the plugin**, where `<marketplace>` is this marketplace's folder or Git address:

| Tool | Commands |
|---|---|
| Claude Code | `claude plugin marketplace add <marketplace>`, then `claude plugin install agnos@agnos-marketplace` |
| GitHub Copilot CLI | `copilot plugin marketplace add <marketplace>`, then `copilot plugin install agnos@agnos-marketplace` |
| OpenAI Codex | `codex plugin marketplace add <marketplace>`, then install the plugin from the ChatGPT desktop app, as Codex's documentation says |

**2. Ask your agent to call the `agnos-init` skill once**, from your project's root. This step is required: until it runs, an
agent in your project does not know about AGNOS. <!-- RQ-INI-007 --> Your own content stays as it is: AGNOS only owns the lines
between its `AGNOS:BEGIN` and `AGNOS:END` markers. To update a project after AGNOS changes, call it again.

**3. Open a new conversation in your tool**, so that it reads the block, **and in it ask the agent to start an AGNOS session.**
<!-- RQ-PLG-020 -->

**Then read `AGNOS-GETTING-STARTED.md`**, which `agnos-init` wrote at your project's root: a complete worked session, what you
type and what comes back, and the concepts behind it. Its source is
[the skill's template](.github/skills/agnos-init/assets/templates/AGNOS-GETTING-STARTED.md). <!-- RQ-PLG-021, RQ-PLG-022 -->

---

## License

AGNOS is distributed under the GNU Affero General Public License v3: see [LICENSE.md](LICENSE.md).
