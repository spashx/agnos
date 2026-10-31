"""Tests of the removal of the workshop's IDs, of the check on the output and of the lines to read (RQ-MTA-009, RQ-MTA-010,
RQ-MTA-012, TASK-MTA-006; ADR-MTA-002: DEC-MTA-009). Most forms are taken from this repository, with the trigram ABC.

Run from the repository root: python -m unittest discover -s .github/skills/agnos-meta-release/tests -v
"""
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import release  # noqa: E402

INDEX = "@process/a.md\nFTR-ABC-001|1-9||A feature\nRQ-ABC-001|2-3||A requirement\n#next RQ-ABC-002\n"
PATTERN = release.id_pattern(release.index_trigrams(INDEX))

REMOVALS = (
    ("a parenthesis of IDs", "the time it took (RQ-ABC-018).\n", "the time it took.\n"),
    ("a parenthesis over two lines", "a change (ADR-ABC-013, TASK-ABC-089,\n  RQ-ABC-104 to RQ-ABC-106)\nnext\n", "a change\nnext\n"),
    ("a label's parenthesis", "Views (TASK-ABC-005): overview\n", "Views: overview\n"),
    ("IDs with a nested parenthesis", "x (RQ-ABC-001 / ADR-ABC-001 (DEC-ABC-001 to DEC-ABC-004)) y\n", "x y\n"),
    ("a comment alone on its line", "a\n<!-- RQ-ABC-001 / ADR-ABC-001 -->\nb\n", "a\nb\n"),
    ("a comment closing a sentence", "run this: <!-- RQ-ABC-010 -->\n", "run this:\n"),
    ("a comment inside a sentence", "the hash <!-- RQ-ABC-080 -->; nothing else\n", "the hash; nothing else\n"),
    ("a heading's comment", "## Libraries <!-- FTR-ABC-005; ADR-ABC-010: DEC-ABC-040 -->\n", "## Libraries\n"),
    ("a leading citation", "# RQ-ABC-001: the order\n", "# The order\n"),
    ("a leading range", "# RQ-ABC-001 to RQ-ABC-004: the order\n", "# The order\n"),
    ("a leading list in a JSON comment", '"_comment": "FTR-ABC-004, ADR-ABC-009 (DEC-ABC-037): the settings"\n', '"_comment": "The settings"\n'),
    ("a Python comment of IDs alone", "# RQ-ABC-001\ndef f():\n", "def f():\n"),
    ("a comment ending a line of code", "A = 1  # DEC-ABC-003\n", "A = 1\n"),
    ("a comment ending a line, with text", "A = 1  # RQ-ABC-107: seconds\n", "A = 1  # Seconds\n"),
    ("a CSS comment with an abbreviation", "a { b: c; }   /* TASK-ABC-073, 074 */\n", "a { b: c; }\n"),
    ("a mixed parenthesis, the ID last", "(1,000 tasks delivered; RQ-ABC-078)\n", "(1,000 tasks delivered)\n"),
    ("a mixed parenthesis, the ID first", "(RQ-ABC-078: the tasks)\n", "(the tasks)\n"),
    ("a line of IDs alone in a docstring", "A title.\n\nRQ-ABC-001 to RQ-ABC-006 / ADR-ABC-001.\n", "A title.\n\n"),
    ("an ID undefined in the index", "x (RQ-ABC-999)\n", "x\n"),
    ("abbreviated numbers", "x (RQ-ABC-074, 076, 083 to 085)\n", "x\n"),
    ("a comment of labels and IDs only", "a\n<!-- FTR-ABC-001; history: FTR-ABC-002,\n  RQ-ABC-001; call graph: DEC-ABC-019. -->\nb\n", "a\nb\n"),
    ("a CSS selector's spaces on the same line", ".a .b { c: d; }   /* RQ-ABC-001 */\n", ".a .b { c: d; }\n"),
    ("a path after a colon on the same line", "Procedure: ../SKILL.md (RQ-ABC-001)\n", "Procedure: ../SKILL.md\n"),
    ("a trailing comma elsewhere on the same line", "a = [1 , 2] ,  # RQ-ABC-001\n", "a = [1 , 2] ,\n"),
)
UNCHANGED = (
    "an example RQ-EXP-001 and DEC-USR-001 stay\n",
    "`DEC-<TRI>-<NNN>` and a plain line\n",
    "RQ-ABC-001".replace("ABC", "EXP") + " (TASK-EXP-001)\r\n",
)


