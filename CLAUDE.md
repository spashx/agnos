# AGNOS Process — Claude Code Entry Point

@.github/instructions/agnos-sw-eng.instructions.md

## Tool Mapping (Claude Code)

<!-- RQ-AGT-001 -->
The imported instruction file is written to be tool-neutral; these Claude Code specifics are worth
calling out explicitly:

- **User questions**: where the process says `askQuestion` / `AskUserQuestion`, use the
  `AskUserQuestion` tool.
- **Init skill**: use the skill named `agnos-init`. Under Claude Code it is discovered at
  `.claude/skills/agnos-init/SKILL.md`, which points to the canonical procedure at
  `.github/skills/agnos-init/SKILL.md` — read and follow that procedure. <!-- RQ-INI-009 -->
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
- **Traceability skill**: use the skill named `agnos-trace`. Under Claude Code it is discovered at
  `.claude/skills/agnos-trace/SKILL.md`, which points to the canonical procedure at
  `.github/skills/agnos-trace/SKILL.md` — read and follow that procedure. <!-- RQ-AGT-001 -->
