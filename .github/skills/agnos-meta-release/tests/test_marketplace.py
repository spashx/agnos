"""Tests of the marketplace the release writes (RQ-PLG-001, RQ-PLG-002, RQ-PLG-003, RQ-PLG-007, TASK-PLG-005; ADR-PLG-001: DEC-PLG-001, DEC-PLG-002).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-meta-release/tests -v
"""
import json
import re
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
PROCESS_SKILL = f"{SKILLS}/agnos-instructions/SKILL.md"     # RQ-PLG-035 / DEC-PLG-030
OLD_PROCESS_SKILL = f"{SKILLS}/agnos-process"
CATALOGUES = (".claude-plugin/marketplace.json",)     # RQ-PLG-043 / DEC-PLG-033: no Codex catalogue
WITHDRAWN_CATALOGUE = ".agents/plugins/marketplace.json"
MANIFESTS = (f"{PLUGIN}/plugin.json", f"{PLUGIN}/.claude-plugin/plugin.json")
ATTRIBUTES = ".gitattributes"
AGENT_PLUGINS_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
WORKSHOP_ROOTS = (".github/", ".claude/", "CLAUDE.md", "AGENTS.md", "CONTRIBUTING.md", "SECURITY.md", "CODE_OF_CONDUCT.md")
SAME_IN_MANIFESTS = ("name", "version", "description")
GUIDE = "AGNOS-GETTING-STARTED.md"          # RQ-PLG-022
FORMER_GUIDE = "GETTING_STARTED.MD"
ROOT = HERE.parents[3]
COMPATIBILITY = "COMPATIBILITY.md"           # RQ-PLG-023
README_SECTIONS = ["What AGNOS Provides", "Requirements", "Getting Started", "License"]
REQUIREMENTS_NAMED = ("git", "PowerShell 5.1", "bash", "Python 3.9", "requirements-callgraph.txt", "not fetched",
                      "chat.useAgentsMdFile", "chat.useAgentSkills")     # TASK-PLG-049: the VS Code settings AGNOS relies on
MOVED_SECTIONS = ("What was tested", "How a Session Runs", "Core Concepts", "Continuous Improvement", "Repository Map")


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

    def test_RQ_PLG_002_given_the_output_then_the_catalogue_declares_the_plugin_where_it_is(self):
        self.built()
        self.assertEqual(f"./{PLUGIN}", self.json_of(CATALOGUES[0])["plugins"][0]["source"])

    def test_RQ_PLG_043_given_the_output_then_no_codex_catalogue_and_no_codex_value(self):
        """RQ-PLG-043 / DEC-PLG-033."""
        names = self.built()
        self.assertNotIn(WITHDRAWN_CATALOGUE, names)
        for name in (*CATALOGUES, *MANIFESTS):
            self.assertNotIn("codex", (self.output / name).read_text(encoding="utf-8").lower(), name)

    def test_RQ_PLG_002_given_the_output_then_the_manifests_agree_and_only_the_root_one_has_the_schema(self):
        self.built()
        root, claude = (self.json_of(name) for name in MANIFESTS)
        for key in SAME_IN_MANIFESTS:
            self.assertEqual(root[key], claude[key], key)
        self.assertEqual(AGENT_PLUGINS_SCHEMA, root["$schema"])
        self.assertNotIn("$schema", claude)

    def test_RQ_PLG_032_given_the_version_file_then_the_version_is_the_one_it_holds(self):
        """RQ-PLG-032 replaces the changelog's latest release as the version's source (DEC-PLG-025)."""
        self.built()
        for name in MANIFESTS:
            self.assertEqual("1.2.0", self.json_of(name)["version"], name)
        self.assertEqual("1.2.0", self.json_of(CATALOGUES[0])["plugins"][0]["version"])


