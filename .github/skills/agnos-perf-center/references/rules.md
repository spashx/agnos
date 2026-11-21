# agnos-perf-center: rules behind the results

<!-- RQ-TRC-099, DEC-TRC-051. RQ-TRC-003 to RQ-TRC-008; call graph: FTR-TRC-002, ADR-TRC-004, ADR-TRC-005;
     history: FTR-HST-001, FTR-HST-002, FTR-HST-003, ADR-HST-001; delivery: FTR-TRC-004, ADR-TRC-009, FTR-TRC-006;
     quality: ADR-TRC-008; matrix and detail panel: ADR-TRC-006, ADR-TRC-007. -->

Read this file to explain a finding or a figure. The format of the data is in `data-format.md`. `#<ID>` in the page's URL selects
an element, `#box:<qualified name>` or `#box:(global)` a scope.

## Rules behind the numbers <!-- DEC-TRC-003, DEC-TRC-004 -->

- A link is an ID written in an element's own lines (its line range without the ranges of the elements it contains), or
  in a source line. `<A> to <B>`, `<A>–<B>`, `<A>..<B>` of one type and trigram count as every defined ID between them.
- **covered**: a source file cites the requirement; **indirect**: a source file cites a decision, task, ADR, plan or
  feature linked to it (another requirement does not count); **uncovered**: neither.
- Findings (the elements that fail a check): `uncovered`, `untasked` (no task cites the requirement), `task-no-rq` (the
  task cites no requirement itself), `adr-no-rq` (neither the ADR nor its decisions cite one), `empty` (feature without
  requirement, ADR without decision, plan without task), `isolated` (no link touches the element or what it contains),
  `undefined` (cited, not in the index), `untraced-files` (scanned files citing no ID).
- An ID quoted in prose as an example (a test fixture's IDs in a task's Verification field, an instructions file's
  sample IDs) is a citation like any other: it shows as `undefined`. Write such examples without the ID grammar.

## Quality scoring <!-- ADR-TRC-008: DEC-TRC-032, DEC-TRC-033; RQ-TRC-058, RQ-TRC-059, RQ-TRC-064 -->

Each rule is a **check**. Its **score** is 10 × the share of its **population** that is not a finding, to one decimal
(half up); a check with an empty population has no score and weighs nothing. The **overall score** is the average of
the checks' scores weighted by risk (critical 10, high 7.5, medium 5, low 2.5, informational 0); the **grade** is A
from 9, B from 7.5, C from 6, D from 4, else E. A trigram's score uses the same formula on its own elements (the checks
whose findings are IDs; files and functions belong to no trigram). The checks, risks, weights and thresholds are data in
`assets/scoring.json`: change a number there, never in the code.

| Check (key) | Risk | Population | Findings |
|---|---|---|---|
| Requirements covered (`covered`) | critical | requirements | `uncovered` |
| IDs defined (`defined`) | critical | IDs cited by the process or the sources | `undefined` |
| Requirements tasked (`tasked`) | high | requirements | `untasked` |
| Tasks with a requirement (`task-rq`) | high | tasks | `task-no-rq` |
| ADRs with a requirement (`adr-rq`) | medium | ADRs | `adr-no-rq` |
| Containers not empty (`filled`) | medium | features, ADRs, plans | `empty` |
| Elements connected (`connected`) | medium | defined elements | `isolated` |
| Source files traced (`files-traced`) | medium | scanned files | `untraced-files` |
| Functions traced (`functions-traced`) | medium | functions (with `--call-graph`; no score without it) | functions citing no ID |
| Files parsed (`files-parsed`) <!-- RQ-TRC-122, DEC-TRC-067 --> | medium | files the call graph read (with `--call-graph`) | files whose tree holds an `ERROR` or `MISSING` node |

## Call graph <!-- DEC-TRC-013 to DEC-TRC-018 -->

- A function is a definition with a body; its key is `fn:<file>:<first line>`. It cites the IDs of its lines and of the
  comment block just above it. Coverage and the findings stay file-based: the call graph changes none of them.
- A file whose syntax tree-sitter cannot fully read (a syntax error, a dialect its grammar lacks) still gives the functions
  found in it, and is a finding of `files-parsed`: some of its functions may be missing, and with them their findings
  of `functions-traced`. <!-- RQ-TRC-122, DEC-TRC-067 -->
- Calls are resolved by name: among the definitions of that name in the caller's language, the first non-empty set of
  the caller's class, its namespace, its file, its folder, the project. One left: a call link; two to five: one link to
  each, marked ambiguous; more: counted as ambiguous; none: counted as external. Macros, virtual dispatch, function
  pointers and callbacks are not followed.
- A certain receiver comes first <!-- RQ-TRC-124, DEC-TRC-071 -->: through the caller's own object (`self`, `this`,
  `Self`, the `self` words of the language table) the callee is looked for in the caller's class, then its ancestors;
  through its parent (`super`, `base`, `super()`) in its ancestors only; through a qualifier naming a scope (`A::f`,
  `A.f`) in that scope, then its ancestors. Found nowhere there: external, `library`, never a guess elsewhere. Through
  any other receiver (`other.f()`), or `this` in a function of no class: by name, as above. Counts are per caller and
  call signature (name, receiver).
- A call never traces a function <!-- RQ-TRC-128, DEC-TRC-018 -->: `functions-traced` reads only the IDs of a function's
  own lines and of the comment block just above it, never those of its class, namespace, callers or callees.
