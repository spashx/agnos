# agnos-perf-center — call graph: operational analysis and recommendations

**Addressee**: the agent that will define the evolution requirements.
**Subject**: the quality of the call graph produced by `callgraph.py`, and its effects on the `functions-traced` check.
**Status**: static analysis of the source. No new AGNOS ID is proposed here — writing the requirements remains yours.

---

## 1. Scope and method

**Base analysed**: `spashx/agnos`, branch `dev`, shallow clone.

| Artifact | Role in the analysis |
|---|---|
| `.github/skills/agnos-perf-center/scripts/callgraph.py` (405 l.) | read in full |
| `assets/callgraph/*.scm` (7 files) | read in full |
| `assets/callgraph/languages.json` | read |
| `requirements-callgraph.txt` | pinned grammar versions |
| `references/rules.md`, `references/data-format.md` | the scoring and data contract |
| `agnos-process/1.requirements/FTR-TRC-002-call-graph.md` | the requirements in force |
| `tests/test_callgraph.py` (966 l.), `tests/test_languages.py` (179 l.) | the pinned behaviour |
| `tests/fixtures/repo/calls/`, `tests/fixtures/languages/` | the actual test coverage |

**Levels of evidence used below**:

- **[P]** *proven* — established by reading the code, a `.scm` file or a test assertion, with a `file:line` reference.
- **[D]** *deduced* — a logical consequence of the code, not exercised by any test; needs empirical confirmation.
- **[V]** *to verify* — depends on a tree-sitter node name I could not confirm against the pinned grammars (the analysis environment had no network access and the grammars were not installed).

**Pinned versions** (`requirements-callgraph.txt`): `tree-sitter==0.25.2`, `tree-sitter-c==0.24.1`, `tree-sitter-cpp==0.23.4`, `tree-sitter-c-sharp==0.23.5`, `tree-sitter-java==0.23.5`, `tree-sitter-javascript==0.25.0`, `tree-sitter-python==0.25.0`, `tree-sitter-rust==0.24.2`. Every **[V]** point must be verified against these exact versions.

---

## 2. The arbitration criterion

The call graph enters the score through one check only. `references/rules.md:42`:

> `Functions traced (functions-traced)` | medium | functions (with `--call-graph`; no score without it) | **functions citing no ID**

Two consequences bound any evolution:

1. **Requirement coverage does not run through call edges.** `rules.md:14` defines `indirect` by the chain of process artifacts (DEC, TASK, ADR, PLAN, FTR), never by a function call. **[P]**
2. **The `functions-traced` check uses no edge.** It reads only `function["ids"]`, filled at `callgraph.py:198-200` from `cited`. **[P]**

**Criterion retained for ranking**: *what distorts the score comes before what degrades the graph's readability.* One defect found distorts the score (§4, R1). The others only affect the accuracy of the edges, hence how usable the page is.

---

## 3. Guiding principle, and the options rejected

The perf center measures the **implementation**: the code that executes an implementation. The unit of traceability is therefore the function, and every function must cite its own ID. `FTR-TRC-002-call-graph.md:86-88` states it:

> The trace generator SHALL link a function to every AGNOS ID written in its line range or in the comment just above […] *Rationale*: AGNOS puts requirement IDs in doc comments; the function is where they belong.

Two evolutions were examined and **must be rejected**. They look attractive, and an agent reading the code without this principle would propose them. They are recorded here so they are not reintroduced.

### 3.1 — REJECTED: inherit IDs from the enclosing scope

**Technical finding**: `callgraph.py:193` iterates over `caps[DEFINITION]` only. `caps[SCOPE]` serves `scope_names` (l. 177) and `declared_scopes` (l. 210) and nothing else. An ID written in the comment block above a class is therefore attached to no function, and every method of that class remains a `functions-traced` finding. **[P]**

**Grounds for rejection**: an ID on a class proves nothing about the implementation. It establishes no trace into the bodies of the methods, which is the code that actually runs. Inheriting it would turn a correct finding into apparent conformance — that is, into a false negative of the check, the costliest kind of defect for a traceability tool. The current behaviour matches the intent and `FTR-TRC-002`.

