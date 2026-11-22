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
PROCESS_SKILL = "agnos-instructions"     # RQ-PLG-035 / DEC-PLG-030
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
FACTS, KNOWLEDGE = "0.facts", "4.knowledge"                     # RQ-PLG-048, RQ-PLG-049 / DEC-PLG-038
NEW_SUBFOLDERS = (FACTS, KNOWLEDGE)
FACTS_STATEMENTS = ("the user places", "never changes", "transform", "index")        # DEC-PLG-040
KNOWLEDGE_STATEMENTS = ("dynamic", "uneven maturity", "date")                       # DEC-PLG-040
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
FOLDER_GUIDE = f"{FOLDER}/{GUIDE}"      # RQ-PLG-033 / DEC-PLG-026
FOLDER_VERSION = f"{FOLDER}/VERSION.txt"
OWNED_FILES = {FOLDER_GUIDE: GUIDE_TEMPLATE, FOLDER_VERSION: SKILL_DIR / "assets/templates" / "VERSION.txt"}
GUIDE_EXAMPLE_TRIGRAM = b"EXP"
GUIDE_STEPS = ("new conversation", "AGNOS session", "Write the requirement", "approved", "commit-task",
               "End of session", "agnos-perf-center")
ID_TRIGRAM_RE = re.compile(rb"\b(?:FTR|RQ|ADR|DEC|PLAN|TASK)-([A-Z]{3})-\d{3}\b")
SUCCESS_STEP_RE = re.compile(r"^   - `0`:.*$", re.M)
TEMPLATES = SKILL_DIR / "assets" / "templates"
BLOCK_TEMPLATE = "agnos.block.md"                       # RQ-INI-019 / DEC-INI-014
QUESTION_LINE_START = b"- Where the process asks the user a question"
QUESTION_TOOLS = (b"`askQuestion`", b"`AskUserQuestion`", b"ask in chat")
# RQ-INI-020 / DEC-INI-015: the block's notes are its comments, the marker lines excepted.
COMMENT_RE = re.compile(rb"<!--(?! AGNOS:)(.*?)-->", re.S)
CONTEXT_SUBJECTS = (b"claude code", b"github copilot", b"session start", b"clear", b"compaction")
REINVOKE_ORDER = f"After a compaction, invoke `{PROCESS_SKILL}` again".encode()


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

    # RQ-INI-019 / DEC-INI-014
    def test_RQ_INI_019_given_a_new_project_then_both_blocks_are_identical_and_name_both_question_tools(self):
        for _, project, result in self.each_script():
            self.assertEqual(0, result.returncode, result.stderr)
            blocks = [(project / name).read_bytes() for name in ENTRY_FILES]
            self.assertEqual(blocks[0], blocks[1])
            question = next(line for line in blocks[0].splitlines() if line.startswith(QUESTION_LINE_START))
            for tool in QUESTION_TOOLS:
                self.assertIn(tool, question)

    # RQ-INI-020 / DEC-INI-015
    def test_RQ_INI_020_given_the_block_then_its_comments_explain_both_tools_on_start_clear_and_compaction(self):
        for _, project, result in self.each_script():
            self.assertEqual(0, result.returncode, result.stderr)
            data = (project / ENTRY_FILES[0]).read_bytes()
            notes = b" ".join(COMMENT_RE.findall(data)).lower()
            for subject in CONTEXT_SUBJECTS:
                self.assertIn(subject, notes)

    # RQ-INI-020 / DEC-INI-015
    def test_RQ_INI_020_given_the_block_then_it_orders_the_skill_invoked_again_outside_any_comment(self):
        for _, project, result in self.each_script():
            self.assertEqual(0, result.returncode, result.stderr)
            visible = COMMENT_RE.sub(b"", (project / ENTRY_FILES[0]).read_bytes())
            self.assertIn(REINVOKE_ORDER, visible)

    # RQ-INI-019 / DEC-INI-014
    def test_RQ_INI_019_given_the_templates_folder_then_it_holds_one_block_template(self):
        self.assertEqual([BLOCK_TEMPLATE], sorted(path.name for path in TEMPLATES.glob("*.block.md")))


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
                for entry in (*ENTRY_FILES, ".gitignore"):          # RQ-INI-016: the second run changes no .gitignore
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

    def test_RQ_PLG_050_given_a_project_without_facts_and_knowledge_when_run_then_both_are_added_and_nothing_else_changes(self):
        """Given an AGNOS project without 0.facts/ and 4.knowledge/, When agnos-init runs, Then both are added with their
        readme And no other file changes (RQ-PLG-050; DEC-PLG-038)."""
        for name, runner in RUNNERS.items():
            with self.subTest(script=name):
                project = self.project(name)
                self.assertEqual(0, runner(project).returncode)
                before = snapshot(project)
                for folder in NEW_SUBFOLDERS:
                    shutil.rmtree(project / FOLDER / folder)
                self.assertEqual(0, runner(project).returncode)
                self.assertEqual(before, snapshot(project))

    def test_RQ_PLG_048_given_the_facts_readme_then_it_states_who_places_facts_and_that_they_stay_unchanged(self):
        """Given the 0.facts readme template, Then it says the user places the facts, their content is never changed, and a
        skill may transform and index them (RQ-PLG-048; DEC-PLG-040)."""
        text = (TEMPLATES / f"{FACTS}.{README}").read_text(encoding="utf-8").lower()
        for statement in FACTS_STATEMENTS:
            self.assertIn(statement, text)

    def test_RQ_PLG_049_given_the_knowledge_readme_then_it_states_dynamic_uneven_dated_content(self):
        """Given the 4.knowledge readme template, Then it says its content is dynamic, of uneven maturity, and dated
        (RQ-PLG-049; DEC-PLG-040)."""
        text = (TEMPLATES / f"{KNOWLEDGE}.{README}").read_text(encoding="utf-8").lower()
        for statement in KNOWLEDGE_STATEMENTS:
            self.assertIn(statement, text)

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


