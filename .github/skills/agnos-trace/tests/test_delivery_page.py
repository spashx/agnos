"""Tests of the Delivery figures of the agnos-trace page (FTR-TRC-004, ADR-TRC-009: DEC-TRC-038), in a headless browser,
on a page whose data file is given synthetic `history` and `delivery` blocks.

Run from the repository root: python -m unittest discover -s .github/skills/agnos-trace/tests -v
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))

import history  # noqa: E402
import trace_matrix as tm  # noqa: E402
from test_history_page import NEEDS_BROWSER, found, linear_graph  # noqa: E402
from test_trace_matrix import BROWSER, generate, rendered_dom_after  # noqa: E402

HUMAN, AGENT, TOGETHER = "human", "agent", "together"
PEOPLE = [
    {"name": "Alice", "names": ["Alice"], "emails": ["alice@example.com"], "mergedBy": [], "kind": HUMAN, "commits": 3,
     "coCommits": 0},
    {"name": "Claude Opus 5.5", "names": ["Claude Opus 5.5"], "emails": ["noreply@anthropic.com"], "mergedBy": [],
     "kind": AGENT, "commits": 2, "coCommits": 1},
]
COMMITS = [
    {"hash": "d000000000", "date": "2026-09-15T10:00:00Z", "subject": "start", "author": 0, "coAuthors": [], "kind": HUMAN},
    {"hash": "d000000001", "date": "2026-10-15T10:00:00Z", "subject": "feat(DEM): TASK-B1", "author": 0, "coAuthors": [],
     "kind": HUMAN},
    {"hash": "d000000002", "date": "2026-10-22T10:00:00Z", "subject": "feat(DEM): TASK-A1", "author": 0, "coAuthors": [1],
     "kind": TOGETHER},
    {"hash": "d000000003", "date": "2026-10-23T10:00:00Z", "subject": "feat(DEM): TASK-A2", "author": 1, "coAuthors": [],
     "kind": AGENT},
    {"hash": "d000000004", "date": "2026-10-27T10:00:00Z", "subject": "fix(DEM): TASK-A3", "author": 1, "coAuthors": [],
     "kind": AGENT},
]
TASKS = [
    ["TASK-DEM-101", "M", False, 1, 12, "feat", False, None],          # period B, Alice
    ["TASK-DEM-001", "L", True, 2, 40, "feat", False, None],           # period A, Alice and Claude; a task of the fixture
    ["TASK-DEM-103", "S", False, 3, 5, None, False, None],             # period A, Claude, a subject with no type
    ["TASK-DEM-104", "S", False, 4, 3, "fix", True, None],             # period A, Claude, reworked
    ["TASK-DEM-105", "S", False, 3, 0, "feat", False, "created-done"],  # set aside
]
ACTIVE_DAYS = {"0": ["2026-09-15", "2026-10-15", "2026-10-22"], "1": ["2026-10-22", "2026-10-23", "2026-10-27"]}


def add_delivery(page):
    """Writes the synthetic history and delivery blocks into the data files of a generated page."""
    json_path, _ = tm.data_paths(page)
    data = json.loads(json_path.read_text(encoding="utf-8"))
    data["history"] = {"graph": linear_graph(COMMITS), "people": PEOPLE, "commits": COMMITS,
                       "limits": {"since": "6.weeks", "depth": None, "commits": len(COMMITS), "first": COMMITS[0]["date"],
                                  "last": COMMITS[-1]["date"], "shallow": False},
                       "interventions": {"elements": {}, "files": {}}}
    data["delivery"] = {"tasks": TASKS, "activeDays": ACTIVE_DAYS, "settings": history.load_delivery_settings()}
    tm.write_outputs(page, data, data["meta"]["title"])


OPEN = """
const out = document.documentElement.dataset;
const d = agnosTrace.delivery;
const bounds = d.bounds();
const [A, B] = d.defaults(bounds);
const all = d.filter();
const fmt = (f) => [f.tasks, f.points, f.activeDays, f.throughput === null ? "-" : f.throughput.toFixed(3),
  f.reworkRate === null ? "-" : f.reworkRate.toFixed(3)].join(",");
