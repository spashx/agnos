"""Tests of the call-graph languages after C and C++ (RQ-TRC-050, DEC-TRC-025, DEC-TRC-026), on
tests/fixtures/languages/<language>, one folder each, outside the fixture repository so its counts do not change.

Run from the repository root: python -m unittest discover -s .github/skills/agnos-trace/tests -v
Skipped without the packages of requirements-callgraph.txt.
"""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))

import callgraph as cg  # noqa: E402
import trace_matrix as tm  # noqa: E402
from test_callgraph import HAS_TREE_SITTER, NEEDS_TREE_SITTER, by_name, calls_of  # noqa: E402
from test_trace_matrix import PROCESS  # noqa: E402

LANGUAGES = HERE / "fixtures" / "languages"
CITED = "RQ-DEM-001"                    # the fixture process's ID each language fixture cites above one definition


def language_graph(folder):
    """The call graph of tests/fixtures/languages/<folder>, its IDs read as the fixture process defines them."""
    model = tm.build_process_model(PROCESS)
    scanned = tm.scan_sources(model, [LANGUAGES / folder], base=LANGUAGES)
    return cg.analyse(scanned, tm.code_citations(model), tm.evidence)


def scopes_of(graph):
    """{scope: (kind, parent scope or None)}."""
    names = [name for name, _, _ in graph.scopes]
    return {name: (kind, names[parent] if parent != cg.NO_SCOPE else None) for name, kind, parent in graph.scopes}


def call_links(graph):
    """{(caller, callee): ambiguous} of the graph's calls, by qualified names."""
    return {pair: ambiguous for pair, (ambiguous, _) in calls_of(graph).items()}


@unittest.skipUnless(HAS_TREE_SITTER, NEEDS_TREE_SITTER)
class CSharpTest(unittest.TestCase):
    """TASK-TRC-032: RQ-TRC-050, RQ-TRC-032, RQ-TRC-047 (DEC-TRC-025, DEC-TRC-026)."""

    @classmethod
    def setUpClass(cls):
        cls.graph = language_graph("csharp")
        cls.functions = by_name(cls.graph)

    def test_RQ_TRC_050_given_csharp_files_when_analysed_then_methods_constructors_and_local_functions_are_functions(
            self):
        self.assertEqual({"Demo.Shapes.Greeter.Greet", "Demo.Shapes.Greeter.Name", "Demo.Shapes.Greeter.Greeter",
                          "Demo.Data.Store.Count", "Demo.Data.Store.Twice"}, set(self.functions))   # not Area()
        self.assertEqual({"csharp"}, {f["language"] for f in self.graph.functions})

    def test_RQ_TRC_050_given_csharp_calls_when_analysed_then_they_are_linked_and_the_library_call_is_external(self):
        self.assertEqual({("Demo.Shapes.Greeter.Greet", "Demo.Shapes.Greeter.Name"): False,
                          ("Demo.Data.Store.Count", "Demo.Data.Store.Twice"): False}, call_links(self.graph))
        self.assertEqual((0, 1), (self.graph.ambiguous, self.graph.external))

    def test_RQ_TRC_050_given_an_id_above_an_attributed_csharp_method_when_analysed_then_the_method_cites_it(self):
        self.assertEqual({CITED}, set(self.functions["Demo.Shapes.Greeter.Greet"]["ids"]))

    def test_RQ_TRC_050_given_file_scoped_and_block_namespaces_when_analysed_then_they_and_the_classes_are_scopes(self):
        self.assertEqual({"Demo": ("namespace", None), "Demo.Shapes": ("namespace", "Demo"),
                          "Demo.Shapes.Greeter": ("class", "Demo.Shapes"), "Demo.Data": ("namespace", "Demo"),
                          "Demo.Data.Store": ("class", "Demo.Data")}, scopes_of(self.graph))


@unittest.skipUnless(HAS_TREE_SITTER, NEEDS_TREE_SITTER)
class JavaTest(unittest.TestCase):
    """TASK-TRC-033: RQ-TRC-050, RQ-TRC-032, RQ-TRC-047 (DEC-TRC-025, DEC-TRC-026)."""

    @classmethod
    def setUpClass(cls):
        cls.graph = language_graph("java")
        cls.functions = by_name(cls.graph)

    def test_RQ_TRC_050_given_a_java_file_when_analysed_then_methods_and_constructors_with_a_body_are_functions(self):
        self.assertEqual({"demo.shapes.Greeter.toString", "demo.shapes.Greeter.name", "demo.shapes.Greeter.Greeter"},
                         set(self.functions))                                                # not area()
        self.assertEqual({"java"}, {f["language"] for f in self.graph.functions})

    def test_RQ_TRC_050_given_java_calls_when_analysed_then_they_are_linked_and_the_library_call_is_external(self):
        self.assertEqual({("demo.shapes.Greeter.toString", "demo.shapes.Greeter.name"): (False, [8, 9])},
                         calls_of(self.graph))
        self.assertEqual((0, 1), (self.graph.ambiguous, self.graph.external))

    def test_RQ_TRC_050_given_an_id_above_an_annotated_java_method_when_analysed_then_the_method_cites_it(self):
        self.assertEqual({CITED}, set(self.functions["demo.shapes.Greeter.toString"]["ids"]))

    def test_RQ_TRC_050_given_a_java_package_when_analysed_then_it_is_the_namespace_of_the_files_classes(self):
        self.assertEqual({"demo": ("namespace", None), "demo.shapes": ("namespace", "demo"),
                          "demo.shapes.Greeter": ("class", "demo.shapes")}, scopes_of(self.graph))


@unittest.skipUnless(HAS_TREE_SITTER, NEEDS_TREE_SITTER)
class JavaScriptTest(unittest.TestCase):
    """TASK-TRC-034: RQ-TRC-050, RQ-TRC-032, RQ-TRC-047 (DEC-TRC-025, DEC-TRC-026)."""

    @classmethod
    def setUpClass(cls):
        cls.graph = language_graph("javascript")
        cls.functions = by_name(cls.graph)

    def test_RQ_TRC_050_given_javascript_files_when_analysed_then_every_function_given_a_name_is_a_function(self):
        self.assertEqual({"start", "helper", "$", "Panel.show", "Panel.#paint", "click", "key", "load"},
                         set(self.functions))
        self.assertEqual({"javascript"}, {f["language"] for f in self.graph.functions})

    def test_RQ_TRC_050_given_javascript_calls_to_dollar_and_a_private_method_then_they_are_linked(self):
        self.assertEqual({("start", "$"): False, ("start", "helper"): False, ("Panel.show", "Panel.#paint"): False},
                         call_links(self.graph))
        self.assertEqual((0, 2), (self.graph.ambiguous, self.graph.external))     # require, readFileSync

    def test_RQ_TRC_050_given_an_id_above_an_exports_member_when_analysed_then_its_function_cites_it(self):
        self.assertEqual({CITED}, set(self.functions["load"]["ids"]))

    def test_RQ_TRC_050_given_javascript_modules_when_analysed_then_the_class_is_the_only_box(self):
        self.assertEqual({"Panel": ("class", None)}, scopes_of(self.graph))


if __name__ == "__main__":
    unittest.main()
