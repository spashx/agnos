"""Tests that the report page takes its visual values from the perf center's tokens (RQ-PLG-017, TASK-PLG-015;
ADR-PLG-002: DEC-PLG-012; ADR-TRC-002).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-meta-release/tests -v
"""
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import release  # noqa: E402

ROOT = HERE.parents[3]
PERF_CENTER = ROOT / ".github/skills/agnos-perf-center"
VAR_RE = re.compile(r"var\(--[a-z0-9-]+\)")
DECLARATION_RE = re.compile(r"([a-z-]+)\s*:\s*([^;{}]+);")
DIGIT_RE = re.compile(r"\d")
COLOUR_WORD_RE = re.compile(r"#[0-9a-f]{3,8}\b|\b(?:rgb|rgba|hsl|hsla|oklch)\(", re.I)
DARK_QUERY = "prefers-color-scheme: dark"


def output_with_perf_center(base):
    """An output holding the perf center as the release places it."""
    target = base / release.PLUGIN_SKILLS / "agnos-perf-center"
    shutil.copytree(PERF_CENTER, target, ignore=shutil.ignore_patterns("tests", "__pycache__"))
    return base


class TokensTest(unittest.TestCase):
    """RQ-PLG-017: the tokens of the commit rehearsed, compiled by its own perf center."""

    def setUp(self):
        holder = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(holder.cleanup)
        self.output = output_with_perf_center(Path(holder.name))

    def test_RQ_PLG_017_given_the_outputs_perf_center_then_its_tokens_compile_with_a_dark_theme(self):
        css = release.page_tokens(self.output)
        self.assertIn("--s-surface:", css)
        self.assertIn(DARK_QUERY, css)

    def test_RQ_PLG_017_given_the_compilation_then_it_leaves_no_cache_in_the_output(self):
        release.page_tokens(self.output)
        self.assertEqual([], list(self.output.rglob("__pycache__")))

    def test_RQ_PLG_017_given_every_variable_of_the_stylesheet_then_the_tokens_define_it(self):
        css = release.page_tokens(self.output)
        for used in sorted(set(VAR_RE.findall(release.REPORT_CSS_PATH.read_text(encoding="utf-8")))):
            self.assertIn(f"{used[len('var('):-1]}:", css, used)


class StylesheetTest(unittest.TestCase):
    """RQ-PLG-017: no raw visual literal in the page's stylesheet."""

    def test_RQ_PLG_017_given_the_stylesheet_then_no_declaration_holds_a_number_or_a_colour_outside_a_token(self):
        text = release.REPORT_CSS_PATH.read_text(encoding="utf-8")
        declarations = DECLARATION_RE.findall(text)
        self.assertTrue(declarations)
        for name, value in declarations:
            bare = VAR_RE.sub("", value)
            self.assertIsNone(DIGIT_RE.search(bare), f"{name}: {value}")
            self.assertIsNone(COLOUR_WORD_RE.search(bare), f"{name}: {value}")


if __name__ == "__main__":
    unittest.main()
