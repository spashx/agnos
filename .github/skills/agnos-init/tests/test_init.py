"""Tests of agnos-init: each case runs both scripts on the same bytes (FTR-INI-001, TASK-INI-001; ADR-INI-001).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-init/tests -v
The bash version is run by Git Bash when found, else by `bash` on the PATH; set AGNOS_BASH to choose another one.
"""
import json
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
SKILL_NAME = "agnos-init"
PROCESS_SKILL = "agnos-process"
ANY_PATH_RE = re.compile(rb"\.\./|\.github|\.claude|\{\{")
MISSING_TARGET = "missing"
ENTRY_FILES = ("CLAUDE.md", "AGENTS.md")
# RQ-PLG-036 / DEC-PLG-027: the folder's names come from the layout the scripts' copies are generated from.
LAYOUT = json.loads((SKILL_DIR / "assets" / "layout.json").read_text(encoding="utf-8"))
FOLDER = LAYOUT["folder"]
INDEX = LAYOUT["index"]
LEGACY_FOLDER = LAYOUT["legacyFolder"]
LEGACY_INDEX = LAYOUT["legacyIndex"]
PROCESS_FOLDERS = tuple(LAYOUT["subfolders"])
README = "readme.md"
BEGIN = b"<!-- AGNOS:BEGIN"
END = b"<!-- AGNOS:END -->"
BOM = b"\xef\xbb\xbf"
OLD_TIME = 946684800
ID_RE = re.compile(rb"\b(?:FTR|RQ|ADR|DEC|PLAN|TASK)-[A-Z]{3}-\d{3}\b")
MAX_DESCRIPTION = 1024
MAX_SKILL_LINES = 500
PROJECT_RULES = f"{FOLDER}/{LAYOUT['projectRules']}"
GUIDE = "AGNOS-GETTING-STARTED.md"
GUIDE_TEMPLATE = SKILL_DIR / "assets/templates" / GUIDE
GUIDE_EXAMPLE_TRIGRAM = b"EXP"
GUIDE_STEPS = ("new conversation", "AGNOS session", "Write the requirement", "approved", "commit-task",
               "End of session", "agnos-perf-center")
ID_TRIGRAM_RE = re.compile(rb"\b(?:FTR|RQ|ADR|DEC|PLAN|TASK)-([A-Z]{3})-\d{3}\b")
SUCCESS_STEP_RE = re.compile(r"^   - `0`:.*$", re.M)


def bash_command():
    configured = os.environ.get("AGNOS_BASH")
    if configured:
        return configured
    return str(GIT_BASH) if GIT_BASH.exists() else "bash"


def run_powershell(project, target=".", script=PS_SCRIPT):
    return subprocess.run(["powershell", "-NoProfile", "-File", str(script), "-Target", target],
                          cwd=project, capture_output=True, text=True, encoding="utf-8")


def run_bash(project, target=".", script=SH_SCRIPT):
    return subprocess.run([bash_command(), Path(script).as_posix(), "--target", target],
                          cwd=project, capture_output=True, text=True, encoding="utf-8")


# RQ-PLG-008: a system runs the scripts it can; Linux usually has no PowerShell, and the two are compared where both run.
RUNNERS = {name: runner for name, tool, runner in (("powershell", "powershell", run_powershell), ("bash", bash_command(), run_bash))
           if shutil.which(tool)}


def snapshot(project):
    return {p.relative_to(project).as_posix(): p.read_bytes() for p in project.rglob("*") if p.is_file()}


