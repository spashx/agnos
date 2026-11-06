"""Tests of the plugin proof (RQ-PLG-010, TASK-PLG-008; ADR-PLG-001: DEC-PLG-007).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-meta-plugin-proof/tests -v
"""
import ast
import contextlib
import io
import json
import os
import re
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))
import plugin_proof as proof  # noqa: E402

ROOT = SKILL_DIR.parents[2]
NAME = "agnos-meta-plugin-proof"
DESCRIPTION_RE = re.compile(r'^description: "(.*)"$', re.M)
LINES_LIMIT = 500
SKILLS = ("agnos-index", "agnos-init")
OUTPUTS = {"claude": "Skills (2)  agnos-index, agnos-init\nAgents (1)  x", "copilot": "Installed 2 skills."}


def marketplace(base):
    folder = base / "market"
    for skill in SKILLS:
        (folder / proof.PLUGIN_SKILLS / skill).mkdir(parents=True)
    return folder


class Runner:
    """Stands for the tools: records each command and answers as told."""

    def __init__(self, fail_on=None, answer=""):
        self.calls = []
        self.fail_on = fail_on
        self.answer = answer

    def __call__(self, command, cwd=None, env=None):
        self.calls.append(SimpleNamespace(command=[str(c) for c in command], cwd=cwd, env=env))
        text = " ".join(str(c) for c in command)
        code = 1 if self.fail_on and self.fail_on in text else 0
        out = self.answer if "-p" in command else next((said for tool, said in OUTPUTS.items() if tool in text), "")
        return SimpleNamespace(returncode=code, stdout=out)


class IsolationTest(unittest.TestCase):
    """RQ-PLG-010."""

    def test_RQ_PLG_010_given_each_tool_then_its_homes_are_inside_the_work_folder(self):
        work = Path("work")
        self.assertEqual(str(work / "claude-home"), proof.isolated_env("claude", work)["CLAUDE_CONFIG_DIR"])
        copilot = proof.isolated_env("copilot", work)
        self.assertEqual(str(work / "copilot-home"), copilot["COPILOT_HOME"])
        self.assertEqual(str(work / "copilot-cache"), copilot["COPILOT_CACHE_HOME"])

    def test_RQ_PLG_010_given_the_tools_questions_then_none_grants_every_tool(self):
        for tool in proof.TOOLS:
            command = " ".join(proof.ask_command(tool, "x", Path("plugin"), "question"))
            self.assertNotIn("allow-all", command)
            self.assertNotIn("dangerously", command)
            self.assertNotIn("bypass", command)

    def test_RQ_PLG_010_given_a_claude_binary_named_by_the_variable_then_it_is_used(self):
        with unittest.mock.patch.dict(os.environ, {"AGNOS_CLAUDE": "named"}):
            self.assertEqual("named", proof.find_tool("claude"))


class InstallTest(unittest.TestCase):
    """RQ-PLG-010."""

    def setUp(self):
        holder = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(holder.cleanup)
        self.base = Path(holder.name)
        self.market = marketplace(self.base)

    def test_RQ_PLG_010_given_a_tool_when_it_installs_then_no_model_is_called_and_the_skills_are_counted(self):
        runner = Runner()
        checks = proof.prove_install("copilot", "copilot", self.market, self.base, runner)
        self.assertEqual({proof.PASS}, {check["status"] for check in checks})
        self.assertFalse([call for call in runner.calls if "-p" in call.command])
        self.assertTrue(all(call.env["COPILOT_HOME"] for call in runner.calls))

    def test_RQ_PLG_010_given_a_failed_install_then_the_check_fails(self):
        checks = proof.prove_install("copilot", "copilot", self.market, self.base, Runner(fail_on="install"))
        self.assertIn(proof.FAIL, {check["status"] for check in checks})

    def test_RQ_PLG_010_given_fewer_skills_than_the_plugin_holds_then_the_check_fails(self):
        (self.market / proof.PLUGIN_SKILLS / "agnos-third").mkdir()
        checks = proof.prove_install("copilot", "copilot", self.market, self.base, Runner())
        self.assertIn(proof.FAIL, {check["status"] for check in checks})

    def test_RQ_PLG_010_given_a_model_that_did_not_do_it_then_it_is_not_observed_and_nothing_fails(self):
        project = self.base / "project"
        project.mkdir()
        checks = proof.ask_questions("copilot", "copilot", self.market / proof.PLUGIN_FOLDER, project, self.base,
                                     Runner(answer="I could not."), initialise=lambda *_: proof.PASS)
        self.assertEqual({proof.NOT_OBSERVED}, {c["status"] for c in checks if c["check"] != proof.INIT_DIRECT})

    def test_RQ_PLG_010_given_a_model_that_answered_then_the_answer_is_observed(self):
        project = self.base / "project"
        project.mkdir()
        checks = proof.ask_questions("copilot", "copilot", self.market / proof.PLUGIN_FOLDER, project, self.base,
                                     Runner(answer=f"{proof.PROCESS_ANSWER} {proof.AGENT_MARKER}"), initialise=lambda *_: proof.PASS)
        status = {check["check"]: check["status"] for check in checks}
        self.assertEqual(proof.PASS, status["process"])
        self.assertEqual(proof.PASS, status["agent"])

    def test_RQ_PLG_010_given_the_direct_call_of_init_fails_then_the_check_fails(self):
        project = self.base / "project"
        project.mkdir()
        checks = proof.ask_questions("copilot", "copilot", self.market / proof.PLUGIN_FOLDER, project, self.base,
                                     Runner(answer="no"), initialise=lambda *_: proof.FAIL)
        self.assertIn(proof.FAIL, {check["status"] for check in checks})


