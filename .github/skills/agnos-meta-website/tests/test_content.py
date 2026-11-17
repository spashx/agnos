"""Tests of agnos-meta-website's content: reading en.md and fr.md, their checks against the template, a
variable left in a field, the declared links and French typography (FTR-WEB-001: RQ-WEB-003, RQ-WEB-004, RQ-WEB-006,
RQ-WEB-016, RQ-WEB-020; ADR-WEB-001: DEC-WEB-001, DEC-WEB-003, DEC-WEB-008)."""
import importlib.util
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_DIR / "scripts" / "build_site.py"
_spec = importlib.util.spec_from_file_location("agnos_meta_website", SCRIPT)
site = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(site)

NBSP = " "
NARROW_NBSP = " "
PNG = b"\x89PNG\r\n\x1a\n"
LINK_NAME = "site"                          # RQ-WEB-020: the fixture's declared link
LINK_ADDRESS = "https://example.org/site"
TEMPLATE = """<!doctype html><html lang="en"><head><title data-i18n="page.title"></title>
<meta name="description" data-i18n-attr="content=page.description"></head><body>
<p data-i18n="hero.text"></p><ul data-i18n="hero.tags"></ul><figure data-i18n="hero.shot"></figure>
<pre data-i18n="hero.excerpt"></pre><p data-i18n="hero.figure"></p>
<script>const FR = /*@FR@*/{};</script></body></html>"""
EN = """<!-- a comment, ignored -->
## page

### title
The title

### description
A *described* page

## hero

### text
First line\\
second `code` with **strong** and [a link](https://example.org)

### tags
- One
- Two

### shot
![The view](screens/view.png)

### excerpt
```
@agnos-process/one.md
RQ-BKG-003|42-56||No double booking
```

### figure
The index, an excerpt
"""
FR = """## page

### title
Le titre

### description
Une page *décrite*

## hero

### text
Est-ce construit ? Oui : l'index ; enfin !

### tags
- Un
- Deux

### shot
![La vue](screens/view.png)

### excerpt
```
@agnos-process/one.md
RQ-BKG-003|42-56||No double booking
```

### figure
The index, an excerpt
"""


