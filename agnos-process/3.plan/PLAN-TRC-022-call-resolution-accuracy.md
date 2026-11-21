# PLAN-TRC-022: Call resolution accuracy

## Overview
Resolve calls by their receiver, link constructions to constructors, prefer ancestor classes and tell overloads apart by
arity, without ever tracing a function by its calls (recommendations R3 to R6 of
`insights/callgraph-operational-analysis.md`, owner choice of 2026-11-21).

## References
- **Requirements**: RQ-TRC-124, RQ-TRC-125, RQ-TRC-126, RQ-TRC-127, RQ-TRC-128, RQ-TRC-029, RQ-TRC-123
- **ADRs**: ADR-TRC-021 (DEC-TRC-069 to DEC-TRC-073), ADR-TRC-004 (DEC-TRC-014, DEC-TRC-015, DEC-TRC-018)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-TRC-112: Specify call resolution accuracy
- **Tier**: M
- **Status**: Done
- **Description**: Write RQ-TRC-124 to RQ-TRC-128 and the amendment of RQ-TRC-029 in FTR-TRC-002, ADR-TRC-021 and this plan.
- **Requirement refs**: RQ-TRC-124, RQ-TRC-125, RQ-TRC-126, RQ-TRC-127, RQ-TRC-128
- **ADR refs**: ADR-TRC-021
- **Acceptance Criteria** (Gherkin): Given the owner's scope, When the artifacts are written, Then the index lists RQ-TRC-124
  to RQ-TRC-128, ADR-TRC-021, DEC-TRC-069 to DEC-TRC-073 and TASK-TRC-112 to TASK-TRC-116 with no duplicate.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `build-index.ps1`: exit 0, 1009 entries, 159 documents; the index lists RQ-TRC-124 to RQ-TRC-128,
  ADR-TRC-021, DEC-TRC-069 to DEC-TRC-073, TASK-TRC-112 to TASK-TRC-116; no duplicate reported.
- **Assumptions**: the node names were checked on the pinned grammars (`object_creation_expression`, `new_expression`,
  `superclass`, `super_interfaces`, `base_list`, `base_class_clause`, `class_heritage`, `superclasses`, `impl_item trait:`);
  Java needs a receiver capture, its call name being the identifier alone.

### TASK-TRC-113: Resolve calls by their receiver
- **Tier**: L
- **Status**: Done
- **Description**: Merge captures per node, read the receiver of each call (`@call.receiver` in Java), the `self` and
  `super` words of the language table, restrict the candidates before the preferences, documentation.
- **Requirement refs**: RQ-TRC-124, RQ-TRC-128, RQ-TRC-029
- **ADR refs**: ADR-TRC-021 (DEC-TRC-069, DEC-TRC-070, DEC-TRC-071)
- **Acceptance Criteria** (Gherkin): the acceptance criteria of RQ-TRC-124 (the ancestor ones once TASK-TRC-115 is done)
  and of RQ-TRC-128; Given the skill's suite, Then all pass.
- **Dependencies**: TASK-TRC-112
- **Assignee**: AI
- **Verification**: tests first: `test_resolution.py` 12 sub-cases failed (class-name receiver and own-object receiver, six
  languages each). After: `test_resolution.py` 6 run, OK; full suite 429 run, OK, 3 skipped (opt-in performance tests,
  `AGNOS_PERF_CENTER_PERF=1`, not measured); fixtures' pinned counts unchanged. Demo (client + service): 2 links removed,
  both `super().__init__()` linked to the method itself.
- **Assumptions**: RQ-TRC-124's first criterion amended (from a method of `A`, the class preference already picks `A.f`);
  Python's `cls` is an own-object word; a receiver names a scope when its last part is a scope's last part.

### TASK-TRC-114: Link constructions to constructors
- **Tier**: M
- **Status**: Not Started
- **Description**: Capture `new` in the Java, C#, C++ and JavaScript query files, give the `constructor` name of Python and
  JavaScript in the language table, resolve a construction to the constructors of its class, documentation.
- **Requirement refs**: RQ-TRC-125, RQ-TRC-123
- **ADR refs**: ADR-TRC-021 (DEC-TRC-069, DEC-TRC-070)
- **Acceptance Criteria** (Gherkin): the acceptance criteria of RQ-TRC-125; Given the skill's suite, Then all pass.
- **Dependencies**: TASK-TRC-113
- **Assignee**: AI
- **Verification**: pending
- **Assumptions**: pending

### TASK-TRC-115: Add ancestor classes to resolution
- **Tier**: L
- **Status**: Done
- **Description**: Capture `@scope.base` in the query files of the languages with classes, build the ancestors breadth
  first, add their level, list the unknown base names in the summary line and the call graph card, documentation.
- **Requirement refs**: RQ-TRC-126, RQ-TRC-124
- **ADR refs**: ADR-TRC-021 (DEC-TRC-069, DEC-TRC-072)
- **Acceptance Criteria** (Gherkin): the acceptance criteria of RQ-TRC-126 and the ancestor ones of RQ-TRC-124; Given the
  skill's suite, Then all pass.
- **Dependencies**: TASK-TRC-113
- **Assignee**: AI
- **Verification**: tests first: `AncestorTest` 11 failures and 1 error (`no attribute 'unknown_bases'`), six languages.
  After: `test_resolution.py` 13 run, OK (the card's tooltip test in headless Edge included); full suite 436 run, OK,
  3 skipped (opt-in performance tests, `AGNOS_PERF_CENTER_PERF=1`, not measured); `node --check assets/matrix.js` exit 0.
  Demo: `ReservationConflict.__init__` now linked to `RoombookError.__init__`; unknown bases are library classes only.
- **Assumptions**: the summary line names the first 10 unknown bases and counts the others; the card's figure is
  "Unknown base classes", its tooltip listing them all; a Python base other than a name or an attribute (`Generic[T]`,
  `metaclass=`) is not read.

### TASK-TRC-116: Filter candidates by arity
- **Tier**: M
- **Status**: Not Started
- **Description**: Capture `@definition.parameters` and `@call.arguments`, give the `arity` node types in the language
  table, keep the compatible candidates when there are several, documentation.
- **Requirement refs**: RQ-TRC-127
- **ADR refs**: ADR-TRC-021 (DEC-TRC-069, DEC-TRC-070, DEC-TRC-073)
- **Acceptance Criteria** (Gherkin): the acceptance criteria of RQ-TRC-127; Given the skill's suite, Then all pass.
- **Dependencies**: TASK-TRC-113
- **Assignee**: AI
- **Verification**: pending
- **Assumptions**: pending
