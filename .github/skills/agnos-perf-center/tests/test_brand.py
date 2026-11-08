"""Tests of the brand, the version and the licences of the agnos-perf-center page (FTR-TRC-009, ADR-TRC-014: DEC-TRC-056 to
DEC-TRC-058).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-perf-center/tests -v
"""
import json
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

    def test_RQ_TRC_018_given_the_token_file_then_no_token_is_declared_twice_in_a_tier(self):
        def refuse_duplicates(pairs):
            names = [name for name, _ in pairs]
            self.assertEqual([], sorted({n for n in names if names.count(n) > 1}), "declared twice in one object")
            return dict(pairs)
        json.loads(tm.TOKENS_PATH.read_text(encoding="utf-8"), object_pairs_hook=refuse_duplicates)

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
APP_TITLE = "AGNOS"      # DEC-TRC-061: the foot reads the name alone, then the version
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
    """A page generated while VERSION.txt holds `content`; None as content means the file does not exist."""
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


# RQ-TRC-111, RQ-TRC-112, DEC-TRC-058: the Licenses topic and its badges
APP_BADGE = "AGNOS=AGPL-3.0"       # the label is the application's name (owner, 2026-11-06, RQ-TRC-112)
SPDX_URL = "https://spdx.org/licenses/{id}.html"     # DEC-TRC-062
UNCLASSIFIED_LICENCE = "BSD-3-Clause"
READ_LICENCES = """
const out = document.documentElement.dataset;
document.getElementById("help-button").click();
document.querySelector('#help-list button[data-topic="licenses"]').click();
const list = document.getElementById("licence-list");
const badges = [...list.querySelectorAll(".licence-badge")];
const part = (badge, name) => badge.querySelector(`.licence-badge-${name}`);
out.badges = badges.map((b) => `${part(b, "label").textContent}=${part(b, "value").textContent}`).join(";");
out.shown = [...document.querySelectorAll("#help-dialog [data-help]")].filter((s) => !s.hidden).map((s) => s.dataset.help).join(",");
out.sideBySide = String(badges.every((b) => {
  const label = part(b, "label").getBoundingClientRect(), value = part(b, "value").getBoundingClientRect();
  return label.width > 0 && value.width > 0 && Math.abs(label.right - value.left) < 1 && Math.abs(label.top - value.top) < 1;
}));
out.labelFill = getComputedStyle(part(badges[0], "label")).backgroundColor;
out.labelInk = getComputedStyle(part(badges[0], "label")).color;
out.valueFills = badges.map((b) => getComputedStyle(part(b, "value")).backgroundColor).join("|");
out.valueInk = getComputedStyle(part(badges[0], "value")).color;
out.links = badges.map((b) => b.tagName === "A" ? `${b.getAttribute("href")} ${b.target} ${b.rel}` : "none").join(";");
out.linkCount = String(list.querySelectorAll("a").length);
out.intro = list.parentElement.textContent.includes("The licence of this application") ? "present" : "absent";
out.tones = Object.keys(agnosTrace.licenceTones).join(",");
"""
READ_ABOUT = """
const out = document.documentElement.dataset;
document.getElementById("help-button").click();
document.querySelector('#help-list button[data-topic="about"]').click();
const about = document.querySelector('[data-help="about"]');
out.aboutLinks = [...about.querySelectorAll("a")].map((a) => a.href).join(" ");
out.aboutText = about.textContent.replace(/\\s+/g, " ");
"""
LICENCE_NAMES = ("badges", "shown", "side-by-side", "label-fill", "label-ink", "value-fills", "value-ink", "links", "link-count", "intro", "tones")


