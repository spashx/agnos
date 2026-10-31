"""Tests of the Delivery figures of the agnos-perf-center page (FTR-TRC-004, ADR-TRC-009: DEC-TRC-038), in a headless browser,
on a page whose data file is given synthetic `history` and `delivery` blocks.

Run from the repository root: python -m unittest discover -s .github/skills/agnos-perf-center/tests -v
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
import perf_center as tm  # noqa: E402
from test_history_page import NEEDS_BROWSER, found, linear_graph  # noqa: E402
from test_perf_center import BROWSER, generate, rendered_dom_after  # noqa: E402

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


FRICTION = [
    ["2026-10-15", "DEM", 5, 5, 5, 5, 1],                              # period B, Alice: 20 events
    ["2026-10-22", "DEM", 2, 1, 0, 1, 2],                              # period A, Alice: 4 events
    ["2026-10-27", "OTH", 3, 3, 1, 1, 4],                              # period A, Claude: 8 events
]


def add_delivery(page, friction=None):
    """Writes the synthetic history and delivery blocks into the data files of a generated page."""
    json_path, _ = tm.data_paths(page)
    data = json.loads(json_path.read_text(encoding="utf-8"))
    data["history"] = {"graph": linear_graph(COMMITS), "people": PEOPLE, "commits": COMMITS,
                       "limits": {"since": "6.weeks", "depth": None, "commits": len(COMMITS), "first": COMMITS[0]["date"],
                                  "last": COMMITS[-1]["date"], "shallow": False},
                       "interventions": {"elements": {}, "files": {}}}
    data["delivery"] = {"tasks": TASKS, "activeDays": ACTIVE_DAYS, "settings": history.load_delivery_settings(),
                        "friction": friction or []}
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
        self.assertEqual("overview,matrix,graph,history,delivery,quality", got["tabs"])
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

    def test_RQ_TRC_083_given_the_timeline_then_its_bars_in_a_and_b_take_their_period_s_colour(self):
        got = self.run_script("""
const option = optionOf("timeline");
const days = [].concat(option.xAxis)[0].data;
const colourOn = (day) => { const d = option.series[2].data[days.indexOf(day)]; return d.itemStyle ? d.itemStyle.color : "neutral"; };
out.in_a = String(colourOn("2026-10-22") === periodColour("a"));
out.in_b = String(colourOn("2026-10-15") === periodColour("b"));
out.outside = String(colourOn("2026-09-20") === "neutral" || colourOn("2026-09-20") === resolved(css("--s-text-muted")));
""", "in_a", "in_b", "outside")
        self.assertEqual({"in_a": "true", "in_b": "true", "outside": "true"}, got)

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
out.last = buckets[buckets.length - 1] + ":" + sumOf(weeks.series.filter((s) => s.stack), buckets.length - 1);
""", "days", "areas", "zoom", "weeks", "last")
        self.assertEqual(("42", "2", "true", "7"), (got["days"], got["areas"], got["zoom"], got["weeks"]))
        self.assertEqual("2026-10-26:1", got["last"])

    def test_RQ_TRC_097_given_the_timeline_then_its_slider_lies_whole_inside_the_chart_below_the_plot(self):
        got = self.run_script("""
const option = optionOf("timeline");
const slider = option.dataZoom.find((z) => z.type === "slider");
const grid = [].concat(option.grid)[0];
out.inside = String(slider.bottom >= Number.parseFloat(css("--s-space-sm")));
out.room = String(grid.bottom >= slider.bottom + slider.height + Number.parseFloat(css("--s-space-sm")));
out.raised = String(grid.top === Number.parseFloat(css("--s-space-2xl")));
""", "inside", "room", "raised")
        self.assertEqual({"inside": "true", "room": "true", "raised": "true"}, got)

    def test_RQ_TRC_097_given_the_slider_spanning_the_whole_axis_then_both_handles_are_drawn_inside_the_chart_box(self):
        got = self.run_script("""
const box = document.querySelector('#delivery-charts [data-chart="timeline"]');
const frame = box.getBoundingClientRect();
const slider = optionOf("timeline").dataZoom.find((z) => z.type === "slider");
const band = frame.bottom - slider.bottom - slider.height - Number.parseFloat(css("--s-space-xs"));
const drawn = [...box.querySelectorAll("svg path")].map((p) => p.getBoundingClientRect())
  .filter((r) => r.width > 0 && r.height > 0 && r.top >= band);
out.drawn = String(drawn.length > 0);
out.slider_from = String(drawn.every((r) => r.left >= frame.left));
out.slider_to = String(drawn.every((r) => r.right <= frame.right));
""", "drawn", "slider_from", "slider_to")
        self.assertEqual({"drawn": "true", "slider_from": "true", "slider_to": "true"}, got)

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


