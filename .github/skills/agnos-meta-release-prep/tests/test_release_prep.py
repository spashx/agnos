"""Tests of the release preparation's deterministic steps: check, review, set-version (RQ-PLG-027, RQ-PLG-028, RQ-PLG-029,
RQ-PLG-032, TASK-PLG-033; ADR-PLG-005: DEC-PLG-022, DEC-PLG-023, DEC-PLG-025).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-meta-release-prep/tests -v
"""
import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import release_prep  # noqa: E402

EXIT_OK = 0
EXIT_FAILED = 1
VERSION_FILE = ".github/skills/agnos-init/assets/templates/VERSION"
CHANGELOG = "CHANGELOG.md"
README = "README.md"
GUIDE = ".github/skills/agnos-init/assets/templates/AGNOS-GETTING-STARTED.md"
INDEX = "agnos-process/process.idx.md"
PLAN_A = "agnos-process/3.plan/PLAN-ABC-001-a.md"
PLAN_B = "agnos-process/3.plan/PLAN-ABC-002-b.md"
RELEASED = "## [v3.1]\n- released\n"
PLAN_TEXT = ("# PLAN-ABC-001: A\n\n### TASK-ABC-001: Done one\n- **Status**: Done\n\n"
             "### TASK-ABC-002: Going\n- **Status**: In Progress\n\n### TASK-ABC-003: Waiting\n- **Status**: Not Started\n\n"
             "### TASK-ABC-004: Stuck\n- **Status**: Blocked\n")


def changelog(*sections):
    """A changelog whose [Unreleased] holds these `### <name>` sections, one bullet each, above a released one."""
    body = "".join(f"### {name}\n- an entry\n" for name in sections)
    return f"# Changelog\n\n## [Unreleased]\n{body}\n{RELEASED}"


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.org",
                           "-c", "core.autocrlf=false", *args], capture_output=True, text=True, check=True).stdout


class PrepCase(unittest.TestCase):
    def setUp(self):
        holder = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(holder.cleanup)
        self.repo = Path(holder.name)
        git(self.repo, "init", "-q")
        self.commit({VERSION_FILE: "3.1.0\n", CHANGELOG: changelog("Added"), README: "# Readme\n", PLAN_A: PLAN_TEXT})
        self.run_script("check")        # the index, built and committed, so that the tree is clean
        self.commit({})

    def commit(self, files):
        self.write(files)
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "--allow-empty", "-m", "commit")

    def write(self, files):
        for name, text in files.items():
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="")

    def read(self, name):
        return (self.repo / name).read_text(encoding="utf-8")

    def run_script(self, *args):
        """The exit code and everything printed, both streams together in order."""
        said = io.StringIO()
        with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
            code = release_prep.main([*args, "--repo", str(self.repo)])
        return code, said.getvalue()


class CheckTest(PrepCase):
    """RQ-PLG-027: the repository is checked before any edit."""

    def test_RQ_PLG_027_given_a_changed_tracked_file_when_the_check_runs_then_it_exits_1_names_it_and_edits_nothing(self):
        self.write({README: "# Changed\n"})
        index_before = self.read(INDEX)
        (self.repo / INDEX).unlink()
        code, said = self.run_script("check")
        self.assertEqual(EXIT_FAILED, code)
        self.assertIn(README, said)
        self.assertFalse((self.repo / INDEX).exists(), "the index was written although the check stopped")
        self.assertTrue(index_before)

    def test_RQ_PLG_027_given_a_duplicate_id_when_the_check_runs_then_it_exits_1_and_names_it(self):
        self.commit({PLAN_B: "# PLAN-ABC-002: B\n\n### TASK-ABC-002: Twice\n- **Status**: Done\n"})
        code, said = self.run_script("check")
        self.assertEqual(EXIT_FAILED, code)
        self.assertIn("TASK-ABC-002", said)

    def test_RQ_PLG_027_given_a_clean_repository_then_it_exits_0_and_lists_each_open_task_with_its_status(self):
        code, said = self.run_script("check")
        self.assertEqual(EXIT_OK, code, said)
        for task, status in (("TASK-ABC-002", "In Progress"), ("TASK-ABC-003", "Not Started"), ("TASK-ABC-004", "Blocked")):
            self.assertTrue(any(task in line and status in line for line in said.splitlines()), said)
        self.assertNotIn("TASK-ABC-001", said)


