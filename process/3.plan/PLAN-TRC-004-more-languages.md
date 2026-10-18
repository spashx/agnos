# PLAN-TRC-004: C#, Java, JavaScript, Python and Rust in the Call Graph

## Overview
Implement RQ-TRC-050 after ADR-TRC-004 (DEC-TRC-025, DEC-TRC-026): one table entry, one query file, one pinned grammar
wheel of the tree-sitter project and one fixture per language, then the skill's documentation and a run on this
repository's Python. The fixtures stand in `tests/fixtures/languages/`, outside the scanned fixture repository, so the
counts of the existing tests do not change.

## References
- **Requirements**: RQ-TRC-050; RQ-TRC-028 to RQ-TRC-032, RQ-TRC-047 (what each language must give), RQ-TRC-039,
  RQ-TRC-040 (pinned, reproducible)
- **ADRs**: ADR-TRC-004 (DEC-TRC-014, DEC-TRC-015, DEC-TRC-025, DEC-TRC-026), ADR-TRC-005 (DEC-TRC-019)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-TRC-032: C#
- **Tier**: L
- **Status**: Done
- **Description**: Add the `csharp` entry (`.cs`, `tree-sitter-c-sharp`, separator `.`, scopes), `csharp.scm` and the
  pinned wheel; methods with a block or `=>` body, constructors, local functions; block and file-scoped namespaces.
- **Requirement refs**: RQ-TRC-050, RQ-TRC-032, RQ-TRC-047
- **ADR refs**: ADR-TRC-004 (DEC-TRC-025, DEC-TRC-026), ADR-TRC-005 (DEC-TRC-019)
- **Acceptance Criteria**: Given a fixture `.cs` file with `namespace A.B;`, a class whose method calls another and
  `Console.WriteLine`, and an ID above an `[Attribute]` method, When analysed, Then the functions are `A.B.C.m` and
  `A.B.C.n`, `m` calls `n`, the library call is external, the attributed method is linked to the ID, and the scopes are
  `A`, `A.B` (namespace) and `A.B.C` (class).
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `CSharpTest` 4/4 OK: `Demo.Shapes.Greeter.Greet`, `.Name` (`=>`), `.Greeter` (constructor),
  `Demo.Data.Store.Count` and its local `Twice`, not the interface's `Area()`; `Greet → Name`, `Count → Twice`, external
  1 (`WriteLine`); `Greet` cites the ID above `[Obsolete]`; scopes `Demo`, `Demo.Shapes` (file-scoped), `Demo.Data`
  (block) namespaces, `Greeter`, `Store` classes. Whole suite 114 OK, 1 skipped; Sonar: no finding.
- **Assumptions**: a second fixture file covers the block namespace and the local function the description names; the
  fixture cites `RQ-DEM-001`, an ID of the fixture process.

### TASK-TRC-033: Java
- **Tier**: L
- **Status**: Not Started
- **Description**: Add the `java` entry (`.java`, `tree-sitter-java`, separator `.`, scopes), `java.scm` and the pinned
  wheel; methods and constructors with a body (no interface or abstract method); the package as the file's namespace.
- **Requirement refs**: RQ-TRC-050, RQ-TRC-032, RQ-TRC-047
- **ADR refs**: ADR-TRC-004 (DEC-TRC-025, DEC-TRC-026), ADR-TRC-005 (DEC-TRC-019)
- **Acceptance Criteria**: Given a fixture `.java` file with `package a.b;`, a class whose `@Override` method calls
  another and `System.out.println`, an interface method without body and an ID above the annotation, When analysed,
  Then the functions are `a.b.C.m` and `a.b.C.n` (the interface method is not one), `m` calls `n`, the library call is
  external, `m` is linked to the ID, and the scopes are `a`, `a.b` and `a.b.C`.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: —
- **Assumptions**: —

### TASK-TRC-034: JavaScript and Node.js
- **Tier**: L
- **Status**: Not Started
- **Description**: Add the `javascript` entry (`.js .jsx .mjs .cjs`, `tree-sitter-javascript`, separator `.`, classes),
  `javascript.scm` and the pinned wheel; function declarations, methods, functions and arrows given a name, an object
  key or a member (`exports.f = …`); a called name may hold `$` and start with `#` (DEC-TRC-026).
