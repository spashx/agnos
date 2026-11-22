"""Tests of the graph explorer page written by agnos-graph --explorer (FTR-TRC-014; ADR-TRC-025: DEC-TRC-084, DEC-TRC-085,
DEC-TRC-088, DEC-TRC-089, DEC-TRC-091; design system ADR-TRC-002: DEC-TRC-009, DEC-TRC-010).

TASK-TRC-133: RQ-TRC-144 to RQ-TRC-149, RQ-TRC-154 to RQ-TRC-157.
Run from the repository root: python -m unittest discover -s .github/skills/agnos-graph/tests -v
The page tests need a Chromium-family browser (set AGNOS_GRAPH_BROWSER); without one they are skipped, never failed.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))
import agnos_layout  # noqa: E402  RQ-PLG-036: the graph file's name, as the script reads it
from test_graph import PROCESS, SOURCES, GENERATED_AT, run_main  # noqa: E402

ASSETS = HERE.parent / "assets" / "explorer"
TOKENS = ASSETS / "tokens.json"
PAGE_NAME = "graph-explorer.html"                 # RQ-TRC-144: stated, not read from the script
DATA_NAME = "agnos-graph.data.js"
DATA_GLOBAL = "window.AGNOS_GRAPH"                # DEC-TRC-088
NODE_TYPES = ("ftr", "rq", "adr", "dec", "plan", "task", "sec", "file", "fn", "undefined")   # RQ-TRC-146, RQ-TRC-147
BACKGROUNDS = ("surface", "surface-subtle", "surface-selected")                              # RQ-TRC-157
CONTRAST_MIN = 4.5
RAW_VISUAL_RE = re.compile(r"#[0-9A-Fa-f]{3,8}\b|\brgba?\(|\bhsla?\(|\b\d+(?:\.\d+)?px\b")    # DEC-TRC-010
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
COMPAT_LAYER_VAR = "__COMPAT_LAYER"               # under this Windows shim, Edge dumps an empty DOM
NEEDS_BROWSER = "no Chromium-family browser found (set AGNOS_GRAPH_BROWSER)"


def find_browser():
    """A Chromium-family browser: $AGNOS_GRAPH_BROWSER, a usual install path or one on the PATH."""
    if os.environ.get("AGNOS_GRAPH_BROWSER"):
        return os.environ["AGNOS_GRAPH_BROWSER"]
    found = [p for p in BROWSER_CANDIDATES if Path(p).is_file()] + [shutil.which(n) for n in BROWSER_NAMES]
    return next((p for p in found if p), None)


BROWSER = find_browser()


def rendered_dom_after(page, script):
    """The DOM once the page ran, then the given script, from a headless browser (--dump-dom) (RQ-TRC-145)."""
    copy = page.with_name("scripted-" + page.name)
    copy.write_text(page.read_text(encoding="utf-8").replace("</body>", f"<script>{script}</script></body>"),
                    encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k.upper() != COMPAT_LAYER_VAR}
    with tempfile.TemporaryDirectory() as profile:
        done = subprocess.run([BROWSER, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                               f"--user-data-dir={profile}", f"--virtual-time-budget={BROWSER_BUDGET_MS}",
                               f"--window-size={BROWSER_WINDOW}", "--dump-dom", copy.resolve().as_uri()],
                              capture_output=True, timeout=120, check=False, env=env)
    return done.stdout.decode("utf-8", errors="replace")


def results(dom):
    """The values a test script left in data-r-* attributes of the root element."""
    return dict(re.findall(r'data-r-([a-z-]+)="([^"]*)"', dom))


def build(tmp, *extra):
    """The graph of the fixture, built in tmp with the given options; returns (exit code, graph path, stderr)."""
    out = Path(tmp) / "graph" / "agnos-graph.json"
    code, _, err = run_main(["--process", str(PROCESS), "--sources", str(SOURCES), "--out", str(out),
                             "--generated-at", GENERATED_AT, *extra])
    return code, out, err


def luminance(hex_colour):
    """WCAG 2.1 relative luminance of a #RRGGBB colour (RQ-TRC-157)."""
    channels = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(a, b):
    """WCAG 2.1 contrast ratio of two #RRGGBB colours (RQ-TRC-157)."""
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


