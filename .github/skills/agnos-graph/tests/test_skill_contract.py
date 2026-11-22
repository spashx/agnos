"""Tests of the agnos-graph skill's contract and of its format reference (FTR-TRC-011; ADR-TRC-022).

TASK-TRC-121: RQ-TRC-133, RQ-TRC-130, RQ-TRC-119 (the report of the scan lines, moved from agnos-perf-center), RQ-TRC-102.
Run from the repository root: python -m unittest discover -s .github/skills/agnos-graph/tests -v
"""
import importlib.util
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from test_graph import FIXTURE, committed_fixture, run_main, setUpModule  # noqa: F401  (setUpModule: no git config)

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
SKILL = SKILL_DIR / "SKILL.md"
POINTER = SKILL_DIR.parents[2] / ".claude" / "skills" / "agnos-graph" / "SKILL.md"
FORMAT = SKILL_DIR / "references" / "graph-format.md"
MAX_LINES = 50                      # RQ-TRC-102, as for the performance center's skill
MAX_DESCRIPTION = 400
DESCRIPTION_RE = re.compile(r'^description: "(.*)"$', re.M)
PARAMETERS = ("--process", "--sources", "--out", "--ext", "--exclude", "--generated-at", "--call-graph", "--history",
              "--history-since", "--history-depth")
HAS_TREE_SITTER = importlib.util.find_spec("tree_sitter") is not None


def front_matter(text):
    """The block between the first two `---` lines."""
    return text.split("---\n")[1]


class SkillContractTest(unittest.TestCase):
    """TASK-TRC-121: RQ-TRC-133, RQ-TRC-102."""

    @classmethod
    def setUpClass(cls):
        cls.text = SKILL.read_text(encoding="utf-8")

    def test_RQ_TRC_102_given_the_skill_then_it_stays_within_its_lines_and_its_description(self):
        self.assertLessEqual(len(self.text.splitlines()), MAX_LINES)
        self.assertLessEqual(len(DESCRIPTION_RE.search(self.text).group(1)), MAX_DESCRIPTION)

    def test_RQ_TRC_133_given_the_skill_then_it_gives_its_parameters_outputs_exit_codes_and_its_format_reference(self):
        for parameter in PARAMETERS:
            self.assertIn(f"`{parameter}", self.text, parameter)
        for part in ("**Output:**", "**Exit codes:**", "`0`", "`1`", "references/graph-format.md"):
            self.assertIn(part, self.text, part)

    def test_RQ_TRC_133_given_the_claude_code_pointer_then_it_shares_the_front_matter_and_names_the_skill(self):
        pointer = POINTER.read_text(encoding="utf-8")
        self.assertEqual(front_matter(self.text), front_matter(pointer))
        self.assertIn(".github/skills/agnos-graph/SKILL.md", pointer)

    def test_RQ_TRC_119_given_the_skill_then_its_report_step_names_the_scan_lines(self):
        report = [line for line in self.text.splitlines() if line.startswith("**Report**")]
        self.assertEqual(1, len(report))
        for words in ("scanned extensions", "scanned names", "excluded"):
            self.assertIn(words, report[0])


class FormatReferenceTest(unittest.TestCase):
    """TASK-TRC-121: RQ-TRC-133, RQ-TRC-130: the reference names every key of a graph file."""

    def test_RQ_TRC_133_given_a_graph_with_every_option_then_the_reference_names_each_of_its_keys(self):
        document = FORMAT.read_text(encoding="utf-8")
        tmp = Path(tempfile.mkdtemp(prefix="agnos-graph-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        process, sources, _ = committed_fixture(tmp)
        out = tmp / "graph.json"
        extra = ["--call-graph"] if HAS_TREE_SITTER else []
        code, _, err = run_main(["--process", str(process), "--sources", str(sources), "--sources",
                                 str(process.parent / "calls"), "--out", str(out), "--history", *extra])
        self.assertEqual(0, code, err)
        data = json.loads(out.read_text(encoding="utf-8"))
        names = {*data, *data["meta"], *data["meta"]["summaries"], *data["elements"][0],
                 *next(iter(data["tasks"].values()))}
        if "callGraph" in data:
            names |= {"parsedFiles", "unparsedFiles"}
        for name in names:
            self.assertIn(f"`{name}`", document, name)
        self.assertTrue(FIXTURE.is_dir())


if __name__ == "__main__":
    unittest.main()