- **Requirement refs**: RQ-TRC-050, RQ-TRC-032, RQ-TRC-047
- **ADR refs**: ADR-TRC-004 (DEC-TRC-025, DEC-TRC-026), ADR-TRC-005 (DEC-TRC-019)
- **Acceptance Criteria**: Given a fixture `.js` file with an exported function, an arrow `const`, `exports.f =
  function`, a class whose method calls `this.#p()`, a call to `$()` defined in the file and to `require`, When
  analysed, Then each is a function, the class's methods are in its class box, the calls to `#p` and `$` are linked,
  `require` is external, and no namespace box exists.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: —
- **Assumptions**: —

### TASK-TRC-035: Python
- **Tier**: L
- **Status**: Not Started
- **Description**: Add the `python` entry (`.py .pyw`, `tree-sitter-python`, separator `.`, classes), `python.scm` and
  the pinned wheel; `def` as definitions, decorators captured as `@comment` (DEC-TRC-026).
- **Requirement refs**: RQ-TRC-050, RQ-TRC-031, RQ-TRC-032, RQ-TRC-047
- **ADR refs**: ADR-TRC-004 (DEC-TRC-025, DEC-TRC-026), ADR-TRC-005 (DEC-TRC-019)
- **Acceptance Criteria**: Given a fixture `.py` file with a class whose method calls `self.n()`, a module function
  calling `print`, and an ID in the comment above a `@staticmethod`, When analysed, Then the functions are `C.m`, `C.n`
  and `f`, `m` calls `n`, `print` is external, the decorated method is linked to the ID, and the only box is the class
  `C`.
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: —
- **Assumptions**: —

### TASK-TRC-036: Rust
- **Tier**: L
- **Status**: Not Started
- **Description**: Add the `rust` entry (`.rs`, `tree-sitter-rust`, separator `::`, scopes), `rust.scm` and the pinned
  wheel; `fn` with a body, inline `mod` as namespace, `impl` blocks (by their type) and traits as classes, attributes
  captured as `@comment`; the trailing `::` of a turbofish dropped (DEC-TRC-026).
- **Requirement refs**: RQ-TRC-050, RQ-TRC-031, RQ-TRC-032, RQ-TRC-047
- **ADR refs**: ADR-TRC-004 (DEC-TRC-025, DEC-TRC-026), ADR-TRC-005 (DEC-TRC-019)
- **Acceptance Criteria**: Given a fixture `.rs` file with `mod a`, `impl<T> S<T>` holding `new`, a `#[test]` function
  with an ID in the `///` comment above the attribute, calls `S::new()`, `g::<u8>()` and `println!`, When analysed, Then
  the functions are `a::S::new`, `a::g` and the test function, the two calls are linked, the macro is not a call, the
  test is linked to the ID, and the scopes are `a` (namespace) and `a::S` (class).
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: —
- **Assumptions**: —

### TASK-TRC-037: Documentation and a run on this repository
- **Tier**: M
- **Status**: Not Started
- **Description**: Update `SKILL.md` (delivered languages, what counts in each, the file-wide namespace and decorator
  rules), then run `--call-graph` on this repository's Python (`.github/skills`, `tools/`) and report the counts.
- **Requirement refs**: RQ-TRC-050, RQ-TRC-017, RQ-TRC-036
- **ADR refs**: ADR-TRC-004 (DEC-TRC-025, DEC-TRC-026)
- **Acceptance Criteria**: Given `SKILL.md`, Then it names the seven languages and the rules of DEC-TRC-026; Given this
  repository's Python scanned with `--call-graph`, When the generator runs, Then it exits 0 with Python functions and
  calls in its summary, and a function whose comment above cites an ID is linked to it.
- **Dependencies**: TASK-TRC-032 to TASK-TRC-036
- **Assignee**: AI
- **Verification**: —
- **Assumptions**: —
