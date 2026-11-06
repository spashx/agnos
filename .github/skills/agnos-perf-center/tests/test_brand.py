"""Tests of the brand, the version and the licences of the agnos-perf-center page (FTR-TRC-009, ADR-TRC-014: DEC-TRC-056 to
DEC-TRC-058).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-perf-center/tests -v
"""
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))

import perf_center as tm  # noqa: E402
from test_history_page import NEEDS_BROWSER, found  # noqa: E402
from test_perf_center import BROWSER, generate, rendered_dom_after  # noqa: E402
from test_scorecard import CONTRAST_MIN, contrast  # noqa: E402

# RQ-TRC-114, DEC-TRC-056: the colours of the retained design "Spans", as semantic tokens.
BRAND_COLOURS = {"brand-tile": "#3C4043", "brand-light": "#E8EAED", "brand-blue": "#4285F4",
                 "brand-green": "#34A853", "brand-yellow": "#FBBC05"}
BADGE_TONES = ("badge-tone-green", "badge-tone-blue", "badge-tone-yellow", "badge-tone-light")
HEADER_MARK = "brand-mark-size"
ABOUT_MARK = "brand-mark-size-large"
ABOUT_MARK_TIMES = 3
PIXELS = "px"


def resolve(tokens, component, theme):
    """The raw value a component token ends in, through its semantic and its global token (RQ-TRC-115, DEC-TRC-009)."""
    semantic = tokens["semantic"][tokens["component"][component]]
    reference = semantic[theme] if isinstance(semantic, dict) else semantic
    return tokens["global"][reference]


class BrandTokensTest(unittest.TestCase):
    """TASK-TRC-092: RQ-TRC-114, RQ-TRC-115 (DEC-TRC-056)."""

    def test_RQ_TRC_114_given_the_token_file_when_resolved_then_the_brand_colours_are_those_of_the_retained_design(self):
        css = tm.tokens_css(tm.load_tokens(tm.TOKENS_PATH))
        for name, value in BRAND_COLOURS.items():
            self.assertEqual(1, css.count(f"--s-{name}: {value};"), name)   # written once: both themes inherit it

    def test_RQ_TRC_115_given_the_badge_tokens_when_contrast_is_computed_then_no_text_is_below_4_5_in_either_theme(self):
        tokens = tm.load_tokens(tm.TOKENS_PATH)
        for theme in tm.THEMES:
            ink = resolve(tokens, "badge-ink", theme)
            for tone in BADGE_TONES:
                self.assertGreaterEqual(contrast(resolve(tokens, tone, theme), ink), CONTRAST_MIN, f"{theme} {tone}")
            self.assertGreaterEqual(contrast(resolve(tokens, "badge-label-bg", theme), resolve(tokens, "badge-label-ink", theme)),
                                    CONTRAST_MIN, f"{theme} label")

    def test_RQ_TRC_114_given_the_mark_sizes_then_the_about_mark_is_at_least_three_times_the_header_mark(self):
        tokens = tm.load_tokens(tm.TOKENS_PATH)
        size = lambda name: float(resolve(tokens, name, "light").removesuffix(PIXELS))  # noqa: E731
        self.assertGreaterEqual(size(ABOUT_MARK), ABOUT_MARK_TIMES * size(HEADER_MARK))


# RQ-TRC-114, DEC-TRC-056: the parts of the mark in the sprite, and the token each is filled from
MARK_PARTS = (("tile", "brand-tile"), ("bar-light", "brand-light"), ("bar-blue", "brand-blue"),
              ("bar-green", "brand-green"), ("bar-yellow", "brand-yellow"))
