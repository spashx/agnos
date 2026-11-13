"""Tests of agnos-meta-website's design system: the site's layer over the Performance Center's tokens and its CSS
(FTR-WEB-001: RQ-WEB-014, RQ-WEB-015; ADR-WEB-001: DEC-WEB-005; ADR-TRC-002)."""
import importlib.util
import json
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("agnos_meta_website", SKILL_DIR / "scripts" / "build_site.py")
site = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(site)

MIN_TEXT_CONTRAST = 4.5
THEMES = ("light", "dark")
# (text, background) pairs the page draws, by semantic token; text-subtle never stands on surface-hover, where the
# Performance Center's slate-500 gives 4.34:1
TEXT_PAIRS = [(text, surface) for text in ("text", "text-muted", "text-subtle")
              for surface in ("surface-subtle", "surface-raised")]
TEXT_PAIRS += [("text", "surface-hover"), ("text-muted", "surface-hover"), ("text-on-accent", "accent"),
               ("accent", "surface-raised"), ("web-band-text", "web-band"), ("web-band-text-muted", "web-band"),
               ("web-band-accent", "web-band"), ("web-band-text-on-accent", "web-band-accent"),
               ("text", "web-human-subtle"), ("text", "web-agent-subtle"),
               ("web-band-text", "web-console")]   # TASK-WEB-018: the start steps' console
PERF_CENTER_COLOURS = ("kind-human", "kind-agent", "brand-tile", "brand-light", "brand-blue", "brand-green",
                       "brand-yellow")
LINEAR_THRESHOLD = 0.03928   # WCAG 2: below it a channel is linear


def luminance(colour):
    """WCAG relative luminance of #RRGGBB."""
    channels = [int(colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= LINEAR_THRESHOLD else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(first, second):
    """WCAG contrast ratio of two colours."""
    high, low = sorted((luminance(first), luminance(second)), reverse=True)
    return (high + 0.05) / (low + 0.05)


class TestTheLayer(unittest.TestCase):
    """RQ-WEB-015: the Performance Center's tokens extended by the site's, without repeating a name."""

    def setUp(self):
        self.errors = []
        self.tokens = site.load_design_system(self.errors)

    def test_given_the_assets_then_the_design_system_loads_without_error(self):
        self.assertEqual(self.errors, [])

    def test_given_the_identity_and_brand_colours_then_they_are_the_perf_centers(self):
        perf_center = json.loads(site.PERF_CENTER_TOKENS.read_text(encoding="utf-8"))
        for name in PERF_CENTER_COLOURS:
            ref = perf_center["semantic"][name]
            refs = ref if isinstance(ref, dict) else {"light": ref, "dark": ref}
            expected = tuple(perf_center["global"][refs[theme]] for theme in THEMES)
            self.assertEqual(site.theme_values(self.tokens, name, self.errors), expected, name)

    def test_given_a_site_token_named_as_a_perf_center_one_then_it_is_reported(self):
        layer = {"global": {}, "semantic": {"accent": "color.blue-600"}, "component": {}}
        errors = []
        site.merge_tokens(json.loads(site.PERF_CENTER_TOKENS.read_text(encoding="utf-8")), layer, errors)
        self.assertIn("tokens.json: semantic token accent is already a Performance Center token", errors)

    def test_given_a_reference_to_no_token_then_it_is_reported(self):
        tokens = {"global": {}, "semantic": {"web-x": "web.none"}, "component": {"web-y": "web-none"}}
        errors = []
        site.theme_values(tokens, "web-x", errors)
        site.tokens_css(tokens, set(), {"web-y"}, errors)
        self.assertIn("design token web-x refers to web.none, which is no global token", errors)
        self.assertIn("component token web-y refers to web-none, which is no semantic token", errors)


class TestContrast(unittest.TestCase):
    """RQ-WEB-014: every text pair the page draws reaches 4.5:1 in each theme."""

    def test_given_each_theme_then_every_text_pair_reaches_the_minimum(self):
        errors = []
        tokens = site.load_design_system(errors)
        for text, background in TEXT_PAIRS:
            for index, theme in enumerate(THEMES):
                ratio = contrast(site.theme_values(tokens, text, errors)[index],
                                 site.theme_values(tokens, background, errors)[index])
                self.assertGreaterEqual(ratio, MIN_TEXT_CONTRAST, f"{text} on {background}, {theme}: {ratio:.2f}")
        self.assertEqual(errors, [])


class TestTheCss(unittest.TestCase):
    """RQ-WEB-015, DEC-WEB-005: the tokens the template uses become CSS custom properties, in each theme."""

    def setUp(self):
        self.errors = []
        self.tokens = site.load_design_system(self.errors)

    def test_given_used_tokens_then_each_becomes_one_variable_per_theme(self):
        css = site.tokens_css(self.tokens, {"web-band", "web-space-4"}, {"web-link"}, self.errors)
        self.assertEqual(self.errors, [])
        self.assertEqual(css.count("--s-web-space-4: 4px;"), 1)
        self.assertEqual(css.count("--s-web-band: "), 3)   # light, dark by preference, dark by choice
        self.assertIn("--c-web-link: var(--s-accent);", css)
        self.assertIn("--s-accent: ", css)                  # the component's semantic token comes with it

    def test_given_a_template_then_its_tokens_are_written_and_its_media_values_filled(self):
        template = ("<style>/*@TOKENS@*/\n.a{color:var(--s-text)}"
                    "@media (max-width: {{t:web-size-breakpoint-wide}}){.a{padding:var(--s-web-space-4)}}</style>")
        page = site.apply_tokens(template, self.tokens, self.errors)
        self.assertEqual(self.errors, [])
        self.assertIn("@media (max-width: 980px)", page)
        self.assertRegex(page, r"--s-text: #[0-9A-Fa-f]{6};")
        self.assertNotIn("/*@TOKENS@*/", page)

    def test_given_a_template_using_an_unknown_token_then_it_is_reported(self):
        site.apply_tokens("<style>/*@TOKENS@*/.a{color:var(--s-web-none)}</style>", self.tokens, self.errors)
        self.assertIn("template: --s-web-none is no design token", self.errors)


if __name__ == "__main__":
    unittest.main()
