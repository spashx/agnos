"""Tests of the agnos-trace generator (FTR-TRC-001), on the synthetic process of tests/fixtures/repo.

Run from the repository root: python -m unittest discover -s .github/skills/agnos-trace/tests -v
"""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import trace_matrix as tm  # noqa: E402

FIXTURE = HERE / "fixtures" / "repo"
PROCESS = FIXTURE / "process"
SOURCES = FIXTURE / "src"


def run_main(args):
    """Runs the generator's entry point; returns (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = tm.main(args)
    return code, out.getvalue(), err.getvalue()


class ProcessModelTest(unittest.TestCase):
    """TASK-TRC-001: RQ-TRC-001 to RQ-TRC-005, RQ-TRC-007 (DEC-TRC-002, DEC-TRC-003)."""

    @classmethod
    def setUpClass(cls):
        cls.model = tm.build_process_model(PROCESS)

    def refs(self, src):
        return sorted(dst for (s, dst, kind) in self.model.edges if s == src and kind == "refs")

    def children(self, parent):
        return sorted(dst for (s, dst, kind) in self.model.edges if s == parent and kind == "contains")

    def test_RQ_TRC_003_given_the_fixture_index_when_the_model_is_built_then_every_row_is_an_element(self):
        defined = [e for e in self.model.elements.values() if e["kind"] == "element"]
        self.assertEqual(15, len(defined))
        rq = self.model.elements["RQ-DEM-002"]
        self.assertEqual(("RQ", "DEM", "process/1.requirements/FTR-DEM-001-demo-feature.md", 13, 17, "Covered indirectly"),
                         (rq["type"], rq["tri"], rq["doc"], rq["first"], rq["last"], rq["title"]))
        self.assertEqual("In Progress", self.model.elements["TASK-DEM-002"]["status"])

    def test_RQ_TRC_004_given_nested_ranges_when_the_model_is_built_then_each_parent_contains_its_children(self):
        self.assertEqual([f"RQ-DEM-00{i}" for i in range(1, 6)], self.children("FTR-DEM-001"))
        self.assertEqual(["DEC-DEM-001"], self.children("ADR-DEM-001"))
        self.assertEqual(["TASK-DEM-001", "TASK-DEM-002", "TASK-DEM-003"], self.children("PLAN-DEM-001"))
        self.assertEqual([], self.children("FTR-DEM-002"))

    def test_RQ_TRC_005_given_a_task_citing_a_range_when_the_model_is_built_then_the_range_is_expanded(self):
        self.assertEqual(["ADR-DEM-001", "RQ-DEM-001", "RQ-DEM-002", "RQ-DEM-003"], self.refs("TASK-DEM-001"))

    def test_RQ_TRC_005_given_a_plan_when_the_model_is_built_then_it_has_only_the_references_of_its_own_lines(self):
        self.assertEqual(["ADR-DEM-001"], self.refs("PLAN-DEM-001"))

    def test_RQ_TRC_005_given_a_reference_when_the_model_is_built_then_its_lines_are_kept(self):
        lines = self.model.edges[("DEC-DEM-001", "RQ-DEM-004", "refs")]
        self.assertEqual([[12, "This decision serves RQ-DEM-004."]], lines)

    def test_RQ_TRC_005_given_range_notations_when_expanded_then_only_defined_ids_of_one_prefix_count(self):
        defined = {"RQ-DEM-001", "RQ-DEM-002", "RQ-DEM-003", "TASK-DEM-001"}
        expand = lambda text: sorted(tm.extract_ids(text, defined))  # noqa: E731
        self.assertEqual(["RQ-DEM-001", "RQ-DEM-002", "RQ-DEM-003"], expand("RQ-DEM-001–RQ-DEM-003"))
        self.assertEqual(["RQ-DEM-001", "RQ-DEM-002"], expand("RQ-DEM-001..RQ-DEM-002"))
        self.assertEqual(["RQ-DEM-001", "RQ-DEM-002", "RQ-DEM-003", "RQ-DEM-009"], expand("RQ-DEM-001 to RQ-DEM-009"))
        self.assertEqual(["RQ-DEM-001", "RQ-DEM-003"], expand("RQ-DEM-003 to RQ-DEM-001"))
        self.assertEqual(["RQ-DEM-001", "TASK-DEM-001"], expand("RQ-DEM-001 to TASK-DEM-001"))
        self.assertEqual([], expand("XRQ-DEM-001 RQ-DEM-0011 rq-dem-001"))

    def test_RQ_TRC_007_given_an_undefined_id_in_a_task_when_the_model_is_built_then_it_is_an_undefined_element(self):
        self.assertEqual(["DEC-DEM-099", "RQ-DEM-002"], self.refs("TASK-DEM-002"))
        self.assertEqual("undefined", self.model.elements["DEC-DEM-099"]["kind"])

    def test_RQ_TRC_002_given_no_index_when_the_generator_runs_then_it_exits_1_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "page.html"
            code, _, err = run_main(["--process", tmp, "--sources", str(SOURCES), "--out", str(out)])
            self.assertEqual(1, code)
            self.assertIn("INDEX.idx.md", err)
            self.assertFalse(out.exists())

    def test_RQ_TRC_002_given_a_missing_source_folder_when_the_generator_runs_then_it_exits_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "page.html"
            code, _, err = run_main(["--process", str(PROCESS), "--sources", str(Path(tmp) / "nope"), "--out", str(out)])
            self.assertEqual(1, code)
            self.assertIn("nope", err)
            self.assertFalse(out.exists())


def scanned_model(**options):
    """The fixture model with its sources scanned, file paths shown relative to the fixture repository."""
    model = tm.build_process_model(PROCESS)
    tm.scan_sources(model, [SOURCES], base=FIXTURE, **options)
    return model


def code_links(model, path):
    return {dst: lines for (src, dst, kind), lines in model.edges.items() if src == path and kind == "code"}


class SourceScannerTest(unittest.TestCase):
    """TASK-TRC-002: RQ-TRC-006, RQ-TRC-007 (DEC-TRC-001, DEC-TRC-003)."""

    @classmethod
    def setUpClass(cls):
        cls.model = scanned_model()

    def test_RQ_TRC_006_given_a_source_line_citing_an_id_when_scanned_then_the_file_links_to_it_with_the_line(self):
        self.assertEqual({"RQ-DEM-001": [[1, "# Implements RQ-DEM-001."]],
                          "RQ-DEM-099": [[5, '"""RQ-DEM-099 is not defined anywhere."""']]},
                         code_links(self.model, "src/a.py"))
        self.assertEqual(["TASK-DEM-002"], list(code_links(self.model, "src/lib/b.cpp")))

    def test_RQ_TRC_006_given_the_default_lists_when_scanned_then_excluded_folders_and_other_extensions_are_skipped(self):
        self.assertEqual(["src/a.py", "src/lib/b.cpp", "src/notrace.py", "src/xss.js"], sorted(self.model.files))

    def test_RQ_TRC_006_given_a_file_without_id_when_scanned_then_it_is_kept_with_no_link(self):
        self.assertEqual({}, code_links(self.model, "src/notrace.py"))
        self.assertEqual(0, self.model.files["src/notrace.py"]["ids"])

    def test_RQ_TRC_006_given_other_extensions_and_exclusions_when_scanned_then_they_replace_the_defaults(self):
        model = scanned_model(extensions={".bin", ".py"}, excludes=["lib"])
        self.assertEqual(["src/a.py", "src/data.bin", "src/dist/generated.py", "src/notrace.py"], sorted(model.files))
        self.assertIn("RQ-DEM-005", code_links(model, "src/data.bin"))

    def test_RQ_TRC_006_given_a_binary_or_oversized_file_when_scanned_then_it_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "bin.py").write_bytes(b"RQ-DEM-001\x00\x01")
            (root / "big.py").write_bytes(b"# RQ-DEM-001\n" + b"x" * tm.MAX_SOURCE_BYTES)
            (root / "ok.py").write_text("# RQ-DEM-001\n", encoding="utf-8")
            model = tm.build_process_model(PROCESS)
            tm.scan_sources(model, [root], base=root)
            self.assertEqual(["ok.py"], sorted(model.files))

    def test_RQ_TRC_007_given_an_undefined_id_in_a_source_when_scanned_then_it_is_an_undefined_element(self):
        self.assertEqual("undefined", self.model.elements["RQ-DEM-099"]["kind"])


class CoverageAndGapsTest(unittest.TestCase):
    """TASK-TRC-003: RQ-TRC-008, RQ-TRC-009, RQ-TRC-017 (DEC-TRC-002, DEC-TRC-004)."""

    @classmethod
    def setUpClass(cls):
        cls.analysis = tm.analyse(scanned_model())

    def test_RQ_TRC_008_given_the_fixture_when_coverage_is_computed_then_each_requirement_has_its_rating(self):
        self.assertEqual({"RQ-DEM-001": "covered", "RQ-DEM-002": "indirect", "RQ-DEM-003": "uncovered",
                          "RQ-DEM-004": "uncovered", "RQ-DEM-005": "uncovered"}, self.analysis["coverage"])

    def test_RQ_TRC_008_given_a_requirement_depending_on_a_covered_one_when_rated_then_the_dependency_does_not_cover_it(
            self):
        model = tm.build_process_model(PROCESS)
        model.add_edge("src/x.py", "RQ-DEM-001", "code", [1, "RQ-DEM-001"])
        self.assertEqual("uncovered", tm.analyse(model)["coverage"]["RQ-DEM-002"])

    def test_RQ_TRC_009_given_the_fixture_when_gaps_are_listed_then_each_list_holds_its_planted_elements(self):
        self.assertEqual({"uncovered": ["RQ-DEM-003", "RQ-DEM-004", "RQ-DEM-005"],
                          "untasked": ["RQ-DEM-004", "RQ-DEM-005"],
                          "task-no-rq": ["TASK-DEM-003"],
                          "adr-no-rq": ["ADR-DEM-002"],
                          "empty": ["FTR-DEM-002", "ADR-DEM-002", "PLAN-DEM-002"],
                          "isolated": ["RQ-DEM-005", "FTR-DEM-002", "ADR-DEM-002", "PLAN-DEM-002"],
                          "undefined": ["DEC-DEM-099", "RQ-DEM-099"],
                          "untraced-files": ["src/notrace.py"]}, self.analysis["gaps"])

    def test_RQ_TRC_017_given_the_fixture_when_the_generator_runs_then_it_prints_the_counts_and_the_gaps(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out, _ = run_main(["--process", str(PROCESS), "--sources", str(SOURCES), "--out",
                                     str(Path(tmp) / "page.html")])
        self.assertEqual(0, code)
        summary = out.strip().splitlines()[-1]
        for part in ("15 elements", "4 files", "RQ 5: covered 1, indirect 1, uncovered 3", "uncovered 3", "untasked 2",
                     "task-no-rq 1", "adr-no-rq 1", "empty 3", "isolated 4", "undefined 2", "untraced-files 1"):
            self.assertIn(part, summary)


GENERATED_AT = "2026-01-01T00:00Z"
SKILL = HERE.parent
RAW_VISUAL_RE = r"#[0-9A-Fa-f]{3,8}\b|\brgba?\(|\bhsla?\(|\b\d+(?:\.\d+)?(?:px|ms)\b"


def generate(out, *extra):
    code, stdout, stderr = run_main(["--process", str(PROCESS), "--sources", str(SOURCES), "--out", str(out),
                                     "--generated-at", GENERATED_AT, *extra])
    if code:
        raise AssertionError(stderr)
    return out.read_text(encoding="utf-8"), stdout


def data_block(page):
    start = page.index('<script type="application/json" id="trace-data">') + len(
        '<script type="application/json" id="trace-data">')
    return page[start:page.index("</script>", start)]


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

    def test_RQ_TRC_010_given_a_generated_page_when_searched_then_it_references_nothing_outside_itself(self):
        lowered = self.page.lower()
        for needle in ("<script src", "<link", "url(http", "@import", 'src="http', "href=\"http"):
            self.assertNotIn(needle, lowered)

    def test_RQ_TRC_023_given_one_generated_at_when_generated_twice_then_the_pages_are_identical_and_in_lf(self):
        again, _ = generate(Path(self.tmp.name) / "again.html")
        self.assertEqual(self.page, again)
        raw = (Path(self.tmp.name) / "again.html").read_bytes()
        self.assertNotIn(b"\r", raw)

    def test_RQ_TRC_024_given_the_vendored_library_when_hashed_then_it_matches_the_recorded_sha256(self):
        import hashlib
        import re
        vendor = SKILL / "scripts" / "vendor"
        recorded = dict(re.findall(r"^\| `([^`]+)` \|.*\| ([0-9a-f]{64}) \|$", (vendor / "VENDOR.md").read_text(
            encoding="utf-8"), re.M))
        for name, sha in recorded.items():
            self.assertEqual(sha, hashlib.sha256((vendor / name).read_bytes()).hexdigest(), name)
        self.assertEqual({"cytoscape.min.js", "LICENSE"}, set(recorded))

    def test_RQ_TRC_024_given_a_generated_page_then_it_carries_the_library_and_its_licence(self):
        self.assertIn("Permission is hereby granted", self.page)
        self.assertIn("The Cytoscape Consortium", self.page)

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
    """A Chromium-family browser for the page tests: $AGNOS_TRACE_BROWSER, a usual install path or one on the PATH."""
    import os
    import shutil
    if os.environ.get("AGNOS_TRACE_BROWSER"):
        return os.environ["AGNOS_TRACE_BROWSER"]
    found = [p for p in BROWSER_CANDIDATES if Path(p).is_file()] + [shutil.which(n) for n in BROWSER_NAMES]
    return next((p for p in found if p), None)


BROWSER = find_browser()


def rendered_dom(page_path, fragment=""):
    """The DOM of the page once its script ran, from a headless browser (--dump-dom)."""
    import subprocess
    with tempfile.TemporaryDirectory() as profile:
        done = subprocess.run([BROWSER, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                               f"--user-data-dir={profile}", f"--virtual-time-budget={BROWSER_BUDGET_MS}",
                               f"--window-size={BROWSER_WINDOW}", "--dump-dom",
                               page_path.resolve().as_uri() + fragment], capture_output=True, timeout=120, check=False)
    return done.stdout.decode("utf-8", errors="replace")


@unittest.skipUnless(BROWSER, "no Chromium-family browser found (set AGNOS_TRACE_BROWSER)")
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


@unittest.skipUnless(BROWSER, "no Chromium-family browser found (set AGNOS_TRACE_BROWSER)")
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


def rendered_dom_after(page_path, script):
    """The DOM once the page ran, then the given script (a copy of the page with the script at its end)."""
    copy = page_path.with_name("scripted-" + page_path.name)
    copy.write_text(page_path.read_text(encoding="utf-8").replace("</body>", f"<script>{script}</script></body>"),
                    encoding="utf-8")
    return rendered_dom(copy)


KEY_PRESSES = """
const press = (id, key, times) => { const bar = document.getElementById(id);
  for (let i = 0; i < times; i += 1) bar.dispatchEvent(new KeyboardEvent("keydown", { key, bubbles: true })); };
press("split-left", "ArrowRight", 3);
press("split-right", "ArrowLeft", 50);
"""


@unittest.skipUnless(BROWSER, "no Chromium-family browser found (set AGNOS_TRACE_BROWSER)")
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


@unittest.skipUnless(BROWSER, "no Chromium-family browser found (set AGNOS_TRACE_BROWSER)")
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
        tree = ast.parse((SKILL / "scripts" / "trace_matrix.py").read_text(encoding="utf-8"))
        imported = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
        imported |= {node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module}
        self.assertEqual(set(), imported - set(sys.stdlib_module_names))


if __name__ == "__main__":
    unittest.main()
