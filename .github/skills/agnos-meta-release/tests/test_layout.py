"""Tests of the layout generator and its check (RQ-PLG-036, RQ-PLG-037; ADR-PLG-006: DEC-PLG-027, DEC-PLG-028; TASK-PLG-039).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-meta-release/tests -v
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import layout  # noqa: E402
import release  # noqa: E402

ROOT = HERE.parents[3]
EXIT_OK = 0
EXIT_FAILED = 1
ENCODING = "utf-8"
OTHER_FOLDER = "agnos-process"
OTHER_INDEX = "process.idx.md"
GIT_BASH = Path("C:/Program Files/Git/bin/bash.exe")
PRINTED_KEYS = ("FOLDER", "INDEX", "SESSION_STATE", "SUBFOLDERS")


def bash():
    """The bash to run, Git's on Windows (RQ-PLG-036)."""
    return str(GIT_BASH) if GIT_BASH.exists() else "bash"


def run(root, *arguments):
    """layout.py run on a fixture root (RQ-PLG-036, RQ-PLG-037)."""
    return subprocess.run([sys.executable, str(HERE.parent / "scripts" / "layout.py"), *arguments, "--root", str(root)],
                          capture_output=True, text=True, encoding=ENCODING)


class LayoutFixture(unittest.TestCase):
    """A fixture repository holding the layout and the skill folders it is copied into (RQ-PLG-036, RQ-PLG-037)."""

    def setUp(self):
        """A temporary root with the repository's layout, the skills of the copies and no Markdown (RQ-PLG-036)."""
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        source = self.root / layout.LAYOUT_PATH
        source.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / layout.LAYOUT_PATH, source)
        for skill in layout.COPIES:
            (self.root / layout.SKILLS / skill / layout.SCRIPTS).mkdir(parents=True, exist_ok=True)

    def set_layout(self, **values):
        """Changes values of the fixture's layout.json (RQ-PLG-036)."""
        path = self.root / layout.LAYOUT_PATH
        data = json.loads(path.read_text(encoding=ENCODING))
        data.update(values)
        path.write_text(json.dumps(data, indent=2), encoding=ENCODING)

    def copy(self, skill, language):
        """The path of one generated copy (RQ-PLG-036)."""
        return self.root / layout.SKILLS / skill / layout.SCRIPTS / layout.COPY_NAMES[language]

    def write_skill_text(self, text):
        """A delivered SKILL.md of the fixture holding the given text (RQ-PLG-037)."""
        path = self.root / layout.SKILLS / "agnos-index" / "SKILL.md"
        path.write_text(text, encoding=ENCODING)
        return path

    def printed(self, language):
        """FOLDER, INDEX, SESSION_STATE and SUBFOLDERS as the copy of one language reads them (RQ-PLG-036)."""
        if language == "py":
            namespace = {}
            exec(self.copy("agnos-perf-center", "py").read_text(encoding=ENCODING), namespace)
            return [namespace[key] if key != "SUBFOLDERS" else " ".join(namespace[key]) for key in PRINTED_KEYS]
        if language == "ps1":
            path = self.copy("agnos-index", "ps1")
            script = f". '{path}'; " + "; ".join(
                f"Write-Output ($AGNOS_{key} -join ' ')" for key in PRINTED_KEYS)
            output = subprocess.run(["powershell", "-NoProfile", "-Command", script], capture_output=True, text=True)
        else:
            path = self.copy("agnos-index", "sh").as_posix()
            script = f". '{path}'; " + "; ".join(f'printf "%s\\n" "$AGNOS_{key}"' for key in PRINTED_KEYS)
            output = subprocess.run([bash(), "-c", script], capture_output=True, text=True)
        return output.stdout.splitlines()


