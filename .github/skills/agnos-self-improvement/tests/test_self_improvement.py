"""Tests of agnos-self-improvement's budget scripts: each case runs both on the same project (FTR-RSI-001, TASK-RSI-002; ADR-RSI-001).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-self-improvement/tests -v
The bash version is run by Git Bash when found, else by `bash` on the PATH; set AGNOS_BASH to choose another one.
"""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
PS_SCRIPT = SCRIPTS / "budget.ps1"
SH_SCRIPT = SCRIPTS / "budget.sh"
GIT_BASH = Path(r"C:\Program Files\Git\bin\bash.exe")
ENCODING = "utf-8"
PROJECT_RULES = "agnos-process/project-rules.md"
INSTRUCTIONS = ".github/instructions/agnos-sw-eng.instructions.md"
DEFAULT_CEILING = 100
DECLARED_CEILING = 60
INSTRUCTIONS_CEILING = 400
EXIT_OK = 0
EXIT_ERROR = 1
EXIT_OVER = 2


def bash_command():
    """RQ-RSI-004: the bash that runs budget.sh."""
    configured = os.environ.get("AGNOS_BASH")
    if configured:
        return configured
    return str(GIT_BASH) if GIT_BASH.exists() else "bash"


def declaration(path, ceiling=None):
    """RQ-RSI-002: the sentence a project's entry point declares its target with."""
    suffix = f", at most {ceiling} lines" if ceiling else ""
    return f"- `{path}` is the improvement target{suffix}: the process's improvements go into it.\n"


class BudgetTest(unittest.TestCase):
    """RQ-RSI-002, RQ-RSI-003, RQ-RSI-004: `budget` run by both scripts in a throw-away git project."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "project"
        (self.root / ".git").mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode(ENCODING))

    def run_budget(self):
        """RQ-RSI-004: runs both scripts and asserts they agree; returns (exit code, stdout, stderr)."""
        commands = (["powershell", "-NoProfile", "-File", str(PS_SCRIPT)], [bash_command(), str(SH_SCRIPT)])
        results = [subprocess.run(command, cwd=self.root, capture_output=True, text=True, encoding=ENCODING)
                   for command in commands]
        ps, sh = ((r.returncode, r.stdout.strip(), r.stderr.strip()) for r in results)
        self.assertEqual(ps, sh, "budget.ps1 and budget.sh disagree")
        return ps

    def test_RQ_RSI_003_given_project_rules_declared_without_ceiling_then_the_ceiling_is_100(self):
        """Given project-rules.md declared with no ceiling and 3 lines, When budget runs, Then ceiling=100 left=97."""
        self.write("CLAUDE.md", declaration(PROJECT_RULES))
        self.write(PROJECT_RULES, "a\nb\nc\n")
        code, out, err = self.run_budget()
        self.assertEqual(EXIT_OK, code, err)
        self.assertEqual(f"target={PROJECT_RULES} ceiling={DEFAULT_CEILING} lines=3 left={DEFAULT_CEILING - 3}", out)

    def test_RQ_RSI_003_given_a_declared_ceiling_then_it_is_the_ceiling(self):
        """Given `at most 60 lines` in AGENTS.md, When budget runs, Then ceiling=60."""
        self.write("AGENTS.md", declaration(PROJECT_RULES, DECLARED_CEILING))
        self.write(PROJECT_RULES, "a\n")
        code, out, err = self.run_budget()
        self.assertEqual(EXIT_OK, code, err)
        self.assertIn(f"ceiling={DECLARED_CEILING} ", out)

    def test_RQ_RSI_003_given_the_instructions_file_as_target_then_its_own_ceiling_is_read(self):
        """Given the instructions file declared, stating 400 lines, CRLF and no final newline, When budget runs, Then ceiling=400 lines=2."""
        self.write("CLAUDE.md", declaration(INSTRUCTIONS, DECLARED_CEILING))
        self.write(INSTRUCTIONS, f"# X\r\n- This file SHALL NOT exceed {INSTRUCTIONS_CEILING} lines. <!-- RQ -->")
        code, out, err = self.run_budget()
        self.assertEqual(EXIT_OK, code, err)
        self.assertIn(f"ceiling={INSTRUCTIONS_CEILING} lines=2 ", out)

    def test_RQ_RSI_002_given_no_declaration_then_it_stops_with_an_error(self):
        """Given entry points without a declaration, When budget runs, Then exit 1 naming the declaration."""
        self.write("CLAUDE.md", "# Project\n")
        code, out, err = self.run_budget()
        self.assertEqual(EXIT_ERROR, code)
        self.assertIn("is the improvement target", err)
        self.assertEqual("", out)

    def test_RQ_RSI_002_given_a_target_outside_the_git_root_then_it_stops_with_an_error(self):
        """Given a declared path climbing above the git root, When budget runs, Then exit 1 naming that path."""
        outside = "docs/../../plugin/agnos-sw-eng.instructions.md"
        self.write("CLAUDE.md", declaration(outside))
        code, _, err = self.run_budget()
        self.assertEqual(EXIT_ERROR, code)
        self.assertIn(outside, err)

    def test_RQ_RSI_002_given_an_absolute_target_then_it_stops_with_an_error(self):
        """Given an absolute declared path, When budget runs, Then exit 1 naming that path."""
        absolute = "/opt/agnos/agnos-sw-eng.instructions.md"
        self.write("CLAUDE.md", declaration(absolute))
        code, _, err = self.run_budget()
        self.assertEqual(EXIT_ERROR, code)
        self.assertIn(absolute, err)

    def test_RQ_RSI_003_given_a_target_over_its_ceiling_then_it_exits_2(self):
        """Given 3 lines for `at most 2 lines`, When budget runs, Then exit 2 with left=-1."""
        self.write("CLAUDE.md", declaration(PROJECT_RULES, 2))
        self.write(PROJECT_RULES, "a\nb\nc\n")
        code, out, _ = self.run_budget()
        self.assertEqual(EXIT_OVER, code)
        self.assertIn("left=-1", out)

    def test_RQ_RSI_003_given_a_declared_target_not_yet_created_then_it_counts_0_lines(self):
        """Given project-rules.md declared but absent, When budget runs, Then lines=0 and exit 0 (RQ-PLG-018 creates it)."""
        self.write("CLAUDE.md", declaration(PROJECT_RULES))
        code, out, err = self.run_budget()
        self.assertEqual(EXIT_OK, code, err)
        self.assertIn("lines=0 ", out)


class PortabilityTest(unittest.TestCase):
    """RQ-RSI-004: shell scripts only."""

    def test_RQ_RSI_004_given_the_scripts_folder_then_it_holds_the_two_shell_scripts_only(self):
        """Given scripts/, When its files are listed, Then they are budget.ps1 and budget.sh."""
        self.assertEqual({PS_SCRIPT.name, SH_SCRIPT.name}, {p.name for p in SCRIPTS.iterdir() if p.is_file()})


if __name__ == "__main__":
    unittest.main()
