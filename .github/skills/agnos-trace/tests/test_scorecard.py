"""Tests of the quality scorecard (FTR-TRC-003, ADR-TRC-008): the scores, the grades, the data written for the page.

Run from the repository root: python -m unittest discover -s .github/skills/agnos-trace/tests -v
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import scorecard as sc  # noqa: E402
import trace_matrix as tm  # noqa: E402
from test_trace_matrix import (BROWSER, PROCESS, SOURCES, generate, rendered_dom_after, run_main,  # noqa: E402
                               scanned_model)


class ScoreArithmeticTest(unittest.TestCase):
    """TASK-TRC-046: RQ-TRC-058, RQ-TRC-059 (DEC-TRC-032)."""

    @classmethod
    def setUpClass(cls):
        cls.scoring = sc.load_scoring()

    def test_RQ_TRC_058_given_10_requirements_of_which_2_fail_when_scored_then_the_check_scores_8(self):
        self.assertEqual(8.0, sc.score_of(10, 2))

    def test_RQ_TRC_058_given_no_finding_or_all_findings_then_the_score_is_10_or_0(self):
        self.assertEqual((10.0, 0.0), (sc.score_of(7, 0), sc.score_of(7, 7)))

    def test_RQ_TRC_058_given_an_empty_population_when_scored_then_there_is_no_score(self):
        self.assertIsNone(sc.score_of(0, 0))

    def test_RQ_TRC_058_given_a_share_between_two_decimals_when_scored_then_it_rounds_half_up_to_one(self):
        self.assertEqual(8.8, sc.score_of(8, 1))                       # 8.75
        self.assertEqual(6.7, sc.score_of(3, 1))                       # 6.666...

    def test_RQ_TRC_059_given_scored_checks_when_averaged_then_the_risk_weights_them_and_informational_counts_for_nothing(
            self):
        scored = [("critical", 10.0), ("high", 0.0), ("informational", 0.0), ("medium", None)]
        self.assertEqual(5.7, sc.weighted_score(scored, self.scoring))   # (10 * 10 + 7.5 * 0) / 17.5
        self.assertIsNone(sc.weighted_score([("informational", 3.0)], self.scoring))

    def test_RQ_TRC_059_given_the_thresholds_then_9_is_A_and_8_9_is_B_and_3_9_is_E(self):
        grade = lambda score: sc.grade_of(score, self.scoring)  # noqa: E731
        self.assertEqual(["A", "B", "B", "C", "D", "E", "E"], [grade(x) for x in (9.0, 8.9, 7.5, 6.0, 4.0, 3.9, 0.0)])
        self.assertIsNone(grade(None))

    def test_RQ_TRC_059_given_a_scoring_file_when_read_then_each_check_has_a_known_risk_and_the_weights_are_data(self):
        self.assertEqual({"critical": 10, "high": 7.5, "medium": 5, "low": 2.5, "informational": 0}, self.scoring["risks"])
        self.assertTrue(all(c["risk"] in self.scoring["risks"] for c in self.scoring["checks"]))
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "scoring.json"
            bad.write_text('{"risks": {}}', encoding="utf-8")
            with self.assertRaises(sc.ScoringError):
                sc.load_scoring(bad)


class QualityBlockTest(unittest.TestCase):
    """TASK-TRC-046: RQ-TRC-058, RQ-TRC-059, RQ-TRC-064 (DEC-TRC-032, DEC-TRC-033), on the fixture."""

    @classmethod
    def setUpClass(cls):
        cls.model = scanned_model()
        cls.analysis = tm.analyse(cls.model)
        cls.scoring = sc.load_scoring()
        cls.quality = sc.build(cls.model, cls.analysis, cls.scoring)
        cls.checks = {c["key"]: c for c in cls.quality["checks"]}

    def test_RQ_TRC_058_given_the_fixture_then_each_check_has_the_population_and_findings_of_its_rule(self):
        covered = self.checks["covered"]
        self.assertEqual((5, ["RQ-DEM-003", "RQ-DEM-004", "RQ-DEM-005"], 4.0),
                         (covered["population"], covered["findings"], covered["score"]))
        self.assertEqual(["DEC-DEM-099", "RQ-DEM-099"], self.checks["defined"]["findings"])
        self.assertEqual(8, self.checks["defined"]["population"])          # the 6 defined IDs cited and the 2 undefined
        files = self.checks["files-traced"]
        self.assertEqual((4, ["src/notrace.py"], "file"), (files["population"], files["findings"], files["items"]))

    def test_RQ_TRC_058_given_no_call_graph_then_the_functions_check_is_left_out(self):
        self.assertNotIn("functions-traced", self.checks)

    def test_RQ_TRC_059_given_the_fixture_then_the_overall_score_is_the_weighted_average_of_the_checks(self):
        pairs = [(c["risk"], c["score"]) for c in self.quality["checks"]]
        weights = self.scoring["risks"]
        expected = sum(weights[r] * s for r, s in pairs) / sum(weights[r] for r, _ in pairs)
        self.assertAlmostEqual(expected, self.quality["score"], delta=0.05)
        self.assertEqual(sc.grade_of(self.quality["score"], self.scoring), self.quality["grade"])
        self.assertEqual("C", self.quality["grade"])

    def test_RQ_TRC_059_given_the_fixture_then_the_trigram_has_its_own_score_without_files_or_functions(self):
        trigram = self.quality["trigrams"]["DEM"]
        keys = [c["key"] for c in trigram["checks"]]
        self.assertNotIn("files-traced", keys)
        self.assertEqual(["covered", "defined", "tasked", "task-rq", "adr-rq", "filled", "connected"], keys)
        covered = next(c for c in trigram["checks"] if c["key"] == "covered")
        self.assertEqual(self.checks["covered"]["score"], covered["score"])
        self.assertIn(trigram["grade"], "ABCDE")

    def test_RQ_TRC_064_given_a_run_then_the_data_file_holds_the_same_numbers_as_the_summary_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "page.html"
            code, out, _ = run_main(["--process", str(PROCESS), "--sources", str(SOURCES), "--out", str(page)])
            data = json.loads(page.with_suffix(".json").read_text(encoding="utf-8"))
        self.assertEqual(0, code)
        quality = data["quality"]
        self.assertNotIn("gaps", data)
        self.assertIn(f"quality: {quality['grade']} {quality['score']}/10", out)
        for check in quality["checks"]:
            self.assertIn(f"{check['key']} {check['score']}", out)

    def test_RQ_TRC_064_given_two_runs_then_the_quality_is_the_same(self):
        with tempfile.TemporaryDirectory() as tmp:
            runs = []
            for name in ("a", "b"):
                page = Path(tmp) / f"{name}.html"
                run_main(["--process", str(PROCESS), "--sources", str(SOURCES), "--out", str(page),
                          "--generated-at", "x"])
                runs.append(json.loads(page.with_suffix(".json").read_text(encoding="utf-8"))["quality"])
        self.assertEqual(runs[0], runs[1])


GAP_WORD = "gap"
SKILL = HERE.parent
RENDERED_CHECK = "agnosTrace.showView('quality');"


class VocabularyTest(unittest.TestCase):
    """TASK-TRC-047: RQ-TRC-057 (DEC-TRC-034): the former word for a finding list is gone from what a reader gets."""

    def test_RQ_TRC_057_given_the_data_the_summary_line_and_the_documentation_then_none_holds_the_retired_word(self):
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "page.html"
            code, out, _ = run_main(["--process", str(PROCESS), "--sources", str(SOURCES), "--out", str(page)])
            data = page.with_suffix(".json").read_text(encoding="utf-8")
        self.assertEqual(0, code)
        self.assertNotIn(GAP_WORD, data.lower())
        self.assertNotIn(GAP_WORD, out.lower())
        for name in ("SKILL.md", "assets/matrix.html", "assets/scoring.json"):
            self.assertNotIn(GAP_WORD, (SKILL / name).read_text(encoding="utf-8").lower(), name)

    @unittest.skipUnless(BROWSER, "no Chromium-family browser found (set AGNOS_TRACE_BROWSER)")
    def test_RQ_TRC_057_given_the_page_when_rendered_then_its_text_ids_and_classes_name_quality_checks_and_findings(self):
        import re
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "page.html"
            generate(path)
            dom = rendered_dom_after(path, RENDERED_CHECK)
        visible = re.sub(r"<(style|script)\b.*?</\1>", "", dom, flags=re.S)       # the style's layout spacing is not wording
        self.assertNotIn(GAP_WORD, visible.lower())
        self.assertRegex(visible, r'data-view="quality"[^>]*>Quality')
        self.assertIn('id="check-covered"', visible)
        self.assertIn("finding", visible)


CHECK_CARDS = """
const out = document.documentElement.dataset;
agnosTrace.showView("quality");
const cards = () => [...document.querySelectorAll("#quality-list .check-card")];
const toggle = (card) => card.querySelector(".check-toggle");
const open = () => cards().filter((c) => toggle(c).getAttribute("aria-expanded") === "true").map((c) => c.dataset.check);
out.order = cards().map((c) => c.dataset.check).join(",");
out.compact = open().join(",");
out.compactHasFindings = String(cards().some((c) => c.querySelector(".finding")));
toggle(cards()[0]).click();
out.one = open().join(",");
out.rule = cards()[0].querySelector(".check-detail .check-card-desc")?.textContent.slice(0, 20) || "";
out.formula = cards()[0].querySelector(".check-formula")?.textContent || "";
const finding = cards()[0].querySelector(".finding");
out.findings = String(cards()[0].querySelectorAll(".finding").length);
finding.click();
out.selected = agnosTrace.state.selected;
agnosTrace.showView("quality");
document.getElementById("expand-checks").click();
out.all = String(open().length === cards().length);
document.getElementById("collapse-checks").click();
out.none = open().join(",");
"""


@unittest.skipUnless(BROWSER, "no Chromium-family browser found (set AGNOS_TRACE_BROWSER)")
class CheckCardsTest(unittest.TestCase):
    """TASK-TRC-048: RQ-TRC-062 (DEC-TRC-034)."""

    def test_RQ_TRC_062_given_the_quality_view_when_chevrons_are_pressed_then_checks_open_one_by_one_or_all_at_once(self):
        import re
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "page.html"
            generate(path)
            found = dict(re.findall(r'data-(order|compact|compact-has-findings|one|rule|formula|findings|selected|all|none)="([^"]*)"',
                                    rendered_dom_after(path, CHECK_CARDS)))
        self.assertEqual("covered,adr-rq,filled,tasked,task-rq,connected,defined,files-traced", found["order"])   # lowest first
        self.assertEqual("", found["compact"])                          # every check compact when the view opens
        self.assertEqual("false", found["compact-has-findings"])
        self.assertEqual("covered", found["one"])                       # the others stay compact
        self.assertTrue(found["rule"].startswith("Every requirement is"))
        self.assertIn("4.0", found["formula"])
        self.assertEqual("3", found["findings"])
        self.assertEqual("RQ-DEM-003", found["selected"])               # a finding selects its element
        self.assertEqual("true", found["all"])
        self.assertEqual("", found["none"])


GRADES = "ABCDE"
CONTRAST_MIN = 4.5
HEX_DIGITS = 2


def luminance(hex_colour):
    channels = [int(hex_colour.lstrip("#")[i:i + HEX_DIGITS], 16) / 255 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(first, second):
    light, dark = sorted((luminance(first), luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


class GradePaletteTest(unittest.TestCase):
    """TASK-TRC-049: RQ-TRC-065 (DEC-TRC-035)."""

    def test_RQ_TRC_065_given_the_tokens_of_both_themes_then_each_grade_letter_has_a_contrast_of_4_5_on_its_fill(self):
        tokens = tm.load_tokens(tm.TOKENS_PATH)
        for theme in tm.THEMES:
            for letter in GRADES.lower():
                fill = tokens["global"][tokens["semantic"][f"grade-{letter}"][theme]]
                text = tokens["global"][tokens["semantic"][f"on-grade-{letter}"][theme]]
                self.assertGreaterEqual(contrast(fill, text), CONTRAST_MIN, f"{theme} grade {letter}")

    def test_RQ_TRC_065_given_the_five_grade_fills_then_they_run_from_green_to_red_like_the_food_and_energy_labels(self):
        tokens = tm.load_tokens(tm.TOKENS_PATH)
        for theme in tm.THEMES:
            fills = [tokens["global"][tokens["semantic"][f"grade-{c}"][theme]].lower() for c in GRADES.lower()]
            self.assertEqual(5, len(set(fills)))
            red, green = (lambda f: int(f[1:3], 16)), (lambda f: int(f[3:5], 16))
            self.assertGreater(green(fills[0]), red(fills[0]))                  # A is green
            self.assertGreater(red(fills[-1]), green(fills[-1]))                # E is red
            hues = [red(f) - green(f) for f in fills]
            self.assertEqual(hues, sorted(hues))                                 # redder at each step


REPORT_CARD = """
const out = document.documentElement.dataset;
agnosTrace.showView("quality");
const text = (selector) => document.querySelector(selector)?.textContent.trim() || "";
out.grade = text("#quality-report .report-grade");
out.score = text("#quality-report .report-score");
out.verdict = text("#quality-report .report-verdict");
out.scale = [...document.querySelectorAll("#quality-report .scale-step")].map((s) => s.textContent.trim()).join("");
out.current = text("#quality-report .scale-step.is-current");
out.trigrams = [...document.querySelectorAll("#quality-report .report-trigram")].map((t) => [...t.children].map((c) => c.textContent.trim()).join(" ")).join("|");
out.fixes = [...document.querySelectorAll("#quality-report .fix-first button")].map((b) => b.dataset.check).join(",");
out.tab = text("#quality-grade");
out.side = text("#side-grade");
out.overview = text("#overview-grade");
document.querySelector("#quality-report .fix-first button").click();
out.opened = [...agnosTrace.state.openChecks].join(",");
out.view = document.querySelector(".tab[aria-selected=true]").dataset.view;
"""


@unittest.skipUnless(BROWSER, "no Chromium-family browser found (set AGNOS_TRACE_BROWSER)")
class ReportCardTest(unittest.TestCase):
    """TASK-TRC-049: RQ-TRC-060, RQ-TRC-064 (DEC-TRC-034)."""

    def test_RQ_TRC_060_given_the_fixture_when_the_quality_view_opens_then_the_report_card_reads_at_a_glance(self):
        import re
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "page.html"
            generate(path)
            quality = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))["quality"]
            dom = rendered_dom_after(path, REPORT_CARD)
            found = dict(re.findall(r'data-(grade|score|verdict|scale|current|trigrams|fixes|tab|side|overview|opened)="([^"]*)"', dom))
            # the view the script wrote on the root element, not a tab's data-view (TASK-HST-004 added a tab after Quality)
            found["view"] = re.search(r'<html[^>]*\sdata-view="([^"]*)"', dom).group(1)
        self.assertEqual(quality["grade"], found["grade"])
        self.assertEqual(f"{quality['score']:.1f} / 10", found["score"])
        self.assertEqual("Fair: 6 checks need attention", found["verdict"])
        self.assertEqual(GRADES, found["scale"])                       # the A to E scale, the current grade marked
        self.assertEqual(quality["grade"], found["current"])
        self.assertEqual("DEM " + quality["trigrams"]["DEM"]["grade"] + " " + f"{quality['trigrams']['DEM']['score']:.1f}",
                         found["trigrams"])
        self.assertEqual("covered,adr-rq,filled", found["fixes"])       # the three lowest-scored checks
        self.assertEqual((quality["grade"],) * 3, (found["tab"], found["side"], found["overview"]))   # RQ-TRC-064
        self.assertEqual("covered", found["opened"])                    # a "Fix first" link opens its check
        self.assertEqual("quality", found["view"])


CHARTS = """
const out = document.documentElement.dataset;
agnosTrace.showView("quality");
const charts = [...document.querySelectorAll("#quality-charts svg")];
out.svgs = String(charts.length);
out.named = String(charts.every((c) => c.getAttribute("role") === "img" && c.querySelector("title")?.textContent.trim()
  && c.querySelector("desc")?.textContent.trim()));
