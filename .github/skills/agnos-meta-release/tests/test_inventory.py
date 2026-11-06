"""Tests that the output holds what is declared, nothing more (RQ-PLG-012, TASK-PLG-011; ADR-PLG-002: DEC-PLG-008).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-meta-release/tests -v
"""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))
import release  # noqa: E402
from test_select import EXIT_FAILED, EXIT_OK, GENERATED, PROCESS_PLACE, SKILL_PLACE, TOOLKIT_FILE, VERSION_PLACE, RehearsalCase, files_under  # noqa: E402

STRAY = "plugins/agnos/skills/agnos-index/scripts/__pycache__/x.cpython-314.pyc"
CACHE_FOLDER = "__pycache__"
MODULE = "imported.py"
MAIN = "main.py"


def stray_proof(repo, output, demo):
    """A proof that leaves a cache in the output, as running its Python in place did."""
    (output / STRAY).parent.mkdir(parents=True, exist_ok=True)
    (output / STRAY).write_bytes(b"cache")
    return []


class InventoryTest(RehearsalCase):
    """RQ-PLG-012."""

    def rehearse_with(self, proof):
        said = io.StringIO()     # RQ-PLG-014: a rehearsal's problems are printed with its other findings
        with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
            code = release.main(["--repo", str(self.repo), "--dry-run", "--output", str(self.output)], proof=proof)
        return code, said.getvalue()

    def test_RQ_PLG_012_given_a_rehearsal_then_the_files_on_disk_are_exactly_the_delivered_and_generated_ones(self):
        self.assertEqual(EXIT_OK, self.rehearse()[0])
        self.assertEqual(sorted({TOOLKIT_FILE, SKILL_PLACE, PROCESS_PLACE, "CHANGELOG.md", VERSION_PLACE, *GENERATED}), files_under(self.output))

    def test_RQ_PLG_012_given_a_file_added_to_the_output_before_the_inventory_then_it_exits_1_and_names_it(self):
        code, errors = self.rehearse_with(stray_proof)
        self.assertEqual(EXIT_FAILED, code)
        self.assertIn(STRAY, errors)


class NoCacheTest(unittest.TestCase):
    """RQ-PLG-012: the checks run Python from the output, which must not leave its cache there."""

    def test_RQ_PLG_012_given_a_python_script_importing_a_module_when_the_release_runs_it_then_no_pycache_is_written(self):
        with tempfile.TemporaryDirectory() as holder:
            folder = Path(holder)
            (folder / MODULE).write_text("VALUE = 1\n", encoding="utf-8")
            (folder / MAIN).write_text("import imported\n", encoding="utf-8")
            self.assertEqual(b"exit 0", release.run_tool([sys.executable, MAIN], folder))
            self.assertFalse((folder / CACHE_FOLDER).exists())


if __name__ == "__main__":
    unittest.main()
