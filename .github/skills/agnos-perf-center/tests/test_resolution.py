"""Tests of the call resolution accuracy of the call graph (FTR-TRC-002, ADR-TRC-021): the receiver (RQ-TRC-124), the
constructions (RQ-TRC-125), the ancestor classes (RQ-TRC-126), the arity (RQ-TRC-127), and calls never tracing a function
(RQ-TRC-128). Each case writes its sources in a temporary folder, so the fixtures' pinned counts do not change.

Run from the repository root: python -m unittest discover -s .github/skills/agnos-perf-center/tests -v
Skipped without the packages of requirements-callgraph.txt.
"""
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))

import callgraph as cg  # noqa: E402
import perf_center as tm  # noqa: E402
from test_callgraph import HAS_TREE_SITTER, NEEDS_TREE_SITTER, calls_of  # noqa: E402

CITED_ID = "RQ-DEM-001"


def graph_of(sources, cited=None):
    """The call graph of {file name: text}, written in a temporary folder; cited: {file name: [(line, ID, proof)]}."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for name, text in sources.items():
            (root / name).write_text(text, encoding="utf-8")
        return cg.analyse(sorted((name, root / name) for name in sources), cited or {}, tm.evidence)


def callees(graph, caller):
    """{callee: ambiguous} of one caller, by qualified names."""
    return {callee: ambiguous for (source, callee), (ambiguous, _) in calls_of(graph).items() if source == caller}


# RQ-TRC-124: per language, a function of C calling A's f through the class name, another calling f through an object.
QUALIFIED_RECEIVER = {
    "python": ("m.py", "class A:\n    def f(self):\n        return 0\n\n\nclass B:\n    def f(self):\n        return 1\n\n\n"
                       "class C:\n    def g(self):\n        return A.f(self)\n\n    def h(self, other):\n"
                       "        return other.f()\n", ".", "A", "B", "C"),
    "java": ("M.java", "class A { static int f() { return 0; } }\nclass B { int f() { return 1; } }\n"
                       "class C { int g() { return A.f(); } int h(B other) { return other.f(); } }\n", ".", "A", "B", "C"),
    "javascript": ("m.js", "class A { static f() { return 0; } }\nclass B { f() { return 1; } }\n"
                           "class C { g() { return A.f(); } h(other) { return other.f(); } }\n", ".", "A", "B", "C"),
    "cpp": ("m.cpp", "struct A { static int f() { return 0; } };\nstruct B { int f() { return 1; } };\n"
                     "struct C { int g() { return A::f(); } int h(B& other) { return other.f(); } };\n", "::", "A", "B", "C"),
    "csharp": ("M.cs", "class A { public static int f() { return 0; } }\nclass B { public int f() { return 1; } }\n"
                       "class C { int g() { return A.f(); } int h(B other) { return other.f(); } }\n", ".", "A", "B", "C"),
    "rust": ("m.rs", "struct A;\nstruct B;\nstruct C;\nimpl A { fn f() -> u8 { 0 } }\nimpl B { fn f(&self) -> u8 { 1 } }\n"
                     "impl C { fn g(&self) -> u8 { A::f() } fn h(&self, other: &B) -> u8 { other.f() } }\n", "::",
             "A", "B", "C"),
}

# RQ-TRC-124: per language, a method calling g through its own object, g being defined in another class only.
OWN_RECEIVER_MISSING = {
    "python": ("m.py", "class A:\n    def f(self):\n        return self.g()\n\n\nclass B:\n    def g(self):\n"
                       "        return 0\n", "A.f"),
    "java": ("M.java", "class A { int f() { return this.g(); } }\nclass B { int g() { return 0; } }\n", "A.f"),
    "javascript": ("m.js", "class A { f() { return this.g(); } }\nclass B { g() { return 0; } }\n", "A.f"),
    "cpp": ("m.cpp", "struct A { int f() { return this->g(); } };\nstruct B { int g() { return 0; } };\n", "A::f"),
    "csharp": ("M.cs", "class A { int f() { return this.g(); } }\nclass B { int g() { return 0; } }\n", "A.f"),
    "rust": ("m.rs", "struct A;\nstruct B;\nimpl A { fn f(&self) -> u8 { self.g() } }\n"
                     "impl B { fn g(&self) -> u8 { 0 } }\n", "A::f"),
}


@unittest.skipUnless(HAS_TREE_SITTER, NEEDS_TREE_SITTER)
class ReceiverTest(unittest.TestCase):
    """TASK-TRC-113: RQ-TRC-124 (DEC-TRC-069, DEC-TRC-070, DEC-TRC-071)."""

    def test_RQ_TRC_124_given_a_call_through_a_class_name_when_analysed_then_it_is_one_plain_link_to_that_class(self):
        for language, (name, text, sep, a, b, c) in QUALIFIED_RECEIVER.items():
            with self.subTest(language):
                graph = graph_of({name: text})
                self.assertEqual({f"{a}{sep}f": False}, callees(graph, f"{c}{sep}g"))

    def test_RQ_TRC_124_given_a_call_through_another_object_when_analysed_then_it_stays_ambiguous(self):
        for language, (name, text, sep, a, b, c) in QUALIFIED_RECEIVER.items():
            with self.subTest(language):
                graph = graph_of({name: text})
                self.assertEqual({f"{a}{sep}f": True, f"{b}{sep}f": True}, callees(graph, f"{c}{sep}h"))

    def test_RQ_TRC_124_given_an_own_object_call_to_a_method_of_another_class_only_then_no_link_and_library(self):
        for language, (name, text, caller) in OWN_RECEIVER_MISSING.items():
            with self.subTest(language):
                graph = graph_of({name: text})
                self.assertEqual({}, callees(graph, caller))
                self.assertEqual((1, 1), (graph.external, graph.unresolved["library"]))

    def test_RQ_TRC_124_given_this_in_a_function_of_no_class_when_analysed_then_the_name_resolves_as_before(self):
        graph = graph_of({"m.js": "function g() { return 0; }\nfunction f() { return this.g(); }\n"})
        self.assertEqual({"g": False}, callees(graph, "f"))


@unittest.skipUnless(HAS_TREE_SITTER, NEEDS_TREE_SITTER)
class ConformanceTest(unittest.TestCase):
    """TASK-TRC-113: RQ-TRC-128 (DEC-TRC-018): neither the enclosing class nor the callers trace a function."""

    def test_RQ_TRC_128_given_an_id_above_a_class_when_analysed_then_its_method_cites_no_id(self):
        graph = graph_of({"m.py": "# RQ-DEM-001\nclass A:\n    def f(self):\n        return 0\n"},
                         {"m.py": [(1, CITED_ID, "# RQ-DEM-001")]})
        self.assertEqual({}, {f["qualified"]: f for f in graph.functions}["A.f"]["ids"])

    def test_RQ_TRC_128_given_an_untraced_function_called_only_by_traced_ones_when_analysed_then_it_cites_no_id(self):
        graph = graph_of({"m.py": "# RQ-DEM-001\ndef f():\n    return g()\n\n\ndef g():\n    return 0\n"},
                         {"m.py": [(1, CITED_ID, "# RQ-DEM-001")]})
        functions = {f["qualified"]: f for f in graph.functions}
        self.assertEqual(({CITED_ID}, {}), (set(functions["f"]["ids"]), functions["g"]["ids"]))
        self.assertEqual({"g": False}, callees(graph, "f"))


if __name__ == "__main__":
    unittest.main()
