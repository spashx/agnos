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
BLOCK = "AGNOS block"
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
    """RQ-PLG-018, DEC-PLG-013."""

    def test_RQ_PLG_018_given_the_delivered_process_then_self_improvement_targets_the_file_the_agnos_block_names(self):
        rules = section(delivered_process(), SELF_IMPROVEMENT)
        self.assertIn(TARGET, rules)
        self.assertIn(BLOCK, rules)

    def test_RQ_PLG_018_given_the_delivered_process_then_end_session_refers_to_the_improvement_target(self):
        self.assertIn(TARGET, section(delivered_process(), END_SESSION))


class OwnNameTest(unittest.TestCase):
    """RQ-PLG-019, DEC-PLG-014."""

    def test_RQ_PLG_019_given_the_delivered_process_then_it_does_not_name_its_repository_file(self):
        self.assertNotIn(REPOSITORY_FILE_NAME, delivered_process())


if __name__ == "__main__":
    unittest.main()