class ProcessSkillTest(MarketplaceCase):
    """RQ-PLG-003, DEC-PLG-002."""

    def test_RQ_PLG_003_given_the_instructions_then_the_skill_holds_them_without_ids_under_a_name_and_a_description(self):
        self.commit({INSTRUCTIONS_FILE: "# Process <!-- RQ-ABC-001 -->\nThe rules.\n"})
        self.built()
        text = (self.output / PROCESS_SKILL).read_text(encoding="utf-8")
        self.assertRegex(text, r'\A---\nname: agnos-instructions\ndescription: ".+"\n---\n')
        self.assertFalse((self.output / OLD_PROCESS_SKILL).exists())     # RQ-PLG-035: no skill named agnos-process
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
    """RQ-PLG-008: the README points to where the files are in the marketplace; RQ-PLG-022: the guide is the init's template."""

    def test_RQ_PLG_008_given_a_document_with_workshop_links_when_it_runs_then_they_lead_into_the_plugin(self):
        links = "[a](.github/instructions/agnos-sw-eng.instructions.md) [b](.github/skills/agnos-index/SKILL.md)\n"
        self.commit({"README.md": links, CHANGELOG_FILE: f"## [v1.2]\n{links}"})
        self.built()
        expected = f"[a]({PROCESS_SKILL}) [b]({SKILLS}/agnos-index/SKILL.md)\n"
        self.assertEqual(expected, (self.output / "README.md").read_text(encoding="utf-8"))
        self.assertIn(links, (self.output / CHANGELOG_FILE).read_text(encoding="utf-8"))

    def test_RQ_PLG_022_given_the_readme_then_it_sends_the_user_to_the_guide_agnos_init_writes(self):
        text = (HERE.parents[3] / "README.md").read_text(encoding="utf-8")
        self.assertIn(GUIDE, text)
        self.assertNotIn(FORMER_GUIDE, text)


class WhatWasTestedTest(unittest.TestCase):
    """RQ-PLG-008, amended by RQ-PLG-023: what was tested is stated in COMPATIBILITY.md."""

    def test_RQ_PLG_008_given_compatibility_then_it_says_macos_and_codex_are_not_tested(self):
        text = (ROOT / COMPATIBILITY).read_text(encoding="utf-8")
        for row in ("| macOS | Not tested", "| OpenAI Codex | Not tested"):
            self.assertIn(row, text)


class ReadmeTest(unittest.TestCase):
    """RQ-PLG-023, DEC-PLG-018: one reader per document."""

    def setUp(self):
        self.text = (ROOT / "README.md").read_text(encoding="utf-8")

    def test_RQ_PLG_023_given_the_readme_then_its_sections_are_provides_getting_started_and_license_in_order(self):
        self.assertEqual(README_SECTIONS, re.findall(r"^## (.+?)\s*$", self.text, re.M))

    def test_RQ_PLG_023_given_the_readme_then_its_requirements_name_each_platform_need_and_what_the_user_installs(self):
        requirements = self.text.split("## Requirements", 1)[1].split("\n## ", 1)[0]
        for need in REQUIREMENTS_NAMED:
            self.assertIn(need, requirements, need)

    def test_RQ_PLG_023_given_the_readme_then_it_names_compatibility_and_says_nothing_of_what_was_tested(self):
        self.assertIn(COMPATIBILITY, self.text)
        self.assertNotIn("tested", self.text.lower())
        for moved in MOVED_SECTIONS:
            self.assertNotIn(moved.lower(), self.text.lower(), moved)

    def test_RQ_PLG_023_given_contributing_then_it_holds_the_repository_map(self):
        self.assertIn("## Repository Map", (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8"))



class CompatibilityDeliveredTest(MarketplaceCase):
    """RQ-PLG-023."""

    def test_RQ_PLG_023_given_a_commit_with_compatibility_when_it_runs_then_the_marketplace_holds_it(self):
        self.commit({COMPATIBILITY: "| macOS | Not tested |\n"})
        self.assertIn(COMPATIBILITY, self.built())


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
