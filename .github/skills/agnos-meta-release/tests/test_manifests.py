"""Tests that the release checks the manifests by itself, whatever the tool (RQ-PLG-015, TASK-PLG-014; ADR-PLG-002: DEC-PLG-010).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-meta-release/tests -v
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))
import release  # noqa: E402
from test_select import EXIT_OK, REPORT_SUFFIX, RehearsalCase  # noqa: E402

SCRIPT = HERE.parent / "scripts" / "release.py"
VERSION = "1.2.0"
AI_TOOL_CALLS = ("plugin validate", "AGNOS_CLAUDE")


class ManifestCase(unittest.TestCase):
    def setUp(self):
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.output = Path(holder.name)
        release.write_marketplace(self.output, VERSION)

    def edit(self, name, change):
        path = self.output / name
        data = json.loads(path.read_text(encoding="utf-8"))
        change(data)
        path.write_text(json.dumps(data), encoding="utf-8")

    def assertNamed(self, name):
        problems = release.manifest_problems(self.output)
        self.assertTrue(any(name in problem for problem in problems), problems)


class ConsistentTest(ManifestCase):
    """RQ-PLG-015: what the release writes passes its own check."""

    def test_RQ_PLG_015_given_the_written_marketplace_then_no_manifest_problem_is_named(self):
        self.assertEqual([], release.manifest_problems(self.output))


class RefusedTest(ManifestCase):
    """RQ-PLG-015: each fault is named with its file."""

    def test_RQ_PLG_015_given_a_manifest_missing_its_version_then_the_file_is_named(self):
        self.edit(release.CLAUDE_MANIFEST, lambda data: data.pop("version"))
        self.assertNamed(release.CLAUDE_MANIFEST)

    def test_RQ_PLG_015_given_a_catalogue_naming_a_missing_plugin_folder_then_the_file_is_named(self):
        self.edit(release.CLAUDE_CATALOGUE, lambda data: data["plugins"][0].update(source="./plugins/absent"))
        self.assertNamed(release.CLAUDE_CATALOGUE)

    def test_RQ_PLG_015_given_a_description_that_differs_between_files_then_the_file_is_named(self):
        self.edit(release.ROOT_MANIFEST, lambda data: data.update(description="another"))
        self.assertNamed(release.ROOT_MANIFEST)

    def test_RQ_PLG_015_given_a_catalogue_with_no_owner_then_the_file_is_named(self):
        self.edit(release.CLAUDE_CATALOGUE, lambda data: data.pop("owner"))
        self.assertNamed(release.CLAUDE_CATALOGUE)

    def test_RQ_PLG_015_given_a_file_that_is_not_json_then_the_file_is_named(self):
        (self.output / release.ROOT_MANIFEST).write_text("{", encoding="utf-8")
        self.assertNamed(release.ROOT_MANIFEST)

    def test_RQ_PLG_015_given_a_missing_manifest_then_the_file_is_named(self):
        (self.output / release.CLAUDE_MANIFEST).unlink()
        self.assertNamed(release.CLAUDE_MANIFEST)


class InTheReportTest(RehearsalCase):
    """RQ-PLG-015: the check is in the report, and no AI tool is called."""

    def test_RQ_PLG_015_given_a_rehearsal_then_the_reports_checks_hold_manifests_true(self):
        self.assertEqual(EXIT_OK, self.rehearse()[0])
        report = json.loads(Path(f"{self.output}{REPORT_SUFFIX}").read_text(encoding="utf-8"))
        self.assertIs(True, report["checks"]["manifests"])

    def test_RQ_PLG_015_given_the_release_script_then_it_calls_no_ai_tool_so_the_verdict_is_the_same_without_claude(self):
        text = SCRIPT.read_text(encoding="utf-8")
        for call in AI_TOOL_CALLS:
            self.assertNotIn(call, text)


if __name__ == "__main__":
    unittest.main()
