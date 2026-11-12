"""Tests of the agent identities of the replay engine (TASK-DMO-015; RQ-DMO-023, RQ-DMO-024, RQ-DMO-025;
ADR-DMO-002: DEC-DMO-008).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-meta-demo/tests -v
"""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
ROOT = SKILL_DIR.parents[2]
REPLAY = SKILL_DIR / "scripts" / "replay.ps1"
HUMAN = "nina-dev"
HUMAN_EMAIL = "nina-dev@agnos-demo.example"
CLAUDE = "Claude Code/Claude Opus 5.5"
CLAUDE_EMAIL = "noreply@anthropic.com"
COPILOT = "Copilot SDK in VS Code/auto"
COPILOT_EMAIL = "223556219+Copilot@users.noreply.github.com"
AGENT_KIND = "agent"
FILE_NAME = "notes.txt"
OTHER_FILE = "other.txt"
SUBJECT_TOGETHER = "feat(BKG): TASK-BKG-001 notes started"
SUBJECT_AGENT = "fix(BKG): TASK-BKG-001 notes corrected"
TRAILER_PREFIX = "Co-Authored-By: "
FORMAT_AUTHOR = "%an <%ae>"
FORMAT_COMMITTER = "%cn <%ce>"
FORMAT_BODY = "%B"


def identity(name, email):
    """RQ-DMO-024: an identity as git and the trailer write it."""
    return f"{name} <{email}>"


class ReplayAgentsTest(unittest.TestCase):
    """RQ-DMO-023, RQ-DMO-024, RQ-DMO-025 / DEC-DMO-008."""

    def setUp(self):
        self.work = Path(tempfile.mkdtemp(prefix="agnos-replay-agents-"))
        self.content = self.work / "content"
        self.content.mkdir()
        (self.content / FILE_NAME).write_text("first line\n", encoding="utf-8")
        (self.content / OTHER_FILE).write_text("other\n", encoding="utf-8")
        self.target = self.work / "target"

    def tearDown(self):
        shutil.rmtree(self.work, ignore_errors=True)

    def replay(self, steps):
        """RQ-DMO-021: replays a scenario of the given steps into the target, returns the process result."""
        scenario = {
            "defaultBranch": "main",
            "utcOffset": "+02:00",
            "identities": {
                HUMAN: {"email": HUMAN_EMAIL},
                CLAUDE: {"email": CLAUDE_EMAIL, "kind": AGENT_KIND},
                COPILOT: {"email": COPILOT_EMAIL, "kind": AGENT_KIND},
            },
            "steps": steps,
        }
        path = self.work / "scenario.json"
        path.write_text(json.dumps(scenario), encoding="utf-8")
        return subprocess.run(
            ["powershell", "-NoProfile", "-File", str(REPLAY), "-Scenario", str(path), "-Content", str(self.content),
             "-Toolkit", str(ROOT), "-Target", str(self.target)],
            capture_output=True, text=True, encoding="utf-8")

    def log(self, fmt, rev):
        """RQ-DMO-024: one field of one commit of the target."""
        return subprocess.run(["git", "log", "-1", f"--format={fmt}", rev], cwd=self.target,
                              capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()

    def first_step(self, **extra):
        """RQ-DMO-024: a human commit adding the notes file."""
        step = {"op": "commit", "date": "2026-08-24", "time": "10:00", "by": HUMAN, "message": SUBJECT_TOGETHER,
                "add": [FILE_NAME]}
        step.update(extra)
        return step

    def agent_step(self, **extra):
        """RQ-DMO-025: an agent commit editing the notes file."""
        step = {"op": "commit", "date": "2026-08-25", "time": "11:00", "by": COPILOT, "message": SUBJECT_AGENT,
                "edits": [{"path": FILE_NAME, "find": "first line", "replace": "first line, corrected"}]}
        step.update(extra)
        return step

    def test_RQ_DMO_024_given_a_step_with_claude_when_replayed_then_the_commit_ends_with_its_trailer(self):
        # Given a human step with Claude Code as co-author
        steps = [self.first_step(**{"with": CLAUDE})]
        # When it is replayed
        result = self.replay(steps)
        # Then the commit is the human's and its message ends with the single Claude Code trailer
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(identity(HUMAN, HUMAN_EMAIL), self.log(FORMAT_AUTHOR, "HEAD"))
        body = self.log(FORMAT_BODY, "HEAD").splitlines()
        self.assertEqual(SUBJECT_TOGETHER, body[0])
        self.assertEqual(TRAILER_PREFIX + identity(CLAUDE, CLAUDE_EMAIL), body[-1])
        self.assertEqual(1, sum(line.startswith(TRAILER_PREFIX) for line in body))

    def test_RQ_DMO_025_given_an_agent_step_when_replayed_then_the_agent_is_author_and_committer_without_trailer(self):
        # Given a human step, then a step by Copilot alone editing the committed file
        steps = [self.first_step(), self.agent_step()]
        # When they are replayed
        result = self.replay(steps)
        # Then the second commit has Copilot as author and committer and no trailer
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(identity(COPILOT, COPILOT_EMAIL), self.log(FORMAT_AUTHOR, "HEAD"))
        self.assertEqual(identity(COPILOT, COPILOT_EMAIL), self.log(FORMAT_COMMITTER, "HEAD"))
        self.assertNotIn(TRAILER_PREFIX, self.log(FORMAT_BODY, "HEAD"))

    def test_RQ_DMO_023_given_with_on_a_merge_when_replayed_then_it_fails_naming_the_step(self):
        # Given a merge step with a co-author
        steps = [self.first_step(),
                 {"op": "branch", "name": "feature/BKG"},
                 self.agent_step(**{"by": HUMAN}),
                 {"op": "merge", "date": "2026-08-26", "time": "12:00", "by": HUMAN, "branch": "feature/BKG",
                  "message": "Merge feature/BKG", "into": "main", "with": CLAUDE}]
        # When it is replayed
        result = self.replay(steps)
        # Then the replay fails naming the merge step
        self.assertEqual(1, result.returncode)
        self.assertIn("Merge feature/BKG", result.stderr)

    def test_RQ_DMO_024_given_with_naming_a_human_when_replayed_then_it_fails_naming_the_step(self):
        # Given a step whose co-author is a human identity
        steps = [self.first_step(**{"with": HUMAN})]
        # When it is replayed
        result = self.replay(steps)
        # Then the replay fails naming the step
        self.assertEqual(1, result.returncode)
        self.assertIn(SUBJECT_TOGETHER, result.stderr)

    def test_RQ_DMO_025_given_an_agent_adding_a_file_when_replayed_then_it_fails_naming_the_step(self):
        # Given a step by Copilot alone that adds a file
        steps = [self.first_step(), self.agent_step(**{"add": [OTHER_FILE]})]
        # When it is replayed
        result = self.replay(steps)
        # Then the replay fails naming the step, the first commit kept as the last one
        self.assertEqual(1, result.returncode)
        self.assertIn(SUBJECT_AGENT, result.stderr)
        self.assertEqual(SUBJECT_TOGETHER, self.log("%s", "HEAD"))

    def test_RQ_DMO_025_given_an_agent_step_with_a_co_author_when_replayed_then_it_fails_naming_the_step(self):
        # Given a step by Copilot alone that also names a co-author
        steps = [self.first_step(), self.agent_step(**{"with": CLAUDE})]
        # When it is replayed
        result = self.replay(steps)
        # Then the replay fails naming the step
        self.assertEqual(1, result.returncode)
        self.assertIn(SUBJECT_AGENT, result.stderr)


if __name__ == "__main__":
    unittest.main()