def library_badges(libraries):
    """What the Licenses topic shows of a library record: `<name> <version>=<licence>`, after the application's badge."""
    return ";".join([APP_BADGE] + [f"{lib['name']} {lib['version']}={lib['licence']}" for lib in libraries])


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class LicencesTopicTest(unittest.TestCase):
    """TASK-TRC-095: RQ-TRC-111, RQ-TRC-112, RQ-TRC-115 (DEC-TRC-058), in a headless browser."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.page, _ = generate(Path(cls.tmp.name) / "page.html")
        cls.tokens = tm.load_tokens(tm.TOKENS_PATH)
        cls.libraries = json.loads(tm.LIBRARIES_PATH.read_text(encoding="utf-8"))["libraries"]

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def licences(self, page=None):
        return found(rendered_dom_after((page or self.page).path, READ_LICENCES), *LICENCE_NAMES)

    def fill(self, component):
        return rgb(resolve(self.tokens, component, "light"))

    def test_RQ_TRC_111_given_the_licenses_topic_then_it_shows_alone_with_the_application_and_each_library_of_the_record(self):
        got = self.licences()
        self.assertEqual("licenses", got["shown"])
        self.assertEqual(library_badges(self.libraries), got["badges"])

    def test_RQ_TRC_112_given_a_badge_then_its_label_and_value_stand_side_by_side_the_label_grey_and_the_ink_from_the_tokens(self):
        got = self.licences()
        self.assertEqual("true", got["side-by-side"])
        self.assertEqual((self.fill("badge-label-bg"), self.fill("badge-label-ink"), self.fill("badge-ink")),
                         (got["label-fill"], got["label-ink"], got["value-ink"]))

    def test_RQ_TRC_112_given_licences_of_different_kinds_then_their_values_are_filled_with_different_brand_tones(self):
        got = self.licences()
        tones = [self.fill(f"badge-tone-{tone}") for tone in ("green", "blue", "yellow")]     # AGPL-3.0, MIT, Apache-2.0
        self.assertEqual("|".join(tones), got["value-fills"])
        self.assertEqual(3, len(set(tones)))

    def test_RQ_TRC_112_given_every_badge_then_it_is_a_link_to_its_spdx_page_in_a_new_tab(self):
        """DEC-TRC-062: each badge, the application's included, opens https://spdx.org/licenses/<id>.html in a new tab."""
        got = self.licences()
        licences = [APP_BADGE.split("=")[1]] + [lib["licence"] for lib in self.libraries]
        self.assertEqual(";".join(f"{SPDX_URL.format(id=licence)} _blank noopener" for licence in licences), got["links"])
        self.assertEqual(str(len(licences)), got["link-count"])
        self.assertNotIn("github.com", got["links"])

    def test_RQ_TRC_112_given_the_links_then_every_licence_they_name_is_in_the_tone_table(self):
        """DEC-TRC-062: only a licence of the script's tone table is linked."""
        got = self.licences()
        ids = [link.split()[0].removeprefix(SPDX_URL.split("{")[0]).removesuffix(".html") for link in got["links"].split(";")]
        self.assertTrue(set(ids) <= set(got["tones"].split(",")), ids)

    def test_RQ_TRC_111_given_the_licenses_topic_then_it_has_no_introduction_sentence(self):
        """DEC-TRC-062: the sentence explaining the badges is removed."""
        self.assertEqual("absent", self.licences()["intro"])
        self.assertNotIn("The licence of this application", self.page)

    def test_RQ_TRC_112_given_the_library_record_then_every_licence_of_it_has_a_tone_chosen_for_it(self):
        listed = self.licences()["tones"].split(",")
        for library in self.libraries:
            self.assertIn(library["licence"], listed, f"{library['name']}: classify its licence in LICENCE_TONE")

    def test_RQ_TRC_111_given_a_version_changed_in_the_record_only_then_the_topic_shows_it_and_an_unclassified_licence_takes_the_light_tone(self):
        record = json.loads(tm.LIBRARIES_PATH.read_text(encoding="utf-8"))
        record["libraries"][0]["version"] = "9.9.9"
        record["libraries"][1]["licence"] = UNCLASSIFIED_LICENCE
        changed = Path(self.tmp.name) / "libraries.json"
        changed.write_text(json.dumps(record), encoding="utf-8")
        with mock.patch.object(tm, "LIBRARIES_PATH", changed):
            page, _ = generate(Path(self.tmp.name) / "changed.html")
        got = self.licences(page)
        self.assertEqual(library_badges(record["libraries"]), got["badges"])
        self.assertTrue(got["value-fills"].endswith(self.fill("badge-tone-light")), got["value-fills"])
        self.assertTrue(got["links"].endswith(";none"), got["links"])     # DEC-TRC-062: no link for a licence outside the table

    def test_RQ_TRC_111_given_the_about_topic_then_it_no_longer_shows_the_licence_nor_its_link(self):
        got = found(rendered_dom_after(self.page.path, READ_ABOUT), "about-links", "about-text")
        self.assertNotIn("LICENSE", got["about-links"])
        self.assertEqual(2, len(got["about-links"].split()))
        self.assertNotIn("Licence", got["about-text"])
        self.assertNotIn("AGPL", got["about-text"])

    def test_RQ_TRC_112_given_the_page_then_nothing_in_it_draws_a_badge_from_a_service(self):
        self.assertNotIn("shields.io", self.page)
        self.assertNotIn("<img", self.page)


