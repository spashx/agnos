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
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))
import agnos_layout  # noqa: E402  RQ-PLG-036: the graph file's name, as the script reads it
from test_graph import (PROCESS, SOURCES, GENERATED_AT, HAS_TREE_SITTER, NEEDS_TREE_SITTER, run_main,  # noqa: E402
                        committed_fixture, isolated_git)

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
CDN_PROBE = "https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.30.2/cytoscape.min.js"   # the library the graph view loads
CDN_TIMEOUT_S = 5
NEEDS_NETWORK = "no Chromium-family browser, or cdnjs unreachable: the graph view loads Cytoscape.js from it (DEC-TRC-090)"


def cdn_reachable():
    """True when cdnjs answers: the graph view loads Cytoscape.js from it (RQ-TRC-150, DEC-TRC-090)."""
    import urllib.request
    try:
        urllib.request.urlopen(urllib.request.Request(CDN_PROBE, method="HEAD"), timeout=CDN_TIMEOUT_S).close()
        return True
    except OSError:
        return False


ONLINE = bool(BROWSER) and cdn_reachable()


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

    def test_RQ_TRC_114_given_the_header_then_it_draws_the_agnos_mark_in_the_brand_colours(self):
        """TASK-TRC-134 (owner's request of 2026-11-23): Given the page, Then its header draws the AGNOS mark "Spans" And its
        five colours are the performance center's brand colours (RQ-TRC-114, DEC-TRC-056)."""
        page = (ASSETS / "explorer.html").read_text(encoding="utf-8")
        parts = ("mark-tile", "mark-bar-light", "mark-bar-blue", "mark-bar-green", "mark-bar-yellow")
        for part in parts:
            self.assertIn(f'class="{part}"', page)
        perf = json.loads((HERE.parents[1] / "agnos-perf-center" / "assets" / "tokens.json").read_text(encoding="utf-8"))
        for brand in ("brand-tile", "brand-light", "brand-blue", "brand-green", "brand-yellow"):
            self.assertEqual(perf["global"][perf["semantic"][brand]], self.colour(brand), brand)

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

    # RQ-TRC-145, amended by TASK-GXP-008 and TASK-GXP-009: the date as the performance center shows it, its UTC value in the
    # tooltip, on the right beside the help, no commit, no counts
    def test_RQ_TRC_145_given_the_page_then_its_header_shows_the_readable_date_with_utc_tooltip_on_the_right_alone(self):
        found = self.run_page("const head = document.getElementById('graph-meta'); r('head', head.textContent);"
                              "r('tip', head.querySelector('[title]').title);"
                              "const help = document.getElementById('help-button').getBoundingClientRect();"
                              "const box = head.getBoundingClientRect(); r('beside', box.right <= help.left && help.left - box.right < help.width * 2);")
        self.assertTrue(found["head"].startswith("Generated "))
        self.assertNotIn(GENERATED_AT, found["head"])
        for word in ("commit", "elements", "nodes", "relations"):
            self.assertNotIn(word, found["head"])
        self.assertEqual(GENERATED_AT.replace("T", " ").replace("Z", " UTC"), found["tip"])
        self.assertEqual("true", found["beside"])

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

    def test_RQ_TRC_159_given_the_title_header_edge_dragged_then_the_column_widens_keeps_it_on_sort_and_has_a_minimum(self):
        # TASK-TRC-142: a drag is a pointer press on the header's handle, moves on the document, a release
        found = self.run_page(
            "agnosExplorer.showView('nodes'); const th = () => document.querySelector('#node-table th[data-key=\"title\"]');"
            "const drag = (dx) => { const h = th().querySelector('.col-resize'); const x = h.getBoundingClientRect().left;"
            " h.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, clientX: x, pointerId: 1 }));"
            " document.dispatchEvent(new PointerEvent('pointermove', { bubbles: true, clientX: x + dx, pointerId: 1 }));"
            " document.dispatchEvent(new PointerEvent('pointerup', { bubbles: true, clientX: x + dx, pointerId: 1 })); };"
            "const w = () => th().getBoundingClientRect().width; const before = w(); drag(150); r('wider', w() - before);"
            "const wide = w(); th().click(); r('sorted', Math.abs(w() - wide) < 1);"
            "drag(-5000); r('min', Math.round(w()));"
            "r('token', parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--c-table-column-min-width')));")
        self.assertGreater(float(found["wider"]), 100)
        self.assertEqual("true", found["sorted"])
        self.assertEqual(found["token"], found["min"])

    def test_RQ_TRC_165_given_the_graph_view_then_the_legend_shows_types_and_kinds_from_tokens_and_folds(self):
        # TASK-TRC-145
        found = self.run_page(
            "const css = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();"
            "const rgb = (c) => { const d = document.createElement('i'); d.style.color = c; document.body.appendChild(d); const v = getComputedStyle(d).color; d.remove(); return v; };"
            "const legend = document.getElementById('graph-legend');"
            "const rq = legend.querySelector('[data-type=\"RQ\"] .swatch'); r('rq', getComputedStyle(rq).backgroundColor === rgb(css('--s-type-rq')));"
            "const line = legend.querySelector('[data-kind=\"contains\"] .legend-line'); const s = getComputedStyle(line);"
            "r('dashed', s.borderTopStyle); r('colour', s.borderTopColor === rgb(css('--c-graph-edge-contains')));"
            "legend.querySelector('.legend-toggle').click(); r('folded', getComputedStyle(legend.querySelector('.legend-body')).display);"
            "r('title', getComputedStyle(legend.querySelector('.legend-toggle')).display);")
        self.assertEqual(("true", "dashed", "true"), (found["rq"], found["dashed"], found["colour"]))
        self.assertEqual("none", found["folded"])
        self.assertNotEqual("none", found["title"])

    def test_RQ_TRC_165_given_the_graph_view_then_the_legend_is_a_wrapped_band_along_its_bottom(self):
        # TASK-TRC-148: as the performance center's legend
        found = self.run_page(
            "agnosExplorer.showView('graph'); const view = document.getElementById('view-graph').getBoundingClientRect();"
            "const legend = document.getElementById('graph-legend'); const box = legend.getBoundingClientRect();"
            "r('gap', view.bottom - box.bottom); r('wide', box.width > box.height);"
            "const items = [...legend.querySelectorAll('li')].map((li) => li.getBoundingClientRect());"
            "r('rows', items[1].top === items[0].top && items[1].left > items[0].left);")
        self.assertLess(float(found["gap"]), 40)
        self.assertGreaterEqual(float(found["gap"]), 0)
        self.assertEqual(("true", "true"), (found["wide"], found["rows"]))

    def test_RQ_TRC_146_given_an_undefined_task_id_selected_then_the_detail_names_its_type_as_not_defined(self):
        # TASK-TRC-148: the note of TASK-TRC-147 holds for every type, not only ADR
        graph = {"elements": [{"id": "TASK-ZZZ-001", "kind": "undefined", "type": "TASK", "tri": "ZZZ", "title": "", "doc": "",
                               "first": 0, "last": 0, "status": ""}], "edges": []}
        found = self.run_page(f"agnosExplorer.loadText('g.json', {json.dumps(json.dumps(graph))});"
                              "agnosExplorer.select('TASK-ZZZ-001'); r('note', document.querySelector('#detail .detail-empty').textContent);")
        self.assertIn("cited TASK ID, not defined in the index", found["note"])

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


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class QueryLanguageTest(unittest.TestCase):
    """TASK-TRC-135: RQ-TRC-151, RQ-TRC-152, RQ-TRC-155 (DEC-TRC-092), in a headless browser."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        code, out, err = build(cls.tmp.name, "--explorer")
        assert code == 0, err
        cls.page = out.parent / PAGE_NAME
        cls.graph = json.loads(out.read_text(encoding="utf-8"))
        cls.defined = {e["id"]: e for e in cls.graph["elements"] if e["kind"] == "element"}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def shown_after(self, query):
        """The node IDs every view shows once the query ran, and the query's message."""
        found = results(rendered_dom_after(self.page, "const r = (k, v) => document.documentElement.setAttribute('data-r-' + k,"
                                                      f" String(v)); agnosExplorer.query({json.dumps(query)});"
                                                      "r('shown', agnosExplorer.shownIds().join(' '));"
                                                      "r('message', document.getElementById('query-message').textContent);"))
        return set(found.get("shown", "").split()), found.get("message", "")

    def of_type(self, *types):
        return {i for i, e in self.defined.items() if e["type"] in types}

    def linked(self, source_type, field, target_type):
        """(source, target) of the links whose source and target types and field are those given."""
        return {(s, t) for s, t, rows in self.graph["links"] if s.startswith(source_type + "-") and t.startswith(target_type + "-")
                and any(f == field for _, f in rows)}

    def test_RQ_TRC_152_given_key_value_terms_then_every_term_is_met(self):
        shown, _ = self.shown_after("type:RQ tri:DEM status:!Done")
        self.assertEqual({i for i in self.of_type("RQ") if self.defined[i]["status"] != "Done"}, shown)

    def test_RQ_TRC_152_given_a_list_of_values_then_one_of_them_is_met(self):
        self.assertEqual(self.of_type("RQ", "DEC"), self.shown_after("type:RQ,DEC")[0])

    def test_RQ_TRC_152_given_a_contains_term_then_the_text_is_found_whatever_its_case(self):
        shown, _ = self.shown_after("title:~COVER")
        self.assertEqual({i for i, e in self.defined.items() if "cover" in e["title"].lower()}, shown)
        self.assertTrue(shown)

    def test_RQ_TRC_152_given_a_negated_cited_by_term_then_only_the_uncited_requirements_are_shown(self):
        cited = {t for _, t in self.linked("TASK", "Requirement refs", "RQ")}
        self.assertEqual(self.of_type("RQ") - cited, self.shown_after("type:RQ !cited-by:TASK[Requirement refs]")[0])

    def test_RQ_TRC_152_given_a_cites_term_then_only_the_citing_nodes_are_shown(self):
        citing = {s for s, t, rows in self.graph["links"] if t.startswith("ADR-") and any(f == "ADR refs" for _, f in rows)}
        self.assertTrue(citing)
        self.assertEqual(citing, self.shown_after("cites:ADR[ADR refs]")[0])

    def test_RQ_TRC_152_given_an_edge_query_then_only_those_relations_and_their_ends_are_shown(self):
        ends = {x for s, t, rows in self.graph["links"] if s.startswith("DEC-") and any(f == "text" for _, f in rows) for x in (s, t)}
        self.assertTrue(ends)
        self.assertEqual(ends, self.shown_after("edge kind:refs field:text from:DEC")[0])

    def test_RQ_TRC_152_given_a_term_that_does_not_parse_then_it_is_named_and_the_former_result_stays(self):
        found = results(rendered_dom_after(self.page, "const r = (k, v) => document.documentElement.setAttribute('data-r-' + k,"
                                                      " String(v)); agnosExplorer.query('type:RQ'); const before = agnosExplorer.shownIds().join(' ');"
                                                      "agnosExplorer.query('type:'); r('kept', agnosExplorer.shownIds().join(' ') === before);"
                                                      "r('message', document.getElementById('query-message').textContent);"))
        self.assertEqual("true", found["kept"])
        self.assertIn("type:", found["message"])

    def test_RQ_TRC_151_given_a_field_unchecked_then_no_relation_of_that_field_is_shown(self):
        found = results(rendered_dom_after(self.page, "const r = (k, v) => document.documentElement.setAttribute('data-r-' + k,"
                                                      " String(v)); const box = document.querySelector('#facet-field input[value=\"text\"]');"
                                                      "r('count', box.closest('label').textContent.replace(/\\D+/g, ' ').trim()); box.click();"
                                                      "agnosExplorer.showView('relations');"
                                                      "r('fields', [...document.querySelectorAll('#relation-table tbody tr td:nth-child(4)')].map((c) => c.textContent).join('|'));"))
        self.assertNotIn("text", found["fields"].split("|"))
        texts = sum(1 for _, _, rows in self.graph["links"] if any(f == "text" for _, f in rows))
        self.assertIn(str(texts), found["count"].split())

    def test_RQ_TRC_160_given_the_node_types_facet_when_none_then_all_is_clicked_then_no_node_then_every_node_is_shown(self):
        # TASK-TRC-141
        found = results(rendered_dom_after(self.page, "const r = (k, v) => document.documentElement.setAttribute('data-r-' + k,"
                                                      " String(v)); const f = () => document.getElementById('facet-type');"
                                                      "f().querySelector('[data-bulk=\"none\"]').click(); r('none', agnosExplorer.shownIds().length);"
                                                      "r('checked', f().querySelectorAll('input:checked').length);"
                                                      "f().querySelector('[data-bulk=\"all\"]').click(); r('all', agnosExplorer.shownIds().length);"
                                                      "r('total', agnosExplorer.counts().nodes);"))
        self.assertEqual(("0", "0"), (found["none"], found["checked"]))
        self.assertEqual(found["total"], found["all"])

    def test_RQ_TRC_161_given_a_facet_list_with_its_scrollbar_then_every_count_ends_left_of_it(self):
        # TASK-TRC-141: the list is made shorter than its values so that its scrollbar shows
        found = results(rendered_dom_after(self.page, "const r = (k, v) => document.documentElement.setAttribute('data-r-' + k,"
                                                      " String(v)); const list = document.querySelector('#facet-type .facet-values');"
                                                      "list.style.maxHeight = '3em'; const inner = list.getBoundingClientRect().left + list.clientLeft + list.clientWidth;"
                                                      "r('scrolls', list.scrollHeight > list.clientHeight);"
                                                      "r('clear', [...list.querySelectorAll('.count')].every((c) => c.getBoundingClientRect().right <= inner + 0.5));"
                                                      "const panel = document.getElementById('facets');"
                                                      "r('panel', getComputedStyle(panel).scrollbarGutter);"))
        self.assertEqual(("true", "true"), (found["scrolls"], found["clear"]))
        self.assertIn("stable", found["panel"])

    def test_RQ_TRC_151_given_the_query_focused_when_a_facet_value_is_clicked_then_its_term_is_written(self):
        found = results(rendered_dom_after(self.page, "const r = (k, v) => document.documentElement.setAttribute('data-r-' + k,"
                                                      " String(v)); const q = document.getElementById('query'); q.focus();"
                                                      "document.querySelector('#facet-type input[value=\"RQ\"]').click(); r('query', q.value);"))
        self.assertIn("type:RQ", found["query"])


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class SavedQueriesTest(unittest.TestCase):
    """TASK-TRC-136: RQ-TRC-153, RQ-TRC-155 (DEC-TRC-093), in a headless browser, each run in a fresh profile."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        code, out, err = build(cls.tmp.name, "--explorer")
        assert code == 0, err
        cls.page = out.parent / PAGE_NAME
        cls.presets = json.loads((ASSETS / "presets.json").read_text(encoding="utf-8"))["queries"]

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_page(self, script):
        return results(rendered_dom_after(self.page, "const r = (k, v) => document.documentElement.setAttribute('data-r-' + k,"
                                                     " String(v)); const s = agnosExplorer.saved;"
                                                     "const labels = () => [...document.querySelectorAll('#saved-queries .saved-run')]"
                                                     ".map((b) => b.textContent).join('|');" + script))

    def test_RQ_TRC_164_given_the_buttons_being_edited_then_every_control_has_a_tooltip_and_the_tools_read_words(self):
        # TASK-TRC-144: a node is selected, so that the detail panel's controls exist too
        found = self.run_page(
            "document.querySelector('[data-saved=\"manage\"]').click(); agnosExplorer.select('RQ-DEM-001');"
            "const controls = [...document.querySelectorAll('button, input, select, label.button, [role=tab]')];"
            "r('untitled', controls.filter((c) => !(c.title || '').trim()).map((c) => c.id || c.className || c.tagName).join('|'));"
            "r('tools', [...new Set([...document.querySelectorAll('.saved-tool')].map((b) => b.textContent))].join('|'));")
        self.assertEqual("", found["untitled"])
        self.assertEqual("Edit|Move left|Move right|Delete", found["tools"])

    def test_RQ_TRC_153_given_an_empty_store_then_the_default_buttons_are_shown(self):
        found = self.run_page("r('labels', labels());")
        self.assertEqual("|".join(p["label"] for p in self.presets), found["labels"])

    def test_RQ_TRC_153_given_a_created_button_when_the_page_reloads_then_it_is_shown_and_runs_its_query(self):
        found = self.run_page("s.add('Undefined IDs only', 'type:UNDEFINED'); s.load(); r('labels', labels());"
                              "[...document.querySelectorAll('#saved-queries .saved-run')].pop().click();"
                              "r('query', document.getElementById('query').value);")
        self.assertTrue(found["labels"].endswith("|Undefined IDs only"))
        self.assertEqual("type:UNDEFINED", found["query"])

    def test_RQ_TRC_153_given_a_button_edited_moved_and_deleted_when_reloaded_then_the_changes_are_kept(self):
        found = self.run_page("s.edit(0, 'First renamed', 'type:FTR'); s.move(0, 1); s.remove(2); s.load(); r('labels', labels());"
                              "r('query', s.list()[1].query);")
        labels = [p["label"] for p in self.presets]
        expected = [labels[1], "First renamed"] + labels[3:]
        self.assertEqual("|".join(expected), found["labels"])
        self.assertEqual("type:FTR", found["query"])

    def test_RQ_TRC_153_given_buttons_exported_then_imported_in_a_fresh_store_then_the_same_buttons_are_shown(self):
        found = self.run_page("s.add('Mine', 'type:RQ'); s.move(s.list().length - 1, -1); const text = s.exportText();"
                              "localStorage.clear(); s.load(); const fresh = labels(); s.importText(text); s.load();"
                              "r('fresh', fresh); r('labels', labels()); r('order', JSON.parse(text).queries.map((q) => q.label).join('|'));")
        self.assertEqual("|".join(p["label"] for p in self.presets), found["fresh"])
        self.assertEqual(found["order"], found["labels"])
        self.assertIn("Mine", found["labels"])

    def test_RQ_TRC_155_given_the_default_buttons_then_each_query_parses(self):
        found = self.run_page("r('bad', s.list().filter((q) => !agnosExplorer.query(q.query)).map((q) => q.label).join('|'));")
        self.assertEqual("", found["bad"])


@unittest.skipUnless(BROWSER and HAS_TREE_SITTER, f"{NEEDS_BROWSER}, or {NEEDS_TREE_SITTER}")
class CallGraphAndHistoryTest(unittest.TestCase):
    """TASK-TRC-137: RQ-TRC-146 (DEC-TRC-089): functions, calls, history and delivery in the explorer."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        folder, patch = isolated_git()
        cls.addClassCleanup(shutil.rmtree, folder, ignore_errors=True)
        with patch:
            process, src, head = committed_fixture(Path(cls.tmp.name))
            out = Path(cls.tmp.name) / "graph" / "agnos-graph.json"
            code, _, err = run_main(["--process", str(process), "--sources", str(src), "--sources", str(process.parent / "calls"),
                                     "--out", str(out), "--generated-at", GENERATED_AT, "--call-graph", "--history", "--explorer"])
        assert code == 0, err
        cls.page = out.parent / PAGE_NAME
        cls.graph = json.loads(out.read_text(encoding="utf-8"))
        cls.head = head

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_RQ_TRC_146_given_a_call_graph_then_its_functions_and_calls_are_nodes_and_relations(self):
        found = results(rendered_dom_after(self.page, "const r = (k, v) => document.documentElement.setAttribute('data-r-' + k, String(v));"
                                                      "agnosExplorer.query('type:FN'); r('fns', agnosExplorer.shownIds().length);"
                                                      "agnosExplorer.query('edge kind:call'); agnosExplorer.showView('relations');"
                                                      "r('calls', document.querySelectorAll('#relation-table tbody tr').length);"))
        self.assertEqual(str(len(self.graph["callGraph"]["functions"])), found["fns"])
        self.assertGreater(int(found["calls"]), 0)

    def test_RQ_TRC_146_given_a_history_then_a_task_detail_shows_its_commits_and_identities(self):
        task = next(iter(self.graph["tasks"]))
        found = results(rendered_dom_after(self.page, "const r = (k, v) => document.documentElement.setAttribute('data-r-' + k, String(v));"
                                                      f"agnosExplorer.select('{task}');"
                                                      "r('text', document.getElementById('detail').textContent.replace(/\\s+/g, ' '));"))
        self.assertIn(self.head[:10], found["text"])
        self.assertIn("Tester", found["text"])


