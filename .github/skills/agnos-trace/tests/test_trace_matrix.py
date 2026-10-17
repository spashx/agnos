"""Tests of the agnos-trace generator (FTR-TRC-001), on the synthetic process of tests/fixtures/repo.

Run from the repository root: python -m unittest discover -s .github/skills/agnos-trace/tests -v
"""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import trace_matrix as tm  # noqa: E402

FIXTURE = HERE / "fixtures" / "repo"
PROCESS = FIXTURE / "process"
SOURCES = FIXTURE / "src"


def run_main(args):
    """Runs the generator's entry point; returns (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = tm.main(args)
    return code, out.getvalue(), err.getvalue()


class ProcessModelTest(unittest.TestCase):
    """TASK-TRC-001: RQ-TRC-001 to RQ-TRC-005, RQ-TRC-007 (DEC-TRC-002, DEC-TRC-003)."""

    @classmethod
    def setUpClass(cls):
        cls.model = tm.build_process_model(PROCESS)

    def refs(self, src):
        return sorted(dst for (s, dst, kind) in self.model.edges if s == src and kind == "refs")

    def children(self, parent):
        return sorted(dst for (s, dst, kind) in self.model.edges if s == parent and kind == "contains")

    def test_RQ_TRC_003_given_the_fixture_index_when_the_model_is_built_then_every_row_is_an_element(self):
        defined = [e for e in self.model.elements.values() if e["kind"] == "element"]
        self.assertEqual(15, len(defined))
        rq = self.model.elements["RQ-DEM-002"]
        self.assertEqual(("RQ", "DEM", "process/1.requirements/FTR-DEM-001-demo-feature.md", 13, 17, "Covered indirectly"),
                         (rq["type"], rq["tri"], rq["doc"], rq["first"], rq["last"], rq["title"]))
        self.assertEqual("In Progress", self.model.elements["TASK-DEM-002"]["status"])

    def test_RQ_TRC_004_given_nested_ranges_when_the_model_is_built_then_each_parent_contains_its_children(self):
        self.assertEqual([f"RQ-DEM-00{i}" for i in range(1, 6)], self.children("FTR-DEM-001"))
        self.assertEqual(["DEC-DEM-001"], self.children("ADR-DEM-001"))
        self.assertEqual(["TASK-DEM-001", "TASK-DEM-002", "TASK-DEM-003"], self.children("PLAN-DEM-001"))
        self.assertEqual([], self.children("FTR-DEM-002"))

    def test_RQ_TRC_005_given_a_task_citing_a_range_when_the_model_is_built_then_the_range_is_expanded(self):
        self.assertEqual(["ADR-DEM-001", "RQ-DEM-001", "RQ-DEM-002", "RQ-DEM-003"], self.refs("TASK-DEM-001"))

    def test_RQ_TRC_005_given_a_plan_when_the_model_is_built_then_it_has_only_the_references_of_its_own_lines(self):
        self.assertEqual(["ADR-DEM-001"], self.refs("PLAN-DEM-001"))

    def test_RQ_TRC_005_given_a_reference_when_the_model_is_built_then_its_lines_are_kept(self):
        lines = self.model.edges[("DEC-DEM-001", "RQ-DEM-004", "refs")]
        self.assertEqual([[12, "This decision serves RQ-DEM-004."]], lines)

    def test_RQ_TRC_005_given_range_notations_when_expanded_then_only_defined_ids_of_one_prefix_count(self):
        defined = {"RQ-DEM-001", "RQ-DEM-002", "RQ-DEM-003", "TASK-DEM-001"}
        expand = lambda text: sorted(tm.extract_ids(text, defined))  # noqa: E731
        self.assertEqual(["RQ-DEM-001", "RQ-DEM-002", "RQ-DEM-003"], expand("RQ-DEM-001–RQ-DEM-003"))
        self.assertEqual(["RQ-DEM-001", "RQ-DEM-002"], expand("RQ-DEM-001..RQ-DEM-002"))
        self.assertEqual(["RQ-DEM-001", "RQ-DEM-002", "RQ-DEM-003", "RQ-DEM-009"], expand("RQ-DEM-001 to RQ-DEM-009"))
        self.assertEqual(["RQ-DEM-001", "RQ-DEM-003"], expand("RQ-DEM-003 to RQ-DEM-001"))
        self.assertEqual(["RQ-DEM-001", "TASK-DEM-001"], expand("RQ-DEM-001 to TASK-DEM-001"))
        self.assertEqual([], expand("XRQ-DEM-001 RQ-DEM-0011 rq-dem-001"))

    def test_RQ_TRC_007_given_an_undefined_id_in_a_task_when_the_model_is_built_then_it_is_an_undefined_element(self):
        self.assertEqual(["DEC-DEM-099", "RQ-DEM-002"], self.refs("TASK-DEM-002"))
        self.assertEqual("undefined", self.model.elements["DEC-DEM-099"]["kind"])

    def test_RQ_TRC_002_given_no_index_when_the_generator_runs_then_it_exits_1_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "page.html"
            code, _, err = run_main(["--process", tmp, "--sources", str(SOURCES), "--out", str(out)])
            self.assertEqual(1, code)
            self.assertIn("INDEX.idx.md", err)
            self.assertFalse(out.exists())

    def test_RQ_TRC_002_given_a_missing_source_folder_when_the_generator_runs_then_it_exits_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "page.html"
            code, _, err = run_main(["--process", str(PROCESS), "--sources", str(Path(tmp) / "nope"), "--out", str(out)])
            self.assertEqual(1, code)
            self.assertIn("nope", err)
            self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