**For the requirement writing**: any evolution requirement must explicitly preserve this property. Do not frame it as a limitation to be fixed.

### 3.2 — REJECTED: an "indirectly traced" tier for `functions-traced`

**Proposal examined**: a function with no ID, called only by traced functions, would count as indirectly traced — by analogy with the `indirect` tier of requirements.

**Grounds for rejection**: the same, and more serious since it bears on the score. A traced caller says nothing about the callee's implementation. Moreover the edge that would ground the deduction may itself be wrong: §4-R4 and §5 show that the edges carry unresolved hypotheses. Grounding a score on a heuristic resolution imports the graph's uncertainty into the quality score.

**To retain**: call edges are a support for exploration and diagnosis. They must not become a source of conformance.

---

## 4. Recommendations

### R1 — Detect the files that do not parse

**Priority: high. This is the only defect found that distorts the score, and it does so in the dangerous direction.**

**Finding [P]**: `callgraph.py:68-69`

```python
def parse(self, language, data):
    return self.api.Parser(language).parse(data).root_node
```

No call to `root.has_error`, `is_error` or `is_missing` exists anywhere in `scripts/` (verified by searching every script of the skill). The tree-sitter parser is error-tolerant: it always produces a tree, inserting `ERROR` and `MISSING` nodes into it.

**Impact [D]**: a syntactically broken file, or one written in a dialect the pinned grammar does not cover, yields a degraded tree, hence few or no `@definition`. Functions absent from the graph cannot be reported as untraced. **The `functions-traced` score is therefore inflated by a parsing failure.** `files-traced` does not compensate: it looks only at the file's ID citations, not at its structure. `summary()` (l. 339-347) mentions missing packages only, never a degraded parse.

This failure mode is silent and monotonic in the wrong direction: the more broken a file is, the better the score looks.

**Proposal**: expose error detection as first-class data.

1. Read `root.has_error` per file in `file_functions` (l. 184) or in `analyse` (l. 395).
2. Add a counter to `CallGraph` (l. 330-337) along with the list of files concerned.
3. Carry it into `summary()` (l. 339) and into `callGraph.counts` (l. 374), hence into `references/data-format.md:64`.
4. A process decision to take: should a file that does not parse be a quality finding in its own right, or only a mention? A finding is defensible: a file the tool cannot read is not a traced file.

**Verification**: add to `tests/fixtures/languages/` one deliberately broken file per language, and assert that the counter reports it. Naming to follow: `test_<ID>_given_..._when_..._then_...` (the convention observed in `test_languages.py`, the ID in the doc comment per `DEC-PLG-021`).

**Cost**: low. Three to five lines of Python. No `.scm` to change. Common to all 7 languages, since `has_error` is a property of the tree-sitter core and not of any grammar.

**Risk**: the value of `callGraph.counts` changes, so the pinned page hash (`test_callgraph.py:32`, `DATA_BEFORE_PLAN_SHA256`) will have to be re-pinned.

---

### R2 — Break down the `external` counter

**Priority: high, as a prerequisite for arbitration.** Without this breakdown, R3 to R6 cannot be ranked on measurements.

**Finding [P]**: `callgraph.py:269-274`

```python
for (caller_index, name), lines in grouped.items():
    caller = graph.functions[caller_index]
    candidates = definitions.get((caller[LANGUAGE_FUNCTION], name), [])
    chosen = preferred(caller, candidates, separators[...]) if candidates else []
    if not chosen:
        graph.external += 1
```

`external` aggregates four heterogeneous causes:

| Cause | Nature | Reference |
|---|---|---|
| call to a library outside the scanned scope | **normal**, not fixable | — |
| unresolved constructor call | **a missed internal edge** | §R4 |
| cross-language call | a design limit | `callgraph.py:264`, key `(language, name)` |
| name rejected upstream by `NAME_RE` | not counted here, dropped at l. 229 | `callgraph.py:50`, `229` |

