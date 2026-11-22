# AGNOS Process — Claude Code Entry Point

<!-- RQ-AGT-002: AGENTS.md's own "Non-negotiable rules" and generic tool mapping load here too, so the
     approval gate and the other reminders are not carried by the instructions import alone. -->
@AGENTS.md
@.github/instructions/agnos-sw-eng.instructions.md
@agnos-process/project-rules.md

## Tool Mapping (Claude Code)

<!-- RQ-AGT-001 -->
The imported instruction file is written to be tool-neutral; these Claude Code specifics are worth
calling out explicitly:

- **User questions**: where the process says `askQuestion` / `AskUserQuestion`, use the
  `AskUserQuestion` tool.
- **Init skill**: use the skill named `agnos-init`. Under Claude Code it is discovered at
  `.claude/skills/agnos-init/SKILL.md`, which points to the canonical procedure at
  `.github/skills/agnos-init/SKILL.md` — read and follow that procedure. <!-- RQ-INI-009 -->
- **Session skill**: use the skill named `agnos-session`. Under Claude Code it is discovered at
  `.claude/skills/agnos-session/SKILL.md`, which points to the canonical procedure at
  `.github/skills/agnos-session/SKILL.md` — read and follow that procedure. <!-- RQ-INI-018 -->
- **Git workflow skill**: use the skill named `agnos-git-workflow`. Under Claude Code it is
  discovered at `.claude/skills/agnos-git-workflow/SKILL.md`, which points to the canonical
  procedure at `.github/skills/agnos-git-workflow/SKILL.md` — read and follow that procedure.
- **Index skill**: use the skill named `agnos-index`. Under Claude Code it is discovered at
  `.claude/skills/agnos-index/SKILL.md`, which points to the canonical procedure at
  `.github/skills/agnos-index/SKILL.md` — read and follow that procedure. <!-- RQ-IDX-010 -->
- **Design-system skill**: use the skill named `agnos-design-system`. Under Claude Code it is
  discovered at `.claude/skills/agnos-design-system/SKILL.md`, which points to the canonical
  procedure and template under `.github/skills/agnos-design-system/` — read and follow that
  procedure. <!-- RQ-DSY-001 -->
- **Graph skill**: use the skill named `agnos-graph`. Under Claude Code it is discovered at
  `.claude/skills/agnos-graph/SKILL.md`, which points to the canonical procedure at
  `.github/skills/agnos-graph/SKILL.md` — read and follow that procedure. <!-- RQ-TRC-133 -->
- **Performance center skill**: use the skill named `agnos-perf-center`. Under Claude Code it is discovered at
  `.claude/skills/agnos-perf-center/SKILL.md`, which points to the canonical procedure at
  `.github/skills/agnos-perf-center/SKILL.md` — read and follow that procedure. <!-- RQ-AGT-001 -->
- **Self-improvement skill**: use the skill named `agnos-self-improvement`. Under Claude Code it is
  discovered at `.claude/skills/agnos-self-improvement/SKILL.md`, which points to the canonical
  procedure at `.github/skills/agnos-self-improvement/SKILL.md` — read and follow that procedure.
  Its improvement target is declared in `AGENTS.md`, imported above. <!-- RQ-RSI-001, RQ-RSI-002 -->
