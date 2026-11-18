"""Tests of the repository's addresses: assets/links.json declares each address once and the checked documents hold
none of them hard-coded (FTR-DOC-003: RQ-DOC-007; ADR-DOC-001: DEC-DOC-001).

The rules are small functions of this module, unit-tested on in-memory fixtures; the last tests apply them to the real
documents.

Run from the repository root: python -m unittest discover -s .github/skills/agnos-meta-docs-sync/tests -v
"""
import json
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ENCODING = "utf-8"
LINKS_FILE = ROOT / "assets" / "links.json"                                     # RQ-DOC-007 / DEC-DOC-001
MARKETPLACE_FILE = ROOT / ".github" / "skills" / "agnos-meta-release" / "assets" / "marketplace.json"
LINKS_KEY = "links"
PROCESS_LINK = "process"
HOMEPAGE, REPOSITORY = "homepage", "repository"
PLUGIN = "plugin"
DECLARED_NAMES = ("process", "marketplace", "getting-started", "guide", "website", "website-repository",
                  "perf-center", "demo-repository")
CHECKED_DOCUMENTS = (                                                           # RQ-DOC-007: paths from the root
    "README.md",
    "COMPATIBILITY.md",
    ".github/skills/agnos-init/assets/templates/AGNOS-GETTING-STARTED.md",
    ".github/skills/agnos-meta-demo/assets/content/README.md",
    ".github/skills/agnos-meta-demo/assets/content/drafts/README.web.md",
    ".github/skills/agnos-meta-release/assets/plugin-README.md",
)
# A Markdown reference definition: [name]: address (up to three spaces of indentation, an optional title is ignored).
REFERENCE_DEFINITION = re.compile(r"^ {0,3}\[([^\]]+)\]:[ \t]*(\S+).*$", re.M)
URL = re.compile(r"https?://[^\s<>\"'`)\]]+")
URL_TRAILING = ".,;:!?"
URL_BOUNDARY = "#/?"         # what may follow a declared address inside a longer URL


def definitions(text):
    """{name: address} of the reference definition lines of a text. RQ-DOC-007 / DEC-DOC-001"""
    return {match.group(1): match.group(2) for match in REFERENCE_DEFINITION.finditer(text)}


def wrong_definitions(document, text, links):
    """One message per reference definition named like a declared link whose address differs. RQ-DOC-007 /
    DEC-DOC-001"""
    return [f"{document}: [{name}] is {address}, declared {links[name]}"
            for name, address in definitions(text).items() if name in links and address != links[name]]


def starts_with_address(url, address):
    """True when url is address, or address followed by a path, fragment or query. RQ-DOC-007 / DEC-DOC-001"""
    return url == address or (url.startswith(address) and url[len(address)] in URL_BOUNDARY)


def hard_coded_addresses(document, text, links):
    """One message per URL outside a reference definition line that is, or starts with, a declared address (a URL
    longer than the address, such as address#section, is a hard-coded copy unless another declared name holds it,
    and that name is then the one to reference). RQ-DOC-007 / DEC-DOC-001"""
    body = REFERENCE_DEFINITION.sub("", text)
    found = []
    for match in URL.finditer(body):
        url = match.group(0).rstrip(URL_TRAILING)
        found += [f"{document}: {url} hard-codes [{name}] {address}"
                  for name, address in links.items() if starts_with_address(url, address)]
    return found


def marketplace_mismatches(manifest, links):
    """One message per plugin field that is not the process address. RQ-DOC-007 / DEC-DOC-001"""
    return [f"marketplace.json: {field} is {manifest[PLUGIN][field]}, expected {links[PROCESS_LINK]}"
            for field in (HOMEPAGE, REPOSITORY) if manifest[PLUGIN][field] != links[PROCESS_LINK]]


def load(path):
    """The JSON of a file. RQ-DOC-007"""
    return json.loads(Path(path).read_text(encoding=ENCODING))


FIXTURE_LINKS = {"market": "https://example.org/market", "start": "https://example.org/market#start",
                 "site": "https://example.org/site"}


class TestReferenceDefinitions(unittest.TestCase):
    """RQ-DOC-007 / DEC-DOC-001: rule a, a reference definition holds the declared address."""

    def test_given_a_definition_with_the_declared_address_then_there_is_no_failure(self):
        # Given [market]: <declared>, When checked, Then nothing is reported
        self.assertEqual(wrong_definitions("d.md", "[market]: https://example.org/market\n", FIXTURE_LINKS), [])

    def test_given_a_definition_with_another_address_then_the_document_and_the_name_are_reported(self):
        # Given [market]: <other>, When checked, Then the failure names the document and the name
        failures = wrong_definitions("d.md", "text\n[market]: https://example.org/old\n", FIXTURE_LINKS)
        self.assertEqual(len(failures), 1)
        self.assertIn("d.md", failures[0])
        self.assertIn("[market]", failures[0])

    def test_given_a_definition_of_an_undeclared_name_then_it_is_ignored(self):
        # Given [other]: <anything>, When checked, Then nothing is reported
        self.assertEqual(wrong_definitions("d.md", "[other]: https://elsewhere.org\n", FIXTURE_LINKS), [])