LOAD_LIMIT_MS = 5000          # RQ-TRC-158


@unittest.skipUnless(ONLINE and HAS_TREE_SITTER and os.environ.get("AGNOS_GRAPH_PERF"),
                     "set AGNOS_GRAPH_PERF=1 (needs a browser, cdnjs and tree-sitter): builds this repository's graph")
class LoadTimeTest(unittest.TestCase):
    """TASK-TRC-138: RQ-TRC-158: this repository's graph with call graph and history, first view under 5 s."""

    def test_RQ_TRC_158_given_this_repository_graph_then_the_first_view_is_drawn_in_less_than_5_s(self):
        repo = HERE.parents[3]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "agnos-graph.json"
            code, _, err = run_main(["--process", str(repo / "agnos-process"), "--sources", str(repo / ".github"), "--out", str(out),
                                     "--call-graph", "--history", "--explorer"])
            self.assertEqual(0, code, err)
            env = {k: v for k, v in os.environ.items() if k.upper() != COMPAT_LAYER_VAR}
            with tempfile.TemporaryDirectory() as profile:
                done = subprocess.run([BROWSER, "--headless=new", "--disable-gpu", "--no-first-run", f"--user-data-dir={profile}",
                                       f"--window-size={BROWSER_WINDOW}", "--dump-dom", (out.parent / PAGE_NAME).resolve().as_uri()],
                                      capture_output=True, timeout=300, check=False, env=env)
            found = re.search(r'data-first-view-ms="(\d+)"', done.stdout.decode("utf-8", errors="replace"))
            self.assertIsNotNone(found)
            self.assertLess(int(found.group(1)), LOAD_LIMIT_MS)


