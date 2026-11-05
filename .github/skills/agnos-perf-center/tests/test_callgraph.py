"""Tests of the optional call-graph analysis of agnos-perf-center (FTR-TRC-002, ADR-TRC-004), on tests/fixtures/repo.

Run from the repository root: python -m unittest discover -s .github/skills/agnos-perf-center/tests -v
The tests that parse need the packages of requirements-callgraph.txt and are skipped without them.
"""
import ast
import hashlib
import importlib.util
import json
import os
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
import perf_center as tm  # noqa: E402
import scorecard as sc  # noqa: E402
from test_perf_center import (BROWSER, FIXTURE, PROCESS, SKILL, SOURCES, comparable, data_block,  # noqa: E402
                               generate, output_bytes, rendered_dom, rendered_dom_after, run_main)

CALLS = FIXTURE / "calls"

HAS_TREE_SITTER = importlib.util.find_spec("tree_sitter") is not None
NEEDS_TREE_SITTER = "tree-sitter is not installed (pip install -r .github/skills/agnos-perf-center/requirements-callgraph.txt)"
DATA_BEFORE_PLAN_SHA256 = "b3e71cd10842e48aec7851af03db63ea48752ae3b3a8ea2cf7bb67d6c7f01039"   # the fixture page's data;
# re-pinned by TASK-TRC-064: meta.library became meta.libraries (RQ-TRC-082);
# re-pinned by TASK-TRC-089: meta.summary starts with the skill's new name (RQ-TRC-105)
# without --call-graph, with its two machine-dependent fields (the process and source paths given) blanked; re-pinned
# on purpose by TASK-TRC-046 and TASK-TRC-050 (ADR-TRC-008, DEC-TRC-033): the `quality` block replaced the finding lists, then gained labels.


def location_free_sha256(page):
    data = json.loads(data_block(page))
    data["meta"]["process"] = data["meta"]["sources"] = None
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()


def summary_line(stdout):
    return stdout.strip().splitlines()[-1]


class OptionalModuleTest(unittest.TestCase):
    """TASK-TRC-009: RQ-TRC-026, RQ-TRC-027, RQ-TRC-039 (DEC-TRC-013)."""

    def test_RQ_TRC_026_given_no_call_graph_option_when_generated_then_the_data_is_the_one_before_this_feature(self):
        # the files are shown relative to the current folder: the hash is the one of a run from the skill's folder
        previous = os.getcwd()
        os.chdir(SKILL)
        try:
            with tempfile.TemporaryDirectory() as tmp:
                page, _ = generate(Path(tmp) / "page.html")
                self.assertEqual(DATA_BEFORE_PLAN_SHA256, location_free_sha256(page))     # its data file, beside it
        finally:
            os.chdir(previous)

    def test_RQ_TRC_039_given_no_call_graph_option_when_the_generator_runs_then_no_tree_sitter_module_is_imported(self):
        probe = ("import sys, tempfile, pathlib; sys.path.insert(0, sys.argv[1]); import perf_center as tm\n"
                 "out = pathlib.Path(tempfile.mkdtemp()) / 'page.html'\n"
                 "code = tm.main(['--process', sys.argv[2], '--sources', sys.argv[3], '--out', str(out)])\n"
                 "print(code, sorted(m for m in sys.modules if m.startswith(('tree_sitter', 'agnos_perf_center'))))")
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
            self.assertEqual(comparable(first), comparable(second))
        self.assertIn("call graph: ", summary_line(out))
        self.assertEqual(calls_of(fixture_call_graph()[1]), self.calls)


def call_graph_page(out):
    """The fixture page with tests/fixtures/repo/calls scanned too and the call graph on."""
    return generate(out, "--sources", str(CALLS), "--call-graph")


def fragment(key):
    import urllib.parse
    return "#" + urllib.parse.quote(key, safe="")