class ProposalTest(unittest.TestCase):
    """RQ-PLG-028 / DEC-PLG-023: the version proposed from the [Unreleased] sections."""

    def test_RQ_PLG_028_given_3_1_0_and_added_and_changed_then_the_proposal_is_3_2_0(self):
        self.assertEqual("3.2.0", release_prep.proposed_version("3.1.0", release_prep.unreleased(changelog("Added", "Changed"))))

    def test_RQ_PLG_028_given_a_removed_section_then_the_proposal_is_4_0_0(self):
        self.assertEqual("4.0.0", release_prep.proposed_version("3.1.0", release_prep.unreleased(changelog("Added", "Removed"))))

    def test_RQ_PLG_028_given_fixed_only_then_the_proposal_is_3_1_1(self):
        self.assertEqual("3.1.1", release_prep.proposed_version("3.1.0", release_prep.unreleased(changelog("Fixed"))))

    def test_RQ_PLG_028_given_an_empty_unreleased_then_no_version_is_proposed(self):
        self.assertIsNone(release_prep.proposed_version("3.1.0", release_prep.unreleased(changelog())))


class ReviewTest(PrepCase):
    """RQ-PLG-028: what docs-sync changed, shown for review."""

    def test_RQ_PLG_028_given_the_synced_documents_then_the_review_shows_the_diff_unreleased_and_proposal(self):
        self.write({CHANGELOG: changelog("Added", "Changed"), GUIDE: "# Guide\n"})
        code, said = self.run_script("review")
        self.assertEqual(EXIT_OK, code, said)
        self.assertIn(CHANGELOG, said)
        self.assertIn(GUIDE, said)
        self.assertIn("+### Changed", said)
        self.assertIn("proposed: 3.2.0", said)
        self.assertNotIn("unexpected", said)

    def test_RQ_PLG_028_given_a_file_changed_outside_the_four_of_docs_sync_then_it_is_named_as_unexpected(self):
        self.write({README: "# Changed\n"})
        _, said = self.run_script("review")
        self.assertTrue(any("unexpected" in line and README in line for line in said.splitlines()), said)

    def test_RQ_PLG_028_given_an_empty_unreleased_then_the_review_says_there_is_nothing_to_release(self):
        self.write({CHANGELOG: changelog()})
        _, said = self.run_script("review")
        self.assertIn("nothing to release", said)
        self.assertNotIn("proposed: ", said)


class SetVersionTest(PrepCase):
    """RQ-PLG-029, RQ-PLG-032: the approved version written into VERSION and the changelog's heading, nothing else."""

    def test_RQ_PLG_029_given_3_2_0_approved_then_version_and_heading_hold_it_and_every_other_line_is_unchanged(self):
        before = self.read(CHANGELOG)
        code, said = self.run_script("set-version", "3.2.0")
        self.assertEqual(EXIT_OK, code, said)
        self.assertEqual("3.2.0\n", self.read(VERSION_FILE))
        self.assertEqual(before.replace("## [Unreleased]\n", "## [3.2.0]\n"), self.read(CHANGELOG))

    def test_RQ_PLG_029_given_a_version_that_is_not_semver_then_it_is_refused_and_neither_file_changes(self):
        self.assertRefused("v3.2")

    def test_RQ_PLG_029_given_a_version_not_above_the_current_one_then_it_is_refused(self):
        self.assertRefused("3.1.0")
        self.assertRefused("3.0.9")
        self.assertRefused("3.1.0-rc.1")      # a pre-release precedes its release

    def test_RQ_PLG_029_given_a_pre_release_above_the_current_version_then_it_is_accepted(self):
        self.assertEqual(EXIT_OK, self.run_script("set-version", "4.0.0-rc.1+build.5")[0])
        self.assertEqual("4.0.0-rc.1+build.5\n", self.read(VERSION_FILE))

    def test_RQ_PLG_029_given_a_changelog_without_unreleased_then_it_is_refused(self):
        self.commit({CHANGELOG: RELEASED})
        self.assertRefused("3.2.0")

    def assertRefused(self, version):
        files = (self.read(VERSION_FILE), self.read(CHANGELOG))
        code, said = self.run_script("set-version", version)
        self.assertEqual(EXIT_FAILED, code, said)
        self.assertEqual(files, (self.read(VERSION_FILE), self.read(CHANGELOG)))


class PrecedenceTest(unittest.TestCase):
    """DEC-PLG-023: SemVer 2.0.0 precedence, section 11 of the specification."""

    def test_DEC_PLG_023_given_the_specifications_example_then_each_version_precedes_the_next(self):
        ordered = ("1.0.0-alpha", "1.0.0-alpha.1", "1.0.0-alpha.beta", "1.0.0-beta", "1.0.0-beta.2", "1.0.0-beta.11",
                   "1.0.0-rc.1", "1.0.0", "2.0.0", "2.1.0", "2.1.1")
        for lower, higher in zip(ordered, ordered[1:]):
            self.assertTrue(release_prep.is_above(higher, lower), (higher, lower))
            self.assertFalse(release_prep.is_above(lower, higher), (lower, higher))

    def test_DEC_PLG_023_given_build_metadata_only_then_the_versions_have_the_same_precedence(self):
        self.assertFalse(release_prep.is_above("1.0.0+b2", "1.0.0+b1"))


if __name__ == "__main__":
    unittest.main()
