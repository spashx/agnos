"""Tests of the typed element links of agnos-graph (FTR-TRC-013; ADR-TRC-024: DEC-TRC-081 to DEC-TRC-083), on the
synthetic process of tests/fixtures/links.

TASK-TRC-128: RQ-TRC-138 to RQ-TRC-141. Run: python -m unittest discover -s .github/skills/agnos-graph/tests
"""
import copy
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import graph  # noqa: E402

PROCESS = HERE / "fixtures" / "links" / "process"
TEXT = "text"
RQ1, RQ2, RQ3 = "RQ-LNK-001", "RQ-LNK-002", "RQ-LNK-003"
FTR, ADR, DEC, PLAN, TASK = "FTR-LNK-001", "ADR-LNK-001", "DEC-LNK-001", "PLAN-LNK-001", "TASK-LNK-001"
EXPECTED_LINKS = [
    [DEC, RQ1, [[14, "Requirement refs"]]],
    [DEC, RQ2, [[13, TEXT]]],
    [PLAN, ADR, [[8, "ADR refs"]]],
    [PLAN, RQ1, [[7, "Requirement refs"]]],
    [PLAN, RQ3, [[4, TEXT]]],
    [RQ1, ADR, [[12, TEXT]]],
    [RQ1, RQ2, [[9, TEXT], [10, "Dependencies"]]],
    [RQ1, RQ3, [[11, "Dependencies"]]],
    [TASK, ADR, [[16, "ADR refs"]]],
    [TASK, DEC, [[16, "ADR refs"]]],
    [TASK, RQ1, [[15, "Requirement refs"]]],
    [TASK, RQ2, [[14, TEXT]]],
]


# RQ-TRC-138
def links_of(process):
    """{(source, target): [[line, field]]} of a process folder, as the graph file's links block holds them."""
    model = graph.build_process_model(process)
    return {(s, t): fields for s, t, fields in graph.element_links(process, model)}


class LinkFieldTest(unittest.TestCase):
    """TASK-TRC-128: RQ-TRC-138, RQ-TRC-139 (DEC-TRC-081, DEC-TRC-082)."""

    @classmethod
    def setUpClass(cls):
        cls.links = links_of(PROCESS)

    def test_RQ_TRC_138_given_the_fixture_then_the_links_block_holds_the_expected_rows_in_edge_order(self):
        model = graph.build_process_model(PROCESS)
        self.assertEqual(EXPECTED_LINKS, graph.element_links(PROCESS, model))

    def test_RQ_TRC_138_given_a_task_citing_in_requirement_refs_and_description_then_their_fields_differ(self):
        self.assertEqual([[15, "Requirement refs"]], self.links[(TASK, RQ1)])
        self.assertEqual([[14, TEXT]], self.links[(TASK, RQ2)])

    def test_RQ_TRC_138_given_an_adr_or_a_feature_citing_ids_then_their_edges_stay_and_no_link_row_is_written(self):
        model = graph.build_process_model(PROCESS)
        self.assertIn((ADR, FTR, graph.KEY_REFS), model.edges)
        self.assertIn((FTR, RQ2, graph.KEY_REFS), model.edges)
        self.assertFalse([k for k in self.links if k[0] in (ADR, FTR)])

    def test_RQ_TRC_139_given_a_requirement_citing_in_statement_dependencies_and_adr_refs_then_only_dependencies_is_a_field(self):
        self.assertEqual([[9, TEXT], [10, "Dependencies"]], self.links[(RQ1, RQ2)])
        self.assertEqual([[12, TEXT]], self.links[(RQ1, ADR)])

    def test_RQ_TRC_139_given_a_decision_citing_in_rationale_and_requirement_refs_then_their_fields_differ(self):
        self.assertEqual([[13, TEXT]], self.links[(DEC, RQ2)])
        self.assertEqual([[14, "Requirement refs"]], self.links[(DEC, RQ1)])

    def test_RQ_TRC_139_given_a_plan_citing_in_references_and_overview_then_their_fields_differ(self):
        self.assertEqual([[7, "Requirement refs"]], self.links[(PLAN, RQ1)])
        self.assertEqual([[8, "ADR refs"]], self.links[(PLAN, ADR)])
        self.assertEqual([[4, TEXT]], self.links[(PLAN, RQ3)])


class FieldExtentTest(unittest.TestCase):
    """TASK-TRC-128: RQ-TRC-140 (DEC-TRC-083)."""

    def test_RQ_TRC_140_given_a_dependencies_list_wrapped_over_two_lines_then_both_citations_are_dependencies(self):
        links = links_of(PROCESS)
        self.assertEqual([[10, "Dependencies"]], [p for p in links[(RQ1, RQ2)] if p[0] == 10])
        self.assertEqual([[11, "Dependencies"]], links[(RQ1, RQ3)])


class UnchangedBlocksTest(unittest.TestCase):
    """TASK-TRC-128: RQ-TRC-141 (DEC-TRC-081)."""

    def test_RQ_TRC_141_given_the_links_computed_then_the_model_is_unchanged(self):
        model = graph.build_process_model(PROCESS)
        before = (copy.deepcopy(model.elements), copy.deepcopy(model.edges))
        graph.element_links(PROCESS, model)
        self.assertEqual(before, (model.elements, model.edges))

    def test_RQ_TRC_141_given_every_link_row_then_it_matches_a_refs_edge_and_its_proof_lines(self):
        model = graph.build_process_model(PROCESS)
        for source, target, fields in graph.element_links(PROCESS, model):
            proofs = model.edges[(source, target, graph.KEY_REFS)]
            self.assertEqual([p[0] for p in proofs], [f[0] for f in fields])

    def test_RQ_TRC_141_given_the_state_data_then_links_is_its_own_block(self):
        model = graph.build_process_model(PROCESS)
        links = graph.element_links(PROCESS, model)
        data = graph.state_data(model, {}, {}, links=links)
        self.assertEqual(links, data[graph.KEY_LINKS])
        self.assertEqual(graph.state_data(model, {}, {})["edges"], data["edges"])


if __name__ == "__main__":
    unittest.main()
