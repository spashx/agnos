# PLAN-TRC-012: A Skill Limited to its Contract, a Guide in the Page

## Overview
Move the reader's guide into the page and the rest into references first, then cut `SKILL.md`, so that no fact is lost on
the way. Page tests need the network. Full test suites run on a copy, through a subagent.

## References
- **Requirements**: RQ-TRC-098 to RQ-TRC-102; refined: RQ-TRC-017
- **ADRs**: ADR-TRC-012 (DEC-TRC-050 to DEC-TRC-052); ADR-TRC-002 (design system); extended: DEC-TRC-008

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-TRC-087: The Help dialog in the page
- **Tier**: M
- **Status**: Done
- **Description**: Accept ADR-TRC-012, note the extension in DEC-TRC-008 and RQ-TRC-017, and add the Help button and dialog from the former "What the page shows".
- **Requirement refs**: RQ-TRC-101, RQ-TRC-103
- **ADR refs**: ADR-TRC-012 (DEC-TRC-052), ADR-TRC-002
- **Acceptance Criteria**: Given the fixture, Then each criterion of RQ-TRC-101 holds in Gherkin-named page tests.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `test_help.py`: 6 tests OK. A review against the code corrected two imprecise statements. Escape itself is the browser's: the test closes through the Close button.
- **Assumptions**: the LinkedIn address is the one listed on the spashx GitHub profile; a "Search and details" topic holds what no tab owns; the guide's stale points of the former text were corrected against the code, not moved.

### TASK-TRC-088: The references and the contract
- **Tier**: M
- **Status**: Done
- **Description**: Write the three references from the former text, cut `SKILL.md` to its contract, shorten its description, realign the Claude Code pointer, extend the test of RQ-TRC-057 and add the tests of the size and the data format.
- **Requirement refs**: RQ-TRC-098, RQ-TRC-099, RQ-TRC-100, RQ-TRC-102, RQ-TRC-017, RQ-TRC-057
- **ADR refs**: ADR-TRC-012 (DEC-TRC-050, DEC-TRC-051)
- **Acceptance Criteria**: Given the tests, Then the criteria of RQ-TRC-100 and RQ-TRC-102 hold; Given each section of the former `SKILL.md`, Then a comparison finds its facts in the Help dialog or the references; Given a fresh subagent with the new `SKILL.md`, Then it runs the skill and reports the scores, and answers the `undefined` question of RQ-TRC-099 from one reference.
- **Dependencies**: TASK-TRC-087
- **Assignee**: AI
- **Verification**: `test_skill_contract.py`: 4 tests OK. Comparison by a subagent: rule, format and maintenance text found moved; its gaps and 5 inaccuracies of `data-format.md` fixed. Fresh subagent with the new `SKILL.md`: exit 0, line and scores reported, `undefined` answered from `references/rules.md` alone.
- **Assumptions**: the fresh-agent trial ran before the final small additions to `SKILL.md`; the contradiction between RQ-TRC-063 and its test is left for the owner.
