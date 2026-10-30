"""Tests of the grouped and "together" marks of the History timeline (TASK-TRC-068: RQ-TRC-086, RQ-TRC-089; DEC-TRC-044,
DEC-HST-005), in a headless browser, on pages whose data file is given a synthetic `history` block.

Run from the repository root: python -m unittest discover -s .github/skills/agnos-trace/tests -v
"""
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))

from test_history_page import AGENT, HUMAN, NEEDS_BROWSER, OPEN, PEOPLE, TOGETHER, add_history, found, history_block  # noqa: E402
from test_trace_matrix import BROWSER, generate, rendered_dom_after  # noqa: E402

ALICE, BOB, CLAUDE = 0, 1, 2
ROW_HOUR, ROW_ALICE, ROW_HUMANS, ROW_MIXED, ROW_PAIR, ROW_ALONE, ROW_INSTANT = (
    "RQ-DEM-001", "RQ-DEM-002", "RQ-DEM-003", "RQ-DEM-004", "RQ-DEM-005", "FTR-DEM-001", "FTR-DEM-002")   # rows in view


def commit(n, date, author, co_authors, kind):
    return {"hash": f"c{n:09d}", "date": date, "subject": f"subject {n}", "author": author, "coAuthors": co_authors,
            "kind": kind}


COMMITS = [
    commit(0, "2026-01-05T10:00:00Z", ALICE, [], HUMAN),            # 0-2: within an hour
    commit(1, "2026-01-05T10:20:00Z", ALICE, [], HUMAN),
    commit(2, "2026-01-05T10:40:00Z", BOB, [], HUMAN),
    commit(3, "2026-02-05T10:00:00Z", CLAUDE, [], AGENT),           # 3-4: an agent then a human, close
    commit(4, "2026-02-05T10:20:00Z", BOB, [], HUMAN),
    commit(5, "2026-03-05T10:00:00Z", ALICE, [CLAUDE], TOGETHER),   # 5-6: the same pair
    commit(6, "2026-03-05T10:20:00Z", CLAUDE, [ALICE], TOGETHER),
    commit(7, "2026-04-05T10:00:00Z", ALICE, [CLAUDE], TOGETHER),   # alone: Alice the author
    commit(8, "2026-05-05T10:00:00Z", CLAUDE, [BOB], TOGETHER),     # alone: the agent the author
    commit(9, "2026-06-05T10:00:00Z", ALICE, [], HUMAN),            # 9-10: seconds apart, never split
    commit(10, "2026-06-05T10:00:01Z", ALICE, [], HUMAN),
]
ELEMENTS = {
    ROW_HOUR: [[0, 4], [1, 4], [2, 4]],
    ROW_ALICE: [[0, 4], [1, 4]],
    ROW_HUMANS: [[0, 4], [2, 4]],
    ROW_MIXED: [[3, 4], [4, 4]],
    ROW_PAIR: [[5, 4], [6, 4]],
    ROW_ALONE: [[7, 4], [8, 400]],
    ROW_INSTANT: [[9, 4], [10, 4]],
}

HELPERS = """
const row = (key) => document.querySelector(`.history-row[data-key="${key}"]`);
const marks = (key) => [...row(key).querySelectorAll(".history-mark")];
const canvas = document.createElement("canvas").getContext("2d");
const rgb = (colour) => {
  const value = colour.startsWith("var(") ? getComputedStyle(document.documentElement).getPropertyValue(colour.slice(4, -1)).trim() : colour;
  canvas.fillStyle = value; canvas.fillRect(0, 0, 1, 1);
  return [...canvas.getImageData(0, 0, 1, 1).data].slice(0, 3).join(" ");
};
const fillOf = (node) => rgb(node.getAttribute("fill"));
const identity = (n) => rgb(`var(--c-history-identity-${n + 1})`);
"""


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class GroupedMarksTest(unittest.TestCase):
    """TASK-TRC-068: RQ-TRC-086, RQ-TRC-089."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "page.html"
        generate(cls.path)
        add_history(cls.path, lambda data: history_block(data, elements=ELEMENTS, files={}, commits=COMMITS, people=PEOPLE))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_script(self, script, *names):
        return found(rendered_dom_after(self.path, OPEN + HELPERS + script), *names)

    def test_RQ_TRC_086_given_three_commits_in_an_hour_then_one_mark_reads_3_and_zooming_on_it_draws_three(self):
        got = self.run_script(f"""
