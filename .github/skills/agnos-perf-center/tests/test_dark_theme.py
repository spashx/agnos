"""Dark theme in layers and its contrast (RQ-TRC-117, RQ-TRC-118; ADR-TRC-017: DEC-TRC-063, DEC-TRC-064; TASK-TRC-103)."""

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))

import perf_center as tm  # noqa: E402
from test_brand import resolve  # noqa: E402
from test_scorecard import contrast, luminance  # noqa: E402

DARK = "dark"
LIGHT = "light"
TEXT_MIN = 4.5                                                   # WCAG SC 1.4.3
MARK_MIN = 3.0                                                   # WCAG SC 1.4.11
LAYERS = ("control-bg", "page-bg", "card-bg", "table-row-hover")  # RQ-TRC-117: fields < page < raised < hover
SURFACES = ("page-bg", "card-bg", "table-row-hover", "table-row-selected")
TEXTS = ("text", "text-muted", "text-subtle", "accent", "status-ok", "status-warn", "status-error")
MARKS = ("type-ftr", "type-rq", "type-adr", "type-dec", "type-plan", "type-task", "type-fn", "border-strong",
         *(f"identity-{n}" for n in range(1, 13)))
LIGHT_BEFORE = {"surface": "#FFFFFF", "surface-subtle": "#F8FAFC", "surface-raised": "#FFFFFF", "surface-hover": "#F1F5F9",
                "surface-selected": "#EFF6FF", "border": "#E2E8F0", "border-strong": "#CBD5E1", "text-subtle": "#64748B",
                "type-ftr": "#0072B2", "type-task": "#D55E00", "graph-background": "#F8FAFC", "graph-node-border": "#FFFFFF",
                "accent-subtle": "#EFF6FF", "accent-border": "#DBEAFE", "identity-1": "#2563EB", "identity-4": "#DC2626",
                "identity-8": "#B45309", "identity-9": "#6366F1"}  # the light values before TASK-TRC-103


class DarkThemeTest(unittest.TestCase):
    """TASK-TRC-103: RQ-TRC-117, RQ-TRC-118."""

    @classmethod
    def setUpClass(cls):
        cls.tokens = tm.load_tokens(tm.TOKENS_PATH)

    def semantic(self, name, theme):
        """The raw value of a semantic token in a theme (DEC-TRC-009)."""
        ref = self.tokens["semantic"][name]
        return self.tokens["global"][ref[theme] if isinstance(ref, dict) else ref]

    def test_RQ_TRC_117_given_the_dark_tokens_when_the_surfaces_are_compared_then_fields_page_raised_hover_grow_lighter(self):
        values = [luminance(resolve(self.tokens, name, DARK)) for name in LAYERS]
        self.assertEqual(sorted(set(values)), values, dict(zip(LAYERS, values)))
        self.assertEqual(resolve(self.tokens, "page-bg", DARK), resolve(self.tokens, "graph-bg", DARK))

    def test_RQ_TRC_117_given_the_light_theme_then_no_token_changed(self):
        self.assertEqual(LIGHT_BEFORE, {name: self.semantic(name, LIGHT) for name in LIGHT_BEFORE})

    def test_RQ_TRC_118_given_each_dark_surface_then_texts_reach_4_5_and_marks_3(self):
        weak = []
        for surface in SURFACES:
            back = resolve(self.tokens, surface, DARK)
            for names, floor in ((TEXTS, TEXT_MIN), (MARKS, MARK_MIN)):
                weak += [(name, surface, round(contrast(self.semantic(name, DARK), back), 2)) for name in names
                         if contrast(self.semantic(name, DARK), back) < floor]
        self.assertEqual([], weak)


if __name__ == "__main__":
    unittest.main()
