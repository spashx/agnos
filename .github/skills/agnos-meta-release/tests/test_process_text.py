"""Tests of the process text a plugin user receives (RQ-PLG-018, RQ-PLG-019, TASK-PLG-019; ADR-PLG-003: DEC-PLG-013, DEC-PLG-014).

The instructions file of this repository goes through `process_skill`, as the release delivers it.
Run from the repository root: python -m unittest discover -s .github/skills/agnos-meta-release/tests -v
"""
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import release  # noqa: E402

ROOT = HERE.parents[3]
REPOSITORY_FILE_NAME = Path(release.INSTRUCTIONS).name
TARGET = "improvement target"
SKILL = "`agnos-self-improvement` skill"     # RQ-RSI-001 / DEC-RSI-001
PLUGIN_RULE = "never into a file of an installed plugin"
END_SESSION = "## END SESSION ACTION"
SELF_IMPROVEMENT = "## RECURSIVE SELF-IMPROVEMENT SESSIONS"
NEXT_SECTION_RE = re.compile(r"\n## ")


def delivered_process():
    return release.process_skill((ROOT / release.INSTRUCTIONS).read_text(encoding=release.ENCODING))


def section(text, heading):
    start = text.index(heading) + len(heading)
    following = NEXT_SECTION_RE.search(text, start)
    return text[start:following.start() if following else len(text)]


class ImprovementTargetTest(unittest.TestCase):
    """RQ-PLG-018, DEC-PLG-013, as amended by RQ-RSI-001, RQ-RSI-002 (DEC-RSI-001, DEC-RSI-002)."""

    def test_RQ_RSI_002_given_the_delivered_process_then_self_improvement_goes_through_the_skill_to_the_declared_target(self):
        """Given the delivered process, When its self-improvement section is read, Then it names the skill, the target and the plugin rule."""
        rules = section(delivered_process(), SELF_IMPROVEMENT)
        self.assertIn(SKILL, rules)
        self.assertIn(TARGET, rules)
        self.assertIn(PLUGIN_RULE, rules)

    def test_RQ_RSI_001_given_the_delivered_process_then_end_session_invokes_the_skill(self):
        """Given the delivered process, When END SESSION is read, Then its follow-up invokes the skill."""
        self.assertIn(SKILL, section(delivered_process(), END_SESSION))


class DefinitionOfDoneTest(unittest.TestCase):
    """RQ-PLG-025, DEC-PLG-020 (TASK-PLG-028)."""

    FUNCTIONS_ITEM = ("Every new function, method and class cites its requirement ID in its doc comment or in the "
                      "comment just above it")
    DOD = "### DEFINITION OF DONE"
    EVERY_TIER = re.compile(r"\|\s*✓\s*\|\s*✓\s*\|\s*✓\s*\|\s*$")
    LINE_BUDGET = 400

    def test_RQ_PLG_025_given_the_delivered_process_then_the_dod_names_functions_for_every_tier(self):
        rows = [line for line in section(delivered_process(), self.DOD).splitlines() if self.FUNCTIONS_ITEM in line]
        self.assertEqual(1, len(rows))
        self.assertRegex(rows[0], self.EVERY_TIER)

    def test_RQ_PLG_025_given_the_instructions_file_then_it_stays_within_its_line_budget(self):
        lines = (ROOT / release.INSTRUCTIONS).read_text(encoding=release.ENCODING).splitlines()
        self.assertLessEqual(len(lines), self.LINE_BUDGET)


class TestTraceabilityTest(unittest.TestCase):
    """RQ-PLG-026, DEC-PLG-021 (TASK-PLG-030)."""

    TRACEABILITY = "### MANDATORY TRACEABILITY"
    NEXT_SUBSECTION_RE = re.compile(r"\n###? ")
    TEST_DOC_COMMENTS = "class/function doc comments, those of test functions included"
    TEST_NAMES = "test case names"

    def traceability(self):
        text = delivered_process()
        start = text.index(self.TRACEABILITY) + len(self.TRACEABILITY)
        following = self.NEXT_SUBSECTION_RE.search(text, start)
        return text[start:following.start()]

    def test_RQ_PLG_026_given_the_delivered_process_then_a_test_cites_its_id_in_its_doc_comment(self):
        self.assertIn(self.TEST_DOC_COMMENTS, self.traceability())

    def test_RQ_PLG_026_given_the_delivered_process_then_no_id_is_asked_in_a_test_name(self):
        self.assertNotIn(self.TEST_NAMES, self.traceability())


class OwnNameTest(unittest.TestCase):
    """RQ-PLG-019, DEC-PLG-014."""

    def test_RQ_PLG_019_given_the_delivered_process_then_it_does_not_name_its_repository_file(self):
        self.assertNotIn(REPOSITORY_FILE_NAME, delivered_process())


if __name__ == "__main__":
    unittest.main()
