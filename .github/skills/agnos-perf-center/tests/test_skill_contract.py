"""Tests of the skill's contract and references (FTR-TRC-007, ADR-TRC-012: DEC-TRC-050, DEC-TRC-051).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-perf-center/tests -v
"""
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import perf_center as tm  # noqa: E402

SKILL_DIR = HERE.parent
SKILL = SKILL_DIR / "SKILL.md"
REFERENCES = SKILL_DIR / "references"
FIXTURE = HERE / "fixtures" / "repo"
MAX_LINES = 50
MAX_DESCRIPTION = 400
DESCRIPTION_RE = re.compile(r'^description: "(.*)"$', re.M)


def size_problems(text):
    """What a SKILL.md text breaks of RQ-TRC-102: the limit it passes, named; nothing when within both."""
    problems = []
    if len(text.splitlines()) > MAX_LINES:
        problems.append(f"more than {MAX_LINES} lines")
    if len(DESCRIPTION_RE.search(text).group(1)) > MAX_DESCRIPTION:
        problems.append(f"description over {MAX_DESCRIPTION} characters")
    return problems


class SkillSizeTest(unittest.TestCase):
    """TASK-TRC-088: RQ-TRC-102, RQ-TRC-098."""

    def test_RQ_TRC_102_given_the_skill_then_it_stays_within_its_lines_and_its_description(self):
        self.assertEqual([], size_problems(SKILL.read_text(encoding="utf-8")))

    def test_RQ_TRC_102_given_a_skill_one_over_a_limit_then_that_limit_is_named(self):
        fits = 'description: "x"\n' + "line\n" * (MAX_LINES - 1)
        self.assertEqual([], size_problems(fits))
        self.assertEqual([f"more than {MAX_LINES} lines"], size_problems(fits + "line\n"))
        wide = f'description: "{"x" * (MAX_DESCRIPTION + 1)}"\n'
        self.assertEqual([f"description over {MAX_DESCRIPTION} characters"], size_problems(wide))

    def test_RQ_TRC_098_given_the_skill_then_it_describes_no_view_and_names_each_reference(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertNotIn("What the page shows", text)
        for reference in REFERENCES.glob("*.md"):
            self.assertIn(f"references/{reference.name}", text)


class DataFormatTest(unittest.TestCase):
    """TASK-TRC-088: RQ-TRC-100."""

    def test_RQ_TRC_100_given_a_page_with_every_option_then_the_document_names_each_block_and_field(self):
        document = (REFERENCES / "data-format.md").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "page.html"
            code = tm.main(["--process", str(FIXTURE / "process"), "--sources", str(FIXTURE / "src"), "--out", str(page),
                            "--call-graph", "--history"])
            self.assertEqual(0, code)
            data = json.loads(page.with_suffix(".json").read_text(encoding="utf-8"))
        names = {*data, *data["meta"], *data["quality"], *data["elements"][0]}
        for block in ("history", "delivery", "callGraph"):
            if block in data:
                names |= {block, *data[block]}
        for name in names:
            self.assertIn(f"`{name}`", document, name)


if __name__ == "__main__":
    unittest.main()
