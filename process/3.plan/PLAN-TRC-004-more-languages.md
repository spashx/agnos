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
- **Status**: Done
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
- **Verification**: `JavaTest` 4/4 OK: `demo.shapes.Greeter.toString`, `.name`, `.Greeter` (constructor), not the
  interface's `area()`; `toString → name` on lines 8 and 9, external 1 (`println`); `toString` cites the ID above
  `@Override`; scopes `demo`, `demo.shapes` (the package) and `demo.shapes.Greeter`. Whole suite 118 OK, 1 skipped;
  Sonar: no finding.
- **Assumptions**: None

### TASK-TRC-034: JavaScript and Node.js
- **Tier**: L
- **Status**: Done
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
- **Verification**: `JavaScriptTest` 4/4 OK on `ui.mjs` and `server.cjs`: `start`, `helper` (arrow), `$`, `Panel.show`,
  `Panel.#paint`, `click`, `key` (object key), `load` (`exports.load = function`); `start → $`, `start → helper`,
  `Panel.show → Panel.#paint`, external 2 (`require`, `readFileSync`); `load` cites the ID above it; the only box is
  the class `Panel`. Whole suite 122 OK, 1 skipped (C and C++ unchanged with the new name rule); Sonar: no finding.
- **Assumptions**: the fixture is split into an ES module and a CommonJS file, to cover `.mjs` and `.cjs`; a call
  outside any function (a module's top-level `require`) belongs to no caller and is not counted, as in C++.

### TASK-TRC-035: Python
- **Tier**: L
- **Status**: Done
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
- **Verification**: `PythonTest` 4/4 OK: `Greeter.greet`, `Greeter.name`, `main`; `greet → name` (`self.name()`),
  `main → Greeter.greet`, external 2 (`print`, the class call `Greeter()`); `Greeter.name` cites the ID above
  `@staticmethod`, `greet` none; the only box is `Greeter`. The fixture repository's own `src/a.py` and
  `src/notrace.py` are now read: `PageDataTest` expects 14 functions (was 12) and 9 untraced (was 8), `untraced()`
  among them, not `covered()`. Whole suite 126 OK, 1 skipped; Sonar: no finding reported.
- **Assumptions**: None

### TASK-TRC-036: Rust
- **Tier**: L
- **Status**: Done
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
- **Verification**: `RustTest` 4/4 OK: `shapes::Square::new` (in `impl<T> Square<T>`), `shapes::convert`,
  `shapes::Area::area` (a trait's default method), `shapes::builds`, not `name()`; `builds → Square::new` and
  `builds → convert` (`convert::<u8>()`), no external, `println!` not a call; `builds` cites the `///` ID above
  `#[test]`, after a fix found by the test (Error Recovery, one attempt): a Rust line comment ends at column 0 of the
  next row, `comment_tops` now takes the row before; scopes `shapes` (namespace), `shapes::Square`, `shapes::Area`.
  Whole suite 130 OK, 1 skipped; Sonar on `callgraph.py`: no finding.
- **Assumptions**: a trait's default method is a function in the trait's box, its declaration without body is not.

### TASK-TRC-037: Documentation and a run on this repository
- **Tier**: M
- **Status**: Done
- **Description**: Update `SKILL.md` (delivered languages, what counts in each, the file-wide namespace and decorator
  rules), then run `--call-graph` on this repository's Python (`.github/skills`, `tools/`) and report the counts.
- **Requirement refs**: RQ-TRC-050, RQ-TRC-017, RQ-TRC-036
- **ADR refs**: ADR-TRC-004 (DEC-TRC-025, DEC-TRC-026)
- **Acceptance Criteria**: Given `SKILL.md`, Then it names the seven languages and the rules of DEC-TRC-026; Given this
  repository's Python scanned with `--call-graph`, When the generator runs, Then it exits 0 with Python functions and
  calls in its summary, and a function whose comment above cites an ID is linked to it.
- **Dependencies**: TASK-TRC-032 to TASK-TRC-036
- **Assignee**: AI
- **Verification**: `SKILL.md` names the seven languages, what a definition is in each, their boxes and the rules of
  DEC-TRC-026. `--sources .github/skills --sources tools --exclude fixtures --exclude __pycache__ --exclude vendor
  --call-graph`: exit 0, about 1 s, "call graph: 568 functions, 969 calls, ambiguous 62, external 1542" (344 Python, 224
  JavaScript); `file_functions` linked to RQ-TRC-028, RQ-TRC-031, DEC-TRC-016, TASK-TRC-010 of the comment above it,
  `plain_name` and `comment_tops` to DEC-TRC-026 of their docstrings. Without `--exclude vendor`, the minified
  `cytoscape.min.js` alone gives 1,369 functions and most of 1,440 ambiguous calls.
- **Assumptions**: the run excludes the skills' fixtures (their IDs are examples) and the vendored library; the
  worktree's `tools/` holds the four scripts of this branch.
