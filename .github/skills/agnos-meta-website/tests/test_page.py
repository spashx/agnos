"""Tests of agnos-meta-website's page: the template, the content and the placeholder images of the assets (FTR-WEB-001:
RQ-WEB-003, RQ-WEB-007 to RQ-WEB-015; ADR-WEB-001: DEC-WEB-003, DEC-WEB-004, DEC-WEB-005)."""
import importlib.util
import json
import re
import shutil
import struct
import subprocess
import tempfile
import unittest
import zlib
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("agnos_meta_website", SKILL_DIR / "scripts" / "build_site.py")
site = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(site)

TEMPLATE = (site.ASSETS_DIR / site.TEMPLATE).read_text(encoding="utf-8")
VIEWS = ("overview", "graph", "quality", "history", "delivery")
EXAMPLES = ("example-requirement", "example-adr", "example-plan")
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SCREEN_RATIO = 16 / 10
RGB_COLOUR_TYPE = 2
FONT_HOSTS = ("https://fonts.googleapis.com", "https://fonts.gstatic.com")
RAW_VALUE = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(|\b\d*\.?\d+(?:px|em|rem|vw|vh|s|ms)\b|"
                       r"(?:font-weight|opacity|line-height|letter-spacing)\s*:\s*-?(?!(?:0|1)(?![.\d]))\.?\d")
LETTERS = re.compile(r"[A-Za-zÀ-ɏ]")


def build():
    """The page built from the real assets on a small demo, and its errors."""
    root = Path(tempfile.mkdtemp(prefix="agnos-meta-website-page-"))
    try:
        process = root / "agnos-process"
        for folder in site.PROCESS_FOLDERS:
            (process / folder).mkdir(parents=True)
        (process / "1.requirements" / "FTR-BKG-001.md").write_bytes(b"### RQ-BKG-001: One requirement\n" + b"x" * 69014)
        (process / site.INDEX).write_bytes(b"x" * 5843)
        errors = []
        result = site.build_page(site.ASSETS_DIR, root, errors)
        return (result[0] if result else ""), errors
    finally:
        shutil.rmtree(root, ignore_errors=True)


PAGE, ERRORS = build()


class TestTheTemplate(unittest.TestCase):
    """RQ-WEB-003, RQ-WEB-015: a template without text and without raw visual values."""

    def test_given_the_template_then_its_style_holds_no_raw_visual_value(self):
        styles = "".join(re.findall(r"<style>(.*?)</style>", TEMPLATE, re.S))
        attributes = "".join(re.findall(r'\sstyle="([^"]*)"', TEMPLATE))
        self.assertTrue(styles)
        self.assertEqual(RAW_VALUE.findall(styles + attributes), [])

    def test_given_the_template_then_it_holds_no_text(self):
        body = re.sub(r"<!--.*?-->|<style>.*?</style>|<script>.*?</script>|<svg\b.*?</svg>", "", TEMPLATE, flags=re.S)
        text = re.sub(r"<[^>]+>", " ", body)
        self.assertEqual(LETTERS.findall(text), [])
        self.assertIsNone(re.search(r'\s(?:aria-label|alt|title)="', TEMPLATE))