**Proof that the conflation is real and already visible [P]**: `tests/test_languages.py:140`

```python
self.assertEqual((0, 2), (self.graph.ambiguous, self.graph.external))      # print, the class Greeter()
```

In this single assertion the value `2` adds together a legitimate library call (`print`) and a missed internal edge (`Greeter()`). The number cannot tell them apart: the test's comment is the only source of that information.

**Proposal**: replace the single counter with a breakdown by cause, in `CallGraph` and then in `callGraph.counts`. Count the names dropped by `NAME_RE` at l. 229 as well — today they are invisible end to end.

**Verification**: rewrite the assertion above so it separates the two causes, which will document defect R4 instead of hiding it in a comment.

**Cost**: low. Pure Python, no `.scm`.

---

### R3 — Keep the call's receiver

**Priority: high. The best gain-to-cost ratio of the set.**

**Finding [P]**: `callgraph.py:135-137`

```python
def last_part(name):
    """The name a call is looked up by: the last part of 'a.b->c::d'."""
    return MEMBER_RE.split(name)[-1]
```

Called at l. 228, `last_part` discards everything before the last part. `self.f()`, `this.f()`, `other.f()` and `Type::f()` become indistinguishable: all reduce to `f`.

**Impact [D]**: resolution loses information which, for `self` and `this`, is **certain** and not heuristic — the callee belongs to the caller's class or to one of its ancestors. `preferred` (l. 239-254) can then only *prefer* the caller's class instead of *restricting* to it. When the name is common, the number of candidates can exceed `MAX_AMBIGUOUS = 5` (l. 43) and **the edge is lost** (l. 275-276).

Amplifying cases identified **[D]**:

- Python: `super().__init__()` reduces to `__init__`, hence to every `__init__` in the project.
- Rust: `Foo::new()` reduces to `new`, hence to every `new` in the project — a near-universal convention in Rust.
- Any language: `get`, `run`, `name`, `value`.

**Proposal**: keep the prefix produced by `plain_name(text_of(expression))` before calling `last_part`, carry it through to `resolve`, then add a restriction level ahead of `preferred`:

- receiver `self` / `this` → restrict to the candidates of the caller's class, then of its ancestors (depends on R5);
- receiver qualified by a known type or namespace (`Type::f`, `Mod.f`) → restrict to the candidates of that scope;
- unknown receiver (a local variable) → current behaviour unchanged.

Mind the semantic distinction: restricting and preferring are not the same operation. For a certain receiver, an empty list after restriction is valid information — the callee is out of scope — and must count as `external` rather than fall back to the whole project.

**Verification**: one case per language contrasting `self.f()` with `other.f()`, with two same-named definitions in distinct classes; assert that only the right edge exists. One Python case with six `__init__` and one `super().__init__()`, asserting that the edge is created where today it is lost.

**Cost**: low to moderate. Entirely in Python, **no `.scm` file to write** — the called expression is already captured by `@call.name` in all 7 languages. This is the only substantial gain in accuracy that adds no per-language cost.

---

### R4 — Capture constructor calls

**Priority: moderate. Needs a process decision before implementation, since the current behaviour is pinned by a test.**

**Finding [P]**: none of the 7 `.scm` files captures `object_creation_expression` or `new_expression` (exhaustive search over `assets/callgraph/*.scm`). The call captures are:

| Language | Call capture | Constructor captured as a definition? |
|---|---|---|
| java | `(method_invocation name: (identifier) @call.name) @call` | **yes**, `(constructor_declaration …) @definition`, named `Foo` |
| csharp | `(invocation_expression function: (_) @call.name) @call` | **yes**, `(constructor_declaration …) @definition`, named `Foo` |
| cpp | `(call_expression function: (_) @call.name) @call` | **yes** via `function_definition` **[D]** |
| javascript | `(call_expression function: (_) @call.name) @call` | **yes** via `method_definition`, named `constructor` |
| python | `(call function: (_) @call.name) @call` | `__init__` only; the class is a `@scope`, never a `@definition` |
| rust | `(call_expression function: (_) @call.name) @call` | not applicable (`Foo::new()` is an ordinary call) |
| c | `(call_expression function: (_) @call.name) @call` | not applicable |