@unittest.skipUnless(ONLINE, NEEDS_NETWORK)
class GraphViewTest(unittest.TestCase):
    """TASK-TRC-134: RQ-TRC-147, RQ-TRC-150, RQ-TRC-154 (DEC-TRC-090, DEC-TRC-091), in a headless browser."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        code, out, err = build(cls.tmp.name, "--explorer")
        assert code == 0, err
        cls.page = out.parent / PAGE_NAME

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_page(self, script):
        return results(rendered_dom_after(self.page, "const r = (k, v) => document.documentElement.setAttribute("
                                                     "'data-r-' + k, String(v)); const g = agnosExplorer.graph;"
                                                     "agnosExplorer.showView('graph');" + script))

    def test_RQ_TRC_150_given_a_dragged_node_when_a_type_is_hidden_then_shown_then_it_keeps_its_position(self):
        found = self.run_page("g.move('RQ-DEM-001', 4321, -1234); agnosExplorer.hideTypes(['TASK']);"
                              "r('hidden', g.shown('TASK-DEM-001')); agnosExplorer.hideTypes([]);"
                              "const p = g.position('RQ-DEM-001'); r('pos', Math.round(p.x) + ',' + Math.round(p.y));"
                              "r('back', g.shown('TASK-DEM-001'));")
        self.assertEqual(("false", "4321,-1234", "true"), (found["hidden"], found["pos"], found["back"]))

    def test_RQ_TRC_150_given_the_fit_button_then_every_shown_node_is_in_the_view(self):
        # 5000 graph units away: within what the minimum zoom token can frame (a view of about 11000 units at 0.08)
        found = self.run_page("g.move('RQ-DEM-001', 5000, 5000); document.getElementById('graph-fit').click();"
                              "r('inside', g.allInView());")
        self.assertEqual("true", found["inside"])

    def test_RQ_TRC_150_given_the_zoom_bounds_then_they_are_the_tokens(self):
        found = self.run_page(
            "const css = (n) => parseFloat(getComputedStyle(document.documentElement).getPropertyValue(n));"
            "const cy = g.cy(); r('min', cy.minZoom() === css('--c-graph-zoom-min')); r('max', cy.maxZoom() === css('--c-graph-zoom-max'));"
            "for (let i = 0; i < 40; i += 1) document.getElementById('graph-zoom-in').click(); r('top', cy.zoom() <= cy.maxZoom());")
        self.assertEqual(("true", "true", "true"), (found["min"], found["max"], found["top"]))

    def test_RQ_TRC_154_given_a_selected_node_when_isolated_then_widened_then_one_then_two_hops_are_shown(self):
        found = self.run_page("agnosExplorer.select('RQ-DEM-001'); agnosExplorer.isolate(); r('one', g.shownIds().join(' '));"
                              "agnosExplorer.widen(); r('two', g.shownIds().length);")
        one = set(found["one"].split())
        self.assertIn("RQ-DEM-001", one)
        self.assertIn("FTR-DEM-001", one)                  # its feature contains it: one hop
        self.assertGreater(int(found["two"]), len(one))

    def test_RQ_TRC_154_given_a_hidden_node_then_it_is_listed_and_can_be_shown_again(self):
        found = self.run_page("agnosExplorer.select('RQ-DEM-001'); agnosExplorer.hide('RQ-DEM-001');"
                              "r('gone', g.shown('RQ-DEM-001')); r('listed', document.getElementById('hidden-list').textContent);"
                              "document.querySelector('#hidden-list [data-unhide=\"RQ-DEM-001\"]').click(); r('back', g.shown('RQ-DEM-001'));")
        self.assertEqual("false", found["gone"])
        self.assertIn("RQ-DEM-001", found["listed"])
        self.assertEqual("true", found["back"])

    def test_RQ_TRC_151_given_a_relation_kind_unchecked_then_its_edges_leave_the_graph_and_the_count(self):
        # TASK-TRC-140: the graph view hides the relations a facet excludes, as the tables do
        found = self.run_page("const cy = g.cy(); const drawn = (k) => cy.edges().filter((e) => e.data('kind') === k && !e.hasClass('hidden')).length;"
                              "r('before', drawn('contains')); document.querySelector('#facet-kind input[value=\"contains\"]').click();"
                              "r('after', drawn('contains')); r('edges', g.shownEdgeCount());"
                              "r('count', document.getElementById('view-count').textContent.split('·')[1]);")
        self.assertGreater(int(found["before"]), 0)
        self.assertEqual("0", found["after"])
        self.assertIn(f"{found['edges']} /", found["count"])

    def test_RQ_TRC_162_given_circle_chosen_then_the_nodes_are_on_a_circle_in_view_and_keep_it_after_a_filter(self):
        # TASK-TRC-143
        found = self.run_page(
            "const sel = document.getElementById('graph-layout'); sel.value = 'circle'; sel.dispatchEvent(new Event('change'));"
            "const ps = g.shownIds().map((id) => g.position(id)); const cx = ps.reduce((s, p) => s + p.x, 0) / ps.length;"
            "const cy0 = ps.reduce((s, p) => s + p.y, 0) / ps.length; const d = ps.map((p) => Math.hypot(p.x - cx, p.y - cy0));"
            "r('spread', (Math.max(...d) - Math.min(...d)) / Math.max(...d)); r('inside', g.allInView());"
            "const before = g.position('RQ-DEM-001'); agnosExplorer.hideTypes(['TASK']); agnosExplorer.hideTypes([]);"
            "const after = g.position('RQ-DEM-001'); r('kept', Math.abs(before.x - after.x) + Math.abs(before.y - after.y) < 1);")
        self.assertLess(float(found["spread"]), 0.01)
        self.assertEqual(("true", "true"), (found["inside"], found["kept"]))

    def test_RQ_TRC_166_given_type_columns_when_top_to_bottom_chosen_then_a_type_shares_a_row_and_types_go_down(self):
        # TASK-TRC-149
        found = self.run_page(
            "const pick = (id, v) => { const s = document.getElementById(id); s.value = v; s.dispatchEvent(new Event('change')); };"
            "pick('graph-layout', 'columns'); pick('graph-direction', 'tb');"
            "const y = (id) => Math.round(g.position(id).y); r('row', y('RQ-DEM-001') === y('RQ-DEM-002'));"
            "r('down', y('FTR-DEM-001') < y('RQ-DEM-001') && y('RQ-DEM-001') < y('TASK-DEM-001'));"
            "r('enabled', !document.getElementById('graph-direction').disabled);"
            "pick('graph-layout', 'circle'); r('disabled', document.getElementById('graph-direction').disabled);")
        self.assertEqual(("true", "true", "true", "true"), (found["row"], found["down"], found["enabled"], found["disabled"]))

    def test_RQ_TRC_167_given_a_node_hovered_then_after_the_delay_its_properties_show_and_the_selection_stays(self):
        # TASK-TRC-150: the delay is the copied tooltip token; virtual time runs the timers
        found = self.run_page(
            "const delay = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--c-graph-tip-delay'));"
            "agnosExplorer.select('RQ-DEM-002'); const tip = document.getElementById('graph-tip'); const node = g.cy().$id('RQ-DEM-001');"
            "const keys = (root) => [...root.querySelectorAll('.properties dt')].map((d) => d.textContent).join('|');"
            "node.emit('mouseover'); setTimeout(() => r('early', tip.hidden), delay / 2);"
            "setTimeout(() => { r('shown', !tip.hidden); r('tipkeys', keys(tip)); r('id', tip.querySelector('.detail-id').textContent);"
            " r('selected', document.querySelector('#detail .detail-id').textContent);"
            " agnosExplorer.select('RQ-DEM-001'); r('detailkeys', keys(document.getElementById('detail')));"
            " node.emit('mouseout'); r('gone', tip.hidden); }, delay + 300);")
        self.assertEqual(("true", "true", "true"), (found["early"], found["shown"], found["gone"]))
        self.assertEqual(("RQ-DEM-001", "RQ-DEM-002"), (found["id"], found["selected"]))
        self.assertTrue(found["tipkeys"])
        self.assertEqual(found["detailkeys"], found["tipkeys"])

    def test_RQ_TRC_163_given_a_node_right_clicked_when_two_hops_chosen_then_only_its_two_hop_neighbourhood_is_shown(self):
        found = self.run_page(
            "agnosExplorer.select('RQ-DEM-001'); agnosExplorer.isolate(); agnosExplorer.widen(); r('two', g.shownIds().sort().join(' '));"
            "agnosExplorer.showAll(); g.cy().$id('RQ-DEM-001').emit('cxttap');"
            "r('menu', [...document.querySelectorAll('#graph-menu [data-menu]')].map((b) => b.dataset.menu).join(' '));"
            "document.querySelector('#graph-menu [data-menu=\"hops:2\"]').click(); r('shown', g.shownIds().sort().join(' '));"
            "r('closed', document.getElementById('graph-menu').hidden);")
        self.assertIn("hops:1", found["menu"].split())
        self.assertIn("hide", found["menu"].split())
        self.assertEqual(found["two"], found["shown"])
        self.assertEqual("true", found["closed"])

    def test_RQ_TRC_163_given_the_background_right_clicked_then_layouts_and_no_node_action_and_escape_closes(self):
        found = self.run_page(
            "g.cy().emit('cxttap'); const menu = document.getElementById('graph-menu');"
            "r('items', [...menu.querySelectorAll('[data-menu]')].map((b) => b.dataset.menu).join(' ')); r('open', !menu.hidden);"
            "document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })); r('closed', menu.hidden);")
        items = found["items"].split()
        self.assertIn("layout:circle", items)
        self.assertFalse([i for i in items if i.startswith("hops:") or i == "hide"])
        self.assertEqual(("true", "true"), (found["open"], found["closed"]))

    def test_RQ_TRC_147_given_a_node_in_the_graph_then_its_colour_is_its_type_token(self):
        found = self.run_page(
            "const want = getComputedStyle(document.documentElement).getPropertyValue('--s-type-rq').trim().toLowerCase();"
            "r('same', g.colour('RQ-DEM-001') === want);")
        self.assertEqual("true", found["same"])


class MenuBarTest(unittest.TestCase):
    """TASK-GXP-002: RQ-GXP-001, RQ-TRC-164 (ADR-GXP-001: DEC-GXP-001), in a headless browser."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        code, out, err = build(cls.tmp.name, "--explorer")
        assert code == 0, err
        cls.page = out.parent / PAGE_NAME

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_page(self, script):
        # RQ-GXP-001: helpers reading the menu bar as the reader sees it
        return results(rendered_dom_after(self.page, "const r = (k, v) => document.documentElement.setAttribute('data-r-' + k,"
                                                     " String(v)); const bar = document.getElementById('menubar');"
                                                     "const title = (n) => bar.querySelector(`[data-menu-title=\"${n}\"]`);"
                                                     "const shown = () => [...bar.querySelectorAll('[role=menu]:not([hidden]) [role=menuitem]')]"
                                                     ".map((i) => i.textContent).join('|');"
                                                     "const key = (k) => document.activeElement.dispatchEvent(new KeyboardEvent('keydown',"
                                                     " { key: k, bubbles: true }));" + script))

    # RQ-GXP-001
    def test_RQ_GXP_001_given_the_explorer_when_file_is_clicked_then_open_import_and_export_are_listed(self):
        found = self.run_page("title('file').click(); r('items', shown());")
        self.assertEqual("Open graph file…|Import saved queries…|Export saved queries…", found["items"])

    # RQ-GXP-001
    def test_RQ_GXP_001_given_an_open_menu_when_right_arrow_then_the_next_opens_and_escape_closes_to_its_title(self):
        found = self.run_page("title('file').click(); title('file').focus(); key('ArrowRight');"
                              "r('open', [...bar.querySelectorAll('[role=menu]:not([hidden])')].map((m) => m.dataset.menu).join('|'));"
                              "key('Escape'); r('closed', bar.querySelectorAll('[role=menu]:not([hidden])').length);"
                              "r('focus', document.activeElement.dataset.menuTitle);")
        self.assertEqual(("view", "0", "view"), (found["open"], found["closed"], found["focus"]))

    # RQ-GXP-001: the menus whose actions exist, in order; Time, Appearance and Dimensions come with their tasks
    # (TASK-GXP-003 added Help)
    def test_RQ_GXP_001_given_the_menu_bar_then_only_delivered_menus_are_shown_and_every_item_has_a_tooltip(self):
        found = self.run_page("r('menus', [...bar.querySelectorAll('[data-menu-title]')].map((t) => t.textContent).join('|'));"
                              "r('untitled', [...bar.querySelectorAll('button')].filter((b) => !(b.title || '').trim())"
                              ".map((b) => b.textContent).join('|'));")
        self.assertEqual("File|View|Filter|Time|Appearance|Help", found["menus"])   # TASK-GXP-004 Appearance, TASK-GXP-005 Time
        self.assertEqual("", found["untitled"])

    # RQ-GXP-001: an item that does not apply to the current view is disabled
    def test_RQ_GXP_001_given_the_nodes_view_then_fit_is_disabled_and_choosing_graph_shows_the_graph_view(self):
        found = self.run_page("agnosExplorer.showView('nodes'); title('view').click();"
                              "const item = (t) => [...bar.querySelectorAll('[role=menuitem]')].find((i) => i.textContent === t);"
                              "r('fit', item('Fit').disabled); item('Graph').click();"
                              "r('view', document.querySelector('.tab[aria-selected=true]').dataset.view);"
                              "r('closed', bar.querySelectorAll('[role=menu]:not([hidden])').length);")
        self.assertEqual(("true", "graph", "0"), (found["fit"], found["view"], found["closed"]))


