"""Tests of the History tab's controls, of the identities' icons, of the commit in the detail panel and of its git
graph (FTR-HST-001: RQ-HST-022 to RQ-HST-026; ADR-HST-001: DEC-HST-009 to DEC-HST-011), in a headless browser.

Run from the repository root: python -m unittest discover -s .github/skills/agnos-perf-center/tests -v
"""
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))

from test_history_page import NEEDS_BROWSER, START, add_history, found  # noqa: E402
from test_perf_center import BROWSER, generate, rendered_dom_after  # noqa: E402


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


COMMIT_PANEL = """
agnosTrace.showView("history");
const clickMark = (row, commit) => document.querySelector(`.history-row[data-key="${row}"] .history-mark[data-commit="${commit}"]`)
  .dispatchEvent(new MouseEvent("click", { bubbles: true }));
const text = (selector) => document.querySelector(selector)?.textContent || "";
const groups = () => [...document.querySelectorAll('#detail .detail-body .group[data-group]:not([data-group="graph"])')].map((g) => g.dataset.group + ":"
  + [...g.querySelectorAll(".link-item")].map((i) => i.querySelector(".id").textContent + "=" + i.querySelector(".link-rel").textContent).join(";")).join("|");
"""


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class CommitDetailTest(PageTestCase):
    """TASK-HST-016: RQ-HST-023, RQ-HST-007, RQ-HST-026 (DEC-HST-009)."""

    def run_script(self, script, *names):
        return super().run_script(COMMIT_PANEL + script, *names)

    def test_RQ_HST_023_given_a_mark_clicked_then_the_detail_panel_shows_the_commit_and_what_it_changed(self):
        got = self.run_script("""
clickMark("RQ-DEM-002", 4);
out.selected = agnosTrace.state.selected;
out.viewed = agnosTrace.state.view;
out.card = String(Boolean(document.getElementById("history-card")));
out.kindline = text("#detail .detail-top .detail-kind");
out.shownhash = text("#detail .detail-top .detail-id");
out.subject = text("#detail .detail-top .detail-title");
out.people = [...document.querySelectorAll("#detail .detail-top .history-person")].map((p) => (p.querySelector(".kind-icon") ? "icon:" : "") + p.textContent).join(",");
out.badges = [...document.querySelectorAll("#detail .detail-top .detail-badges .badge")].map((b) => b.textContent).join(",");
out.tags = [...document.querySelectorAll("#detail .detail-summary .tag")].map((t) => t.dataset.group).join(",");
out.groups = groups();
out.marked = [...document.querySelectorAll(".history-mark.is-selected")].map((m) => m.dataset.commit).join(",");
out.address = decodeURIComponent(location.hash);
""", "selected", "viewed", "card", "kindline", "shownhash", "subject", "people", "badges", "tags", "groups", "marked", "address")
        file = self.data["files"][0]["path"]
        self.assertEqual(("commit:a000000005", "history", "false"), (got["selected"], got["viewed"], got["card"]))
        self.assertIn("Commit", got["kindline"])
        self.assertIn("Agent", got["kindline"])
        self.assertEqual(("a000000005", "tests"), (got["shownhash"], got["subject"]))
        self.assertEqual("icon:Claude Opus 5.5", got["people"])
        self.assertEqual("7 lines,main", got["badges"])
        self.assertEqual("graph,RQ,FILE", got["tags"])                    # RQ-HST-025: the git graph's tag first
        self.assertEqual(f"RQ:RQ-DEM-002=3 lines|FILE:{file.rsplit('/', 1)[-1]}=4 lines", got["groups"])
        self.assertEqual("4", got["marked"])
        self.assertEqual("#commit:a000000005", got["address"])

    def test_RQ_HST_023_given_an_item_of_a_group_clicked_then_it_is_selected_and_the_mark_unmarked(self):
        got = self.run_script("""
clickMark("RQ-DEM-002", 4);
document.querySelector('#detail .group[data-group="RQ"] .id-link').click();
out.selected = agnosTrace.state.selected;
out.marked = String(document.querySelectorAll(".history-mark.is-selected").length);
""", "selected", "marked")
        self.assertEqual(("RQ-DEM-002", "0"), (got["selected"], got["marked"]))

    def test_RQ_HST_023_given_a_feature_and_its_requirement_changed_then_the_total_counts_their_lines_once(self):
        got = self.run_script("""
clickMark("RQ-DEM-001", 0);
out.badges = [...document.querySelectorAll("#detail .detail-top .detail-badges .badge")].map((b) => b.textContent).join(",");
out.groups = groups();
""", "badges", "groups")
        self.assertEqual("31 lines,main", got["badges"])                  # RQ-DEM-001's 6 lines are inside FTR-DEM-001's 31
        self.assertEqual("FTR:FTR-DEM-001=31 lines|RQ:RQ-DEM-001=6 lines", got["groups"])

    def test_RQ_HST_023_given_the_keyboard_on_a_mark_then_enter_selects_its_commit(self):
        got = self.run_script("""
document.querySelector('.history-row[data-key="RQ-DEM-001"] .history-mark[data-commit="2"]')
  .dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", bubbles: true }));
out.selected = agnosTrace.state.selected;
agnosTrace.showView("graph");
out.graph = String(document.getElementById("graph-empty").hidden);
""", "selected", "graph")
        self.assertEqual("commit:a000000003", got["selected"])
        self.assertEqual("false", got["graph"])                           # the graph shows no commit: its empty state


