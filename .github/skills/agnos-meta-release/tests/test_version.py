"""Tests of the version read from `VERSION.txt` and of the line on unreleased entries (RQ-PLG-031, RQ-PLG-032, TASK-PLG-035;
ADR-PLG-005: DEC-PLG-024, DEC-PLG-025).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-meta-release/tests -v
"""
import contextlib
import io
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))
import release  # noqa: E402
from test_select import (CHANGELOG_FILE, EXIT_FAILED, EXIT_OK, REPORT_SUFFIX, VERSION_FILE, RehearsalCase,  # noqa: E402
                         no_proof)

MANIFESTS = ("plugins/agnos/plugin.json", "plugins/agnos/.claude-plugin/plugin.json")
CATALOGUES = (".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json")
DELIVERED_VERSION = "plugins/agnos/skills/agnos-init/assets/templates/VERSION.txt"
PAGE_SUFFIX = ".report.html"
UNRELEASED_KEY = "unreleasedEntries"
RELEASED = "## [v1.2]\n- released\n"
THREE_ENTRIES = f"## [Unreleased]\n### Added\n- one\n- two\n### Fixed\n- three\n\n{RELEASED}"


class VersionCase(RehearsalCase):
    def rehearse_out(self):
        """The exit code, the normal output and the error stream of a rehearsal."""
        out, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(errors):
            code = release.main(["--repo", str(self.repo), "--dry-run", "--output", str(self.output)], proof=no_proof)
        return code, out.getvalue(), errors.getvalue()

    def json_of(self, name):
        return json.loads((self.output / name).read_text(encoding="utf-8"))

    def report(self):
        return json.loads(Path(f"{self.output}{REPORT_SUFFIX}").read_text(encoding="utf-8"))


class FromTheVersionFileTest(VersionCase):
    """RQ-PLG-032: the manifests' version comes from `VERSION.txt`, in SemVer 2.0.0."""

    def test_RQ_PLG_032_given_version_3_2_0_when_rehearsed_then_the_four_manifests_and_the_delivered_file_hold_it(self):
        self.commit({VERSION_FILE: "3.2.0\n"})
        self.assertEqual(EXIT_OK, self.rehearse()[0])
        for name in MANIFESTS:
            self.assertEqual("3.2.0", self.json_of(name)["version"], name)
        for name in CATALOGUES:
            self.assertEqual("3.2.0", self.json_of(name)["plugins"][0]["version"], name)
        self.assertEqual("3.2.0\n", (self.output / DELIVERED_VERSION).read_text(encoding="utf-8"))

    def test_RQ_PLG_032_given_a_pre_release_with_build_metadata_then_it_is_delivered_as_written(self):
        self.commit({VERSION_FILE: "4.0.0-rc.1+build.5\n"})
        self.assertEqual(EXIT_OK, self.rehearse()[0])
        self.assertEqual("4.0.0-rc.1+build.5", self.json_of(MANIFESTS[0])["version"])

    def test_RQ_PLG_032_given_no_version_file_then_it_exits_1_names_the_file_and_writes_nothing(self):
        (self.repo / VERSION_FILE).unlink()
        self.commit({})
        code, errors = self.rehearse()
        self.assertEqual(EXIT_FAILED, code)
        self.assertIn(VERSION_FILE, errors)
        self.assertFalse(self.output.exists())

    def test_RQ_PLG_032_given_v3_2_in_the_version_file_then_it_exits_1_names_the_file_and_writes_nothing(self):
        self.commit({VERSION_FILE: "v3.2\n"})
        code, errors = self.rehearse()
        self.assertEqual(EXIT_FAILED, code)
        self.assertIn(VERSION_FILE, errors)
        self.assertFalse(self.output.exists())

    def test_RQ_PLG_032_given_a_leading_zero_then_it_is_not_semver_and_refused(self):
        self.commit({VERSION_FILE: "3.02.0\n"})
        self.assertEqual(EXIT_FAILED, self.rehearse()[0])

    def test_RQ_PLG_032_given_the_changelogs_latest_release_v1_2_then_it_is_left_as_it_is(self):
        self.commit({VERSION_FILE: "3.2.0\n", CHANGELOG_FILE: RELEASED})
        self.assertEqual(EXIT_OK, self.rehearse()[0])
        self.assertEqual(RELEASED, (self.output / CHANGELOG_FILE).read_text(encoding="utf-8"))

    def test_RQ_PLG_032_given_a_changelog_with_no_release_then_the_version_file_still_gives_the_version(self):
        self.commit({CHANGELOG_FILE: "## [Unreleased]\n"})
        self.assertEqual(EXIT_OK, self.rehearse()[0])
        self.assertEqual("1.2.0", self.json_of(MANIFESTS[0])["version"])


class UnreleasedTest(VersionCase):
    """RQ-PLG-031: the entries under `[Unreleased]` are said and recorded, failing nothing."""

    def test_RQ_PLG_031_given_3_unreleased_bullets_then_the_line_says_3_entries_and_the_exit_code_is_unchanged(self):
        self.commit({CHANGELOG_FILE: THREE_ENTRIES})
        code, out, _ = self.rehearse_out()
        self.assertEqual(EXIT_OK, code)
        self.assertIn("unreleased: 3 entries, version 1.2.0 delivered", out.splitlines())
        self.assertEqual(3, self.report()[UNRELEASED_KEY])

    def test_RQ_PLG_031_given_no_unreleased_entry_then_no_such_line_is_printed(self):
        self.commit({CHANGELOG_FILE: f"## [Unreleased]\n\n{RELEASED}"})
        code, out, _ = self.rehearse_out()
        self.assertEqual(EXIT_OK, code)
        self.assertNotIn("unreleased:", out)
        self.assertEqual(0, self.report()[UNRELEASED_KEY])

    def test_RQ_PLG_031_given_bullets_of_released_sections_only_then_none_is_counted(self):
        self.commit({CHANGELOG_FILE: RELEASED})
        self.assertEqual(EXIT_OK, self.rehearse()[0])
        self.assertEqual(0, self.report()[UNRELEASED_KEY])

    def test_RQ_PLG_031_given_unreleased_entries_then_the_page_shows_their_count(self):
        self.commit({CHANGELOG_FILE: THREE_ENTRIES})
        self.assertEqual(EXIT_OK, self.rehearse()[0])
        page = Path(f"{self.output}{PAGE_SUFFIX}").read_text(encoding="utf-8")
        self.assertIn(f"REPORT.{UNRELEASED_KEY}", page)
        self.assertEqual(3, self.report()[UNRELEASED_KEY])


if __name__ == "__main__":
    unittest.main()