"""


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class DeliveryFiguresTest(unittest.TestCase):
    """TASK-TRC-058: RQ-TRC-070, RQ-TRC-071, RQ-TRC-072, RQ-TRC-073."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "page.html"
        generate(cls.path)
        add_delivery(cls.path)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_script(self, script, *names):
        return found(rendered_dom_after(self.path, OPEN + script), *names)

    def test_RQ_TRC_072_given_a_cut_history_then_the_first_day_is_left_out_and_the_defaults_are_the_last_two_weeks(self):
        got = self.run_script("""
out.first = bounds.first; out.last = bounds.last;
out.a = A.from + ".." + A.to; out.b = B.from + ".." + B.to;
""", "first", "last", "a", "b")
        self.assertEqual(("2026-09-16", "2026-10-27"), (got["first"], got["last"]))
        self.assertEqual(("2026-10-21..2026-10-27", "2026-10-14..2026-10-20"), (got["a"], got["b"]))

    def test_RQ_TRC_072_given_a_history_shorter_than_two_weeks_then_the_defaults_are_its_two_halves(self):
        got = self.run_script("""
const [a, b] = d.defaults({ first: "2026-10-20", last: "2026-10-27" });
out.a = a.from + ".." + a.to; out.b = b.from + ".." + b.to;
""", "a", "b")
        self.assertEqual(("2026-10-24..2026-10-27", "2026-10-20..2026-10-23"), (got["a"], got["b"]))

    def test_RQ_TRC_072_given_ready_made_ranges_then_those_beyond_the_history_read_are_disabled(self):
        got = self.run_script("""
const presets = Object.fromEntries(d.presets(bounds).map((p) => [p.key, p.enabled]));
out.last30 = String(presets["last-30"]); out.last90 = String(presets["last-90"]);
""", "last30", "last90")
        self.assertEqual(("true", "false"), (got["last30"], got["last90"]))

    def test_RQ_TRC_072_given_a_date_outside_the_history_read_then_it_is_refused_with_a_message(self):
        got = self.run_script("""
out.outside = d.checkDay("2026-09-01", bounds) || "";
out.inside = d.checkDay("2026-10-01", bounds) || "accepted";
out.bad = d.checkDay("2026-13-45", bounds) || "";
""", "outside", "inside", "bad")
        self.assertIn("outside the history read", got["outside"])
        self.assertEqual("accepted", got["inside"])
        self.assertIn("not a date", got["bad"])

    def test_RQ_TRC_070_given_the_two_periods_then_points_active_days_throughput_and_rework_rate(self):
        got = self.run_script("""
out.a = fmt(d.figures(A, all, bounds)); out.b = fmt(d.figures(B, all, bounds));
const fa = d.figures(A, all, bounds), fb = d.figures(B, all, bounds);
out.change = d.variation(fa.throughput, fb.throughput).toFixed(3);
""", "a", "b", "change")
        # A: L 8 + S 1 + S 1 = 10 points over 3 active days, 1 task of 3 reworked; B: M 3 over 1 day
        self.assertEqual("3,10,3,3.333,0.333", got["a"])
        self.assertEqual("1,3,1,3.000,0.000", got["b"])
        self.assertEqual("0.111", got["change"])

    def test_RQ_TRC_070_given_the_filters_then_the_figures_count_only_the_tasks_kept(self):
        got = self.run_script("""
const tierL = d.filter(); tierL.tiers.add("L");
out.tier = fmt(d.figures(A, tierL, bounds));
const text = d.filter(); text.text = "task-dem-103";
out.text = fmt(d.figures(A, text, bounds));
const agents = d.filter(); agents.kinds.add("agent");
out.agents = fmt(d.figures(A, agents, bounds));
const noRetier = d.filter(); noRetier.reTiered = false;
out.retier = fmt(d.figures(A, noRetier, bounds));
""", "tier", "text", "agents", "retier")
        self.assertEqual("1,8,3,2.667,0.000", got["tier"])
        self.assertEqual("1,1,3,0.333,0.000", got["text"])
        self.assertEqual("2,2,3,0.667,0.500", got["agents"])     # the agent's own days: 22, 23 and 27 October
        self.assertEqual("2,2,3,0.667,0.500", got["retier"])

    def test_RQ_TRC_070_given_each_identity_then_its_points_by_tier_and_its_own_throughput(self):
        got = self.run_script("""
out.people = d.perIdentity(A, all, bounds).map((e) => [e.person, e.byTier.S, e.byTier.M, e.byTier.L, e.activeDays,
  e.throughput.toFixed(3)].join(":")).join(" ");
""", "people")
        self.assertEqual("0:0:0:8:1:8.000 1:2:0:8:3:3.333", got["people"])

    def test_RQ_TRC_073_given_six_weeks_then_day_and_week_and_given_twenty_then_month_too(self):
        got = self.run_script("""
out.six = d.grains(bounds).join(",");
out.twenty = d.grains({ first: "2026-01-01", last: "2026-05-31" }).join(",");
out.week = d.bucketOf("2026-10-22", "week"); out.month = d.bucketOf("2026-10-22", "month");
const weeks = d.pointsOverTime(all, "week", bounds);
const lastWeek = weeks[weeks.length - 1];
out.lastweek = [lastWeek.bucket, lastWeek.byTier.S, lastWeek.byTier.M, lastWeek.byTier.L].join(":");
""", "six", "twenty", "week", "month", "lastweek")
        self.assertEqual("day,week", got["six"])
        self.assertEqual("day,week,month", got["twenty"])
        self.assertEqual(("2026-10-19", "2026-10"), (got["week"], got["month"]))
        self.assertEqual("2026-10-26:1:0:0", got["lastweek"])


