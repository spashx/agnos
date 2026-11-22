"""Tests that delivered skills name their files from their own folder (RQ-PLG-005, TASK-PLG-002; ADR-PLG-001: DEC-PLG-004).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-meta-release/tests -v
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import agnos_layout  # noqa: E402  RQ-PLG-036: the process folder's names, as the scripts read them

ROOT = Path(__file__).resolve().parents[4]
SKILLS = ROOT / ".github" / "skills"
META_PREFIX = "agnos-meta-"
TESTS_FOLDER = "tests"
CACHE_FOLDER = "__pycache__"
SKILL_FILE = "SKILL.md"
PLACEHOLDER = "<skill-folder>"
WORKSHOP_PATH_RE = re.compile(r"\.github/|\.claude/|CLAUDE_")
COMMAND_RE = re.compile(r"scripts/\S+\.(?:ps1|sh|py)")
TEXT_SUFFIXES = {".md", ".ps1", ".sh", ".py", ".json", ".txt"}
GIT_BASH = Path(r"C:\Program Files\Git\bin\bash.exe")
INDEX_FILE = f"{agnos_layout.FOLDER}/{agnos_layout.INDEX}"
PERF_PAGE = f"{agnos_layout.FOLDER}/{agnos_layout.PERF_CENTER_PAGE}"


def delivered_skills():
    return [path for path in SKILLS.iterdir() if path.is_dir() and not path.name.startswith(META_PREFIX)]


def delivered_files():
    for skill in delivered_skills():
        for path in skill.rglob("*"):
            parts = path.relative_to(skill).parts
            if path.is_file() and path.suffix in TEXT_SUFFIXES and TESTS_FOLDER not in parts and CACHE_FOLDER not in parts:
                yield path


def bash():
    return str(GIT_BASH) if GIT_BASH.exists() else "bash"


class WordingTest(unittest.TestCase):
    """RQ-PLG-005."""

    def test_RQ_PLG_005_given_the_delivered_files_when_searched_then_none_holds_a_workshop_path(self):
        found = []
        for path in delivered_files():
            if WORKSHOP_PATH_RE.search(path.read_text(encoding="utf-8")):
                found.append(path.relative_to(SKILLS).as_posix())
        self.assertEqual([], found)

    def test_RQ_PLG_005_given_a_skill_that_runs_a_script_then_it_says_what_its_folder_is(self):
        for skill in delivered_skills():
            text = (skill / SKILL_FILE).read_text(encoding="utf-8")
            if COMMAND_RE.search(text):
                self.assertIn(f"`{PLACEHOLDER}` is the folder holding this file", text, skill.name)


class AnywhereTest(unittest.TestCase):
    """RQ-PLG-005: a skill copied away from the repository, as in an installed plugin, works on the project it is run from."""

    def setUp(self):
        self.base = Path(tempfile.mkdtemp(prefix="agnos-skill-paths-"))
        self.addCleanup(shutil.rmtree, self.base, ignore_errors=True)
        self.project = self.base / "project"
        (self.project / agnos_layout.FOLDER / "1.requirements").mkdir(parents=True)
        (self.project / "src").mkdir()
        (self.project / agnos_layout.FOLDER / "1.requirements" / "FTR-ABC-001-x.md").write_text("# FTR-ABC-001: X\n", encoding="utf-8")

    def installed(self, name):
        target = self.base / "plugin" / "skills" / name
        shutil.copytree(SKILLS / name, target, ignore=shutil.ignore_patterns(TESTS_FOLDER, CACHE_FOLDER))
        return target

    def run_here(self, *command):
        result = subprocess.run(command, cwd=self.project, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(0, result.returncode, result.stderr)

    def assert_only_in_project(self, name):
        self.assertTrue((self.project / name).is_file())
        self.assertFalse((self.base / "plugin" / name).exists())

    def test_RQ_PLG_005_given_an_installed_index_skill_when_run_from_a_project_then_the_index_lands_in_the_project(self):
        script = self.installed("agnos-index") / "scripts"
        if os.name == "nt":
            self.run_here("powershell", "-NoProfile", "-File", str(script / "build-index.ps1"))
        else:
            self.run_here(bash(), (script / "build-index.sh").as_posix())
        self.assert_only_in_project(INDEX_FILE)

    def test_RQ_PLG_005_given_an_installed_perf_center_when_run_from_a_project_then_the_page_lands_in_the_project(self):
        (self.project / INDEX_FILE).write_text("", encoding="utf-8")
        self.installed("agnos-graph")       # TASK-TRC-122, DEC-TRC-076: the perf center runs its sibling, as the plugin delivers both
        script = self.installed("agnos-perf-center") / "scripts" / "perf_center.py"
        self.run_here(sys.executable, str(script), "--process", agnos_layout.FOLDER, "--sources", "src")
        self.assert_only_in_project(PERF_PAGE)


if __name__ == "__main__":
    unittest.main()
