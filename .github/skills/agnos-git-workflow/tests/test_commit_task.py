"""Tests of commit-task: each case runs both scripts on a temporary git repository (RQ-HST-030, TASK-PLG-064; DEC-HST-013).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-git-workflow/tests -v
The sh version is run by `bash` started from Git Bash when found, else from `bash` on the PATH; set AGNOS_BASH to choose another one.
"""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
PS_SCRIPT = SKILL_DIR / "scripts" / "commit-task.ps1"
SH_SCRIPT = SKILL_DIR / "scripts" / "commit-task.sh"
GIT_BASH = Path(r"C:\Program Files\Git\bin\bash.exe")
TASK = "TASK-ABC-001"
ADR = "ADR-ABC-002"
HARNESS = "Copilot SDK in VS Code"
MODEL = "auto"
EMAIL = "223556219+Copilot@users.noreply.github.com"
DESCRIPTION = "add the README sentence"
TRAILER = f"Co-Authored-By: {HARNESS}/{MODEL} <{EMAIL}>"
TRAILER_KEY = "co-authored-by:"
STAGED_FILE = "README.md"


def bash_command():
    configured = os.environ.get("AGNOS_BASH")
    if configured:
        return configured
    return str(GIT_BASH) if GIT_BASH.exists() else "bash"


def run_powershell(repo, *arguments):
    """Runs commit-task.ps1 in `repo` (DEC-HST-013)."""
    return subprocess.run(["powershell", "-NoProfile", "-File", str(PS_SCRIPT), *arguments],
                          cwd=repo, capture_output=True, text=True, encoding="utf-8")


def run_sh(repo, *arguments):
    """Runs commit-task.sh in `repo` (DEC-HST-013)."""
    return subprocess.run([bash_command(), SH_SCRIPT.as_posix(), *arguments],
                          cwd=repo, capture_output=True, text=True, encoding="utf-8")


# RQ-PLG-008: a system runs the scripts it can; the two are compared where both run.
RUNNERS = {name: runner for name, tool, runner in (("powershell", "powershell", run_powershell), ("bash", bash_command(), run_sh))
           if shutil.which(tool)}


def git(repo, *arguments):
    return subprocess.run(["git", *arguments], cwd=repo, capture_output=True, text=True, encoding="utf-8", check=True).stdout


def new_repo():
    """A repository with one commit and one staged change (RQ-HST-030)."""
    repo = Path(tempfile.mkdtemp())
    git(repo, "init", "-q")
    git(repo, "config", "user.name", "Tester")
    git(repo, "config", "user.email", "tester@example.com")
    git(repo, "config", "core.autocrlf", "false")
    (repo / STAGED_FILE).write_text("one\n", encoding="utf-8")
    git(repo, "add", STAGED_FILE)
    git(repo, "commit", "-q", "-m", "init")
    (repo / STAGED_FILE).write_text("one\ntwo\n", encoding="utf-8")
    git(repo, "add", STAGED_FILE)
    return repo


def arguments(**overrides):
    values = {"-Task": TASK, "-Type": "docs", "-Description": DESCRIPTION,
              "-Harness": HARNESS, "-Model": MODEL, "-Email": EMAIL}
    values.update(overrides)
    result = []
    for key, value in values.items():
        if value is not None:
            result += [key, value]
    return result


