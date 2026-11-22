# PLAN-WEB-008: English text aligned on the French

## Overview
Translate again into `en.md` the fields of the site whose French text the owner changed, state OpenAI Codex support as coming in
both languages, and correct four typos of `fr.md` (owner request of 2026-11-13).

## References
- **Requirement refs**: RQ-WEB-003, RQ-WEB-007, RQ-WEB-009
- **ADR refs**: ADR-WEB-001 (DEC-WEB-003)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-WEB-020: Align the English text with the French
- **Tier**: M
- **Status**: Done
- **Description**: Retranslate from `fr.md` into `en.md` the Matrix, examples, Graph, History, Delivery and Quality fields that
  differ; write "OpenAI Codex support coming soon" in `hero.tools` and `start.step1-text` of both languages; correct "Vu
  chronologique", "abre", "implémention", "cérémonique" and "KPIs simple" in `fr.md`.
- **Requirement refs**: RQ-WEB-003, RQ-WEB-007, RQ-WEB-009
- **ADR refs**: ADR-WEB-001 (DEC-WEB-003)
- **Acceptance Criteria** (Gherkin): Given each field changed in `fr.md`, Then `en.md` states the same content in English; Given
  both files, Then the hero and step 1 state OpenAI Codex support as coming; Given the skill's tests, Then all pass; Given a
  build, Then it exits 0.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: field-by-field comparison script before the edit: 30 English fields lagging the French, all rewritten;
  `git diff --stat`: `en.md` 40+/39-, `fr.md` 6 lines; `python -m unittest discover -s tests`: 65 OK, 0 skipped; `build` exit 0.
- **Assumptions**: the owner's `TODO` note in the English `footer.developers` is left as is; the translation is reviewed by the
  owner on the rebuilt site.
