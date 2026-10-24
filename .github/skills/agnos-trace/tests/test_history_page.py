"""Tests of the History view of the agnos-trace page (FTR-HST-001, ADR-HST-001: DEC-HST-005, DEC-HST-006), in a
headless browser, on pages whose data file is given a synthetic `history` block.

Run from the repository root: python -m unittest discover -s .github/skills/agnos-trace/tests -v
"""
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))

import trace_matrix as tm  # noqa: E402
from test_trace_matrix import BROWSER, generate, rendered_dom_after, run_main  # noqa: E402

NEEDS_BROWSER = "no Chromium-family browser found (set AGNOS_TRACE_BROWSER)"
HUMAN, AGENT, TOGETHER = "human", "agent", "together"
PEOPLE = [
    {"name": "Alice", "names": ["Alice", "alice"], "emails": ["alice@example.com"], "mergedBy": ["email"], "kind": HUMAN,
     "commits": 3, "coCommits": 0},
    {"name": "Bob", "names": ["Bob"], "emails": ["bob@example.com"], "mergedBy": [], "kind": HUMAN, "commits": 2,
     "coCommits": 0},
    {"name": "Claude Opus 5.5", "names": ["Claude Opus 5.5"], "emails": ["noreply@anthropic.com"], "mergedBy": [],
     "kind": AGENT, "commits": 1, "coCommits": 2},
]
COMMITS = [
    {"hash": "a000000001", "date": "2026-01-05T10:00:00Z", "subject": "feature drafted", "author": 0, "coAuthors": [],
     "kind": HUMAN},
    {"hash": "a000000002", "date": "2026-01-20T10:00:00Z", "subject": "plan", "author": 1, "coAuthors": [], "kind": HUMAN},
    {"hash": "a000000003", "date": "2026-02-02T10:00:00Z", "subject": "requirement refined", "author": 0,
     "coAuthors": [2], "kind": TOGETHER},
    {"hash": "a000000004", "date": "2026-02-18T10:00:00Z", "subject": "code", "author": 1, "coAuthors": [2],
     "kind": TOGETHER},
    {"hash": "a000000005", "date": "2026-03-03T10:00:00Z", "subject": "tests", "author": 2, "coAuthors": [], "kind": AGENT},
    {"hash": "a000000006", "date": "2026-03-20T10:00:00Z", "subject": "fix", "author": 0, "coAuthors": [], "kind": HUMAN},
]


def linear_graph(commits):
    """RQ-HST-024: the commits on one branch, newest first, each the child of the one before it in date."""
    newest = list(reversed(range(len(commits))))
    return {"branches": ["main"], "nodes": [{"hash": commits[ci]["hash"], "parents": [n + 1] if n + 1 < len(newest) else [],
                                             "branch": 0, "commit": ci} for n, ci in enumerate(newest)]}


def history_block(data, elements=None, files=None, people=PEOPLE, commits=COMMITS, graph=None):
    """A history block for a page's data: the given interventions, or a few on the fixture's elements and files."""
    first_file = data["files"][0]["path"]
    return {
        "graph": graph or linear_graph(commits),
        "limits": {"since": None, "depth": None, "commits": len(commits), "first": commits[0]["date"],
                   "last": commits[-1]["date"], "shallow": False},
        "people": people, "commits": commits,
        "interventions": {
            "elements": elements if elements is not None else
            {"FTR-DEM-001": [[0, 31]], "RQ-DEM-001": [[0, 6], [2, 2], [5, 3]], "RQ-DEM-002": [[4, 3]],
             "TASK-DEM-001": [[1, 5]]},
            "files": files if files is not None else {first_file: [[3, 10], [4, 4]]},
        },
    }


def add_history(page, make=history_block):
    """Writes a history block into the data files of a generated page; returns the data."""
    json_path, script_path = tm.data_paths(page)
    data = json.loads(json_path.read_text(encoding="utf-8"))
    data["history"] = make(data)
    tm.write_outputs(page, data, data["meta"]["title"])
    return data


def found(dom, *names):
    return dict(re.findall(r'data-(%s)="([^"]*)"' % "|".join(names), dom))


OPEN = """
const out = document.documentElement.dataset;
agnosTrace.showView("history");
"""


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class TimelineTest(unittest.TestCase):
    """TASK-HST-004: RQ-HST-007, RQ-HST-014."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.plain = Path(cls.tmp.name) / "plain.html"
        generate(cls.plain)
        cls.path = Path(cls.tmp.name) / "page.html"
        generate(cls.path)
        cls.data = add_history(cls.path)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_script(self, script, *names, path=None):
        return found(rendered_dom_after(path or self.path, OPEN + script), *names)

    def test_RQ_HST_007_given_a_page_without_history_then_there_is_no_history_tab(self):
        got = found(rendered_dom_after(self.plain, """
const out = document.documentElement.dataset;
const tab = document.querySelector('.tab[data-view="history"]');
out.tab = tab && !tab.hidden ? "shown" : "none";
"""), "tab")
        self.assertEqual("none", got["tab"])

    def test_RQ_HST_007_given_the_requirements_angle_then_one_row_per_element_with_its_marks(self):
        got = self.run_script("""
const rows = document.getElementById("history-rows");
out.total = rows.dataset.total;
const row = rows.querySelector('.history-row[data-key="RQ-DEM-001"]');
out.marks = String(row ? row.querySelectorAll(".history-mark").length : -1);
out.commits = row ? [...row.querySelectorAll(".history-mark")].map((m) => m.dataset.commit).join(",") : "";
out.tab = document.querySelector('.tab[data-view="history"]').hidden ? "hidden" : "shown";
""", "total", "marks", "commits", "tab")
        defined = [e for e in self.data["elements"] if e["kind"] == "element"]
        groups = len({e["type"] for e in defined})
        self.assertEqual("shown", got["tab"])
        self.assertEqual(str(len(defined) + groups), got["total"])
        self.assertEqual("3", got["marks"])
        self.assertEqual("0,2,5", got["commits"])

    def test_RQ_HST_007_given_the_code_angle_then_the_rows_are_the_files(self):
        got = self.run_script("""
