"""Tests of agnos-meta-website's page: the template, the content and the placeholder images of the assets (FTR-WEB-001:
RQ-WEB-003, RQ-WEB-007 to RQ-WEB-015, RQ-WEB-020; ADR-WEB-001: DEC-WEB-003, DEC-WEB-004, DEC-WEB-005, DEC-WEB-008)."""
import importlib.util
import json
import re
import shutil
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("agnos_meta_website", SKILL_DIR / "scripts" / "build_site.py")
site = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(site)

TEMPLATE = (site.ASSETS_DIR / site.TEMPLATE).read_text(encoding="utf-8")
VIEWS = ("matrix", "graph", "history", "delivery", "quality")
EXAMPLES = ("example-requirement", "example-adr", "example-plan")
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SCREEN_SIZE = (1920, 1080)   # RQ-WEB-012, RQ-WEB-019: the capture ratio, at a size the build accepts
FONT_HOSTS = ("https://fonts.googleapis.com", "https://fonts.gstatic.com")
RAW_VALUE = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(|\b\d*\.?\d+(?:px|em|rem|vw|vh|s|ms)\b|"
                       r"(?:font-weight|opacity|line-height|letter-spacing)\s*:\s*-?(?!(?:0|1)(?![.\d]))\.?\d")
LETTERS = re.compile(r"[A-Za-zÀ-ɏ]")


