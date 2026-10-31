"""Tests of the report script of the agnos-meta-docs-sync skill (FTR-DOC-001, TASK-DOC-001), on a temporary git repository.

Run from the repository root: python -m unittest discover -s .github/skills/agnos-meta-docs-sync/tests -v
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import changes_since as cs  # noqa: E402

TRACE_TESTS = HERE.parents[1] / "agnos-trace" / "tests"      # the literal test of the agnos-trace skill
sys.path.insert(0, str(TRACE_TESTS))

IDENTITY = {"GIT_AUTHOR_NAME": "tester", "GIT_AUTHOR_EMAIL": "tester@example.invalid",
            "GIT_COMMITTER_NAME": "tester", "GIT_COMMITTER_EMAIL": "tester@example.invalid"}
SKILL_FRONT = '---\nname: {name}\ndescription: "{description}"\n---\n\n# {name}\n'


def git(repo, *args):
    env = {**os.environ, **IDENTITY}
    done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env=env, check=True)
    return done.stdout.strip()


def commit(repo, message, files):
    """Writes the files {relative path: text}, commits them, returns the commit ID."""
    for name, text in files.items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)
    return git(repo, "rev-parse", "HEAD")


class ChangesSinceTest(unittest.TestCase):
    """TASK-DOC-001: RQ-DOC-001, RQ-DOC-004."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        git(self.repo, "init", "-q")
        self.first = commit(self.repo, "chore: start", {"CHANGELOG.md": "# Changelog\n", "AGENTS.md": "# Agents\n",
                                                         "README.md": "# Readme\n"})
        self.second = commit(self.repo, "docs: changelog entry", {"CHANGELOG.md": "# Changelog\n- one\n"})
        commit(self.repo, "chore: index", {"process/INDEX.idx.md": "index\n", "process/_sessionstate/session.yaml": "x: 1\n"})
        self.skill = commit(self.repo, "feat(ABC): add a skill", {
            ".github/skills/one/SKILL.md": SKILL_FRONT.format(name="one", description="A process skill."),
            ".github/skills/agnos-meta-two/SKILL.md": SKILL_FRONT.format(name="agnos-meta-two", description="Builds a thing.")})

    def tearDown(self):
        self.tmp.cleanup()

    def target(self, report, name):
        return next(t for t in report["targets"] if t["file"] == name)

    def test_RQ_DOC_001_given_a_changelog_changed_before_two_commits_then_only_the_commit_with_real_changes_is_listed(self):
        changelog = self.target(cs.collect(self.repo), "CHANGELOG.md")
        self.assertEqual(self.second, changelog["lastCommit"])
        self.assertEqual([self.skill], [c["sha"] for c in changelog["commits"]])       # the index-only commit is left out
        self.assertEqual("feat(ABC): add a skill", changelog["commits"][0]["subject"])
        self.assertEqual([".github/skills/agnos-meta-two/SKILL.md", ".github/skills/one/SKILL.md"], changelog["commits"][0]["files"])

    def test_RQ_DOC_001_given_a_document_never_committed_then_its_last_change_is_null_and_every_commit_is_listed(self):
        missing = self.target(cs.collect(self.repo), "CLAUDE.md")
        self.assertIsNone(missing["lastCommit"])
        self.assertEqual(3, len(missing["commits"]))                                    # the index-only commit stays out

    def test_RQ_DOC_001_given_a_merge_commit_then_it_is_not_listed(self):
        git(self.repo, "checkout", "-q", "-b", "side")
        commit(self.repo, "feat(ABC): side", {"side.txt": "x\n"})
        git(self.repo, "checkout", "-q", "-")
        git(self.repo, "merge", "--no-ff", "-q", "-m", "Merge side", "side")
        subjects = [c["subject"] for c in self.target(cs.collect(self.repo), "CHANGELOG.md")["commits"]]
        self.assertIn("feat(ABC): side", subjects)
        self.assertNotIn("Merge side", subjects)

    def test_RQ_DOC_001_given_the_skills_then_each_has_a_name_a_description_and_a_maintainer_flag(self):
        skills = {s["name"]: s for s in cs.collect(self.repo)["skills"]}
        self.assertEqual({"one", "agnos-meta-two"}, set(skills))
        self.assertEqual((False, True), (skills["one"]["maintainer"], skills["agnos-meta-two"]["maintainer"]))
        self.assertEqual("A process skill.", skills["one"]["description"])
        self.assertEqual(".github/skills/one/SKILL.md", skills["one"]["path"])

    def test_RQ_MTA_002_given_a_prefixed_skill_whose_description_does_not_say_maintainer_then_it_is_flagged(self):
        commit(self.repo, "feat(ABC): a meta skill", {
            ".github/skills/agnos-meta-other/SKILL.md": SKILL_FRONT.format(name="agnos-meta-other", description="Does a thing.")})
        skills = {s["name"]: s for s in cs.collect(self.repo)["skills"]}
        self.assertTrue(skills["agnos-meta-other"]["maintainer"])

    def test_RQ_MTA_002_given_a_skill_without_the_prefix_whose_description_says_maintainer_then_it_is_not_flagged(self):
        commit(self.repo, "feat(ABC): another skill", {
            ".github/skills/agnos-other/SKILL.md": SKILL_FRONT.format(name="agnos-other", description="AGNOS maintainer skill. Does a thing.")})
        skills = {s["name"]: s for s in cs.collect(self.repo)["skills"]}
        self.assertFalse(skills["agnos-other"]["maintainer"])

    def test_RQ_DOC_004_given_two_runs_then_the_output_is_the_same_and_valid_json(self):
        first = subprocess.run([sys.executable, str(HERE.parent / "scripts" / "changes_since.py"), "--repo", str(self.repo)],
                               capture_output=True, text=True, check=True).stdout
        second = subprocess.run([sys.executable, str(HERE.parent / "scripts" / "changes_since.py"), "--repo", str(self.repo)],
                                capture_output=True, text=True, check=True).stdout
        self.assertEqual(first, second)
        self.assertEqual(self.skill, json.loads(first)["head"])

    def test_RQ_DOC_001_given_a_folder_that_is_not_a_repository_then_the_script_exits_1_with_a_message(self):
        with tempfile.TemporaryDirectory() as empty:
            done = subprocess.run([sys.executable, str(HERE.parent / "scripts" / "changes_since.py"), "--repo", empty],
                                  capture_output=True, text=True, check=False)
        self.assertEqual(1, done.returncode)
        self.assertIn("not a git repository", done.stderr)


class ScriptLiteralsTest(unittest.TestCase):
    """TASK-DOC-001: RQ-DOC-004, with the detector of the agnos-trace skill (RQ-TRC-067)."""

    @unittest.skipUnless(TRACE_TESTS.is_dir(), "the agnos-trace skill is not beside this one")
    def test_RQ_DOC_004_given_the_script_then_no_literal_is_written_more_than_once(self):
        import test_literals as detector
        counter = detector.python_literals(HERE.parent / "scripts" / "changes_since.py")
        self.assertEqual([], sorted(lit for lit, n in counter.items() if n > 1))


if __name__ == "__main__":
    unittest.main()