class CommitTaskTest(unittest.TestCase):
    """RQ-HST-030 / DEC-HST-013: the script builds the message and its single co-author trailer."""

    def setUp(self):
        self.repos = []

    def tearDown(self):
        for repo in self.repos:
            shutil.rmtree(repo, ignore_errors=True)

    def repo(self):
        repo = new_repo()
        self.repos.append(repo)
        return repo

    def test_RQ_HST_030_given_valid_arguments_then_the_commit_holds_one_harness_model_trailer(self):
        for name, runner in RUNNERS.items():
            with self.subTest(runner=name):
                repo = self.repo()
                result = runner(repo, *arguments())
                self.assertEqual(result.returncode, 0, result.stderr)
                message = git(repo, "log", "-1", "--format=%B")
                self.assertEqual(message.splitlines()[0], f"docs(ABC): {TASK} {DESCRIPTION}")
                self.assertEqual(message.lower().count(TRAILER_KEY), 1)
                self.assertIn(TRAILER, message.splitlines())

    def test_RQ_HST_030_given_an_adr_then_the_subject_holds_adr_slash_task(self):
        for name, runner in RUNNERS.items():
            with self.subTest(runner=name):
                repo = self.repo()
                result = runner(repo, *arguments(**{"-Adr": ADR}))
                self.assertEqual(result.returncode, 0, result.stderr)
                subject = git(repo, "log", "-1", "--format=%s").strip()
                self.assertEqual(subject, f"docs(ABC): {ADR}/{TASK} {DESCRIPTION}")

    def test_RQ_HST_030_given_an_iteration_then_its_trailer_precedes_the_co_author(self):
        for name, runner in RUNNERS.items():
            with self.subTest(runner=name):
                repo = self.repo()
                result = runner(repo, *arguments(**{"-Iteration": "1/5"}))
                self.assertEqual(result.returncode, 0, result.stderr)
                lines = git(repo, "log", "-1", "--format=%B").rstrip().splitlines()
                self.assertEqual(lines[-2:], ["Iteration: 1/5", TRAILER])

    def test_RQ_HST_030_given_dry_run_then_the_message_is_printed_and_head_is_unchanged(self):
        for name, runner in RUNNERS.items():
            with self.subTest(runner=name):
                repo = self.repo()
                head = git(repo, "rev-parse", "HEAD")
                result = runner(repo, *arguments(), "-DryRun")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(TRAILER, result.stdout.splitlines())
                self.assertEqual(git(repo, "rev-parse", "HEAD"), head)

    def test_RQ_HST_030_given_a_missing_value_then_exit_1_and_nothing_committed(self):
        for name, runner in RUNNERS.items():
            for missing in ("-Harness", "-Model", "-Email", "-Task", "-Type", "-Description"):
                with self.subTest(runner=name, missing=missing):
                    repo = self.repo()
                    head = git(repo, "rev-parse", "HEAD")
                    result = runner(repo, *arguments(**{missing: None}))
                    self.assertEqual(result.returncode, 1)
                    self.assertEqual(git(repo, "rev-parse", "HEAD"), head)

    def test_RQ_HST_030_given_an_empty_harness_then_exit_1(self):
        for name, runner in RUNNERS.items():
            with self.subTest(runner=name):
                repo = self.repo()
                result = runner(repo, *arguments(**{"-Harness": ""}))
                self.assertEqual(result.returncode, 1)

    def test_RQ_HST_030_given_an_invalid_id_or_type_then_exit_1(self):
        cases = ({"-Task": "TASK-AB-1"}, {"-Adr": "ADR-1"}, {"-Type": "feature"}, {"-Iteration": "one"})
        for name, runner in RUNNERS.items():
            for case in cases:
                with self.subTest(runner=name, case=case):
                    repo = self.repo()
                    head = git(repo, "rev-parse", "HEAD")
                    result = runner(repo, *arguments(**case))
                    self.assertEqual(result.returncode, 1)
                    self.assertEqual(git(repo, "rev-parse", "HEAD"), head)

    def test_RQ_HST_030_given_the_same_arguments_then_both_versions_print_the_same_message(self):
        if len(RUNNERS) < 2:
            self.skipTest("only one of powershell and bash is available")
        outputs = {name: runner(self.repo(), *arguments(**{"-Adr": ADR}), "-DryRun").stdout
                   for name, runner in RUNNERS.items()}
        self.assertEqual(outputs["powershell"], outputs["bash"])


if __name__ == "__main__":
    unittest.main()