class ExplorerFilesTest(unittest.TestCase):
    """TASK-TRC-133: RQ-TRC-144, RQ-TRC-145, RQ-TRC-155, RQ-TRC-156 (DEC-TRC-085, DEC-TRC-088)."""

    def test_RQ_TRC_144_given_explorer_when_the_graph_is_built_then_the_page_and_its_data_are_beside_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out, err = build(tmp, "--explorer")
            self.assertEqual(0, code, err)
            self.assertEqual({out.name, PAGE_NAME, DATA_NAME}, {p.name for p in out.parent.iterdir()})

    def test_RQ_TRC_144_given_no_explorer_when_the_graph_is_built_then_no_explorer_file_is_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out, err = build(tmp)
            self.assertEqual(0, code, err)
            self.assertEqual({out.name}, {p.name for p in out.parent.iterdir()})

    def test_RQ_TRC_156_given_explorer_or_not_then_the_graph_file_holds_the_same_bytes(self):
        with tempfile.TemporaryDirectory() as plain, tempfile.TemporaryDirectory() as explored:
            self.assertEqual(0, build(plain)[0])
            self.assertEqual(0, build(explored, "--explorer")[0])
            self.assertEqual(build(plain)[1].read_bytes(), build(explored, "--explorer")[1].read_bytes())

    def test_RQ_TRC_145_given_the_data_script_then_it_sets_the_global_to_the_graph(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, out, _ = build(tmp, "--explorer")
            text = (out.parent / DATA_NAME).read_text(encoding="utf-8")
            self.assertTrue(text.startswith(DATA_GLOBAL + " = "))
            self.assertEqual(json.loads(out.read_text(encoding="utf-8")),
                             json.loads(text[len(DATA_GLOBAL) + len(" = "):].rstrip().rstrip(";")))

    def test_RQ_TRC_155_given_the_page_then_it_is_english_and_loads_its_data_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, out, _ = build(tmp, "--explorer")
            page = (out.parent / PAGE_NAME).read_text(encoding="utf-8")
            self.assertIn('<html lang="en">', page)
            self.assertIn(f'<script src="{DATA_NAME}"></script>', page)
            self.assertIn("<title>Graph explorer", page)
            self.assertNotRegex(page, r"/\*@[A-Z_]+@\*/|@[A-Z_]+@")    # every marker replaced


class ExplorerTokensTest(unittest.TestCase):
    """TASK-TRC-133: RQ-TRC-147, RQ-TRC-157 (DEC-TRC-009, DEC-TRC-010, DEC-TRC-091)."""

    @classmethod
    def setUpClass(cls):
        cls.tokens = json.loads(TOKENS.read_text(encoding="utf-8"))

    def colour(self, semantic):
        return self.tokens["global"][self.tokens["semantic"][semantic]]

    def test_RQ_TRC_147_given_the_tokens_then_each_node_type_has_a_surface_and_a_text_colour(self):
        for kind in NODE_TYPES:
            self.assertIn(f"type-{kind}", self.tokens["semantic"])
            self.assertIn(f"type-{kind}-text", self.tokens["semantic"])

    def test_RQ_TRC_157_given_each_type_text_token_then_its_contrast_on_every_background_is_at_least_4_5(self):
        ratios = {(kind, bg): round(contrast(self.colour(f"type-{kind}-text"), self.colour(bg)), 2)
                  for kind in NODE_TYPES for bg in BACKGROUNDS}
        self.assertEqual({}, {k: r for k, r in ratios.items() if r < CONTRAST_MIN})

    def test_DEC_TRC_010_given_the_page_style_and_script_then_no_raw_visual_value_is_written(self):
        for name in ("explorer.css", "explorer.js"):
            text = re.sub(r"/\*.*?\*/|//[^\n]*", "", (ASSETS / name).read_text(encoding="utf-8"), flags=re.S)
            self.assertEqual([], RAW_VISUAL_RE.findall(text), name)


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class ExplorerPageTest(unittest.TestCase):
    """TASK-TRC-133: RQ-TRC-145, RQ-TRC-146, RQ-TRC-148, RQ-TRC-149, RQ-TRC-154, in a headless browser."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        code, out, err = build(cls.tmp.name, "--explorer")
        assert code == 0, err
        cls.page = out.parent / PAGE_NAME
        cls.graph = json.loads(out.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_page(self, script):
        return results(rendered_dom_after(self.page, "const r = (k, v) => document.documentElement.setAttribute("
                                                     "'data-r-' + k, String(v));" + script))

    def test_RQ_TRC_145_given_the_page_then_its_header_shows_the_date_the_commit_and_the_counts(self):
        found = self.run_page("r('head', document.getElementById('graph-meta').textContent);")
        self.assertIn(GENERATED_AT, found["head"])
        self.assertIn(f"{len(self.graph['elements'])} elements", found["head"])

    def test_RQ_TRC_146_given_the_tables_then_they_list_every_node_and_relation_of_the_file(self):
        found = self.run_page("agnosExplorer.showView('nodes'); r('nodes', document.querySelectorAll('#node-table tbody tr').length);"
                              "agnosExplorer.showView('relations'); r('relations', document.querySelectorAll('#relation-table tbody tr').length);")
        nodes = len(self.graph["elements"]) + len(self.graph["sections"]) + len(self.graph["files"])
        relations = len(self.graph["edges"]) + len(self.graph["sections"]) + sum(len(s["refs"]) for s in self.graph["sections"])
        self.assertEqual((str(nodes), str(relations)), (found["nodes"], found["relations"]))

    def test_RQ_TRC_149_given_the_relation_table_then_it_scrolls_under_a_fixed_header_and_sorts_on_a_header_click(self):
        found = self.run_page(
            "agnosExplorer.showView('relations'); const t = document.getElementById('relation-table');"
            "r('sticky', getComputedStyle(t.querySelector('th')).position);"
            "r('scroll', getComputedStyle(t.closest('.table-scroll')).overflowY);"
            "const head = t.querySelector('th[data-key=\"source\"]'); head.click();"
            "const first = () => t.querySelector('tbody tr td').textContent; r('asc', first()); head.click(); r('desc', first());")
        sources = sorted(e[0] for e in self.graph["edges"])
        self.assertEqual(("sticky", "auto"), (found["sticky"], found["scroll"]))
        self.assertEqual(sources[0], found["asc"])
        self.assertNotEqual(found["asc"], found["desc"])

    def test_RQ_TRC_145_given_a_file_without_elements_then_it_is_named_and_the_graph_stays(self):
        found = self.run_page("const before = agnosExplorer.counts().nodes; agnosExplorer.loadText('bad.json', '{}');"
                              "r('message', document.getElementById('load-message').textContent);"
                              "r('kept', agnosExplorer.counts().nodes === before);")
        self.assertIn("bad.json", found["message"])
        self.assertIn("no elements list", found["message"])
        self.assertEqual("true", found["kept"])

    def test_RQ_TRC_145_given_another_valid_graph_then_it_replaces_the_shown_one(self):
        other = {"meta": {"generatedAt": "2026-01-01T00:00Z", "commit": None}, "edges": [], "files": [], "links": [],
                 "sections": [], "tasks": {}, "elements": [{"id": "RQ-ZZZ-001", "type": "RQ", "tri": "ZZZ", "kind": "element",
                                                           "doc": "x.md", "first": 1, "last": 2, "status": "", "title": "T"}]}
        found = self.run_page(f"agnosExplorer.loadText('other.json', {json.dumps(json.dumps(other))});"
                              "r('nodes', agnosExplorer.counts().nodes);")
        self.assertEqual("1", found["nodes"])

    def test_RQ_TRC_148_given_the_splitters_when_moved_with_the_keys_then_the_side_panels_change_by_one_step(self):
        found = self.run_page(
            "const w = (id) => document.getElementById(id).getBoundingClientRect().width;"
            "const key = (id, k) => document.getElementById(id).dispatchEvent(new KeyboardEvent('keydown', {key: k, bubbles: true}));"
            "const step = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--c-splitter-step'));"
            "const s0 = w('facets'), d0 = w('detail'); key('split-left', 'ArrowRight'); key('split-right', 'ArrowLeft');"
            "r('left', Math.round(w('facets') - s0) === Math.round(step)); r('right', Math.round(w('detail') - d0) === Math.round(step));")
        self.assertEqual(("true", "true"), (found["left"], found["right"]))

    def test_RQ_TRC_154_given_a_selected_plan_then_the_detail_lists_its_properties_and_relations_with_field_and_proof(self):
        found = self.run_page("agnosExplorer.select('PLAN-DEM-001'); const d = document.getElementById('detail');"
                              "r('text', d.textContent.replace(/\\s+/g, ' '));")
        self.assertIn("PLAN-DEM-001", found["text"])
        self.assertIn("ADR-DEM-001", found["text"])
        self.assertIn("ADR refs", found["text"])
        self.assertIn("- **ADR refs**: ADR-DEM-001", found["text"])

    def test_RQ_TRC_147_given_a_type_label_in_a_table_then_it_uses_its_type_text_token(self):
        found = self.run_page(
            "agnosExplorer.showView('nodes'); const cell = document.querySelector('#node-table .type-label[data-type=\"RQ\"]');"
            "const want = getComputedStyle(document.documentElement).getPropertyValue('--s-type-rq-text').trim();"
            "const probe = document.createElement('span'); probe.style.color = want; document.body.append(probe);"
            "r('same', getComputedStyle(cell).color === getComputedStyle(probe).color);")
        self.assertEqual("true", found["same"])


if __name__ == "__main__":
    unittest.main()