document.querySelector('#history-angle [data-angle="code"]').click();
const rows = document.getElementById("history-rows");
out.files = String(rows.querySelectorAll('.history-row[data-key^="file:"]').length);   // RQ-HST-019: under their folders
out.first = rows.querySelector('.history-row[data-key^="file:"]')?.dataset.key || "";
""", "files", "first")
        self.assertEqual(str(len(self.data["files"])), got["files"])
        self.assertTrue(got["first"].startswith("file:"), got["first"])

    def test_RQ_HST_007_given_the_wheel_over_the_timeline_then_it_zooms_around_the_pointer(self):
        got = self.run_script("""
const plot = document.getElementById("history-plot");
const view = agnosTrace.historyView;
const box = plot.getBoundingClientRect();
const [t0, t1] = view.span();
const x = view.xOf((t0 + t1) / 2 - (t1 - t0) / 4);
const anchor = view.timeAt(x);
plot.dispatchEvent(new WheelEvent("wheel", { deltaY: -120, clientX: x, clientY: box.top + 20, bubbles: true, cancelable: true }));
const [u0, u1] = view.span();
out.narrower = String(u1 - u0 < t1 - t0);
out.kept = String(Math.abs(view.timeAt(x) - anchor) < (u1 - u0) / 100);
""", "narrower", "kept")
        self.assertEqual(("true", "true"), (got["narrower"], got["kept"]))

    def test_RQ_HST_007_given_the_keyboard_then_it_zooms_pans_and_fits(self):
        got = self.run_script("""
const plot = document.getElementById("history-plot");
const view = agnosTrace.historyView;
const spanSize = () => { const [a, b] = view.span(); return b - a; };
const spanStart = () => view.span()[0];
const w0 = spanSize();
plot.dispatchEvent(new KeyboardEvent("keydown", { key: "+", bubbles: true }));
out.zoomed = String(spanSize() < w0);
const s0 = spanStart();
plot.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowRight", bubbles: true }));
out.pan = String(spanStart() > s0);
plot.dispatchEvent(new KeyboardEvent("keydown", { key: "0", bubbles: true }));
out.fit = String(Math.abs(spanSize() - w0) < 1);
""", "zoomed", "pan", "fit")
        self.assertEqual(("true", "true", "true"), (got["zoomed"], got["pan"], got["fit"]))

    def test_RQ_HST_007_given_a_mark_then_hover_shows_its_commit_and_click_selects_it_in_the_detail_panel(self):
        got = self.run_script("""
const mark = document.querySelector('.history-row[data-key="RQ-DEM-001"] .history-mark[data-commit="2"]');
mark.dispatchEvent(new FocusEvent("focus"));
const tip = document.getElementById("tip");
out.tip = tip.hidden ? "" : tip.textContent;
mark.dispatchEvent(new MouseEvent("click", { bubbles: true }));
out.detail = document.querySelector("#detail .detail-id")?.textContent || "";
""", "tip", "detail")
        for text in ("a000000003", "Alice", "Claude Opus 5.5", "requirement refined", "2 lines"):
            self.assertIn(text, got["tip"], text)
        self.assertEqual("a000000003", got["detail"])                     # RQ-HST-007 as amended: RQ-HST-023

    def test_RQ_HST_007_given_a_row_label_when_clicked_then_the_element_is_selected(self):
        got = self.run_script("""
document.querySelector('.history-row[data-key="RQ-DEM-001"] .history-label').click();
out.selected = agnosTrace.state.selected;
""", "selected")
        self.assertEqual("RQ-DEM-001", got["selected"])

    def test_RQ_HST_014_given_marks_then_their_shape_tells_the_kind_and_each_has_a_name(self):
        got = self.run_script("""