class TestHardCodedAddresses(unittest.TestCase):
    """RQ-DOC-007 / DEC-DOC-001: rule b, no declared address outside a reference definition line."""

    def test_given_only_reference_definitions_and_references_then_there_is_no_failure(self):
        # Given a reference-style link and its definition, When checked, Then nothing is reported
        text = "See [the market][market].\n\n[market]: https://example.org/market\n"
        self.assertEqual(hard_coded_addresses("d.md", text, FIXTURE_LINKS), [])

    def test_given_an_inline_link_to_a_declared_address_then_it_is_reported(self):
        # Given [x](<declared>), When checked, Then the failure names the document and the link name
        failures = hard_coded_addresses("d.md", "See [x](https://example.org/site).\n", FIXTURE_LINKS)
        self.assertEqual(len(failures), 1)
        self.assertIn("d.md", failures[0])
        self.assertIn("[site]", failures[0])

    def test_given_a_bare_declared_address_before_a_full_stop_then_it_is_reported(self):
        # Given a sentence ending in a declared address and a period, When checked, Then it is reported
        self.assertEqual(len(hard_coded_addresses("d.md", "Go to https://example.org/site.\n", FIXTURE_LINKS)), 1)

    def test_given_a_url_extending_a_declared_address_by_a_fragment_or_a_path_then_it_is_reported(self):
        # Given address#fragment and address/blob/x, When checked, Then each is a hard-coded copy
        text = "https://example.org/site#a and https://example.org/site/blob/x\n"
        self.assertEqual(len(hard_coded_addresses("d.md", text, FIXTURE_LINKS)), 2)

    def test_given_a_url_equal_to_another_declared_address_then_it_is_reported_under_both_names(self):
        # Given the declared "start" address, which extends "market", When checked, Then both names are reported
        failures = hard_coded_addresses("d.md", "https://example.org/market#start\n", FIXTURE_LINKS)
        self.assertEqual(len(failures), 2)

    def test_given_a_url_merely_sharing_a_prefix_with_a_declared_address_then_it_is_not_reported(self):
        # Given example.org/market-place, which only begins with the characters of market, Then it is not a copy
        self.assertEqual(hard_coded_addresses("d.md", "https://example.org/market-place\n", FIXTURE_LINKS), [])

    def test_given_a_definition_of_a_declared_address_among_other_text_then_only_the_other_text_is_checked(self):
        # Given a definition line and an inline copy, When checked, Then one failure
        text = "[site]: https://example.org/site\nhttps://example.org/site\n"
        self.assertEqual(len(hard_coded_addresses("d.md", text, FIXTURE_LINKS)), 1)


class TestMarketplaceManifest(unittest.TestCase):
    """RQ-DOC-007 / DEC-DOC-001: rule d, the plugin's homepage and repository are the process address."""

    def test_given_both_fields_equal_to_the_process_address_then_there_is_no_failure(self):
        # Given homepage and repository equal to links["process"], When checked, Then nothing is reported
        manifest = {PLUGIN: {HOMEPAGE: "https://p", REPOSITORY: "https://p"}}
        self.assertEqual(marketplace_mismatches(manifest, {PROCESS_LINK: "https://p"}), [])

    def test_given_a_field_with_another_address_then_it_is_reported(self):
        # Given a repository field that differs, When checked, Then the failure names the field
        manifest = {PLUGIN: {HOMEPAGE: "https://p", REPOSITORY: "https://old"}}
        failures = marketplace_mismatches(manifest, {PROCESS_LINK: "https://p"})
        self.assertEqual(len(failures), 1)
        self.assertIn(REPOSITORY, failures[0])


class TestRepositoryAddresses(unittest.TestCase):
    """RQ-DOC-007 / DEC-DOC-001: the rules applied to the real links file, documents and manifest."""

    @classmethod
    def setUpClass(cls):
        cls.links = load(LINKS_FILE)[LINKS_KEY]

    def test_given_links_json_then_it_declares_exactly_the_eight_names(self):
        # Given assets/links.json, Then its names are exactly the eight of RQ-DOC-007
        self.assertEqual(sorted(self.links), sorted(DECLARED_NAMES))

    def test_given_marketplace_json_then_homepage_and_repository_are_the_process_address(self):
        # Given the release's marketplace.json, Then both fields equal links["process"]
        self.assertEqual(marketplace_mismatches(load(MARKETPLACE_FILE), self.links), [])

    def test_given_the_checked_documents_then_each_reference_definition_holds_the_declared_address(self):
        # Given the checked documents, Then no reference definition of a declared name differs from links.json
        failures = []
        for document in CHECKED_DOCUMENTS:
            text = (ROOT / document).read_text(encoding=ENCODING)
            failures += wrong_definitions(document, text, self.links)
        self.assertEqual(failures, [])

    def test_given_the_checked_documents_then_none_hard_codes_a_declared_address(self):
        # Given the checked documents, Then no declared address appears outside a reference definition line
        failures = []
        for document in CHECKED_DOCUMENTS:
            text = (ROOT / document).read_text(encoding=ENCODING)
            failures += hard_coded_addresses(document, text, self.links)
        self.assertEqual(failures, [])


