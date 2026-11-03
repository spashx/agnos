"""Tests of the page written beside the report (RQ-PLG-016, TASK-PLG-016; ADR-PLG-002: DEC-PLG-011, DEC-PLG-012).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-meta-release/tests -v
"""
import json
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))
import release  # noqa: E402
from test_select import EXIT_OK, REPORT_SUFFIX, TOOLKIT_FILE, RehearsalCase  # noqa: E402

PAGE_SUFFIX = ".report.html"
DATA_RE = re.compile(r'<script type="application/json" id="report">(.*?)</script>', re.S)
HOSTILE = "</script><script>alert(1)</script> & <b>bold</b>"
NETWORK_RE = re.compile(r"""(?:src|href)\s*=\s*["']?(?:https?:)?//""", re.I)
SECTIONS = ("Checks", "Problems", "Lines to read", "Mentions", "IDs outside comments", "IDs removed per file", "Delivered", "Left out")
TOKENS = ":root { --s-surface: white; }"


def sample_report():
    return {"commit": "abc", "delivered": [TOOLKIT_FILE], "leftOut": ["CLAUDE.md"], "removed": {TOOLKIT_FILE: 2},
            "toRead": [{"file": TOOLKIT_FILE, "line": 3, "text": HOSTILE}], "mentions": [], "idsOutsideComments": [],
            "checks": {"noIdLeft": True, "manifests": True, "sameBehaviour": True}, "problems": []}


def embedded(page):
    found = DATA_RE.search(page)
    return json.loads(found.group(1)) if found else None


class PageTest(unittest.TestCase):
    """RQ-PLG-016: one self-contained page, its data embedded safely."""

    def test_RQ_PLG_016_given_a_report_then_the_page_embeds_every_value_of_it(self):
        report = sample_report()
        self.assertEqual(report, embedded(release.report_page(report, TOKENS)))

    def test_RQ_PLG_016_given_a_text_holding_a_script_tag_then_the_page_holds_it_only_as_data(self):
        page = release.report_page(sample_report(), TOKENS)
        self.assertNotIn("</script><script>alert", page)
        self.assertEqual(HOSTILE, embedded(page)["toRead"][0]["text"])

    def test_RQ_PLG_016_given_the_page_then_it_loads_nothing_from_the_network_and_draws_text_only(self):
        page = release.report_page(sample_report(), TOKENS)
        self.assertIsNone(NETWORK_RE.search(page))
        self.assertNotIn("<link", page)
        self.assertNotIn("innerHTML", page)

    def test_RQ_PLG_016_given_the_page_then_it_names_each_section_of_the_report(self):
        page = release.report_page(sample_report(), TOKENS)
        for section in SECTIONS:
            self.assertIn(section, page)

    def test_RQ_PLG_017_given_the_tokens_then_they_precede_the_stylesheet_in_the_page(self):
        page = release.report_page(sample_report(), TOKENS)
        self.assertLess(page.index(TOKENS), page.index(release.REPORT_CSS_PATH.read_text(encoding="utf-8").strip()))


class WrittenTest(RehearsalCase):
    """RQ-PLG-016: the page is written beside the JSON report, with the same data."""

    def test_RQ_PLG_016_given_a_rehearsal_then_the_page_is_beside_the_json_and_embeds_it(self):
        self.assertEqual(EXIT_OK, self.rehearse()[0])
        page = Path(f"{self.output}{PAGE_SUFFIX}").read_text(encoding="utf-8")
        report = json.loads(Path(f"{self.output}{REPORT_SUFFIX}").read_text(encoding="utf-8"))
        self.assertEqual(report, embedded(page))


if __name__ == "__main__":
    unittest.main()
