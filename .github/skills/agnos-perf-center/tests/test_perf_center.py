"""Tests of the agnos-perf-center generator (FTR-TRC-001), on the synthetic process of tests/fixtures/repo.

Run from the repository root: python -m unittest discover -s .github/skills/agnos-perf-center/tests -v
"""
import contextlib
import io
import re
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "agnos-graph" / "scripts"))   # DEC-TRC-074: the moved modules
import agnos_layout  # noqa: E402  RQ-PLG-036: the index and log names, as the scripts read them

import graph as gr  # noqa: E402
import perf_center as tm  # noqa: E402

FIXTURE = HERE / "fixtures" / "repo"
PROCESS = FIXTURE / "process"
SOURCES = FIXTURE / "src"
GRAPH_FOLDER_FILE = "4.knowledge/graph/agnos-graph.json"   # RQ-TRC-142 / DEC-TRC-086: the default graph read, stated, not read


# RQ-TRC-131 (TASK-TRC-118): the options of the scan go to agnos-graph, which writes the graph the page is made from.
GRAPH_VALUED = ("--sources", "--ext", "--exclude", "--history-since", "--history-depth")
GRAPH_FLAGS = ("--call-graph", "--history")
SHARED = ("--process", "--generated-at")


def split_options(args):
    """(the graph script's options, the page's) of a run written as one command line, as before the separation."""
    graph_args, page_args, rest = [], [], list(args)
    while rest:
        option = rest.pop(0)
        if option in GRAPH_FLAGS:
            graph_args.append(option)
        elif option in GRAPH_VALUED:
            graph_args += [option, rest.pop(0)]
        elif option in SHARED:
            value = rest.pop(0)
            graph_args += [option, value]
            page_args += [option, value]
        else:
            page_args.append(option)
    return graph_args, page_args


def run_main(args):
    """Builds the graph with agnos-graph, then runs the generator on it; returns (exit code, the generator's stdout, the
    stderr of both)."""
    graph_args, page_args = split_options(args)
    out, err, graph_out = io.StringIO(), io.StringIO(), io.StringIO()
    with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stderr(err):
        graph_file = str(Path(tmp) / "agnos-graph.json")
        with contextlib.redirect_stdout(graph_out):
            code = gr.main([*graph_args, "--out", graph_file]) if "--sources" in graph_args else 0
        if code == 0:
            with contextlib.redirect_stdout(out):
                code = tm.main([*page_args, "--graph", graph_file] if "--sources" in graph_args else page_args)
    return code, out.getvalue(), err.getvalue()


class GeneratorInputTest(unittest.TestCase):
    """TASK-TRC-001: RQ-TRC-002, through the graph the generator reads since TASK-TRC-118 (RQ-TRC-131)."""

    def test_RQ_TRC_002_given_no_index_when_the_generator_runs_then_it_exits_1_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "page.html"
            code, _, err = run_main(["--process", tmp, "--sources", str(SOURCES), "--out", str(out)])
            self.assertEqual(1, code)
            self.assertIn(agnos_layout.INDEX, err)
            self.assertFalse(out.exists())

    def test_RQ_TRC_002_given_a_missing_source_folder_when_the_generator_runs_then_it_exits_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "page.html"
            code, _, err = run_main(["--process", str(PROCESS), "--sources", str(Path(tmp) / "nope"), "--out", str(out)])
            self.assertEqual(1, code)
            self.assertIn("nope", err)
            self.assertFalse(out.exists())


def scanned_model(**options):
    """The fixture model with its sources scanned, file paths shown relative to the fixture repository (agnos-graph's
    model, which the analysis reads as the graph file's, DEC-TRC-075)."""
    model = gr.build_process_model(PROCESS)
    gr.scan_sources(model, [SOURCES], base=FIXTURE, **options)
    return model