class Fixture(unittest.TestCase):
    """A temporary assets folder; each test changes one of its files."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="agnos-meta-website-"))
        self.assets = self.root / "assets"
        (self.assets / "content").mkdir(parents=True)
        (self.assets / "screens").mkdir()
        (self.assets / "template.html").write_text(TEMPLATE, encoding="utf-8")
        (self.assets / "content" / "en.md").write_text(EN, encoding="utf-8")
        (self.assets / "content" / "fr.md").write_text(FR, encoding="utf-8")
        (self.assets / "screens" / "view.png").write_bytes(PNG)
        self.write_links({LINK_NAME: LINK_ADDRESS})

    def write_links(self, links):
        """The fixture's site.json, declaring the given links. RQ-WEB-020"""
        (self.assets / "site.json").write_text(json.dumps({"links": links}), encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def write(self, name, text):
        (self.assets / "content" / name).write_text(text, encoding="utf-8")

    def page(self):
        """(page, errors) of a build of the fixture."""
        errors = []
        result = site.build_page(self.assets, errors, tokens={tier: {} for tier in site.TIERS})
        return (result[0] if result else None), errors

    def french(self, page):
        """The French dictionary the page holds."""
        return json.loads(re.search(r"const FR = (\{.*?\});</script>", page, re.S).group(1))


class TestContentInTheAssets(Fixture):
    """RQ-WEB-003: the text from en.md and fr.md, the images from screens/, a template without text."""

    def test_given_the_fixture_when_built_then_english_fills_the_markup(self):
        page, errors = self.page()
        self.assertEqual(errors, [])
        self.assertIn('<title data-i18n="page.title">The title</title>', page)
        self.assertIn('content="A described page"', page)
        self.assertIn("First line<br>second <code>code</code> with <strong>strong</strong> and "
                      '<a href="https://example.org">a link</a>', page)
        self.assertIn("<li>One</li><li>Two</li>", page)
        self.assertNotIn("a comment", page)

    def test_given_a_tour_image_when_built_then_it_links_nowhere(self):
        """RQ-WEB-011: a screenshot of the content is an image, enlarged by the page, not a link."""
        page, _ = self.page()
        self.assertNotIn('href="demo/PERF-CENTER.html#RQ-BKG-003"', page)
        self.assertIn('<img src="screens/view.png" alt="The view"', page)

    def test_given_a_code_block_with_marks_then_they_are_highlighted(self):
        errors = []
        self.assertEqual(site.render("x.y", ["```", "refs: ==RQ-BKG-003== <done>", "```"], "en", errors),
                         (site.KIND_CODE, "refs: <mark>RQ-BKG-003</mark> &lt;done&gt;"))

    def test_given_a_plain_image_then_it_is_an_image_without_link(self):
        errors = []
        self.assertEqual(site.render("x.y", ["![An example](screens/view.png)"], "en", errors),
                         (site.KIND_IMAGE, ("An example", "screens/view.png")))
        self.assertEqual(errors, [])

    def test_given_an_index_excerpt_when_built_then_its_path_lines_are_dimmed(self):
        page, _ = self.page()
        self.assertIn("<span>@agnos-process/one.md</span>\nRQ-BKG-003|42-56||No double booking", page)

    def test_given_a_word_changed_in_french_when_built_then_only_the_french_changes(self):
        before, _ = self.page()
        self.write("fr.md", FR.replace("Le titre", "Un autre titre"))
        after, errors = self.page()
        self.assertEqual(errors, [])
        self.assertEqual(self.french(after)["html"]["page.title"], "Un autre titre")
        self.assertEqual(before.split("const FR")[0], after.split("const FR")[0])

    def test_given_the_page_then_french_holds_every_element_and_attribute(self):
        page, _ = self.page()
        french = self.french(page)
        self.assertEqual(french["attr"], {"page.description": "Une page décrite"})
        self.assertEqual(set(french["html"]), {"page.title", "hero.text", "hero.tags", "hero.shot", "hero.excerpt",
                                               "hero.figure"})


class TestContentChecks(Fixture):
    """RQ-WEB-004: each fault is reported with its file and its field, and nothing is built."""

    def assertFault(self, expected):
        page, errors = self.page()
        self.assertIsNone(page)
        self.assertTrue(any(expected in error for error in errors), errors)

    def test_given_a_field_in_one_language_only(self):
        self.write("fr.md", FR.replace("### tags\n- Un\n- Deux\n", ""))
        self.assertFault("fr.md: hero.tags is missing")

    def test_given_a_field_defined_twice(self):
        self.write("en.md", EN + "\n### figure\nAgain\n")
        self.assertFault("en.md:")
        self.assertFault("hero.figure is defined twice")

    def test_given_text_outside_a_field(self):
        self.write("en.md", "Loose text\n" + EN)
        self.assertFault("en.md:1: text outside a field")

    def test_given_a_field_mixing_a_list_and_a_paragraph(self):
        self.write("en.md", EN.replace("- One\n- Two", "- One\nTwo"))
        self.assertFault("en.md: hero.tags mixes a list and a paragraph")

    def test_given_a_field_of_two_paragraphs(self):
        self.write("en.md", EN.replace("A *described* page", "One\n\nTwo"))
        self.assertFault("en.md: page.description holds more than one paragraph")

    def test_given_a_field_unknown_to_the_template(self):
        self.write("en.md", EN + "\n### extra\nMore\n")
        self.write("fr.md", FR + "\n### extra\nPlus\n")
        self.assertFault("content: hero.extra is used by no element of the template")

    def test_given_a_template_element_without_a_field(self):
        extra = '<p data-i18n="hero.figure"></p><p data-i18n="hero.none"></p>'
        template = TEMPLATE.replace('<p data-i18n="hero.figure"></p>', extra)
        (self.assets / "template.html").write_text(template, encoding="utf-8")
        self.assertFault("template: hero.none has no text in the content")

    def test_given_a_template_element_holding_text(self):
        (self.assets / "template.html").write_text(TEMPLATE.replace('"hero.text"></p>', '"hero.text">Text</p>'),
                                                   encoding="utf-8")
        self.assertFault("template: the element of hero.text must be empty")

    def test_given_a_missing_image(self):
        (self.assets / "screens" / "view.png").unlink()
        self.assertFault("en.md: hero.shot: screens/view.png does not exist")


class TestVariableLeftInAField(Fixture):
    """RQ-WEB-004 (RQ-WEB-005 deprecated): the content holds no variable; one left in a field is reported."""

    def test_given_a_field_without_variable_then_its_text_is_kept(self):
        # Given the fixture's figure field, When built, Then its text is in both languages as written
        page, errors = self.page()
        self.assertEqual(errors, [])
        self.assertIn(">The index, an excerpt</p>", page)
        self.assertEqual(self.french(page)["html"]["hero.figure"], "The index, an excerpt")

    def test_given_a_variable_left_in_a_field_then_it_is_reported(self):
        # Given a former measure left in a field, When built, Then the error names the file, the field and the variable
        self.write("en.md", EN.replace("The index, an excerpt", "Ratio {{index.ratio}}"))
        page, errors = self.page()
        self.assertIsNone(page)
        self.assertIn("en.md: hero.figure: unknown variable {{index.ratio}}", errors)


class TestDeclaredLinks(Fixture):
    """RQ-WEB-020, RQ-WEB-004 / DEC-WEB-008: the addresses of assets/site.json, in the fields and the template."""

    def test_given_a_declared_link_in_a_field_then_both_languages_hold_its_address(self):
        # Given {{link.site}} in a paragraph of each language, When built, Then each holds the declared address
        self.write("en.md", EN.replace("The index, an excerpt", "See {{link.site}}"))
        self.write("fr.md", FR.replace("The index, an excerpt", "Voir {{link.site}}"))
        page, errors = self.page()
        self.assertEqual(errors, [])
        self.assertIn(f">See {LINK_ADDRESS}</p>", page)
        self.assertEqual(self.french(page)["html"]["hero.figure"], f"Voir {LINK_ADDRESS}")

    def test_given_a_declared_link_in_a_code_block_then_it_holds_its_address(self):
        # Given {{link.site}} in a console excerpt, When built, Then the excerpt holds the address
        self.write("en.md", EN.replace("RQ-BKG-003|42-56||No double booking", "add {{link.site}}"))
        page, errors = self.page()
        self.assertEqual(errors, [])
        self.assertIn(f"add {LINK_ADDRESS}", page)

    def test_given_a_declared_link_as_a_link_address_then_the_anchor_leads_to_it(self):
        # Given [a link]({{link.site}}), When built, Then the anchor's href is the address
        self.write("en.md", EN.replace("(https://example.org)", "({{link.site}})"))
        page, errors = self.page()
        self.assertEqual(errors, [])
        self.assertIn(f'<a href="{LINK_ADDRESS}">a link</a>', page)

    def test_given_an_undeclared_link_in_a_field_then_it_is_reported(self):
        # Given {{link.unknown}} in a field, When built, Then the error names the file, the field and the variable
        self.write("en.md", EN.replace("The index, an excerpt", "See {{link.unknown}}"))
        page, errors = self.page()
        self.assertIsNone(page)
        self.assertIn("en.md: hero.figure: unknown variable {{link.unknown}}", errors)

    def test_given_a_declared_link_in_the_template_then_it_holds_its_address(self):
        # Given {{v:link.site}} in the template, When built, Then the attribute holds the address
        template = TEMPLATE.replace("<body>", '<body><a href="{{v:link.site}}"></a>')
        (self.assets / "template.html").write_text(template, encoding="utf-8")
        page, errors = self.page()
        self.assertEqual(errors, [])
        self.assertIn(f'<a href="{LINK_ADDRESS}"></a>', page)

    def test_given_an_undeclared_link_in_the_template_then_it_is_reported(self):
        # Given {{v:link.unknown}} in the template, When built, Then the error names it
        template = TEMPLATE.replace("<body>", '<body><a href="{{v:link.unknown}}"></a>')
        (self.assets / "template.html").write_text(template, encoding="utf-8")
        page, errors = self.page()
        self.assertIsNone(page)
        self.assertIn("template: unknown value {{v:link.unknown}}", errors)

    def test_given_site_json_declaring_the_computed_demo_link_then_it_is_reported(self):
        # Given site.json declaring demo, which the build computes, When built, Then the error names it
        self.write_links({LINK_NAME: LINK_ADDRESS, "demo": "https://example.org/demo"})
        page, errors = self.page()
        self.assertIsNone(page)
        self.assertIn("site.json: link demo is computed by the build", errors)

    def test_given_no_site_json_then_it_is_reported(self):
        # Given the assets without site.json, When built, Then the error names the file
        (self.assets / "site.json").unlink()
        page, errors = self.page()
        self.assertIsNone(page)
        self.assertTrue(any(error.startswith("site.json:") for error in errors), errors)


class TestFrenchTypography(Fixture):
    """RQ-WEB-006: no-break spaces and typographic apostrophes in French only."""

    def test_given_plain_french_when_built_then_the_page_is_typeset(self):
        page, _ = self.page()
        self.assertEqual(self.french(page)["html"]["hero.text"],
                         "Est-ce construit" + NARROW_NBSP + "? Oui" + NBSP + ": l’index" + NARROW_NBSP + "; enfin" +
                         NARROW_NBSP + "!")

    def test_given_english_then_the_rule_does_not_apply(self):
        self.assertEqual(site.typography("Is it built ? Yes : it's", "en"), "Is it built ? Yes : it's")


class TestStandardLibraryOnly(unittest.TestCase):
    """RQ-WEB-016: the script imports Python's standard library only."""

    def test_given_the_script_then_each_import_is_standard(self):
        source = SCRIPT.read_text(encoding="utf-8")
        modules = re.findall(r"^(?:from|import)\s+([a-zA-Z_]+)", source, re.M)
        self.assertTrue(modules)
        self.assertEqual([m for m in modules if m not in sys.stdlib_module_names], [])


if __name__ == "__main__":
    unittest.main()
