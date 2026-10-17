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


def scanned_model(**options):
    """The fixture model with its sources scanned, file paths shown relative to the fixture repository."""
    model = tm.build_process_model(PROCESS)
    tm.scan_sources(model, [SOURCES], base=FIXTURE, **options)
    return model


def code_links(model, path):
    return {dst: lines for (src, dst, kind), lines in model.edges.items() if src == path and kind == "code"}


class SourceScannerTest(unittest.TestCase):
    """TASK-TRC-002: RQ-TRC-006, RQ-TRC-007 (DEC-TRC-001, DEC-TRC-003)."""

    @classmethod
    def setUpClass(cls):
        cls.model = scanned_model()

    def test_RQ_TRC_006_given_a_source_line_citing_an_id_when_scanned_then_the_file_links_to_it_with_the_line(self):
        self.assertEqual({"RQ-DEM-001": [[1, "# Implements RQ-DEM-001."]],
                          "RQ-DEM-099": [[5, '"""RQ-DEM-099 is not defined anywhere."""']]},
                         code_links(self.model, "src/a.py"))
        self.assertEqual(["TASK-DEM-002"], list(code_links(self.model, "src/lib/b.cpp")))

    def test_RQ_TRC_006_given_the_default_lists_when_scanned_then_excluded_folders_and_other_extensions_are_skipped(self):
        self.assertEqual(["src/a.py", "src/lib/b.cpp", "src/notrace.py", "src/xss.js"], sorted(self.model.files))

    def test_RQ_TRC_006_given_a_file_without_id_when_scanned_then_it_is_kept_with_no_link(self):
        self.assertEqual({}, code_links(self.model, "src/notrace.py"))
        self.assertEqual(0, self.model.files["src/notrace.py"]["ids"])

    def test_RQ_TRC_006_given_other_extensions_and_exclusions_when_scanned_then_they_replace_the_defaults(self):
        model = scanned_model(extensions={".bin", ".py"}, excludes=["lib"])
        self.assertEqual(["src/a.py", "src/data.bin", "src/dist/generated.py", "src/notrace.py"], sorted(model.files))
        self.assertIn("RQ-DEM-005", code_links(model, "src/data.bin"))

    def test_RQ_TRC_006_given_a_binary_or_oversized_file_when_scanned_then_it_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "bin.py").write_bytes(b"RQ-DEM-001\x00\x01")
            (root / "big.py").write_bytes(b"# RQ-DEM-001\n" + b"x" * tm.MAX_SOURCE_BYTES)
            (root / "ok.py").write_text("# RQ-DEM-001\n", encoding="utf-8")
            model = tm.build_process_model(PROCESS)
            tm.scan_sources(model, [root], base=root)
            self.assertEqual(["ok.py"], sorted(model.files))

    def test_RQ_TRC_007_given_an_undefined_id_in_a_source_when_scanned_then_it_is_an_undefined_element(self):
        self.assertEqual("undefined", self.model.elements["RQ-DEM-099"]["kind"])


class CoverageAndGapsTest(unittest.TestCase):
    """TASK-TRC-003: RQ-TRC-008, RQ-TRC-009, RQ-TRC-017 (DEC-TRC-002, DEC-TRC-004)."""

    @classmethod
    def setUpClass(cls):
        cls.analysis = tm.analyse(scanned_model())

    def test_RQ_TRC_008_given_the_fixture_when_coverage_is_computed_then_each_requirement_has_its_rating(self):
        self.assertEqual({"RQ-DEM-001": "covered", "RQ-DEM-002": "indirect", "RQ-DEM-003": "uncovered",
                          "RQ-DEM-004": "uncovered", "RQ-DEM-005": "uncovered"}, self.analysis["coverage"])

    def test_RQ_TRC_008_given_a_requirement_depending_on_a_covered_one_when_rated_then_the_dependency_does_not_cover_it(
            self):
        model = tm.build_process_model(PROCESS)
        model.add_edge("src/x.py", "RQ-DEM-001", "code", [1, "RQ-DEM-001"])
        self.assertEqual("uncovered", tm.analyse(model)["coverage"]["RQ-DEM-002"])

    def test_RQ_TRC_009_given_the_fixture_when_gaps_are_listed_then_each_list_holds_its_planted_elements(self):
        self.assertEqual({"uncovered": ["RQ-DEM-003", "RQ-DEM-004", "RQ-DEM-005"],
                          "untasked": ["RQ-DEM-004", "RQ-DEM-005"],
                          "task-no-rq": ["TASK-DEM-003"],
                          "adr-no-rq": ["ADR-DEM-002"],
                          "empty": ["FTR-DEM-002", "ADR-DEM-002", "PLAN-DEM-002"],
                          "isolated": ["RQ-DEM-005", "FTR-DEM-002", "ADR-DEM-002", "PLAN-DEM-002"],
                          "undefined": ["DEC-DEM-099", "RQ-DEM-099"],
                          "untraced-files": ["src/notrace.py"]}, self.analysis["gaps"])

    def test_RQ_TRC_017_given_the_fixture_when_the_generator_runs_then_it_prints_the_counts_and_the_gaps(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out, _ = run_main(["--process", str(PROCESS), "--sources", str(SOURCES), "--out",
                                     str(Path(tmp) / "page.html")])
        self.assertEqual(0, code)
        summary = out.strip().splitlines()[-1]
        for part in ("15 elements", "4 files", "RQ 5: covered 1, indirect 1, uncovered 3", "uncovered 3", "untasked 2",
                     "task-no-rq 1", "adr-no-rq 1", "empty 3", "isolated 4", "undefined 2", "untraced-files 1"):
            self.assertIn(part, summary)


if __name__ == "__main__":
    unittest.main()