# RQ-TRC-116, DEC-TRC-059: the lockup of the retained design in the About topic, as the design states it
LOCKUP_TAGLINE = "Agentic efficiency by traceability"
LOCKUP_NAME = "AGNOS v." + ".".join(tm.VERSION_PATH.read_text(encoding="utf-8").strip().split(".")[:2])   # DEC-TRC-061
LOCKUP_TOKENS = {"text-wordmark": "30px", "tracking-wordmark": "0.12em", "tracking-tagline": "0.02em",
                 "line-display": "1.1", "line-snug": "1.3", "weight-bold": "700", "weight-medium": "500",
                 "text-small": "13px"}
READ_LOCKUP = """
const out = document.documentElement.dataset;
document.getElementById("help-button").click();
document.querySelector('#help-list button[data-topic="about"]').click();
const about = document.querySelector('[data-help="about"]');
const mark = about.querySelector("svg.brand-mark").getBoundingClientRect();
const name = about.querySelector(".about-wordmark"), tagline = about.querySelector(".about-tagline");
const n = name.getBoundingClientRect(), t = tagline.getBoundingClientRect();
const style = (node) => { const s = getComputedStyle(node); return [s.fontSize, s.fontWeight, s.letterSpacing, s.lineHeight].join(" "); };
out.nameText = name.textContent.trim(); out.taglineText = tagline.textContent;
out.nameStyle = style(name); out.taglineStyle = style(tagline);
out.toTheRight = String(n.left >= mark.right && t.left >= mark.right);
out.below = String(t.top >= n.bottom - 1);
out.aligned = String(Math.abs(n.left - t.left) < 1);
out.centred = String(Math.abs((n.top + t.bottom) / 2 - (mark.top + mark.bottom) / 2) < 2);
out.aboveText = String(Math.max(mark.bottom, t.bottom) <= about.querySelector("p").getBoundingClientRect().top);
const colours = () => `${getComputedStyle(name).color}|${getComputedStyle(tagline).color}`;
document.documentElement.dataset.theme = "light"; out.coloursLight = colours();
document.documentElement.dataset.theme = "dark"; out.coloursDark = colours();
"""
LOCKUP_NAMES = ("name-text", "tagline-text", "name-style", "tagline-style", "to-the-right", "below", "aligned", "centred",
                "above-text", "colours-light", "colours-dark")
LENGTH_TOLERANCE = 0.05


def semantic(tokens, name, theme):
    """The raw value a semantic token ends in, in a theme (DEC-TRC-009)."""
    reference = tokens["semantic"][name]
    return tokens["global"][reference[theme] if isinstance(reference, dict) else reference]


