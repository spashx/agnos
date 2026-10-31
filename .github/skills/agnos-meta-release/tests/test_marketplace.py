"""Tests of the marketplace the release writes (RQ-PLG-001, RQ-PLG-002, RQ-PLG-003, RQ-PLG-007, TASK-PLG-005; ADR-PLG-001: DEC-PLG-001, DEC-PLG-002).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-meta-release/tests -v
"""
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scripts"))
import release  # noqa: E402
from test_select import CHANGELOG_FILE, INSTRUCTIONS_FILE, EXIT_FAILED, EXIT_OK, RehearsalCase, files_under  # noqa: E402

PLUGIN = "plugins/agnos"
SKILLS = f"{PLUGIN}/skills"
PROCESS_SKILL = f"{SKILLS}/agnos-process/SKILL.md"
CATALOGUES = (".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json")
MANIFESTS = (f"{PLUGIN}/plugin.json", f"{PLUGIN}/.claude-plugin/plugin.json")
ATTRIBUTES = ".gitattributes"
AGENT_PLUGINS_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
WORKSHOP_ROOTS = (".github/", ".claude/", "CLAUDE.md", "AGENTS.md", "CONTRIBUTING.md", "SECURITY.md", "CODE_OF_CONDUCT.md")
SAME_IN_MANIFESTS = ("name", "version", "description")


class MarketplaceCase(RehearsalCase):
    def built(self):
        code, errors = self.rehearse()
        self.assertEqual(EXIT_OK, code, errors)
        return files_under(self.output)

    def json_of(self, name):
        return json.loads((self.output / name).read_text(encoding="utf-8"))


class TreeTest(MarketplaceCase):
    """RQ-PLG-001, DEC-PLG-001."""

    def test_RQ_PLG_001_given_a_commit_when_it_runs_then_a_skill_lands_in_the_plugin(self):
        self.assertIn(f"{SKILLS}/agnos-index/SKILL.md", self.built())

    def test_RQ_PLG_001_given_workshop_files_when_it_runs_then_none_is_in_the_output(self):
        self.commit({"CLAUDE.md": "c\n", "AGENTS.md": "a\n", ".claude/skills/agnos-index/SKILL.md": "p\n", "CONTRIBUTING.md": "c\n"})
        for name in self.built():
            self.assertFalse(name.startswith(WORKSHOP_ROOTS), name)

    def test_RQ_PLG_001_given_the_repositorys_attributes_when_it_runs_then_the_output_has_its_own_for_the_plugins_paths(self):
        self.commit({ATTRIBUTES: "# RQ-ABC-001\n.github/skills/x/*.sh text eol=lf\n"})
        self.assertIn(ATTRIBUTES, self.built())
        text = (self.output / ATTRIBUTES).read_text(encoding="utf-8")
        self.assertNotIn(".github", text)
        self.assertIn("*.sh text eol=lf", text)


class CatalogueTest(MarketplaceCase):
    """RQ-PLG-002."""

    def test_RQ_PLG_002_given_the_output_then_both_catalogues_declare_the_plugin_where_it_is(self):
        self.built()
        claude, codex = (self.json_of(name) for name in CATALOGUES)
        self.assertEqual(f"./{PLUGIN}", claude["plugins"][0]["source"])
        self.assertEqual({"source": "local", "path": f"./{PLUGIN}"}, codex["plugins"][0]["source"])
        self.assertEqual(claude["name"], codex["name"])
        self.assertEqual({"installation", "authentication"}, set(codex["plugins"][0]["policy"]))
        self.assertTrue(codex["plugins"][0]["category"])

    def test_RQ_PLG_002_given_the_output_then_the_manifests_agree_and_only_the_root_one_has_the_schema(self):
        self.built()
        root, claude = (self.json_of(name) for name in MANIFESTS)
        for key in SAME_IN_MANIFESTS:
            self.assertEqual(root[key], claude[key], key)
        self.assertEqual(AGENT_PLUGINS_SCHEMA, root["$schema"])
        self.assertNotIn("$schema", claude)

    def test_RQ_PLG_002_given_the_changelog_then_the_version_is_its_latest_release(self):
        self.built()
        for name in MANIFESTS:
            self.assertEqual("1.2.0", self.json_of(name)["version"], name)
        self.assertEqual("1.2.0", self.json_of(CATALOGUES[0])["plugins"][0]["version"])

    def test_RQ_PLG_002_given_a_changelog_with_no_release_when_it_runs_then_it_stops_and_says_so(self):
        self.commit({CHANGELOG_FILE: "## [Unreleased]\n"})
        code, errors = self.rehearse()
        self.assertEqual(EXIT_FAILED, code)
        self.assertIn(CHANGELOG_FILE, errors)
        self.assertFalse(self.output.exists())