# RQ-INI-023 / DEC-INI-017: a plan written with the former reference names, in CRLF, a task's own field among them.
PLAN_FILE = f"{FOLDER}/3.plan/PLAN-ABC-001-a.md"
OLD_PLAN = (b"# PLAN-ABC-001: A\r\n\r\n## Overview\r\n- **Requirements**: RQ-ABC-009\r\n\r\n## References\r\n"
            b"- **Requirements**: RQ-ABC-001,\r\n  RQ-ABC-002\r\n- **ADRs**: ADR-ABC-001\r\n"
            b"- **Requirements handed to another component**: None\r\n\r\n## Tasks\r\n\r\n### TASK-ABC-001: Do it\r\n"
            b"- **Requirements**: RQ-ABC-001")
NEW_PLAN = OLD_PLAN.replace(b"## References\r\n- **Requirements**: RQ-ABC-001,",
                            b"## References\r\n- **Requirement refs**: RQ-ABC-001,").replace(
                            b"- **ADRs**: ADR-ABC-001", b"- **ADR refs**: ADR-ABC-001")
CONVERTED = "converted "
NOT_A_PLAN = f"{FOLDER}/3.plan/notes.md"


class PlanFieldConversionTest(InitCase):
    """RQ-INI-023 / DEC-INI-017: the former plan reference names are converted at every run."""

    def test_RQ_INI_023_given_a_plan_with_former_names_when_run_then_only_its_references_lines_are_renamed(self):
        """Given a CRLF plan with the former names under References, under its Overview and under a task, When either
        script runs, Then only the two References lines are renamed And both scripts write the same bytes And the plan is
        reported converted (RQ-INI-023)."""
        files = {PLAN_FILE: OLD_PLAN, NOT_A_PLAN: OLD_PLAN}
        for _, project, result in self.each_script(files):
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(NEW_PLAN, (project / PLAN_FILE).read_bytes())
            self.assertEqual(OLD_PLAN, (project / NOT_A_PLAN).read_bytes())
            self.assertIn(f"{CONVERTED}{PLAN_FILE}", result.stdout)
            self.assertNotIn(f"{CONVERTED}{NOT_A_PLAN}", result.stdout)

    def test_RQ_INI_023_given_a_converted_project_when_run_again_then_nothing_is_written_nor_reported(self):
        """Given a converted project, When run again, Then nothing is written And no converted line is reported (RQ-INI-023)."""
        for name, runner in RUNNERS.items():
            with self.subTest(script=name):
                project = self.project(name, {PLAN_FILE: OLD_PLAN})
                self.assertEqual(0, runner(project).returncode)
                before = snapshot(project)
                os.utime(project / PLAN_FILE, (OLD_TIME, OLD_TIME))
                result = runner(project)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual(before, snapshot(project))
                self.assertEqual(OLD_TIME, int((project / PLAN_FILE).stat().st_mtime))
                self.assertNotIn(CONVERTED, result.stdout)

    def test_RQ_INI_023_given_a_legacy_folder_when_run_then_it_is_moved_then_converted(self):
        """Given a project in the legacy process/ folder holding a plan with the former names, When run, Then it is moved
        And its plan converted (RQ-INI-023, RQ-PLG-038)."""
        legacy_plan = f"{LEGACY_FOLDER}/3.plan/PLAN-ABC-001-a.md"
        files = {f"{LEGACY_FOLDER}/{LEGACY_INDEX}": b"# index\n", legacy_plan: OLD_PLAN}
        for _, project, result in self.each_script(files):
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn(f"moved {LEGACY_FOLDER}", result.stdout)
            self.assertEqual(NEW_PLAN, (project / PLAN_FILE).read_bytes())
            self.assertIn(f"{CONVERTED}{PLAN_FILE}", result.stdout)


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


