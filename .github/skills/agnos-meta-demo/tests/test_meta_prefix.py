"""Tests of the names of the meta skills and of the demo's content (FTR-MTA-001, TASK-MTA-001, TASK-MTA-003;
ADR-MTA-001: DEC-MTA-003, DEC-MTA-006; TASK-INI-003, RQ-INI-008).

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
CONTENT = SKILL_DIR / "assets" / "content"
VERIFY = SKILL_DIR / "scripts" / "verify.ps1"
META_SKILLS = ("agnos-meta-demo", "agnos-meta-docs-sync", "agnos-meta-qa", "agnos-meta-release")
META_AGENT = "agnos-meta-docs-sync.md"
OLD_NAMES = ("agnos-demo", "agnos-docs-sync")
NAME_RE = re.compile(r"^name:\s*(\S+)\s*$", re.M)
PATTERN_RE = re.compile(r"^\$TOOLKIT_PATTERN = '([^']*)'", re.M)
TOOLKIT_PATHS = (".github/skills/agnos-index/SKILL.md", ".claude/settings.json", "GETTING_STARTED.MD",
                 "CHANGELOG.md", "CONTRIBUTING.md", "LICENSE.md", "SECURITY.md", "CODE_OF_CONDUCT.md", "agnos-overview.png")
PROJECT_PATHS = ("README.md", ".gitignore", ".gitattributes", "CLAUDE.md", "AGENTS.md", "process/INDEX.idx.md", "service/roombook/CHANGELOG.md", "client/src/app.ts")
OWN_FILES = {".gitignore", ".gitattributes"}
DEMO_TOOLKIT_PATH = "../agnos-lightweight-process"
TRIGRAMS_RE = re.compile(r"^\$TOOLKIT_TRIGRAMS = '([^']*)'", re.M)
OWN_TRIGRAMS = {"INI", "MTA"}


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


class DemoContentTest(unittest.TestCase):
    """RQ-MTA-005."""

    def setUp(self):
        self.plan = json.loads(SCENARIO.read_text(encoding="utf-8"))

    def test_RQ_MTA_005_given_the_scenario_then_it_imports_no_toolkit_and_starts_with_the_projects_own_files(self):
        self.assertNotIn("baselineExclude", self.plan)
        self.assertEqual([], [s for s in self.plan["steps"] if s["op"] == "baseline"])
        first = self.plan["steps"][0]
        self.assertEqual(OWN_FILES, {item["to"] for item in first["add"]})
        for item in first["add"]:
            self.assertTrue((CONTENT / item["from"]).is_file(), item["from"])

    def test_RQ_MTA_005_given_the_verification_then_it_refuses_every_toolkit_file_and_no_project_file(self):
        pattern = PATTERN_RE.search(VERIFY.read_text(encoding="utf-8")).group(1)
        for path in TOOLKIT_PATHS:
            self.assertRegex(path, pattern)
        for path in PROJECT_PATHS:
            self.assertNotRegex(path, pattern)

    def test_RQ_INI_008_given_the_scenario_then_the_first_commit_calls_agnos_init_with_a_relative_path(self):
        self.assertEqual(DEMO_TOOLKIT_PATH, self.plan["steps"][0]["init"])

    def test_RQ_INI_008_given_the_verification_then_it_refuses_the_ids_of_this_feature_and_checks_the_block(self):
        text = VERIFY.read_text(encoding="utf-8")
        self.assertLessEqual(OWN_TRIGRAMS, set(TRIGRAMS_RE.search(text).group(1).split("|")))
        self.assertIn("Report 'RQ-INI-008'", text)

    def test_RQ_MTA_005_given_the_demo_readme_then_it_gives_no_path_into_the_toolkit(self):
        for name in ("README.md", "drafts/README.web.md"):
            text = (CONTENT / name).read_text(encoding="utf-8")
            self.assertNotIn(".github/", text, name)
            self.assertNotIn("clone of the AGNOS toolkit", text, name)


if __name__ == "__main__":
    unittest.main()