const marks = [...document.querySelectorAll(".history-mark")];
out.shapes = [...new Set(marks.map((m) => m.dataset.kind + ":" + m.firstElementChild.tagName))].sort().join(",");
out.named = String(marks.every((m) => m.getAttribute("aria-label") && m.getAttribute("tabindex") === "0"));
""", "shapes", "named")
        self.assertEqual("agent:path,human:circle,together:circle", got["shapes"])
        self.assertEqual("true", got["named"])


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class FiguresAndFiltersTest(unittest.TestCase):
    """TASK-HST-005: RQ-HST-008, RQ-HST-009, RQ-HST-014."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "page.html"
        generate(cls.path)
        add_history(cls.path)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_script(self, script, *names, path=None):
        return found(rendered_dom_after(path or self.path, OPEN + script), *names)

    def test_RQ_HST_008_given_the_tab_then_the_figures_count_the_commits_shown_and_the_share_with_an_agent(self):
        got = self.run_script("""
const figure = (key) => document.querySelector(`#history-kpis [data-figure="${key}"] .kpi-value`)?.textContent || "";
out.commits = figure("commits");
out.humans = figure("humans");
out.agents = figure("agents");
out.share = figure("share");
""", "commits", "humans", "agents", "share")
        # the requirements angle shows commits 0, 1, 2, 4 and 5; 2 (together) and 4 (agent) have an agent
        self.assertEqual(("5", "2", "1", "40 %"), (got["commits"], got["humans"], got["agents"], got["share"]))

    def test_RQ_HST_009_given_one_identity_selected_then_only_its_commits_and_rows_stay(self):
        got = self.run_script("""
document.querySelector('#history-people [data-person="1"]').click();
const rows = document.getElementById("history-rows");
out.rowcount = rows.dataset.total;
out.keys = [...rows.querySelectorAll(".history-row[data-key]")].map((r) => r.dataset.key).join(",");
out.commits = document.querySelector('#history-kpis [data-figure="commits"] .kpi-value').textContent;
out.kept = document.getElementById("history-kept").textContent;
document.getElementById("history-show-empty").click();
out.withempty = rows.dataset.total;
""", "rowcount", "keys", "commits", "kept", "withempty")
        self.assertEqual("TASK-DEM-001", got["keys"])                 # Bob's commits are 1 and 3; 3 is on a file only
        self.assertEqual("2", got["rowcount"])                           # the row and its type heading
        self.assertEqual("1", got["commits"])
        self.assertIn("1 row", got["kept"])
        self.assertGreater(int(got["withempty"]), 2)

    def test_RQ_HST_009_given_the_kind_agents_then_only_commits_with_an_agent_stay_and_reset_shows_all(self):
        got = self.run_script("""
const rows = document.getElementById("history-rows");
const all = rows.dataset.total;
document.querySelector('#history-kind [data-kind="agent"]').click();
// the commits of the rows shown, from the view's state: the rows below the window are not in the document (RQ-HST-013)
const shownCommits = () => [...new Set(agnosTrace.historyView.state.rows.filter((r) => !r.group)
  .flatMap((r) => r.marks.map(([ci]) => ci)))].sort().join(",");
out.commits = shownCommits();
document.getElementById("history-reset").click();
out.reset = String(rows.dataset.total === all);
out.after = shownCommits();
""", "commits", "reset", "after")
        self.assertEqual("2,4", got["commits"])
        self.assertEqual("true", got["reset"])
        self.assertEqual("0,1,2,4,5", got["after"])

    def test_RQ_HST_008_given_the_zoom_then_the_band_period_follows_it(self):
        got = self.run_script("""
const band = document.getElementById("history-band");
const view = agnosTrace.historyView;
out.fit = band.dataset.unit;
const [a] = view.span();
view.setSpan(a, 10 * 86400000);
out.days = band.dataset.unit;
out.bars = String(band.querySelectorAll(".history-bar").length > 0);
""", "fit", "days", "bars")
        self.assertEqual(("week", "day", "true"), (got["fit"], got["days"], got["bars"]))

    def test_RQ_HST_014_given_20_identities_then_each_has_its_own_colour_and_its_kind_icon(self):
        people = [{"name": f"P{n}", "names": [f"P{n}"], "emails": [f"p{n}@x"], "mergedBy": [],
                   "kind": AGENT if n % 5 == 0 else HUMAN, "commits": 1, "coCommits": 0} for n in range(20)]
        commits = [{"hash": f"b{n:09d}", "date": f"2026-02-{n + 1:02d}T10:00:00Z", "subject": "s", "author": n,
                    "coAuthors": [], "kind": people[n]["kind"]} for n in range(20)]
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "page.html"
            generate(page)
            add_history(page, lambda data: history_block(data, {"RQ-DEM-001": [[n, 1] for n in range(20)]}, {},
                                                         people, commits))
            got = self.run_script("""
const chips = [...document.querySelectorAll("#history-people [data-person]")];
out.chips = String(chips.length);
out.colours = String(new Set(chips.map((c) => getComputedStyle(c.querySelector(".kind-icon")).color)).size);   // RQ-HST-026
out.icons = chips.map((c) => c.querySelector(".kind-icon").classList.contains("kind-agent") ? "a" : "h").join("");
""", "chips", "colours", "icons", path=page)
        self.assertEqual(("20", "20"), (got["chips"], got["colours"]))
        self.assertEqual("".join("a" if n % 5 == 0 else "h" for n in range(20)), got["icons"])


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class EntryPointsTest(unittest.TestCase):
    """TASK-HST-006: RQ-HST-010, RQ-HST-011, RQ-HST-014."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.plain = Path(cls.tmp.name) / "plain.html"
        generate(cls.plain)
        cls.path = Path(cls.tmp.name) / "page.html"
        generate(cls.path)
        cls.data = add_history(cls.path)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_script(self, script, *names, path=None):
        return found(rendered_dom_after(path or self.path, START + script), *names)

    def test_RQ_HST_010_given_a_history_then_the_sidebar_lists_the_identities_with_counts_and_kinds(self):
        got = self.run_script("""
const items = [...document.querySelectorAll("#history-shortcuts [data-person]")];
out.names = items.map((i) => i.querySelector(".history-name").textContent).join(",");
out.counts = items.map((i) => i.querySelector(".chip-count").textContent).join(",");
out.kinds = items.map((i) => i.querySelector(".kind-icon").classList.contains("kind-agent") ? "agent" : "human").join(",");
out.section = document.getElementById("side-history").hidden ? "hidden" : "shown";
""", "names", "counts", "kinds", "section")
        self.assertEqual("shown", got["section"])
        self.assertEqual("Alice,Bob,Claude Opus 5.5", got["names"])
        self.assertEqual("3,2,3", got["counts"])
        self.assertEqual("human,human,agent", got["kinds"])

    def test_RQ_HST_010_given_the_pointer_on_an_identity_then_its_tooltip_tells_its_names_and_how_they_were_merged(self):
        got = self.run_script("""
const item = document.querySelector('#history-shortcuts [data-person="0"]');
item.dispatchEvent(new FocusEvent("focus"));
const tip = document.getElementById("tip");
out.tip = tip.hidden ? "" : tip.textContent;
""", "tip")
        for text in ("Alice", "alice", "alice@example.com", "merged by e-mail"):
            self.assertIn(text, got["tip"], text)

    def test_RQ_HST_010_given_an_identity_clicked_then_the_history_tab_opens_filtered_on_it(self):
        got = self.run_script("""
document.querySelector('#history-shortcuts [data-person="1"]').click();
out.opened = agnosTrace.state.view;
out.pressed = [...document.querySelectorAll('#history-people [aria-pressed="true"]')].map((c) => c.dataset.person).join(",");
out.keys = [...document.querySelectorAll("#history-rows .history-row[data-key]")].map((r) => r.dataset.key).join(",");
""", "opened", "pressed", "keys")
        self.assertEqual(("history", "1", "TASK-DEM-001"), (got["opened"], got["pressed"], got["keys"]))

    def test_RQ_HST_011_given_a_feature_when_its_history_button_is_pressed_then_the_tab_shows_it_and_what_it_contains(self):
        got = self.run_script("""