**Proof that the defect is pinned, not overlooked [P]**: `tests/test_languages.py:137-140` asserts that the instantiation `Greeter()` in the Python fixture counts as `external`. The test's comment names it explicitly. **This is therefore not a latent bug: it is behaviour specified by the test.** Any evolution entails re-pinning that assertion, hence a traced decision.

**Proof of the unexercised case [P]**: `tests/fixtures/languages/java/Greeter.java` defines `public Greeter() {}`, captured as a function (`test_languages.py:80-82` asserts `demo.shapes.Greeter.Greeter` among the functions), but no fixture instantiates it. The same holds for C#. The constructor is therefore an **orphan node**: present in the graph, with no incoming edge at all. The defect exists but is not currently exercised by the tests on those two languages.

**Impact [D]**: constructors appear never to be called. The page shows them as roots, which distorts any reading of the call structure. The chain breaks upstream of the initialisation code, which often carries the most requirements.

**Proposal**, per language, with the real resolution cost:

- **java, csharp** — capture `object_creation_expression` with the type as `@call.name` **[V]**. Resolution then works **with no further change**, since the constructor is already a definition named `Foo`: `last_part("Foo")` yields `Foo`, which is the key of `definitions`. The most favourable gain-to-cost ratio.
- **cpp** — capture `new_expression` **[V]**. Note that stack construction (`Foo f(1);`) is a declaration, not a call expression: it will stay out of the graph. To be settled explicitly in the requirement so no expectation is left unmet.
- **javascript** — capturing `new_expression` **[V]** is not enough: the captured name would be `Foo` while the definition is named `constructor`. Needs a mapping in `resolve`.
- **python** — the instantiation is already captured as a `call`, but no definition carries the class name. Needs a class → `__init__` mapping, hence access to the scope from resolution. This is the costliest case.

**Recommended staging**: handle java and csharp first (one query line each, no code), then arbitrate cpp, javascript and python on the measurements coming from R2. The value of R2 shows here: without the breakdown of `external`, nothing says whether these calls are frequent in real projects.

**Constraint to recall**: `references/rules.md:52-55` holds that languages are data — adding a language must not change the scripts. The javascript and python variants above need code, and so depart from that principle. The requirement will have to either accept the departure or carry the mapping in `languages.json` to preserve the property.

---

### R5 — Add an "ancestor classes" level to resolution

**Priority: moderate.**

**Finding [P]**: `callgraph.py:239-254`

```python
scope = caller[KEY_SCOPE]
namespace = scope.rpartition(separator)[0]
levels = (
    lambda f: scope and f[KEY_SCOPE] == scope,
    lambda f: namespace and f[KEY_SCOPE] == namespace,
    lambda f: f[KEY_FILE] == caller[KEY_FILE],
    lambda f: folder_of(f[KEY_FILE]) == folder_of(caller[KEY_FILE]),
)
```

The class level is a **string equality** on the qualified scope.

**Impact [D]**: an inherited method has, by construction, a scope different from the caller's. It never satisfies level 1. Level 2 does not catch it either: `f[KEY_SCOPE] == namespace` selects only functions whose scope is *exactly* the namespace, that is, free functions — not the methods of a sibling class. A call to an inherited method therefore falls through to the file level, then the folder, then the whole project, with the risk of exceeding `MAX_AMBIGUOUS` and losing the edge.

This defect primarily affects java, csharp, cpp and python, where inheritance is structural.

**Proposal**: capture the inheritance clause (`superclass` / `extends` / `implements` / `base_clause` / the base-class list / the `argument_list` of a Python `class_definition`) **[V]** under a new capture name, build the ancestor chain by qualified scope, and insert a level between levels 1 and 2 of `preferred`.