@unittest.skipUnless(HAS_TREE_SITTER, NEEDS_TREE_SITTER)
class PageDataTest(unittest.TestCase):
    """TASK-TRC-012: RQ-TRC-033, RQ-TRC-035, RQ-TRC-038 (DEC-TRC-016)."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.page, cls.summary = call_graph_page(Path(cls.tmp.name) / "page.html")
        cls.data = json.loads(data_block(cls.page))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_RQ_TRC_038_given_the_call_graph_when_embedded_then_functions_are_a_table_and_calls_a_flat_integer_list(self):
        graph = self.data["callGraph"]
        self.assertEqual(14, len(graph["functions"]))           # the 11 of calls/, src/lib/b.cpp's indirect(),
        # and since Python is read (RQ-TRC-050) src/a.py's covered() and src/notrace.py's untraced()
        paths = [f["path"] for f in self.data["files"]]
        file_index, first, last, name, language = graph["functions"][1][:5]
        self.assertTrue(paths[file_index].endswith("/calls/net/port.hpp"), paths[file_index])   # shown from the cwd
        self.assertEqual((7, 7, "net::Port::send"), (first, last, name))
        self.assertEqual("cpp", graph["languages"][language])
        self.assertTrue(all(isinstance(n, int) for n in graph["calls"]))
        self.assertEqual({"functions": 14, "calls": 8, "ambiguous": 2, "external": 2}, graph["counts"])

    def test_RQ_TRC_038_given_the_call_graph_when_embedded_then_it_adds_at_most_120_bytes_per_function_and_16_per_call(
            self):
        without, _ = generate(Path(self.tmp.name) / "without.html", "--sources", str(CALLS))
        counts = self.data["callGraph"]["counts"]
        added = output_bytes(self.page) - output_bytes(without)
        self.assertLessEqual(added, 120 * counts["functions"] + 16 * counts["calls"])

    def test_RQ_PLG_024_given_the_call_graph_when_embedded_then_untraced_functions_are_a_medium_check(self):
        """RQ-TRC-035 amended by RQ-PLG-024 (DEC-PLG-019): the untraced functions weigh as the untraced files."""
        graph = self.data["callGraph"]
        check = next(c for c in self.data["quality"]["checks"] if c["key"] == "functions-traced")
        names = [graph["functions"][i][3] for i in check["findings"]]
        self.assertNotIn("untraced", graph)                     # stored once, in the quality block
        self.assertEqual(9, len(names))                         # src/notrace.py's untraced() since RQ-TRC-050
        self.assertIn("untraced", names)
        self.assertNotIn("covered", names)                      # its docstring cites an ID
        self.assertNotIn("net::Port::send", names)
        self.assertEqual(("medium", "function"), (check["risk"], check["items"]))

    def test_RQ_PLG_024_given_untraced_functions_when_scored_then_they_lower_the_score_and_count_in_the_findings(self):
        quality = self.data["quality"]
        check = next(c for c in quality["checks"] if c["key"] == "functions-traced")
        others = [c for c in quality["checks"] if c["key"] != "functions-traced"]
        without = sc.weighted_score([(c["risk"], c["score"]) for c in others], sc.load_scoring())
        self.assertLess(check["score"], 10.0)
        self.assertLess(quality["score"], without)              # the check pulls the overall score down
        total = sum(len(c["findings"]) for c in quality["checks"])
        self.assertIn(f"findings {total};", self.summary)       # the functions' findings are in the total


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
            graph = cg.analyse([("widget.cpp", path)], {}, tm.evidence)
        self.assertEqual([["ui", "namespace", -1], ["ui::Widget", "class", 0]], graph.scopes)
        self.assertEqual("ui::Widget", scope_of(graph, "ui::Widget::paint"))

    def test_RQ_TRC_038_given_the_page_data_then_it_adds_one_scope_index_per_function_and_one_row_per_scope(self):
        data = self.graph.page_data({f["file"]: n for n, f in enumerate(self.graph.functions)})
        self.assertEqual(self.graph.scopes, data["scopes"])
        rows = {row[3]: row for row in data["functions"]}
        self.assertEqual({8}, {len(row) for row in rows.values()})
        self.assertEqual(1, rows["net::Port::send"][7])
        self.assertEqual(-1, rows["relay"][7])


@unittest.skipUnless(HAS_TREE_SITTER and BROWSER, NEEDS_TREE_SITTER + ", or no Chromium-family browser found")
class FunctionPanelTest(unittest.TestCase):
    """TASK-TRC-012: RQ-TRC-033, RQ-TRC-035 (DEC-TRC-016, DEC-TRC-018), in a real browser."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "page.html"
        page, _ = call_graph_page(cls.path)
        data = json.loads(data_block(page))
        paths = [f["path"] for f in data["files"]]
        cls.keys = {f[3]: f"fn:{paths[f[0]]}:{f[1]}" for f in data["callGraph"]["functions"]}   # no key suffix here

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_RQ_TRC_033_given_a_function_when_selected_then_the_panel_shows_its_callers_callees_and_ids(self):
        dom = rendered_dom(self.path, fragment(self.keys["net::Port::write"]))
        self.assertIn('<h2 class="detail-id">net::Port::write</h2>', dom)
        self.assertIn("Callers 2", dom)
        self.assertIn("Callees 0", dom)
        self.assertIn('<span class="id">net::Port::send</span>', dom)
        self.assertIn('<span class="id">relay</span>', dom)
        self.assertIn("ambiguous", dom)
        dom = rendered_dom(self.path, fragment(self.keys["net::Port::send"]))
        self.assertIn('<span class="id">RQ-DEM-001</span>', dom)
        self.assertIn("calls/net/port.hpp:7-7", dom)

    def test_RQ_TRC_033_given_a_requirement_cited_by_a_function_when_selected_then_the_function_is_listed(self):
        dom = rendered_dom(self.path, "#RQ-DEM-001")
        self.assertIn("Function 1", dom)
        self.assertIn('<span class="id">net::Port::send</span>', dom)

    def test_RQ_TRC_033_given_a_function_name_when_searched_then_the_function_is_found(self):
        dom = rendered_dom_after(self.path, "const s = document.getElementById('search'); s.value = 'port::wr';"
                                            "s.dispatchEvent(new Event('input'));")
        self.assertRegex(dom, r'<li class="search-result t-FN"[^>]*>.*?net::Port::write')

    def test_RQ_TRC_035_given_the_call_graph_when_the_page_opens_then_the_graph_view_and_gaps_show_it_uninflated(self):
        """TASK-TRC-076: the card under the graph's frame, only while the implementation is drawn; none in the overview."""
        import re
        data = json.loads(data_block(self.path))
        total = sum(len(c["findings"]) for c in data["quality"]["checks"] if c["risk"] != "informational")
        dom = rendered_dom_after(self.path, """
const out = document.documentElement.dataset;
out.cgoverview = String([...document.querySelectorAll("#view-overview .card-title")].some((t) => t.textContent === "Call graph"));
agnosTrace.showView("graph");
const card = document.getElementById("call-graph-card");
out.cgoff = String(card.hidden);                                     // functions off at load
document.getElementById("show-functions").click();
out.cgon = String(!card.hidden && card.previousElementSibling.classList.contains("graph-frame"));
out.cgtext = card.textContent;
document.getElementById("show-functions").click();
out.cgagain = String(card.hidden);
""")
        found = dict(re.findall(r'data-(cgoverview|cgoff|cgon|cgtext|cgagain)="([^"]*)"', dom))
        self.assertEqual(("false", "true", "true", "true"), (found["cgoverview"], found["cgoff"], found["cgon"], found["cgagain"]))
        for part in ("Call graph", "8 call links", "Ambiguous calls", "External calls", "Untraced functions"):
            self.assertIn(part, found["cgtext"])
        risk = next(c["risk"] for c in data["quality"]["checks"] if c["key"] == "functions-traced")
        self.assertIn(f"citing no ID · {risk}", found["cgtext"])   # RQ-PLG-024: the risk read from the data
        self.assertNotIn("informational", found["cgtext"])
        self.assertIn(f'<span class="tab-count" id="quality-count">{total}</span>', dom)