class ProcessSkillTest(MarketplaceCase):
    """RQ-PLG-003, DEC-PLG-002."""

    def test_RQ_PLG_003_given_the_instructions_then_the_skill_holds_them_without_ids_under_a_name_and_a_description(self):
        self.commit({INSTRUCTIONS_FILE: "# Process <!-- RQ-ABC-001 -->\nThe rules.\n"})
        self.built()
        text = (self.output / PROCESS_SKILL).read_text(encoding="utf-8")
        self.assertRegex(text, r'\A---\nname: agnos-process\ndescription: ".+"\n---\n')
        self.assertIn("The rules.\n", text)
        self.assertNotIn("RQ-ABC-001", text)

    def test_RQ_PLG_003_given_instructions_with_their_own_header_then_the_skill_has_only_its_own(self):
        self.commit({INSTRUCTIONS_FILE: '---\r\napplyTo: "**"\r\n---\r\n\r\n# Process\r\n'})
        self.built()
        text = (self.output / PROCESS_SKILL).read_bytes().decode("utf-8")
        self.assertNotIn("applyTo", text)
        self.assertEqual(2, text.count("---"))
        self.assertTrue(text.endswith("\n\n# Process\r\n"))

    def test_RQ_PLG_003_given_no_instructions_when_it_runs_then_it_stops_and_names_them(self):
        (self.repo / INSTRUCTIONS_FILE).unlink()
        self.commit({})
        code, errors = self.rehearse()
        self.assertEqual(EXIT_FAILED, code)
        self.assertIn(INSTRUCTIONS_FILE, errors)
        self.assertFalse(self.output.exists())


class UserDocumentsTest(MarketplaceCase):
    """RQ-PLG-008: the README and the guide point to where the files are in the marketplace."""

    def test_RQ_PLG_008_given_a_document_with_workshop_links_when_it_runs_then_they_lead_into_the_plugin(self):
        links = "[a](.github/instructions/agnos-sw-eng.instructions.md) [b](.github/skills/agnos-index/SKILL.md)\n"
        self.commit({"README.md": links, "GETTING_STARTED.MD": links, CHANGELOG_FILE: f"## [v1.2]\n{links}"})
        self.built()
        expected = f"[a]({PROCESS_SKILL}) [b]({SKILLS}/agnos-index/SKILL.md)\n"
        for name in ("README.md", "GETTING_STARTED.MD"):
            self.assertEqual(expected, (self.output / name).read_text(encoding="utf-8"), name)
        self.assertIn(links, (self.output / CHANGELOG_FILE).read_text(encoding="utf-8"))


class AgentTest(MarketplaceCase):
    """RQ-PLG-006, DEC-PLG-005."""

    NAME = "agnos-helper"
    SOURCE = f".github/agents/{NAME}.agent.md"
    CLAUDE = f"{PLUGIN}/agents/{NAME}.md"
    COPILOT = f"{PLUGIN}/com.github.copilot/agents/{NAME}.agent.md"
    BODY = "Do the work.\n"

    def definition(self, tools="read, search, edit, execute", model="haiku"):
        return f"---\nname: {self.NAME}\ndescription: A helper.\ntools: {tools}\nmodel: {model}\n---\n\n{self.BODY}"

    def test_RQ_PLG_006_given_a_definition_when_it_runs_then_each_tool_gets_its_own_values_and_the_same_body(self):
        self.commit({self.SOURCE: self.definition()})
        files = self.built()
        self.assertNotIn(self.SOURCE, files)
        claude = (self.output / self.CLAUDE).read_text(encoding="utf-8")
        copilot = (self.output / self.COPILOT).read_text(encoding="utf-8")
        self.assertIn(f"name: {self.NAME}\n", claude)
        self.assertIn("description: A helper.\n", claude)
        self.assertIn("tools: Read, Grep, Glob, Edit, Bash\n", claude)
        self.assertIn("model: haiku\n", claude)
        self.assertIn(f"name: {self.NAME}\n", copilot)
        self.assertIn("tools: read, search, edit, execute\n", copilot)
        self.assertNotIn("model:", copilot)
        self.assertTrue(claude.endswith(f"---\n\n{self.BODY}"))
        self.assertTrue(copilot.endswith(f"---\n\n{self.BODY}"))

    def test_RQ_PLG_006_given_a_tool_or_model_missing_from_the_table_when_it_runs_then_it_stops_and_names_it(self):
        for definition, named in ((self.definition(tools="read, teleport"), "teleport"), (self.definition(model="opus"), "opus")):
            self.commit({self.SOURCE: definition})
            code, errors = self.rehearse()
            self.assertEqual(EXIT_FAILED, code)
            self.assertIn(named, errors)
            self.assertIn(self.SOURCE, errors)
            self.assertFalse(self.output.exists())

    def test_RQ_PLG_006_given_a_definition_with_an_id_when_it_runs_then_neither_file_holds_it(self):
        self.commit({self.SOURCE: self.definition() + "<!-- RQ-ABC-001 -->\n"})
        self.built()
        for name in (self.CLAUDE, self.COPILOT):
            self.assertNotIn("RQ-ABC-001", (self.output / name).read_text(encoding="utf-8"))

    def test_RQ_PLG_006_given_a_meta_agent_when_it_runs_then_it_is_not_delivered(self):
        self.commit({".github/agents/agnos-meta-x.agent.md": self.definition()})
        self.assertEqual([], [name for name in self.built() if "agnos-meta-x" in name])


class PlaceTest(unittest.TestCase):
    """RQ-PLG-001."""

    def test_RQ_PLG_001_given_a_delivered_path_then_it_has_one_place(self):
        self.assertEqual(f"{SKILLS}/a/b.py", release.place_of(".github/skills/a/b.py"))
        self.assertEqual("README.md", release.place_of("README.md"))
        self.assertEqual(PROCESS_SKILL, release.place_of(INSTRUCTIONS_FILE))


if __name__ == "__main__":
    unittest.main()
