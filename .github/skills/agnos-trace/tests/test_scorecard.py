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
from test_trace_matrix import PROCESS, SOURCES, run_main, scanned_model  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