class LayoutTest(LayoutFixture):
    """layout.py --write and --check (RQ-PLG-036, RQ-PLG-037; TASK-PLG-039, TASK-PLG-042)."""

    def test_RQ_PLG_036_given_the_layout_when_written_then_each_copy_says_it_is_generated(self):
        """Given the layout, When the copies are written, Then each starts with its generated line (RQ-PLG-036)."""
        self.assertEqual(run(self.root, "--write").returncode, EXIT_OK)
        for skill, languages in layout.COPIES.items():
            for language in languages:
                first = self.copy(skill, language).read_text(encoding=ENCODING).splitlines()[0]
                self.assertIn(layout.GENERATED_MARK, first, f"{skill} {language}")

    def test_RQ_PLG_036_given_another_folder_when_written_then_every_language_reads_the_same_values(self):
        """Given another folder and index, When the copies are written, Then Python, PowerShell and bash read them (RQ-PLG-036)."""
        self.set_layout(folder=OTHER_FOLDER, index=OTHER_INDEX)
        self.assertEqual(run(self.root, "--write").returncode, EXIT_OK)
        expected = self.printed("py")
        self.assertEqual(expected[:2], [OTHER_FOLDER, OTHER_INDEX])
        self.assertEqual(self.printed("ps1"), expected)
        self.assertEqual(self.printed("sh"), expected)

    def test_RQ_PLG_037_given_the_copies_as_generated_then_the_check_passes(self):
        """Given the copies as generated and no Markdown, When checked, Then the exit is 0 (RQ-PLG-037)."""
        run(self.root, "--write")
        result = run(self.root, "--check")
        self.assertEqual(result.returncode, EXIT_OK, result.stdout + result.stderr)

    def test_RQ_PLG_037_given_a_copy_edited_by_hand_then_the_check_fails_naming_it(self):
        """Given a copy edited by hand, When checked, Then the exit is 1 And the copy is named (RQ-PLG-037)."""
        run(self.root, "--write")
        edited = self.copy("agnos-index", "sh")
        edited.write_text(edited.read_text(encoding=ENCODING) + "# edited\n", encoding=ENCODING)
        result = run(self.root, "--check")
        self.assertEqual(result.returncode, EXIT_FAILED)
        self.assertIn("agnos-index/scripts/agnos-layout.sh", result.stdout)

    def test_RQ_PLG_037_given_a_missing_copy_then_the_check_fails_naming_it(self):
        """Given a copy never written, When checked, Then the exit is 1 And the copy is named (RQ-PLG-037)."""
        result = run(self.root, "--check")
        self.assertEqual(result.returncode, EXIT_FAILED)
        self.assertIn("agnos-perf-center/scripts/agnos_layout.py", result.stdout)

    def test_RQ_PLG_037_given_a_skill_citing_an_old_subfolder_then_the_check_fails_naming_its_line(self):
        """Given folder agnos-process And a SKILL.md citing process/3.plan/, When checked, Then file and line are named (RQ-PLG-037)."""
        self.set_layout(folder=OTHER_FOLDER, index=OTHER_INDEX)
        run(self.root, "--write")
        self.write_skill_text("# Skill\n\nRead `process/3.plan/` first.\n")
        result = run(self.root, "--check")
        self.assertEqual(result.returncode, EXIT_FAILED)
        self.assertIn("agnos-index/SKILL.md:3", result.stdout)

    def test_RQ_PLG_037_given_a_skill_citing_only_declared_paths_then_the_check_passes(self):
        """Given a SKILL.md citing the folder, a subfolder's file, the index and the legacy folder, Then the check passes (RQ-PLG-037)."""
        self.set_layout(folder=OTHER_FOLDER, index=OTHER_INDEX)
        run(self.root, "--write")
        self.write_skill_text(f"`{OTHER_FOLDER}/`, `{OTHER_FOLDER}/3.plan/PLAN-X.md`, `{OTHER_FOLDER}/{OTHER_INDEX}`;"
                              " a `process/` holding `process/INDEX.idx.md` is moved.\n")
        result = run(self.root, "--check")
        self.assertEqual(result.returncode, EXIT_OK, result.stdout)

    def test_RQ_PLG_037_given_a_path_the_layout_does_not_declare_then_the_check_fails(self):
        """Given a SKILL.md citing a file at the folder's root the layout does not declare, Then the check fails (RQ-PLG-037)."""
        run(self.root, "--write")
        self.write_skill_text("See `process/NOTES.md`.\n")
        result = run(self.root, "--check")
        self.assertEqual(result.returncode, EXIT_FAILED)
        self.assertIn("process/NOTES.md", result.stdout)

    def test_RQ_PLG_036_given_a_delivered_script_holding_a_name_of_the_layout_then_the_check_fails_naming_its_line(self):
        """Given a delivered skill's script writing the index's name out, When checked, Then file and line are named (RQ-PLG-036)."""
        run(self.root, "--write")
        script = self.root / layout.SKILLS / "agnos-perf-center" / layout.SCRIPTS / "tool.py"
        script.write_text('"""A tool."""\nNAME = "INDEX.idx.md"\n', encoding=ENCODING)
        result = run(self.root, "--check")
        self.assertEqual(result.returncode, EXIT_FAILED)
        self.assertIn("agnos-perf-center/scripts/tool.py:2", result.stdout)

    def test_RQ_PLG_036_given_a_script_reading_the_copys_constant_then_the_check_passes_and_the_bare_name_fails(self):
        """Given AGNOS_VERSION read from the copy, Then it passes; Given 'VERSION.txt' written out, Then its line is named (RQ-PLG-033, RQ-PLG-036, DEC-PLG-032)."""
        run(self.root, "--write")
        script = self.root / layout.SKILLS / "agnos-init" / layout.SCRIPTS / "init.sh"
        script.write_text('OWNED="$AGNOS_GUIDE $AGNOS_VERSION"\n', encoding=ENCODING)
        result = run(self.root, "--check")
        self.assertEqual(result.returncode, EXIT_OK, result.stdout)
        script.write_text('OWNED="$AGNOS_GUIDE $AGNOS_VERSION"\nNAME=VERSION.txt\n', encoding=ENCODING)
        result = run(self.root, "--check")
        self.assertEqual(result.returncode, EXIT_FAILED)
        self.assertIn("agnos-init/scripts/init.sh:2: VERSION.txt", result.stdout)

    def test_RQ_PLG_036_given_a_python_script_reading_an_attribute_of_the_copy_then_the_check_passes_and_the_string_fails(self):
        """Given agnos_layout.VERSION read from the Python copy, Then it passes; Given "VERSION.txt" written out, Then its
        line is named (RQ-PLG-036, TASK-PLG-050, DEC-PLG-032)."""
        run(self.root, "--write")
        script = self.root / layout.SKILLS / "agnos-perf-center" / layout.SCRIPTS / "tool.py"
        script.write_text("path = folder / agnos_layout.VERSION\n", encoding=ENCODING)
        result = run(self.root, "--check")
        self.assertEqual(result.returncode, EXIT_OK, result.stdout)
        script.write_text('path = folder / agnos_layout.VERSION\nname = "VERSION.txt"\n', encoding=ENCODING)
        result = run(self.root, "--check")
        self.assertEqual(result.returncode, EXIT_FAILED)
        self.assertIn("agnos-perf-center/scripts/tool.py:2: VERSION.txt", result.stdout)

    def test_RQ_PLG_037_given_a_skill_citing_the_guide_and_version_in_the_folder_then_the_check_passes(self):
        """Given a SKILL.md citing agnos-process/AGNOS-GETTING-STARTED.md and agnos-process/VERSION.txt, Then it passes (RQ-PLG-033, RQ-PLG-037, DEC-PLG-032)."""
        run(self.root, "--write")
        self.write_skill_text("Read `agnos-process/AGNOS-GETTING-STARTED.md`; `agnos-process/VERSION.txt` names the version.\n")
        result = run(self.root, "--check")
        self.assertEqual(result.returncode, EXIT_OK, result.stdout)

    def test_RQ_PLG_036_given_a_maintainer_script_holding_a_name_of_the_layout_then_the_check_ignores_it(self):
        """Given an agnos-meta- skill's script writing the index's name out, When checked, Then it passes (RQ-PLG-036)."""
        run(self.root, "--write")
        script = self.root / layout.SKILLS / "agnos-meta-demo" / layout.SCRIPTS / "tool.py"
        script.write_text('NAME = "INDEX.idx.md"\n', encoding=ENCODING)
        self.assertEqual(run(self.root, "--check").returncode, EXIT_OK)

    def test_RQ_PLG_037_given_the_working_tree_then_the_check_passes(self):
        """Given this repository's working tree, When checked, Then the exit is 0 (RQ-PLG-037)."""
        result = run(ROOT, "--check")
        self.assertEqual(result.returncode, EXIT_OK, result.stdout + result.stderr)