TURN_FUNCTIONS_ON = ("[...document.querySelectorAll('#type-filters .chip')]"
                     ".find((b) => b.textContent.startsWith('Functions')).click();")


def graph_attributes(dom):
    import re
    found = dict(re.findall(r'data-graph-(\w+)="([^"]*)"', dom))
    status = re.search(r'id="graph-status"[^>]*>([^<]*)<', dom)
    found["status"] = status.group(1) if status else ""
    return found


@unittest.skipUnless(HAS_TREE_SITTER and BROWSER, NEEDS_TREE_SITTER + ", or no Chromium-family browser found")
class FunctionGraphTest(unittest.TestCase):
    """TASK-TRC-013: RQ-TRC-034 (DEC-TRC-017, DEC-TRC-006), in a real browser."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "page.html"
        page, _ = call_graph_page(cls.path)
        data = json.loads(data_block(page))
        paths = [f["path"] for f in data["files"]]
        cls.keys = {f[3]: f"fn:{paths[f[0]]}:{f[1]}" for f in data["callGraph"]["functions"]}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_RQ_TRC_034_given_the_page_just_opened_when_a_requirement_is_drawn_then_functions_appear_only_once_turned_on(
            self):
        show = "agnosTrace.select('RQ-DEM-001'); agnosTrace.showView('graph');"
        before = graph_attributes(rendered_dom_after(self.path, show))
        after = graph_attributes(rendered_dom_after(self.path, TURN_FUNCTIONS_ON + show))
        self.assertEqual("RQ-DEM-001", before["selected"])
        self.assertEqual(int(before["nodes"]) + 1, int(after["nodes"]))        # net::Port::send cites it

    def test_RQ_TRC_034_given_functions_on_when_a_function_is_drawn_then_its_calls_are_links_of_the_graph(self):
        dom = rendered_dom_after(self.path, TURN_FUNCTIONS_ON + f"agnosTrace.select('{self.keys['net::Port::write']}');"
                                                                "agnosTrace.showView('graph');")
        attributes = graph_attributes(dom)
        self.assertEqual("4", attributes["nodes"])           # itself, its file, net::Port::send and relay
        # links: the file contains both methods; send -> write, relay -> write and relay -> send (x.send()) are calls
        self.assertIn("4 elements · 5 links", attributes["status"])


GLOBAL_BOX = "box:(global)"         # what stands in no named namespace (DEC-TRC-019 as amended, TASK-TRC-028)
READ_DRAWING = "document.documentElement.dataset.drawing = JSON.stringify(agnosTrace.graph.elements());"


def drawing(path, script):
    """The data of the elements drawn once functions are on and the script ran: ({node id: data}, {edge id: data})."""
    import html
    import re
    dom = rendered_dom_after(path, TURN_FUNCTIONS_ON + script + READ_DRAWING)
    found = json.loads(html.unescape(re.search(r'data-drawing="([^"]*)"', dom).group(1)))
    return ({e["id"]: e for e in found if "source" not in e}, {e["id"]: e for e in found if "source" in e})


@unittest.skipUnless(HAS_TREE_SITTER and BROWSER, NEEDS_TREE_SITTER + ", or no Chromium-family browser found")
class DetailLevelTest(unittest.TestCase):
    """TASK-TRC-024: RQ-TRC-047, RQ-TRC-037 (DEC-TRC-021), in a real browser."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "page.html"
        page, _ = call_graph_page(cls.path)
        data = json.loads(data_block(page))
        cls.paths = [f["path"] for f in data["files"]]
        cls.keys = {f[3]: f"fn:{cls.paths[f[0]]}:{f[1]}" for f in data["callGraph"]["functions"]}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_RQ_TRC_047_given_the_namespace_level_when_relay_is_drawn_then_its_calls_are_one_link_per_box_with_a_count(
            self):
        nodes, edges = drawing(self.path, f"agnosTrace.graph.setDetail('namespace');"
                                          f"agnosTrace.select('{self.keys['relay']}'); agnosTrace.showView('graph');")
        self.assertFalse([key for key in nodes if key.startswith(("fn:", "box:file:"))])     # TASK-TRC-028: no file box
        self.assertIn("box:net", nodes)
        to_net = edges[f"{GLOBAL_BOX}>box:net>calls"]
        self.assertEqual((2, True), (to_net["count"], to_net["ambiguous"]))     # x.send() and port.write(3), ambiguous
        to_global = edges[f"box:net>{GLOBAL_BOX}>calls"]                         # net::Session::send calls log(2)
        self.assertEqual((1, False), (to_global["count"], to_global["ambiguous"]))
        # relay -> log (both global) and send -> write (both in net) stay inside their box
        self.assertEqual(2, len([e for e in edges.values() if e["kind"] == "calls"]))

    def test_RQ_TRC_047_given_the_class_level_when_a_requirement_is_drawn_then_its_citing_function_is_its_class(self):
        nodes, edges = drawing(self.path, "agnosTrace.graph.setDetail('class');"
                                          "agnosTrace.select('RQ-DEM-001'); agnosTrace.showView('graph');")
        self.assertIn("box:net::Port>RQ-DEM-001>code", edges)
        self.assertNotIn(self.keys["net::Port::send"], nodes)

    def test_RQ_TRC_047_given_the_function_level_again_when_a_function_is_drawn_then_the_drawing_is_unchanged(self):
        show = f"agnosTrace.select('{self.keys['net::Port::write']}'); agnosTrace.showView('graph');"
        before = drawing(self.path, show)
        after = drawing(self.path, "agnosTrace.graph.setDetail('namespace');" + show
                        + "agnosTrace.graph.setDetail('function');")
        self.assertEqual(before, after)
        self.assertEqual(4, len([k for k in before[0] if not k.startswith(("header:", "box:"))]))


