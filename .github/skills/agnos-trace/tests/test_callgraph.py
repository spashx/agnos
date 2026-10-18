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
from test_trace_matrix import (BROWSER, FIXTURE, PROCESS, SKILL, SOURCES, data_block, generate,  # noqa: E402
                               rendered_dom, rendered_dom_after, run_main)

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
        cls.page, _ = call_graph_page(Path(cls.tmp.name) / "page.html")
        cls.data = json.loads(data_block(cls.page))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_RQ_TRC_038_given_the_call_graph_when_embedded_then_functions_are_a_table_and_calls_a_flat_integer_list(self):
        graph = self.data["callGraph"]
        self.assertEqual(12, len(graph["functions"]))           # the 11 of calls/ and src/lib/b.cpp's indirect()
        paths = [f["path"] for f in self.data["files"]]
        file_index, first, last, name, language = graph["functions"][1][:5]
        self.assertTrue(paths[file_index].endswith("/calls/net/port.hpp"), paths[file_index])   # shown from the cwd
        self.assertEqual((7, 7, "net::Port::send"), (first, last, name))
        self.assertEqual("cpp", graph["languages"][language])
        self.assertTrue(all(isinstance(n, int) for n in graph["calls"]))
        self.assertEqual({"functions": 12, "calls": 8, "ambiguous": 2, "external": 2}, graph["counts"])

    def test_RQ_TRC_038_given_the_call_graph_when_embedded_then_it_adds_at_most_120_bytes_per_function_and_16_per_call(
            self):
        without, _ = generate(Path(self.tmp.name) / "without.html", "--sources", str(CALLS))
        counts = self.data["callGraph"]["counts"]
        added = len(self.page.encode("utf-8")) - len(without.encode("utf-8"))
        self.assertLessEqual(added, 120 * counts["functions"] + 16 * counts["calls"])

    def test_RQ_TRC_035_given_the_call_graph_when_embedded_then_untraced_functions_are_listed_outside_the_gaps(self):
        graph = self.data["callGraph"]
        names = [graph["functions"][i][3] for i in graph["untraced"]]
        self.assertEqual(8, len(names))
        self.assertNotIn("net::Port::send", names)
        self.assertNotIn("untraced-functions", self.data["gapKinds"])


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

    def test_RQ_TRC_035_given_the_call_graph_when_the_page_opens_then_the_overview_and_gaps_show_it_uninflated(self):
        data = json.loads(data_block(self.path.read_text(encoding="utf-8")))
        total = sum(len(data["gaps"][g]) for g in data["gapKinds"])
        dom = rendered_dom(self.path)
        self.assertIn('<h2 class="card-title">Call graph</h2>', dom)
        self.assertIn("8 call links", dom)
        self.assertIn("Untraced functions", dom)
        self.assertIn(f'<span class="tab-count" id="gaps-count">{total}</span>', dom)


TURN_FUNCTIONS_ON = ("[...document.querySelectorAll('#type-filters .chip')]"
                     ".find((b) => b.textContent.startsWith('Functions')).click();")


def graph_attributes(dom):
    import re
    found = dict(re.findall(r'data-graph-(\w+)="([^"]*)"', dom))
    status = re.search(r'id="graph-status">([^<]*)<', dom)
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


PERF_FILES = 2000
PERF_PER_FILE = 10
PERF_CALLEES = ((1, 0), (7, 1), (13, 3), (29, 7))           # (file step, function step) of each function's callees


def write_large_tree(root):
    """2,000 C++ files of 10 functions; each function calls hub() and four others: 20,001 functions, 100,000 calls."""
    (root / "hub.cpp").write_text("int hub()\n{\n    return 0;\n}\n", encoding="utf-8")
    for i in range(PERF_FILES):
        body = []
        for j in range(PERF_PER_FILE):
            callees = " + ".join(f"f_{(i + di) % PERF_FILES}_{(j + dj) % PERF_PER_FILE}()" for di, dj in PERF_CALLEES)
            body.append(f"int f_{i}_{j}()\n{{\n    return hub() + {callees};\n}}\n")
        (root / f"m{i:04d}.cpp").write_text("\n".join(body), encoding="utf-8")


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


@unittest.skipUnless(HAS_TREE_SITTER and BROWSER and __import__("os").environ.get("AGNOS_TRACE_PERF"),
                     "set AGNOS_TRACE_PERF=1 (needs tree-sitter and a Chromium-family browser): about a minute")
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
                timings[name] = (time.perf_counter() - started, len(page.encode("utf-8")))
            counts = json.loads(data_block(page))["callGraph"]["counts"]
            dom = rendered_dom_live(Path(tmp) / "with.html", TURN_FUNCTIONS_ON +
                                    "document.querySelector('#depth button[data-depth=\"2\"]').click();"
                                    "agnosTrace.select([...agnosTrace.nodes.values()].find((n) => n.label === 'hub').key);"
                                    "agnosTrace.showView('graph');")
        added_time = timings["with"][0] - timings["without"][0]
        added_bytes = timings["with"][1] - timings["without"][1]
        attributes = graph_attributes(dom)
        ready = int(re.search(r'data-ready-ms="(\d+)"', dom).group(1))
        print(f"\n  run {timings['without'][0]:.1f} s, with the call graph {timings['with'][0]:.1f} s (+{added_time:.1f} s), "
              f"page +{added_bytes} bytes, interactive {ready} ms, "
              f"graph {attributes['nodes']} nodes in {attributes['ms']} ms: {attributes['status']}")
        self.assertEqual((20002, 100000), (counts["functions"], counts["calls"]))   # + indirect() of the fixture's src/
        self.assertLess(added_time, 30)                                                       # RQ-TRC-036
        self.assertLessEqual(added_bytes, 120 * counts["functions"] + 16 * counts["calls"])   # RQ-TRC-038
        self.assertLess(ready, 3000)                                                          # RQ-TRC-037
        self.assertLessEqual(int(attributes["nodes"]), 400)
        self.assertLess(int(attributes["ms"]), 500)
        self.assertRegex(attributes["status"], r"\d+ not drawn")


if __name__ == "__main__":
    unittest.main()