class TestTheBuiltPage(unittest.TestCase):
    """RQ-WEB-007 to RQ-WEB-011, RQ-WEB-013: the page built from the real assets."""

    def test_given_the_assets_then_the_page_builds_without_error(self):
        self.assertEqual(ERRORS, [])

    def test_given_the_page_without_script_then_it_reads_complete_in_english(self):
        self.assertIsNone(site.SLOT.search(PAGE.split("<script>")[0]))
        self.assertIn('<html lang="en">', PAGE)
        self.assertIn("Is what we asked for actually built?", PAGE)

    def test_given_the_page_then_french_holds_every_text(self):
        french = json.loads(re.search(r"const FR = (\{.*?\});\n", PAGE, re.S).group(1))
        self.assertEqual(set(french["html"]), set(site.ANY_SLOT.findall(TEMPLATE)))
        self.assertEqual(set(french["attr"]), {m.group("key") for m in site.ATTRIBUTE_SLOT.finditer(TEMPLATE)})
        self.assertIn("construit ?", french["html"]["stop-overview.question"])

    def test_given_the_header_then_the_lockup_reads_agnos_and_its_tagline(self):
        brand = re.search(r'<a class="brand".*?</a>', PAGE, re.S).group(0)
        self.assertIn('<span class="brand-name" data-i18n="brand.name">AGNOS</span>', brand)
        tagline = "Agentic efficiency by traceability"
        self.assertIn(f'<span class="brand-tagline" data-i18n="brand.tagline">{tagline}</span>', brand)
        self.assertLess(brand.index("brand-name"), brand.index("brand-tagline"))
        css = PAGE.split("</style>")[0]
        self.assertIn(".brand-name{font-weight:var(--s-weight-bold)", css)
        self.assertIn("letter-spacing:var(--s-tracking-tagline);color:var(--s-text-muted)", css)

    def test_given_the_page_then_its_elements_stand_in_order(self):
        markers = ['class="notice"', 'class="bar"', 'id="top"', 'class="chain-card"', 'id="tour"', 'id="overview"',
                   'id="graph"', 'id="quality"', 'id="history"', 'id="delivery"', 'data-i18n="index-card.title"',
                   'data-i18n="design-card.title"', 'id="start"', 'class="steps"', 'class="foot"']
        positions = [PAGE.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("agent identities will be added", PAGE)

    def test_given_the_chain_then_it_shows_both_modes(self):
        chain = re.search(r'<div class="chain" data-mode="mixed">.*?<p class="chain-foot"', PAGE, re.S).group(0)
        loop_in, loop_on = chain.split('<div class="loop loop-on">')
        self.assertLess(loop_in.index("#icon-human"), loop_in.index("#icon-agent"))
        self.assertIn('class="who when-on"><svg class="agent"', loop_in)
        self.assertTrue(loop_on.split("#icon-")[1].startswith("agent"))
        self.assertIn('data-chain="on"', PAGE)
        self.assertIn('.chain[data-mode="on"] .loop-in', PAGE)

    def test_given_the_tour_then_each_screenshot_opens_the_demo(self):
        shots = re.findall(r'<a class="shot-link" href="([^"]+)"[^>]*><img src="([^"]+)"', PAGE)
        self.assertEqual([src for _, src in shots], [f"screens/{view}.png" for view in VIEWS])
        self.assertTrue(all(href.startswith(site.DEMO_LINK) for href, _ in shots))
        self.assertIn(("demo/PERF-CENTER.html#RQ-BKG-003", "screens/graph.png"), shots)
        self.assertEqual(PAGE.count('<span class="shot-open">Open in the demo'), len(VIEWS))
        self.assertIn("@media (hover:none){.shot-open{opacity:1}}", PAGE)

    def test_given_the_page_then_no_request_leaves_it_but_fonts(self):
        sources = re.findall(r'\ssrc="([^"]+)"', PAGE)
        stylesheets = re.findall(r'<link\b[^>]*\shref="([^"]+)"', PAGE)
        self.assertTrue(all("://" not in source for source in sources), sources)
        self.assertTrue(all(href.startswith(FONT_HOSTS) for href in stylesheets), stylesheets)
        self.assertNotIn("<script src", PAGE)

    def test_given_the_page_then_its_script_parses(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("node is not installed: the script's syntax is not checked")
        script = re.search(r"<script>(.*?)</script>", PAGE, re.S).group(1)
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as handle:
            handle.write(script)
        try:
            result = subprocess.run([node, "--check", handle.name], capture_output=True, text=True, check=False)
        finally:
            Path(handle.name).unlink()
        self.assertEqual(result.returncode, 0, result.stderr)


class TestTheCards(unittest.TestCase):
    """RQ-WEB-018: three cards behind the views, the index, the identifiers and the design system."""

    def test_given_the_page_then_three_cards_stand_in_order(self):
        more = re.search(r'<section class="more" id="more">.*?</section>', PAGE, re.S).group(0)
        titles = re.findall(r'<h3 data-i18n="([a-z-]+)\.title">[^<]+</h3>', more)
        self.assertEqual(titles, ["index-card", "id-card", "design-card"])
        card = more.split('data-i18n="id-card.title"')[1].split('data-i18n="design-card.title"')[0]
        snippets = re.findall(r'<pre class="snippet" data-i18n="id-card\.([a-z]+)">(.*?)</pre>', card, re.S)
        self.assertEqual([name for name, _ in snippets], ["requirement", "task", "adr"])
        self.assertIn("RQ-BKG-003", snippets[0][1])
        self.assertIn("<mark>RQ-BKG-003</mark>", snippets[1][1])
        self.assertIn("<mark>RQ-BKG-003</mark>", snippets[2][1])
        self.assertLess(card.index("Primary key"), card.index("Foreign key"))

    def test_given_the_style_then_the_blocks_of_both_cards_stand_top_to_bottom(self):
        css = PAGE.split("</style>")[0]
        self.assertIn(".styles{display:grid;grid-template-columns:minmax(0,1fr)", css)
        self.assertIn(".stack{display:grid;grid-template-columns:minmax(0,1fr)", css)

    def test_given_the_style_then_the_cards_stand_in_three_columns_and_stack_on_phones(self):
        css = PAGE.split("</style>")[0]
        self.assertIn(".cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr))", css)
        wide = css.split("@media (max-width: 980px)")[1].split("}\n@media")[0]
        self.assertNotIn(".cards", wide)
        self.assertIn(".cards{grid-template-columns:minmax(0,1fr)}", css.split("@media (max-width: 640px)")[1])


DEMO_TOKENS = SKILL_DIR.parents[2].parent / "agnos-lightweight-process.demo" / "client" / "design" / "tokens.json"
STYLES = ("primary", "danger")
# site token -> the demo's token whose resolved value it repeats
SAMPLE_TOKENS = {"web-sample-primary-background": "button.primary.background",
                 "web-sample-primary-text": "button.primary.text",
                 "web-sample-danger-background": "button.danger.background",
                 "web-sample-danger-text": "button.danger.text"}


class TestTheDesignSystemCard(unittest.TestCase):
    """RQ-WEB-018: three of Roombook's button styles, each with its tokens, its CSS and a rendered button."""

    def test_given_the_card_then_each_style_shows_its_tokens_its_css_and_a_button(self):
        card = PAGE.split('data-i18n="design-card.title"')[1].split("</section>")[0]
        for style in STYLES:
            tokens = re.search(rf'data-i18n="design-card\.{style}-tokens">(.*?)</pre>', card, re.S).group(1)
            css = re.search(rf'data-i18n="design-card\.{style}-css">(.*?)</pre>', card, re.S).group(1)
            self.assertIn(f"button.{style}.background", tokens)
            self.assertIn(f".button-{style}", css)
            self.assertIn(f"var(--button-{style}-background)", css)
            sample = rf'<span class="sample sample-{style}" data-i18n="design-card\.{style}-button">[^<]+</span>'
            self.assertRegex(card, sample)
        self.assertIn(".sample-primary{background:var(--s-web-sample-primary-background)", PAGE)

    def test_given_the_demo_then_the_sample_colours_are_roombooks(self):
        if not DEMO_TOKENS.is_file():
            self.skipTest(f"{DEMO_TOKENS} is absent: the sample colours are not compared")
        demo = json.loads(DEMO_TOKENS.read_text(encoding="utf-8"))
        flat = {**demo["global"], **demo["semantic"], **demo["component"]}

        def resolve(name):
            value = flat[name]
            return resolve(value[1:-1]) if value.startswith("{") else value

        errors = []
        tokens = site.load_design_system(errors)
        for site_token, demo_token in SAMPLE_TOKENS.items():
            self.assertEqual(site.theme_values(tokens, site_token, errors)[0].lower(), resolve(demo_token).lower(),
                             site_token)
        self.assertEqual(errors, [])


class TestTheIndexAndGraph(unittest.TestCase):
    """RQ-WEB-005, RQ-WEB-018: the index's measured speed, and the identifiers drawn as a small graph."""

    def test_given_the_index_card_then_it_states_a_measured_speed_per_hundred_artifacts(self):
        text = re.search(r'data-i18n="index-card.text">(.*?)</p>', PAGE, re.S).group(1)
        self.assertRegex(text, r"deterministic skill.*\d\.\d s per 100 artifacts")

    def test_given_the_identifiers_card_then_a_graph_links_task_and_adr_to_the_requirement(self):
        card = PAGE.split('data-i18n="id-card.title"')[1].split('data-i18n="design-card.title"')[0]
        graph = re.search(r'<svg class="id-graph".*?</svg>', card, re.S).group(0)
        self.assertEqual(re.findall(r'class="node node-([a-z]+)"', graph), ["task", "rq", "adr", "file"])
        self.assertEqual(len(re.findall(r'class="edge"[^>]*marker-end="url\(#id-arrow\)"', graph)), 3)
        self.assertIn(">No double booking</text>", graph)
        self.assertIn(">overlap_rule.py</text>", graph)
        self.assertIn(".node-file{fill:var(--s-type-file)}", PAGE)
        code = re.search(r'<pre class="excerpt" data-i18n="id-card.code">(.*?)</pre>', card, re.S).group(1)
        self.assertIn("class OverlapRule:", code)
        self.assertEqual(code.count("<mark>RQ-BKG-003</mark>"), 3)
        self.assertIn(".node-rq{fill:var(--s-type-rq)}", PAGE)

    def test_given_the_design_system_card_then_it_shows_two_styles(self):
        card = PAGE.split('data-i18n="design-card.title"')[1].split("</section>")[0]
        self.assertEqual(re.findall(r'class="sample sample-([a-z]+)"', card), list(STYLES))


class TestTheExamples(unittest.TestCase):
    """RQ-WEB-017: three examples under the Overview stop, enlarged on click."""

    def test_given_the_overview_stop_then_three_examples_follow_its_screenshot(self):
        stop = re.search(r'<section class="stop" id="overview">.*?</section>', PAGE, re.S).group(0)
        examples = re.findall(r'<button type="button" class="example-open"[^>]*><img src="([^"]+)" alt="([^"]+)"', stop)
        self.assertEqual([src for src, _ in examples], [f"screens/{name}.png" for name in EXAMPLES])
        self.assertTrue(all(alt for _, alt in examples))
        self.assertLess(stop.index("shot-link"), stop.index("example-open"))
        captions = re.findall(r'<figcaption data-i18n="examples\.[a-z-]+">([^<]+)</figcaption>', stop)
        self.assertEqual(len(captions), len(EXAMPLES))

    def test_given_the_style_then_the_examples_stand_side_by_side_and_stack_on_phones(self):
        css = PAGE.split("</style>")[0]
        self.assertIn(".examples{grid-column:1/-1;display:grid;grid-template-columns:repeat(3,minmax(0,1fr))", css)
        narrow = css.split("@media (max-width: 640px)")[1]
        self.assertIn(".examples{grid-template-columns:minmax(0,1fr)}", narrow)

    def test_given_the_page_then_a_dialog_enlarges_an_example_and_closes(self):
        self.assertRegex(PAGE, r'<dialog class="zoom"[^>]*aria-label="[^"]+"')
        self.assertRegex(PAGE, r'<button type="button" class="zoom-close"[^>]*aria-label="[^"]+"')
        script = re.search(r"<script>(.*?)</script>", PAGE, re.S).group(1)
        for part in ("showModal()", "zoom.close()", "event.target === zoom", '"close"', "opener.focus()"):
            self.assertIn(part, script)


def png_pixels(path):
    """(width, height, colour type, the decompressed rows) of a PNG."""
    data = path.read_bytes()
    assert data.startswith(PNG_SIGNATURE)
    position, idat, header = len(PNG_SIGNATURE), b"", None
    while position < len(data):
        length, kind = struct.unpack(">I4s", data[position:position + 8])
        body = data[position + 8:position + 8 + length]
        if kind == b"IHDR":
            header = struct.unpack(">IIBBBBB", body)
        elif kind == b"IDAT":
            idat += body
        position += 12 + length
    return header[0], header[1], header[3], zlib.decompress(idat)


class TestThePlaceholders(unittest.TestCase):
    """RQ-WEB-012: one single-colour PNG per view, at 16:10."""

    def test_given_the_assets_then_each_view_has_a_single_colour_placeholder(self):
        for view in VIEWS + EXAMPLES:
            width, height, colour_type, rows = png_pixels(site.ASSETS_DIR / "screens" / f"{view}.png")
            self.assertAlmostEqual(width / height, SCREEN_RATIO, msg=view)
            self.assertEqual(colour_type, RGB_COLOUR_TYPE, view)
            row = 1 + 3 * width
            first = rows[1:4]
            self.assertTrue(all(rows[i * row + 1:(i + 1) * row] == first * width for i in range(height)), view)


if __name__ == "__main__":
    unittest.main()
