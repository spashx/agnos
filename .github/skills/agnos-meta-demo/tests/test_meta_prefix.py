"""Tests of the prefix of the meta skills (FTR-MTA-001, TASK-MTA-001; ADR-MTA-001: DEC-MTA-003).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-meta-demo/tests -v
"""
import json
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
ROOT = SKILL_DIR.parents[2]
GITHUB_SKILLS = ROOT / ".github" / "skills"
CLAUDE_SKILLS = ROOT / ".claude" / "skills"
AGENTS = ROOT / ".claude" / "agents"
SKILL_FILE = "SKILL.md"
SCENARIO = SKILL_DIR / "assets" / "scenario.json"
VERIFY = SKILL_DIR / "scripts" / "verify.ps1"
META_SKILLS = ("agnos-meta-demo", "agnos-meta-docs-sync")
META_AGENT = "agnos-meta-docs-sync.md"
OLD_NAMES = ("agnos-demo", "agnos-docs-sync")
NAME_RE = re.compile(r"^name:\s*(\S+)\s*$", re.M)
PATTERN_RE = re.compile(r"^\$MAINTAINER_PATTERN = '([^']*)'", re.M)
META_EXCLUSIONS = {r"^\.github/skills/agnos-meta-", r"^\.claude/skills/agnos-meta-", r"^\.claude/agents/agnos-meta-"}


def name_in(path):
    return NAME_RE.search(path.read_text(encoding="utf-8")).group(1)


class NamesTest(unittest.TestCase):
    """RQ-MTA-001."""

    def test_RQ_MTA_001_given_the_repository_then_each_meta_skill_has_its_prefixed_name_in_each_location(self):
        for name in META_SKILLS:
            for folder in (GITHUB_SKILLS, CLAUDE_SKILLS):
                self.assertEqual(name, name_in(folder / name / SKILL_FILE))
        self.assertEqual(META_AGENT.removesuffix(".md"), name_in(AGENTS / META_AGENT))

    def test_RQ_MTA_001_given_the_repository_then_no_location_keeps_an_old_name(self):
        for name in OLD_NAMES:
            self.assertFalse((GITHUB_SKILLS / name).exists(), name)
            self.assertFalse((CLAUDE_SKILLS / name).exists(), name)
            self.assertFalse((AGENTS / f"{name}.md").exists(), name)


class CriterionTest(unittest.TestCase):
    """RQ-MTA-002."""

    def test_RQ_MTA_002_given_the_baseline_exclusions_then_they_name_the_prefix_and_no_skill(self):
        exclusions = json.loads(SCENARIO.read_text(encoding="utf-8"))["baselineExclude"]
        self.assertTrue(META_EXCLUSIONS <= set(exclusions))
        self.assertEqual([], [e for e in exclusions if any(n in e for n in OLD_NAMES + META_SKILLS)])

    def test_RQ_MTA_002_given_the_verification_then_its_pattern_names_the_prefix_and_no_skill(self):
        pattern = PATTERN_RE.search(VERIFY.read_text(encoding="utf-8")).group(1)
        for path in (".github/skills/agnos-meta-other/SKILL.md", ".claude/skills/agnos-meta-other/SKILL.md", ".claude/agents/agnos-meta-other.md"):
            self.assertRegex(path, pattern)
        self.assertNotRegex(".github/skills/agnos-index/SKILL.md", pattern)
        self.assertEqual([], [n for n in OLD_NAMES + META_SKILLS if n in pattern])


if __name__ == "__main__":
    unittest.main()