class ReleaseTest(LayoutFixture):
    """The release checks the layout of the commit it rehearses (RQ-PLG-037, DEC-PLG-028; TASK-PLG-043)."""

    def commit(self):
        """The fixture committed as a git repository (RQ-PLG-037)."""
        for arguments in (("init", "-q"), ("add", "."), ("-c", "user.name=t", "-c", "user.email=t@example.org",
                                                         "commit", "-q", "-m", "fixture")):
            subprocess.run(["git", "-C", str(self.root), *arguments], check=True, capture_output=True)

    def test_RQ_PLG_037_given_a_commit_as_generated_then_the_release_finds_nothing(self):
        """Given a commit whose copies are as generated, When the release checks it, Then nothing is found (RQ-PLG-037)."""
        run(self.root, "--write")
        self.commit()
        self.assertEqual([], release.layout_findings(self.root))

    def test_RQ_PLG_037_given_a_commit_with_a_copy_edited_by_hand_then_the_release_names_it(self):
        """Given a committed copy edited by hand, When the release checks it, Then the copy is named (RQ-PLG-037)."""
        run(self.root, "--write")
        edited = self.copy("agnos-perf-center", "py")
        edited.write_text(edited.read_text(encoding=ENCODING) + "X = 1\n", encoding=ENCODING)
        self.commit()
        self.assertTrue(any("agnos-perf-center/scripts/agnos_layout.py" in f for f in release.layout_findings(self.root)))

    def test_RQ_PLG_037_given_a_commit_with_a_skill_citing_an_old_subfolder_then_the_release_names_its_line(self):
        """Given folder agnos-process And a committed SKILL.md citing process/3.plan/, Then its file and line are named (RQ-PLG-037)."""
        self.set_layout(folder=OTHER_FOLDER, index=OTHER_INDEX)
        run(self.root, "--write")
        self.write_skill_text("# Skill\n\nRead `process/3.plan/` first.\n")
        self.commit()
        self.assertTrue(any("agnos-index/SKILL.md:3" in f for f in release.layout_findings(self.root)))


if __name__ == "__main__":
    unittest.main()
