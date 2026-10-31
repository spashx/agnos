"""Tests of the packaging of the agnos-meta-release skill (RQ-MTA-013, TASK-MTA-008; ADR-MTA-002: DEC-MTA-007).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-meta-release/tests -v
"""
import ast
import re
import sys
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
ROOT = SKILL_DIR.parents[2]
NAME = "agnos-meta-release"
SKILL = SKILL_DIR / "SKILL.md"
POINTER = ROOT / ".claude" / "skills" / NAME / "SKILL.md"
SCRIPT = SKILL_DIR / "scripts" / "release.py"
CHANGELOG = ROOT / "CHANGELOG.md"
DESCRIPTION_RE = re.compile(r'^description: "(.*)"$', re.M)
NAME_RE = re.compile(r"^name: (\S+)$", re.M)
DESCRIPTION_LIMIT = 1024
LINES_LIMIT = 500


class PackagingTest(unittest.TestCase):
    """RQ-MTA-013."""

    def test_RQ_MTA_013_given_the_skill_then_both_files_carry_its_name_and_a_description_of_what_and_when(self):
        for path in (SKILL, POINTER):
            text = path.read_text(encoding="utf-8")
            self.assertEqual(NAME, NAME_RE.search(text).group(1))
            description = DESCRIPTION_RE.search(text).group(1)
            self.assertLessEqual(len(description), DESCRIPTION_LIMIT)
            self.assertIn("USE FOR", description)

    def test_RQ_MTA_013_given_the_procedure_then_it_stays_under_its_limit_and_the_pointer_names_it(self):
        self.assertLess(len(SKILL.read_text(encoding="utf-8").splitlines()), LINES_LIMIT)
        self.assertIn(f".github/skills/{NAME}/SKILL.md", POINTER.read_text(encoding="utf-8"))

    def test_RQ_MTA_013_given_the_script_then_it_imports_the_standard_library_only(self):
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported |= {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                imported.add(node.module.split(".")[0])
        self.assertEqual(set(), imported - set(sys.stdlib_module_names))

    def test_RQ_MTA_013_given_the_changelog_then_it_names_the_skill(self):
        self.assertIn(NAME, CHANGELOG.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
