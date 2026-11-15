"""Tests that the console says everything to act on (RQ-PLG-014, TASK-PLG-013; ADR-PLG-002: DEC-PLG-009).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-meta-release/tests -v
"""
import contextlib
import io
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))
import release  # noqa: E402
from test_inventory import STRAY, stray_proof  # noqa: E402
from test_select import EXIT_FAILED, EXIT_OK, TOOLKIT_FILE, RehearsalCase, no_proof  # noqa: E402

LAST_LINE = "agnos-meta-release: exit="
TO_READ_TEXT = "# Toolkit\n\nThis rule fulfils RQ-ABC-001.\n"     # a removal leaves "fulfils ." to read
MENTION_TEXT = "# Toolkit\n\nSee agnos-meta-other.\n"


class ConsoleCase(RehearsalCase):
    def console(self, *args, proof=no_proof):
        out, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(errors):
            code = release.main([str(a) for a in args], proof=proof)
        return code, out.getvalue().splitlines()

    def rehearse_console(self, proof=no_proof):
        return self.console("--repo", self.repo, "--dry-run", "--output", self.output, proof=proof)


class FindingsTest(ConsoleCase):
    """RQ-PLG-014: what to read is printed, with its file and line."""

    def test_RQ_PLG_014_given_a_rehearsal_with_a_line_to_read_then_it_is_printed_with_its_file_and_line(self):
        self.commit({TOOLKIT_FILE: TO_READ_TEXT})
        code, lines = self.rehearse_console()
        self.assertEqual(EXIT_OK, code)
        self.assertTrue(any(line.startswith(f"toRead: {TOOLKIT_FILE}:3:") for line in lines), lines)

    def test_RQ_PLG_014_given_a_mention_of_a_meta_skill_then_it_is_printed_with_its_file_and_line(self):
        self.commit({TOOLKIT_FILE: MENTION_TEXT})
        _, lines = self.rehearse_console()
        self.assertTrue(any(line.startswith(f"mentions: {TOOLKIT_FILE}:3:") for line in lines), lines)


class LastLineTest(ConsoleCase):
    """RQ-PLG-014: the last line gives the exit code, whatever the outcome."""

    def test_RQ_PLG_014_given_a_rehearsal_that_passes_then_the_last_line_says_exit_0_and_the_files_on_disk(self):
        code, lines = self.rehearse_console()
        self.assertEqual(EXIT_OK, code)
        self.assertTrue(lines[-1].startswith(f"{LAST_LINE}0, 9 files,"), lines[-1])

    def test_RQ_PLG_014_given_a_rehearsal_that_fails_then_the_last_line_says_exit_1(self):
        code, lines = self.rehearse_console(proof=stray_proof)
        self.assertEqual(EXIT_FAILED, code)
        self.assertTrue(lines[-1].startswith(f"{LAST_LINE}1, 10 files,"), lines[-1])
        self.assertTrue(any(STRAY in line for line in lines), lines)

    def test_RQ_PLG_014_given_a_refusal_before_writing_then_the_last_line_says_exit_1_and_nothing_written(self):
        code, lines = self.console("--repo", self.repo, "--output", self.output)
        self.assertEqual(EXIT_FAILED, code)
        self.assertTrue(lines[-1].startswith(f"{LAST_LINE}1, nothing written"), lines[-1])


if __name__ == "__main__":
    unittest.main()