agnosTrace.select("FTR-DEM-001");
document.querySelector('#detail [data-action="history"]').click();
const keys = () => [...document.querySelectorAll("#history-rows .history-row[data-key]")].map((r) => r.dataset.key)
  .filter((key) => !key.startsWith("dir:")).join(",");                              // RQ-HST-019: the folders aside
out.opened = agnosTrace.state.view;
out.keys = keys();
out.chip = document.getElementById("history-scope").textContent;
document.querySelector('#history-angle [data-angle="code"]').click();
out.code = keys();
""", "opened", "keys", "chip", "code")
        self.assertEqual("history", got["opened"])
        self.assertEqual("FTR-DEM-001,RQ-DEM-001,RQ-DEM-002,RQ-DEM-003,RQ-DEM-004,RQ-DEM-005", got["keys"])
        self.assertIn("FTR-DEM-001", got["chip"])
        scope = {"FTR-DEM-001", "RQ-DEM-001", "RQ-DEM-002", "RQ-DEM-003", "RQ-DEM-004", "RQ-DEM-005"}
        citing = sorted({"file:" + s for s, d, kind, _ in self.data["edges"] if kind == "code" and d in scope})
        self.assertTrue(citing)
        self.assertEqual(",".join(citing), got["code"])

    def test_RQ_HST_011_given_the_scope_chip_removed_then_every_row_shows_with_the_filters_kept(self):
        got = self.run_script("""
const rows = document.getElementById("history-rows");
agnosTrace.showView("history");
out.all = rows.dataset.total;
agnosTrace.select("RQ-DEM-001");
document.querySelector('#detail [data-action="history"]').click();
document.querySelector('#history-kind [data-kind="human"]').click();
out.scoped = [...rows.querySelectorAll(".history-row[data-key]")].map((r) => r.dataset.key).join(",");
document.querySelector("#history-scope button").click();
out.chipgone = String(document.getElementById("history-scope").hidden);
out.kindpressed = document.querySelector('#history-kind [aria-pressed="true"]').dataset.kind;
document.getElementById("history-reset").click();
out.back = String(rows.dataset.total === out.all);
""", "all", "scoped", "chipgone", "kindpressed", "back")
        self.assertEqual("RQ-DEM-001", got["scoped"])
        self.assertEqual(("true", "human", "true"), (got["chipgone"], got["kindpressed"], got["back"]))

    def test_RQ_HST_011_given_a_file_when_its_history_button_is_pressed_then_the_code_angle_shows_it(self):
        first = "file:" + self.data["files"][0]["path"]
        got = self.run_script(f"""
agnosTrace.select({json.dumps(first)});
document.querySelector('#detail [data-action="history"]').click();
out.anglepressed = document.querySelector('#history-angle [aria-pressed="true"]').dataset.angle;
out.keys = [...document.querySelectorAll("#history-rows .history-row[data-key]")].map((r) => r.dataset.key)
  .filter((key) => !key.startsWith("dir:")).join(",");                              // RQ-HST-019: the folders aside
""", "anglepressed", "keys")
        self.assertEqual(("code", first), (got["anglepressed"], got["keys"]))

    def test_RQ_HST_010_given_no_history_then_there_is_no_history_section_nor_button(self):
        got = self.run_script("""
agnosTrace.select("FTR-DEM-001");
out.section = document.getElementById("side-history").hidden ? "hidden" : "shown";
out.button = String(Boolean(document.querySelector('#detail [data-action="history"]')));
""", "section", "button", path=self.plain)
        self.assertEqual(("hidden", "false"), (got["section"], got["button"]))


START = """
const out = document.documentElement.dataset;
"""

# RQ-HST-016: the titles an element and its containers carry, up to the page, for "one tooltip at once".
TITLED_ANCESTORS = """
const titledAncestors = (node) => {
  const found = [];
  for (let n = node; n && n.nodeType === 1; n = n.parentElement || n.parentNode) {
    if (n.getAttribute("title")) found.push(n.id || n.className.baseVal || n.className || n.tagName);
    if (n.querySelector && n.querySelector(":scope > title")) found.push("svg title of " + (n.id || n.tagName));
  }
  return found.join("|");
};
"""


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class TooltipComponentTest(unittest.TestCase):
    """TASK-HST-009: RQ-HST-016, RQ-HST-018, RQ-HST-010, RQ-HST-014."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "page.html"
        generate(cls.path)
        add_history(cls.path)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_script(self, script, *names):
        return found(rendered_dom_after(self.path, START + TITLED_ANCESTORS + script), *names)

    def test_RQ_HST_016_given_a_radar_point_then_one_rich_tooltip_and_no_title_around_it(self):
        got = self.run_script("""
agnosTrace.showView("quality");
const point = document.querySelector("#quality-charts .radar-point");
point.dispatchEvent(new FocusEvent("focus"));
const tip = document.getElementById("tip");
out.shown = String(!tip.hidden);
out.head = tip.firstElementChild ? getComputedStyle(tip.firstElementChild).fontWeight : "";
out.titles = titledAncestors(point);
out.tips = String(document.querySelectorAll('[role="tooltip"]:not([hidden])').length);
""", "shown", "head", "titles", "tips")
        self.assertEqual(("true", "", "1"), (got["shown"], got["titles"], got["tips"]))
        self.assertGreaterEqual(int(got["head"]), 600)

    def test_RQ_HST_016_given_a_commit_mark_then_one_rich_tooltip_and_no_title_around_it(self):
        got = self.run_script("""
agnosTrace.showView("history");
const mark = document.querySelector(".history-mark");
mark.dispatchEvent(new FocusEvent("focus"));
const tip = document.getElementById("tip");
out.shown = String(!tip.hidden);
out.titles = titledAncestors(mark);
""", "shown", "titles")
        self.assertEqual(("true", ""), (got["shown"], got["titles"]))

    def test_RQ_HST_016_given_the_charts_then_each_is_named_by_aria_label_and_described(self):
        got = self.run_script("""
agnosTrace.showView("quality");
const charts = [...document.querySelectorAll("#quality-charts svg[role=img]")];
out.named = String(charts.length === 3 && charts.every((c) => c.getAttribute("aria-label") && c.querySelector("desc")
  && !c.querySelector(":scope > title")));
""", "named")
        self.assertEqual("true", got["named"])

    def test_RQ_HST_010_given_identities_then_the_merge_line_shows_only_when_merged_and_the_chip_tip_is_the_sidebar_one(self):
        got = self.run_script("""
const tip = document.getElementById("tip");
const read = (node) => { node.dispatchEvent(new FocusEvent("focus")); const text = tip.hidden ? "" : tip.textContent;
  node.dispatchEvent(new FocusEvent("blur")); return text; };
out.alice = read(document.querySelector('#history-shortcuts [data-person="0"]'));
out.claude = read(document.querySelector('#history-shortcuts [data-person="2"]'));
agnosTrace.showView("history");
out.chip = read(document.querySelector('#history-people [data-person="0"]'));
out.chiptitle = document.querySelector('#history-people [data-person="0"]').getAttribute("title") || "";
""", "alice", "claude", "chip", "chiptitle")
        self.assertIn("merged by e-mail", got["alice"])
        self.assertNotIn("merge", got["claude"].lower())
        self.assertEqual(got["alice"], got["chip"])
        self.assertEqual("", got["chiptitle"])