out.before = String(marks("{ROW_HOUR}").length);
out.count = marks("{ROW_HOUR}")[0].dataset.count;
out.text = marks("{ROW_HOUR}")[0].querySelector("text").textContent;
marks("{ROW_HOUR}")[0].dispatchEvent(new MouseEvent("click", {{ bubbles: true }}));
out.after = String(marks("{ROW_HOUR}").length);
""", "before", "count", "text", "after")
        self.assertEqual(("1", "3", "3", "3"), (got["before"], got["count"], got["text"], got["after"]))

    def test_RQ_TRC_086_given_a_group_then_its_tooltip_lists_its_commits(self):
        got = self.run_script(f"""
marks("{ROW_HOUR}")[0].dispatchEvent(new FocusEvent("focus"));
out.tip = document.getElementById("tip").textContent;
""", "tip")
        for text in ("3 commits", "Alice", "Bob", "subject 0", "subject 2"):
            self.assertIn(text, got["tip"], text)

    def test_RQ_TRC_086_given_a_groups_tooltip_then_each_commits_date_and_time_are_bold(self):
        got = self.run_script(f"""
marks("{ROW_HOUR}")[0].dispatchEvent(new FocusEvent("focus"));
const dates = [...document.querySelectorAll("#tip .tip-date")];
out.dates = String(dates.length);
out.bold = String(dates.every((d) => Number(getComputedStyle(d).fontWeight) >= 600));
out.first = dates[0]?.textContent || "";
out.subject = String(dates.every((d) => !d.textContent.includes("subject")));
""", "dates", "bold", "first", "subject")
        self.assertEqual(("3", "true", "true"), (got["dates"], got["bold"], got["subject"]))
        self.assertRegex(got["first"], r"\d{1,2}:\d{2}")

    def test_RQ_TRC_086_given_a_group_that_cannot_split_when_activated_then_its_newest_commit_is_selected(self):
        got = self.run_script(f"""
const view = agnosTrace.historyView;
const at = Date.parse("2026-06-05T10:00:00Z");
view.setSpan(at - 1800000, 3600000);
out.grouped = marks("{ROW_INSTANT}")[0].dataset.count;
marks("{ROW_INSTANT}")[0].dispatchEvent(new MouseEvent("click", {{ bubbles: true }}));
out.detail = document.querySelector("#detail .detail-id")?.textContent || "";
""", "grouped", "detail")
        self.assertEqual(("2", "c000000010"), (got["grouped"], got["detail"]))

    def test_RQ_TRC_086_given_a_group_then_its_colour_names_someone_or_is_neutral(self):
        got = self.run_script(f"""
const shape = (key) => marks(key)[0].firstElementChild;
out.alice = String(fillOf(shape("{ROW_ALICE}")) === identity(0));
out.humans = String(shape("{ROW_HUMANS}").getAttribute("fill") === "var(--c-history-group-fill)");
out.mixedkind = marks("{ROW_MIXED}")[0].dataset.kind;
out.mixedtag = shape("{ROW_MIXED}").tagName;
out.mixedfill = shape("{ROW_MIXED}").getAttribute("fill");
""", "alice", "humans", "mixedkind", "mixedtag", "mixedfill")
        self.assertEqual(("true", "true", "mixed", "rect", "var(--c-history-group-fill)"),
                         (got["alice"], got["humans"], got["mixedkind"], got["mixedtag"], got["mixedfill"]))

    def test_RQ_TRC_086_given_marks_of_different_lines_then_they_have_one_size_and_fill_the_row(self):
        got = self.run_script(f"""
