# FTR-PLG-004: Function Traceability Counts, and is Asked for Plainly

## Overview
Every function, method and class cites the requirement it implements, as the process already requires in its code section; the
Definition of Done says so in one line, and the perf center's score counts the functions that do not.

Source: the owner's session of 2026-11-05 in GitHub Copilot in VS Code, model chosen by the tool ("Auto", Copilot Free). Its
`prime_number.py` cited `RQ-SLG-001` in its file header only: the perf center found 7 untraced functions of 7 (corrected on
2026-11-05 from "3": the 4 tests, named `test_RQ_SLG_001_...`, cite no ID either), yet graded the project A 10/10, since
"functions traced" weighs nothing. The tests followed one reading of the traceability rule, which asks for IDs in "test case
names" while asking for all references in comments (RQ-PLG-026). The Claude Code session of 2026-11-04, on Claude Sonnet, had traced its
functions. Which of the model or the wording caused the difference is not known.

Out of scope: running the perf center before each commit (not chosen by the owner on 2026-11-05); choosing the model.

## Stakeholders
- **Owner**: the repository owner (maintainer of AGNOS).
- **Consumers**: developers using the AGNOS plugin and their agents; whoever reads the perf center's grade.

---

## Functional Requirements

### RQ-PLG-024: Untraced functions lower the score
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The perf center SHALL score the check "Functions traced" at the risk level medium (weight 5), as "Files traced", so that its findings lower the overall score and count in the findings total; WHILE the call graph is not computed, the check SHALL have no score and SHALL weigh nothing, as today. Amends RQ-TRC-035 and RQ-TRC-059 on that check's weight.
- **Rationale**: a function that cites no requirement breaks the process's code rule; graded A 10/10 with 7 untraced functions of 7, the page hid it.
- **Priority**: Must
- **Acceptance Criteria**: Given a call graph whose functions cite no ID, When the scorecard is computed, Then "Functions traced" has risk medium, its findings count in the total, And the overall score is below 10; Given no call graph, Then the check has no score And the overall score is unchanged; Given the page, Then the check's risk shown is read from the data, not written in the code.
- **Dependencies**: RQ-TRC-035, RQ-TRC-059

### RQ-PLG-025: The Definition of Done names functions
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The Definition of Done SHALL hold, for every tier, the item "Every new function, method and class cites its requirement ID in its doc comment or in the comment just above it".
- **Rationale**: the DoD said "every new artifact", which an agent may not apply to a function; the rule stood only in the prose of the code section.
- **Priority**: Must
- **Acceptance Criteria**: Given the process skill the release generates, Then its DoD matrix holds that item for S, M and L; Given the instructions file, Then it stays within 400 lines.
- **Dependencies**: RQ-PLG-003

### RQ-PLG-026: A test cites its requirement in a comment, not in its name
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The traceability rule of the process SHALL ask for a test's requirement ID in its doc comment or in the comment just above it, as for any function, and SHALL NOT ask for it in the test's name; a test's name stays Gherkin.
- **Rationale**: the rule listed "test case names" among the places of an ID while asking for every reference in comments; an agent read the first and named its tests `test_RQ_SLG_001_...`, which neither the comment rule nor the perf center reads as an ID.
- **Priority**: Must
- **Acceptance Criteria**: Given the process skill the release generates, When its MANDATORY TRACEABILITY section is read, Then it names the doc comments of test functions And no longer holds "test case names"; Given the instructions file, Then it stays within 400 lines.
- **Dependencies**: RQ-PLG-025