HELP_TOPICS = "Overview|Graph|Nodes|Relations|Facets and queries|Time|Appearance|Licenses|About"   # RQ-GXP-002: stated, not read


class HelpDialogTest(unittest.TestCase):
    """TASK-GXP-003: RQ-GXP-002, RQ-GXP-003, RQ-GXP-004 (ADR-GXP-001: DEC-GXP-002), in a headless browser and in Python."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        code, out, err = build(cls.tmp.name, "--explorer")
        assert code == 0, err
        cls.page = out.parent / PAGE_NAME

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_page(self, script):
        # RQ-GXP-002: helpers reading the dialog as the reader sees it
        return results(rendered_dom_after(self.page, "const r = (k, v) => document.documentElement.setAttribute('data-r-' + k,"
                                                     " String(v)); const dialog = document.getElementById('help-dialog');"
                                                     "const topic = () => dialog.querySelector('[data-help]:not([hidden])').dataset.title;"
                                                     + script))

    # RQ-GXP-002
    def test_RQ_GXP_002_given_the_nodes_view_when_help_opens_then_the_nodes_topic_is_shown_among_every_topic(self):
        found = self.run_page("agnosExplorer.showView('nodes'); document.getElementById('help-button').click();"
                              "r('open', dialog.open); r('topic', topic());"
                              "r('list', [...document.querySelectorAll('#help-list .help-topic')].map((b) => b.textContent).join('|'));")
        self.assertEqual(("true", "Nodes", HELP_TOPICS), (found["open"], found["topic"], found["list"]))

    # RQ-GXP-002
    def test_RQ_GXP_002_given_the_help_open_when_a_topic_is_clicked_then_it_replaces_the_former_and_close_closes(self):
        found = self.run_page("document.getElementById('help-button').click();"
                              "[...document.querySelectorAll('#help-list .help-topic')].find((b) => b.textContent === 'About').click();"
                              "r('topic', topic()); r('shown', dialog.querySelectorAll('[data-help]:not([hidden])').length);"
                              "document.getElementById('help-close').click(); r('open', dialog.open);")
        self.assertEqual(("About", "1", "false"), (found["topic"], found["shown"], found["open"]))

    # RQ-GXP-002, RQ-GXP-001: the Help menu opens the same dialog on a chosen topic
    def test_RQ_GXP_002_given_the_help_menu_when_licenses_is_chosen_then_the_dialog_shows_licenses(self):
        found = self.run_page("document.querySelector('[data-menu-title=\"help\"]').click();"
                              "[...document.querySelectorAll('#menubar [role=menuitem]')].find((i) => i.textContent === 'Licenses').click();"
                              "r('open', dialog.open); r('topic', topic());")
        self.assertEqual(("true", "Licenses"), (found["open"], found["topic"]))

    # RQ-GXP-003
    def test_RQ_GXP_003_given_the_licenses_topic_then_agnos_and_each_library_have_a_badge_linked_to_spdx(self):
        found = self.run_page("const badges = [...document.querySelectorAll('#licence-list .licence-badge')];"
                              "r('badges', badges.map((b) => b.textContent.replace(/\\s+/g, ' ').trim()).join('|'));"
                              "r('mit', badges.find((b) => b.textContent.includes('Cytoscape')).getAttribute('href'));")
        self.assertEqual("AGNOSAGPL-3.0|Cytoscape.js 3.30.2MIT", found["badges"])
        self.assertEqual("https://spdx.org/licenses/MIT.html", found["mit"])

    def about_of(self, version_text):
        """The About lockup's name of a page rendered while the version file holds version_text, or is absent (None)."""
        import explorer
        version = Path(self.tmp.name) / f"VERSION-{abs(hash(version_text))}"
        if version_text is not None:
            version.write_text(version_text, encoding="utf-8")
        with mock.patch.object(explorer, "VERSION_PATH", version):
            page = explorer.render_page()
        return re.search(r'class="about-wordmark">([^<]*)<', page).group(1).strip(), page

    # RQ-GXP-004
    def test_RQ_GXP_004_given_a_version_file_then_about_reads_agnos_major_minor_the_tagline_and_names_agnos_graph(self):
        name, page = self.about_of("3.12.4\n")
        self.assertEqual("AGNOS v.3.12", name)
        self.assertIn("Agentic efficiency by traceability", page)
        self.assertIn("generated by agnos-graph", page)

    # RQ-GXP-004
    def test_RQ_GXP_004_given_no_version_file_then_about_reads_agnos_alone(self):
        self.assertEqual("AGNOS", self.about_of(None)[0])


