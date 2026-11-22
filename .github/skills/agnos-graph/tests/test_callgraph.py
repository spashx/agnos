"""Unit tests of the call graph module of agnos-graph (FTR-TRC-002, ADR-TRC-004): functions, calls, scopes, parse failures.

Moved from agnos-perf-center by TASK-TRC-117 (RQ-TRC-133, DEC-TRC-074); the page tests of the call graph stay there.
Run from the repository root: python -m unittest discover -s .github/skills/agnos-graph/tests -v
"""
import ast
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import callgraph as cg  # noqa: E402
import graph as gr  # noqa: E402

SKILL = HERE.parent
FIXTURE = HERE / "fixtures" / "repo"
PROCESS = FIXTURE / "process"
CALLS = FIXTURE / "calls"

HAS_TREE_SITTER = importlib.util.find_spec("tree_sitter") is not None
NEEDS_TREE_SITTER = "tree-sitter is not installed (pip install -r .github/skills/agnos-graph/requirements-callgraph.txt)"


class OptionalModuleTest(unittest.TestCase):
    """TASK-TRC-009: RQ-TRC-027, RQ-TRC-039 (DEC-TRC-013)."""

    @unittest.skipUnless(HAS_TREE_SITTER, NEEDS_TREE_SITTER)
    def test_RQ_TRC_027_given_a_language_whose_grammar_is_missing_when_loaded_then_only_that_language_is_skipped(self):
        table = dict(cg.load_table())
        table["nolang"] = {"extensions": [".nolang"], "package": "tree-sitter-nolang",
                           "module": "tree_sitter_nolang_absent", "query": "cpp.scm"}
        grammars, missing = cg.load_grammars(table, cg.TreeSitter())
        self.assertEqual(["tree-sitter-nolang"], missing)
        self.assertNotIn(".nolang", grammars)
        self.assertEqual("cpp", grammars[".cpp"].name)

    def test_RQ_TRC_039_given_the_call_graph_module_when_its_imports_are_read_then_they_are_all_standard_library(self):
        tree = ast.parse((SKILL / "scripts" / "callgraph.py").read_text(encoding="utf-8"))
        imported = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        imported |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
        self.assertEqual(set(), imported - set(sys.stdlib_module_names))

    def test_RQ_TRC_039_given_the_requirements_file_when_read_then_it_pins_tree_sitter_and_every_grammar_of_the_table(
            self):
        pins = dict(line.split("==") for line in cg.REQUIREMENTS_PATH.read_text(encoding="utf-8").splitlines()
                    if line and not line.startswith("#"))
        self.assertEqual({cg.CORE_PACKAGE} | {e["package"] for e in cg.load_table().values()}, set(pins))
        if HAS_TREE_SITTER:
            import importlib.metadata
            self.assertEqual(pins, {p: importlib.metadata.version(p) for p in pins})


class LanguageTableTest(unittest.TestCase):
    """TASK-TRC-009: RQ-TRC-032 (DEC-TRC-014)."""

    def test_RQ_TRC_032_given_the_language_table_then_each_entry_names_its_extensions_package_module_and_query(self):
        table = cg.load_table()
        self.assertEqual({"c", "cpp", "csharp", "java", "javascript", "python", "rust"}, set(table))                # RQ-TRC-050
        seen = []
        for name, entry in table.items():
            self.assertTrue(entry["extensions"] and all(x.startswith(".") for x in entry["extensions"]), name)
            self.assertTrue(entry["package"] and entry["module"], name)
            self.assertTrue((cg.ASSETS_DIR / entry["query"]).is_file(), name)
            seen += entry["extensions"]
        self.assertEqual(len(seen), len(set(seen)))
        self.assertIn(".h", table["cpp"]["extensions"])          # owner default: headers read with the C++ grammar


def fixture_call_graph():
    """The model of the fixture process with tests/fixtures/repo/calls scanned, and the call graph of those files."""
    model = gr.build_process_model(PROCESS)
    scanned = gr.scan_sources(model, [CALLS], base=FIXTURE)
    return model, cg.analyse(scanned, gr.code_citations(model), gr.evidence)


def by_name(graph):
    return {f["qualified"]: f for f in graph.functions}