class RemovalTest(unittest.TestCase):
    """RQ-MTA-009."""

    def test_RQ_MTA_009_given_each_form_of_citation_then_it_goes_with_the_punctuation_that_served_it(self):
        for name, before, after in REMOVALS:
            with self.subTest(name):
                self.assertEqual(after, release.remove_ids(before, PATTERN)[0])

    def test_RQ_MTA_009_given_ids_of_another_trigram_or_no_id_then_the_text_is_unchanged_byte_for_byte(self):
        for text in UNCHANGED:
            self.assertEqual((text, 0), release.remove_ids(text, PATTERN)[:2])

    def test_RQ_MTA_009_given_a_line_with_no_id_beside_a_cleaned_one_then_its_bytes_and_ending_stay(self):
        cleaned, _, _ = release.remove_ids("kept  ,\r\nA = 1  # DEC-ABC-003\r\nkept too\n", PATTERN)
        self.assertEqual("kept  ,\r\nA = 1\r\nkept too\n", cleaned)

    def test_RQ_MTA_009_given_the_index_then_its_trigrams_are_read_and_not_the_next_line(self):
        self.assertEqual({"ABC"}, release.index_trigrams(INDEX))

    def test_RQ_MTA_009_given_a_number_that_is_a_quantity_then_it_is_not_taken_for_an_abbreviation(self):
        self.assertEqual("x, 100 ms\n", release.remove_ids("x RQ-ABC-001, 100 ms\n", PATTERN)[0])


class OutputCheckTest(unittest.TestCase):
    """RQ-MTA-010."""

    def setUp(self):
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.output = Path(holder.name)

    def write(self, name, data):
        path = self.output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def test_RQ_MTA_010_given_an_id_left_in_a_comment_or_a_visible_text_then_the_file_and_line_are_named(self):
        self.write("a.py", b"x = 1\n# RQ-ABC-001\n")
        self.write("b.md", b"see RQ-ABC-999\n")
        self.assertEqual(["a.py:2: RQ-ABC-001", "b.md:1: RQ-ABC-999"], release.check_output(self.output, PATTERN, {}))

    def test_RQ_MTA_010_given_an_id_in_a_binary_file_or_a_path_then_it_is_named(self):
        self.write("a.bin", b"\xff\xfe RQ-ABC-001")
        self.write("RQ-ABC-002/b.md", b"clean\n")
        problems = release.check_output(self.output, PATTERN, {})
        self.assertEqual(2, len(problems))
        self.assertTrue(any("RQ-ABC-001" in p for p in problems) and any("RQ-ABC-002" in p for p in problems))

    def test_RQ_MTA_010_given_a_meta_file_in_the_output_then_it_is_named(self):
        self.write(".github/skills/agnos-meta-x/SKILL.md", b"clean\n")
        rules = release.load_rules()
        self.assertEqual([".github/skills/agnos-meta-x/SKILL.md: a file of the Meta layer"], release.check_output(self.output, PATTERN, rules))

    def test_RQ_MTA_010_given_an_output_with_only_examples_then_it_passes(self):
        self.write("a.md", b"RQ-EXP-001 and DEC-USR-001\n")
        self.assertEqual([], release.check_output(self.output, PATTERN, {}))


class LinesToReadTest(unittest.TestCase):
    """RQ-MTA-012."""

    def test_RQ_MTA_012_given_a_sentence_left_ending_in_a_preposition_then_it_is_a_line_to_read(self):
        _, count, to_read = release.remove_ids("kept\nThe findings are justified in TASK-ABC-006.\n", PATTERN)
        self.assertEqual(1, count)
        self.assertEqual([(2, "The findings are justified in.")], to_read)

    def test_RQ_MTA_012_given_a_clean_removal_then_nothing_is_to_read(self):
        self.assertEqual([], release.remove_ids("the time it took (RQ-ABC-018).\n", PATTERN)[2])

    def test_RQ_MTA_012_given_a_line_ending_in_a_comma_away_from_the_removal_then_nothing_is_to_read(self):
        self.assertEqual([], release.remove_ids("the walk's functions (RQ-ABC-018) at the level of detail,\n", PATTERN)[2])

    def test_RQ_MTA_012_given_a_mention_of_a_meta_skill_or_undelivered_path_then_it_is_listed(self):
        text = "call `agnos-meta-qa` and read `.github/skills/x/tests/test_a.py`\nnothing here\n"
        self.assertEqual([(1, "agnos-meta-"), (1, ".github/skills/x/tests/test_a.py")],
                         release.mentions(text, [".github/skills/x/tests/test_a.py"]))

    def test_RQ_MTA_012_given_a_test_named_alone_then_it_is_listed_and_a_project_file_is_not(self):
        text = "see `test_a.py`\nread process/INDEX.idx.md and session.yaml\n"
        left_out = [".github/skills/x/tests/test_a.py", "process/INDEX.idx.md", "process/_sessionstate/session.yaml"]
        self.assertEqual([(1, "test_a.py")], release.mentions(text, left_out))

    def test_RQ_MTA_012_given_markdown_then_only_ids_outside_a_comment_are_listed(self):
        text = "visible RQ-ABC-001\n<!-- hidden RQ-ABC-002\nstill RQ-ABC-003 -->\nvisible again TASK-ABC-004\n"
        self.assertEqual([(1, "RQ-ABC-001"), (4, "TASK-ABC-004")], release.ids_outside_comments(text, PATTERN))


if __name__ == "__main__":
    unittest.main()