TAB = """
const out = document.documentElement.dataset;
agnosTrace.showView("delivery");
const figure = (key) => document.querySelector(`#delivery-kpis [data-figure="${key}"]`);
const ab = (key) => { const f = figure(key); return f ? [f.dataset.a, f.dataset.b, f.dataset.change].join("|") : ""; };
"""


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class DeliveryTabTest(unittest.TestCase):
    """TASK-TRC-059: RQ-TRC-072, RQ-TRC-074, RQ-TRC-076, RQ-TRC-079."""

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
        return found(rendered_dom_after(path or self.path, TAB + script), *names)

    def test_RQ_TRC_074_given_a_delivery_block_then_the_tab_stands_between_history_and_quality(self):
        got = self.run_script("""
out.tabs = [...document.querySelectorAll(".tab")].filter((t) => !t.hidden).map((t) => t.dataset.view).join(",");
out.shown = document.getElementById("view-delivery").hidden ? "hidden" : "shown";
""", "tabs", "shown")
        self.assertEqual("overview,graph,matrix,history,delivery,quality", got["tabs"])
        self.assertEqual("shown", got["shown"])

    def test_RQ_TRC_074_given_no_delivery_block_then_there_is_no_delivery_tab(self):
        got = found(rendered_dom_after(self.plain, """
const out = document.documentElement.dataset;
const tab = document.querySelector('.tab[data-view="delivery"]');
out.tab = tab && !tab.hidden ? "shown" : "none";
"""), "tab")
        self.assertEqual("none", got["tab"])

    def test_RQ_TRC_074_given_the_tab_then_the_band_gives_the_four_figures_for_a_b_and_their_variation(self):
        got = self.run_script("""
out.tasks = ab("tasks"); out.bandpoints = ab("points"); out.bandthroughput = ab("throughput"); out.rework = ab("rework");
out.text = figure("throughput").textContent;
""", "tasks", "bandpoints", "bandthroughput", "rework", "text")
        self.assertEqual("3|1|2.000", got["tasks"])
        self.assertEqual("10|3|2.333", got["bandpoints"])
        self.assertEqual("3.333|3.000|0.111", got["bandthroughput"])
        self.assertEqual("0.333|0.000|", got["rework"])                 # no variation from zero
        self.assertIn("+11 %", got["text"])

    def test_RQ_TRC_076_given_the_tag_l_alone_then_the_band_counts_l_tasks_only(self):
        got = self.run_script("""
document.querySelector('#delivery-tiers [data-tier="L"]').click();
out.tasks = ab("tasks"); out.bandpoints = ab("points");
document.getElementById("delivery-filter").value = "TASK-DEM-104";
document.getElementById("delivery-filter").dispatchEvent(new Event("input"));
out.text = ab("tasks");
""", "tasks", "bandpoints", "text")
        self.assertEqual("1|0|", got["tasks"])
        self.assertEqual("8|0|", got["bandpoints"])
        self.assertEqual("0|0|", got["text"])                           # TASK-DEM-104 is an S task: the tag L leaves it out

    def test_RQ_TRC_076_given_a_delivery_commit_with_no_type_then_its_tag_is_none(self):
        got = self.run_script("""
out.types = [...document.querySelectorAll("#delivery-types [data-type]")].map((c) => c.dataset.type).join(",");
""", "types")
        self.assertEqual("feat,fix,none", got["types"])

    def test_RQ_TRC_072_given_a_date_outside_the_history_read_then_it_is_refused_and_the_period_kept(self):
        got = self.run_script("""
const from = document.getElementById("delivery-from-a");
out.min = from.min; out.max = from.max;
from.value = "2026-09-01";
from.dispatchEvent(new Event("change"));
const message = document.getElementById("delivery-message");
out.message = message.hidden ? "" : message.textContent;
out.kept = from.value;
""", "min", "max", "message", "kept")
        self.assertEqual(("2026-09-16", "2026-10-27"), (got["min"], got["max"]))
        self.assertIn("outside the history read", got["message"])
        self.assertEqual("2026-10-21", got["kept"])

    def test_RQ_TRC_072_given_the_ready_made_ranges_then_one_beyond_the_history_is_disabled_and_says_why(self):
        got = self.run_script("""
const option = document.querySelector('#delivery-preset-a option[value="last-90"]');
out.disabled = String(option.disabled); out.why = option.title;
const select = document.getElementById("delivery-preset-b");
select.value = "previous-14"; select.dispatchEvent(new Event("change"));
out.periodb = document.getElementById("delivery-from-b").value + ".." + document.getElementById("delivery-to-b").value;
out.read = document.getElementById("delivery-read").textContent;
""", "disabled", "why", "periodb", "read")
        self.assertEqual("true", got["disabled"])
        self.assertIn("beyond the history read", got["why"])
        self.assertEqual("2026-09-30..2026-10-13", got["periodb"])
        self.assertIn("2026-09-15", got["read"])
        self.assertIn("2026-10-27", got["read"])

    def test_RQ_TRC_079_given_the_toolbar_then_every_control_has_an_accessible_name(self):
        got = self.run_script("""
const controls = [...document.querySelectorAll("#view-delivery input, #view-delivery select, #view-delivery button")];
out.unnamed = controls.filter((c) => !(c.getAttribute("aria-label") || c.closest("label") || c.textContent.trim()))
  .map((c) => c.id || c.outerHTML.slice(0, 40)).join(",");
out.controls = String(controls.length);
""", "unnamed", "controls")
        self.assertEqual("", got["unnamed"])
        self.assertGreater(int(got["controls"]), 10)


