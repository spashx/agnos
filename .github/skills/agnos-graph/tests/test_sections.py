"""Tests of the document sections of agnos-graph (FTR-TRC-012; ADR-TRC-023: DEC-TRC-078 to DEC-TRC-080), on the synthetic
process of tests/fixtures/sections.

TASK-TRC-125: RQ-TRC-134 to RQ-TRC-137. Run: python -m unittest discover -s .github/skills/agnos-graph/tests
"""
import contextlib
import copy
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import graph  # noqa: E402

PROCESS = HERE / "fixtures" / "sections" / "process"
SOURCES = HERE / "fixtures" / "repo" / "src"
GENERATED_AT = "2026-11-22T10:00Z"
FTR, ADR = "FTR-SEC-001", "ADR-SEC-001"


# RQ-TRC-134 to RQ-TRC-136
def sections_of(process):
    """{section ID: section} of a process folder, as the graph file holds them."""
    model = graph.build_process_model(process)
    return {s["id"]: s for s in graph.document_sections(process, model)}


class SectionNodesTest(unittest.TestCase):
    """TASK-TRC-125: RQ-TRC-134, RQ-TRC-135 (DEC-TRC-079)."""

    @classmethod
    def setUpClass(cls):
        cls.sections = sections_of(PROCESS)

    def test_RQ_TRC_134_given_an_adr_with_context_and_decision_then_context_is_a_section_and_decision_is_not(self):
        self.assertIn(f"{ADR}#Context", self.sections)
        self.assertNotIn(f"{ADR}#Decision", self.sections)
        context = self.sections[f"{ADR}#Context"]
        self.assertEqual(("SEC", 2, ADR, 6, 11, "Context"),
                         (context["type"], context["level"], context["parent"], context["first"], context["last"],
                          context["title"]))

    def test_RQ_TRC_134_given_a_feature_then_its_requirements_section_is_excluded_and_an_added_heading_kept(self):
        self.assertIn(f"{FTR}#Glossary", self.sections)
        self.assertNotIn(f"{FTR}#Functional Requirements", self.sections)

    def test_RQ_TRC_134_given_a_heading_inside_a_code_fence_then_it_is_no_section(self):
        self.assertNotIn(f"{ADR}#Not a heading", self.sections)

    def test_RQ_TRC_134_given_the_fixture_then_the_sections_are_in_document_and_line_order(self):
        self.assertEqual([f"{FTR}#Overview", f"{FTR}#Overview/Scope", f"{FTR}#Overview/Note", f"{FTR}#Overview/Note.2",
                          f"{FTR}#Glossary", f"{ADR}#Status", f"{ADR}#Context", f"{ADR}#Consequences"],
                         list(self.sections))

    def test_RQ_TRC_135_given_a_subsection_and_a_deeper_heading_then_only_the_subsection_is_a_node(self):
        scope = self.sections[f"{FTR}#Overview/Scope"]
        self.assertEqual((3, f"{FTR}#Overview", 5, 8), (scope["level"], scope["parent"], scope["first"], scope["last"]))
        self.assertFalse([i for i in self.sections if i.endswith("Detail")])


class SectionCitationsTest(unittest.TestCase):
    """TASK-TRC-125: RQ-TRC-136 (DEC-TRC-080)."""

    @classmethod
    def setUpClass(cls):
        cls.sections = sections_of(PROCESS)

    def test_RQ_TRC_136_given_a_section_citing_an_id_then_it_holds_the_id_with_its_line_and_text(self):
        self.assertEqual([["RQ-SEC-001", [[7, "Motivated by RQ-SEC-001."]]]], self.sections[f"{ADR}#Context"]["refs"])

    def test_RQ_TRC_136_given_citations_in_a_section_and_its_subsection_then_each_goes_to_the_narrowest(self):
        self.assertEqual([["RQ-SEC-002", [[4, "Serves RQ-SEC-002."]]]], self.sections[f"{FTR}#Overview"]["refs"])
        self.assertEqual([["ADR-SEC-001", [[6, "Scope cites ADR-SEC-001."]]],
                          ["RQ-SEC-001", [[8, "Detail cites RQ-SEC-001."]]]],
                         self.sections[f"{FTR}#Overview/Scope"]["refs"])

    def test_RQ_TRC_136_given_two_subsections_of_one_title_then_the_second_is_suffixed(self):
        self.assertEqual("Note", self.sections[f"{FTR}#Overview/Note.2"]["title"])
        self.assertEqual((11, 13), (self.sections[f"{FTR}#Overview/Note.2"]["first"],
                                    self.sections[f"{FTR}#Overview/Note.2"]["last"]))


class UnchangedConsumersTest(unittest.TestCase):
    """TASK-TRC-125: RQ-TRC-137 (DEC-TRC-078)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="agnos-graph-sections-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def run_graph(self, out):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = graph.main(["--process", str(PROCESS), "--sources", str(SOURCES), "--out", str(out),
                               "--generated-at", GENERATED_AT])
        self.assertEqual(0, code, stderr.getvalue())
        return out.read_bytes()

    def test_RQ_TRC_137_given_the_sections_read_then_the_model_elements_and_edges_are_unchanged(self):
        model = graph.build_process_model(PROCESS)
        elements, edges = copy.deepcopy(model.elements), copy.deepcopy(model.edges)
        graph.document_sections(PROCESS, model)
        self.assertEqual((elements, edges), (model.elements, model.edges))

    def test_RQ_TRC_137_given_the_graph_file_then_sections_is_a_block_of_its_own(self):
        data = json.loads(self.run_graph(self.tmp / "graph.json"))
        self.assertIn("sections", data)
        self.assertFalse([e for e in data["elements"] if e["type"] == "SEC"])
        self.assertFalse([e for e in data["edges"] if "#" in e[0] or "#" in e[1]])

    def test_RQ_TRC_136_given_a_fixed_date_when_run_twice_then_the_two_files_are_byte_identical(self):
        self.assertEqual(self.run_graph(self.tmp / "a.json"), self.run_graph(self.tmp / "b.json"))


if __name__ == "__main__":
    unittest.main()