@unittest.skipUnless(HAS_TREE_SITTER and BROWSER, NEEDS_TREE_SITTER + ", or no Chromium-family browser found")
class BoxDrawingTest(unittest.TestCase):
    """TASK-TRC-025: RQ-TRC-047, RQ-TRC-018 (DEC-TRC-020), in a real browser."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "page.html"
        page, _ = call_graph_page(cls.path)
        data = json.loads(data_block(page))
        paths = [f["path"] for f in data["files"]]
        cls.keys = {f[3]: f"fn:{paths[f[0]]}:{f[1]}" for f in data["callGraph"]["functions"]}
        cls.show_relay = f"agnosTrace.select('{cls.keys['relay']}'); agnosTrace.showView('graph');"

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_RQ_TRC_047_given_the_function_level_with_enclosing_boxes_then_a_method_is_in_its_class_in_its_namespace(
            self):
        nodes, _ = drawing(self.path, self.show_relay)
        send = nodes[self.keys["net::Port::send"]]
        port = nodes[send["parent"]]
        self.assertEqual(("net::Port", "class", "Port"), (port["name"], port["box"], port["label"]))
        self.assertEqual("send", send["label"])                                # named inside its box
        space = nodes[port["parent"]]
        self.assertEqual(("net", "namespace"), (space["name"], space["box"]))
        self.assertNotIn("parent", nodes[self.keys["relay"]])                 # no scope: no box at the function level

    def test_RQ_TRC_047_given_enclosing_boxes_off_then_the_class_box_stands_alone(self):
        nodes, _ = drawing(self.path, "agnosTrace.graph.setEnclosing(false);" + self.show_relay)
        port = nodes[nodes[self.keys["net::Port::send"]]["parent"]]
        self.assertEqual(("net::Port", "net::Port"), (port["name"], port["label"]))     # alone: its whole name
        self.assertNotIn("parent", port)
        self.assertFalse([n for n in nodes.values() if n.get("box") == "namespace"])

    def test_RQ_TRC_047_given_the_class_level_with_enclosing_boxes_then_class_boxes_are_in_their_namespace(self):
        nodes, _ = drawing(self.path, "agnosTrace.graph.setDetail('class');" + self.show_relay)
        self.assertIn("box:net::Port", nodes)
        space = nodes[nodes["box:net::Port"]["parent"]]
        self.assertEqual(("net", "namespace"), (space["name"], space["box"]))

    def test_RQ_TRC_018_given_the_box_kinds_then_each_has_its_colour_token(self):
        tokens = tm.load_tokens(tm.TOKENS_PATH)["component"]
        for kind in ("namespace", "class", "global"):
            self.assertIn(f"graph-box-{kind}", tokens)


CLICK_DETAIL = "document.querySelector('#detail-level button[data-detail=\"{}\"]').click();"
READ_CONTROLS = """
const out = document.documentElement.dataset;
out.pressed = document.querySelector('#detail-level button[aria-pressed="true"]').dataset.detail;
out.enclosingDisabled = String(document.getElementById("show-enclosing").disabled);
"""


@unittest.skipUnless(HAS_TREE_SITTER and BROWSER, NEEDS_TREE_SITTER + ", or no Chromium-family browser found")
class DetailControlsTest(unittest.TestCase):
    """TASK-TRC-026: RQ-TRC-047, RQ-TRC-013, RQ-TRC-016, RQ-TRC-045, RQ-TRC-046 (DEC-TRC-022), in a real browser."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "page.html"
        page, _ = call_graph_page(cls.path)
        data = json.loads(data_block(page))
        cls.paths = [f["path"] for f in data["files"]]
        cls.keys = {f[3]: f"fn:{cls.paths[f[0]]}:{f[1]}" for f in data["callGraph"]["functions"]}
        cls.plain = Path(cls.tmp.name) / "plain.html"
        generate(cls.plain)
        cls.show_relay = f"agnosTrace.select('{cls.keys['relay']}'); agnosTrace.showView('graph');"

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def controls(self, script):
        import re
        dom = rendered_dom_after(self.path, TURN_FUNCTIONS_ON + script + READ_CONTROLS + READ_DRAWING)
        return dict(re.findall(r'data-(pressed|enclosing-disabled)="([^"]*)"', dom)), dom

    def test_RQ_TRC_047_given_the_detail_choice_when_class_is_chosen_then_the_graph_is_drawn_by_class_boxes(self):
        found, dom = self.controls(self.show_relay + CLICK_DETAIL.format("class"))
        self.assertEqual({"pressed": "class", "enclosing-disabled": "false"}, found)
        self.assertIn("box:net::Port", dom)

    def test_RQ_TRC_047_given_the_detail_choice_when_namespace_is_chosen_then_the_enclosing_switch_is_disabled(self):
        found, _ = self.controls(self.show_relay + CLICK_DETAIL.format("namespace"))
        self.assertEqual({"pressed": "namespace", "enclosing-disabled": "true"}, found)

    def test_RQ_TRC_045_given_the_controls_then_each_has_a_tooltip(self):
        _, dom = self.controls("")
        self.assertRegex(dom, r'<fieldset class="segmented" id="detail-level"[^>]* title="[^"]+"')
        for level in ("namespace", "class", "function"):
            self.assertRegex(dom, rf'data-detail="{level}"[^>]* title="[^"]+"|title="[^"]+"[^>]* data-detail="{level}"')
        self.assertRegex(dom, r'<label class="toggle[^"]*" title="[^"]+"><input type="checkbox" id="show-enclosing"')

    def test_RQ_TRC_016_given_a_class_box_when_selected_then_its_panel_lists_its_methods_and_their_requirement(self):
        dom = rendered_dom(self.path, fragment("box:net::Port"))
        self.assertIn('<h2 class="detail-id">net::Port</h2>', dom)
        self.assertIn('<div class="detail-kind"><span class="dot t-FN"></span>Class</div>', dom)     # RQ-TRC-048
        for name in ("net::Port::send", "net::Port::write", "RQ-DEM-001", "net"):
            self.assertIn(f'<span class="id">{name}</span>', dom)
        panel = dom[dom.index('id="detail"'):]
        self.assertNotIn("null", panel[:panel.index("</aside>")] if "</aside>" in panel else panel)

    def test_RQ_TRC_046_given_a_link_merging_calls_when_its_tooltip_is_asked_then_it_gives_their_count(self):
        import html
        import re
        dom = rendered_dom_after(self.path, TURN_FUNCTIONS_ON + "agnosTrace.graph.setDetail('namespace');" + self.show_relay
                                 + f"document.documentElement.dataset.tip = "
                                   f"agnosTrace.graph.tipFor('{GLOBAL_BOX}>box:net>calls');")
        tip = html.unescape(re.search(r'data-tip="([^"]*)"', dom).group(1))
        self.assertIn("ambiguous call", tip)
        self.assertIn("2 call sites", tip)

    def test_RQ_TRC_047_given_the_legend_then_it_shows_the_box_kinds(self):
        dom = rendered_dom(self.path)
        for kind in ("namespace", "class", "global"):
            self.assertIn(f'<span class="legend-box box-{kind}"></span>', dom)

    def test_RQ_TRC_016_given_the_global_box_when_selected_then_its_panel_lists_the_functions_outside_any_namespace(self):
        dom = rendered_dom(self.path, fragment(GLOBAL_BOX))
        panel = dom[dom.index('id="detail"'):]
        panel = panel[:panel.index("</aside>")]                                 # the matrix lists functions too
        self.assertIn('<h2 class="detail-id">(global namespace)</h2>', panel)                  # RQ-TRC-048
        self.assertIn("Global namespace", panel)
        for name in ("relay", "log", "operator==", "helper", "table", "run"):
            self.assertIn(f'<span class="id">{name}</span>', panel)
        self.assertNotIn('<span class="id">net::Port::send</span>', panel)

    def test_RQ_TRC_047_given_a_page_without_call_graph_then_neither_control_appears(self):
        dom = rendered_dom(self.plain)
        for absent in ('id="detail-level"', 'id="show-enclosing"', 'class="legend-box'):     # the page's script names them
            self.assertNotIn(absent, dom)