class InitCase(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp(prefix="agnos-init-"))
        self.addCleanup(shutil.rmtree, self.base, ignore_errors=True)

    def project(self, name, files=None):
        project = self.base / name
        project.mkdir()
        for path, data in (files or {}).items():
            target = project / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        return project

    def each_script(self, files=None):
        """Runs both scripts, checks they wrote the same bytes, and returns (name, project, result) for each."""
        runs = []
        for name, runner in RUNNERS.items():
            project = self.project(name, files)
            runs.append((name, project, runner(project)))
        for _, project, _result in runs[1:]:
            self.assertEqual(snapshot(runs[0][1]), snapshot(project))
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

    def test_RQ_INI_001_given_an_absolute_target_when_either_script_runs_then_it_writes_there(self):
        for name, runner in RUNNERS.items():
            target = self.project(f"{name}-target")
            result = runner(self.project(f"{name}-elsewhere"), target.as_posix())
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue((target / ENTRY_FILES[0]).is_file(), name)

    def test_RQ_INI_001_given_a_missing_target_when_either_script_runs_then_it_exits_1_and_writes_nothing(self):
        for name, runner in RUNNERS.items():
            project = self.project(name)
            result = runner(project, MISSING_TARGET)
            self.assertEqual(1, result.returncode, name)
            self.assertEqual({}, snapshot(project), name)
            self.assertIn("agnos-init:", result.stderr, name)

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

    def test_RQ_PLG_004_given_a_new_project_when_run_then_both_blocks_name_the_process_skill_and_hold_no_path(self):
        for _, project, result in self.each_script():
            self.assertEqual(0, result.returncode, result.stderr)
            for name in ENTRY_FILES:
                data = (project / name).read_bytes()
                self.assertIn(f"`{PROCESS_SKILL}`".encode(), data, name)
                self.assertIsNone(ANY_PATH_RE.search(data), name)

    def test_RQ_INI_010_given_both_blocks_then_each_orders_the_read_and_none_relies_on_an_import(self):
        order = (f"Before any other action, invoke the skill named `{PROCESS_SKILL}` and follow it. "
                 "Run its START SESSION ACTION only when the user asks to start a session.").encode()
        for _, project, result in self.each_script():
            self.assertEqual(0, result.returncode, result.stderr)
            for name in ENTRY_FILES:
                data = (project / name).read_bytes()
                self.assertIn(order, data, name)
                self.assertFalse(any(line.startswith(b"@") for line in data.splitlines()), name)

    def test_RQ_PLG_018_given_both_blocks_then_each_reads_the_project_rules_and_names_them_the_improvement_target(self):
        for _, project, result in self.each_script():
            self.assertEqual(0, result.returncode, result.stderr)
            for name in ENTRY_FILES:
                data = (project / name).read_bytes()
                self.assertIn(f"Read `{PROJECT_RULES}` when it exists".encode(), data, name)
                self.assertIn(f"`{PROJECT_RULES}` is the improvement target".encode(), data, name)

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
                self.assertEqual(0, runner(project).returncode)
                before = snapshot(project)
                for path in project.rglob("*"):
                    if path.is_file():
                        os.utime(path, (OLD_TIME, OLD_TIME))
                result = runner(project)
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
                    for path, data in files.items():
                        (project / path).write_bytes(data)
                    result = runner(project)
                    self.assertEqual(1, result.returncode, name)
                    self.assertIn("AGENTS.md", result.stderr, name)
                    self.assertEqual(files, snapshot(project), name)