@unittest.skipUnless(HAS_TREE_SITTER, NEEDS_TREE_SITTER)
class FunctionsTest(unittest.TestCase):
    """TASK-TRC-010: RQ-TRC-028, RQ-TRC-031, RQ-TRC-032 (DEC-TRC-014, DEC-TRC-016)."""

    @classmethod
    def setUpClass(cls):
        cls.model, cls.graph = fixture_call_graph()
        cls.functions = by_name(cls.graph)

    def test_RQ_TRC_028_given_c_and_cpp_files_when_analysed_then_every_definition_has_its_qualified_name_and_lines(self):
        self.assertEqual([("relay", "calls/app/main.cpp", 4, 11),
                          ("net::Port::send", "calls/net/port.hpp", 7, 7),
                          ("net::Port::write", "calls/net/port.hpp", 8, 8),
                          ("net::Session::send", "calls/net/session.cpp", 14, 17),
                          ("net::Session::write", "calls/net/session.cpp", 19, 19),
                          ("net::Session::Session", "calls/net/session.cpp", 21, 21),
                          ("log", "calls/net/session.cpp", 25, 25),
                          ("operator==", "calls/net/session.cpp", 27, 27),
                          ("helper", "calls/util.c", 3, 3),
                          ("table", "calls/util.c", 5, 5),
                          ("run", "calls/util.c", 7, 10)],
                         [(f["qualified"], f["file"], f["first"], f["last"]) for f in self.graph.functions])

    def test_RQ_TRC_028_given_a_function_when_analysed_then_it_has_its_key_name_language_and_first_line(self):
        send = self.functions["net::Session::send"]
        self.assertEqual(("fn:calls/net/session.cpp:14", "send", "cpp", "int Session::send()"),
                         (send["key"], send["name"], send["language"], send["text"]))
        self.assertEqual("c", self.functions["helper"]["language"])

    def test_RQ_TRC_031_given_an_id_in_the_comment_just_above_a_function_when_analysed_then_the_function_cites_it(self):
        self.assertEqual({"RQ-DEM-001": [[6, "/// RQ-DEM-001: a port sends what it writes."]]},
                         self.functions["net::Port::send"]["ids"])
        self.assertEqual({"TASK-DEM-001": [[13, "// TASK-DEM-001: sending logs."]]},
                         self.functions["net::Session::send"]["ids"])
        self.assertEqual({"RQ-DEM-002": [[1, "/* RQ-DEM-002: helpers in C."]]}, self.functions["helper"]["ids"])
        self.assertEqual({}, self.functions["net::Port::write"]["ids"])

    def test_RQ_TRC_031_given_a_function_citing_an_id_when_analysed_then_its_file_still_cites_it(self):
        self.assertIn(("calls/net/port.hpp", "RQ-DEM-001", "code"), self.model.edges)


def calls_of(graph):
    """{(caller, callee): (ambiguous, call-site lines)}, by qualified names."""
    names = [f["qualified"] for f in graph.functions]
    return {(names[caller], names[callee]): (ambiguous, lines) for caller, callee, ambiguous, lines in graph.calls}


