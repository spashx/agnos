"""Tests of agnos-init: each case runs both scripts on the same bytes (FTR-INI-001, TASK-INI-001; ADR-INI-001).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-init/tests -v
The bash version is run by Git Bash when found, else by `bash` on the PATH; set AGNOS_BASH to choose another one.
"""
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
ROOT = SKILL_DIR.parents[2]
PS_SCRIPT = SKILL_DIR / "scripts" / "init.ps1"
SH_SCRIPT = SKILL_DIR / "scripts" / "init.sh"
GIT_BASH = Path(r"C:\Program Files\Git\bin\bash.exe")
INSTRUCTIONS = ".github/instructions/agnos-sw-eng.instructions.md"
SKILL_NAME = "agnos-init"
TOOLKIT_ARG = "../agnos"
TOOLKIT_ARG_WINDOWS = "..\\agnos"
ENTRY_FILES = ("CLAUDE.md", "AGENTS.md")
PROCESS_FOLDERS = ("1.requirements", "2.architecture", "3.plan", "_sessionstate")
BEGIN = b"<!-- AGNOS:BEGIN"
END = b"<!-- AGNOS:END -->"
BOM = b"\xef\xbb\xbf"
OLD_TIME = 946684800
ID_RE = re.compile(rb"\b(?:FTR|RQ|ADR|DEC|PLAN|TASK)-[A-Z]{3}-\d{3}\b")
MAX_DESCRIPTION = 1024
MAX_SKILL_LINES = 500


def bash_command():
    configured = os.environ.get("AGNOS_BASH")
    if configured:
        return configured
    return str(GIT_BASH) if GIT_BASH.exists() else "bash"


def run_powershell(project, toolkit):
    return subprocess.run(["powershell", "-NoProfile", "-File", str(PS_SCRIPT), "-Target", ".", "-Toolkit", toolkit],
                          cwd=project, capture_output=True, text=True, encoding="utf-8")


def run_bash(project, toolkit):
    return subprocess.run([bash_command(), SH_SCRIPT.as_posix(), "--target", ".", "--toolkit", toolkit],
                          cwd=project, capture_output=True, text=True, encoding="utf-8")


RUNNERS = {"powershell": run_powershell, "bash": run_bash}


def snapshot(project):
    return {p.relative_to(project).as_posix(): p.read_bytes() for p in project.rglob("*") if p.is_file()}


class InitCase(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp(prefix="agnos-init-"))
        self.addCleanup(shutil.rmtree, self.base, ignore_errors=True)
        instructions = self.base / "agnos" / INSTRUCTIONS
        instructions.parent.mkdir(parents=True)
        instructions.write_text("# instructions\n", encoding="utf-8")

    def project(self, name, files=None):
        project = self.base / name
        project.mkdir()
        for path, data in (files or {}).items():
            target = project / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        return project

    def each_script(self, files=None, toolkit=TOOLKIT_ARG):
        """Runs both scripts, checks they wrote the same bytes, and returns (name, project, result) for each."""
        runs = []
        for name, runner in RUNNERS.items():
            project = self.project(name, files)
            runs.append((name, project, runner(project, toolkit)))
        self.assertEqual(snapshot(runs[0][1]), snapshot(runs[1][1]))
        return runs


