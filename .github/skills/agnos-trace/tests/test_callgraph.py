"""Tests of the optional call-graph analysis of agnos-trace (FTR-TRC-002, ADR-TRC-004), on tests/fixtures/repo.

Run from the repository root: python -m unittest discover -s .github/skills/agnos-trace/tests -v
The tests that parse need the packages of requirements-callgraph.txt and are skipped without them.
"""
import ast
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))

import callgraph as cg  # noqa: E402
import trace_matrix as tm  # noqa: E402
from test_trace_matrix import FIXTURE, PROCESS, SKILL, SOURCES, data_block, generate, run_main  # noqa: E402

CALLS = FIXTURE / "calls"

HAS_TREE_SITTER = importlib.util.find_spec("tree_sitter") is not None
NEEDS_TREE_SITTER = "tree-sitter is not installed (pip install -r .github/skills/agnos-trace/requirements-callgraph.txt)"
DATA_BEFORE_PLAN_SHA256 = "c43656a2d4ce43c171aff4ceb8477c82836225ee4074c19af25bb54793ca5dd2"   # the fixture page's data
# before PLAN-TRC-002, with its two machine-dependent fields (the process and source paths given) blanked


def location_free_sha256(page):
    data = json.loads(data_block(page))
    data["meta"]["process"] = data["meta"]["sources"] = None
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()


def summary_line(stdout):
    return stdout.strip().splitlines()[-1]


class OptionalModuleTest(unittest.TestCase):
    """TASK-TRC-009: RQ-TRC-026, RQ-TRC-027, RQ-TRC-039 (DEC-TRC-013)."""

    def test_RQ_TRC_026_given_no_call_graph_option_when_generated_then_the_data_is_the_one_before_this_feature(self):
        with tempfile.TemporaryDirectory() as tmp:
            page, _ = generate(Path(tmp) / "page.html")
        self.assertEqual(DATA_BEFORE_PLAN_SHA256, location_free_sha256(page))

    def test_RQ_TRC_039_given_no_call_graph_option_when_the_generator_runs_then_no_tree_sitter_module_is_imported(self):
        probe = ("import sys, tempfile, pathlib; sys.path.insert(0, sys.argv[1]); import trace_matrix as tm\n"
                 "out = pathlib.Path(tempfile.mkdtemp()) / 'page.html'\n"
                 "code = tm.main(['--process', sys.argv[2], '--sources', sys.argv[3], '--out', str(out)])\n"
                 "print(code, sorted(m for m in sys.modules if m.startswith(('tree_sitter', 'agnos_trace'))))")
        done = subprocess.run([sys.executable, "-c", probe, str(SKILL / "scripts"), str(PROCESS), str(SOURCES)],
                              capture_output=True, text=True, timeout=120, check=False)
        self.assertEqual("0 []", done.stdout.strip().splitlines()[-1], done.stderr)

    def test_RQ_TRC_027_given_no_tree_sitter_when_run_with_call_graph_then_it_exits_0_and_prints_the_install_command(
            self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(sys.modules, {"tree_sitter": None}):
            out = Path(tmp) / "page.html"
            code, stdout, err = run_main(["--process", str(PROCESS), "--sources", str(SOURCES), "--out", str(out),
                                          "--call-graph"])
            self.assertEqual(0, code, err)
            self.assertTrue(out.is_file())
        line = summary_line(stdout)
        self.assertIn("call graph skipped: tree-sitter not installed", line)
        self.assertIn("pip install -r ", line)
        self.assertIn("requirements-callgraph.txt", line)

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
        self.assertEqual({"c", "cpp"}, set(table))
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
    model = tm.build_process_model(PROCESS)
    scanned = tm.scan_sources(model, [CALLS], base=FIXTURE)
    return model, cg.analyse(scanned, tm.code_citations(model), tm.evidence)


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

    def test_RQ_TRC_030_given_more_than_five_candidates_when_called_then_no_link_is_made_and_it_counts_as_ambiguous(
            self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for n in range(cg.MAX_AMBIGUOUS + 1):
                (root / f"d{n}").mkdir()
                (root / f"d{n}" / "f.cpp").write_text("int f() { return 0; }\n", encoding="utf-8")
            (root / "main.cpp").write_text("int g() { return f(); }\n", encoding="utf-8")
            files = sorted((p.relative_to(root).as_posix(), p) for p in root.rglob("*.cpp"))
            graph = cg.analyse(files, {}, tm.evidence)
        self.assertEqual(([], 1, 0), (graph.calls, graph.ambiguous, graph.external))

    def test_RQ_TRC_040_given_the_fixture_when_the_page_is_generated_twice_with_the_call_graph_then_it_is_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            first, out = generate(Path(tmp) / "one.html", "--call-graph")
            second, _ = generate(Path(tmp) / "two.html", "--call-graph")
        self.assertEqual(first, second)
        self.assertIn("call graph: ", summary_line(out))
        self.assertEqual(calls_of(fixture_call_graph()[1]), self.calls)


if __name__ == "__main__":
    unittest.main()
