"""Tests that this repository's citations stay in comments (RQ-MTA-014, TASK-MTA-009).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-meta-demo/tests -v
"""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SKILLS = ".github/skills"
# RQ-PLG-036 / DEC-PLG-027: the process folder and its index, as the layout declares them
LAYOUT = json.loads((ROOT / SKILLS / "agnos-init" / "assets" / "layout.json").read_text(encoding="utf-8"))
INDEX = ROOT / LAYOUT["folder"] / LAYOUT["index"]
CHANGELOG = ROOT / "CHANGELOG.md"
DOCS_SYNC_SKILL = ROOT / SKILLS / "agnos-meta-docs-sync" / "SKILL.md"
SCRIPTS = (f"{SKILLS}/agnos-perf-center/scripts/perf_center.py",
           f"{SKILLS}/agnos-meta-docs-sync/scripts/changes_since.py",
           f"{SKILLS}/agnos-meta-qa/scripts/qa.py")
ID_TYPES = "FTR|RQ|ADR|DEC|PLAN|TASK"
DEFINITION_RE = re.compile(rf"^(?:{ID_TYPES})-([A-Z]{{3}})-\d{{3}}\|", re.M)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
COMMENT_OPEN = "<!--"
SKIPPED_RE = re.compile(rf"^{re.escape(LAYOUT['folder'])}/|/tests?/|^{SKILLS}/agnos-meta-demo/assets/")
MARKDOWN_RE = re.compile(r"\.md$", re.I)
PREVIOUS_ENTRY_ID = "TASK-TRC-091"
COMMENT_FORM = "<!-- TASK-TRC-046, RQ-TRC-058 -->"


def repository_id_pattern():
    trigrams = sorted(set(DEFINITION_RE.findall(INDEX.read_text(encoding="utf-8"))))
    return re.compile(rf"\b(?:{ID_TYPES})-(?:{'|'.join(trigrams)})-\d{{3}}\b")


def tracked_markdown():
    listed = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True)
    return [path for path in listed.stdout.splitlines() if MARKDOWN_RE.search(path) and not SKIPPED_RE.search(path)]


class CitationsTest(unittest.TestCase):
    """RQ-MTA-014."""

    def test_RQ_MTA_014_given_the_markdown_outside_process_when_comments_are_set_aside_then_none_shows_an_id(self):
        pattern = repository_id_pattern()
        shown = []
        for path in tracked_markdown():
            visible = HTML_COMMENT_RE.sub("", (ROOT / path).read_text(encoding="utf-8"))
            shown += [f"{path}: {line.strip()}" for line in visible.splitlines() if pattern.search(line)]
        self.assertEqual([], shown)

    def test_RQ_MTA_014_given_the_markdown_outside_process_then_no_comment_opens_inside_another(self):
        nested = [path for path in tracked_markdown()
                  if any(COMMENT_OPEN in comment[len(COMMENT_OPEN):]
                         for comment in HTML_COMMENT_RE.findall((ROOT / path).read_text(encoding="utf-8")))]
        self.assertEqual([], nested)

    def test_RQ_MTA_014_given_the_scripts_when_run_with_help_then_none_shows_an_id(self):
        pattern = repository_id_pattern()
        for script in SCRIPTS:
            helped = subprocess.run([sys.executable, script, "--help"], cwd=ROOT, capture_output=True, text=True,
                                    encoding="utf-8", check=True)
            self.assertIsNone(pattern.search(helped.stdout), script)

    def test_RQ_MTA_014_given_the_changelog_when_an_id_of_a_previous_entry_is_searched_then_it_is_found_in_a_comment(self):
        comments = HTML_COMMENT_RE.findall(CHANGELOG.read_text(encoding="utf-8"))
        self.assertTrue(any(PREVIOUS_ENTRY_ID in comment for comment in comments))

    def test_RQ_MTA_014_given_the_docs_sync_skill_when_it_is_read_then_it_asks_for_the_comment_form(self):
        self.assertIn(COMMENT_FORM, DOCS_SYNC_SKILL.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