**Implementation caveat [P]**: `captures_of` (l. 140-150) breaks on a fixed order of kinds and keeps only `caps[kind][0]`, that is **one node per capture name per match**. Adding a capture name requires changing the tuple at l. 145, and an inheritance clause with several types (`implements A, B`) cannot be captured under a single name without losing the later types. To be designed accordingly.

**Cost**: moderate. One pattern per language, plus resolution code. To be undertaken after R3, which it complements: restricting by `self` has its full effect only once the ancestors are known.

---

### R6 — Filter by arity

**Priority: low.**

**Finding [P]**: nothing in `callgraph.py` reads the parameter count of a definition or the argument count of a call. Resolution is purely nominal (l. 264, l. 271).

**Impact [D]**: overloads — C++, Java, C# — are not discriminated. Every variant of a name is a candidate, which feeds the `ambiguous` counter and the `MAX_AMBIGUOUS` overruns.

**Proposal**: count the arguments at the call site and the parameters at the definition, then use it as a filter *before* `preferred`. The filter must not be blocking: default arguments, variadics, implicit parameters and an explicit `this` all make strict equality wrong. A "compatible arity" filter rather than an "equal arity" one.

**Cost**: moderate. The parameter field name differs by language (`parameters` in python and java, `declarator` in cpp), which requires an extra entry in `languages.json` to respect `rules.md:52-55`. The gain is confined to projects with heavy overloading. Undertake only if R2 shows that the share of `ambiguous` justifies it.

---

### R7 — Make calls outside functions visible

**Priority: low, to be arbitrated.**

**Finding [P]**: `callgraph.py:229`

```python
if stack and NAME_RE.match(name):
```

An empty stack means the call is contained in no definition. The call is then simply dropped: it appears neither as an edge, nor in `external`, nor in `ambiguous`.

**Impact [D]**: module-level initialisation code — common in Python, JavaScript and Rust — is invisible. It is neither traced nor reported as untraced.

**Process decision required**: under the principle of §3, the unit of traceability is the function. A module-level call belongs to no function, so it has nothing to trace. Two defensible readings:

1. **The status quo is justified**: this code is not within the remit of `functions-traced`. It falls under `files-traced`, which already covers it through the file's ID citation.
2. **It is a gap to close**: this code runs, therefore it implements. One pseudo-function per file would make it visible and traceable.

I recommend **settling this explicitly** rather than leaving the drop implicit in the code. At a minimum, count these calls (see R2) to measure the volume before deciding.

---

## 5. A point of vocabulary to fix in the requirements

"Edge" and "call" do not denote the same thing, and the page shows both under the same label. To be clarified before any requirement carries a figure.

**Finding [P]**: `callgraph.py:281-284`

```python
link = links.setdefault((caller_index, index[id(callee)]), [ambiguous, set()])
link[1].update(lines)
...
graph.calls = [[caller, callee, ambiguous, sorted(lines)] for (caller, callee), (ambiguous, lines) in sorted(links.items())]
```

An edge is a quadruple `[caller index, callee index, ambiguous, [lines]]`, **aggregated per (caller, callee) pair**.

| Property | Consequence | Evidence |
|---|---|---|
| An edge aggregates every call site of a pair | ten calls from `f` to `g` give **one** edge carrying ten lines | l. 281-282 |
| `len(self.calls)` counts pairs | the "N calls" wording of `summary()` is an **edge count** | l. 283, l. 343 |
| A call site yields 0, 1, or 2 to 5 edges | 0 if `external`, if `> MAX_AMBIGUOUS`, if `NAME_RE` rejects, if outside any function | l. 229, 274-282 |
| An `ambiguous` edge is a **hypothesis** | 2 to 5 mutually exclusive edges; at most one matches the real call | l. 278-282 |
| `ambiguous` and `external` count `(caller, name)` pairs | not edges, not call sites | l. 267, 274-279 |