CHARTS = """
const chartOf = (key) => echarts.getInstanceByDom(document.querySelector(`#delivery-charts [data-chart="${key}"]`));
const optionOf = (key) => chartOf(key).getOption();
const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const sumOf = (series, index) => series.reduce((sum, s) => sum + (s.data[index]?.value ?? s.data[index] ?? 0), 0);
const resolved = (colour) => { const p = document.createElement("span"); p.style.color = colour; document.body.append(p);
  const value = getComputedStyle(p).color; p.remove(); return value; };
const periodColour = (key) => resolved(css(`--c-delivery-period-${key}`));
const noPattern = (option) => option.series.every((s) => !s.itemStyle || !s.itemStyle.decal || s.itemStyle.decal.symbol === "none");
"""


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class DeliveryChartsTest(unittest.TestCase):
    """TASK-TRC-066: RQ-TRC-083, RQ-TRC-075 (as amended), RQ-TRC-087."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "page.html"
        generate(cls.path)
        add_delivery(cls.path)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_script(self, script, *names):
        return found(rendered_dom_after(self.path, TAB + CHARTS + script), *names)

    def test_RQ_TRC_083_given_the_tab_then_three_library_charts_are_drawn_each_named_and_reached_by_tab(self):
        got = self.run_script("""
const boxes = [...document.querySelectorAll("#delivery-charts [data-chart]")];
out.charts = boxes.map((b) => b.dataset.chart).join(",");
out.drawn = String(boxes.every((b) => echarts.getInstanceByDom(b) && b.querySelector("svg")));
out.named = String(boxes.every((b) => b.getAttribute("tabindex") === "0" && b.getAttribute("aria-label")));
""", "charts", "drawn", "named")
        self.assertEqual(("throughput,timeline,tiers", "true", "true"), (got["charts"], got["drawn"], got["named"]))

    def test_RQ_TRC_083_given_the_legends_then_each_tier_is_named_in_full(self):
        got = self.run_script("""