class ProcessFolderTest(InitCase):
    """RQ-INI-005."""

    def test_RQ_INI_005_given_a_new_project_when_run_then_each_folder_holds_only_its_readme_with_no_id(self):
        for _, project, result in self.each_script():
            self.assertEqual(0, result.returncode, result.stderr)
            for folder in PROCESS_FOLDERS:
                self.assertEqual([README], [p.name for p in (project / FOLDER / folder).iterdir()])
                data = (project / FOLDER / folder / README).read_bytes()
                self.assertEqual((SKILL_DIR / "assets/templates" / f"{folder}.{README}").read_bytes(), data)
                self.assertTrue(data.startswith(b"# "), folder)
                self.assertNotIn(b"\r", data, folder)
                self.assertIsNone(ID_RE.search(data), folder)

    def test_RQ_INI_005_given_a_folder_with_content_when_run_then_it_gets_no_readme_and_its_file_stays(self):
        plan = b"# PLAN\n"
        for _, project, result in self.each_script({f"{FOLDER}/3.plan/PLAN-X.md": plan}):
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertFalse((project / FOLDER / "3.plan" / README).exists())
            self.assertEqual(plan, (project / FOLDER / "3.plan/PLAN-X.md").read_bytes())

    def test_RQ_INI_005_given_a_readme_the_user_changed_when_run_again_then_it_stays(self):
        for name, runner in RUNNERS.items():
            with self.subTest(script=name):
                project = self.project(name)
                self.assertEqual(0, runner(project).returncode)
                readme = project / FOLDER / "3.plan" / README
                readme.write_bytes(b"# Mine\n")
                self.assertEqual(0, runner(project).returncode)
                self.assertEqual(b"# Mine\n", readme.read_bytes())

    def test_RQ_INI_005_given_a_new_project_when_init_then_index_run_then_both_exit_0(self):
        project = self.project("indexed")
        index = ROOT / ".github/skills/agnos-index/scripts/build-index"
        if "powershell" in RUNNERS:
            self.assertEqual(0, run_powershell(project).returncode)
            command = ["powershell", "-NoProfile", "-File", f"{index}.ps1"]
        else:
            self.assertEqual(0, run_bash(project).returncode)
            command = [bash_command(), f"{index.as_posix()}.sh"]
        result = subprocess.run(command, cwd=project, capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn(": 0 entries, 0 documents", result.stdout)


NEW_FOLDER = "agnos-process"
NEW_INDEX = "process.idx.md"
MOVED = f"moved {LEGACY_FOLDER}"
LEGACY_DOCUMENT = f"{LEGACY_FOLDER}/1.requirements/FTR-ABC-001.md"
AGNOS_FILES = {f"{LEGACY_FOLDER}/{LEGACY_INDEX}": b"# index\n", LEGACY_DOCUMENT: b"# FTR-ABC-001: A\n"}
GIT = ("git", "-c", "user.name=test", "-c", "user.email=test@example.org", "-c", "core.autocrlf=false")


def git(project, *arguments):
    """git run in a test project, with an identity of its own (RQ-PLG-038)."""
    return subprocess.run([*GIT, *arguments], cwd=project, capture_output=True, text=True, check=True).stdout


class MigrationTest(InitCase):
    """RQ-PLG-038, DEC-PLG-031: run on a copy of the skill whose layout names agnos-process/ and process.idx.md."""

    def setUp(self):
        """A copy of the skill's scripts and assets, its layout copies naming the new folder and index (RQ-PLG-038)."""
        super().setUp()
        skill = self.base / "skill"
        shutil.copytree(SKILL_DIR / "scripts", skill / "scripts")
        shutil.copytree(SKILL_DIR / "assets", skill / "assets")
        for name, pattern in (("agnos-layout.ps1", "${0} = '{1}'"), ("agnos-layout.sh", "{0}='{1}'")):
            path = skill / "scripts" / name
            prefix = "$" if name.endswith(".ps1") else ""
            lines = []
            for line in path.read_text(encoding="utf-8").splitlines():
                for key, value in (("AGNOS_FOLDER", NEW_FOLDER), ("AGNOS_INDEX", NEW_INDEX)):
                    if line.startswith(f"{prefix}{key} ") or line.startswith(f"{prefix}{key}="):
                        line = pattern.format(key, value)
                lines.append(line)
            path.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
        self.runners = {name: (lambda project, runner=runner, script=skill / "scripts" / script: runner(project, ".", script))
                        for name, runner, script in (("powershell", run_powershell, "init.ps1"), ("bash", run_bash, "init.sh"))
                        if name in RUNNERS}

    def each_run(self, files):
        """Runs both renamed scripts on the same files, checks they wrote the same bytes (RQ-PLG-038)."""
        runs = []
        for name, runner in self.runners.items():
            project = self.project(name, files)
            runs.append((name, project, runner(project)))
        for _, project, _result in runs[1:]:
            self.assertEqual(snapshot(runs[0][1]), snapshot(project))
        return runs

    def test_RQ_PLG_038_given_a_tracked_agnos_folder_when_run_then_git_shows_renames_and_it_is_reported_moved(self):
        """Given a git project with a tracked process/ of AGNOS, When run, Then git shows renames to agnos-process/ (RQ-PLG-038)."""
        for name, runner in self.runners.items():
            with self.subTest(script=name):
                project = self.project(name, AGNOS_FILES)
                git(project, "init", "-q")
                git(project, "add", ".")
                git(project, "commit", "-q", "-m", "process")
                result = runner(project)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertIn(MOVED, result.stdout)
                status = git(project, "status", "--porcelain")
                self.assertIn(f"R  {LEGACY_FOLDER}/{LEGACY_INDEX} -> {NEW_FOLDER}/{NEW_INDEX}", status)
                self.assertIn(f"R  {LEGACY_DOCUMENT} -> {NEW_FOLDER}/1.requirements/FTR-ABC-001.md", status)
                self.assertFalse((project / LEGACY_FOLDER).exists())

    def test_RQ_PLG_038_given_an_untracked_agnos_folder_when_run_then_it_is_renamed_and_reported_moved(self):
        """Given an untracked process/ of AGNOS, When run, Then it is renamed And reported moved (RQ-PLG-038)."""
        for _, project, result in self.each_run(AGNOS_FILES):
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn(MOVED, result.stdout)
            self.assertEqual(b"# index\n", (project / NEW_FOLDER / NEW_INDEX).read_bytes())
            self.assertTrue((project / NEW_FOLDER / "1.requirements/FTR-ABC-001.md").is_file())
            self.assertFalse((project / LEGACY_FOLDER).exists())

    def test_RQ_PLG_038_given_a_process_folder_without_index_when_run_then_it_is_left_untouched(self):
        """Given a process/ without INDEX.idx.md, When run, Then it is left as it was (RQ-PLG-038)."""
        files = {f"{LEGACY_FOLDER}/notes.txt": b"mine\n"}
        for _, project, result in self.each_run(files):
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertNotIn(MOVED, result.stdout)
            self.assertEqual(b"mine\n", (project / LEGACY_FOLDER / "notes.txt").read_bytes())
            self.assertTrue((project / NEW_FOLDER / "3.plan" / README).is_file())

    def test_RQ_PLG_038_given_both_folders_when_run_then_it_exits_1_names_both_and_changes_nothing(self):
        """Given process/ of AGNOS and agnos-process/, When run, Then the exit is 1 And nothing changed (RQ-PLG-038)."""
        files = {**AGNOS_FILES, f"{NEW_FOLDER}/3.plan/PLAN-X.md": b"# PLAN\n"}
        for name, runner in self.runners.items():
            with self.subTest(script=name):
                project = self.project(name, files)
                result = runner(project)
                self.assertEqual(1, result.returncode, name)
                self.assertIn(LEGACY_FOLDER, result.stderr)
                self.assertIn(NEW_FOLDER, result.stderr)
                self.assertEqual(files, snapshot(project))


class GuideTest(InitCase):
    """RQ-PLG-021, RQ-PLG-022, DEC-PLG-016, DEC-PLG-017."""

    def test_RQ_PLG_021_given_a_new_project_when_either_script_runs_then_the_guide_is_created_from_its_template(self):
        for _, project, result in self.each_script():
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(GUIDE_TEMPLATE.read_bytes(), (project / GUIDE).read_bytes())
            self.assertIn(f"created {GUIDE}", result.stdout)

    def test_RQ_PLG_021_given_a_guide_with_other_content_when_run_then_it_is_rewritten_and_reported_updated(self):
        for _, project, result in self.each_script({GUIDE: b"# edited by hand\n"}):
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(GUIDE_TEMPLATE.read_bytes(), (project / GUIDE).read_bytes())
            self.assertIn(f"updated {GUIDE}", result.stdout)

    def test_RQ_PLG_021_given_the_same_guide_when_run_again_then_it_is_reported_unchanged(self):
        for name, runner in RUNNERS.items():
            with self.subTest(script=name):
                project = self.project(name)
                self.assertEqual(0, runner(project).returncode)
                self.assertIn(f"unchanged {GUIDE}", runner(project).stdout)

    def test_RQ_PLG_021_given_the_template_then_it_names_each_step_and_no_path_outside_the_project(self):
        data = GUIDE_TEMPLATE.read_bytes()
        for step in GUIDE_STEPS:
            self.assertIn(step.encode(), data, step)
        self.assertIsNone(ANY_PATH_RE.search(data))

    def test_RQ_PLG_023_given_the_template_then_it_holds_the_artifacts_and_the_identifier_format(self):
        data = GUIDE_TEMPLATE.read_bytes()
        self.assertIn(b"`<TYPE>-<TRI>-<NNN>`", data)
        for folder in PROCESS_FOLDERS:
            self.assertIn(f"`{FOLDER}/{folder}/`".encode(), data, folder)

    def test_RQ_PLG_022_given_the_template_then_its_only_ids_are_the_guides_example(self):
        self.assertEqual({GUIDE_EXAMPLE_TRIGRAM}, set(ID_TRIGRAM_RE.findall(GUIDE_TEMPLATE.read_bytes())))


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

    def test_RQ_PLG_020_given_the_success_step_then_it_gives_a_new_conversation_then_an_agnos_session_as_two_steps(self):
        step = SUCCESS_STEP_RE.search(self.text).group()
        conversation, session = step.index("new conversation"), step.index("AGNOS session")
        self.assertLess(conversation, session)
        self.assertNotIn("new session", step)

    def test_RQ_INI_009_given_the_repository_then_the_pointer_and_both_lists_name_the_skill(self):
        self.assertEqual(SKILL_NAME, re.search(r"^name:\s*(\S+)\s*$", (ROOT / ".claude/skills" / SKILL_NAME / "SKILL.md").read_text(encoding="utf-8"), re.M).group(1))
        for name in ENTRY_FILES:
            self.assertIn(f"`{SKILL_NAME}`", (ROOT / name).read_text(encoding="utf-8"), name)


if __name__ == "__main__":
    unittest.main()