FILL_NAMES = tuple(f"fill-{part}" for part, _ in MARK_PARTS)
# the geometry of the retained design, on its 24-unit grid: x, y and width of each bar
BAR_GEOMETRY = {"bar-light": "4,3,16", "bar-blue": "4,8,6", "bar-green": "10,13,5", "bar-yellow": "15,18,5"}
READ_MARK = """
const out = document.documentElement.dataset;
const part = (name) => document.querySelector(`#brand-mark .mark-${name}`);
for (const name of ["tile", "bar-light", "bar-blue", "bar-green", "bar-yellow"]) {
  out[`fill${name.replace(/(^|-)(.)/g, (_, __, c) => c.toUpperCase())}`] = getComputedStyle(part(name)).fill;
}
for (const name of ["bar-light", "bar-blue", "bar-green", "bar-yellow"]) {
  out[`geo${name.replace(/(^|-)(.)/g, (_, __, c) => c.toUpperCase())}`] = ["x", "y", "width"].map((a) => part(name).getAttribute(a)).join(",");
}
const fills = () => ["tile", "bar-light", "bar-blue", "bar-green", "bar-yellow"].map((n) => getComputedStyle(part(n)).fill).join("|");
document.documentElement.dataset.theme = "light"; out.themeLight = fills();
document.documentElement.dataset.theme = "dark"; out.themeDark = fills();
"""
PLACE_MARK = """
const out = document.documentElement.dataset;
const header = document.querySelector(".topbar svg.brand-mark");
out.headerUse = header.querySelector("use").getAttribute("href");
out.headerWidth = String(header.getBoundingClientRect().width);
out.dots = String(document.querySelectorAll("svg.brand-mark circle").length);
document.getElementById("help-button").click();
document.querySelector('#help-list button[data-topic="about"]').click();
const large = document.querySelector('[data-help="about"] svg.brand-mark');
out.aboutUse = large.querySelector("use").getAttribute("href");
out.aboutWidth = String(large.getBoundingClientRect().width);
out.aboveText = String(large.getBoundingClientRect().bottom <= document.querySelector('[data-help="about"] p').getBoundingClientRect().top);
"""


def rgb(hex_colour):
    """A colour as the browser reports a computed fill, rgb(r, g, b)."""
    value = hex_colour.lstrip("#")
    return "rgb(" + ", ".join(str(int(value[i:i + 2], 16)) for i in (0, 2, 4)) + ")"


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class BrandMarkTest(unittest.TestCase):
    """TASK-TRC-093: RQ-TRC-114, RQ-TRC-115 (DEC-TRC-056), in a headless browser."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "page.html"
        generate(cls.path)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def read(self, script, *names):
        return found(rendered_dom_after(self.path, script), *names)

    def test_RQ_TRC_114_given_the_page_when_the_mark_is_read_then_its_tile_and_four_bars_are_filled_with_the_brand_colours(self):
        got = self.read(READ_MARK, *(f"fill-{p}" for p, _ in MARK_PARTS))
        self.assertEqual({f"fill-{part}": rgb(BRAND_COLOURS[token]) for part, token in MARK_PARTS}, got)

    def test_RQ_TRC_114_given_the_light_and_the_dark_themes_then_the_mark_is_filled_alike(self):
        got = self.read(READ_MARK, "theme-light", "theme-dark")
        expected = "|".join(rgb(BRAND_COLOURS[token]) for _, token in MARK_PARTS)
        self.assertEqual({"theme-light": expected, "theme-dark": expected}, got)

    def test_RQ_TRC_114_given_the_mark_then_the_three_coloured_bars_each_start_further_right_and_lower_than_the_one_above(self):
        got = self.read(READ_MARK, *(f"geo-{name}" for name in BAR_GEOMETRY))
        self.assertEqual({f"geo-{name}": value for name, value in BAR_GEOMETRY.items()}, got)

    def test_RQ_TRC_114_given_the_header_and_the_about_topic_then_both_hold_the_mark_and_the_about_one_is_three_times_larger(self):
        got = self.read(PLACE_MARK, "header-use", "header-width", "dots", "about-use", "about-width", "above-text")
        tokens = tm.load_tokens(tm.TOKENS_PATH)
        self.assertEqual(("#brand-mark", "#brand-mark", "0"), (got["header-use"], got["about-use"], got["dots"]))
        self.assertEqual(float(resolve(tokens, HEADER_MARK, "light").removesuffix(PIXELS)), float(got["header-width"]))
        self.assertGreaterEqual(float(got["about-width"]), ABOUT_MARK_TIMES * float(got["header-width"]))
        self.assertEqual("true", got["above-text"])


# RQ-TRC-109, RQ-TRC-110, DEC-TRC-057: the foot of the left panel
APP_TITLE = "AGNOS Performance Center"
FOOT_RE = re.compile(r'<footer class="side-footer"[^>]*>(.*?)</footer>', re.DOTALL)
TAG_RE = re.compile(r"<[^>]*>")
UNREADABLE_VERSIONS = ("v3.2\n", "3.1\n", "03.1.0\n", "", "3.1.0\n3.2.0\n", "latest\n")
READ_FOOT = """
document.documentElement.dataset.foot = document.querySelector(".side-footer").textContent.replace(/\\s+/g, " ").trim();
"""


def foot(page):
    """The text of the left panel's foot in a generated page, tags removed and spaces collapsed."""
    return " ".join(TAG_RE.sub("", FOOT_RE.search(page).group(1)).split())