class CoverageAndFindingsTest(unittest.TestCase):
    """TASK-TRC-003: RQ-TRC-008, RQ-TRC-009, RQ-TRC-017 (DEC-TRC-002, DEC-TRC-004)."""

    @classmethod
    def setUpClass(cls):
        cls.analysis = tm.analyse(scanned_model())

    def test_RQ_TRC_008_given_the_fixture_when_coverage_is_computed_then_each_requirement_has_its_rating(self):
        self.assertEqual({"RQ-DEM-001": "covered", "RQ-DEM-002": "indirect", "RQ-DEM-003": "uncovered",
                          "RQ-DEM-004": "uncovered", "RQ-DEM-005": "uncovered"}, self.analysis["coverage"])

    def test_RQ_TRC_008_given_a_requirement_depending_on_a_covered_one_when_rated_then_the_dependency_does_not_cover_it(
            self):
        model = gr.build_process_model(PROCESS)                 # TASK-TRC-118: the model is agnos-graph's
        model.add_edge("src/x.py", "RQ-DEM-001", "code", [1, "RQ-DEM-001"])
        self.assertEqual("uncovered", tm.analyse(model)["coverage"]["RQ-DEM-002"])

    def test_RQ_TRC_009_given_the_fixture_when_findings_are_listed_then_each_list_holds_its_planted_elements(self):
        self.assertEqual({"uncovered": ["RQ-DEM-003", "RQ-DEM-004", "RQ-DEM-005"],
                          "untasked": ["RQ-DEM-004", "RQ-DEM-005"],
                          "task-no-rq": ["TASK-DEM-003"],
                          "adr-no-rq": ["ADR-DEM-002"],
                          "empty": ["FTR-DEM-002", "ADR-DEM-002", "PLAN-DEM-002"],
                          "isolated": ["RQ-DEM-005", "FTR-DEM-002", "ADR-DEM-002", "PLAN-DEM-002"],
                          "undefined": ["DEC-DEM-099", "RQ-DEM-099"],
                          "untraced-files": ["src/notrace.py"]}, self.analysis["findings"])

    def test_RQ_TRC_017_given_the_fixture_when_the_generator_runs_then_it_prints_the_counts_and_the_quality(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out, _ = run_main(["--process", str(PROCESS), "--sources", str(SOURCES), "--out",
                                     str(Path(tmp) / "page.html")])
        self.assertEqual(0, code)
        summary = out.strip().splitlines()[-1]
        for part in ("15 elements", "4 files", "RQ 5: covered 1, indirect 1, uncovered 3", "quality: C 6.1/10",
                     "covered 4.0", "defined 7.5", "tasked 6.0", "task-rq 6.7", "adr-rq 5.0", "filled 5.0",
                     "connected 7.3", "files-traced 7.5", "findings 17"):
            self.assertIn(part, summary)

    def test_RQ_TRC_107_given_the_fixture_when_the_generator_runs_then_the_last_stdout_line_ends_with_the_duration(self):
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "page.html"
            code, out, _ = run_main(["--process", str(PROCESS), "--sources", str(SOURCES), "--out", str(page)])
            generated = page.read_text(encoding="utf-8") + page.with_suffix(".json").read_text(encoding="utf-8")
        self.assertEqual(0, code)
        lines = out.strip().splitlines()
        self.assertRegex(lines[-1], DURATION_LINE_RE)
        self.assertEqual(1, len([line for line in lines if re.search(DURATION_LINE_RE, line)]))
        self.assertNotRegex(generated, DURATION_OUTPUT_RE)    # the generated files stay deterministic


DURATION_LINE_RE = r" written in \d+\.\d{3} s$"    # RQ-TRC-107
DURATION_OUTPUT_RE = r" in \d+\.\d{3} s"
GENERATED_AT = "2026-01-01T00:00Z"
SKILL = HERE.parent
RAW_VISUAL_RE = r"#[0-9A-Fa-f]{3,8}\b|\brgba?\(|\bhsla?\(|\b\d+(?:\.\d+)?(?:px|ms)\b"


class PageText(str):
    """A generated page's text, and the path it was written to: its data files stand beside it (RQ-TRC-010)."""
    path = None


def generate(out, *extra):
    code, stdout, stderr = run_main(["--process", str(PROCESS), "--sources", str(SOURCES), "--out", str(out),
                                     "--generated-at", GENERATED_AT, *extra])
    if code:
        raise AssertionError(stderr)
    page = PageText(out.read_text(encoding="utf-8"))
    page.path = out
    return page, stdout


def data_block(page):
    """The JSON of a generated page, read from its <page>.json (a PageText from generate, or the page's path)."""
    path = page if isinstance(page, Path) else page.path
    return tm.data_paths(path)[0].read_text(encoding="utf-8").strip()


def comparable(page):
    """A page and its data with the data file's own name blanked: what two runs to two names must share."""
    return page.replace(page.path.stem + tm.DATA_SCRIPT_SUFFIX, "@") + data_block(page)


def output_bytes(page):
    """The size of a page and of its data, the part loaded by the browser (RQ-TRC-038)."""
    return len(page.encode("utf-8")) + tm.data_paths(page.path)[1].stat().st_size


class PageAssemblyTest(unittest.TestCase):
    """TASK-TRC-004: RQ-TRC-001, RQ-TRC-010, RQ-TRC-018, RQ-TRC-022 to RQ-TRC-024 (DEC-TRC-005, DEC-TRC-006,
    DEC-TRC-009, DEC-TRC-010)."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.page, cls.stdout = generate(Path(cls.tmp.name) / "page.html")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_RQ_TRC_010_given_a_generated_page_when_searched_then_it_loads_only_its_libraries_and_its_data_script(self):
        import json
        import re
        lowered = self.page.lower()
        libraries = json.loads(tm.LIBRARIES_PATH.read_text(encoding="utf-8"))["libraries"]
        scripts = re.findall(r'<script src="([^"]*)"([^>]*)>', self.page)          # RQ-TRC-080 amends RQ-TRC-010
        self.assertEqual([lib["url"] for lib in libraries] + ["page.data.js"], [src for src, _ in scripts])
        for (src, attributes), lib in zip(scripts, libraries):
            self.assertTrue(src.startswith("https://cdnjs.cloudflare.com/ajax/libs/"), src)
            self.assertIn(f'integrity="{lib["integrity"]}"', attributes)
            self.assertIn('crossorigin="anonymous"', attributes)
        # RQ-TRC-103, RQ-TRC-111: the links of the About and Licenses topics load nothing until followed; any other address is still refused
        loaded = re.sub(r'<a class="(?:about-link|licence-badge licence-badge-link)" href="https://[^"]*"', "", lowered)
        for needle in ("<link", "url(http", "@import", "href=\"http"):
            self.assertNotIn(needle, loaded)
        json_path, script_path = tm.data_paths(self.page.path)
        script = script_path.read_text(encoding="utf-8")
        self.assertTrue(script.startswith(tm.DATA_GLOBAL + " = "))
        self.assertEqual(json.loads(json_path.read_text(encoding="utf-8")),
                         json.loads(script[len(tm.DATA_GLOBAL + " = "):].rstrip().rstrip(";")))

    def test_RQ_TRC_010_given_the_data_script_missing_when_the_page_opens_then_it_names_the_file(self):
        import shutil
        if not BROWSER:
            self.skipTest("no Chromium-family browser found (set AGNOS_PERF_CENTER_BROWSER)")
        lonely = Path(self.tmp.name) / "alone" / "page.html"
        lonely.parent.mkdir(exist_ok=True)
        shutil.copy(self.page.path, lonely)
        dom = rendered_dom(lonely)
        self.assertIn('class="data-missing"', dom)
        self.assertIn("page.data.js", dom)

    def test_RQ_TRC_023_given_one_generated_at_when_generated_twice_then_the_pages_are_identical_and_in_lf(self):
        again, _ = generate(Path(self.tmp.name) / "again.html")
        self.assertEqual(comparable(self.page), comparable(again))
        for path in (again.path, *tm.data_paths(again.path)):
            self.assertNotIn(b"\r", path.read_bytes(), path.name)

    def test_RQ_TRC_082_given_the_library_record_then_each_library_has_an_exact_version_a_cdnjs_url_and_a_hash(self):
        import json
        import re
        libraries = json.loads(tm.LIBRARIES_PATH.read_text(encoding="utf-8"))["libraries"]
        self.assertEqual({"cytoscape", "echarts"}, {lib["global"] for lib in libraries})
        for lib in libraries:
            self.assertRegex(lib["version"], r"^\d+\.\d+\.\d+$")
            self.assertIn(f"/{lib['version']}/", lib["url"])
            self.assertRegex(lib["integrity"], r"^sha512-[A-Za-z0-9+/]{86}==$")
            self.assertTrue(lib["licence"] and lib["name"], lib)
        self.assertFalse((SKILL / "scripts" / "vendor").exists())                 # DEC-TRC-040: no vendored copy

    def test_RQ_TRC_082_given_a_version_changed_in_the_record_then_the_page_loads_that_version(self):
        import json
        from unittest import mock
        record = json.loads(tm.LIBRARIES_PATH.read_text(encoding="utf-8"))
        record["libraries"][0]["version"] = "9.9.9"
        record["libraries"][0]["url"] = record["libraries"][0]["url"].replace("3.30.2", "9.9.9")
        changed = Path(self.tmp.name) / "libraries.json"
        changed.write_text(json.dumps(record), encoding="utf-8")
        with mock.patch.object(tm, "LIBRARIES_PATH", changed):
            again, _ = generate(Path(self.tmp.name) / "changed.html")
        self.assertIn("/cytoscape/9.9.9/cytoscape.min.js", again)
        data = json.loads(tm.data_paths(again.path)[0].read_text(encoding="utf-8"))
        self.assertIn({"name": "Cytoscape.js", "version": "9.9.9", "licence": "MIT"},
                      [{k: lib[k] for k in ("name", "version", "licence")} for lib in data["meta"]["libraries"]])

    def test_RQ_TRC_081_given_libraries_that_cannot_load_then_the_graph_says_so_and_the_matrix_works(self):
        import json
        import re
        if not BROWSER_FOUND:
            self.skipTest("no Chromium-family browser found (set AGNOS_PERF_CENTER_BROWSER)")
        offline = Path(self.tmp.name) / "offline" / "page.html"
        offline.parent.mkdir(exist_ok=True)
        for source in (self.page.path, *tm.data_paths(self.page.path)):
            (offline.parent / source.name).write_bytes(source.read_bytes())
        text = offline.read_text(encoding="utf-8")
        for lib in json.loads(tm.LIBRARIES_PATH.read_text(encoding="utf-8"))["libraries"]:
            text = text.replace(lib["url"], f"missing-{lib['global']}.js")       # a library that cannot be loaded
        offline.write_text(text, encoding="utf-8")
        dom = rendered_dom_after(offline, """
const out = document.documentElement.dataset;
agnosTrace.select("RQ-DEM-001");
agnosTrace.showView("graph");
const missing = document.querySelector("#view-graph .library-missing");
out.message = missing ? missing.textContent : "";
out.rows = String(document.querySelectorAll("#matrix-table tbody tr").length);
""")
        got = dict(re.findall(r'data-(message|rows)="([^"]*)"', dom))
        self.assertIn("Cytoscape.js could not be loaded", got.get("message", ""))
        self.assertGreater(int(got.get("rows", "0")), 0)

    def test_RQ_TRC_022_given_a_source_line_holding_a_script_end_when_embedded_then_it_cannot_close_the_data(self):
        import json
        block = data_block(self.page)
        self.assertNotIn("<", block)
        data = json.loads(block)
        texts = [line[1] for edge in data["edges"] for line in edge[3]]
        self.assertIn("// RQ-DEM-001 </script><img src=x onerror=alert(1)>", texts)

    def test_RQ_TRC_018_given_the_token_file_when_resolved_then_both_themes_are_written(self):
        css = tm.tokens_css(tm.load_tokens(tm.TOKENS_PATH))
        self.assertIn("--s-surface:", css)
        self.assertIn("--c-graph-node-size: var(--s-size-node);", css)
        self.assertIn("[data-theme=\"dark\"]", css)
        self.assertIn("prefers-color-scheme: dark", css)

    def test_RQ_TRC_018_given_an_unresolved_token_when_resolved_then_it_is_an_input_error(self):
        broken = {"global": {"color.a": "#000000"}, "semantic": {"text": {"light": "color.a", "dark": "color.b"}},
                  "component": {}}
        with self.assertRaises(tm.InputError):
            tm.tokens_css(broken)
        with self.assertRaises(tm.InputError):
            tm.tokens_css({"global": {"color.a": "#000000"}, "semantic": {"text": "color.a"},
                           "component": {"x": "nothing"}})

    def test_RQ_TRC_018_given_the_page_style_and_script_when_searched_then_they_hold_no_raw_visual_value(self):
        import re
        for name in ("matrix.css", "matrix.js", "matrix.html"):
            text = (SKILL / "assets" / name).read_text(encoding="utf-8")
            self.assertEqual([], re.findall(RAW_VISUAL_RE, text), name)

    def test_RQ_TRC_001_given_no_out_when_the_generator_runs_then_the_page_is_written_in_the_process_folder(self):
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            shutil.copytree(FIXTURE, repo)
            code, out, err = run_main(["--process", str(repo / "process"), "--sources", str(repo / "src"),
                                       "--generated-at", GENERATED_AT])
            self.assertEqual(0, code, err)
            self.assertTrue((repo / "process" / tm.DEFAULT_OUT_NAME).is_file())
            self.assertIn(tm.DEFAULT_OUT_NAME, out.strip().splitlines()[-1])


BROWSER_CANDIDATES = (
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
)
BROWSER_NAMES = ("chromium", "chromium-browser", "google-chrome", "chrome", "msedge", "microsoft-edge")
BROWSER_BUDGET_MS = "8000"
BROWSER_WINDOW = "1600,1000"


def find_browser():
    """A Chromium-family browser for the page tests: $AGNOS_PERF_CENTER_BROWSER, a usual install path or one on the PATH."""
    import os
    import shutil
    if os.environ.get("AGNOS_PERF_CENTER_BROWSER"):
        return os.environ["AGNOS_PERF_CENTER_BROWSER"]
    found = [p for p in BROWSER_CANDIDATES if Path(p).is_file()] + [shutil.which(n) for n in BROWSER_NAMES]
    return next((p for p in found if p), None)


CDN_PROBE = "https://cdnjs.cloudflare.com/ajax/libs/echarts/6.1.0/echarts.min.js"   # a file the page loads: the site's root may redirect endlessly
CDN_TIMEOUT_S = 5


def cdn_reachable():
    """True when cdnjs answers: the page loads its libraries from it (RQ-TRC-080)."""
    import urllib.request
    try:
        urllib.request.urlopen(urllib.request.Request(CDN_PROBE, method="HEAD"), timeout=CDN_TIMEOUT_S).close()
        return True
    except OSError:
        return False


# RQ-TRC-081, DEC-TRC-041: the page tests need the libraries from cdnjs; offline, they are skipped, never failed.
BROWSER_FOUND = find_browser()
ONLINE = bool(BROWSER_FOUND) and cdn_reachable()
BROWSER = BROWSER_FOUND if ONLINE else None
if BROWSER_FOUND and not ONLINE:
    import sys as _sys
    print("agnos-perf-center tests: cdnjs unreachable, the page tests are skipped (they need the network)", file=_sys.stderr)


COMPAT_LAYER_VAR = "__COMPAT_LAYER"   # Windows application-compatibility shim, inherited from some parent shells


def browser_env():
    """TASK-TRC-106 (RQ-TRC-081 page tests): os.environ without the Windows compatibility shim.

    Under __COMPAT_LAYER, Edge exits 0 with an empty --dump-dom."""
    import os
    return {name: value for name, value in os.environ.items() if name.upper() != COMPAT_LAYER_VAR}


def rendered_dom(page_path, fragment="", window=BROWSER_WINDOW):
    """The DOM of the page once its script ran, from a headless browser (--dump-dom) in a window of the given size.

    TASK-TRC-106 (RQ-TRC-081 page tests): launched with browser_env()."""
    import subprocess
    with tempfile.TemporaryDirectory() as profile:
        done = subprocess.run([BROWSER_FOUND, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                               f"--user-data-dir={profile}", f"--virtual-time-budget={BROWSER_BUDGET_MS}",
                               f"--window-size={window}", "--dump-dom",
                               page_path.resolve().as_uri() + fragment], capture_output=True, timeout=120, check=False,
                              env=browser_env())
    return done.stdout.decode("utf-8", errors="replace")


@unittest.skipUnless(BROWSER, "no Chromium-family browser found (set AGNOS_PERF_CENTER_BROWSER)")
class PageViewsTest(unittest.TestCase):
    """TASK-TRC-005: RQ-TRC-011, RQ-TRC-013 to RQ-TRC-016, RQ-TRC-022 (DEC-TRC-005, DEC-TRC-007), in a real browser."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "page.html"
        generate(cls.path)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_RQ_TRC_016_given_a_fragment_when_the_page_opens_then_the_detail_shows_the_element_links_by_type(self):
        dom = rendered_dom(self.path, "#RQ-DEM-002")
        self.assertIn('data-ready="true"', dom)
        self.assertIn('<h2 class="detail-id">RQ-DEM-002</h2>', dom)
        for summary in ("Feature 1", "Requirement 1", "Tasks 2"):
            self.assertIn(summary, dom)
        for linked in ("TASK-DEM-001", "TASK-DEM-002", "FTR-DEM-001", "RQ-DEM-001"):
            self.assertIn(f'<span class="id">{linked}</span>', dom)
        import re
        self.assertEqual([], re.findall(r">\s*(?:null|undefined)\s*<", dom))

    # TASK-TRC-108: RQ-TRC-121 (DEC-TRC-066), the view named in the fragment
    TAB_TAG = re.compile(r'<button class="tab"[^>]*>')
    VIEW_OF_TAB = re.compile(r'data-view="([\w-]+)"')

    def opened_view(self, dom):
        """The data-view of the selected tab, and whether its section is shown. RQ-TRC-121"""
        selected = [self.VIEW_OF_TAB.search(tag).group(1) for tag in self.TAB_TAG.findall(dom) if 'aria-selected="true"' in tag]
        self.assertEqual(1, len(selected), selected)
        section = re.search(rf'<section class="view[^"]*" id="view-{selected[0]}"[^>]*>', dom).group(0)
        return selected[0], " hidden" not in section

    def test_RQ_TRC_121_given_view_matrix_in_the_fragment_when_the_page_opens_then_the_matrix_is_shown(self):
        dom = rendered_dom(self.path, "#view=matrix")
        self.assertIn('data-ready="true"', dom)
        self.assertEqual(("matrix", True), self.opened_view(dom))

    def test_RQ_TRC_121_given_each_shown_tab_when_its_view_is_in_the_fragment_then_it_opens(self):
        shown = [self.VIEW_OF_TAB.search(tag).group(1) for tag in self.TAB_TAG.findall(rendered_dom(self.path)) if " hidden" not in tag]
        self.assertGreaterEqual(len(shown), 4, shown)
        for view in shown:
            with self.subTest(view=view):
                self.assertEqual((view, True), self.opened_view(rendered_dom(self.path, f"#view={view}")))

    def test_RQ_TRC_121_given_a_hidden_or_unknown_view_when_the_page_opens_then_the_overview_opens(self):
        for fragment in ("#view=history", "#view=unknown", "#view="):
            with self.subTest(fragment=fragment):
                self.assertEqual(("overview", True), self.opened_view(rendered_dom(self.path, fragment)))

    def test_RQ_TRC_015_given_the_fixture_when_the_page_opens_then_the_overview_shows_its_coverage(self):
        dom = rendered_dom(self.path)
        self.assertIn('<span class="kpi-value">20 %</span>', dom)
        self.assertIn("1 of 5 cited by a source file · 1 more indirectly", dom)

    def test_RQ_TRC_014_given_the_fixture_when_the_page_opens_then_the_matrix_has_a_row_per_requirement(self):
        dom = rendered_dom(self.path)
        self.assertEqual(5, dom.count('<tr data-key="RQ-DEM-') + dom.count('<tr class="selected" data-key="RQ-DEM-'))
        self.assertIn("5 of 5 requirements", dom)

    def test_RQ_TRC_022_given_a_source_line_holding_html_when_shown_then_it_is_text(self):
        dom = rendered_dom(self.path, "#RQ-DEM-001")
        self.assertIn("&lt;/script&gt;&lt;img src=x onerror=alert(1)&gt;", dom)
        self.assertNotIn("<img", dom)

    def test_RQ_TRC_022_given_the_page_script_when_searched_then_it_never_writes_html(self):
        script = (SKILL / "assets" / "matrix.js").read_text(encoding="utf-8")
        for needle in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write"):
            self.assertNotIn(needle, script)


def neighbourhood(model, start, depth):
    """The elements within `depth` links of `start`, links taken both ways (what the graph view draws)."""
    adjacent = {}
    for (src, dst, kind) in model.edges:
        a = "file:" + src if kind == "code" else src
        adjacent.setdefault(a, set()).add(dst)
        adjacent.setdefault(dst, set()).add(a)
    seen, frontier = {start}, {start}
    for _ in range(depth):
        frontier = {n for f in frontier for n in adjacent.get(f, ())} - seen
        seen |= frontier
    return seen


@unittest.skipUnless(BROWSER, "no Chromium-family browser found (set AGNOS_PERF_CENTER_BROWSER)")
class GraphViewTest(unittest.TestCase):
    """TASK-TRC-006: RQ-TRC-012, RQ-TRC-020 (DEC-TRC-006, DEC-TRC-007), in a real browser."""

    def test_RQ_TRC_012_given_a_selected_requirement_when_the_graph_opens_then_it_draws_its_direct_links(self):
        import re
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "page.html"
            generate(path)
            dom = rendered_dom(path, "#RQ-DEM-002")
        expected = neighbourhood(scanned_model(), "RQ-DEM-002", 1)   # depth 1 is the default
        self.assertEqual({"RQ-DEM-002", "FTR-DEM-001", "TASK-DEM-001", "TASK-DEM-002", "RQ-DEM-001"}, expected)
        attributes = dict(re.findall(r'data-graph-(\w+)="([^"]*)"', dom))
        self.assertEqual("RQ-DEM-002", attributes.get("selected"))
        self.assertEqual(str(len(expected)), attributes.get("nodes"))
        self.assertLess(int(attributes.get("ms", "99999")), 500)
        self.assertIn("<canvas", dom)


class GraphToolbarTest(unittest.TestCase):
    """TASK-TRC-099: RQ-TRC-012, RQ-TRC-045 (ADR-TRC-015, DEC-TRC-060)."""

    def test_RQ_TRC_012_given_the_page_then_whole_graph_is_removed_and_fit_remains(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "page.html"
            page, _ = generate(path)
        self.assertNotIn('id="whole"', page)
        self.assertNotIn("Whole graph", page)
        self.assertIn('id="fit"', page)


def rendered_dom_after(page_path, script, window=BROWSER_WINDOW):
    """The DOM once the page ran, then the given script (a copy of the page with the script at its end)."""
    copy = page_path.with_name("scripted-" + page_path.name)
    copy.write_text(page_path.read_text(encoding="utf-8").replace("</body>", f"<script>{script}</script></body>"),
                    encoding="utf-8")
    return rendered_dom(copy, window=window)


KEY_PRESSES = """
const press = (id, key, times) => { const bar = document.getElementById(id);
  for (let i = 0; i < times; i += 1) bar.dispatchEvent(new KeyboardEvent("keydown", { key, bubbles: true })); };
press("split-left", "ArrowRight", 3);
press("split-right", "ArrowLeft", 50);
"""


@unittest.skipUnless(BROWSER, "no Chromium-family browser found (set AGNOS_PERF_CENTER_BROWSER)")
class SplitterTest(unittest.TestCase):
    """TASK-TRC-008: RQ-TRC-025, RQ-TRC-018 (DEC-TRC-012)."""

    def test_RQ_TRC_025_given_the_splitters_when_moved_by_keyboard_then_widths_change_by_steps_and_stop_at_the_maximum(
            self):
        import re
        tokens = tm.load_tokens(tm.TOKENS_PATH)["global"]
        px = lambda name: int(tokens[name].removesuffix("px"))  # noqa: E731
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "page.html"
            generate(path)
            before = dict(re.findall(r'data-(sidebar|detail)-width="(\d+)"', rendered_dom(path)))
            after = dict(re.findall(r'data-(sidebar|detail)-width="(\d+)"', rendered_dom_after(path, KEY_PRESSES)))
        self.assertEqual({"sidebar": str(px("dimension.sidebar")), "detail": str(px("dimension.detail"))}, before)
        self.assertEqual(str(px("dimension.sidebar") + 3 * px("space.16")), after["sidebar"])
        self.assertEqual(str(px("dimension.detail-max")), after["detail"])

    def test_RQ_TRC_025_given_the_page_when_opened_then_the_two_bars_are_focusable_separators(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "page.html"
            generate(path)
            dom = rendered_dom(path)
        for bar in ("split-left", "split-right"):
            self.assertRegex(dom, rf'<div[^>]*id="{bar}"[^>]*role="separator"[^>]*tabindex="0"|'
                                  rf'<div[^>]*role="separator"[^>]*id="{bar}"')


NARROW_AND_MEASURE = """
const press = (id, key, times) => { const bar = document.getElementById(id);
  for (let i = 0; i < times; i += 1) bar.dispatchEvent(new KeyboardEvent("keydown", { key, bubbles: true })); };
press("split-left", "ArrowRight", 50);
press("split-right", "ArrowLeft", 50);
const out = document.documentElement.dataset;
agnosTrace.showView("matrix");
const table = document.querySelector(".table-frame");
out.matrixScrolls = String(table.scrollWidth > table.clientWidth);
out.matrixWidth = String(document.getElementById("matrix-table").offsetWidth);
agnosTrace.select("RQ-DEM-002");
document.querySelector('#depth button[data-depth="3"]').click();
agnosTrace.showView("graph");
const scroller = document.getElementById("graph-scroll");
out.graphScrolls = String(scroller.scrollWidth > scroller.clientWidth);
"""


@unittest.skipUnless(BROWSER, "no Chromium-family browser found (set AGNOS_PERF_CENTER_BROWSER)")
class ScrollTest(unittest.TestCase):
    """TASK-TRC-016: RQ-TRC-042, RQ-TRC-018 (DEC-TRC-006, DEC-TRC-012)."""

    def test_RQ_TRC_042_given_narrow_central_views_then_matrix_and_graph_scroll_at_their_minimum_width_and_zoom(self):
        import re
        tokens = tm.load_tokens(tm.TOKENS_PATH)["global"]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "page.html"
            generate(path)
            dom = rendered_dom_after(path, NARROW_AND_MEASURE)
        found = dict(re.findall(r'data-(matrix-scrolls|matrix-width|graph-scrolls|graph-zoom)="([^"]*)"', dom))
        self.assertEqual("true", found.get("matrix-scrolls"))
        self.assertGreaterEqual(int(found["matrix-width"]), int(tokens["dimension.matrix-min"].removesuffix("px")))
        self.assertEqual("true", found.get("graph-scrolls"))
        self.assertGreaterEqual(float(found["graph-zoom"]), float(tokens["dimension.graph-flow-min-zoom"]))


RESIZE_FIRST_COLUMN = """
agnosTrace.showView("matrix");
const heads = () => [...document.querySelectorAll("#matrix-table th")];
const out = document.documentElement.dataset;
out.before = heads().slice(0, 2).map((th) => th.offsetWidth).join(",");
const grip = heads()[0].querySelector(".col-grip");
for (let i = 0; i < 3; i += 1) grip.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowRight", bubbles: true }));
grip.click();
out.after = heads().slice(0, 2).map((th) => th.offsetWidth).join(",");
out.sort = document.querySelector('#matrix-table th[data-column="id"]').getAttribute("aria-sort");   // RQ-TRC-051: Feature leads
heads()[0].querySelector(".col-grip").dispatchEvent(new MouseEvent("dblclick", { bubbles: true }));
out.reset = heads().slice(0, 2).map((th) => th.offsetWidth).join(",");
"""


@unittest.skipUnless(BROWSER, "no Chromium-family browser found (set AGNOS_PERF_CENTER_BROWSER)")
class ColumnResizeTest(unittest.TestCase):
    """TASK-TRC-018: RQ-TRC-043, RQ-TRC-018 (DEC-TRC-012)."""

    def test_RQ_TRC_043_given_a_column_grip_when_moved_by_keyboard_then_only_that_column_widens_and_reset_restores(self):
        import re
        step = int(tm.load_tokens(tm.TOKENS_PATH)["global"]["space.16"].removesuffix("px"))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "page.html"
            generate(path)
            found = dict(re.findall(r'data-(before|after|sort|reset)="([^"]*)"', rendered_dom_after(path, RESIZE_FIRST_COLUMN)))
        before = [int(w) for w in found["before"].split(",")]
        after = [int(w) for w in found["after"].split(",")]
        self.assertEqual(before[0] + 3 * step, after[0])
        self.assertEqual(before[1], after[1])
        self.assertEqual("ascending", found["sort"])
        self.assertEqual(found["before"], found["reset"])


MOVE_COLUMNS = """
agnosTrace.showView("matrix");
const heads = () => [...document.querySelectorAll("#matrix-table th")];
const head = (key) => document.querySelector(`#matrix-table th[data-column="${key}"]`);
const keys = () => heads().map((th) => th.dataset.column).join(",");
const out = document.documentElement.dataset;
const underOwnHeader = () => {
  const row = document.querySelector("#matrix-table tbody tr");
  const cell = (key) => row.children[heads().findIndex((th) => th.dataset.column === key)];
  return Boolean(cell("coverage").querySelector(".badge") && cell("id").classList.contains("cell-requirement"));
};
out.first = keys();
out.under0 = String(underOwnHeader());
const width = head("coverage").offsetWidth;
const alt = (key) => head("coverage").dispatchEvent(new KeyboardEvent("keydown", { key, altKey: true, bubbles: true }));
alt("ArrowLeft");
alt("ArrowLeft");
alt("ArrowLeft");                                    // already first: stays
out.keyed = keys();
out.under1 = String(underOwnHeader());
out.sort = head("id").getAttribute("aria-sort");
out.width = String(head("coverage").offsetWidth === width);
out.stored = localStorage.getItem("agnos-perf-center-column-order") || "";
const transfer = new DataTransfer();
head("id").dispatchEvent(new DragEvent("dragstart", { dataTransfer: transfer, bubbles: true }));
head("coverage").dispatchEvent(new DragEvent("dragover", { dataTransfer: transfer, bubbles: true, cancelable: true }));
head("coverage").dispatchEvent(new DragEvent("drop", { dataTransfer: transfer, bubbles: true, cancelable: true }));
out.dragged = keys();
out.under2 = String(underOwnHeader());
document.getElementById("reset-columns").click();
out.reset = keys();
out.storedAfter = localStorage.getItem("agnos-perf-center-column-order") || "";
"""


@unittest.skipUnless(BROWSER, "no Chromium-family browser found (set AGNOS_PERF_CENTER_BROWSER)")
class ColumnOrderTest(unittest.TestCase):
    """TASK-TRC-039, TASK-TRC-040: RQ-TRC-051, RQ-TRC-052 (DEC-TRC-027, DEC-TRC-028)."""

    def test_RQ_TRC_051_RQ_TRC_052_given_the_matrix_when_columns_are_moved_then_cells_follow_and_reset_restores(self):
        import re
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "page.html"
            generate(path)
            found = dict(re.findall(r'data-(first|under\d|keyed|sort|width|stored|dragged|reset|stored-after)="([^"]*)"',
                                    rendered_dom_after(path, MOVE_COLUMNS)))
        default = "feature,id,coverage,decisions,tasks,files,lines"
        self.assertEqual(default, found["first"])                       # RQ-TRC-051: Feature leads
        self.assertEqual("true", found["under0"])
        self.assertEqual("coverage,feature,id,decisions,tasks,files,lines", found["keyed"])   # Alt+Left, twice
        self.assertEqual("true", found["under1"])
        self.assertEqual("ascending", found["sort"])                    # a move leaves the sort alone
        self.assertEqual("true", found["width"])                        # and the widths
        self.assertEqual("coverage,feature,id,decisions,tasks,files,lines", found["stored"].replace("&quot;", "").strip("[]"))
        self.assertEqual("id,coverage,feature,decisions,tasks,files,lines", found["dragged"])   # dropped on Coverage
        self.assertEqual("true", found["under2"])
        self.assertEqual(default, found["reset"])
        self.assertEqual("", found["stored-after"])


FEATURE_TITLE = """
agnosTrace.showView("matrix");
const heads = [...document.querySelectorAll("#matrix-table th")];
const row = document.querySelector('#matrix-table tbody tr[data-key="RQ-DEM-001"]');
const cell = row.children[heads.findIndex((th) => th.dataset.column === "feature")];
document.documentElement.dataset.featureId = cell.querySelector(".id")?.textContent || "";
document.documentElement.dataset.featureTitle = cell.querySelector(".cell-title")?.textContent || "";
"""


@unittest.skipUnless(BROWSER, "no Chromium-family browser found (set AGNOS_PERF_CENTER_BROWSER)")
class FeatureTitleTest(unittest.TestCase):
    """TASK-TRC-041: RQ-TRC-053 (DEC-TRC-029)."""

    def test_RQ_TRC_053_given_the_matrix_then_a_feature_shows_its_title_under_its_id(self):
        import re
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "page.html"
            generate(path)
            found = dict(re.findall(r'data-(feature-id|feature-title)="([^"]*)"', rendered_dom_after(path, FEATURE_TITLE)))
        self.assertEqual("FTR-DEM-001", found["feature-id"])
        self.assertEqual("Demo Feature", found["feature-title"])


FIXED_BAND = """
agnosTrace.select("RQ-DEM-001");
const out = document.documentElement.dataset;
const detail = document.getElementById("detail");
const band = detail.querySelector(".detail-top");
const body = detail.querySelector(".detail-body");
body.style.maxHeight = "40px";                                      // a body shorter than its links, as a long list is
const topBefore = band.getBoundingClientRect().band;
out.overflows = String(body.scrollHeight > body.clientHeight);
body.scrollTop = body.scrollHeight;
out.scrolled = String(body.scrollTop > 0);
out.bandFixed = String(band.getBoundingClientRect().band === topBefore);
out.panelScrolls = getComputedStyle(detail).overflowY;
out.bodyScrolls = getComputedStyle(body).overflowY;
const size = (node) => Number.parseFloat(getComputedStyle(node).fontSize);
out.titleLarger = String(size(band.querySelector(".detail-title")) > size(body.querySelector(".link-rel")));
out.barColour = String(getComputedStyle(band).borderLeftColor === getComputedStyle(band.querySelector(".detail-kind .dot")).backgroundColor);
out.barWidth = String(Number.parseFloat(getComputedStyle(band).borderLeftWidth) > 0);
"""


@unittest.skipUnless(BROWSER, "no Chromium-family browser found (set AGNOS_PERF_CENTER_BROWSER)")
class DetailBandTest(unittest.TestCase):
    """TASK-TRC-042: RQ-TRC-054 (DEC-TRC-030)."""

    def test_RQ_TRC_054_given_a_selection_when_the_links_scroll_then_the_band_stays_and_stands_out(self):
        import re
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "page.html"
            generate(path)
            found = dict(re.findall(r'data-(overflows|scrolled|band-fixed|panel-scrolls|body-scrolls|title-larger|bar-colour|bar-width)="([^"]*)"',
                                    rendered_dom_after(path, FIXED_BAND)))
        self.assertEqual("true", found["overflows"])
        self.assertEqual("true", found["scrolled"])
        self.assertEqual("true", found["band-fixed"])                 # the links scroll under the band
        self.assertEqual("hidden", found["panel-scrolls"])            # only the body scrolls
        self.assertEqual("auto", found["body-scrolls"])
        self.assertEqual("true", found["title-larger"])
        self.assertEqual("true", found["bar-colour"])                 # the bar is in the element's type colour
        self.assertEqual("true", found["bar-width"])


TAG_FILTER = """
const out = document.documentElement.dataset;
agnosTrace.select("RQ-DEM-001");
const tags = () => [...document.querySelectorAll("#detail .detail-summary [data-group]")];
const shown = () => [...document.querySelectorAll("#detail .detail-body .group")].filter((g) => !g.hidden).map((g) => g.dataset.group).join(",");
out.all = shown();
out.tags = tags().map((t) => t.dataset.group).join(",");
const first = tags()[0];
const second = tags()[1];
first.click();
out.one = shown();
out.firstPressed = first.getAttribute("aria-pressed");
second.click();
out.two = shown();
first.click();
second.click();
out.again = shown();
out.pressedAgain = String(tags().filter((t) => t.getAttribute("aria-pressed") === "true").length);
first.click();
agnosTrace.select("RQ-DEM-002");
out.afterSelect = String(tags().filter((t) => t.getAttribute("aria-pressed") === "true").length);
out.allAfterSelect = String(shown().split(",").length === tags().length);
out.firstTitle = first.title;
"""


@unittest.skipUnless(BROWSER, "no Chromium-family browser found (set AGNOS_PERF_CENTER_BROWSER)")
class TagFilterTest(unittest.TestCase):
    """TASK-TRC-043: RQ-TRC-055, RQ-TRC-045 (DEC-TRC-030)."""

    def test_RQ_TRC_055_given_tags_when_clicked_then_only_their_groups_show_and_a_new_selection_clears_them(self):
        import re
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "page.html"
            generate(path)
            found = dict(re.findall(r'data-(all|tags|one|first-pressed|two|again|pressed-again|after-select|all-after-select|first-title)="([^"]*)"',
                                    rendered_dom_after(path, TAG_FILTER)))
        groups = found["all"].split(",")
        self.assertGreaterEqual(len(groups), 3)
        self.assertEqual(found["tags"].split(","), groups)             # a tag per group, in the same order
        self.assertEqual(groups[0], found["one"])
        self.assertEqual("true", found["first-pressed"])
        self.assertEqual(",".join(groups[:2]), found["two"])           # tags clicked together show their groups together
        self.assertEqual(found["all"], found["again"])
        self.assertEqual("0", found["pressed-again"])
        self.assertEqual("0", found["after-select"])                   # a new selection drops the filter
        self.assertEqual("true", found["all-after-select"])
        self.assertTrue(found["first-title"].strip())                  # RQ-TRC-045


WHEEL_ONE_NOTCH = """
const out = document.documentElement.dataset;
agnosTrace.select("RQ-DEM-001");
agnosTrace.showView("graph");
const frame = document.getElementById("cy");
const before = agnosTrace.graph.zoom();
frame.dispatchEvent(new WheelEvent("wheel", { deltaY: -100, clientX: 400, clientY: 300, bubbles: true, cancelable: true }));
out.ratio = String(agnosTrace.graph.zoom() / before);
out.wheel = String(agnosTrace.graph.wheelSensitivity());
"""


@unittest.skipUnless(BROWSER, "no Chromium-family browser found (set AGNOS_PERF_CENTER_BROWSER)")
class WheelZoomTest(unittest.TestCase):
    """TASK-TRC-044: RQ-TRC-056 (DEC-TRC-031)."""

    def test_RQ_TRC_056_given_the_tokens_then_the_wheel_sensitivity_is_a_token_of_0_1(self):
        tokens = tm.load_tokens(tm.TOKENS_PATH)
        self.assertEqual("0.1", tokens["global"]["dimension.graph-wheel-sensitivity"])
        self.assertIn("graph-wheel-sensitivity", tokens["component"])

    def test_RQ_TRC_056_given_the_graph_when_the_wheel_turns_one_notch_then_the_zoom_changes_by_about_ten_percent(self):
        import re
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "page.html"
            generate(path)
            found = dict(re.findall(r'data-(ratio|wheel)="([^"]*)"', rendered_dom_after(path, WHEEL_ONE_NOTCH)))
        self.assertEqual(0.1, float(found["wheel"]))
        ratio = float(found["ratio"])
        self.assertGreater(ratio, 1.0)                                  # the notch zooms in
        self.assertLess(ratio, 1.2)                                     # the library's default would give 2.5


TOOLTIP_TARGETS = (".tab", "#type-filters .chip", "#tri-filters .chip", ".quality-shortcut", "#depth", "#depth button",
                   "#display", "#show-files", "#show-hierarchy", "#fit", "#coverage-filter button", "#export-csv", "#reset-columns", "#expand-checks", "#collapse-checks",
                   "#matrix-table th", ".kpi-type", "#search")
READ_TOOLTIPS = """
agnosTrace.select("RQ-DEM-002");
const untitled = [];
for (const selector of %s) {
  const found = [...document.querySelectorAll(selector)];
  if (!found.length) untitled.push(selector + " (none)");
  for (const node of found) {
    const titled = node.title || node.closest("label")?.title || node.dataset.richTip;   // DEC-HST-007: or a rich tooltip
    if (!titled) untitled.push(selector);
  }
}
for (const button of document.querySelectorAll(".detail-actions button")) if (!button.title) untitled.push("detail button");
document.documentElement.dataset.untitled = [...new Set(untitled)].join(",");
"""


@unittest.skipUnless(BROWSER, "no Chromium-family browser found (set AGNOS_PERF_CENTER_BROWSER)")
class TooltipTest(unittest.TestCase):
    """TASK-TRC-019: RQ-TRC-045."""

    def test_RQ_TRC_045_given_the_page_then_every_control_has_an_explanatory_tooltip(self):
        import json
        import re
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "page.html"
            generate(path)
            dom = rendered_dom_after(path, READ_TOOLTIPS % json.dumps(list(TOOLTIP_TARGETS)))
        self.assertEqual("", re.search(r'data-untitled="([^"]*)"', dom).group(1))


SEARCH_FOR_COVERED = ("const s = document.getElementById('search'); s.value = 'covered';"
                      "s.dispatchEvent(new Event('input'));"
                      "const first = document.querySelector('#search-results .search-result');")
READ_SEARCH_TIP = """
const tip = document.getElementById("tip");          // the page's one rich tooltip (DEC-HST-007)
document.documentElement.dataset.tipHidden = String(!tip || tip.hidden);
document.documentElement.dataset.tipText = tip ? tip.textContent : "";
document.documentElement.dataset.tipSelected = document.querySelector('#search-results [aria-selected="true"]')?.textContent || "";
"""


@unittest.skipUnless(BROWSER, "no Chromium-family browser found (set AGNOS_PERF_CENTER_BROWSER)")
class SearchTooltipTest(unittest.TestCase):
    """TASK-TRC-030: RQ-TRC-049 (DEC-TRC-024), in a real browser."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "page.html"
        generate(cls.path)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def tip_after(self, script):
        import html
        import re
        dom = rendered_dom_after(self.path, SEARCH_FOR_COVERED + script + f"setTimeout(() => {{ {READ_SEARCH_TIP} }}, 1000);")
        found = dict(re.findall(r'data-(tip-hidden|tip-text)="([^"]*)"', dom))
        return found["tip-hidden"], html.unescape(found["tip-text"])

    def test_RQ_TRC_049_given_a_result_pointed_at_when_the_delay_has_passed_then_the_tooltip_shows_its_whole_text(self):
        hidden, text = self.tip_after("first.dispatchEvent(new MouseEvent('mouseenter'));")
        self.assertEqual("false", hidden)
        self.assertIn("RQ-DEM-001", text)
        self.assertIn("Covered directly", text)
        self.assertRegex(text, r"\.md:\d+-\d+")                                   # its location

    def test_RQ_TRC_049_given_the_pointer_leaving_the_list_then_the_tooltip_is_hidden(self):
        hidden, _ = self.tip_after("first.dispatchEvent(new MouseEvent('mouseenter'));"          # shown at 300 ms, gone at 500
                                   "setTimeout(() => document.getElementById('search-results')"
                                   ".dispatchEvent(new MouseEvent('mouseleave')), 500);")
        self.assertEqual("true", hidden)

    def test_RQ_TRC_049_given_the_keyboard_moving_onto_a_result_then_its_tooltip_shows(self):
        hidden, text = self.tip_after("document.getElementById('search').dispatchEvent("
                                      "new KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true }));")
        self.assertEqual("false", hidden)
        self.assertTrue(text.strip())

    def test_RQ_TRC_049_given_the_tokens_then_the_delay_is_300_ms_and_the_tooltip_has_its_own_tokens(self):
        tokens = tm.load_tokens(tm.TOKENS_PATH)
        self.assertEqual("300ms", tokens["global"]["duration.quick"])
        for name in ("search-tip-delay", "group-label-bg", "group-label-text"):
            self.assertIn(name, tokens["component"])


HOST_TERMS_B64 = ("YWthaQ==", "czUwMDA=", "czYwMDA=", "c3lzZXg=", "anVjZQ==", "eHM1Nms=", "c2FtcGxlcg==", "a2V5Z3JvdXA=",
                  "eHBsb3Jlcg==")   # the host project's names and domain terms, encoded so that this file holds none


class IndependenceTest(unittest.TestCase):
    """TASK-TRC-007: RQ-TRC-019, RQ-TRC-021 (DEC-TRC-001)."""

    def test_RQ_TRC_019_given_the_skill_folder_when_scanned_then_it_names_nothing_of_the_host_project(self):
        import base64
        terms = [base64.b64decode(t).decode() for t in HOST_TERMS_B64]
        found = []
        for path in SKILL.rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts:
                text = path.read_text(encoding="utf-8", errors="replace").lower()
                found += [f"{path.relative_to(SKILL)}: {t}" for t in terms if t in text]
        self.assertEqual([], found)

    def test_RQ_TRC_021_given_the_generator_when_its_imports_are_read_then_they_are_all_standard_library(self):
        import ast
        siblings = {p.stem for p in (SKILL / "scripts").glob("*.py")}      # scorecard.py, beside the generator (ADR-TRC-008)
        for name in ("perf_center.py", "scorecard.py"):
            tree = ast.parse((SKILL / "scripts" / name).read_text(encoding="utf-8"))
            imported = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)
                        for alias in node.names}
            imported |= {node.module.split(".")[0] for node in ast.walk(tree)
                         if isinstance(node, ast.ImportFrom) and node.module}
            self.assertEqual(set(), imported - set(sys.stdlib_module_names) - siblings, name)


class OnDemandGraphTest(unittest.TestCase):
    """TASK-TRC-119: RQ-TRC-132 (DEC-TRC-076): the generator runs agnos-graph when the graph is absent or --rebuild."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="agnos-perf-center-"))
        self.addCleanup(__import__("shutil").rmtree, self.tmp, ignore_errors=True)
        self.process = self.tmp / "process"
        __import__("shutil").copytree(PROCESS, self.process)
        self.graph = self.process / agnos_layout.GRAPH_FILE
        self.out = self.tmp / "page.html"

    def generator(self, *extra, sources=True, date=GENERATED_AT):
        args = ["--process", str(self.process), "--out", str(self.out), "--generated-at", date, *extra]
        if sources:
            args += ["--sources", str(SOURCES)]
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = tm.main(args)
        return code, out.getvalue(), err.getvalue()

    def test_RQ_TRC_132_given_no_graph_file_when_run_with_sources_then_the_graph_is_built_and_the_page_written(self):
        code, stdout, err = self.generator()
        self.assertEqual(0, code, err)
        self.assertTrue(self.graph.is_file())
        self.assertTrue(self.out.is_file())
        self.assertRegex(stdout.strip().splitlines()[-1], r"^agnos-perf-center: \d+ elements")

    def test_RQ_TRC_142_given_a_graph_in_the_graph_folder_when_run_without_graph_then_it_is_read_not_rebuilt(self):
        """TASK-TRC-131: RQ-TRC-142 (DEC-TRC-086): Given the graph in 4.knowledge/graph/, When run without --graph nor
        --rebuild, Then that graph is read And not rewritten."""
        self.assertEqual(0, self.generator()[0])
        graph = self.process / GRAPH_FOLDER_FILE
        self.assertTrue(graph.is_file())
        before = graph.read_bytes()
        code, _, err = self.generator(date="2026-02-02T00:00Z")
        self.assertEqual(0, code, err)
        self.assertEqual(before, graph.read_bytes())

    def test_RQ_TRC_144_given_no_graph_when_the_perf_center_builds_it_then_no_explorer_file_is_written(self):
        """TASK-TRC-133: RQ-TRC-144 (DEC-TRC-085): Given no graph, When the perf center builds it, Then its folder holds the
        graph file alone."""
        self.assertEqual(0, self.generator()[0])
        self.assertEqual([self.graph.name], sorted(p.name for p in self.graph.parent.iterdir()))

    def test_RQ_TRC_132_given_options_of_the_scan_when_the_graph_is_built_then_they_reach_it(self):
        code, _, err = self.generator("--ext", ".py", "--exclude", "dist")
        self.assertEqual(0, code, err)
        meta = __import__("json").loads(self.graph.read_text(encoding="utf-8"))["meta"]
        self.assertEqual(([".py"], ["dist"]), (meta["extensions"], meta["excludes"]))

    def test_RQ_TRC_132_given_an_existing_graph_when_run_without_rebuild_then_the_graph_is_not_rewritten(self):
        self.assertEqual(0, self.generator()[0])
        before = self.graph.read_bytes()
        code, _, err = self.generator(date="2026-02-02T00:00Z")
        self.assertEqual(0, code, err)
        self.assertEqual(before, self.graph.read_bytes())

    def test_RQ_TRC_132_given_rebuild_then_the_graph_is_rewritten(self):
        self.assertEqual(0, self.generator()[0])
        before = self.graph.read_bytes()
        code, _, err = self.generator("--rebuild", date="2026-02-02T00:00Z")
        self.assertEqual(0, code, err)
        self.assertNotEqual(before, self.graph.read_bytes())

    def test_RQ_TRC_132_given_no_graph_and_no_sources_then_it_exits_1_and_writes_nothing(self):
        code, _, err = self.generator(sources=False)
        self.assertEqual(1, code)
        self.assertIn("--sources", err)
        self.assertFalse(self.graph.exists())
        self.assertFalse(self.out.exists())

    def test_RQ_TRC_132_given_a_graph_build_that_fails_then_it_exits_1_and_writes_no_page(self):
        code, _, err = self.generator("--sources", str(self.tmp / "absent"))
        self.assertEqual(1, code)
        self.assertIn("source folder not found", err)
        self.assertFalse(self.out.exists())


class GraphInputTest(unittest.TestCase):
    """TASK-TRC-118: RQ-TRC-131 (DEC-TRC-075): the page is made from the graph file alone."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="agnos-perf-center-"))
        self.addCleanup(__import__("shutil").rmtree, self.tmp, ignore_errors=True)
        self.graph = self.tmp / "agnos-graph.json"
        self.out = self.tmp / "page.html"

    def build_graph(self, *extra):
        code, _, err = gr_run(["--process", str(PROCESS), "--sources", str(SOURCES), "--out", str(self.graph),
                               "--generated-at", GENERATED_AT, *extra])
        self.assertEqual(0, code, err)

    def page(self, graph=None):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = tm.main(["--process", str(PROCESS), "--graph", str(graph or self.graph), "--out", str(self.out),
                            "--generated-at", GENERATED_AT])
        return code, out.getvalue(), err.getvalue()

    def test_RQ_TRC_131_given_a_graph_when_the_page_is_made_from_it_then_its_data_is_the_single_generator_s(self):
        self.build_graph()
        code, stdout, err = self.page()
        self.assertEqual(0, code, err)
        page, _ = generate(self.tmp / "same.html")
        self.assertEqual(data_block(page), data_block(self.out))
        self.assertRegex(stdout.strip().splitlines()[-1], r"^agnos-perf-center: \d+ elements")

    def test_RQ_TRC_131_given_a_graph_without_call_graph_then_the_page_has_none_and_the_run_exits_0(self):
        self.build_graph()
        code, _, err = self.page()
        self.assertEqual(0, code, err)
        self.assertNotIn("callGraph", __import__("json").loads(data_block(self.out)))

    def test_RQ_TRC_131_given_a_file_that_is_not_json_then_it_exits_1_naming_the_file(self):
        self.graph.write_text("{not json", encoding="utf-8")
        code, _, err = self.page()
        self.assertEqual(1, code)
        self.assertIn(self.graph.as_posix(), err)
        self.assertFalse(self.out.exists())

    def test_RQ_TRC_131_given_a_graph_without_elements_then_it_exits_1_naming_the_file(self):
        self.graph.write_text('{"meta": {}}', encoding="utf-8")
        code, _, err = self.page()
        self.assertEqual(1, code)
        self.assertIn(self.graph.as_posix(), err)
        self.assertFalse(self.out.exists())

    def test_RQ_TRC_131_given_no_graph_file_then_it_exits_1_naming_the_file(self):
        code, _, err = self.page()
        self.assertEqual(1, code)
        self.assertIn(self.graph.as_posix(), err)
        self.assertFalse(self.out.exists())


def gr_run(args):
    """Runs the graph script's entry point; returns (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = gr.main(args)
    return code, out.getvalue(), err.getvalue()


if __name__ == "__main__":
    unittest.main()


GENERATED_SCRIPT = """
const out = document.documentElement.dataset;
const item = [...document.querySelectorAll("#meta .meta-item")].find((i) => i.textContent.startsWith("Generated"));
out.shown = item.querySelector(".meta-value").textContent;
out.expected = new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date("2026-01-01T00:00Z"));
item.dispatchEvent(new FocusEvent("focus"));
item.dispatchEvent(new MouseEvent("mouseover", { bubbles: true }));
out.exact = document.getElementById("tip").textContent;
"""


@unittest.skipUnless(BROWSER, "no Chromium-family browser found (set AGNOS_PERF_CENTER_BROWSER)")
class GeneratedDateTest(unittest.TestCase):
    """TASK-TRC-079: RQ-TRC-015 (the header's generation time, readable)."""

    def test_RQ_TRC_015_given_a_generation_time_then_the_header_shows_it_in_the_readers_words_and_the_tip_in_utc(self):
        import re
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "page.html"
            generate(path)
            found = dict(re.findall(r'data-(shown|expected|exact)="([^"]*)"', rendered_dom_after(path, GENERATED_SCRIPT)))
        self.assertEqual(found["expected"], found["shown"])               # the reader's date and time, no T nor Z
        self.assertIn("2026-01-01 00:00 UTC", found["exact"])


