"""Tests of the friction log read from git by agnos-trace (FTR-TRC-006, ADR-TRC-011: DEC-TRC-045), on small repositories.

Run from the repository root: python -m unittest discover -s .github/skills/agnos-trace/tests -v
"""
import contextlib
import io
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))

import history  # noqa: E402
from test_history import RepoTestCase, setUpModule  # noqa: E402,F401

LOG = "process/_sessionstate/METRICS_LOG.md"
HEADER = "| Date | TRI | AskUserQuestion | ErrorRecovery | ReTiered | VerificationCatches |\n|---|---|:-:|:-:|:-:|:-:|\n"
ROW_1 = "| 2026-10-01 | ABC | 1 | 2 | 3 | 4 |\n"
ROW_2 = "| 2026-10-02 | DEF | 0 | 1 | 0 | 2 |\n"
FEATURE = "process/feature.md"


class FrictionLogTest(RepoTestCase):
    """TASK-TRC-082: RQ-TRC-090, RQ-TRC-091."""

    def build(self, since=None):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            block = history.build(self.repo.top / "process", {}, {}, [], [self.repo.top / "process"], since, tasks={})
        return block, err.getvalue()

    def subject_of(self, block, entry):
        return block["commits"][entry[6]]["subject"]

    def test_RQ_TRC_090_given_a_log_then_each_row_comes_with_the_commit_that_added_it(self):
        self.repo.commit({LOG: HEADER + ROW_1}, message="first")
        self.repo.commit({LOG: HEADER + ROW_1 + ROW_2}, message="second")
        block, _ = self.build()
        friction = block["delivery"]["friction"]
        self.assertEqual([["2026-10-01", "ABC", 1, 2, 3, 4], ["2026-10-02", "DEF", 0, 1, 0, 2]], [e[:6] for e in friction])
        self.assertEqual(["first", "second"], [self.subject_of(block, e) for e in friction])

    def test_RQ_TRC_090_given_headers_renamed_then_the_counters_are_read_by_position(self):
        self.repo.commit({LOG: "| A | B | C | D | E | F |\n|-|-|-|-|-|-|\n" + ROW_1})
        block, _ = self.build()
        self.assertEqual([["2026-10-01", "ABC", 1, 2, 3, 4]], [e[:6] for e in block["delivery"]["friction"]])

    def test_RQ_TRC_090_given_a_row_removed_later_then_it_is_absent(self):
        self.repo.commit({LOG: HEADER + ROW_1 + ROW_2})
        self.repo.commit({LOG: HEADER + ROW_2})
        block, _ = self.build()
        self.assertEqual(["DEF"], [e[1] for e in block["delivery"]["friction"]])

    def test_RQ_TRC_090_given_a_row_not_committed_then_it_is_absent(self):
        self.repo.commit({LOG: HEADER + ROW_1})
        self.repo.write(LOG, HEADER + ROW_1 + ROW_2)
        block, _ = self.build()
        self.assertEqual(["ABC"], [e[1] for e in block["delivery"]["friction"]])

    def test_RQ_TRC_090_given_a_row_whose_commit_is_outside_the_history_read_then_it_is_left_out_silently(self):
        self.repo.commit({LOG: HEADER + ROW_1})
        self.repo.commit({LOG: HEADER + ROW_1 + ROW_2})
        block, err = self.build(since="2026-10-02T00:00:00+00:00")
        self.assertEqual(["DEF"], [e[1] for e in block["delivery"]["friction"]])
        self.assertEqual("", err)

    def test_RQ_TRC_091_given_a_malformed_row_then_it_is_left_out_and_named(self):
        bad = "| 2026-10-30 | TRC | x | 1 | 0 | 1 |"
        self.repo.commit({LOG: HEADER + bad + "\n" + ROW_2})
        block, err = self.build()
        self.assertEqual(["DEF"], [e[1] for e in block["delivery"]["friction"]])
        self.assertIn(bad, err)

    def test_RQ_TRC_091_given_a_row_of_a_merge_then_it_is_left_out_and_named(self):
        self.repo.commit({LOG: HEADER})
        self.repo.git("checkout", "-q", "-b", "side")
        self.repo.commit({FEATURE: "1\n"})
        self.repo.git("checkout", "-q", "main")
        self.repo.commit({FEATURE.replace("feature", "other"): "1\n"})
        self.repo.merge("side", "merge side")
        self.repo.write(LOG, HEADER + ROW_1)
        self.repo.git("add", "-A")
        self.repo.git("-c", "user.name=Dan", "-c", "user.email=dan@example.com", "commit", "-q", "--amend", "--no-edit")
        block, err = self.build()
        self.assertEqual([], block["delivery"]["friction"])
        self.assertIn("2026-10-01", err)

    def test_RQ_TRC_091_given_no_log_then_no_entry_and_no_failure(self):
        self.repo.commit({FEATURE: "1\n"})
        block, err = self.build()
        self.assertEqual([], block["delivery"]["friction"])
        self.assertEqual("", err)


if __name__ == "__main__":
    unittest.main()
