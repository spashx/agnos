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
    ["TASK-DEM-102", "L", True, 2, 40, "feat", False, None],           # period A, Alice and Claude
    ["TASK-DEM-103", "S", False, 3, 5, "feat", False, None],           # period A, Claude
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