GITIGNORE = ".gitignore"
SESSION_STATE = f"{FOLDER}/{LAYOUT['sessionState']}"      # RQ-INI-016: the path agnos-init keeps out of git
IGNORE_LINE = SESSION_STATE.encode() + b"\n"


def ignored(project, path):
    """Whether git's ignore rules match the path, tracked or not (RQ-INI-016)."""
    return subprocess.run(["git", "check-ignore", "-q", "--no-index", "--", path], cwd=project).returncode == 0


class GitignoreTest(InitCase):
    """RQ-INI-016 / DEC-INI-012: the session state is added to .gitignore only when it is not ignored yet."""

    def test_RQ_INI_016_given_a_project_without_gitignore_when_run_then_it_is_created_with_the_session_state(self):
        for _, project, result in self.each_script():
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(IGNORE_LINE, (project / GITIGNORE).read_bytes())
            self.assertIn(f"created {GITIGNORE}", result.stdout)

    def test_RQ_INI_016_given_a_git_project_when_run_then_git_ignores_the_session_state(self):
        for name, runner in RUNNERS.items():
            with self.subTest(script=name):
                project = self.project(name)
                git(project, "init", "-q")
                self.assertFalse(ignored(project, SESSION_STATE))
                result = runner(project)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertTrue(ignored(project, SESSION_STATE))

    def test_RQ_INI_016_given_a_git_project_whose_rule_already_ignores_it_when_run_then_gitignore_is_unchanged(self):
        broader = f"# mine\n{FOLDER}/_sessionstate/\n".encode()
        for name, runner in RUNNERS.items():
            with self.subTest(script=name):
                project = self.project(name, {GITIGNORE: broader})
                git(project, "init", "-q")
                result = runner(project)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual(broader, (project / GITIGNORE).read_bytes())
                self.assertIn(f"unchanged {GITIGNORE}", result.stdout)

    def test_RQ_INI_016_given_a_tracked_session_state_and_no_rule_when_run_then_the_rule_is_added(self):
        for name, runner in RUNNERS.items():
            with self.subTest(script=name):
                project = self.project(name, {GITIGNORE: b"*.log\n", SESSION_STATE: b"platform: windows\n"})
                git(project, "init", "-q")
                git(project, "add", ".")
                git(project, "commit", "-q", "-m", "state")
                result = runner(project)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual(b"*.log\n" + IGNORE_LINE, (project / GITIGNORE).read_bytes())
                self.assertIn(f"added {GITIGNORE}", result.stdout)

    def test_RQ_INI_016_given_a_crlf_gitignore_without_final_newline_outside_git_when_run_then_the_line_is_added_in_crlf(self):
        original = b"# mine\r\nbuild/"
        for _, project, result in self.each_script({GITIGNORE: original}):
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(original + b"\r\n" + SESSION_STATE.encode() + b"\r\n", (project / GITIGNORE).read_bytes())
            self.assertIn(f"added {GITIGNORE}", result.stdout)

    def test_RQ_INI_016_given_the_line_already_present_outside_git_when_run_then_gitignore_is_unchanged(self):
        present = b"build/\r\n" + SESSION_STATE.encode() + b"\r\n"
        for _, project, result in self.each_script({GITIGNORE: present}):
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(present, (project / GITIGNORE).read_bytes())
            self.assertIn(f"unchanged {GITIGNORE}", result.stdout)


