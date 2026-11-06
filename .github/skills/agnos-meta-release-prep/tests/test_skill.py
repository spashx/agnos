"""Tests of the agnos-meta-release-prep procedure: the steps' order, nothing published, left out of the release
(RQ-PLG-028, RQ-PLG-029, RQ-PLG-030, TASK-PLG-034; ADR-PLG-005: DEC-PLG-022).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-meta-release-prep/tests -v
"""
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
ROOT = SKILL_DIR.parents[2]
NAME = SKILL_DIR.name
SKILL = SKILL_DIR / "SKILL.md"
POINTER = ROOT / ".claude" / "skills" / NAME / "SKILL.md"
CANONICAL = f".github/skills/{NAME}/SKILL.md"
sys.path.insert(0, str(ROOT / ".github" / "skills" / "agnos-meta-release" / "scripts"))
import release  # noqa: E402  RQ-MTA-002: the release's own layer rules

FRONT_RE = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.S)
DESCRIPTION_LIMIT = 1024
LINE_LIMIT = 500
# RQ-PLG-030: the procedure's steps, in this order, each by a marker its text holds
STEPS = ("release_prep.py check", "agnos-meta-docs-sync", "release_prep.py review", "AskUserQuestion",
         "release_prep.py set-version", "commit-task", "`agnos-meta-release` from", "`agnos-meta-plugin-proof` on",
         "agnos-marketplace", "merge, tag and push")
PROCEDURE_HEADING = "## Procedure"
PUBLISHING = re.compile(r"^\s*(?:git\s+(?:push|tag|merge)\b|.*release\.py\s+--dry-run|.*plugin_proof\.py)", re.M)
CODE_BLOCK_RE = re.compile(r"```[^\n]*\n(.*?)```", re.S)
NEXT_STEPS_HEADING = "## Next steps"


def parts(path):
    found = FRONT_RE.match(path.read_text(encoding="utf-8"))
    fields = dict(re.findall(r"^([a-z-]+):\s*(.*)$", found.group(1), re.M))
    return {key: value.strip().strip('"') for key, value in fields.items()}, found.group(2)


class DefinitionTest(unittest.TestCase):
    """DEC-PLG-022: one maintainer skill, written as the documented practices say."""

    def test_DEC_PLG_022_given_the_skill_then_its_name_is_its_folder_and_its_description_fits(self):
        fields, body = parts(SKILL)
        self.assertEqual(NAME, fields["name"])
        self.assertLessEqual(len(fields["description"]), DESCRIPTION_LIMIT)
        self.assertIn("USE FOR", fields["description"])
        self.assertLess(len(body.splitlines()), LINE_LIMIT)

    def test_DEC_PLG_022_given_the_claude_code_pointer_then_it_names_the_canonical_procedure(self):
        fields, body = parts(POINTER)
        self.assertEqual(NAME, fields["name"])
        self.assertIn(CANONICAL, body)

    def test_DEC_PLG_022_given_the_release_rules_then_the_skill_and_its_pointer_are_left_out(self):
        rules = release.load_rules()
        for path in (CANONICAL, f".github/skills/{NAME}/scripts/release_prep.py", f".claude/skills/{NAME}/SKILL.md"):
            self.assertEqual(release.LAYER_META, release.layer_of(path, rules), path)


class OrderTest(unittest.TestCase):
    """RQ-PLG-028 to RQ-PLG-030: the steps in order, the approval before anything is recorded."""

    def test_RQ_PLG_030_given_the_procedure_then_it_names_the_steps_in_order(self):
        body = parts(SKILL)[1].split(PROCEDURE_HEADING, 1)[1]
        positions = [body.find(step) for step in STEPS]
        self.assertNotIn(-1, positions, dict(zip(STEPS, positions)))
        self.assertEqual(sorted(positions), positions, dict(zip(STEPS, positions)))

    def test_RQ_PLG_030_given_the_next_steps_then_they_hold_the_short_sha_and_run_none_of_them(self):
        body = parts(SKILL)[1]
        self.assertIn(NEXT_STEPS_HEADING, body)
        self.assertIn("git rev-parse --short HEAD", body)
        commands = "\n".join(CODE_BLOCK_RE.findall(body.split(NEXT_STEPS_HEADING)[0]))
        self.assertIsNone(PUBLISHING.search(commands), "a publishing command is run before the next steps")

    def test_RQ_PLG_029_given_no_approval_then_the_procedure_commits_nothing(self):
        body = parts(SKILL)[1]
        self.assertRegex(body, r"(?i)not approve[^\n]*\n?[^\n]*commit nothing")


README = SKILL_DIR / "README.md"
MERMAID_RE = re.compile(r"```mermaid\n(.*?)```", re.S)
# RQ-PLG-030: the diagram's nodes, in the order of the release steps
DIAGRAM_STEPS = ("release_prep.py check", "agnos-meta-docs-sync", "release_prep.py review", "approves",
                 "release_prep.py set-version", "commit-task", "agnos-meta-release --dry-run", "agnos-meta-plugin-proof",
                 "agnos-marketplace", "merge, tag, push")


class ReadmeTest(unittest.TestCase):
    """RQ-PLG-030, TASK-PLG-048: the README draws the release steps in order, and stays out of the release."""

    def test_RQ_PLG_030_given_the_readme_then_its_diagram_names_the_steps_in_order(self):
        diagram = MERMAID_RE.search(README.read_text(encoding="utf-8")).group(1)
        self.assertTrue(diagram.startswith("flowchart"), diagram[:40])
        positions = [diagram.find(step) for step in DIAGRAM_STEPS]
        self.assertNotIn(-1, positions, dict(zip(DIAGRAM_STEPS, positions)))
        self.assertEqual(sorted(positions), positions, dict(zip(DIAGRAM_STEPS, positions)))

    def test_RQ_PLG_030_given_the_release_rules_then_the_readme_is_left_out(self):
        self.assertEqual(release.LAYER_META, release.layer_of(f".github/skills/{NAME}/README.md", release.load_rules()))


if __name__ == "__main__":
    unittest.main()
