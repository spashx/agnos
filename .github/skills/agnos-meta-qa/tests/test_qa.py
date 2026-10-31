"""Tests of the agnos-meta-qa report (FTR-QLT-001, TASK-QLT-001; ADR-QLT-001: DEC-QLT-001 to DEC-QLT-007).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-meta-qa/tests -v
The tests of the real analysers are skipped until `qa.py setup` has run.
"""
import contextlib
import importlib.util
import io
import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
ROOT = SKILL_DIR.parents[2]
FIXTURES = HERE / "fixtures"
SKILL_NAME = "agnos-meta-qa"
FINDING_FIELDS = {"file", "line", "column", "endLine", "endColumn", "tool", "rule", "severity", "message", "fixable", "exception"}
NAME_RE = re.compile(r"^name:\s*(\S+)\s*$", re.M)
DESCRIPTION_RE = re.compile(r"^description:\s*(.*)$", re.M)
EXACT_PIN_RE = re.compile(r"^[a-z-]+==\d+\.\d+\.\d+$")
EXACT_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
INSTALLS = ("pip", "npm", "venv")

_spec = importlib.util.spec_from_file_location("agnos_meta_qa", SKILL_DIR / "scripts" / "qa.py")
qa = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(qa)


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def make_repo(folder):
    git(folder, "init", "-q")
    git(folder, "config", "user.email", "qa@example.invalid")
    git(folder, "config", "user.name", "qa")
    for path in ("src/clean.py", "src/changed.py", "tests/test_a.py", "tests/fixtures/f.py", "vendor/v.js", "README.md"):
        target = folder / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("x = 1\n", encoding="utf-8")
    git(folder, "add", ".")
    git(folder, "commit", "-qm", "first")