@unittest.skipUnless(HAS_TREE_SITTER, NEEDS_TREE_SITTER)
class CallResolutionTest(unittest.TestCase):
    """TASK-TRC-011: RQ-TRC-029, RQ-TRC-030, RQ-TRC-040 (DEC-TRC-015)."""

    @classmethod
    def setUpClass(cls):
        cls.graph = fixture_call_graph()[1]
        cls.calls = calls_of(cls.graph)

    def test_RQ_TRC_029_given_a_name_with_one_definition_when_called_twice_then_one_link_holds_both_lines(self):
        self.assertEqual((False, [8, 9]), self.calls[("relay", "log")])
        self.assertEqual((False, [9]), self.calls[("run", "helper")])

    def test_RQ_TRC_029_given_definitions_in_the_callers_class_and_another_when_called_then_its_class_wins(self):
        self.assertEqual((False, [7]), self.calls[("net::Port::send", "net::Port::write")])
        self.assertNotIn(("net::Port::send", "net::Session::write"), self.calls)

    def test_RQ_TRC_030_given_a_receiver_call_with_two_candidates_outside_both_classes_then_both_links_are_ambiguous(
            self):
        for callee in ("net::Port::send", "net::Session::send"):
            self.assertEqual((True, [6]), self.calls[("relay", callee)])
        for callee in ("net::Port::write", "net::Session::write"):
            self.assertEqual((True, [7]), self.calls[("relay", callee)])

    def test_RQ_TRC_030_given_library_calls_and_a_pointer_call_then_two_are_external_and_the_pointer_is_not_followed(
            self):
        self.assertEqual(8, len(self.calls))
        self.assertEqual((2, 2), (self.graph.ambiguous, self.graph.external))
        self.assertIn("call graph: 11 functions, 8 calls, ambiguous 2, external 2", self.graph.summary())

    def test_RQ_TRC_123_given_a_call_through_a_function_pointer_when_analysed_then_it_counts_as_unnamed(self):
        self.assertEqual({"library": 2, "constructor": 0, "cross-language": 0, "unnamed": 1, "top-level": 0},
                         self.graph.unresolved)                 # puts, printf; (*fp)()

    def test_RQ_TRC_123_given_module_level_calls_when_analysed_then_they_count_as_top_level_and_make_no_link(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "boot.py"
            path.write_text("def f():\n    return 0\n\n\nf()\nprint(f())\n", encoding="utf-8")
            graph = cg.analyse([("boot.py", path)], {}, gr.evidence)
        self.assertEqual(([], 0, 3), (graph.calls, graph.external, graph.unresolved["top-level"]))

    def test_RQ_TRC_123_given_a_c_call_to_a_name_only_python_defines_when_analysed_then_it_counts_as_cross_language(
            self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "main.c").write_text("int run(void) { return py_only(); }\n", encoding="utf-8")
            (root / "lib.py").write_text("def py_only():\n    return 0\n", encoding="utf-8")
            graph = cg.analyse(sorted((p.name, p) for p in root.iterdir()), {}, gr.evidence)
        self.assertEqual((1, 1), (graph.external, graph.unresolved["cross-language"]))

    def test_RQ_TRC_030_given_more_than_five_candidates_when_called_then_no_link_is_made_and_it_counts_as_ambiguous(
            self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for n in range(cg.MAX_AMBIGUOUS + 1):
                (root / f"d{n}").mkdir()
                (root / f"d{n}" / "f.cpp").write_text("int f() { return 0; }\n", encoding="utf-8")
            (root / "main.cpp").write_text("int g() { return f(); }\n", encoding="utf-8")
            files = sorted((p.relative_to(root).as_posix(), p) for p in root.rglob("*.cpp"))
            graph = cg.analyse(files, {}, gr.evidence)
        self.assertEqual(([], 1, 0), (graph.calls, graph.ambiguous, graph.external))

    def test_RQ_TRC_040_given_the_fixture_when_analysed_twice_then_the_calls_are_identical(self):
        """TASK-TRC-117: the call graph half of RQ-TRC-040, moved from the page's determinism test (DEC-TRC-074)."""
        self.assertEqual(calls_of(fixture_call_graph()[1]), self.calls)


# RQ-TRC-122: one source per language whose second definition does not parse, its first one being sound.
BROKEN_SOURCES = {
    "broken.c": "int good(void) { return 0; }\nint bad( { return 1;\n",
    "broken.cpp": "int good() { return 0; }\nint bad( { return 1;\n",
    "Broken.cs": "class A { int good() { return 0; } int bad( { } }\n",
    "Broken.java": "class A { int good() { return 0; } int bad( { } }\n",
    "broken.js": "function good() { return 0; }\nfunction bad( { \n",
    "broken.py": "def good():\n    return 0\n\ndef bad(:\n    pass\n",
    "broken.rs": "fn good() -> i32 { 0 }\nfn bad( { }\n",
}
SOUND_SOURCE = ("sound.c", "int fine(void) { return 0; }\n")


def broken_graph(root):
    """The call graph of BROKEN_SOURCES and SOUND_SOURCE written in root."""
    for name, text in [*BROKEN_SOURCES.items(), SOUND_SOURCE]:
        (root / name).write_text(text, encoding="utf-8")
    files = sorted((p.name, p) for p in root.iterdir())
    return cg.analyse(files, {}, gr.evidence)


@unittest.skipUnless(HAS_TREE_SITTER, NEEDS_TREE_SITTER)
class ParseFailureTest(unittest.TestCase):
    """TASK-TRC-110: RQ-TRC-122 (DEC-TRC-067)."""

    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            cls.graph = broken_graph(Path(tmp))

    def test_RQ_TRC_122_given_a_broken_file_per_language_when_analysed_then_each_is_unparsed_and_the_sound_one_is_not(
            self):
        self.assertEqual(sorted(BROKEN_SOURCES), self.graph.unparsed)
        self.assertEqual(sorted([*BROKEN_SOURCES, SOUND_SOURCE[0]]), self.graph.parsed)

    def test_RQ_TRC_122_given_a_broken_file_when_analysed_then_its_sound_function_is_still_read(self):
        files = {f["file"] for f in self.graph.functions if f["name"] == "good"}
        self.assertEqual(set(BROKEN_SOURCES), files)

    def test_RQ_TRC_122_given_broken_files_when_summarised_then_the_counts_and_summary_line_give_their_number(self):
        self.assertIn(f"unparsed {len(BROKEN_SOURCES)}", self.graph.summary())
        for f in self.graph.functions:
            f.setdefault("dup", 0)
            f.setdefault(cg.KEY_SCOPE_INDEX, cg.NO_SCOPE)
        counts = self.graph.page_data({f["file"]: 0 for f in self.graph.functions})["counts"]
        self.assertEqual(len(BROKEN_SOURCES), counts["unparsed"])

    def test_RQ_TRC_122_given_the_call_graph_fixture_when_analysed_then_no_file_is_unparsed(self):
        graph = fixture_call_graph()[1]
        self.assertEqual([], graph.unparsed)
        self.assertEqual(4, len(graph.parsed))                  # the four C and C++ files of calls/


def scope_of(graph, qualified):
    """The qualified name of the function's scope in the graph's scope table, None when it has none."""
    index = by_name(graph)[qualified]["scope_index"]
    return graph.scopes[index][0] if index >= 0 else None


@unittest.skipUnless(HAS_TREE_SITTER, NEEDS_TREE_SITTER)
class ScopesTest(unittest.TestCase):
    """TASK-TRC-023: RQ-TRC-047, RQ-TRC-032, RQ-TRC-038, RQ-TRC-040 (DEC-TRC-019)."""

    @classmethod
    def setUpClass(cls):
        cls.graph = fixture_call_graph()[1]

    def test_RQ_TRC_047_given_the_language_table_then_cpp_maps_its_scope_nodes_to_kinds_and_c_has_none(self):
        table = cg.load_table()
        self.assertEqual({"namespace_definition": "namespace", "class_specifier": "class",
                          "struct_specifier": "class", "union_specifier": "class"}, table["cpp"]["scopes"])
        self.assertEqual({}, table["c"].get("scopes", {}))

    def test_RQ_TRC_047_given_the_fixture_when_analysed_then_the_scopes_are_net_and_its_two_classes(self):
        self.assertEqual([["net", "namespace", -1], ["net::Port", "class", 0], ["net::Session", "class", 0]],
                         self.graph.scopes)

    def test_RQ_TRC_047_given_functions_in_and_out_of_their_class_when_analysed_then_each_has_its_class_scope(self):
        self.assertEqual("net::Port", scope_of(self.graph, "net::Port::send"))
        self.assertEqual("net::Session", scope_of(self.graph, "net::Session::send"))      # defined out of its class
        self.assertEqual("net::Session", scope_of(self.graph, "net::Session::Session"))

    def test_RQ_TRC_047_given_functions_outside_any_scope_or_in_c_when_analysed_then_they_have_none(self):
        for name in ("relay", "log", "operator==", "helper", "table", "run"):
            self.assertIsNone(scope_of(self.graph, name), name)

    def test_RQ_TRC_047_given_a_method_of_a_class_declared_in_no_scanned_file_then_its_kinds_are_guessed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "widget.cpp"
            path.write_text("int ui::Widget::paint() { return 0; }\n", encoding="utf-8")
            graph = cg.analyse([("widget.cpp", path)], {}, gr.evidence)
        self.assertEqual([["ui", "namespace", -1], ["ui::Widget", "class", 0]], graph.scopes)
        self.assertEqual("ui::Widget", scope_of(graph, "ui::Widget::paint"))

    def test_RQ_TRC_038_given_the_page_data_then_it_adds_one_scope_index_per_function_and_one_row_per_scope(self):
        data = self.graph.page_data({f["file"]: n for n, f in enumerate(self.graph.functions)})
        self.assertEqual(self.graph.scopes, data["scopes"])
        rows = {row[3]: row for row in data["functions"]}
        self.assertEqual({8}, {len(row) for row in rows.values()})
        self.assertEqual(1, rows["net::Port::send"][7])
        self.assertEqual(-1, rows["relay"][7])


if __name__ == "__main__":
    unittest.main()
