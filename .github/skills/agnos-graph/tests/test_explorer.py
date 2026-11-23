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

    def test_RQ_TRC_147_given_a_node_in_the_graph_then_its_colour_is_its_type_token(self):
        found = self.run_page(
            "const want = getComputedStyle(document.documentElement).getPropertyValue('--s-type-rq').trim().toLowerCase();"
            "r('same', g.colour('RQ-DEM-001') === want);")
        self.assertEqual("true", found["same"])


if __name__ == "__main__":
    unittest.main()
