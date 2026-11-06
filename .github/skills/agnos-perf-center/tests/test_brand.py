"""Tests of the brand, the version and the licences of the agnos-perf-center page (FTR-TRC-009, ADR-TRC-014: DEC-TRC-056 to
DEC-TRC-058).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-perf-center/tests -v
"""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))

import perf_center as tm  # noqa: E402
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


if __name__ == "__main__":
    unittest.main()