out.legend = [].concat(optionOf("throughput").legend)[0].data.join("|");
out.text = String(optionOf("tiers").textStyle.fontSize === Number.parseFloat(css("--s-text-small")));
out.caption = String([].concat(optionOf("timeline").legend)[0].textStyle.fontSize === Number.parseFloat(css("--s-text-caption")));
""", "legend", "text", "caption")
        self.assertEqual("S, small task, 1 point|M, medium task, 3 points|L, large task, 8 points", got["legend"])
        self.assertEqual(("true", "true"), (got["text"], got["caption"]))

    def test_RQ_TRC_083_given_an_identity_then_its_bars_give_its_points_per_active_day_in_its_period_s_colour(self):
        got = self.run_script("""
const option = optionOf("throughput");
const names = [].concat(option.yAxis)[0].data;
const claude = names.indexOf("Claude Opus 5.5");
const ofPeriod = (p) => option.series.filter((s) => s.stack === p);
out.rate_a = sumOf(ofPeriod("a"), claude).toFixed(3); out.rate_b = sumOf(ofPeriod("b"), claude).toFixed(3);
out.colours = String(ofPeriod("a").every((s) => s.itemStyle.color === periodColour("a"))
  && ofPeriod("b").every((s) => s.itemStyle.color === periodColour("b")));
out.shades = ofPeriod("a").map((s) => s.itemStyle.opacity).join(",");
out.nopattern = String(noPattern(option));
out.labelled = String(ofPeriod("a").at(-1).label.show && ofPeriod("b").at(-1).label.show);
""", "rate_a", "rate_b", "colours", "shades", "nopattern", "labelled")
        self.assertEqual(("3.333", "0.000"), (got["rate_a"], got["rate_b"]))
        self.assertEqual(("true", "0.4,0.7,1", "true", "true"), (got["colours"], got["shades"], got["nopattern"], got["labelled"]))

    def test_RQ_HST_026_given_the_throughput_chart_then_each_name_is_led_by_its_identity_s_icon_in_its_colour(self):
        got = self.run_script("""
const axis = [].concat(optionOf("throughput").yAxis)[0];
const image = (i) => decodeURIComponent(axis.axisLabel.rich[`p${i}`].backgroundColor.image);
out.richkeys = Object.keys(axis.axisLabel.rich).join(",");
out.iconlabel = axis.axisLabel.formatter(axis.data[1], 1);
out.human = String(image(0).includes("<circle") && image(0).includes(resolved(css("--c-history-identity-1"))));
out.agent = String(image(1).includes("<rect") && image(1).includes(resolved(css("--c-history-identity-2"))));
""", "richkeys", "iconlabel", "human", "agent")
        self.assertEqual(("p0,p1", "{p1|} Claude Opus 5.5"), (got["richkeys"], got["iconlabel"]))
        self.assertEqual(("true", "true"), (got["human"], got["agent"]))

    def test_RQ_TRC_083_given_the_header_then_a_and_b_have_their_colours_as_in_the_charts(self):
        got = self.run_script("""