def toolbar(dom):
    """The graph toolbar of a dumped page: [(fieldset id, its label, [(input id, label text)])] in their order."""
    import re
    bar = dom[dom.index('<div class="toolbar">', dom.index('id="view-graph"')):]
    bar = bar[:bar.index('<span class="toolbar-spacer">')]
    groups = []
    for fieldset in re.findall(r"<fieldset.*?</fieldset>", bar, re.S):
        label = re.search(r'<span class="segmented-label">([^<]*)</span>', fieldset).group(1)
        inputs = re.findall(r'<input type="checkbox" id="([\w-]+)"[^>]*>\s*([^<]+?)\s*</label>', fieldset)
        groups.append((re.search(r'id="([\w-]+)"', fieldset).group(1), label, inputs))
    return groups


@unittest.skipUnless(HAS_TREE_SITTER and BROWSER, NEEDS_TREE_SITTER + ", or no Chromium-family browser found")
class ToolbarWordsTest(unittest.TestCase):
    """TASK-TRC-029: RQ-TRC-048, RQ-TRC-044 (DEC-TRC-023), in a real browser."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "page.html"
        page, _ = call_graph_page(cls.path)
        data = json.loads(data_block(page))
        cls.paths = [f["path"] for f in data["files"]]
        cls.keys = {f[3]: f"fn:{cls.paths[f[0]]}:{f[1]}" for f in data["callGraph"]["functions"]}
        cls.port = "file:" + next(p for p in cls.paths if p.endswith("calls/net/port.hpp"))
        cls.plain = Path(cls.tmp.name) / "plain.html"
        generate(cls.plain)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_RQ_TRC_048_given_the_call_graph_page_then_the_toolbar_has_three_groups_and_display_holds_four_switches(self):
        self.assertEqual([("depth", "Depth", []),
                          ("display", "Display", [("show-files", "Source files"), ("show-functions", "Implementation"),
                                                  ("show-hierarchy", "Specification hierarchy"),
                                                  ("show-enclosing", "Enclosing scopes")]),
                          ("detail-level", "Implementation detail", [])],           # TASK-TRC-030: the reading order
                         toolbar(rendered_dom(self.path)))

    def implementation_states(self, script):
        import re
        dom = rendered_dom_after(self.path, script + "const out = document.documentElement.dataset;"
                                 "out.choice = String(document.getElementById('detail-level').disabled);"
                                 "out.enclosing = String(document.getElementById('show-enclosing').disabled);"
                                 "out.buttons = String([...document.querySelectorAll('#detail-level button')]"
                                 ".every((b) => b.matches(':disabled')));")           # disabled by their fieldset
        return dict(re.findall(r'data-(choice|enclosing|buttons)="([^"]*)"', dom))

    def test_RQ_TRC_048_given_implementation_off_then_the_detail_choice_and_enclosing_scopes_are_disabled(self):
        self.assertEqual({"choice": "true", "enclosing": "true", "buttons": "true"}, self.implementation_states(""))

    def test_RQ_TRC_048_given_implementation_turned_on_then_they_are_enabled_and_turned_off_again_disabled(self):
        click = "document.getElementById('show-functions').click();"
        self.assertEqual({"choice": "false", "enclosing": "false", "buttons": "false"}, self.implementation_states(click))
        self.assertEqual({"choice": "true", "enclosing": "true", "buttons": "true"},
                         self.implementation_states(click + click))

    def test_RQ_TRC_048_given_the_functions_type_filter_then_the_detail_choice_follows_it(self):
        self.assertEqual({"choice": "false", "enclosing": "false", "buttons": "false"},
                         self.implementation_states(TURN_FUNCTIONS_ON))

    def test_RQ_TRC_048_given_the_namespace_detail_with_implementation_on_then_enclosing_scopes_stay_disabled(self):
        states = self.implementation_states(TURN_FUNCTIONS_ON + CLICK_DETAIL.format("namespace"))
        self.assertEqual({"choice": "false", "enclosing": "true"}, {k: states[k] for k in ("choice", "enclosing")})

    def test_RQ_TRC_048_given_the_tokens_then_a_group_label_has_a_background_and_a_text_token(self):
        tokens = tm.load_tokens(tm.TOKENS_PATH)["component"]
        self.assertIn("group-label-bg", tokens)
        self.assertIn("group-label-text", tokens)

    def test_RQ_TRC_048_given_a_page_without_call_graph_then_display_holds_source_files_and_the_hierarchy(self):
        self.assertEqual([("depth", "Depth", []), ("display", "Display", [("show-files", "Source files"),
                                                                          ("show-hierarchy", "Specification hierarchy")])],
                         toolbar(rendered_dom(self.plain)))

    def test_RQ_TRC_048_given_functions_drawn_then_their_column_is_implementation(self):
        nodes, _ = drawing(self.path, "agnosTrace.select('RQ-DEM-001'); agnosTrace.showView('graph');")
        headers = [n["label"] for key, n in nodes.items() if key.startswith("header:")]
        self.assertIn("Implementation · 1", headers)
        self.assertFalse([h for h in headers if h.startswith("Functions")])

    def test_RQ_TRC_048_given_the_hierarchy_off_then_the_feature_goes_and_the_file_still_defines_its_function(self):
        nodes, edges = drawing(self.path, "document.getElementById('show-hierarchy').click();"
                                          "agnosTrace.select('RQ-DEM-001'); agnosTrace.showView('graph');")
        self.assertNotIn("FTR-DEM-001", nodes)
        self.assertIn(f"{self.port}>{self.keys['net::Port::send']}>defines", edges)
        self.assertFalse([e for e in edges.values() if e["kind"] == "contains"])

    def test_RQ_TRC_048_given_source_files_off_then_no_file_and_no_defines_link_is_drawn(self):
        nodes, edges = drawing(self.path, "document.getElementById('show-files').click();"
                                          "agnosTrace.select('RQ-DEM-001'); agnosTrace.showView('graph');")
        self.assertFalse([key for key in nodes if key.startswith("file:")])
        self.assertFalse([e for e in edges.values() if e["kind"] == "defines"])
        self.assertIn("FTR-DEM-001", nodes)


READ_LEGEND = """
const out = document.documentElement.dataset;
out.looks = JSON.stringify(agnosTrace.EDGE_LOOK);
out.samples = String(document.querySelectorAll("#legend svg.legend-edge").length);
out.legendText = document.getElementById("legend").textContent;
"""


@unittest.skipUnless(HAS_TREE_SITTER and BROWSER, NEEDS_TREE_SITTER + ", or no Chromium-family browser found")
class RelationLookTest(unittest.TestCase):
    """TASK-TRC-019: RQ-TRC-044 (DEC-TRC-006, DEC-TRC-017), in a real browser."""

    def test_RQ_TRC_044_given_the_relations_then_each_has_its_own_line_and_colour_an_arrow_and_a_drawn_sample(self):
        import html
        import re
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "page.html"
            call_graph_page(path)
            found = dict(re.findall(r'data-(looks|samples|legend-text)="([^"]*)"', rendered_dom_after(path, READ_LEGEND)))
        looks = json.loads(html.unescape(found["looks"]))
        self.assertEqual({"contains", "defines", "refs", "code", "calls", "ambiguous"}, set(looks))   # RQ-TRC-048
        colours = [look["colour"] for look in looks.values()]
        self.assertEqual(len(colours), len(set(colours)))                    # a colour of its own each
        self.assertTrue(all(look["arrow"] and look["arrow"] != "none" for look in looks.values()))
        self.assertEqual(str(len(looks)), found["samples"])
        legend = html.unescape(found["legend-text"])
        self.assertNotRegex(legend, r"\b(dashed|solid|dotted|straight)\b")
        self.assertIn("caller → callee", legend)


@unittest.skipUnless(HAS_TREE_SITTER and BROWSER, NEEDS_TREE_SITTER + ", or no Chromium-family browser found")
class RelationTooltipTest(unittest.TestCase):
    """TASK-TRC-020: RQ-TRC-046 (DEC-TRC-006), in a real browser."""

    def test_RQ_TRC_046_given_a_call_link_when_its_tooltip_is_asked_then_it_says_the_relation_and_its_ends_in_order(self):
        import html
        import re
        self.assertEqual("1000ms", tm.load_tokens(tm.TOKENS_PATH)["global"]["duration.tooltip"])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "page.html"
            page, _ = call_graph_page(path)
            data = json.loads(data_block(page))
            paths = [f["path"] for f in data["files"]]
            keys = {f[3]: f"fn:{paths[f[0]]}:{f[1]}" for f in data["callGraph"]["functions"]}
            edge = f"{keys['net::Port::send']}>{keys['net::Port::write']}>calls"
            dom = rendered_dom_after(path, TURN_FUNCTIONS_ON + f"agnosTrace.select('{keys['net::Port::write']}');"
                                     f"agnosTrace.showView('graph');"
                                     f"document.documentElement.dataset.tip = agnosTrace.graph.tipFor('{edge}');")
        tip = html.unescape(re.search(r'data-tip="([^"]*)"', dom).group(1))
        self.assertIn("calls (caller → callee)", tip)
        self.assertLess(tip.index("net::Port::send"), tip.index("net::Port::write"))


SHOW_CSV = ("document.body.append(Object.assign(document.createElement('pre'), "
            "{ id: 'csv-text', textContent: agnosTrace.csvText() }));")


@unittest.skipUnless(HAS_TREE_SITTER and BROWSER, NEEDS_TREE_SITTER + ", or no Chromium-family browser found")
class FunctionMatrixTest(unittest.TestCase):
    """TASK-TRC-015: RQ-TRC-041 (DEC-TRC-017, DEC-TRC-007), in a real browser."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "page.html"
        call_graph_page(cls.path)
        cls.plain = Path(cls.tmp.name) / "plain.html"
        generate(cls.plain)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_RQ_TRC_041_given_the_call_graph_when_the_matrix_opens_then_each_row_lists_its_functions_and_the_csv_too(self):
        import re
        dom = rendered_dom_after(self.path, "agnosTrace.showView('matrix');" + SHOW_CSV)
        self.assertRegex(dom, r'data-column="functions"[^>]*>Functions<span class="col-grip"')   # the grip: RQ-TRC-043
        for label in ("ADRs / decisions", "Plans / tasks", "Functions", "Source files"):    # aligned with their cells
            self.assertRegex(dom, rf'<th class="sortable *"[^>]*>{re.escape(label)}<span class="col-grip"')
        self.assertRegex(dom, r'<th class="sortable num"[^>]*>Lines<span class="col-grip"')
        order = re.findall(r'<th [^>]*data-column="(\w+)"', dom)       # RQ-TRC-051: Functions before the source files
        self.assertEqual(["feature", "id", "coverage", "decisions", "tasks", "functions", "files", "lines"], order)
        row = re.search(r'<tr[^>]*data-key="RQ-DEM-001".*?</tr>', dom, re.S).group(0)
        self.assertIn('<span class="id">net::Port::send</span>', row)
        csv = re.search(r'<pre id="csv-text">(.*?)</pre>', dom, re.S).group(1)
        header, *rows = csv.splitlines()
        self.assertIn(",Functions,", header)
        self.assertIn("net::Port::send", next(r for r in rows if r.startswith("RQ-DEM-001,")))

    def test_RQ_TRC_041_given_the_toolbar_switch_when_turned_on_then_the_function_type_filter_is_on(self):
        dom = rendered_dom_after(self.path, "document.getElementById('show-functions').click();")
        self.assertRegex(dom, r'<button class="chip t-FN" type="button" aria-pressed="true"[ >]')   # then its tooltip

    def test_RQ_TRC_041_given_a_requirement_no_function_cites_when_selected_then_its_panel_says_functions_0(self):
        dom = rendered_dom(self.path, "#RQ-DEM-003")
        self.assertIn("Functions 0", dom)

    def test_RQ_TRC_063_given_the_call_graph_in_a_1440_by_900_window_then_all_nine_checks_are_reached_by_scrolling(self):
        import re
        script = ("agnosTrace.showView('quality'); const view = document.getElementById('view-quality');"
                  "const cards = [...document.querySelectorAll('#quality-list .check-card')];"
                  "const last = cards.find((c) => c.dataset.check === 'functions-traced');"
                  "const d = document.documentElement.dataset; d.checks = String(cards.length);"
                  "d.fits = getComputedStyle(view).overflowY; last.scrollIntoView();"   # TASK-TRC-074: the area scrolls
                  "d.visible = String(last.getBoundingClientRect().bottom <= view.getBoundingClientRect().bottom + 1);")
        dom = rendered_dom_after(self.path, script, "1440,900")
        found = dict(re.findall(r'data-(checks|fits|visible)="([^"]*)"', dom))
        self.assertEqual({"checks": "9", "fits": "auto", "visible": "true"}, found)

    def test_RQ_TRC_041_given_a_page_without_call_graph_then_no_function_column_switch_or_count_appears(self):
        dom = rendered_dom_after(self.plain, "agnosTrace.showView('matrix'); agnosTrace.select('RQ-DEM-003');")
        for absent in ('data-column="functions"', 'id="show-functions"', "Functions 0"):
            self.assertNotIn(absent, dom)