READ_TIP = """
const tip = document.getElementById("tip");
const readTip = (node) => { node.dispatchEvent(new FocusEvent("focus")); const head = tip.querySelector(".tip-head")?.textContent || "";
  const text = tip.hidden ? "" : tip.textContent; node.dispatchEvent(new FocusEvent("blur")); return [head, text]; };
"""
# RQ-HST-017: the business items, which raise the rich tooltip and carry no browser title
RICH_TARGETS = (".id-link", ".finding", ".badge-covered", ".badge-indirect", ".badge-uncovered", ".meta-item",
                "#quality-shortcuts .quality-shortcut", ".fix-link", ".check-score", ".check-risk", ".check-count",
                ".grade-chip", ".scale-step", ".report-trigram", ".history-row[data-key] .history-label", "#history-limits", ".stack-part",
                ".coverage-item")


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class RichContentTest(unittest.TestCase):
    """TASK-HST-010: RQ-HST-017, RQ-HST-016."""

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
        return found(rendered_dom_after(self.path, START + READ_TIP + script), *names)

    def test_RQ_HST_017_given_a_requirement_node_of_the_graph_then_its_tooltip_gives_id_title_coverage_and_location(self):
        got = self.run_script("""
agnosTrace.select("RQ-DEM-001");
agnosTrace.showView("graph");
const content = agnosTrace.graph.tipContent("RQ-DEM-001");
out.head = content.head;
out.lines = content.lines.join("|");
const cy = agnosTrace.graph.instance();
cy.getElementById("RQ-DEM-001").emit("mouseover");
setTimeout(() => { out.hovered = tip.hidden ? "" : tip.querySelector(".tip-head").textContent;
  out.containertitle = document.getElementById("cy").getAttribute("title") || ""; }, 1500);
""", "head", "lines", "hovered", "containertitle")
        self.assertEqual("RQ-DEM-001", got["head"])
        for part in ("Requirement", "Covered directly", "Covered", "FTR-DEM-001-demo-feature.md:8-12"):
            self.assertIn(part, got["lines"], part)
        self.assertEqual(("RQ-DEM-001", ""), (got["hovered"], got["containertitle"]))

    def test_RQ_HST_017_given_a_file_node_then_its_bold_line_is_the_file_name_and_its_path_is_below(self):
        path = self.data["files"][0]["path"]
        got = self.run_script(f"""
const content = agnosTrace.graph.tipContent({json.dumps("file:" + path)});
out.head = content.head;
out.lines = content.lines.join("|");
""", "head", "lines")
        self.assertEqual(path.rsplit("/", 1)[-1], got["head"])
        self.assertIn(path, got["lines"])
        self.assertIn("IDs cited", got["lines"])

    def test_RQ_HST_017_given_a_relation_then_its_tooltip_names_it_its_ends_and_its_proof(self):
        got = self.run_script("""
agnosTrace.select("RQ-DEM-001");
agnosTrace.showView("graph");
const edge = agnosTrace.graph.instance().edges().filter((e) => e.data("kind") === "code")[0];
const content = agnosTrace.graph.edgeTipContent(edge.id());
out.head = content.head;
out.lines = content.lines.join("|");
""", "head", "lines")
        self.assertEqual("Cited in code", got["head"])
        self.assertIn("→ RQ-DEM-001", got["lines"])
        self.assertRegex(got["lines"], r"L\d+ ")                          # a proof line with its number

    def test_RQ_HST_017_given_a_matrix_id_a_check_score_and_a_history_label_then_their_tooltips_hold_their_facts(self):
        got = self.run_script("""
agnosTrace.showView("matrix");
const [idHead, idText] = readTip([...document.querySelectorAll('#matrix-table .id-link')].find((b) => b.textContent === "RQ-DEM-001"));
out.idhead = idHead; out.idtext = idText;
agnosTrace.showView("quality");
const [, scoreText] = readTip(document.querySelector("#quality-list .check-score"));
out.score = scoreText;
agnosTrace.showView("history");
const [labelHead, labelText] = readTip(document.querySelector('.history-row[data-key="RQ-DEM-001"] .history-label'));
out.labelhead = labelHead; out.labeltext = labelText;
""", "idhead", "idtext", "score", "labelhead", "labeltext")
        self.assertEqual("RQ-DEM-001", got["idhead"])
        self.assertIn("Covered directly", got["idtext"])
        self.assertRegex(got["score"], r"Score \d+\.\d / 10")
        self.assertIn("population", got["score"])
        self.assertEqual("RQ-DEM-001", got["labelhead"])
        for part in ("3 changes", "2 identities", "Last change", "Alice"):
            self.assertIn(part, got["labeltext"], part)

    def test_RQ_HST_016_given_the_business_items_then_none_has_a_browser_title_and_each_raises_the_rich_tooltip(self):
        got = self.run_script(f"""
agnosTrace.select("RQ-DEM-002");
document.getElementById("expand-checks").click();
agnosTrace.showView("history");
const bad = [];
for (const selector of {json.dumps(list(RICH_TARGETS))}) {{
  const found = [...document.querySelectorAll(selector)];
  if (!found.length) bad.push(selector + " (none)");
  for (const node of found) if (node.getAttribute("title") || node.dataset.richTip !== "true") bad.push(selector);
}}
out.bad = [...new Set(bad)].join(",");
""", "bad")
        self.assertEqual("", got["bad"])