**Operational consequence**: the four values of `callGraph.counts` (`functions`, `calls`, `ambiguous`, `external`) can be neither added nor compared with one another — three different scales. A requirement setting a threshold on these numbers must first fix the unit. That is a further reason to undertake R2.

It is also the substantive argument of §3.2: a graph that contains unresolved disjunctions cannot ground a conformance score.

---

## 6. Design limits to document, not to fix

These are not defects. They should appear in the documentation so that requirements are not misdirected.

| Limit | Evidence | Comment |
|---|---|---|
| No cross-language edge is possible | l. 264: `definitions` is keyed by `(language, name)` | by design; inflates `external` on a polyglot repository |
| Non-conforming names are dropped | l. 50, l. 229: `NAME_RE` rejects `(*fp)` | function pointers, computed calls: beyond the reach of a syntactic analysis |
| Beyond 5 candidates, no edge | l. 43, l. 275-276 | an accepted choice; R3 reduces how often the case arises rather than the threshold |
| C has no scope | `languages.json`, entry `c` with no `scopes` key; l. 310, l. 323 | matches the language |
| The kind of an undeclared scope is guessed | l. 316: class when it is the innermost part, else namespace | a heuristic documented in `DEC-TRC-019` |

---

## 7. Ranked synthesis

| # | Recommendation | Effect | Cost | `.scm`? | Dependency |
|---|---|---|---|---|---|
| **R1** | detect parsing errors | **fixes a distorted score** | low | no | — |
| **R2** | break down `external` | makes quality measurable | low | no | — |
| **R3** | keep the receiver | edge accuracy | low/moderate | **no** | — |
| **R4a** | constructors, java and csharp | missing edges | low | yes, 1 line | decision + re-pinning |
| **R5** | ancestor level | edge accuracy | moderate | yes | after R3 |
| **R4b** | constructors, cpp, js, python | missing edges | moderate | yes + code | after R2 |
| **R6** | arity filter | edge accuracy | moderate | yes + `languages.json` | after R2 |
| **R7** | calls outside functions | process decision | low | no | measure first |

**Recommended sequence**: R1 and R2 first, independently — R1 because it fixes the score, R2 because it conditions every later arbitration. Then R3, the best gain with no per-language cost. Then R4a. The rest on the measurements R2 will have made available.

---

## 8. New functions worth considering

Compatible with the principle of §3, since they serve exploration and diagnosis rather than conformance.

1. **Roots and unreachable functions**, computable from `graph.calls` at no cost. A double use: exploration on the page, and **diagnosis** — a high proportion of constructors among the roots is the direct signature of defect R4. Not to be turned into a quality finding: a function unreachable by static analysis is not thereby untraced (entry point, callback, reflection).
2. **Reverse impact analysis**: which requirements reach a given function. `callGraph.ids` and `callGraph.calls` suffice. This is the case where propagation along the edges is legitimate, since it serves exploration and does not attribute conformance. State in the interface that `ambiguous` edges are hypotheses.
3. **Cycle detection**, only if function 2 is adopted, to bound the traversal.

---

## 9. What was not verified

Methodological honesty — to be cleared before the requirements are written:

- **The tree-sitter node names marked [V]**: `object_creation_expression`, `new_expression`, and the inheritance-clause nodes could not be confirmed against the pinned versions. The analysis environment had no network access and the grammars were not installed. **To confirm before any requirement is written**: `pip install -r requirements-callgraph.txt`, then inspect the tree on a minimal case per language.
- **Nothing was executed**: `callgraph.py` was not run and no test was executed. Every **[D]** point is a deduction from reading, not a measurement. Each recommendation carries a verification procedure to that end.
- **`perf_center.py` and `scorecard.py` were not read in full** — only the lines bearing on the call graph and the scoring. Part of the expected handling may already exist downstream; to be confirmed before opening a requirement on R1 and R2.
- **The real volumetry is unknown**: there is no measurement of how often the R3 to R7 cases arise in a real project. That is exactly what R2 would provide, and the reason for placing it first despite its having no direct effect on graph quality.