class MainTest(unittest.TestCase):
    """RQ-PLG-010."""

    def setUp(self):
        holder = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(holder.cleanup)
        self.base = Path(holder.name)

    def run_main(self, *args, runner=None, tools=None):
        errors, out = io.StringIO(), io.StringIO()
        with contextlib.redirect_stderr(errors), contextlib.redirect_stdout(out):
            code = proof.main([str(a) for a in args], run=runner or Runner(), find=lambda tool: (tools or {}).get(tool))
        return code, out.getvalue(), errors.getvalue()

    def test_RQ_PLG_010_given_no_marketplace_there_then_it_exits_1(self):
        code, _, errors = self.run_main("--marketplace", self.base / "absent")
        self.assertEqual(proof.EXIT_FAILED, code)
        self.assertIn("absent", errors)

    def test_RQ_PLG_010_given_no_tool_present_then_it_says_so_and_exits_0(self):
        market = marketplace(self.base)
        code, out, _ = self.run_main("--marketplace", market, "--work", self.base / "w")
        self.assertEqual(proof.EXIT_OK, code)
        self.assertIn("claude", out)
        self.assertIn(proof.ABSENT, out)

    def test_RQ_PLG_010_given_a_report_path_then_it_holds_the_checks(self):
        market = marketplace(self.base)
        report = self.base / "report.json"
        self.run_main("--marketplace", market, "--work", self.base / "w", "--report", report)
        self.assertIn("checks", json.loads(report.read_text(encoding="utf-8")))


class LinuxTest(unittest.TestCase):
    """RQ-PLG-010."""

    def test_RQ_PLG_010_given_windows_then_the_suites_run_in_wsl_with_translated_paths(self):
        runner = Runner()
        runner.answer = ""
        original = proof.wsl_path
        proof.wsl_path = lambda path, run: f"/mnt/{Path(path).name}"
        self.addCleanup(setattr, proof, "wsl_path", original)
        command = proof.linux_command(Path("repo"), True, runner)
        self.assertEqual("wsl", command[0])
        self.assertIn("/mnt/repo", command)

    def test_RQ_PLG_010_given_linux_then_the_suites_run_directly(self):
        command = proof.linux_command(Path("repo"), False, Runner())
        self.assertEqual("bash", command[0])


class PackagingTest(unittest.TestCase):
    """RQ-PLG-010, RQ-MTA-002: a maintainer skill, standard library only, never delivered."""

    def test_RQ_PLG_010_given_the_skill_then_both_files_carry_its_name_and_a_description_of_what_and_when(self):
        for path in (SKILL_DIR / "SKILL.md", ROOT / ".claude" / "skills" / NAME / "SKILL.md"):
            text = path.read_text(encoding="utf-8")
            self.assertIn(f"name: {NAME}\n", text)
            self.assertIn("USE FOR", DESCRIPTION_RE.search(text).group(1))
            self.assertLess(len(text.splitlines()), LINES_LIMIT)

    def test_RQ_PLG_010_given_the_script_then_it_imports_the_standard_library_and_its_own_folder_only(self):
        imported = set()
        for node in ast.walk(ast.parse((SKILL_DIR / "scripts" / "plugin_proof.py").read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                imported |= {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                imported.add(node.module.split(".")[0])
        beside = {path.stem for path in (SKILL_DIR / "scripts").glob("*.py")}     # RQ-PLG-036: nothing to install
        self.assertEqual(set(), imported - set(sys.stdlib_module_names) - beside)


if __name__ == "__main__":
    unittest.main()
