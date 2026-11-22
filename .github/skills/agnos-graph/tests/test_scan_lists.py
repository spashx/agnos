"""Tests of the scan lists agnos-graph shows (RQ-TRC-119; FTR-TRC-011: RQ-TRC-129).

Moved from agnos-perf-center by TASK-TRC-118: the graph skill scans the sources (owner, 2026-11-22).
Run from the repository root: python -m unittest discover -s .github/skills/agnos-graph/tests -v
"""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import graph as gr  # noqa: E402
from test_graph import run_main  # noqa: E402

PROCESS = HERE / "fixtures" / "repo" / "process"
SOURCES = HERE / "fixtures" / "repo" / "src"


class ScanListsShownTest(unittest.TestCase):
    """TASK-TRC-104: RQ-TRC-119 — what is scanned and excluded is shown in the help and on every run; moved from agnos-perf-center by TASK-TRC-118."""

    def run_with(self, *extra):
        with tempfile.TemporaryDirectory() as tmp:
            code, stdout, stderr = run_main(["--process", str(PROCESS), "--sources", str(SOURCES),
                                             "--out", str(Path(tmp) / "graph.json"), *extra])
        self.assertEqual(0, code, stderr)
        return stdout.splitlines()

    def line(self, lines, prefix):
        found = [line for line in lines if line.startswith(f"agnos-graph: {prefix}")]
        self.assertEqual(1, len(found), (prefix, lines))
        return found[0]

    def test_RQ_TRC_119_given_help_then_ext_and_exclude_list_every_default_and_say_they_replace_it(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit):
            gr.parse_args(["--help"])
        text = " ".join(out.getvalue().split())
        for entry in [*gr.DEFAULT_EXCLUDES, *gr.DEFAULT_EXTENSIONS, *gr.DEFAULT_NAMES]:
            self.assertIn(entry, text)
        self.assertGreaterEqual(text.count("replaces"), 2)

    def test_RQ_TRC_119_given_a_default_run_then_the_lists_in_effect_precede_an_unchanged_summary_line(self):
        lines = self.run_with()
        excluded = self.line(lines, "excluded (default): ")
        extensions = self.line(lines, "scanned extensions (default): ")
        names = self.line(lines, "scanned names (always): ")
        for entry in gr.DEFAULT_EXCLUDES:
            self.assertIn(entry, excluded)
        for entry in gr.DEFAULT_EXTENSIONS:
            self.assertIn(entry, extensions)
        for entry in gr.DEFAULT_NAMES:
            self.assertIn(entry, names)
        self.assertRegex(lines[-1], r"^agnos-graph: \d+ elements")

    def test_RQ_TRC_119_given_user_lists_then_the_lines_say_user_and_hold_only_them(self):
        lines = self.run_with("--exclude", "*.md", "--ext", ".py")
        self.assertEqual("agnos-graph: excluded (user): *.md", self.line(lines, "excluded (user): "))
        self.assertEqual("agnos-graph: scanned extensions (user): .py", self.line(lines, "scanned extensions (user): "))


if __name__ == "__main__":
    unittest.main()