MERGE = "m000000001"


def branched_graph():
    """RQ-HST-024's case on the fixture's commits: main c0, c1, the merge, c5; feature/A c2, c3, c4 from c1."""
    node = lambda h, parents, branch, commit: {"hash": h, "parents": parents, "branch": branch, "commit": commit}  # noqa: E731
    merge = {**node(MERGE, [5, 2], 0, None), "date": "2026-03-10T10:00:00Z", "subject": "Merge branch 'feature/A'"}
    return {"branches": ["main", "feature/A"], "nodes": [
        node("a000000006", [1], 0, 5), merge, node("a000000005", [3], 1, 4), node("a000000004", [4], 1, 3),
        node("a000000003", [5], 1, 2), node("a000000002", [6], 0, 1), node("a000000001", [], 0, 0)]}


GIT_GRAPH = """
agnosTrace.select("commit:a000000004");
const graph = document.querySelector("#detail .git-graph");
const rows = () => [...graph.querySelectorAll(".git-row")];
"""


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class GitGraphTest(unittest.TestCase):
    """TASK-HST-017: RQ-HST-025, RQ-HST-014 (DEC-HST-011)."""

    @classmethod
    def setUpClass(cls):
        from test_history_page import history_block
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "page.html"
        generate(cls.path)
        add_history(cls.path, lambda data: history_block(data, graph=branched_graph()))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_script(self, script, *names):
        return found(rendered_dom_after(self.path, START + GIT_GRAPH + script), *names)

    def test_RQ_HST_025_given_a_commit_of_a_branch_then_its_lanes_names_dots_and_lines_are_drawn(self):
        got = self.run_script("""
out.rows = rows().map((r) => r.dataset.node).join(",");
out.current = rows().filter((r) => r.getAttribute("aria-current") === "true").map((r) => r.dataset.node).join(",");
out.lanes = [...graph.querySelectorAll(".git-dot")].map((d) => d.dataset.node + ":" + d.dataset.lane).join(",");
out.labels = [...graph.querySelectorAll(".git-label")].map((l) => l.textContent).join(",");
out.edges = String(graph.querySelectorAll(".git-edge").length);
out.curves = String([...graph.querySelectorAll(".git-edge")].filter((e) => e.getAttribute("d").includes("C")).length);
out.icons = String(graph.querySelectorAll(".git-row .kind-icon.is-identity").length);
out.ring = String(graph.querySelectorAll(".git-ring").length);
const stroke = (lane) => getComputedStyle(graph.querySelector(`.git-edge[data-lane="${lane}"]`)).stroke;
out.strokes = String(stroke(0) !== stroke(1));
""", "rows", "current", "lanes", "labels", "edges", "curves", "icons", "ring", "strokes")
        self.assertEqual("a000000006,m000000001,a000000005,a000000004,a000000003,a000000002,a000000001", got["rows"])
        self.assertEqual("a000000004", got["current"])
        self.assertEqual("a000000006:0,m000000001:0,a000000005:1,a000000004:1,a000000003:1,a000000002:0,a000000001:0",
                         got["lanes"])
        self.assertEqual("main,feature/A", got["labels"])
        self.assertEqual(("7", "2", "6", "1", "true"),
                         (got["edges"], got["curves"], got["icons"], got["ring"], got["strokes"]))

    def test_RQ_HST_025_given_the_git_graph_tag_then_it_shows_the_graph_alone_and_again_everything(self):
        got = self.run_script("""
const tag = document.querySelector('#detail .detail-summary .tag[data-group="graph"]');
out.tagtext = tag ? tag.textContent : "";
tag.click();
const shown = () => [...document.querySelectorAll("#detail .detail-body .group")].filter((g) => !g.hidden).map((g) => g.dataset.group).join(",");
out.alone = shown();
tag.click();
out.all = shown();
""", "tagtext", "alone", "all")
        self.assertEqual("Git graph 7", got["tagtext"])
        self.assertEqual("graph", got["alone"])
        self.assertEqual("graph,FILE", got["all"])                          # a000000004 changed one file only

    def test_RQ_HST_025_given_the_merge_row_clicked_then_the_merge_is_selected(self):
        got = self.run_script(f"""
rows().find((r) => r.dataset.node === "{MERGE}").click();
out.selected = agnosTrace.state.selected;
out.kindline = document.querySelector("#detail .detail-kind").textContent;
out.note = document.querySelector("#detail .detail-note")?.textContent || "";
out.named = String(rows().every((r) => r.tagName === "BUTTON" && r.getAttribute("aria-label").includes(r.dataset.node)
  && r.dataset.richTip === "true" && !r.getAttribute("title")));                     // RQ-HST-016: one rich tooltip
""", "selected", "kindline", "note", "named")
        self.assertEqual("commit:" + MERGE, got["selected"])
        self.assertIn("Merge", got["kindline"])
        self.assertIn("merge credits no one", got["note"].lower())
        self.assertEqual("true", got["named"])


if __name__ == "__main__":
    unittest.main()
