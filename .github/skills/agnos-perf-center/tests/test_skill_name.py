"""Tests of the skill's name, script and outputs (FTR-TRC-008, ADR-TRC-013: DEC-TRC-053 to DEC-TRC-055).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-perf-center/tests -v
"""
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import agnos_layout  # noqa: E402  RQ-PLG-036: the index and log names, as the scripts read them

import perf_center  # noqa: E402
sys.path.insert(0, str(HERE))
from test_perf_center import run_main  # noqa: E402

REPO = HERE.parents[3]
SKILL_NAME = "agnos-perf-center"
SKILL_FILES = (REPO / ".github" / "skills" / SKILL_NAME / "SKILL.md",
               REPO / ".claude" / "skills" / SKILL_NAME / "SKILL.md")
OUTPUTS = ("perf-center.html", "perf-center.json", "perf-center.data.js")   # RQ-TRC-143 / DEC-TRC-087: lowercase
FIXTURE = HERE / "fixtures" / "repo"
# Assembled, so that this file does not hold what it looks for.
FORMER = re.compile("|".join(("agnos[-_]" + "trace", "trace_" + "matrix",
                              "TRACEABILITY" + r"\.(html|json|data\.js)")), re.I)
# RQ-TRC-143 (TASK-TRC-132): the uppercase outputs of before DEC-TRC-087, matched with their case.
FORMER_UPPERCASE = re.compile("PERF" + "-CENTER" + r"\.(html|json|data\.js)")
FOLDER = re.escape(agnos_layout.FOLDER)     # RQ-PLG-036: the process folder, wherever the layout puts it
HISTORY = re.compile(rf"^({FOLDER}/3\.plan/|CHANGELOG\.md$|{FOLDER}/{re.escape(agnos_layout.INDEX)}$"
                     rf"|{FOLDER}/1\.requirements/FTR-TRC-008-|{FOLDER}/2\.architecture/ADR-TRC-013-"
                     rf"|{FOLDER}/1\.requirements/FTR-TRC-014-)")   # FTR-TRC-014 names the uppercase outputs as former
INSTRUCTIONS = REPO / ".github" / "instructions" / "agnos-sw-eng.instructions.md"


def live_files_holding_a_former_name(former=FORMER):
    """The tracked text files outside history that hold a former name (RQ-TRC-106, RQ-TRC-143)."""
    listed = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True, text=True, encoding="utf-8", check=True)
    found = []
    for name in listed.stdout.splitlines():
        path = REPO / name
        if HISTORY.match(name) or not path.is_file():
            continue
        if former.search(name) or former.search(path.read_bytes().decode("utf-8", "ignore")):
            found.append(name)
    return found


class SkillNameTest(unittest.TestCase):
    """TASK-TRC-089: RQ-TRC-104, RQ-TRC-105, RQ-TRC-106."""

    def test_RQ_TRC_104_given_the_two_entry_points_then_each_carries_the_name_and_says_it_is_not_code_speed(self):
        for skill in SKILL_FILES:
            text = skill.read_text(encoding="utf-8")
            self.assertIn(f"name: {SKILL_NAME}\n", text)
            self.assertIn("not code speed", text)

    def test_RQ_TRC_105_given_no_out_when_the_generator_runs_then_the_page_and_its_data_carry_the_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            process = Path(tmp) / "process"
            process.mkdir()
            (process / agnos_layout.INDEX).write_bytes((FIXTURE / "process" / agnos_layout.INDEX).read_bytes())
            code, _, _ = run_main(["--process", str(process), "--sources", str(FIXTURE / "src")])   # TASK-TRC-118: RQ-TRC-131
            self.assertEqual(0, code)
            names = {path.name for path in process.iterdir()}   # RQ-TRC-143: the names as written, case included
            for output in OUTPUTS:
                self.assertIn(output, names)

    def test_RQ_TRC_143_given_the_tracked_files_then_none_names_the_uppercase_outputs(self):
        """TASK-TRC-132: RQ-TRC-143 (DEC-TRC-087): Given the tracked files but plans, the changelog, the index and the
        features and ADRs naming them as former, Then none names the uppercase outputs."""
        self.assertEqual([], live_files_holding_a_former_name(FORMER_UPPERCASE))

    def test_RQ_TRC_105_given_the_page_script_then_its_title_starts_with_the_name(self):
        script = (HERE.parent / "assets" / "matrix.js").read_text(encoding="utf-8")
        self.assertIn("document.title = `Performance center — ", script)

    def test_RQ_TRC_106_given_the_tracked_files_then_only_history_keeps_a_former_name(self):
        self.assertEqual([], live_files_holding_a_former_name())

    def test_RQ_TRC_106_given_the_instructions_then_the_traceability_rule_is_still_there(self):
        self.assertIn("### MANDATORY TRACEABILITY", INSTRUCTIONS.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