- An unresolved call is counted by cause <!-- RQ-TRC-123, DEC-TRC-068 -->: `constructor` (the name of a class or other
  scope of the caller's language, as Python's `Greeter()`), `cross-language` (defined only in another language),
  `library` (defined in no scanned file), which make up `external`; and, outside it, `unnamed` (a call through an
  expression that is no name, as `(*fp)()`) and `top-level` (a call outside any function, as module-level code).
- Languages are data: `assets/callgraph/languages.json` (extensions, grammar wheel and module, query file, scope
  separator) and one query file `assets/callgraph/<language>.scm` with the captures `@definition`, `@definition.name`,
  `@scope`, `@scope.name`, `@call`, `@call.name`, `@comment`, and the optional `@call.receiver` where the called name is
  a node of its own (Java); the captures of all the matches of one node are merged <!-- DEC-TRC-069 -->. To add a language: one table entry, one query file, its
  grammar wheel pinned in `requirements-callgraph.txt`; no script changes.
- Delivered, each with the grammar the tree-sitter project publishes <!-- RQ-TRC-050, DEC-TRC-025 -->: C (`.c`), C++ (`.h`
  read as C++), C# (`.cs`), Java (`.java`), JavaScript and Node.js (`.js .jsx .mjs .cjs`), Python (`.py .pyw`; stubs
  `.pyi` are not read) and Rust (`.rs`). A definition is a function or method with a body: in JavaScript also a function
  or arrow given to a name, an object key or a member (`exports.f = function`); a Rust trait's default method; not an
  interface or abstract method. `new`, macros (`println!`) and calls outside any function are not calls.
- What differs between languages is settled in their query files <!-- DEC-TRC-026 -->: Java's `package a.b;` and C#'s
  `namespace A.B;` stand before the classes, so the file's root node is captured as that namespace's scope; Python's
  decorators and Rust's attributes are captured as `@comment`, so the comment block above them reaches the definition.
- Boxes come from the entry's `scopes` map <!-- DEC-TRC-019 -->: each scope node type its query captures as `@scope`, with
  the box kind it stands for, `namespace` or `class`. C++ maps `namespace_definition` to `namespace` and
  `class_specifier`, `struct_specifier`, `union_specifier` to `class`; C has no scope (`{}`), so its functions are in
  `(global)`. C# and Java: namespaces (the package) and classes, structs, interfaces, enums, records; Rust: inline
  `mod` blocks, `impl` blocks by their type and traits; JavaScript and Python: classes only, a module being a file, so
  their classes are in `(global)`. To give a new language its boxes, list its grammar's node types for packages, modules or namespaces (`namespace`)
  and for classes, structs or interfaces (`class`). A scope whose node type is not listed, like a qualifier part no
  scanned file declares (a class declared in a header outside the sources), gets a guessed kind: the innermost part of
  a method's qualifier is a class, the outer parts namespaces. Anonymous namespaces and
  lambdas make no box.


## History <!-- FTR-HST-001; ADR-HST-001: DEC-HST-001 to DEC-HST-004, DEC-HST-010 -->

- `scripts/history.py` is loaded only with `--history`; it runs the `git` command, nothing else beyond the standard
  library. Without `--history`, git is not run and the data file is unchanged.
- An **intervention** is a non-merge commit that changed lines of an element's definition (its range in
  `process.idx.md`), of a function's range (with `--call-graph`), or of a scanned file. The ranges of the working tree are
  followed back through every earlier version, across renames and merges, from one `git log -p -U0 -M -m --parents`
  over the process and source folders, as `git log -L` follows one range. Merge commits and uncommitted changes credit
  no one. The changed lines are counted as git's `--numstat` counts them, a hunk's removed lines in proportion of its
  added lines in the range.
- An **identity** is the commit's author (never its committer, who may be the service that merged), after the
  repository's `.mailmap`, and each `Co-Authored-By` co-author. Humans sharing an e-mail address (ignoring case) are one
  identity, named by their most frequent name; an agent is one name and address, since the models of one vendor share a
  no-reply address. An identity is an **agent** when its name or address matches a pattern of `assets/agents.json`
  (edit it to class another assistant), else a **human**; a commit is `human`, `agent` or `together`.
- The period: `--history-since` is given to git, and the author date is then checked against the same cutoff;
  `--history-depth` is git's `--max-count`. A shallow clone is read as far as it goes and marked `shallow`.

## Delivery <!-- FTR-TRC-004; ADR-TRC-009: DEC-TRC-036 to DEC-TRC-038 -->

- A task's **delivery** is the first commit of the history read that turns its `- **Status**:` line to `Done`,
  found in the same log as the history (no other git command). Its date is the commit's author date (the author's own
  day), its deliverers the commit's identities, its tier the `- **Tier**: S|M|L` line of the working tree; a commit
  that changed that line marks it **re-tiered**. Git records when a task is closed, never when its execution began: the
  tab measures throughput, never a duration.
- **Set aside**, shown in the table and counted in no figure: `created-done` (Done from the commit that created it),
  `annotated` (text after Done), `reopened` (its status left Done later), `no-tier`.
- **Points** per tier, **throughput** = points ÷ active days, an **active day** being a day with a commit authored or
  co-authored by an identity the filters keep; when the history read is cut (`--history-since`, `--history-depth`,
  shallow clone) its first day is left out of the periods. A task is **reworked** when a `fix` commit names it, or a
  requirement it cites, in its subject within the rework window.
- `assets/delivery.json` holds the tiers and their points (S 1, M 3, L 8), the rework window (14 days), the month
  threshold (12 weeks), the ready-made ranges and the two default ones: change a number there, never in the code.
- A session of `_sessionstate/METRICS_LOG.md` counts when its row is in the file at HEAD and its commit in the history
  read; **friction per session** is the sum of its four counters over the sessions of a period, divided by them.