const [small, large] = marks("{ROW_ALONE}").map((m) => m.firstElementChild.getAttribute("r"));
out.same = String(small === large);
out.share = String(2 * Number(small) >= 0.6 * parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--c-history-row-height")));
""", "same", "share")
        self.assertEqual(("true", "true"), (got["same"], got["share"]))

    def test_RQ_TRC_086_given_any_group_then_its_count_is_beside_the_symbol(self):
        got = self.run_script(f"""
const over = [];
for (const key of ["{ROW_HOUR}", "{ROW_ALICE}", "{ROW_HUMANS}", "{ROW_MIXED}", "{ROW_PAIR}"]) {{
  const mark = marks(key)[0];
  if (mark.querySelector("text").getBBox().x < mark.firstElementChild.getBBox().x + mark.firstElementChild.getBBox().width) over.push(key);
}}
out.over = over.join(",");
""", "over")
        self.assertEqual("", got.get("over", ""))

    def test_RQ_TRC_086_given_a_group_of_one_pair_then_it_keeps_both_colours(self):
        got = self.run_script(f"""
const mark = marks("{ROW_PAIR}")[0];
out.count = mark.dataset.count;
out.circle = String(fillOf(mark.firstElementChild) === identity(0));
out.diamond = String(fillOf(mark.querySelector(".history-mark-inner")) === identity(2));
""", "count", "circle", "diamond")
        self.assertEqual(("2", "true", "true"), (got["count"], got["circle"], got["diamond"]))

    def test_RQ_TRC_089_given_a_together_commit_then_a_circle_holds_a_diamond_with_no_ring_whoever_is_the_author(self):
        got = self.run_script(f"""
const look = (mark) => [mark.firstElementChild.tagName, fillOf(mark.firstElementChild), mark.querySelector(".history-mark-inner").tagName,
  fillOf(mark.querySelector(".history-mark-inner"))];
const [byHuman, byAgent] = marks("{ROW_ALONE}");
out.human = String(JSON.stringify(look(byHuman)) === JSON.stringify(["circle", identity(0), "path", identity(2)]));
out.agent = String(JSON.stringify(look(byAgent)) === JSON.stringify(["circle", identity(1), "path", identity(2)]));
out.rings = String(document.querySelectorAll(".history-ring").length);
""", "human", "agent", "rings")
        self.assertEqual(("true", "true", "0"), (got["human"], got["agent"], got["rings"]))

    def test_RQ_TRC_089_given_a_diamond_then_it_stays_within_the_marks_radius(self):
        got = self.run_script(f"""
const mark = marks("{ROW_ALONE}")[0];
const circle = mark.firstElementChild.getBBox();
const diamond = mark.querySelector(".history-mark-inner").getBBox();
out.inside = String(diamond.width <= circle.width && diamond.height <= circle.height);
""", "inside")
        self.assertEqual("true", got["inside"])

    def test_RQ_TRC_089_given_the_two_identities_with_one_colour_then_the_diamond_differs_in_both_themes(self):
        for theme in ("light", "dark"):
            with self.subTest(theme=theme):
                got = self.run_script(f"""
const root = document.documentElement;
root.dataset.theme = "{theme}";
root.style.setProperty("--c-history-identity-3", getComputedStyle(root).getPropertyValue("--c-history-identity-1"));
agnosTrace.historyView.redraw();
const [byHuman] = marks("{ROW_ALONE}");
const circle = byHuman.firstElementChild.getAttribute("fill");
const diamond = byHuman.querySelector(".history-mark-inner").getAttribute("fill");
out.gap = String(agnosTrace.historyView.colourGap(diamond, circle) >= parseFloat(getComputedStyle(root).getPropertyValue("--c-history-colour-gap")));
out.pale = String(rgb(circle) !== rgb(diamond));
""", "gap", "pale")
                self.assertEqual(("true", "true"), (got["gap"], got["pale"]))

    def test_RQ_TRC_086_given_a_count_then_it_meets_4_5_to_1_on_the_surface_in_both_themes(self):
        for theme in ("light", "dark"):
            with self.subTest(theme=theme):
                got = self.run_script(f"""
document.documentElement.dataset.theme = "{theme}";
agnosTrace.historyView.redraw();
const luminance = (text) => {{
  const [r, g, b] = text.split(" ").map((v) => {{ const c = Number(v) / 255; return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; }});
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}};
const contrast = (a, b) => {{ const [x, y] = [luminance(a), luminance(b)].sort((m, n) => n - m); return (x + 0.05) / (y + 0.05); }};
const weak = [];
for (const key of ["{ROW_HOUR}", "{ROW_ALICE}", "{ROW_HUMANS}", "{ROW_MIXED}", "{ROW_PAIR}"]) {{
  const mark = marks(key)[0];
  const ratio = contrast(rgb(getComputedStyle(mark.querySelector("text")).fill), rgb("var(--c-history-mark-outline)"));
  if (ratio < 4.5) weak.push(key + ":" + ratio.toFixed(2));
}}
out.weak = weak.join(",");
""", "weak")
                self.assertEqual("", got.get("weak", ""))

    def test_RQ_TRC_089_given_the_legend_then_it_shows_the_new_marks_and_no_ring(self):
        got = self.run_script("""
const legend = document.getElementById("history-legend");
out.rings = String(legend.querySelectorAll(".history-ring").length);
out.inner = String(legend.querySelectorAll(".history-mark-inner").length);
out.square = String(legend.querySelectorAll("rect").length);
out.text = legend.textContent;
""", "rings", "inner", "square", "text")
        self.assertEqual(("0", "1", "1"), (got["rings"], got["inner"], got["square"]))
        self.assertIn("mixed", got["text"])


if __name__ == "__main__":
    unittest.main()
