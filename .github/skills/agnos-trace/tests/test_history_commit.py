"""Tests of the History tab's controls, of the identities' icons, of the commit in the detail panel and of its git
graph (FTR-HST-001: RQ-HST-022 to RQ-HST-026; ADR-HST-001: DEC-HST-009 to DEC-HST-011), in a headless browser.

Run from the repository root: python -m unittest discover -s .github/skills/agnos-trace/tests -v
"""
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))

from test_history_page import NEEDS_BROWSER, START, add_history, found  # noqa: E402
from test_trace_matrix import BROWSER, generate, rendered_dom_after  # noqa: E402


class PageTestCase(unittest.TestCase):
    """A generated page given the synthetic history of test_history_page."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "page.html"
        generate(cls.path)
        cls.data = add_history(cls.path)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_script(self, script, *names):
        return found(rendered_dom_after(self.path, START + script), *names)


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class ControlsTest(PageTestCase):
    """TASK-HST-013: RQ-HST-022."""

    def test_RQ_HST_022_given_the_tab_then_the_selectors_stand_together_and_the_row_filter_comes_first(self):
        got = self.run_script("""
agnosTrace.showView("history");
const toolbar = document.querySelector("#view-history > .toolbar");
const order = () => [...toolbar.querySelectorAll(":scope > fieldset")].filter((f) => !f.hidden).map((f) => f.id).join(",");
out.requirements = order();
document.querySelector('#history-angle [data-angle="code"]').click();
out.code = order();
out.first = document.querySelector(".history-filter-line").firstElementChild.id;
out.filterwidth = String(document.getElementById("history-filter").getBoundingClientRect().width);
out.searchwidth = String(document.getElementById("search").getBoundingClientRect().width);
""", "requirements", "code", "first", "filterwidth", "searchwidth")
        self.assertEqual("history-angle,history-kind", got["requirements"])
        self.assertEqual("history-angle,history-grouping,history-kind", got["code"])
        self.assertEqual("history-filter", got["first"])
        self.assertLessEqual(abs(float(got["filterwidth"]) - float(got["searchwidth"])), 1)


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class IdentityIconTest(PageTestCase):
    """TASK-HST-014: RQ-HST-026, RQ-HST-014."""

    def test_RQ_HST_026_given_an_identity_then_its_icon_is_in_its_colour_and_no_dot_is_drawn(self):
        got = self.run_script("""
const colour = (node) => node ? getComputedStyle(node).color : "";
const side = [...document.querySelectorAll("#history-shortcuts [data-person]")];
agnosTrace.showView("history");
const chips = [...document.querySelectorAll("#history-people [data-person]")];
const marks = [...document.querySelectorAll(".history-mark")];
out.dots = String([...side, ...chips].filter((n) => n.querySelector(".history-swatch")).length);
out.side = side.map((n) => colour(n.querySelector(".kind-icon"))).join("|");
out.chip = chips.map((n) => colour(n.querySelector(".kind-icon"))).join("|");
out.distinct = String(new Set(side.map((n) => colour(n.querySelector(".kind-icon")))).size);
const first = marks.find((m) => m.dataset.kind === "human");
out.markshape = first ? first.firstElementChild.tagName : "";
""", "dots", "side", "chip", "distinct", "markshape")
        self.assertEqual("0", got["dots"])
        self.assertEqual(got["side"], got["chip"])
        self.assertEqual("3", got["distinct"])
        self.assertEqual("circle", got["markshape"])


if __name__ == "__main__":
    unittest.main()
