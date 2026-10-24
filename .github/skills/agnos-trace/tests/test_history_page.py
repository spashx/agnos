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


def history_block(data, elements=None, files=None, people=PEOPLE, commits=COMMITS):
    """A history block for a page's data: the given interventions, or a few on the fixture's elements and files."""
    first_file = data["files"][0]["path"]
    return {
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
out.total = rows.dataset.total;
out.first = rows.querySelector(".history-row[data-key]")?.dataset.key || "";
""", "total", "first")
        self.assertEqual(str(len(self.data["files"])), got["total"])
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

    def test_RQ_HST_007_given_a_mark_then_hover_shows_its_commit_and_click_pins_it(self):
        got = self.run_script("""
const mark = document.querySelector('.history-row[data-key="RQ-DEM-001"] .history-mark[data-commit="2"]');
mark.dispatchEvent(new FocusEvent("focus"));
const tip = document.getElementById("tip");
out.tip = tip.hidden ? "" : tip.textContent;
mark.dispatchEvent(new MouseEvent("click", { bubbles: true }));
const card = document.getElementById("history-card");
out.card = card.hidden ? "" : card.textContent;
""", "tip", "card")
        for text in ("a000000003", "Alice", "Claude Opus 5.5", "requirement refined", "2 lines"):
            self.assertIn(text, got["tip"], text)
        self.assertIn("a000000003", got["card"])

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
out.commits = [...new Set([...rows.querySelectorAll(".history-mark")].map((m) => m.dataset.commit))].sort().join(",");
document.getElementById("history-reset").click();
out.reset = String(rows.dataset.total === all);
out.after = [...new Set([...rows.querySelectorAll(".history-mark")].map((m) => m.dataset.commit))].sort().join(",");
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
out.colours = String(new Set(chips.map((c) => getComputedStyle(c.querySelector(".history-swatch")).backgroundColor)).size);
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
const keys = () => [...document.querySelectorAll("#history-rows .history-row[data-key]")].map((r) => r.dataset.key).join(",");
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
out.keys = [...document.querySelectorAll("#history-rows .history-row[data-key]")].map((r) => r.dataset.key).join(",");
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