class ResultTest(InitCase):
    """RQ-INI-001, RQ-INI-002, RQ-INI-006."""

    def test_RQ_INI_001_given_a_new_project_when_either_script_runs_then_the_block_alone_is_written(self):
        for _, project, result in self.each_script():
            self.assertEqual(0, result.returncode, result.stderr)
            for name in ENTRY_FILES:
                data = (project / name).read_bytes()
                self.assertTrue(data.startswith(BEGIN), name)
                self.assertTrue(data.endswith(END + b"\n"), name)
                self.assertIn(f"created {name}", result.stdout)

    def test_RQ_INI_001_given_a_toolkit_without_instructions_when_either_script_runs_then_it_exits_1_and_writes_nothing(self):
        for _, project, result in self.each_script(toolkit="../missing"):
            self.assertEqual(1, result.returncode)
            self.assertEqual({}, snapshot(project))
            self.assertIn("agnos-init:", result.stderr)

    def test_RQ_INI_002_given_a_crlf_file_with_bom_and_no_final_newline_when_run_then_its_bytes_stay_and_the_block_is_crlf(self):
        original = BOM + "# Règles\r\nmine".encode("utf-8")
        for _, project, result in self.each_script({"CLAUDE.md": original}):
            self.assertEqual(0, result.returncode, result.stderr)
            data = (project / "CLAUDE.md").read_bytes()
            self.assertTrue(data.startswith(original + b"\r\n\r\n" + BEGIN))
            self.assertTrue(data.endswith(END + b"\r\n"))
            self.assertEqual(data.count(b"\n"), data.count(b"\r\n"))
            self.assertIn("added CLAUDE.md", result.stdout)

    def test_RQ_INI_002_given_an_outdated_block_with_text_around_when_run_then_only_the_block_changes(self):
        before, after = b"# Top\n\n", b"\n## Bottom\nmine\n"
        stale = before + BEGIN + b" stale -->\nold line\n" + END + b"\n" + after
        for _, project, result in self.each_script({"AGENTS.md": stale}):
            self.assertEqual(0, result.returncode, result.stderr)
            data = (project / "AGENTS.md").read_bytes()
            self.assertTrue(data.startswith(before + BEGIN))
            self.assertTrue(data.endswith(END + b"\n" + after))
            self.assertNotIn(b"old line", data)
            self.assertIn("updated AGENTS.md", result.stdout)

    def test_RQ_INI_002_given_an_outdated_crlf_block_when_run_then_the_text_around_stays_and_the_block_is_crlf(self):
        before, after = b"# Top\r\n", b"## Bottom\r\n"
        stale = before + BEGIN + b" stale -->\r\nold line\r\n" + END + b"\r\n" + after
        for _, project, result in self.each_script({"AGENTS.md": stale}):
            self.assertEqual(0, result.returncode, result.stderr)
            data = (project / "AGENTS.md").read_bytes()
            self.assertTrue(data.startswith(before + BEGIN))
            self.assertTrue(data.endswith(END + b"\r\n" + after))
            self.assertEqual(data.count(b"\n"), data.count(b"\r\n"))
            self.assertIn("updated AGENTS.md", result.stdout)

    def test_RQ_INI_006_given_a_windows_toolkit_path_when_run_then_the_block_gives_it_with_slashes(self):
        for _, project, result in self.each_script(toolkit=TOOLKIT_ARG_WINDOWS):
            self.assertEqual(0, result.returncode, result.stderr)
            for name in ENTRY_FILES:
                data = (project / name).read_bytes()
                self.assertIn(f"{TOOLKIT_ARG}/{INSTRUCTIONS}".encode(), data, name)
                self.assertIn(f"{TOOLKIT_ARG}/.github/skills/".encode(), data, name)

    def test_RQ_INI_010_given_both_blocks_then_each_orders_the_read_and_none_relies_on_an_import(self):
        order = (f"Before any other action, read in full `{TOOLKIT_ARG}/{INSTRUCTIONS}`, "
                 "then run its START SESSION ACTION.").encode()
        for _, project, result in self.each_script():
            self.assertEqual(0, result.returncode, result.stderr)
            for name in ENTRY_FILES:
                data = (project / name).read_bytes()
                self.assertIn(order, data, name)
                self.assertFalse(any(line.startswith(b"@") for line in data.splitlines()), name)

    def test_RQ_INI_006_given_the_written_blocks_then_they_hold_no_artifact_id_and_no_placeholder(self):
        for _, project, _result in self.each_script():
            for name in ENTRY_FILES:
                data = (project / name).read_bytes()
                self.assertIsNone(ID_RE.search(data), name)
                self.assertNotIn(b"{{", data, name)


class RepeatTest(InitCase):
    """RQ-INI-003."""

    def test_RQ_INI_003_given_an_initialised_project_when_run_again_then_nothing_is_rewritten(self):
        for name, runner in RUNNERS.items():
            with self.subTest(script=name):
                project = self.project(name)
                self.assertEqual(0, runner(project, TOOLKIT_ARG).returncode)
                before = snapshot(project)
                for path in project.rglob("*"):
                    if path.is_file():
                        os.utime(path, (OLD_TIME, OLD_TIME))
                result = runner(project, TOOLKIT_ARG)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual(before, snapshot(project))
                for path in project.rglob("*"):
                    if path.is_file():
                        self.assertEqual(OLD_TIME, int(path.stat().st_mtime), path.name)
                for entry in ENTRY_FILES:
                    self.assertIn(f"unchanged {entry}", result.stdout)