class GuideTest(InitCase):
    """RQ-PLG-021, RQ-PLG-022, RQ-PLG-033, DEC-PLG-016, DEC-PLG-017, DEC-PLG-026: the guide and the version in the process folder."""

    def test_RQ_PLG_033_given_a_new_project_when_either_script_runs_then_the_guide_and_version_are_created_in_the_folder(self):
        for _, project, result in self.each_script():
            self.assertEqual(0, result.returncode, result.stderr)
            for name, template in OWNED_FILES.items():
                self.assertEqual(template.read_bytes(), (project / name).read_bytes(), name)
                self.assertIn(f"created {name}", result.stdout)
            self.assertFalse((project / GUIDE).exists(), "a guide was written at the root")

    def test_RQ_PLG_033_given_files_with_other_content_when_run_then_they_are_rewritten_and_reported_updated(self):
        for _, project, result in self.each_script({name: b"# edited by hand\n" for name in OWNED_FILES}):
            self.assertEqual(0, result.returncode, result.stderr)
            for name, template in OWNED_FILES.items():
                self.assertEqual(template.read_bytes(), (project / name).read_bytes(), name)
                self.assertIn(f"updated {name}", result.stdout)

    def test_RQ_PLG_033_given_a_second_run_then_the_guide_and_version_are_reported_unchanged(self):
        for name, runner in RUNNERS.items():
            with self.subTest(script=name):
                project = self.project(name)
                self.assertEqual(0, runner(project).returncode)
                said = runner(project).stdout
                for owned in OWNED_FILES:
                    self.assertIn(f"unchanged {owned}", said)

    def test_RQ_PLG_033_given_a_root_guide_written_by_a_former_init_then_it_is_removed_and_reported_moved(self):
        former = GUIDE_TEMPLATE.read_bytes().split(b"\n", 1)[0] + b"\nan older guide\n"
        for _, project, result in self.each_script({GUIDE: former}):
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertFalse((project / GUIDE).exists())
            self.assertIn(f"moved {GUIDE} to {FOLDER_GUIDE}", result.stdout)

    def test_RQ_PLG_033_given_a_root_file_of_that_name_with_another_first_line_then_it_is_untouched(self):
        mine = b"# My own getting started\n"
        for _, project, result in self.each_script({GUIDE: mine}):
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(mine, (project / GUIDE).read_bytes())
            self.assertNotIn(f"moved {GUIDE}", result.stdout)

    def test_RQ_PLG_033_given_the_readme_and_the_success_step_then_they_name_the_guide_in_the_folder(self):
        self.assertIn(FOLDER_GUIDE, (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn(FOLDER_GUIDE, SUCCESS_STEP_RE.search((SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")).group())
        self.assertIn(f"`{FOLDER_GUIDE}`".encode(), GUIDE_TEMPLATE.read_bytes())

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