def build():
    """The page built from the real assets, and its errors."""
    errors = []
    result = site.build_page(site.ASSETS_DIR, errors)
    return (result[0] if result else ""), errors


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
        self.assertIn("Was everything we asked for actually built?", PAGE)   # the owner's wording of 2026-11-14 (TASK-WEB-027)

    def test_given_the_page_then_french_holds_every_text(self):
        french = json.loads(re.search(r"const FR = (\{.*?\});\n", PAGE, re.S).group(1))
        self.assertEqual(set(french["html"]), set(site.ANY_SLOT.findall(TEMPLATE)))
        self.assertEqual(set(french["attr"]), {m.group("key") for m in site.ATTRIBUTE_SLOT.finditer(TEMPLATE)})
        self.assertIn("construit ?", french["html"]["matrix.question"])

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
        markers = ['class="notice"', 'class="bar"', 'id="top"', 'class="chain-card"', 'id="tour"', 'id="matrix"',
                   'id="graph"', 'id="history"', 'id="delivery"', 'id="quality"', 'data-i18n="index-card.title"',
                   'data-i18n="design-card.title"', 'id="start"', 'class="steps"', 'class="foot"']
        positions = [PAGE.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("can be traced through a requirement view", PAGE)

    # RQ-WEB-001: the History stop states its traceability in its text, without a separate note
    def test_given_the_history_stop_then_it_holds_no_note(self):
        self.assertNotIn('class="note"', PAGE)
        self.assertNotIn("history.note", PAGE)

    def test_given_the_chain_then_it_shows_both_modes(self):
        chain = re.search(r'<div class="chain" data-mode="mixed">.*?<p class="chain-foot"', PAGE, re.S).group(0)
        loop_in, loop_on = chain.split('<div class="loop loop-on">')
        self.assertLess(loop_in.index("#icon-human"), loop_in.index("#icon-agent"))
        self.assertIn('class="who when-on"><svg class="agent"', loop_in)
        self.assertTrue(loop_on.split("#icon-")[1].startswith("agent"))
        self.assertIn('data-chain="on"', PAGE)
        self.assertIn('.chain[data-mode="on"] .loop-in', PAGE)

    def test_given_the_tour_then_each_screenshot_enlarges_on_click(self):
        """RQ-WEB-011: each tour screenshot is a zoom button, as the examples, and links no more to the demo."""
        shots = re.findall(r'<figure class="shot"><button type="button" class="example-open"[^>]*><img src="([^"]+)" alt="([^"]+)"', PAGE)
        self.assertEqual([src for src, _ in shots], [f"screens/{view}.png" for view in VIEWS])
        self.assertTrue(all(alt for _, alt in shots))
        self.assertNotIn("shot-link", PAGE)
        self.assertNotIn("shot-open", PAGE)
        self.assertNotIn("Open in the demo", PAGE)
        self.assertNotIn('href="demo/PERF-CENTER.html#', PAGE)

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
    """RQ-WEB-018 (RQ-WEB-005 deprecated): the index card without measures, and the identifiers drawn as a graph."""

    def test_given_the_index_card_then_it_holds_its_texts_and_no_measure(self):
        # Given the built page, When its index card is read, Then it holds title, text, excerpt and caption only
        card = PAGE.split('data-i18n="index-card.title"')[1].split('data-i18n="id-card.title"')[0]
        self.assertEqual(re.findall(r'data-i18n="(index-card\.[a-z-]+)"', card),
                         ["index-card.text", "index-card.excerpt", "index-card.caption"])
        self.assertNotIn("bar-row", PAGE)
        self.assertNotIn("{{", PAGE)
        # And neither language states a figure in its text or caption
        french = json.loads(re.search(r"const FR = (\{.*?\});\n", PAGE, re.S).group(1))["html"]
        for key in ("index-card.text", "index-card.caption"):
            english = re.search(rf'data-i18n="{re.escape(key)}">(.*?)</p>', PAGE, re.S).group(1)
            for text in (english, french[key]):
                self.assertIsNone(re.search(r"\d|KB|Ko", text), key)

    def test_given_the_identifiers_card_then_a_graph_links_task_and_adr_to_the_requirement(self):
        card = PAGE.split('data-i18n="id-card.title"')[1].split('data-i18n="design-card.title"')[0]
        graph = re.search(r'<svg class="id-graph".*?</svg>', card, re.S).group(0)
        self.assertEqual(re.findall(r'class="node node-([a-z]+)"', graph), ["task", "rq", "adr", "file"])
        self.assertEqual(len(re.findall(r'class="edge"[^>]*marker-end="url\(#id-arrow\)"', graph)), 3)
        self.assertIn(">Double booking rejection</text>", graph)
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
    """RQ-WEB-017: three examples under the Matrix stop, enlarged on click."""

    def test_given_the_matrix_stop_then_three_examples_follow_its_screenshot(self):
        stop = re.search(r'<section class="stop" id="matrix">.*?</section>', PAGE, re.S).group(0)
        examples = re.findall(r'<figure class="example"><button type="button" class="example-open"[^>]*><img src="([^"]+)" alt="([^"]+)"', stop)
        self.assertEqual([src for src, _ in examples], [f"screens/{name}.png" for name in EXAMPLES])
        self.assertTrue(all(alt for _, alt in examples))
        self.assertLess(stop.index('class="shot"'), stop.index('class="example"'))
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


def png_size(path):
    """(width, height) of a PNG, from its IHDR header. RQ-WEB-012"""
    data = path.read_bytes()
    assert data.startswith(PNG_SIGNATURE)
    return struct.unpack(">II", data[len(PNG_SIGNATURE) + 8:len(PNG_SIGNATURE) + 16])


class TestTheStartSteps(unittest.TestCase):
    """RQ-WEB-009, RQ-WEB-015 (TASK-WEB-018): each start step shows an example command in a console style."""

    def test_given_the_steps_then_each_shows_a_console_command_in_both_languages(self):
        # Given the built page, When its three step cards are read, Then each holds a non-empty console block
        steps = PAGE.split('class="steps"')[1].split('class="foot"')[0]
        french = json.loads(re.search(r"const FR = (\{.*?\});\n", PAGE, re.S).group(1))["html"]
        for number in (1, 2, 3):
            key = f"start.step{number}-command"
            english = re.search(rf'<pre class="console" data-i18n="{re.escape(key)}">(.*?)</pre>', steps, re.S)
            self.assertIsNotNone(english, key)
            self.assertTrue(english.group(1).strip(), key)
            self.assertTrue(french[key].strip(), key)
        self.assertIn("agnos@agnos-marketplace", steps)
        self.assertIn("Démarrez", french["start.step3-command"])

    def test_given_the_console_style_then_it_uses_tokens_only(self):
        # Given the template's style, When the console rule is read, Then it consumes the console token and no raw value
        rule = re.search(r"\.console\{([^}]*)\}", TEMPLATE).group(1)
        self.assertIn("var(--s-web-console)", rule)
        self.assertEqual(RAW_VALUE.findall(rule), [])


MARKETPLACE_LABEL = "AGNOS marketplace"     # RQ-WEB-020: the label of both marketplace buttons
# RQ-DOC-007 / DEC-DOC-001: site.json lists names, the repository's links.json holds their addresses
LISTED_LINKS = json.loads((site.ASSETS_DIR / "site.json").read_text(encoding="utf-8"))["links"]
REPOSITORY_LINKS = json.loads(site.LINKS_FILE.read_text(encoding="utf-8"))["links"]
SITE_LINKS = {name: REPOSITORY_LINKS[name] for name in LISTED_LINKS}


def anchors_to(html, address):
    """The opening tags of the anchors of html that lead to address. RQ-WEB-020"""
    return re.findall(rf'<a [^>]*href="{re.escape(address)}"[^>]*>', html)


class TestTheMarketplaceLinks(unittest.TestCase):
    """RQ-WEB-020, RQ-WEB-009 / DEC-WEB-008 (TASK-WEB-026): the marketplace and getting-started links, declared once."""

    def test_given_site_json_then_it_lists_the_marketplace_and_its_getting_started_section(self):
        # Given the assets' site.json and the links.json it reads (RQ-DOC-007), Then both names resolve to the
        # addresses of the owner's request of 2026-11-18
        self.assertEqual(LISTED_LINKS, ["marketplace", "getting-started"])
        self.assertEqual(SITE_LINKS["marketplace"], "https://github.com/spashx/agnos-marketplace")
        self.assertEqual(SITE_LINKS["getting-started"], "https://github.com/spashx/agnos-marketplace#getting-started")

    def test_given_the_header_then_a_ghost_marketplace_button_follows_the_demo_button(self):
        # Given the header, Then its last two links are the demo button and the marketplace ghost button
        header = PAGE.split('<header class="bar">')[1].split("</header>")[0]
        buttons = re.findall(r'<a class="([^"]*\bbtn\b[^"]*)" href="([^"]+)"[^>]*>([^<]*)</a>', header)
        self.assertEqual([href for _, href, _ in buttons], [site.DEMO_LINK, SITE_LINKS["marketplace"]])
        classes, _, label = buttons[1]
        self.assertIn("btn-ghost", classes.split())
        self.assertEqual(label, MARKETPLACE_LABEL)

    def test_given_the_install_step_then_its_command_and_button_lead_to_the_marketplace(self):
        # Given the first start step, Then its command adds the marketplace address And a button of the same label follows it
        step = PAGE.split('class="steps"')[1].split("</div>")[0]
        self.assertIn(f"claude plugin marketplace add {SITE_LINKS['marketplace']}", step)
        button = re.search(r'<a class="[^"]*\bbtn\b[^"]*" href="([^"]+)"[^>]*>([^<]*)</a>', step.split("</pre>")[1])
        self.assertEqual(button.groups(), (SITE_LINKS["marketplace"], MARKETPLACE_LABEL))

    def test_given_the_footer_then_the_developer_link_leads_to_getting_started(self):
        # Given the footer, Then the developer documentation is a link to the getting-started section, without a TODO
        foot = PAGE.split('class="foot"')[1].split("</div>")[0]
        self.assertEqual(len(anchors_to(foot, SITE_LINKS["getting-started"])), 1)
        self.assertNotIn("TODO", PAGE)

    def test_given_the_french_page_then_both_buttons_keep_the_label_and_the_command_the_address(self):
        # Given the French dictionary, Then the button label is the same And the install command holds the address
        french = json.loads(re.search(r"const FR = (\{.*?\});\n", PAGE, re.S).group(1))["html"]
        self.assertEqual(french["marketplace.label"], MARKETPLACE_LABEL)
        self.assertIn(SITE_LINKS["marketplace"], french["start.step1-command"])
        self.assertNotIn("TODO", json.dumps(french))

    def test_given_the_assets_then_each_address_is_written_in_links_json_only(self):
        # Given the template and both languages, Then none holds an address of links.json nor the <marketplace> placeholder
        sources = [site.ASSETS_DIR / site.TEMPLATE] + [site.ASSETS_DIR / site.CONTENT / f"{lang}.md" for lang in site.LANGUAGES]
        for source in sources:
            text = source.read_text(encoding="utf-8")
            for address in SITE_LINKS.values():
                self.assertNotIn(address, text, source.name)
            self.assertNotIn("<marketplace>", text, source.name)


class TestTheChainPerformanceCenter(unittest.TestCase):
    """RQ-WEB-010, RQ-WEB-015 (TASK-WEB-019): the chain's Performance Center row, without the demo's name, its text from the icon's edge."""

    def test_given_the_chain_then_its_performance_center_row_has_no_demo_name_and_a_full_width_text(self):
        # Given the built page, When the chain's Performance Center row is read
        row = re.search(r'<div class="chain-pc">(.*?)</div>', PAGE, re.S).group(1)
        # Then it names no demo, And its text is a direct child spanning the row
        self.assertNotIn("measure-id", row)
        self.assertNotIn("Roombook", row)
        self.assertTrue(row.rstrip().endswith('</span>'))
        self.assertRegex(row, r'</span><span class="t" data-i18n="chain.measure-text">[^<]+</span>$')
        self.assertIn(".chain-pc .t{grid-column:1 / -1", TEMPLATE)


class TestTheFrames(unittest.TestCase):
    """RQ-WEB-019, DEC-WEB-007: every image framed at the capture ratio through a design-system token."""

    def test_given_the_template_when_framing_images_then_the_ratio_is_the_token_and_no_16_10_remains(self):
        """RQ-WEB-019, DEC-WEB-007."""
        # Given the template
        # When looking for the aspect ratio of the frames
        ratios = re.findall(r"aspect-ratio:([^;}]+)", TEMPLATE)
        # Then each one is the token, and 16/10 is gone
        self.assertTrue(ratios)
        self.assertEqual(set(ratios), {"var(--s-web-ratio-shot)"})
        self.assertNotIn("16/10", TEMPLATE)
        self.assertIn("--s-web-ratio-shot: 16 / 9;", PAGE)


class TestTheScreens(unittest.TestCase):
    """RQ-WEB-012, RQ-WEB-019: one PNG per view and per example, at 1920x1080 (the capture ratio)."""

    def test_given_the_assets_then_each_view_has_its_image_at_the_capture_size(self):
        for view in VIEWS + EXAMPLES:
            # Given the image of a view or an example, Then it is a PNG at the capture size
            self.assertEqual(png_size(site.ASSETS_DIR / "screens" / f"{view}.png"), SCREEN_SIZE, view)


if __name__ == "__main__":
    unittest.main()