TREE_FILES = ["src/a/x.py", "src/a/y.py", "src/b/z.py", "tools/deep/er/w.py"]


def tree_history(data):
    """The fixture's data given four files in folders, and commits on them: 1 on x.py, 3 on y.py, 4 on z.py."""
    data["files"] = [{"path": path, "ids": 0} for path in TREE_FILES]
    return history_block(data, {}, {"src/a/x.py": [[1, 2]], "src/a/y.py": [[3, 4]], "src/b/z.py": [[4, 1]],
                                    "tools/deep/er/w.py": [[0, 1]]})


TREE_ROWS = """
const rows = () => [...document.querySelectorAll("#history-rows .history-row")].map((r) =>
  (r.dataset.key || "") + ":" + (r.querySelector(".history-label")?.style.getPropertyValue("--history-depth") || ""));
const marksOf = (key) => [...document.querySelectorAll(`#history-rows .history-row[data-key="${key}"] .history-mark`)]
  .map((m) => m.dataset.commit).join(",");
"""


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class FolderTreeTest(unittest.TestCase):
    """TASK-HST-011: RQ-HST-019."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "page.html"
        generate(cls.path)
        add_history(cls.path, tree_history)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_script(self, script, *names):
        return found(rendered_dom_after(self.path, START + TREE_ROWS + """
agnosTrace.showView("history");
document.querySelector('#history-angle [data-angle="code"]').click();
""" + script), *names)

    def test_RQ_HST_019_given_files_in_folders_then_the_rows_are_a_tree_indented_by_depth(self):
        got = self.run_script("out.rows = rows().join(\"|\");", "rows")
        self.assertEqual("dir:src:0|dir:src/a:1|file:src/a/x.py:2|file:src/a/y.py:2|dir:src/b:1|file:src/b/z.py:2|"
                         "dir:tools/deep/er:0|file:tools/deep/er/w.py:1", got["rows"])

    def test_RQ_HST_019_given_a_folder_closed_then_its_files_hide_and_it_keeps_their_marks(self):
        got = self.run_script("""