TOKENS = HERE.parent / "assets" / "tokens.json"
THEMES = ("light", "dark")
MARKS = ("delivery-friction", "delivery-rework")
MARK_OUTLINE = "delivery-overlay-outline"
PERIODS = ("period-a", "period-b")
CARD_SURFACES = ("surface", "surface-raised")
TIER_OPACITIES = ("opacity.tier-s", "opacity.tier-m", "opacity.tier-l")
TINT_OPACITY = "opacity.tint"
MIN_MARK_CONTRAST = 3.0


def rgb_of(colour):
    return tuple(int(colour[i:i + 2], 16) for i in (1, 3, 5))


def over(colour, behind, opacity):
    return tuple(opacity * c + (1 - opacity) * b for c, b in zip(colour, behind))


def luminance(rgb):
    r, g, b = (c / 255 / 12.92 if c / 255 <= 0.03928 else ((c / 255 + 0.055) / 1.055) ** 2.4 for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(one, other):
    high, low = sorted((luminance(one), luminance(other)), reverse=True)
    return (high + 0.05) / (low + 0.05)


class DeliveryMarkContrastTest(unittest.TestCase):
    """TASK-TRC-091: RQ-TRC-108, computed from the design tokens."""

    def test_RQ_TRC_108_given_each_theme_then_each_mark_reaches_the_contrast_on_every_background(self):
        tokens = json.loads(TOKENS.read_text(encoding="utf-8"))
        base, semantic, component = tokens["global"], tokens["semantic"], tokens["component"]

        def colour(name, theme):
            return rgb_of(base[semantic[name][theme]])

        for theme in THEMES:
            for surface in CARD_SURFACES:
                behind = colour(surface, theme)
                backgrounds = {surface: behind}
                for period in PERIODS:
                    area = over(colour(period, theme), behind, float(base[TINT_OPACITY]))
                    backgrounds[f"{period} area"] = area
                    for tier in TIER_OPACITIES:
                        backgrounds[f"{period} {tier}"] = over(colour(period, theme), area, float(base[tier]))
                for mark in MARKS:
                    fill = colour(component[mark], theme)
                    outline = colour(component[MARK_OUTLINE], theme)
                    for name, background in backgrounds.items():
                        with self.subTest(theme=theme, mark=mark, background=name):
                            self.assertGreaterEqual(max(contrast(fill, background), contrast(outline, background)),
                                                    MIN_MARK_CONTRAST)


@unittest.skipUnless(BROWSER, NEEDS_BROWSER)
class DeliveryFrictionTest(unittest.TestCase):
    """TASK-TRC-083, TASK-TRC-084: RQ-TRC-092 to RQ-TRC-096."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "page.html"
        generate(cls.path)
        add_delivery(cls.path, FRICTION)
        cls.no_log = Path(cls.tmp.name) / "no_log.html"
        generate(cls.no_log)
        add_delivery(cls.no_log)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_script(self, script, *names, path=None):
        return found(rendered_dom_after(path or self.path, TAB + CHARTS + OPEN.split("\n", 2)[2] + """
const shown = (name) => { const option = optionOf("timeline"); const s = option.series.find((x) => x.name === name);
  if (!s) return "none"; const days = [].concat(option.xAxis)[0].data;
  return days.flatMap((day, i) => (s.data[i] ? [`${day}=${s.data[i]}`] : [])).join(","); };
const tag = (key) => document.querySelector(`#delivery-charts [data-overlay="${key}"]`);
const marksOn = () => { tag("rework").click(); tag("friction").click(); };
""" + script), *names)

    def test_RQ_TRC_092_given_sessions_in_a_and_b_then_the_figure_is_the_events_per_session_and_a_fall_is_better(self):
        got = self.run_script("""
out.ab = ab("friction"); out.text = figure("friction").textContent;
out.place = [...document.querySelectorAll("#delivery-kpis [data-figure]")].map((f) => f.dataset.figure).join(",");
""", "ab", "text", "place")
        self.assertEqual("6.000|20.000|-0.700", got["ab"])
        self.assertIn("better", got["text"])
        self.assertEqual("tasks,points,throughput,rework,friction", got["place"])

    def test_RQ_TRC_092_given_a_period_without_a_session_then_it_reads_a_dash_with_no_word(self):
        got = self.run_script("""
for (const [side, day] of [["from", "2026-10-01"], ["to", "2026-10-02"]]) {
  const input = document.getElementById(`delivery-${side}-b`);
  input.value = day; input.dispatchEvent(new Event("change"));
}
out.ab = ab("friction"); out.sub = figure("friction").querySelector(".kpi-sub").textContent;
""", "ab", "sub")
        self.assertEqual("6.000||", got["ab"])
        self.assertIn("—", got["sub"])
        self.assertNotIn("better", got["sub"])
        self.assertNotIn("worse", got["sub"])

    def test_RQ_TRC_092_given_no_row_then_the_band_keeps_its_four_figures(self):
        got = self.run_script("""
out.count = String(document.querySelectorAll("#delivery-kpis [data-figure]").length);
""", "count", path=self.no_log)
        self.assertEqual("4", got["count"])

    def test_RQ_TRC_093_given_a_variation_then_its_word_comes_from_what_the_figure_measures(self):
        got = self.run_script("""
out.rise = d.verdict(0.5, false); out.reworkrise = d.verdict(0.5, true); out.fall = d.verdict(-0.5, true);
out.zero = d.verdict(0, true) || "no word"; out.unknown = d.verdict(null, false) || "no word";
out.points = figure("points").textContent;
""", "rise", "reworkrise", "fall", "zero", "unknown", "points")
        self.assertEqual(("better", "worse", "better"), (got["rise"], got["reworkrise"], got["fall"]))
        self.assertEqual(("no word", "no word"), (got["zero"], got["unknown"]))
        self.assertIn("better", got["points"])

    def test_RQ_TRC_094_given_a_trigram_or_an_identity_then_the_friction_follows_it(self):
        got = self.run_script("""
const tri = d.filter(); tri.tris.add("OTH");
out.bytrigram = String(d.friction(A, tri, bounds).perSession);
const person = d.filter(); person.people.add(0);
out.byauthor = String(d.friction(A, person, bounds).perSession);
""", "bytrigram", "byauthor")
        self.assertEqual(("8", "4"), (got["bytrigram"], got["byauthor"]))

    def test_RQ_TRC_108_given_the_marks_shown_then_each_series_and_each_tag_has_the_outline_token(self):
        got = self.run_script("""
marksOn();
const outline = resolved(css("--c-delivery-overlay-outline"));
const width = parseFloat(css("--c-delivery-overlay-outline-width"));
out.series = String(["Friction", "Rework"].every((name) => {
  const style = optionOf("timeline").series.find((s) => s.name === name).itemStyle;
  return style.borderColor === outline && style.borderWidth === width;
}));
out.tags = String(["friction", "rework"].every((key) => {
  const style = getComputedStyle(tag(key).querySelector(".delivery-overlay-mark"));
  return style.borderTopColor === outline && parseFloat(style.borderTopWidth) > 0;
}));
""", "series", "tags")
        self.assertEqual(("true", "true"), (got["series"], got["tags"]))

    def test_RQ_TRC_094_given_another_filter_then_the_friction_is_unchanged_and_the_filter_is_named(self):
        got = self.run_script("""
document.querySelector('#delivery-tiers [data-tier="L"]').click();
out.ab = ab("friction"); out.ignored = d.frictionIgnored(agnosTrace.delivery.currentFilter()).join(",");
""", "ab", "ignored")
        self.assertEqual("6.000|20.000|-0.700", got["ab"])
        self.assertEqual("tier", got["ignored"])

    def test_RQ_TRC_095_given_the_grain_then_circles_and_diamonds_stand_on_their_buckets_on_a_second_axis(self):
        got = self.run_script("""
marksOn();
out.friction = shown("Friction"); out.rework = shown("Rework");
const icon = (key) => tag(key).querySelector(".delivery-overlay-mark");
out.icons = String(["rework", "friction"].every((key) => icon(key).offsetWidth > 0
  && getComputedStyle(icon(key)).backgroundColor === resolved(css(`--c-delivery-${key}`))));
out.marklegend = [].concat(optionOf("timeline").legend)[0].data.join(",");
const option = optionOf("timeline");
out.symbols = option.series.filter((s) => !s.stack).map((s) => `${s.symbol}:${s.yAxisIndex}`).join(",");
out.axes = String([].concat(option.yAxis).length);
out.colours = String(option.series.find((s) => s.name === "Friction").itemStyle.color === resolved(css("--c-delivery-friction"))
  && option.series.find((s) => s.name === "Rework").itemStyle.color === resolved(css("--c-delivery-rework")));
document.querySelector('#delivery-grain [data-grain="week"]').click();
out.week = shown("Friction");
""", "friction", "rework", "icons", "marklegend", "symbols", "axes", "colours", "week")
        self.assertEqual("true", got["icons"])
        self.assertNotIn("Rework", got["marklegend"])
        self.assertEqual("2026-10-15=20,2026-10-22=4,2026-10-27=8", got["friction"])
        self.assertEqual("2026-10-27=1", got["rework"])
        self.assertEqual(("diamond:1,circle:1", "2", "true"), (got["symbols"], got["axes"], got["colours"]))
        self.assertEqual("2026-10-12=20,2026-10-19=4,2026-10-26=8", got["week"])

    def test_RQ_TRC_095_given_a_bucket_with_a_session_then_its_tooltip_gives_its_trigram_counters_author_and_commit(self):
        got = self.run_script("""
marksOn();
const box = document.querySelector('#delivery-charts [data-chart="timeline"]');
const days = [].concat(optionOf("timeline").xAxis)[0].data;
chartOf("timeline").dispatchAction({ type: "showTip", seriesIndex: 0, dataIndex: days.indexOf("2026-10-27") });
out.tip = box.textContent;
""", "tip")
        for text in ("OTH", "questions 3", "verification 1", "Claude Opus 5.5", "d000000004", "reworked"):
            self.assertIn(text, got["tip"], text)

    def test_RQ_TRC_096_given_the_tab_then_the_marks_are_off_until_their_tag_is_on_and_the_figures_stay(self):
        got = self.run_script("""
out.pressed = tag("friction").getAttribute("aria-pressed");
out.off = shown("Friction") + "|" + shown("Rework");
const before = document.getElementById("delivery-kpis").textContent;
tag("friction").click();
out.on = shown("Friction"); out.rework = shown("Rework");
out.pressedon = tag("friction").getAttribute("aria-pressed");
out.same = String(before === document.getElementById("delivery-kpis").textContent);
""", "pressed", "off", "on", "rework", "pressedon", "same")
        self.assertEqual(("false", "none|none", "none", "true", "true"),
                         (got["pressed"], got["off"], got["rework"], got["pressedon"], got["same"]))
        self.assertEqual("2026-10-15=20,2026-10-22=4,2026-10-27=8", got["on"])

    def test_RQ_TRC_093_given_each_family_of_figures_then_its_tooltip_says_which_way_is_better(self):
        got = self.run_script("""
const tipOf = (key) => { figure(key).dispatchEvent(new MouseEvent("mouseenter", { bubbles: true }));
  figure(key).dispatchEvent(new MouseEvent("mouseover", { bubbles: true })); return document.body.textContent; };
out.pointstip = String(tipOf("points").includes("More is better, less is worse"));
out.frictiontip = String(tipOf("friction").includes("Less is better, more is worse"));
""", "pointstip", "frictiontip")
        self.assertEqual(("true", "true"), (got["pointstip"], got["frictiontip"]))

    def test_RQ_TRC_096_given_no_log_then_the_friction_tag_is_disabled_and_says_why(self):
        got = self.run_script("""
out.disabled = String(tag("friction").disabled); out.why = tag("friction").title; out.series = shown("Friction");
""", "disabled", "why", "series", path=self.no_log)
        self.assertEqual(("true", "none"), (got["disabled"], got["series"]))
        self.assertIn("METRICS_LOG", got["why"])


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

    def test_RQ_TRC_079_given_a_column_grip_then_its_column_widens_alone_without_sorting_and_a_double_click_resets(self):
        """TASK-TRC-080: every column of the table resizable, as in the matrix (RQ-TRC-043)."""
        got = self.run_script("""
const heads = () => [...document.querySelectorAll("#delivery-table thead th")];
out.grips = String(heads().every((th) => th.querySelector(".col-grip")));
out.before = heads().slice(0, 2).map((th) => th.offsetWidth).join(",");
const grip = heads()[0].querySelector(".col-grip");
for (let i = 0; i < 3; i += 1) grip.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowRight", bubbles: true }));
grip.click();
out.after = heads().slice(0, 2).map((th) => th.offsetWidth).join(",");
out.unsorted = heads()[0].getAttribute("aria-sort");
heads()[0].querySelector(".col-grip").dispatchEvent(new MouseEvent("dblclick", { bubbles: true }));
out.reset = heads().slice(0, 2).map((th) => th.offsetWidth).join(",");
""", "grips", "before", "after", "unsorted", "reset")
        step = int(tm.load_tokens(tm.TOKENS_PATH)["global"]["space.16"].removesuffix("px"))   # --c-splitter-step
        before = [int(w) for w in got["before"].split(",")]
        after = [int(w) for w in got["after"].split(",")]
        self.assertEqual("true", got["grips"])
        self.assertEqual((before[0] + 3 * step, before[1]), (after[0], after[1]))
        self.assertEqual("none", got["unsorted"])                       # a grip never sorts
        self.assertEqual(got["before"], got["reset"])

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