class LockupTokensTest(unittest.TestCase):
    """TASK-TRC-097: RQ-TRC-116, RQ-TRC-018 (DEC-TRC-059)."""

    def test_RQ_TRC_116_given_the_token_file_then_the_type_values_of_the_lockup_are_those_of_the_retained_design(self):
        tokens = tm.load_tokens(tm.TOKENS_PATH)
        self.assertEqual(LOCKUP_TOKENS, {name: semantic(tokens, name, "light") for name in LOCKUP_TOKENS})


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class AboutLockupTest(unittest.TestCase):
    """TASK-TRC-097: RQ-TRC-116 (DEC-TRC-059), in a headless browser."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        page, _ = generate(Path(cls.tmp.name) / "page.html")
        cls.got = found(rendered_dom_after(page.path, READ_LOCKUP), *LOCKUP_NAMES)
        cls.tokens = tm.load_tokens(tm.TOKENS_PATH)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def lengths(self, text):
        """The numbers of a computed style, `font-size weight letter-spacing line-height`, without their units."""
        return [float(part.removesuffix("px")) for part in text.split()]

    def test_RQ_TRC_116_given_the_about_topic_then_the_name_and_the_tagline_read_as_the_owner_wrote_them(self):
        self.assertEqual((LOCKUP_NAME, LOCKUP_TAGLINE), (self.got["name-text"], self.got["tagline-text"]))

    def test_RQ_TRC_116_given_the_lockup_then_the_name_is_right_of_the_mark_the_tagline_below_it_and_the_pair_centred_above_the_text(self):
        self.assertEqual({key: "true" for key in ("to-the-right", "below", "aligned", "centred", "above-text")},
                         {key: self.got[key] for key in ("to-the-right", "below", "aligned", "centred", "above-text")})

    def test_RQ_TRC_116_given_the_lockup_then_the_name_and_the_tagline_are_set_as_the_design_states_them(self):
        name_size, tagline_size = 30, 13                                            # the design's, checked in the token test
        expected_name = [name_size, 700, 0.12 * name_size, 1.1 * name_size]
        expected_tagline = [tagline_size, 500, 0.02 * tagline_size, 1.3 * tagline_size]
        for got, expected in ((self.got["name-style"], expected_name), (self.got["tagline-style"], expected_tagline)):
            for found_value, wanted in zip(self.lengths(got), expected):
                self.assertAlmostEqual(wanted, found_value, delta=LENGTH_TOLERANCE, msg=got)

    def test_RQ_TRC_116_given_each_theme_then_the_name_and_the_tagline_take_the_text_and_the_muted_text_colours(self):
        for theme in tm.THEMES:
            expected = "|".join(rgb(semantic(self.tokens, token, theme)) for token in ("text", "text-muted"))
            self.assertEqual(expected, self.got[f"colours-{theme}"], theme)


# RQ-TRC-113, DEC-TRC-058: the About topic's sentence and link buttons
ABOUT_SENTENCE = "This app is generated by agnos-perf-center, a skill of the AGNOS process."
ABOUT_BUTTONS = "https://github.com/spashx https://www.linkedin.com/in/64493197"
READ_ABOUT_BUTTONS = """
const out = document.documentElement.dataset;
document.getElementById("help-button").click();
document.querySelector('#help-list button[data-topic="about"]').click();
const about = document.querySelector('[data-help="about"]');
const buttons = [...about.querySelectorAll("a.about-link")];
out.sentence = about.querySelector("p").textContent.trim();
out.buttons = buttons.map((a) => a.textContent.replace(/\\s+/g, " ").trim()).join(" ");
out.icons = String(buttons.every((a) => a.querySelector("svg").getBoundingClientRect().width > 0));
"""


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class AboutTopicTest(unittest.TestCase):
    """TASK-TRC-096: RQ-TRC-113 (DEC-TRC-058), in a headless browser."""

    def test_RQ_TRC_113_given_the_about_topic_then_it_says_app_and_its_buttons_read_their_addresses_beside_an_icon(self):
        with tempfile.TemporaryDirectory() as tmp:
            page, _ = generate(Path(tmp) / "page.html")
            got = found(rendered_dom_after(page.path, READ_ABOUT_BUTTONS), "sentence", "buttons", "icons")
        self.assertEqual({"sentence": ABOUT_SENTENCE, "buttons": ABOUT_BUTTONS, "icons": "true"}, got)


if __name__ == "__main__":
    unittest.main()
