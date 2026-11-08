"""Tests of agnos-meta-website's content: reading en.md and fr.md, their checks against the template, the measured
figures and French typography (FTR-WEB-001: RQ-WEB-003, RQ-WEB-004, RQ-WEB-005, RQ-WEB-006, RQ-WEB-016; ADR-WEB-001:
DEC-WEB-001, DEC-WEB-003)."""
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
[![The view](screens/view.png)](demo/PERF-CENTER.html#RQ-BKG-003)

### excerpt
```
@agnos-process/one.md
RQ-BKG-003|42-56||No double booking
```

### figure
Documents {{index.documents}}, index {{index.size}}, ratio {{index.ratio}}
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
[![La vue](screens/view.png)](demo/PERF-CENTER.html#RQ-BKG-003)

### excerpt
```
@agnos-process/one.md
RQ-BKG-003|42-56||No double booking
```

### figure
Documents {{index.documents}}, index {{index.size}}, ratio {{index.ratio}}
"""
DOCUMENTS_BYTES = 12000
INDEX_BYTES = 1000


class Fixture(unittest.TestCase):
    """A temporary assets folder and demo repository; each test changes one of their files."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="agnos-meta-website-"))
        self.assets = self.root / "assets"
        self.demo = self.root / "demo"
        (self.assets / "content").mkdir(parents=True)
        (self.assets / "screens").mkdir()
        (self.assets / "template.html").write_text(TEMPLATE, encoding="utf-8")
        (self.assets / "content" / "en.md").write_text(EN, encoding="utf-8")
        (self.assets / "content" / "fr.md").write_text(FR, encoding="utf-8")
        (self.assets / "screens" / "view.png").write_bytes(PNG)
        process = self.demo / "agnos-process"
        for folder in ("1.requirements", "2.architecture", "3.plan"):
            (process / folder).mkdir(parents=True)
        (process / "1.requirements" / "FTR-BKG-001.md").write_bytes(b"x" * DOCUMENTS_BYTES)
        (process / "process.idx.md").write_bytes(b"x" * INDEX_BYTES)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def write(self, name, text):
        (self.assets / "content" / name).write_text(text, encoding="utf-8")

    def page(self):
        """(page, errors) of a build of the fixture."""
        errors = []
        result = site.build_page(self.assets, self.demo, errors, tokens_css="")
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

    def test_given_a_linked_image_when_built_then_it_opens_its_address(self):
        page, _ = self.page()
        self.assertIn('href="demo/PERF-CENTER.html#RQ-BKG-003"', page)
        self.assertIn('<img src="screens/view.png" alt="The view"', page)

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


class TestMeasuredFigures(Fixture):
    """RQ-WEB-005: the index figures measured on the demo, in each language's number format."""

    def test_given_the_demo_when_built_then_the_figures_are_measured(self):
        page, _ = self.page()
        self.assertIn("Documents 12.0 KB, index 1.0 KB, ratio 1/12", page)
        self.assertEqual(self.french(page)["html"]["hero.figure"],
                         "Documents 12,0" + NBSP + "Ko, index 1,0" + NBSP + "Ko, ratio 1/12")

    def test_given_an_unknown_variable_then_it_is_reported(self):
        self.write("en.md", EN.replace("{{index.ratio}}", "{{index.unknown}}"))
        page, errors = self.page()
        self.assertIsNone(page)
        self.assertIn("en.md: hero.figure: unknown variable {{index.unknown}}", errors)


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