CHOSEN_COLOUR = "#00aa00"                                   # RQ-GXP-005: a reader's colour, not a token's
COLOUR_STORE_KEY = "agnos-graph-explorer.relation-colours"  # DEC-GXP-005: stated, not read from the script


@unittest.skipUnless(ONLINE, NEEDS_NETWORK)
class RelationColourTest(unittest.TestCase):
    """TASK-GXP-004: RQ-GXP-005, RQ-TRC-165 (ADR-GXP-001: DEC-GXP-005), in a headless browser with the graph view."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        code, out, err = build(cls.tmp.name, "--explorer")
        assert code == 0, err
        cls.page = out.parent / PAGE_NAME

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_page(self, script):
        # RQ-GXP-005: helpers choosing a colour as the reader does and reading it back from the graph and the legend
        return results(rendered_dom_after(self.page, "const r = (k, v) => document.documentElement.setAttribute('data-r-' + k,"
                                                     " String(v)); agnosExplorer.showView('graph'); const cy = agnosExplorer.graph.cy();"
                                                     "const rgb = (c) => { const d = document.createElement('i'); d.style.color = c;"
                                                     " document.body.appendChild(d); const v = getComputedStyle(d).color; d.remove(); return v; };"
                                                     "const edge = () => rgb(cy.edges('[kind = \"contains\"]')[0].data('colour'));"
                                                     "const line = () => getComputedStyle(document.querySelector("
                                                     "'#graph-legend [data-kind=\"contains\"] .legend-line')).borderTopColor;"
                                                     "const token = rgb(getComputedStyle(document.documentElement).getPropertyValue('--c-graph-edge-contains').trim());"
                                                     "const menuItem = (menu, label) => { document.querySelector(`[data-menu-title=\"${menu}\"]`).click();"
                                                     " [...document.querySelectorAll('#menubar [role=menuitem]')].find((i) => i.textContent === label).click(); };"
                                                     "const pick = (hex) => { const i = document.getElementById('relation-colour'); i.value = hex;"
                                                     " i.dispatchEvent(new Event('input', { bubbles: true })); };" + script))

    # RQ-GXP-005
    def test_RQ_GXP_005_given_the_graph_view_when_contains_is_given_a_colour_then_its_edges_and_legend_line_take_it(self):
        found = self.run_page(f"menuItem('appearance', 'Colour of contains…'); pick('{CHOSEN_COLOUR}');"
                              f"r('edge', edge() === rgb('{CHOSEN_COLOUR}')); r('line', line() === rgb('{CHOSEN_COLOUR}'));")
        self.assertEqual(("true", "true"), (found["edge"], found["line"]))

    # RQ-GXP-005: kept in the browser, read again on load
    def test_RQ_GXP_005_given_a_chosen_colour_when_the_page_loads_again_then_it_is_kept(self):
        found = self.run_page(f"menuItem('appearance', 'Colour of contains…'); pick('{CHOSEN_COLOUR}');"
                              f"r('stored', JSON.parse(localStorage.getItem('{COLOUR_STORE_KEY}')).contains);"
                              "agnosExplorer.appearance.load();"
                              f"r('edge', edge() === rgb('{CHOSEN_COLOUR}')); r('line', line() === rgb('{CHOSEN_COLOUR}'));")
        self.assertEqual((CHOSEN_COLOUR, "true", "true"), (found["stored"], found["edge"], found["line"]))

    # RQ-GXP-005
    def test_RQ_GXP_005_given_a_chosen_colour_when_reset_colours_is_chosen_then_the_token_colour_is_back(self):
        found = self.run_page(f"menuItem('appearance', 'Colour of contains…'); pick('{CHOSEN_COLOUR}');"
                              "menuItem('appearance', 'Reset colours');"
                              f"r('edge', edge() === token); r('line', line() === token);"
                              f"r('stored', localStorage.getItem('{COLOUR_STORE_KEY}'));")
        self.assertEqual(("true", "true", "null"), (found["edge"], found["line"], found["stored"]))

    # RQ-GXP-005: the legend is the other way to the choice
    def test_RQ_GXP_005_given_the_legend_when_a_relation_kind_is_clicked_then_its_colour_is_being_chosen(self):
        found = self.run_page("document.querySelector('#graph-legend [data-kind=\"contains\"] .legend-kind').click();"
                              f"pick('{CHOSEN_COLOUR}'); r('edge', edge() === rgb('{CHOSEN_COLOUR}'));"
                              "r('tip', document.querySelector('#graph-legend [data-kind=\"contains\"] .legend-kind').title);")
        self.assertEqual("true", found["edge"])
        self.assertIn("contains", found["tip"])


# RQ-GXP-006, DEC-GXP-004: a graph whose history dates its nodes: OLD first changed on 2026-07-14, NEW on 2026-11-05, UNDATED
# never changed in the history read; written by the test, so that each date is known
HISTORY_FIRST = "2026-07-14T10:00:00+00:00"
HISTORY_LAST = "2026-11-05T10:00:00+00:00"
OLD, NEW, UNDATED = "RQ-DEM-001", "RQ-DEM-002", "RQ-DEM-003"


def dated_graph():
    """A graph of three requirements with a history of two commits (graph-format.md, history block)."""
    element = lambda i, title: {"id": i, "type": "RQ", "tri": "DEM", "status": "", "title": title, "doc": "FTR-DEM-001.md",
                                "first": 1, "last": 2, "kind": "element"}
    commit = lambda h, date, subject: {"hash": h, "date": date, "subject": subject, "author": 0, "coAuthors": [], "kind": "human"}
    return {"meta": {"generatedAt": GENERATED_AT, "commit": "0123456789"}, "elements": [element(OLD, "Old"), element(NEW, "New"),
            element(UNDATED, "Undated")], "edges": [], "files": [], "sections": [], "links": [], "tasks": {},
            "history": {"commits": [commit("aaaaaaaaaa", HISTORY_FIRST, "first"), commit("bbbbbbbbbb", HISTORY_LAST, "later")],
                        "people": [{"name": "Dev"}], "interventions": {"elements": {OLD: [[0, 3]], NEW: [[1, 4]]}},
                        "limits": {"first": HISTORY_FIRST, "last": HISTORY_LAST}}}


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class TimePeriodTest(unittest.TestCase):
    """TASK-GXP-005: RQ-GXP-006, RQ-GXP-009 (ADR-GXP-001: DEC-GXP-003, DEC-GXP-004), in a headless browser."""

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

    def run_page(self, script, dated=True):
        # RQ-GXP-006: helpers moving a handle as the reader does and reading the node table
        load = f"agnosExplorer.loadText('dated.json', {json.dumps(json.dumps(dated_graph()))});" if dated else ""
        return results(rendered_dom_after(self.page, "const r = (k, v) => document.documentElement.setAttribute('data-r-' + k,"
                                                     " String(v)); const t = agnosExplorer.time;" + load +
                                                     "const handle = (id, iso) => { const i = document.getElementById(id);"
                                                     " i.value = t.dayOf(iso); i.dispatchEvent(new Event('input', { bubbles: true })); };"
                                                     "const rows = () => { agnosExplorer.showView('nodes'); return [...document.querySelectorAll("
                                                     "'#node-table tbody tr')].map((tr) => tr.dataset.key).sort().join('|'); };"
                                                     "const menuItem = (menu, label) => { document.querySelector(`[data-menu-title=\"${menu}\"]`).click();"
                                                     " [...document.querySelectorAll('#menubar [role=menuitem]')].find((i) => i.textContent === label).click(); };"
                                                     + script))

    # RQ-GXP-006
    def test_RQ_GXP_006_given_a_graph_with_history_when_the_period_starts_in_november_then_the_table_lists_only_nodes_dated_in_it(self):
        found = self.run_page("r('bar', document.getElementById('time-bar').hidden); r('all', rows());"
                              "handle('time-start', '2026-11-01'); r('narrow', rows());"
                              "r('label', document.getElementById('time-range').textContent);")
        self.assertEqual("false", found["bar"])
        self.assertEqual("|".join(sorted((OLD, NEW, UNDATED))), found["all"])
        self.assertEqual(NEW, found["narrow"])
        self.assertIn("2026-11-01", found["label"])

    # RQ-GXP-006 (TASK-GXP-009): the track shares the controls' row, after the mode, to save height
    def test_RQ_GXP_006_given_the_time_bar_then_its_track_is_on_the_controls_row_right_of_the_mode(self):
        found = self.run_page("const box = (id) => document.getElementById(id).getBoundingClientRect();"
                              "const track = document.querySelector('.time-track').getBoundingClientRect(); const mode = box('time-window');"
                              "r('row', Math.abs((track.top + track.bottom) / 2 - (mode.top + mode.bottom) / 2) < mode.height / 2);"
                              "r('right', track.left >= mode.right);")
        self.assertEqual(("true", "true"), (found["row"], found["right"]))

    # RQ-GXP-006, DEC-GXP-004
    def test_RQ_GXP_006_given_a_node_without_history_rows_then_it_is_dated_the_history_first_commit(self):
        found = self.run_page(f"r('undated', t.dateOf('{UNDATED}')); r('old', t.dateOf('{OLD}'));"
                              "handle('time-end', '2026-07-14'); r('first-day', rows());")
        self.assertEqual(found["undated"], found["old"])
        self.assertEqual("|".join(sorted((OLD, UNDATED))), found["first-day"])

    # RQ-GXP-006: the Time menu gives back the whole history
    def test_RQ_GXP_006_given_a_narrowed_period_when_whole_history_is_chosen_then_every_node_is_shown_again(self):
        found = self.run_page("handle('time-start', '2026-11-01'); menuItem('time', 'Whole history'); r('rows', rows());")
        self.assertEqual("|".join(sorted((OLD, NEW, UNDATED))), found["rows"])

    # RQ-GXP-009
    def test_RQ_GXP_009_given_a_graph_without_history_then_no_time_bar_and_the_time_menu_is_disabled_naming_history(self):
        found = self.run_page("const title = document.querySelector('[data-menu-title=\"time\"]');"
                              "r('bar', document.getElementById('time-bar').hidden); r('disabled', title.disabled); r('tip', title.title);"
                              "r('rows', rows().split('|').length);", dated=False)
        nodes = len(self.graph["elements"]) + len(self.graph["sections"]) + len(self.graph["files"])
        self.assertEqual(("true", "true"), (found["bar"], found["disabled"]))
        self.assertIn("--history", found["tip"])
        self.assertEqual(str(nodes), found["rows"])


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class TimePlaybackTest(TimePeriodTest):
    """TASK-GXP-006: RQ-GXP-007, RQ-GXP-008 (ADR-GXP-001: DEC-GXP-006). `t.advance(s)` moves the playback as animation frames
    would over s seconds, so that each step is known; one test lets the real animation frames run."""

    # the page and helpers of TimePeriodTest; its own tests are not run again here
    test_RQ_GXP_006_given_a_graph_with_history_when_the_period_starts_in_november_then_the_table_lists_only_nodes_dated_in_it = None
    test_RQ_GXP_006_given_a_node_without_history_rows_then_it_is_dated_the_history_first_commit = None
    test_RQ_GXP_006_given_the_time_bar_then_its_track_is_on_the_controls_row_right_of_the_mode = None
    test_RQ_GXP_006_given_a_narrowed_period_when_whole_history_is_chosen_then_every_node_is_shown_again = None
    test_RQ_GXP_009_given_a_graph_without_history_then_no_time_bar_and_the_time_menu_is_disabled_naming_history = None

    def run_playback(self, script):
        # RQ-GXP-007: the fastest speed of the speed list, then the reader's actions
        return self.run_page("const speed = document.getElementById('time-speed'); speed.value = speed.options[speed.options.length - 1].value;"
                             "speed.dispatchEvent(new Event('change')); const play = document.getElementById('time-play');"
                             "const count = () => agnosExplorer.shownIds().length;" + script)

    # RQ-GXP-007
    def test_RQ_GXP_007_given_a_period_when_play_is_pressed_then_the_shown_count_grows_until_the_end(self):
        found = self.run_playback("play.click(); r('start', count()); r('label', play.textContent); t.advance(1); r('later', count());"
                                  "t.advance(60); r('end', count()); r('stopped', play.textContent);")
        self.assertEqual(("0", "Pause", "2", "3", "Play"), (found["start"], found["label"], found["later"], found["end"], found["stopped"]))

    # RQ-GXP-007
    def test_RQ_GXP_007_given_loop_checked_when_the_cursor_reaches_the_end_then_it_starts_again_from_the_start(self):
        found = self.run_playback("document.getElementById('time-loop').click(); play.click(); t.advance(1); r('before', count());"
                                  "t.advance(4); r('again', count()); r('playing', play.textContent);")
        self.assertEqual("2", found["before"])
        self.assertLess(int(found["again"]), 3)
        self.assertEqual("Pause", found["playing"])

    # RQ-GXP-007
    def test_RQ_GXP_007_given_playback_when_pause_then_the_cursor_stays_and_when_stop_the_whole_period_is_shown(self):
        found = self.run_playback("play.click(); t.advance(1); play.click(); const at = t.cursor(); t.advance(2);"
                                  "r('kept', t.cursor() === at); r('paused', count());"
                                  "document.getElementById('time-stop').click(); r('stopped', count()); r('cursor', t.cursor());")
        self.assertEqual(("true", "2", "3", "null"), (found["kept"], found["paused"], found["stopped"], found["cursor"]))

    # RQ-GXP-008
    def test_RQ_GXP_008_given_the_window_mode_of_7_days_then_only_the_nodes_of_the_7_days_before_the_cursor_are_shown(self):
        found = self.run_playback("const mode = document.getElementById('time-window'); mode.value = '7'; mode.dispatchEvent(new Event('change'));"
                                  "t.setCursor('2026-11-06T00:00:00Z'); r('window', rows());"
                                  "mode.value = '0'; mode.dispatchEvent(new Event('change')); r('cumulative', rows());")
        self.assertEqual(NEW, found["window"])
        self.assertEqual("|".join(sorted((OLD, NEW, UNDATED))), found["cumulative"])

    # RQ-GXP-007, DEC-GXP-006: the animation frames move the cursor by themselves
    def test_RQ_GXP_007_given_play_pressed_when_frames_pass_then_the_cursor_moves_forward(self):
        found = self.run_playback("play.click(); const first = t.cursor();"
                                  "setTimeout(() => { r('moved', t.cursor() === null || t.cursor() > first); }, 1500);")
        self.assertEqual("true", found["moved"])


@unittest.skipUnless(ONLINE, NEEDS_NETWORK)
class TimePeriodGraphTest(unittest.TestCase):
    """TASK-GXP-005: RQ-GXP-006 in the graph view (DEC-GXP-003: the period is one more term of the visibility every view reads)."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        code, out, err = build(cls.tmp.name, "--explorer")
        assert code == 0, err
        cls.page = out.parent / PAGE_NAME

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    # RQ-GXP-006
    def test_RQ_GXP_006_given_the_graph_view_when_the_period_starts_in_november_then_only_its_nodes_are_drawn(self):
        found = results(rendered_dom_after(self.page, "const r = (k, v) => document.documentElement.setAttribute('data-r-' + k, String(v));"
                                                      f"agnosExplorer.loadText('dated.json', {json.dumps(json.dumps(dated_graph()))});"
                                                      "agnosExplorer.showView('graph'); const i = document.getElementById('time-start');"
                                                      "i.value = agnosExplorer.time.dayOf('2026-11-01'); i.dispatchEvent(new Event('input'));"
                                                      "r('shown', agnosExplorer.graph.shownIds().join('|'));"))
        self.assertEqual(NEW, found["shown"])


if __name__ == "__main__":
    unittest.main()