def generate_with_version(directory, name, content):
    """A page generated while VERSION holds `content`; None as content means the file does not exist."""
    version = Path(directory) / f"VERSION-{name}"
    if content is not None:
        version.write_text(content, encoding="utf-8")
    with mock.patch.object(tm, "VERSION_PATH", version):
        page, _ = generate(Path(directory) / f"{name}.html")
    return page


class PageVersionTest(unittest.TestCase):
    """TASK-TRC-094: RQ-TRC-109, RQ-TRC-110 (DEC-TRC-057)."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_RQ_TRC_109_given_a_VERSION_of_3_1_0_when_a_page_is_generated_then_the_foot_reads_the_title_and_v_3_1(self):
        self.assertEqual(f"{APP_TITLE} v.3.1", foot(generate_with_version(self.tmp.name, "a", "3.1.0\n")))

    def test_RQ_TRC_109_given_a_VERSION_of_3_12_4_then_the_foot_shows_v_3_12_without_the_patch(self):
        self.assertEqual(f"{APP_TITLE} v.3.12", foot(generate_with_version(self.tmp.name, "b", "3.12.4")))

    def test_RQ_TRC_109_given_a_prerelease_VERSION_then_the_foot_shows_its_major_and_minor_only(self):
        self.assertEqual(f"{APP_TITLE} v.4.0", foot(generate_with_version(self.tmp.name, "c", "4.0.0-rc.1+build.5\n")))

    def test_RQ_TRC_109_given_only_VERSION_changed_then_the_foot_changes_and_the_data_files_stay_the_same(self):
        first = generate_with_version(self.tmp.name, "d1", "3.1.0\n")
        second = generate_with_version(self.tmp.name, "d2", "5.2.0\n")
        self.assertEqual((f"{APP_TITLE} v.3.1", f"{APP_TITLE} v.5.2"), (foot(first), foot(second)))
        for suffix in (tm.DATA_JSON_SUFFIX, tm.DATA_SCRIPT_SUFFIX):
            self.assertEqual(first.path.with_name("d1" + suffix).read_bytes(), second.path.with_name("d2" + suffix).read_bytes())

    def test_RQ_TRC_109_given_the_foot_then_it_names_no_library(self):
        text = foot(generate_with_version(self.tmp.name, "e", "3.1.0\n"))
        for needle in ("cdnjs", "Cytoscape", "ECharts", "MIT", "Apache"):
            self.assertNotIn(needle, text)

    def test_RQ_TRC_110_given_no_VERSION_file_when_a_page_is_generated_then_the_run_succeeds_and_the_foot_reads_the_title_alone(self):
        self.assertEqual(APP_TITLE, foot(generate_with_version(self.tmp.name, "f", None)))

    def test_RQ_TRC_110_given_a_VERSION_that_is_not_one_semver_line_then_the_foot_reads_the_title_alone(self):
        for number, content in enumerate(UNREADABLE_VERSIONS):
            with self.subTest(content=content):
                self.assertEqual(APP_TITLE, foot(generate_with_version(self.tmp.name, f"g{number}", content)))

    def test_RQ_TRC_109_given_the_repository_then_the_foot_shows_the_version_of_its_VERSION_file(self):
        major, minor = tm.VERSION_PATH.read_text(encoding="utf-8").strip().split(".")[:2]
        page, _ = generate(Path(self.tmp.name) / "repo.html")
        self.assertEqual(f"{APP_TITLE} v.{major}.{minor}", foot(page))


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class FootInBrowserTest(unittest.TestCase):
    """TASK-TRC-094: RQ-TRC-109 (DEC-TRC-057), in a headless browser."""

    def test_RQ_TRC_109_given_the_page_once_its_script_ran_then_the_foot_still_reads_the_title_and_the_version_alone(self):
        with tempfile.TemporaryDirectory() as tmp:
            page = generate_with_version(tmp, "h", "3.1.0\n")
            got = found(rendered_dom_after(page.path, READ_FOOT), "foot")
        self.assertEqual({"foot": f"{APP_TITLE} v.3.1"}, got)


if __name__ == "__main__":
    unittest.main()
