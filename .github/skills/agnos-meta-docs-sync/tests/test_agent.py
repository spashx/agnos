"""Tests of the definition files of the agnos-meta-docs-sync skill and sub-agent (FTR-DOC-001, TASK-DOC-002).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-meta-docs-sync/tests -v
"""
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
ROOT = SKILL_DIR.parents[2]
SKILL = SKILL_DIR / "SKILL.md"
POINTER = ROOT / ".claude" / "skills" / "agnos-meta-docs-sync" / "SKILL.md"
AGENT = ROOT / ".github" / "agents" / "agnos-meta-docs-sync.agent.md"
POINTER_AGENT = ROOT / ".claude" / "agents" / "agnos-meta-docs-sync.md"
DOCUMENTS = ("CHANGELOG.md", "AGENTS.md", "CLAUDE.md", "GETTING_STARTED.MD")
EDIT_TOOLS = {"Read", "Grep", "Glob", "Edit", "Bash"}
COPILOT_TOOLS = {"read", "search", "edit", "execute"}
FRONT_RE = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.S)
META_PREFIX = "agnos-meta-"


def front_matter(path):
    """The front matter fields of a Markdown file as a dict, and its body."""
    match = FRONT_RE.match(path.read_text(encoding="utf-8"))
    fields = dict(re.findall(r"^([a-z-]+):\s*(.*)$", match.group(1), re.M))
    return {k: v.strip().strip('"') for k, v in fields.items()}, match.group(2)


class SkillTest(unittest.TestCase):
    """TASK-DOC-002: RQ-DOC-002 (RQ-DOC-003 for the discovery)."""

    def test_RQ_DOC_002_given_the_skill_then_it_is_a_maintainer_skill_that_names_the_four_documents_and_their_rules(self):
        fields, body = front_matter(SKILL)
        self.assertEqual("agnos-meta-docs-sync", fields["name"])
        self.assertTrue(fields["name"].startswith(META_PREFIX))
        for name in DOCUMENTS:
            self.assertIn(name, body)
        for rule in ("Keep a Changelog", "Unreleased", "maintainer", "changes_since.py", "never commit"):
            self.assertIn(rule.lower(), body.lower(), rule)
        self.assertRegex(body, r"(?i)no statement without|never state what no commit")

    def test_RQ_DOC_003_given_the_claude_code_pointer_then_it_names_the_same_skill_and_the_canonical_file(self):
        fields, body = front_matter(POINTER)
        self.assertEqual("agnos-meta-docs-sync", fields["name"])
        self.assertEqual(front_matter(SKILL)[0]["description"], fields["description"])
        self.assertIn(".github/skills/agnos-meta-docs-sync/SKILL.md", body)

    def test_RQ_DOC_002_given_a_maintainer_skill_then_the_entry_point_documents_do_not_list_it(self):
        for name in ("AGENTS.md", "CLAUDE.md"):
            self.assertNotIn("agnos-meta-docs-sync", (ROOT / name).read_text(encoding="utf-8"), name)


class AgentTest(unittest.TestCase):
    """TASK-DOC-002: RQ-DOC-003."""

    def test_RQ_DOC_003_given_the_claude_code_pointer_then_it_runs_on_haiku_with_edit_tools_only(self):
        fields, _ = front_matter(POINTER_AGENT)
        self.assertEqual("agnos-meta-docs-sync", fields["name"])
        self.assertEqual("haiku", fields["model"])
        tools = {t.strip() for t in fields["tools"].split(",")}
        self.assertEqual(set(), tools - EDIT_TOOLS)                      # no Write, no notebook or web tool
        self.assertIn("Edit", tools)

    def test_RQ_DOC_003_given_the_definition_then_it_follows_the_skill_edits_four_files_and_never_commits(self):
        _, body = front_matter(AGENT)
        self.assertIn(".github/skills/agnos-meta-docs-sync/SKILL.md", body)
        for name in DOCUMENTS:
            self.assertIn(name, body)
        for ban in ("never commit", "never push", "only these four files"):
            self.assertIn(ban, body.lower(), ban)

    def test_RQ_DOC_003_given_the_definition_then_copilot_gets_only_the_tool_aliases_it_documents(self):
        fields, _ = front_matter(AGENT)
        self.assertEqual("agnos-meta-docs-sync", fields["name"])
        self.assertEqual(COPILOT_TOOLS, {t.strip() for t in fields["tools"].split(",")})

    def test_RQ_DOC_003_given_the_pointer_then_it_names_the_definition_and_holds_none_of_its_procedure(self):
        fields, body = front_matter(POINTER_AGENT)
        self.assertEqual(front_matter(AGENT)[0]["description"], fields["description"])
        self.assertIn(".github/agents/agnos-meta-docs-sync.agent.md", body)
        for procedure in ("changes_since.py", "never commit", *DOCUMENTS):
            self.assertNotIn(procedure, body, procedure)


if __name__ == "__main__":
    unittest.main()