PERF_FILES = 2000
PERF_PER_FILE = 10
PERF_CALLEES = ((1, 0), (7, 1), (13, 3), (29, 7))           # (file step, function step) of each function's callees
PERF_NAMESPACES = 20                                         # file i holds class C<i> in namespace ns<i % 20>


def write_large_tree(root):
    """2,000 C++ files of one class of 10 methods, in 20 namespaces; each method calls hub() and four others: 20,001
    functions, 100,000 calls."""
    (root / "hub.cpp").write_text("int hub()\n{\n    return 0;\n}\n", encoding="utf-8")
    for i in range(PERF_FILES):
        body = []
        for j in range(PERF_PER_FILE):
            callees = " + ".join(f"f_{(i + di) % PERF_FILES}_{(j + dj) % PERF_PER_FILE}()" for di, dj in PERF_CALLEES)
            body.append(f"int f_{i}_{j}()\n{{\n    return hub() + {callees};\n}}\n")
        text = f"namespace ns{i % PERF_NAMESPACES} {{\nstruct C{i} {{\n" + "\n".join(body) + "};\n}\n"
        (root / f"m{i:04d}.cpp").write_text(text, encoding="utf-8")


# RQ-TRC-047, RQ-TRC-037: the drawing of the selection at each level of detail, timed by the page.
READ_LEVELS = """
const levels = {};
for (const level of ["function", "class", "namespace"]) {
  agnosTrace.graph.setDetail(level);
  const graph = document.getElementById("cy").dataset;
  levels[level] = [Number(graph.graphNodes), Number(graph.graphMs)];
}
document.documentElement.dataset.levels = JSON.stringify(levels);
"""


