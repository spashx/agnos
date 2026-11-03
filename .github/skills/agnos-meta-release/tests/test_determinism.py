"""Tests that the same commit gives the same output (RQ-PLG-013, TASK-PLG-012; ADR-PLG-002: DEC-PLG-008).

Each rehearsal runs in its own process with its own hash seed, so that an unsorted set or dict reaching the output shows.
Run from the repository root: python -m unittest discover -s .github/skills/agnos-meta-release/tests -v
"""
import filecmp
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))
import release  # noqa: E402
from test_select import EXIT_OK, RehearsalCase, files_under  # noqa: E402

ROOT = HERE.parents[3]
DEMO = ROOT.parent / release.DEMO_FOLDER_NAME
SCRIPT = HERE.parent / "scripts" / "release.py"
SEEDS = ("1", "2")      # two orders of the same sets


def report_bytes(output):
    return Path(f"{output}{release.REPORT_SUFFIX}").read_bytes()


def rehearse_in_a_process(repo, output, seed, *extra):
    env = {**os.environ, "PYTHONHASHSEED": seed, **release.NO_BYTECODE}
    return subprocess.run([sys.executable, str(SCRIPT), "--repo", str(repo), "--dry-run", "--output", str(output), *extra],
                          capture_output=True, env=env).returncode


class SameOutputCase(unittest.TestCase):
    def assertSameRehearsals(self, repo, base, *extra):
        outputs = [base / f"out{seed}" for seed in SEEDS]
        for seed, output in zip(SEEDS, outputs):
            self.assertEqual(EXIT_OK, rehearse_in_a_process(repo, output, seed, *extra))
        first, second = outputs
        names = files_under(first)
        self.assertEqual(names, files_under(second))
        self.assertEqual([], filecmp.cmpfiles(first, second, names, shallow=False)[1])
        self.assertEqual(report_bytes(first), report_bytes(second))


class SmallRepositoryTest(RehearsalCase, SameOutputCase):
    """RQ-PLG-013, on a repository built by the test, with an absent demo: the proof is not what is compared here."""

    def test_RQ_PLG_013_given_one_commit_rehearsed_in_two_processes_with_two_hash_seeds_then_the_trees_and_reports_are_identical(self):
        holder = self.base / "seeds"
        holder.mkdir()
        absent_demo = self.base / "absent"     # the proof then fails alike in both, and writes its report
        outputs = [holder / f"out{seed}" for seed in SEEDS]
        codes = [rehearse_in_a_process(self.repo, output, seed, "--demo", str(absent_demo)) for seed, output in zip(SEEDS, outputs)]
        self.assertEqual(codes[0], codes[1])
        first, second = outputs
        names = files_under(first)
        self.assertEqual(names, files_under(second))
        self.assertEqual([], filecmp.cmpfiles(first, second, names, shallow=False)[1])
        self.assertEqual(report_bytes(first), report_bytes(second))


@unittest.skipUnless(DEMO.is_dir(), "the demo is not built")
class ThisRepositoryTest(SameOutputCase):
    """RQ-PLG-013, on this repository's HEAD with the proof on the demo."""

    def test_RQ_PLG_013_given_head_rehearsed_in_two_processes_with_two_hash_seeds_then_the_trees_and_reports_are_identical(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as holder:
            self.assertSameRehearsals(ROOT, Path(holder))


if __name__ == "__main__":
    unittest.main()
