"""Tests that the release checks the manifests by itself, whatever the tool (RQ-PLG-015, TASK-PLG-014; ADR-PLG-002: DEC-PLG-010;
RQ-PLG-044, RQ-PLG-045, TASK-PLG-072; ADR-PLG-009: DEC-PLG-035).

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
PLUGIN_README_TEXT = b"# Plugin\n"
WORKSHOP = HERE.parents[3]
WORKSHOP_SKILLS = WORKSHOP / ".github" / "skills"
PROCESS_SKILL_LINK = "skills/agnos-instructions/SKILL.md"     # RQ-PLG-035: generated from the instructions file
OWNER_EMAIL = "25369377+spashx@users.noreply.github.com"     # RQ-PLG-044: GitHub's private address of the owner
LISTING_FIELDS = ("author", "homepage", "repository", "keywords")     # RQ-PLG-045
CATEGORY = "software development"


class ManifestCase(unittest.TestCase):
    def setUp(self):
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.output = Path(holder.name)
        release.write_marketplace(self.output, VERSION, PLUGIN_README_TEXT)

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


class ListingTest(ManifestCase):
    """RQ-PLG-044, RQ-PLG-045 / DEC-PLG-035: the listing fields, from the marketplace asset."""

    def setUp(self):
        super().setUp()
        self.asset = json.loads(release.MARKETPLACE_PATH.read_text(encoding="utf-8"))
        self.catalogue = json.loads((self.output / release.CLAUDE_CATALOGUE).read_text(encoding="utf-8"))

    def test_RQ_PLG_044_given_the_written_catalogue_then_its_metadata_holds_description_and_version_and_the_owner_an_email(self):
        self.assertEqual(VERSION, self.catalogue["metadata"]["version"])
        self.assertEqual(self.asset["marketplace"]["metadata"]["description"], self.catalogue["metadata"]["description"])
        self.assertEqual(OWNER_EMAIL, self.catalogue["owner"]["email"])
        self.assertNotIn("description", self.catalogue)

    def test_RQ_PLG_045_given_the_written_files_then_manifests_and_entry_hold_the_listing_fields_of_the_asset(self):
        entry = self.catalogue["plugins"][0]
        manifests = [json.loads((self.output / name).read_text(encoding="utf-8")) for name in (release.ROOT_MANIFEST, release.CLAUDE_MANIFEST)]
        for data in (entry, *manifests):
            for key in LISTING_FIELDS:
                self.assertEqual(self.asset["plugin"][key], data[key], key)
        self.assertEqual(self.asset["plugin"]["license"], entry["license"])
        self.assertEqual(CATEGORY, entry["category"])
        for data in manifests:
            self.assertNotIn("category", data)


class PluginReadmeTest(ManifestCase):
    """RQ-PLG-042 / DEC-PLG-034: the plugin's README, its links checked from the plugin's folder."""

    def write_readme(self, text):
        (self.output / release.PLUGIN_README).write_text(text, encoding="utf-8")

    def test_RQ_PLG_042_given_the_written_marketplace_then_the_plugin_folder_holds_a_readme(self):
        self.assertTrue((self.output / release.PLUGIN_README).is_file())

    def test_RQ_PLG_042_given_a_readme_link_to_an_absent_file_then_the_link_is_named(self):
        self.write_readme("[a](skills/absent/SKILL.md) [b](https://example.org) [c](#top)\n")
        problems = release.readme_problems(self.output)
        self.assertEqual(1, len(problems), problems)
        self.assertIn("skills/absent/SKILL.md", problems[0])

    def test_RQ_PLG_042_given_a_readme_link_to_a_plugin_file_then_no_problem(self):
        (self.output / release.PLUGIN_FOLDER / "skills" / "x").mkdir(parents=True)
        (self.output / release.PLUGIN_FOLDER / "skills" / "x" / "SKILL.md").write_text("x\n", encoding="utf-8")
        self.write_readme("[x](skills/x/SKILL.md)\n")
        self.assertEqual([], release.readme_problems(self.output))

    def test_RQ_PLG_042_given_a_readme_link_leaving_the_plugin_then_the_link_is_named(self):
        self.write_readme("[r](../../README.md)\n")
        self.assertEqual(1, len(release.readme_problems(self.output)))

    def test_RQ_PLG_042_given_the_workshops_plugin_readme_then_each_link_leads_to_a_delivered_file(self):
        """The asset itself, against this repository's skills: a renamed or removed skill fails here."""
        text = (WORKSHOP / release.PLUGIN_README_SOURCE).read_text(encoding="utf-8")
        links = [link for link in release.LINK_RE.findall(text) if not release.EXTERNAL_LINK_RE.match(link)]
        self.assertTrue(links)
        for link in links:
            source = WORKSHOP / release.INSTRUCTIONS if link == PROCESS_SKILL_LINK else WORKSHOP_SKILLS / link.removeprefix("skills/")
            self.assertTrue(source.is_file(), link)


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

    def test_RQ_PLG_044_given_a_catalogue_metadata_version_that_differs_then_the_catalogue_is_named(self):
        self.edit(release.CLAUDE_CATALOGUE, lambda data: data["metadata"].update(version="0.0.1"))
        self.assertNamed(release.CLAUDE_CATALOGUE)

    def test_RQ_PLG_044_given_a_catalogue_description_at_its_root_then_the_catalogue_is_named(self):
        self.edit(release.CLAUDE_CATALOGUE, lambda data: data.update(description="root"))
        self.assertNamed(release.CLAUDE_CATALOGUE)

    def test_RQ_PLG_045_given_a_manifest_without_homepage_then_the_file_is_named(self):
        self.edit(release.ROOT_MANIFEST, lambda data: data.pop("homepage"))
        self.assertNamed(release.ROOT_MANIFEST)

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
