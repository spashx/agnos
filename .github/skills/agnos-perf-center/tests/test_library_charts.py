"""Tests of the library charts' helper of the agnos-perf-center page (FTR-TRC-005, ADR-TRC-010: DEC-TRC-042, DEC-TRC-043), in a
headless browser, with Apache ECharts loaded from cdnjs (TASK-TRC-065: RQ-TRC-085, RQ-TRC-087).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-perf-center/tests -v
"""
import re
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))

from test_perf_center import BROWSER, generate, rendered_dom_after  # noqa: E402

NEEDS_BROWSER = "no Chromium-family browser found, or cdnjs unreachable (the charts' library comes from it)"

# A bar chart of three items in a box of the page, drawn by the helper; Enter on an item records it.
DRAW = """
const out = document.documentElement.dataset;
const box = document.createElement("div");
box.style.width = "480px"; box.style.height = "240px";
document.body.append(box);
const items = ["first", "second", "third"];
const chart = agnosTrace.libraryChart(box, (theme) => ({
  xAxis: { type: "category", data: items }, yAxis: { type: "value" },
  series: [{ type: "bar", name: "Points", data: [3, 5, 8] }],
}), { label: "Test chart", description: "Three bars", items: items.map((_, i) => ({ seriesIndex: 0, dataIndex: i })),
  onActivate: (item) => { out.activated = String(item.dataIndex); } });
const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const normal = (colour) => { const probe = document.createElement("span"); probe.style.color = colour; document.body.append(probe);
  const value = getComputedStyle(probe).color; probe.remove(); return value; };
"""


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class LibraryChartTest(unittest.TestCase):
    """TASK-TRC-065: RQ-TRC-085, RQ-TRC-087."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "page.html"
        generate(cls.path)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_script(self, script, *names):
        dom = rendered_dom_after(self.path, DRAW + script)
        return dict(re.findall(r'data-(%s)="([^"]*)"' % "|".join(names), dom))

    def test_RQ_TRC_085_given_each_theme_then_the_chart_takes_the_resolved_tokens(self):
        got = self.run_script("""
const textOf = () => { const t = box.querySelector("svg text"); return t ? normal(t.getAttribute("fill")) : "none"; };
out.svg = box.querySelector("svg") ? "svg" : "none";
out.light = String(textOf() === normal(css("--s-text-muted")) || textOf() === normal(css("--s-text")));
out.font = String(agnosTrace.chartTheme().textStyle.fontFamily === css("--s-font-sans"));
document.documentElement.dataset.theme = "dark";
agnosTrace.redrawLibraryCharts();
out.dark = String(agnosTrace.chartTheme().textStyle.color === css("--s-text"));
out.darktext = String(textOf() === normal(css("--s-text-muted")) || textOf() === normal(css("--s-text")));
""", "svg", "light", "font", "dark", "darktext")
        self.assertEqual({"svg": "svg", "light": "true", "font": "true", "dark": "true", "darktext": "true"}, got)

    def test_RQ_TRC_087_given_the_chart_focused_then_the_arrows_show_each_item_and_enter_activates_it(self):
        got = self.run_script("""
out.tab = box.getAttribute("tabindex"); out.label = box.getAttribute("aria-label") || "";
box.focus();
box.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowRight", bubbles: true }));
box.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowRight", bubbles: true }));
out.tip = box.textContent;
box.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", bubbles: true }));
""", "tab", "label", "tip", "activated")
        self.assertEqual(("0", "Test chart"), (got["tab"], got["label"]))
        self.assertIn("second", got["tip"])
        self.assertEqual("1", got.get("activated"))

    def test_RQ_TRC_087_given_a_chart_then_aria_is_on_and_no_pattern_is_drawn(self):   # amended by TASK-TRC-070
        got = self.run_script("""
const option = chart.getOption();
out.aria = String(option.aria.enabled); out.decal = String(option.aria.decal.show);
out.description = box.getAttribute("aria-description") || "";
""", "aria", "decal", "description")
        self.assertEqual(("true", "false", "Three bars"), (got["aria"], got["decal"], got["description"]))

    def test_RQ_TRC_081_given_echarts_missing_then_the_chart_says_so(self):
        got = self.run_script("""
const other = document.createElement("div"); document.body.append(other);
const saved = window.echarts; window.echarts = undefined;
const none = agnosTrace.libraryChart(other, () => ({}), { label: "x", description: "x", items: [] });
window.echarts = saved;
out.missing = other.textContent; out.none = String(none);
""", "missing", "none")
        self.assertIn("Apache ECharts could not be loaded", got["missing"])
        self.assertEqual("null", got["none"])
