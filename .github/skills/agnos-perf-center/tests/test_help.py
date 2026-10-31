"""Tests of the Help dialog of the agnos-perf-center page (FTR-TRC-007, ADR-TRC-012: DEC-TRC-052), in a headless browser.

Run from the repository root: python -m unittest discover -s .github/skills/agnos-perf-center/tests -v
"""
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))

from test_delivery_page import add_delivery  # noqa: E402
from test_history_page import NEEDS_BROWSER, found  # noqa: E402
from test_perf_center import BROWSER, generate, rendered_dom_after  # noqa: E402

OPEN = """
const out = document.documentElement.dataset;
const dialog = document.getElementById("help-dialog");
const button = document.getElementById("help-button");
const shownGuides = () => [...dialog.querySelectorAll("[data-help]")].filter((s) => !s.hidden).map((s) => s.dataset.help).join(",");
const listed = () => [...dialog.querySelectorAll("#help-list button")].map((b) => b.dataset.topic).join(",");
"""


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class HelpDialogTest(unittest.TestCase):
    """TASK-TRC-087: RQ-TRC-101."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.plain = Path(cls.tmp.name) / "plain.html"
        generate(cls.plain)
        cls.path = Path(cls.tmp.name) / "page.html"
        generate(cls.path)
        add_delivery(cls.path)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_script(self, script, *names, path=None):
        return found(rendered_dom_after(path or self.path, OPEN + script), *names)

    def test_RQ_TRC_101_given_the_delivery_tab_when_help_opens_then_only_its_guide_shows_over_the_view(self):
        got = self.run_script("""
agnosTrace.showView("delivery");
button.click();
out.opened = String(dialog.open); out.guides = shownGuides();
out.current = agnosTrace.state.view;
""", "opened", "guides", "current")
        self.assertEqual({"opened": "true", "guides": "delivery", "current": "delivery"}, got)

    def test_RQ_TRC_101_given_the_list_when_a_tab_is_chosen_then_its_guide_replaces_the_other_and_the_view_stays(self):
        got = self.run_script("""
agnosTrace.showView("delivery");
button.click();
dialog.querySelector('#help-list button[data-topic="graph"]').click();
out.guides = shownGuides(); out.current = agnosTrace.state.view;
out.pressed = dialog.querySelector('#help-list [aria-current="true"]').dataset.topic;
""", "guides", "current", "pressed")
        self.assertEqual({"guides": "graph", "current": "delivery", "pressed": "graph"}, got)

    def test_RQ_TRC_101_given_a_page_without_history_then_the_list_has_no_history_nor_delivery(self):
        got = self.run_script("""
out.topics = listed();
""", "topics", path=self.plain)
        self.assertEqual("overview,matrix,graph,quality,common,about", got["topics"])

    def test_RQ_TRC_101_given_a_page_with_history_then_the_list_follows_the_tabs(self):
        got = self.run_script("""
out.topics = listed();
""", "topics")
        self.assertEqual("overview,matrix,graph,history,delivery,quality,common,about", got["topics"])

    def test_RQ_TRC_103_given_the_about_topic_then_it_links_to_the_author_s_profiles_in_a_new_tab(self):
        got = self.run_script("""
button.click();
dialog.querySelector('#help-list button[data-topic="about"]').click();
const anchors = [...dialog.querySelectorAll('[data-help="about"] a')];
out.hrefs = anchors.map((a) => a.href).join(" ");
out.safe = String(anchors.every((a) => a.target === "_blank" && a.rel.includes("noopener")
  && a.querySelector("svg").getBoundingClientRect().width > 0 && a.textContent.trim()));
out.guides = shownGuides();
""", "hrefs", "safe", "guides")
        self.assertEqual("https://github.com/spashx https://www.linkedin.com/in/64493197 "
                         "https://github.com/spashx/agnos-lightweight-process/blob/main/LICENSE.md", got["hrefs"])
        self.assertEqual(("true", "about"), (got["safe"], got["guides"]))

    def test_RQ_TRC_101_given_the_dialog_closed_then_the_focus_returns_to_the_control(self):
        got = self.run_script("""
button.focus();
button.click();
document.getElementById("help-close").click();
out.opened = String(dialog.open); out.focus = document.activeElement.id;
""", "opened", "focus")
        self.assertEqual({"opened": "false", "focus": "help-button"}, got)

    def test_RQ_TRC_101_given_the_dialog_when_resized_then_the_guide_follows_and_it_stays_above_its_minimum(self):
        got = self.run_script("""
button.click();
const body = document.getElementById("help-body");
out.resizable = getComputedStyle(dialog).resize;
const before = body.clientHeight;
dialog.style.height = `${dialog.offsetHeight - 40}px`;
out.follows = String(body.clientHeight < before);
dialog.style.height = "1px"; dialog.style.width = "1px";
out.floor = String(dialog.offsetHeight >= Number.parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--c-help-min-height"))
  || dialog.offsetHeight >= innerHeight);
""", "resizable", "follows", "floor")
        self.assertEqual({"resizable": "both", "follows": "true", "floor": "true"}, got)

    def test_RQ_TRC_101_given_a_guide_longer_than_the_dialog_then_only_the_guide_scrolls(self):
        got = self.run_script("""
agnosTrace.showView("history");
button.click();
dialog.style.height = "1px";                                  // down to its minimum: the guide is now the longer
const body = document.getElementById("help-body");
out.scrolls = String(body.scrollHeight > body.clientHeight && getComputedStyle(body).overflowY === "auto");
const before = document.getElementById("help-close").getBoundingClientRect().top;
body.scrollTop = 200;
out.fixed = String(document.getElementById("help-close").getBoundingClientRect().top === before);
out.bounded = String(dialog.getBoundingClientRect().height <= innerHeight);
""", "scrolls", "fixed", "bounded")
        self.assertEqual({"scrolls": "true", "fixed": "true", "bounded": "true"}, got)


if __name__ == "__main__":
    unittest.main()