out.mark_a = String(getComputedStyle(document.querySelector(".delivery-mark-a")).backgroundColor === periodColour("a"));
out.mark_b = String(getComputedStyle(document.querySelector(".delivery-mark-b")).backgroundColor === periodColour("b"));
const band = document.querySelector('#delivery-kpis [data-figure="tasks"]');
out.band = String(Boolean(band.querySelector(".delivery-mark-a") && band.querySelector(".delivery-mark-b")));
const tiers = optionOf("tiers");
out.tiers = String(tiers.series[0].itemStyle.color === periodColour("a") && tiers.series[1].itemStyle.color === periodColour("b")
  && noPattern(tiers) && tiers.series.every((s) => s.label.show));
const areas = optionOf("timeline").series[0].markArea.data;
out.areas = String(areas[0][0].itemStyle.color === periodColour("a") && areas[1][0].itemStyle.color === periodColour("b"));
""", "mark_a", "mark_b", "band", "tiers", "areas")
        self.assertEqual({"mark_a": "true", "mark_b": "true", "band": "true", "tiers": "true", "areas": "true"}, got)

    def test_RQ_TRC_083_given_a_grain_then_the_timeline_has_one_bar_per_bucket_and_marks_a_and_b(self):
        got = self.run_script("""
const option = optionOf("timeline");
out.days = String([].concat(option.xAxis)[0].data.length);
out.areas = String(option.series[0].markArea.data.length);
out.zoom = String(option.dataZoom.length > 0);
document.querySelector('#delivery-grain [data-grain="week"]').click();
const weeks = optionOf("timeline");
const buckets = [].concat(weeks.xAxis)[0].data;
out.weeks = String(buckets.length);
out.last = buckets[buckets.length - 1] + ":" + sumOf(weeks.series, buckets.length - 1);
""", "days", "areas", "zoom", "weeks", "last")
        self.assertEqual(("42", "2", "true", "7"), (got["days"], got["areas"], got["zoom"], got["weeks"]))
        self.assertEqual("2026-10-26:1", got["last"])

    def test_RQ_TRC_083_given_the_tiers_chart_then_it_counts_the_tasks_per_tier_for_a_and_b_and_follows_the_filters(self):
        got = self.run_script("""
const counts = () => optionOf("tiers").series.map((s) => s.name + ":" + s.data.map((d) => d.value ?? d).join(",")).join(" ");
out.counts = counts();
document.querySelector('#delivery-tiers [data-tier="S"]').click();
out.filtered = counts();
""", "counts", "filtered")
        self.assertEqual("A:2,0,1 B:0,1,0", got["counts"])
        self.assertEqual("A:2,0,0 B:0,0,0", got["filtered"])

    def test_RQ_TRC_087_given_the_throughput_chart_focused_then_the_arrows_show_its_bars(self):
        got = self.run_script("""
