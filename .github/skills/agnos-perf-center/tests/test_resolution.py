"""Tests of the call resolution accuracy of the call graph (FTR-TRC-002, ADR-TRC-021): the receiver (RQ-TRC-124), the
constructions (RQ-TRC-125), the ancestor classes (RQ-TRC-126), the arity (RQ-TRC-127), and calls never tracing a function
(RQ-TRC-128). Each case writes its sources in a temporary folder, so the fixtures' pinned counts do not change.

Run from the repository root: python -m unittest discover -s .github/skills/agnos-perf-center/tests -v
Skipped without the packages of requirements-callgraph.txt.
"""
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "agnos-graph" / "scripts"))   # DEC-TRC-074: the moved modules (TASK-TRC-117)
sys.path.insert(0, str(HERE))

from test_callgraph import HAS_TREE_SITTER  # noqa: E402
from test_perf_center import BROWSER, generate, rendered_dom_after  # noqa: E402


@unittest.skipUnless(HAS_TREE_SITTER and BROWSER, "needs tree-sitter and a Chromium-family browser")
class UnknownBasePageTest(unittest.TestCase):
    """TASK-TRC-115: RQ-TRC-126: the call graph card names the unknown bases."""

    def test_RQ_TRC_126_given_an_unknown_base_when_the_card_figure_is_focused_then_its_tooltip_names_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            sources = Path(tmp) / "src"
            sources.mkdir()
            (sources / "m.py").write_text("class C(Missing):\n    def f(self):\n        return 0\n", encoding="utf-8")
            page, _ = generate(Path(tmp) / "page.html", "--sources", str(sources), "--call-graph")
            script = ("agnosTrace.showView('graph');"
                      "const item = [...document.querySelectorAll('#call-graph-card [data-rich-tip]')]"
                      ".find((b) => b.textContent.startsWith('Unknown base classes'));"
                      "item.dispatchEvent(new Event('focus'));"
                      "document.documentElement.dataset.tip = document.getElementById('tip').textContent;")
            dom = rendered_dom_after(page.path, script)
        self.assertIn("Missing", dom)
        self.assertIn("Unknown base classes", dom)


if __name__ == "__main__":
    unittest.main()