const folder = () => document.querySelector('#history-rows .history-row[data-key="dir:src/a"] .history-label');
out.marks = marksOf("dir:src/a");
folder().click();
out.closed = rows().join("|");
out.expanded = folder().getAttribute("aria-expanded");
out.closedmarks = marksOf("dir:src/a");
agnosTrace.historyView.setSpan(agnosTrace.historyView.span()[0], 20 * 86400000);
document.querySelector('#history-kind [data-kind="human"]').click();
out.still = String(!rows().some((r) => r.startsWith("file:src/a/")));
document.querySelector('#history-kind [data-kind="all"]').click();
folder().click();
out.opened = String(rows().some((r) => r.startsWith("file:src/a/x.py")));
""", "marks", "closed", "expanded", "closedmarks", "still", "opened")
        self.assertEqual("1,3", got["marks"])
        self.assertNotIn("file:src/a/x.py", got["closed"])
        self.assertIn("file:src/b/z.py", got["closed"])
        self.assertEqual(("false", "1,3", "true", "true"), (got["expanded"], got["closedmarks"], got["still"], got["opened"]))


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class LabelColumnAndRowFilterTest(unittest.TestCase):
    """TASK-HST-012: RQ-HST-020, RQ-HST-021."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "page.html"
        generate(cls.path)
        cls.data = add_history(cls.path)
        tokens = tm.load_tokens(tm.TOKENS_PATH)["global"]
        cls.px = {name: float(tokens[name].removesuffix("px")) for name in
                  ("dimension.history-label", "dimension.history-label-min", "dimension.history-label-max", "space.16")}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_script(self, script, *names):
        return found(rendered_dom_after(self.path, START + """
agnosTrace.showView("history");
const keys = () => [...document.querySelectorAll("#history-rows .history-row[data-key]")].map((r) => r.dataset.key).join(",");
const type = (text) => { const box = document.getElementById("history-filter"); box.value = text;
  box.dispatchEvent(new Event("input", { bubbles: true })); };
""" + script), *names)

    def test_RQ_HST_020_given_the_splitter_then_the_label_column_resizes_by_steps_stops_at_its_bounds_and_resets(self):
        got = self.run_script("""
const bar = document.getElementById("history-split");
const press = (key, n) => { for (let i = 0; i < n; i += 1) bar.dispatchEvent(new KeyboardEvent("keydown", { key, bubbles: true })); };
const first = (selector) => Number.parseFloat(getComputedStyle(document.querySelector(selector)).gridTemplateColumns);
out.start = String(first(".history-axis-row"));
press("ArrowRight", 3);
out.three = String(first(".history-axis-row"));
out.aligned = String([".history-band-row", ".history-overview-row", "#history-rows .history-row"].every((s) => first(s) === first(".history-axis-row")));
out.stored = localStorage.getItem("agnos-trace-history-label") || "";
press("ArrowRight", 200);
out.max = String(first(".history-axis-row"));
press("ArrowLeft", 400);
out.min = String(first(".history-axis-row"));
bar.dispatchEvent(new MouseEvent("dblclick", { bubbles: true }));
out.reset = String(first(".history-axis-row"));
out.role = bar.getAttribute("role") + ":" + bar.getAttribute("tabindex");
""", "start", "three", "aligned", "stored", "max", "min", "reset", "role")
        base, step = self.px["dimension.history-label"], self.px["space.16"]
        self.assertEqual(base, float(got["start"]))
        self.assertEqual(base + 3 * step, float(got["three"]))
        self.assertEqual("true", got["aligned"])
        self.assertEqual(base + 3 * step, float(got["stored"]))
        self.assertEqual(self.px["dimension.history-label-max"], float(got["max"]))
        self.assertEqual(self.px["dimension.history-label-min"], float(got["min"]))
        self.assertEqual(base, float(got["reset"]))
        self.assertEqual("separator:0", got["role"])

    def test_RQ_HST_021_given_a_text_then_only_the_rows_holding_it_stay_and_the_figures_follow(self):
        got = self.run_script("""
const all = keys();
type("covered");
out.rows = keys();
out.headings = String(document.querySelectorAll("#history-rows .history-row.is-group").length);
out.commits = document.querySelector('#history-kpis [data-figure="commits"] .kpi-value').textContent;
type("");
out.back = String(keys() === all);
""", "rows", "headings", "commits", "back")
        self.assertEqual("RQ-DEM-001,RQ-DEM-002,RQ-DEM-003,RQ-DEM-004", got["rows"])
        self.assertEqual(("1", "4", "true"), (got["headings"], got["commits"], got["back"]))

    def test_RQ_HST_021_given_a_type_turned_off_then_no_row_of_it_stays(self):
        got = self.run_script("""
document.querySelector('#history-types [data-type="TASK"]').click();
out.tasks = String(keys().split(",").filter((k) => k.startsWith("TASK-")).length);
out.pressed = document.querySelector('#history-types [data-type="TASK"]').getAttribute("aria-pressed");
document.querySelector('#history-angle [data-angle="code"]').click();
out.typeshidden = String(document.getElementById("history-types").hidden);
""", "tasks", "pressed", "typeshidden")
        self.assertEqual(("0", "false", "true"), (got["tasks"], got["pressed"], got["typeshidden"]))

    def test_RQ_HST_021_given_the_code_angle_and_a_text_then_only_the_files_holding_it_stay_with_their_folders(self):
        target = self.data["files"][0]["path"]
        name = target.rsplit("/", 1)[-1]
        got = self.run_script(f"""
document.querySelector('#history-angle [data-angle="code"]').click();
type({json.dumps(name)});
out.files = keys().split(",").filter((k) => !k.startsWith("dir:")).join(",");
out.folders = String(keys().split(",").filter((k) => k.startsWith("dir:")).length > 0);
""", "files", "folders")
        expected = ",".join("file:" + f["path"] for f in self.data["files"] if name.lower() in f["path"].lower())
        self.assertEqual(expected, got["files"])
        self.assertEqual("true", got["folders"])


