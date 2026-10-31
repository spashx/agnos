"""Tests that the output is proved to behave as the workshop does (RQ-MTA-011, TASK-MTA-007; ADR-MTA-002: DEC-MTA-010).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-meta-release/tests -v
"""
import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import release  # noqa: E402

ROOT = HERE.parents[3]
DEMO = ROOT.parent / release.DEMO_FOLDER_NAME
BROKEN = (("broken.py", "def f(:\n"), ("broken.json", '{"a": }\n'))
BROKEN_BY_TOOL = (("node", "broken.js", "function f( {\n"), ("bash", "broken.sh", "if then\n"),
                  ("powershell", "broken.ps1", "function f {\n"))
SOUND = (("sound.py", "def f():\n    return 1\n"), ("sound.json", '{"a": 1}\n'), ("sound.js", "const a = 1;\n"),
         ("sound.sh", "echo a\n"), ("sound.ps1", "Write-Output 'a'\n"))


class Workspace(unittest.TestCase):
    def setUp(self):
        holder = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(holder.cleanup)
        self.base = Path(holder.name)


class ParseTest(Workspace):
    """RQ-MTA-011."""

    def test_RQ_MTA_011_given_a_python_or_json_file_that_no_longer_parses_then_it_is_named(self):
        for name, text in BROKEN:
            (self.base / name).write_text(text, encoding="utf-8")
        problems = release.parse_problems(self.base)
        for name, _ in BROKEN:
            self.assertTrue(any(name in problem for problem in problems), name)

    def test_RQ_MTA_011_given_a_script_of_another_language_that_no_longer_parses_then_it_is_named(self):
        for tool, name, text in BROKEN_BY_TOOL:
            if not shutil.which(tool):
                continue
            (self.base / name).write_text(text, encoding="utf-8")
            self.assertTrue(any(name in problem for problem in release.parse_problems(self.base)), name)

    def test_RQ_MTA_011_given_sound_scripts_then_nothing_is_named(self):
        for name, text in SOUND:
            (self.base / name).write_text(text, encoding="utf-8")
        self.assertEqual([], release.parse_problems(self.base))


class ComparisonTest(Workspace):
    """RQ-MTA-011."""

    @staticmethod
    def runner(results):
        def run(toolkit, _workspace):
            return results[toolkit]
        return run

    def test_RQ_MTA_011_given_the_same_results_from_both_then_nothing_is_named(self):
        same = {"a": {"file": b"x"}, "b": {"file": b"x"}}
        self.assertEqual([], release.compare_runs("a", "b", self.base, [("skill", self.runner(same))]))

    def test_RQ_MTA_011_given_a_result_that_differs_then_the_skill_and_the_file_are_named(self):
        different = {"a": {"file": b"x"}, "b": {"file": b"y"}}
        problems = release.compare_runs("a", "b", self.base, [("skill", self.runner(different))])
        self.assertEqual(1, len(problems))
        self.assertIn("skill", problems[0])
        self.assertIn("file", problems[0])

    def test_RQ_MTA_011_given_the_toolkit_path_in_a_result_then_it_makes_no_difference(self):
        self.assertEqual(release.without_path(b"see /x/a/.github", "/x/a"), release.without_path(b"see /y/b/.github", "/y/b"))


class DemoTest(Workspace):
    """RQ-MTA-011."""

    def test_RQ_MTA_011_given_the_files_agnos_init_writes_then_the_comparison_covers_its_readmes(self):
        for folder in ("1.requirements", "2.architecture", "3.plan", "_sessionstate"):
            self.assertIn(f"process/{folder}/readme.md", release.INIT_RESULTS)

    def test_RQ_MTA_011_given_no_demo_when_the_proof_runs_then_it_says_to_build_it(self):
        problems = release.prove(ROOT, self.base, str(self.base / "absent"))
        self.assertEqual(1, len(problems))
        self.assertIn("agnos-meta-demo", problems[0])

    def test_RQ_MTA_011_given_a_relative_demo_path_then_it_is_read_from_the_current_folder(self):
        self.assertEqual(Path("some/demo").resolve(), release.demo_folder(ROOT, "some/demo"))

    def test_RQ_MTA_011_given_no_demo_path_then_the_demo_is_the_one_beside_the_repository(self):
        self.assertEqual(ROOT.parent / release.DEMO_FOLDER_NAME, release.demo_folder(ROOT, None))

    @unittest.skipUnless(DEMO.is_dir(), "the demo is not built")
    def test_RQ_MTA_011_given_this_repository_and_the_demo_when_it_rehearses_then_it_exits_0_and_the_demo_stays(self):
        before = release.git(DEMO, "status", "--porcelain")
        output = self.base / "out"
        with contextlib.redirect_stdout(io.StringIO()):
            code = release.main(["--repo", str(ROOT), "--dry-run", "--output", str(output)])
        report = json.loads(Path(f"{output}{release.REPORT_SUFFIX}").read_text(encoding="utf-8"))
        self.assertEqual([], report["problems"])
        self.assertEqual(release.EXIT_OK, code)
        self.assertEqual({"noIdLeft": True, "sameBehaviour": True}, report["checks"])
        self.assertEqual(before, release.git(DEMO, "status", "--porcelain"))


if __name__ == "__main__":
    unittest.main()