def rendered_dom_live(page_path, script):
    """Like rendered_dom_after, without virtual time: the page's own timings are real."""
    copy = page_path.with_name("live-" + page_path.name)
    copy.write_text(page_path.read_text(encoding="utf-8").replace("</body>", f"<script>{script}</script></body>"),
                    encoding="utf-8")
    with tempfile.TemporaryDirectory() as profile:
        done = subprocess.run([BROWSER, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                               f"--user-data-dir={profile}", "--window-size=1600,1000", "--dump-dom", copy.resolve().as_uri()],
                              capture_output=True, timeout=300, check=False)
    return done.stdout.decode("utf-8", errors="replace")


@unittest.skipUnless(HAS_TREE_SITTER and BROWSER and __import__("os").environ.get("AGNOS_PERF_CENTER_PERF"),
                     "set AGNOS_PERF_CENTER_PERF=1 (needs tree-sitter and a Chromium-family browser): about a minute")
class LargeCallGraphTest(unittest.TestCase):
    """TASK-TRC-013: RQ-TRC-036, RQ-TRC-037, RQ-TRC-038 (DEC-TRC-016, DEC-TRC-017), on a generated tree."""

    def test_RQ_TRC_036_to_038_given_20000_functions_and_100000_calls_then_time_size_and_drawing_stay_in_their_limits(
            self):
        import re
        import time
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "src"
            root.mkdir()
            write_large_tree(root)
            timings = {}
            for name, extra in (("warm-up", ()), ("without", ()), ("with", ("--call-graph",))):   # warm disk cache first
                started = time.perf_counter()
                page, out = generate(Path(tmp) / f"{name}.html", "--sources", str(root), *extra)
                timings[name] = (time.perf_counter() - started, output_bytes(page))
            counts = json.loads(data_block(page))["callGraph"]["counts"]
            dom = rendered_dom_live(Path(tmp) / "with.html", TURN_FUNCTIONS_ON +
                                    "document.querySelector('#depth button[data-depth=\"2\"]').click();"
                                    "agnosTrace.select([...agnosTrace.nodes.values()].find((n) => n.label === 'hub').key);"
                                    "agnosTrace.showView('graph');" + READ_LEVELS)
            quality = rendered_dom_live(Path(tmp) / "with.html",
                                        "const t0 = performance.now(); agnosTrace.renderQuality();"
                                        "document.documentElement.dataset.quality = String(Math.round(performance.now() - t0));")
        added_time = timings["with"][0] - timings["without"][0]
        added_bytes = timings["with"][1] - timings["without"][1]
        attributes = graph_attributes(dom)
        ready = int(re.search(r'data-ready-ms="(\d+)"', dom).group(1))
        levels = json.loads(__import__("html").unescape(re.search(r'data-levels="([^"]*)"', dom).group(1)))
        print(f"\n  run {timings['without'][0]:.1f} s, with the call graph {timings['with'][0]:.1f} s (+{added_time:.1f} s), "
              f"page +{added_bytes} bytes, interactive {ready} ms, "
              f"graph {attributes['nodes']} nodes in {attributes['ms']} ms: {attributes['status']}; "
              f"levels (nodes, ms): {levels}")
        for level, (drawn, ms) in levels.items():                                         # RQ-TRC-047, TASK-TRC-025
            self.assertLessEqual(drawn, 400, level)
            self.assertLess(ms, 500, level)
        self.assertEqual((20004, 100000), (counts["functions"], counts["calls"]))   # + the 3 functions of the fixture's src/
        self.assertLess(added_time, 30)                                                       # RQ-TRC-036
        self.assertLessEqual(added_bytes, 120 * counts["functions"] + 16 * counts["calls"])   # RQ-TRC-038
        self.assertLess(ready, 3000)                                                          # RQ-TRC-037
        self.assertLess(int(re.search(r'data-quality="(\d+)"', quality).group(1)), 200)         # RQ-TRC-066
        self.assertLessEqual(int(attributes["nodes"]), 400)
        self.assertLess(int(attributes["ms"]), 500)
        self.assertRegex(attributes["status"], r"\d+ not drawn")


if __name__ == "__main__":
    unittest.main()