def luminance(hex_colour):
    def channel(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(int(hex_colour[i:i + 2], 16) / 255) for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def oklch_hex(lightness, chroma, hue):
    """An oklch colour in sRGB hex, clipped to the gamut (the page's golden-angle identity colours)."""
    import math
    a, b = chroma * math.cos(math.radians(hue)), chroma * math.sin(math.radians(hue))
    l_ = (lightness + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m_ = (lightness - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s_ = (lightness - 0.0894841775 * a - 1.2914855480 * b) ** 3
    rgb = (4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
           -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
           -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_)
    encode = lambda x: 12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055  # noqa: E731
    return "#" + "".join(f"{round(max(0.0, min(1.0, encode(max(0.0, x)))) * 255):02X}" for x in rgb)


MARK_CONTRAST = 3.0                                   # RQ-HST-014's metric: marks 3:1, texts 4.5:1
TEXT_CONTRAST = 4.5
GOLDEN_SHOWN = 60                                     # the golden-angle identities checked past the twelve tokens


class ContrastTest(unittest.TestCase):
    """TASK-HST-007: RQ-HST-014."""

    @classmethod
    def setUpClass(cls):
        tokens = tm.load_tokens(tm.TOKENS_PATH)
        cls.g, cls.s, cls.c = tokens["global"], tokens["semantic"], tokens["component"]

    def colour(self, semantic, theme):
        ref = self.s[semantic]
        return self.g[ref[theme] if isinstance(ref, dict) else ref]

    def backgrounds(self):
        return [self.colour(self.c["card-bg"], theme) for theme in tm.THEMES]

    def test_RQ_HST_014_given_the_identity_and_kind_colours_then_each_mark_meets_3_to_1_in_both_themes(self):
        number = lambda name: float(self.g[self.s[self.c[name]]])  # noqa: E731
        golden = [oklch_hex(number("history-identity-lightness-alt" if turn % 2 else "history-identity-lightness"),
                            number("history-identity-chroma"),
                            (number("history-identity-hue-start") + turn * number("history-identity-hue-step")) % 360)
                  for turn in range(GOLDEN_SHOWN)]
        shared = [self.colour(f"identity-{n}", tm.THEMES[0]) for n in range(1, 13)] + golden     # one value for both themes
        pairs = [(m, b) for m in shared for b in self.backgrounds()]
        pairs += [(self.colour(f"kind-{k}", theme), back) for k in ("human", "agent", "together")
                  for theme, back in zip(tm.THEMES, self.backgrounds())]                         # each theme on its own surface
        weak = [(m, round(contrast(m, b), 2)) for m, b in pairs if contrast(m, b) < MARK_CONTRAST]
        self.assertEqual([], weak)

    def test_RQ_HST_014_given_the_texts_of_the_view_then_they_meet_4_5_to_1_and_use_no_weaker_token(self):
        for name in ("text", "text-muted"):
            for theme, back in zip(tm.THEMES, self.backgrounds()):
                self.assertGreaterEqual(contrast(self.colour(name, theme), back), TEXT_CONTRAST, (name, theme))
        css = (tm.ASSETS_DIR / "matrix.css").read_text(encoding="utf-8")
        history_rules = [line for line in css.splitlines() if re.match(r"^\.(history|tip)", line) and "--s-text-subtle" in line]
        self.assertEqual([], history_rules)


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class KeyboardTest(unittest.TestCase):
    """TASK-HST-007: RQ-HST-014: every control, row and mark of the view has a keyboard path and a name."""

    def test_RQ_HST_014_given_the_view_then_every_control_and_mark_is_focusable_and_named(self):
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "page.html"
            generate(page)
            add_history(page)
            got = found(rendered_dom_after(page, START + """
agnosTrace.showView("history");
const view = document.getElementById("view-history");
const items = [...view.querySelectorAll("button, input, [role=separator], .history-mark, .history-bar, #history-plot")];
const unreachable = items.filter((n) => n.tabIndex < 0 || n.disabled).map((n) => n.id || n.className.baseVal || n.className);
const unnamed = items.filter((n) => !(n.getAttribute("aria-label") || n.textContent.trim() || n.getAttribute("title")
  || n.closest("label")?.textContent.trim()))
  .map((n) => n.id || n.className.baseVal || n.className);
out.count = String(items.length);
out.unreachable = [...new Set(unreachable)].join(",");
out.unnamed = [...new Set(unnamed)].join(",");
"""), "count", "unreachable", "unnamed")
        self.assertGreater(int(got["count"]), 20)
        self.assertEqual(("", ""), (got["unreachable"], got["unnamed"]))


class WordingTest(unittest.TestCase):
    """TASK-HST-009: RQ-HST-018: no ID of the skill's process in the page's own wording."""

    def test_RQ_HST_018_given_the_page_script_and_skeleton_then_no_string_names_an_id_of_the_process(self):
        id_re = re.compile(tm.ID_PATTERN)
        script = (tm.ASSETS_DIR / "matrix.js").read_text(encoding="utf-8")
        code = re.sub(r"/\*.*?\*/", "", script, flags=re.S)                  # block comments
        code = re.sub(r"(^|\s)//.*$", "", code, flags=re.M)                     # line comments, not "://" in a string
        named = [line.strip() for line in code.splitlines() if id_re.search(line)]
        skeleton = re.sub(r"<!--.*?-->", "", (tm.ASSETS_DIR / "matrix.html").read_text(encoding="utf-8"), flags=re.S)
        skeleton = re.sub(r"/\*.*?\*/", "", skeleton, flags=re.S)
        self.assertEqual([], named)
        self.assertEqual([], id_re.findall(skeleton))


def large_process(root, count):
    """A process of one feature holding count requirements, with its index."""
    folder = root / "process" / "1.requirements"
    folder.mkdir(parents=True)
    name = "process/1.requirements/FTR-BIG-001-big.md"
    tris = ("BIG", "BIH", "BII")
    per_tri = 999
    lines = ["# FTR-BIG-001: Big", ""] + [f"### RQ-{tris[n // per_tri]}-{n % per_tri + 1:03d}: R{n}" for n in range(count)]
    (root / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
    ids = [line.split(":")[0][4:] for line in lines[2:]]
    rows = ["# AGNOS process index", f"@{name}", f"FTR-BIG-001|1-{len(lines)}||Big"]
    rows += [f"{i}|{n + 3}-{n + 3}||R" for n, i in enumerate(ids)]
    (root / "process" / "INDEX.idx.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (root / "src").mkdir()
    (root / "src" / "code.py").write_text("# RQ-BIG-001\n", encoding="utf-8")
    return root / "process", root / "src", ids


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class VirtualRowsTest(unittest.TestCase):
    """TASK-HST-004: RQ-HST-007, RQ-HST-013 (DEC-HST-005: only the rows in view are in the document)."""

    def test_RQ_HST_013_given_2000_rows_then_fewer_than_100_row_elements_are_in_the_document(self):
        with tempfile.TemporaryDirectory() as tmp:
            process, sources, ids = large_process(Path(tmp), 1999)
            page = Path(tmp) / "page.html"
            code, _, err = run_main(["--process", str(process), "--sources", str(sources), "--out", str(page),
                                     "--generated-at", "x"])
            self.assertEqual(0, code, err)
            add_history(page, lambda data: history_block(data, {i: [[n % len(COMMITS), 1]] for n, i in enumerate(ids)}))
            got = found(rendered_dom_after(page, OPEN + """
const rows = document.getElementById("history-rows");
out.total = rows.dataset.total;
out.drawn = String(rows.querySelectorAll(".history-row").length);
const scroller = document.getElementById("history-scroll");
scroller.scrollTop = scroller.scrollHeight / 2;
scroller.dispatchEvent(new Event("scroll"));
out.after = String(rows.querySelectorAll(".history-row").length);
out.middle = String([...rows.querySelectorAll(".history-row[data-key]")].some((r) => r.dataset.key.startsWith("RQ-BIH")));
"""), "total", "drawn", "after", "middle")
        self.assertEqual("2002", got["total"])              # 1,999 requirements, 1 feature, 2 type headings
        self.assertLess(int(got["drawn"]), 100)
        self.assertLess(int(got["after"]), 100)
        self.assertEqual("true", got["middle"])


if __name__ == "__main__":
    unittest.main()