class DamagedBlockTest(InitCase):
    """RQ-INI-004."""

    CASES = {
        "begin only": BEGIN + b" -->\ntext\n",
        "end only": b"text\n" + END + b"\n",
        "end first": END + b"\n" + BEGIN + b" -->\n",
        "two begins": BEGIN + b" -->\n" + BEGIN + b" -->\n" + END + b"\n",
        "two ends": BEGIN + b" -->\n" + END + b"\n" + END + b"\n",
    }

    def test_RQ_INI_004_given_a_damaged_block_when_run_then_it_exits_1_names_the_file_and_changes_nothing(self):
        for label, damaged in self.CASES.items():
            with self.subTest(case=label):
                files = {"CLAUDE.md": b"# valid\n", "AGENTS.md": damaged}
                base = self.base / label.replace(" ", "-")
                base.mkdir()
                for name, runner in RUNNERS.items():
                    project = base / name
                    project.mkdir()
                    (base / "agnos").mkdir(exist_ok=True)
                    (base / "agnos" / ".github").mkdir(exist_ok=True)
                    shutil.copytree(self.base / "agnos" / ".github" / "instructions",
                                    base / "agnos" / ".github" / "instructions", dirs_exist_ok=True)
                    for path, data in files.items():
                        (project / path).write_bytes(data)
                    result = runner(project, TOOLKIT_ARG)
                    self.assertEqual(1, result.returncode, name)
                    self.assertIn("AGENTS.md", result.stderr, name)
                    self.assertEqual(files, snapshot(project), name)


class ProcessFolderTest(InitCase):
    """RQ-INI-005."""

    def test_RQ_INI_005_given_a_new_project_when_run_then_each_folder_has_a_gitkeep(self):
        for _, project, result in self.each_script():
            self.assertEqual(0, result.returncode, result.stderr)
            for folder in PROCESS_FOLDERS:
                self.assertEqual(b"", (project / "process" / folder / ".gitkeep").read_bytes())

    def test_RQ_INI_005_given_a_folder_with_content_when_run_then_it_gets_no_gitkeep_and_its_file_stays(self):
        plan = b"# PLAN\n"
        for _, project, result in self.each_script({"process/3.plan/PLAN-X.md": plan}):
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertFalse((project / "process/3.plan/.gitkeep").exists())
            self.assertEqual(plan, (project / "process/3.plan/PLAN-X.md").read_bytes())

    def test_RQ_INI_005_given_a_new_project_when_init_then_index_run_then_both_exit_0(self):
        project = self.project("indexed")
        self.assertEqual(0, run_powershell(project, TOOLKIT_ARG).returncode)
        index = ROOT / ".github/skills/agnos-index/scripts/build-index.ps1"
        result = subprocess.run(["powershell", "-NoProfile", "-File", str(index)], cwd=project, capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)


class SkillPracticesTest(unittest.TestCase):
    """RQ-INI-009."""

    def setUp(self):
        self.text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    def test_RQ_INI_009_given_the_skill_then_its_front_matter_and_size_follow_the_practices(self):
        self.assertEqual(SKILL_NAME, re.search(r"^name:\s*(\S+)\s*$", self.text, re.M).group(1))
        description = re.search(r'^description:\s*"(.*)"\s*$', self.text, re.M).group(1)
        self.assertLessEqual(len(description), MAX_DESCRIPTION)
        self.assertIn("USE FOR", description)
        self.assertLess(len(self.text.splitlines()), MAX_SKILL_LINES)
        self.assertNotIn("disable-model-invocation", self.text)

    def test_RQ_INI_009_given_the_repository_then_the_pointer_and_both_lists_name_the_skill(self):
        self.assertEqual(SKILL_NAME, re.search(r"^name:\s*(\S+)\s*$", (ROOT / ".claude/skills" / SKILL_NAME / "SKILL.md").read_text(encoding="utf-8"), re.M).group(1))
        for name in ENTRY_FILES:
            self.assertIn(f"`{SKILL_NAME}`", (ROOT / name).read_text(encoding="utf-8"), name)


if __name__ == "__main__":
    unittest.main()