const box = document.querySelector('#delivery-charts [data-chart="throughput"]');
box.focus();
box.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowRight", bubbles: true }));
out.tip = box.textContent;
""", "tip")
        self.assertIn("Alice", got["tip"])


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class DeliveryTableTest(unittest.TestCase):
    """TASK-TRC-061: RQ-TRC-077, RQ-TRC-079."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "page.html"
        generate(cls.path)
        add_delivery(cls.path)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_script(self, script, *names):
        return found(rendered_dom_after(self.path, TAB + """
const keys = () => [...document.querySelectorAll("#delivery-table tr.delivery-row")].map((r) => r.dataset.key).join(",");
""" + script), *names)

    def test_RQ_TRC_077_given_the_tab_then_the_table_lists_the_tasks_of_a_and_b_and_below_those_set_aside(self):
        got = self.run_script("""
out.rows = keys();
const row = document.querySelector('#delivery-table tr.delivery-row[data-key="TASK-DEM-001"]');
out.cells = [...row.cells].map((c) => c.textContent).join("|");
const aside = [...document.querySelectorAll("#delivery-table tr.delivery-aside")];
out.aside = aside.map((r) => r.dataset.key + ":" + r.dataset.reason).join(",");
out.why = aside.length ? aside[0].textContent : "";
""", "rows", "cells", "aside", "why")
        self.assertEqual("TASK-DEM-101,TASK-DEM-001,TASK-DEM-103,TASK-DEM-104", got["rows"])
        for text in ("TASK-DEM-001", "A range of requirements", "L", "8", "Alice", "Claude Opus 5.5", "2026-10-22", "A", "40"):
            self.assertIn(text, got["cells"], text)
        self.assertEqual("TASK-DEM-105:created-done", got["aside"])
        self.assertIn("Done from its creation", got["why"])

    def test_RQ_TRC_077_given_a_header_then_a_click_sorts_and_a_second_reverses(self):
        got = self.run_script("""
const header = document.querySelector('#delivery-table th[data-sort="points"]');
header.click();
out.up = keys().split(",")[0];
out.sortup = document.querySelector('#delivery-table th[data-sort="points"]').getAttribute("aria-sort");   // the table is drawn again
document.querySelector('#delivery-table th[data-sort="points"]').click();
out.down = keys().split(",")[0];
out.sortdown = document.querySelector('#delivery-table th[data-sort="points"]').getAttribute("aria-sort");
""", "up", "sortup", "down", "sortdown")
        self.assertEqual(("TASK-DEM-103", "ascending"), (got["up"], got["sortup"]))
        self.assertEqual(("TASK-DEM-001", "descending"), (got["down"], got["sortdown"]))

    def test_RQ_TRC_077_given_a_row_clicked_then_the_detail_panel_selects_the_task_and_states_its_delivery(self):
        got = self.run_script("""
document.querySelector('#delivery-table tr.delivery-row[data-key="TASK-DEM-001"]').click();
out.selected = agnosTrace.state.selected;
const line = document.querySelector("#detail .detail-delivery");
out.line = line ? line.textContent : "";
""", "selected", "line")
        self.assertEqual("TASK-DEM-001", got["selected"])
        for text in ("Delivered on 2026-10-22", "Alice", "Claude Opus 5.5", "tier L", "8 points"):
            self.assertIn(text, got["line"], text)

    def test_RQ_TRC_077_given_the_keyboard_then_enter_on_a_row_selects_it(self):
        got = self.run_script("""
const row = document.querySelector('#delivery-table tr.delivery-row[data-key="TASK-DEM-001"]');
out.focusable = row.getAttribute("tabindex");
row.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", bubbles: true }));
out.selected = agnosTrace.state.selected;
""", "focusable", "selected")
        self.assertEqual(("0", "TASK-DEM-001"), (got["focusable"], got["selected"]))

    def test_RQ_TRC_077_given_the_csv_then_it_holds_the_rows_shown_and_follows_the_filters(self):
        got = self.run_script("""
const csv = agnosTrace.deliveryCsv().split("\\r\\n");
out.header = csv[0]; out.lines = String(csv.length - 1);
out.task = csv.find((l) => l.startsWith("TASK-DEM-001")) || "";
document.querySelector('#delivery-tiers [data-tier="S"]').click();
out.filtered = keys();
""", "header", "lines", "task", "filtered")
        self.assertEqual("Task,Title,Tier,Points,Delivered by,Date,Period,Lines,Reworked,Commit type", got["header"])
        self.assertEqual("4", got["lines"])
        self.assertTrue(got["task"].startswith("TASK-DEM-001,A range of requirements,L,8,"), got["task"])
        self.assertEqual("TASK-DEM-103,TASK-DEM-104", got["filtered"])
