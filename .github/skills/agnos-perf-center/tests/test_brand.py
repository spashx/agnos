"""Tests of the brand, the version and the licences of the agnos-perf-center page (FTR-TRC-009, ADR-TRC-014: DEC-TRC-056 to
DEC-TRC-058).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-perf-center/tests -v
"""
import sys
import tempfile
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