README = "README.md"
GUIDE = ".github/skills/agnos-init/assets/templates/AGNOS-GETTING-STARTED.md"
GUIDE_TABLE = "## What you actually type, all together"
PERF_CENTER_ROW = "| 8. "
PERF_CENTER_NAME = "Performance Center"
PERF_CENTER_OPTIONS = ("--call-graph", "--history")
FORMER_TRACE_WORDS = ("Trace", "traceability matrix")
GUIDE_SOURCE = "Its source is"
FULL_REFERENCE = re.compile(r"\]\[([^\]]+)\]")


def referenced_names(text):
    """The names a text references as [label][name] and also defines. RQ-DOC-008 / DEC-DOC-001"""
    return set(FULL_REFERENCE.findall(text)) & set(definitions(text))


def table_rows(text, heading):
    """The table rows (lines starting with |) of the section under heading. RQ-DOC-008"""
    section = text.split(heading, 1)[1].split("\n## ", 1)[0]
    return [line for line in section.splitlines() if line.startswith("|")]


class TestProcessDocumentLinks(unittest.TestCase):
    """RQ-DOC-008 / DEC-DOC-001: the README and the guide link the AGNOS places."""

    @classmethod
    def setUpClass(cls):
        cls.readme = (ROOT / README).read_text(encoding=ENCODING)
        cls.guide = (ROOT / GUIDE).read_text(encoding=ENCODING)

    def test_given_the_readme_then_it_links_the_perf_center_and_the_marketplace(self):
        # Given the README, Then it references and defines perf-center and marketplace
        self.assertLessEqual({"perf-center", "marketplace"}, referenced_names(self.readme))

    def test_given_the_readme_then_the_guide_source_is_the_guide_in_the_marketplace(self):
        # Given the README's sentence on the guide's source, Then its link is the [guide] reference
        sentence = self.readme.split(GUIDE_SOURCE, 1)[1].split("<!--", 1)[0]
        self.assertIn("][guide]", sentence)

    def test_given_the_guide_table_then_row_8_names_the_perf_center_and_its_options(self):
        # Given the table "What you actually type", Then row 8 names the Performance Center, --call-graph and --history
        row = next(line for line in table_rows(self.guide, GUIDE_TABLE) if line.startswith(PERF_CENTER_ROW))
        for word in (PERF_CENTER_NAME, *PERF_CENTER_OPTIONS):
            self.assertIn(word, row)

    def test_given_the_guide_table_then_no_row_names_a_trace(self):
        # Given the table "What you actually type", Then no row names a trace or a traceability matrix
        for line in table_rows(self.guide, GUIDE_TABLE):
            for word in FORMER_TRACE_WORDS:
                self.assertNotIn(word, line)


DEMO_READMES = (".github/skills/agnos-meta-demo/assets/content/README.md",
                ".github/skills/agnos-meta-demo/assets/content/drafts/README.web.md")    # the first one, then the final one
DEMO_LINKED_NAMES = {"perf-center", "marketplace", "process"}
FORMER_SKILL_NAME = "traceability skill"


class TestDemoReadmeLinks(unittest.TestCase):
    """RQ-DOC-008 / DEC-DOC-001: both READMEs of the demo's content link the AGNOS places and name the Performance Center."""

    def test_given_each_demo_readme_then_it_links_the_perf_center_the_marketplace_and_the_process(self):
        # Given each README of the demo's content, Then it references and defines perf-center, marketplace and process
        for document in DEMO_READMES:
            text = (ROOT / document).read_text(encoding=ENCODING)
            self.assertLessEqual(DEMO_LINKED_NAMES, referenced_names(text), document)

    def test_given_each_demo_readme_then_it_names_the_perf_center_not_the_traceability_skill(self):
        # Given each README of the demo's content, Then it names the Performance Center And not the traceability skill
        for document in DEMO_READMES:
            text = (ROOT / document).read_text(encoding=ENCODING)
            self.assertNotIn(FORMER_SKILL_NAME, text, document)
            self.assertIn(PERF_CENTER_NAME, text, document)


if __name__ == "__main__":
    unittest.main()