const points = [...document.querySelectorAll("#quality-charts .radar-point")];
out.points = points.map((p) => p.dataset.check).join(",");
out.focusable = String(points.every((p) => p.getAttribute("tabindex") === "0" && p.getAttribute("aria-label")));
out.bars = String(document.querySelectorAll("#quality-charts .area-bar").length);
out.shares = String(document.querySelectorAll("#quality-charts .share-part").length);
const tip = document.getElementById("chart-tip");
const covered = points.find((p) => p.dataset.check === "covered");
out.hiddenBefore = String(tip.hidden);
covered.dispatchEvent(new MouseEvent("mouseover", { bubbles: true, clientX: 200, clientY: 200 }));
out.tip = tip.hidden ? "" : tip.textContent;
covered.dispatchEvent(new MouseEvent("mouseout", { bubbles: true }));
out.hiddenAfter = String(tip.hidden);
const other = points.find((p) => p.dataset.check === "defined");
other.dispatchEvent(new FocusEvent("focus"));
out.focusTip = tip.hidden ? "" : tip.textContent;
other.dispatchEvent(new FocusEvent("blur"));
document.querySelector("#quality-charts .radar-axis[data-check=filled]").dispatchEvent(new MouseEvent("click", { bubbles: true }));
out.opened = [...agnosTrace.state.openChecks].join(",");
"""


@unittest.skipUnless(BROWSER, "no Chromium-family browser found (set AGNOS_TRACE_BROWSER)")
class ChartsTest(unittest.TestCase):
    """TASK-TRC-050: RQ-TRC-061, RQ-TRC-065 (DEC-TRC-035)."""

    def test_RQ_TRC_061_given_the_quality_view_then_it_draws_a_radar_trigram_bars_and_coverage_with_tooltips(self):
        import re
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "page.html"
            generate(path)
            found = dict(re.findall(r'data-(svgs|named|points|focusable|bars|shares|hidden-before|tip|hidden-after|focus-tip|opened)="([^"]*)"',
                                    rendered_dom_after(path, CHARTS)))
        self.assertEqual("3", found["svgs"])                            # radar, trigram bars, coverage
        self.assertEqual("true", found["named"])                        # a title and a description each (RQ-TRC-065)
        self.assertEqual("covered,defined,tasked,task-rq,adr-rq,filled,connected,files-traced", found["points"])
        self.assertEqual("true", found["focusable"])
        self.assertEqual("1", found["bars"])                            # the fixture has one trigram
        self.assertEqual("3", found["shares"])                          # covered, indirect, uncovered
        self.assertEqual("true", found["hidden-before"])
        for part in ("Requirements covered", "score 4.0", "population 5", "3 findings"):
            self.assertIn(part, found["tip"])                           # on hover
        self.assertEqual("true", found["hidden-after"])
        self.assertIn("IDs defined", found["focus-tip"])                # and on keyboard focus
        self.assertEqual("filled", found["opened"])                     # an axis opens its check


FIT_WINDOW = "1440,900"
FIT_SCRIPT = """
const out = document.documentElement.dataset;
agnosTrace.showView("quality");
const view = document.getElementById("view-quality");
const cards = [...document.querySelectorAll("#quality-list .check-card")];
out.sizes = view.scrollHeight + "/" + view.clientHeight;
out.fits = String(view.scrollHeight <= view.clientHeight);
out.checks = String(cards.length);
out.lastVisible = String(cards.at(-1).getBoundingClientRect().bottom <= view.getBoundingClientRect().bottom);
out.charts = String(document.querySelectorAll("#quality-charts svg").length);
"""
FIT_AREAS = ("AAA", "BBB", "CCC", "DDD", "EEE")


def five_area_process(root):
    """A process of five feature areas of two requirements each, with its index, in the given folder."""
    folder = root / "process" / "1.requirements"
    folder.mkdir(parents=True)
    rows = ["# AGNOS process index - GENERATED by the agnos-index skill, never edit by hand.",
            '# "@<path>" opens a document; rows: ID|first-last|status|title', "#next FTR-AAA-002 RQ-AAA-003"]
    for tri in FIT_AREAS:
        name = f"process/1.requirements/FTR-{tri}-001-area.md"
        (root / name).write_text("\n".join([f"# FTR-{tri}-001: Area", "", "## Requirements", "", f"### RQ-{tri}-001: One", "", "text",
                                            "", f"### RQ-{tri}-002: Two", "", "text"]) + "\n", encoding="utf-8")
        rows += [f"@{name}", f"FTR-{tri}-001|1-11||Area", f"RQ-{tri}-001|5-7||One", f"RQ-{tri}-002|9-11||Two"]
    (root / "process" / "INDEX.idx.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (root / "src").mkdir()
    (root / "src" / "code.py").write_text("# RQ-AAA-001\n", encoding="utf-8")
    return root / "process", root / "src"


@unittest.skipUnless(BROWSER, "no Chromium-family browser found (set AGNOS_TRACE_BROWSER)")
class FitInWindowTest(unittest.TestCase):
    """TASK-TRC-051: RQ-TRC-063 (DEC-TRC-034)."""

    def found(self, process, sources):
        import re
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "page.html"
            code, _, error = run_main(["--process", str(process), "--sources", str(sources), "--out", str(page),
                                       "--generated-at", "x"])
            self.assertEqual(0, code, error)
            dom = rendered_dom_after(page, FIT_SCRIPT, FIT_WINDOW)
        return dict(re.findall(r'data-(sizes|fits|checks|last-visible|charts)="([^"]*)"', dom))

    def test_RQ_TRC_063_given_the_fixture_in_a_1440_by_900_window_then_the_quality_view_has_no_vertical_scroll(self):
        found = self.found(PROCESS, SOURCES)
        self.assertEqual("8", found["checks"])
        self.assertEqual(("true", "true", "3"), (found["fits"], found["last-visible"], found["charts"]), found["sizes"])

    def test_RQ_TRC_063_given_five_feature_areas_in_a_1440_by_900_window_then_the_quality_view_has_no_vertical_scroll(self):
        with tempfile.TemporaryDirectory() as tmp:
            process, sources = five_area_process(Path(tmp))
            found = self.found(process, sources)
        self.assertEqual(("true", "true"), (found["fits"], found["last-visible"]), found["sizes"])


if __name__ == "__main__":
    unittest.main()