def run_main(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = qa.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class NormalisationTest(unittest.TestCase):
    """RQ-QLT-002, DEC-QLT-003."""

    RUFF = [{"code": "E501", "message": "Line too long", "filename": str(ROOT / "a" / "b.py"), "fix": None,
             "location": {"row": 3, "column": 121}, "end_location": {"row": 3, "column": 125}},
            {"code": "UP017", "message": "Use alias", "filename": str(ROOT / "a" / "b.py"), "fix": {"edits": []},
             "location": {"row": 4, "column": 1}, "end_location": {"row": 4, "column": 9}},
            {"code": "F821", "message": "Undefined name", "filename": str(ROOT / "a" / "b.py"), "fix": None,
             "location": {"row": 5, "column": 1}, "end_location": {"row": 5, "column": 2}}]
    ESLINT = [{"filePath": str(ROOT / "a" / "c.js"), "messages": [
        {"ruleId": "sonarjs/no-dead-store", "severity": 1, "message": "Dead", "line": 2, "column": 3, "endLine": 2, "endColumn": 8},
        {"ruleId": "sonarjs/x", "severity": 1, "message": "Fix", "line": 3, "column": 1, "fix": {"range": [0, 1], "text": ""}},
        {"ruleId": None, "severity": 2, "message": "Parsing error", "line": 9, "column": 1}]}]

    def test_RQ_QLT_002_given_ruff_output_when_normalised_then_each_finding_has_the_fields_and_a_relative_path(self):
        findings = qa.from_ruff(self.RUFF, ROOT)
        self.assertEqual(FINDING_FIELDS, set(findings[0]))
        self.assertEqual(("a/b.py", 3, 121, "ruff", "E501"), tuple(findings[0][k] for k in ("file", "line", "column", "tool", "rule")))
        self.assertEqual((False, True), (findings[0]["fixable"], findings[1]["fixable"]))

    def test_RQ_QLT_002_given_a_defect_rule_when_normalised_then_its_severity_is_error_and_others_warning(self):
        self.assertEqual(["warning", "warning", "error"], [f["severity"] for f in qa.from_ruff(self.RUFF, ROOT)])

    def test_RQ_QLT_002_given_eslint_output_when_normalised_then_each_finding_has_the_same_fields(self):
        findings = qa.from_eslint(self.ESLINT, ROOT)
        self.assertEqual(FINDING_FIELDS, set(findings[0]))
        self.assertEqual(("a/c.js", 2, "eslint", "sonarjs/no-dead-store", "warning", False),
                         tuple(findings[0][k] for k in ("file", "line", "tool", "rule", "severity", "fixable")))
        self.assertTrue(findings[1]["fixable"])
        self.assertIsNone(findings[1]["endLine"])

    def test_RQ_QLT_002_given_a_parsing_error_when_normalised_then_it_is_an_error_with_a_rule(self):
        parsing = qa.from_eslint(self.ESLINT, ROOT)[2]
        self.assertEqual(("error", "parsing-error"), (parsing["severity"], parsing["rule"]))

    def test_RQ_QLT_002_given_complexipy_output_when_normalised_then_only_what_exceeds_the_limit_is_kept_at_its_line(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "m.py"
            source.write_text("x = 1\n\n\nclass K:\n    def heavy(self):\n        pass\n\n\ndef light():\n    pass\n", encoding="utf-8")
            rows = [{"path": str(source), "function_name": "K::heavy", "complexity": 16},
                    {"path": str(source), "function_name": "light", "complexity": 15}]
            findings = qa.from_complexipy(rows, Path(folder))
        self.assertEqual(1, len(findings))
        self.assertEqual(FINDING_FIELDS, set(findings[0]))
        self.assertEqual(("m.py", 5, "complexipy", "cognitive-complexity"),
                         tuple(findings[0][k] for k in ("file", "line", "tool", "rule")))
        self.assertIn("16", findings[0]["message"])


class ExceptionTest(unittest.TestCase):
    """RQ-QLT-004, DEC-QLT-004."""

    def marked(self, text, rule="E501", line=2):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / "m.py").write_text(text, encoding="utf-8")
            finding = {"file": "m.py", "line": line, "rule": rule, "exception": None}
            qa.mark_exceptions([finding], Path(folder))
        return finding["exception"]

    def test_RQ_QLT_004_given_a_comment_on_the_line_above_then_the_finding_holds_its_reason(self):
        self.assertEqual("a table", self.marked("# agnos-qa-exception: E501 a table\nlong = 1\n"))

    def test_RQ_QLT_004_given_a_comment_on_the_line_then_the_finding_holds_its_reason(self):
        self.assertEqual("a table", self.marked("\nlong = 1  # agnos-qa-exception: E501 a table\n"))

    def test_RQ_QLT_004_given_a_comment_in_html_or_block_syntax_then_its_closing_mark_is_not_in_the_reason(self):
        self.assertEqual("a table", self.marked("<!-- agnos-qa-exception: E501 a table -->\nlong\n"))
        self.assertEqual("a table", self.marked("/* agnos-qa-exception: E501 a table */\nlong\n"))

    def test_RQ_QLT_004_given_no_reason_or_another_rule_then_the_finding_stays_open(self):
        self.assertIsNone(self.marked("# agnos-qa-exception: E501\nlong = 1\n"))
        self.assertIsNone(self.marked("# agnos-qa-exception: F401 a table\nlong = 1\n"))

    def test_RQ_QLT_002_given_findings_when_summarised_then_exceptions_are_counted_apart(self):
        counts = qa.count_findings([{"rule": "A", "exception": None}, {"rule": "A", "exception": None},
                                    {"rule": "B", "exception": "why"}])
        self.assertEqual({"total": 3, "open": 2, "exceptions": 1, "openByRule": {"A": 2}}, counts)


class ScopeTest(unittest.TestCase):
    """RQ-QLT-003."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        make_repo(self.repo)

    def test_RQ_QLT_003_given_changes_when_no_argument_then_only_the_changed_scripts_are_analysed(self):
        (self.repo / "src/changed.py").write_text("x = 2\n", encoding="utf-8")
        (self.repo / "src/new.js").write_text("var x;\n", encoding="utf-8")
        (self.repo / "tests/test_a.py").write_text("x = 2\n", encoding="utf-8")
        (self.repo / "README.md").write_text("changed\n", encoding="utf-8")
        self.assertEqual(["src/changed.py", "src/new.js"], qa.select_files(self.repo, False, []))

    def test_RQ_QLT_003_given_a_staged_change_when_no_argument_then_it_is_analysed(self):
        (self.repo / "src/changed.py").write_text("x = 2\n", encoding="utf-8")
        git(self.repo, "add", ".")
        self.assertEqual(["src/changed.py"], qa.select_files(self.repo, False, []))

    def test_RQ_QLT_003_given_all_then_clean_scripts_are_analysed_without_tests_fixtures_or_vendor(self):
        self.assertEqual(["src/changed.py", "src/clean.py"], qa.select_files(self.repo, True, []))

    def test_RQ_QLT_003_given_a_folder_then_its_scripts_are_analysed_without_its_tests(self):
        self.assertEqual(["src/changed.py", "src/clean.py"], qa.select_files(self.repo, False, ["src"]))
        self.assertEqual([], qa.select_files(self.repo, False, ["tests"]))

    def test_RQ_QLT_003_given_a_fixture_named_directly_then_it_is_analysed(self):
        self.assertEqual(["tests/fixtures/f.py"], qa.select_files(self.repo, False, ["tests/fixtures/f.py"]))

    def test_RQ_QLT_003_given_a_path_that_does_not_exist_then_it_is_an_error(self):
        with self.assertRaises(qa.QaError):
            qa.select_files(self.repo, False, ["nowhere"])

    def test_RQ_QLT_003_given_the_demo_content_then_it_is_left_out(self):
        self.assertTrue(qa.is_excluded(".github/skills/agnos-meta-demo/assets/content/service/a.py"))
        self.assertFalse(qa.is_excluded(".github/skills/agnos-meta-demo/scripts/a.py"))


class ExitCodeTest(unittest.TestCase):
    """RQ-QLT-005, RQ-QLT-006."""

    def test_RQ_QLT_005_given_a_missing_analyser_and_an_old_report_then_it_exits_1_names_setup_and_removes_the_report(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder)
            make_repo(repo)
            report = repo / "old.json"
            report.write_text("{}", encoding="utf-8")
            code, _, err = run_main("--root", str(repo), "check", "--all", "--out", str(report))
            self.assertEqual(1, code)
            self.assertIn("setup", err)
            self.assertFalse(report.exists())
            self.assertFalse((repo / qa.TOOLS_DIR).exists(), "check installs nothing")

    def test_RQ_QLT_005_given_nothing_to_analyse_then_it_exits_0_with_an_empty_report(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder)
            make_repo(repo)
            report = repo / "r.json"
            code, out, _ = run_main("--root", str(repo), "check", "--out", str(report))
            data = json.loads(report.read_text(encoding="utf-8"))
        self.assertEqual(0, code)
        self.assertEqual(([], 0), (data["findings"], data["summary"]["open"]))
        self.assertIn(str(report), out)


class RepositoryTest(unittest.TestCase):
    """RQ-QLT-001, RQ-QLT-006, RQ-QLT-008, DEC-QLT-001, DEC-QLT-005."""

    def test_RQ_QLT_006_given_the_assets_then_each_analyser_has_an_exact_version(self):
        lines = (SKILL_DIR / "assets" / "requirements.txt").read_text(encoding="utf-8").split()
        self.assertEqual({"ruff", "complexipy"}, {line.split("==")[0] for line in lines})
        for line in lines:
            self.assertRegex(line, EXACT_PIN_RE)
        package = json.loads((SKILL_DIR / "assets" / "package.json").read_text(encoding="utf-8"))
        self.assertEqual({"eslint", "eslint-plugin-sonarjs"}, set(package["dependencies"]))
        for version in package["dependencies"].values():
            self.assertRegex(version, EXACT_VERSION_RE)
        self.assertTrue((SKILL_DIR / "assets" / "package-lock.json").is_file())

    def test_RQ_QLT_006_given_the_tools_folder_then_git_ignores_it(self):
        done = subprocess.run(["git", "-C", str(ROOT), "check-ignore", "-q", f"{qa.TOOLS_DIR}/report.json"], check=False)
        self.assertEqual(0, done.returncode)

    def test_RQ_QLT_001_given_the_repository_then_no_hook_workflow_or_toolkit_procedure_calls_the_skill(self):
        for folder in (ROOT / ".githooks", ROOT / ".husky"):
            self.assertFalse(folder.exists(), folder)
        callers = [ROOT / ".github" / "skills" / "agnos-git-workflow" / "SKILL.md",
                   ROOT / ".github" / "instructions" / "agnos-sw-eng.instructions.md",
                   ROOT / "CLAUDE.md", ROOT / "AGENTS.md"]
        callers += list((ROOT / ".github" / "workflows").glob("*")) if (ROOT / ".github" / "workflows").is_dir() else []
        for path in callers:
            self.assertNotIn(SKILL_NAME, path.read_text(encoding="utf-8"), path)

    def test_RQ_QLT_008_given_both_skill_files_then_each_has_the_prefixed_name_within_the_documented_limits(self):
        for path in (SKILL_DIR / "SKILL.md", ROOT / ".claude" / "skills" / SKILL_NAME / "SKILL.md"):
            text = path.read_text(encoding="utf-8")
            self.assertEqual(SKILL_NAME, NAME_RE.search(text).group(1))
            self.assertLessEqual(len(DESCRIPTION_RE.search(text).group(1)), 1024)
            self.assertLess(len(text.splitlines()), 500)
            self.assertNotIn("disable-model-invocation", text)

    def test_RQ_QLT_001_given_the_description_then_it_limits_the_skill_to_an_explicit_request(self):
        description = DESCRIPTION_RE.search((SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")).group(1)
        self.assertIn("explicit", description)
        self.assertIn("never blocks", description)

    def test_RQ_QLT_008_given_the_procedure_then_it_states_the_editors_complement_apart_from_the_report(self):
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("VS Code", text)
        self.assertIn("never enter the report", text)

    def test_RQ_QLT_007_given_the_script_then_it_has_no_fix_option_and_no_install_outside_setup(self):
        source = (SKILL_DIR / "scripts" / "qa.py").read_text(encoding="utf-8")
        self.assertNotIn('"--fix"', source)
        check_source = source[source.index("def check("):source.index("def main(")]
        for word in INSTALLS:
            self.assertNotIn(word, check_source)


@unittest.skipUnless(qa.analysers_ready(ROOT), "run: python .github/skills/agnos-meta-qa/scripts/qa.py setup")
class RealAnalysersTest(unittest.TestCase):
    """RQ-QLT-002, RQ-QLT-004, RQ-QLT-007: the three analysers on the fixtures, named directly."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.report_path = Path(cls.tmp.name) / "report.json"
        before = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"], capture_output=True, check=True).stdout
        cls.code, cls.out, cls.err = run_main("check", str(FIXTURES / "sample.py"), str(FIXTURES / "sample.js"), "--out", str(cls.report_path))
        cls.status_same = before == subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"], capture_output=True, check=True).stdout
        cls.report = json.loads(cls.report_path.read_text(encoding="utf-8")) if cls.report_path.exists() else None

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def rules(self, tool):
        return {f["rule"] for f in self.report["findings"] if f["tool"] == tool}

    def test_RQ_QLT_005_given_findings_when_check_ends_then_it_exits_0(self):
        self.assertEqual(0, self.code, self.err)

    def test_RQ_QLT_002_given_the_fixtures_then_each_analyser_reports_with_the_same_fields(self):
        self.assertIn("F401", self.rules("ruff"))
        self.assertEqual({"cognitive-complexity"}, self.rules("complexipy"))
        self.assertIn("sonarjs/no-nested-conditional", self.rules("eslint"))
        for finding in self.report["findings"]:
            self.assertEqual(FINDING_FIELDS, set(finding))

    def test_RQ_QLT_002_given_the_report_then_it_holds_its_schema_scope_files_tools_and_counts(self):
        self.assertEqual(qa.SCHEMA_VERSION, self.report["schemaVersion"])
        self.assertEqual("paths", self.report["scope"])
        self.assertEqual(2, len(self.report["files"]))
        self.assertEqual({"ruff", "complexipy", "eslint", "eslint-plugin-sonarjs"}, set(self.report["tools"]))
        self.assertIn(str(self.report_path), self.out)

    def test_RQ_QLT_002_given_the_report_then_findings_are_sorted_by_file_and_line(self):
        keys = [(f["file"], f["line"], f["column"]) for f in self.report["findings"]]
        self.assertEqual(sorted(keys), keys)

    def test_RQ_QLT_004_given_a_justified_finding_in_each_language_then_it_stays_with_its_reason(self):
        reasons = {f["rule"]: f["exception"] for f in self.report["findings"] if f["exception"]}
        self.assertEqual({"E711": "kept for the test", "sonarjs/no-dead-store": "kept for the test"}, reasons)
        self.assertEqual(2, self.report["summary"]["exceptions"])

    def test_RQ_QLT_007_given_a_fixable_finding_when_check_runs_then_git_status_is_unchanged(self):
        self.assertTrue(self.status_same)


if __name__ == "__main__":
    unittest.main()
