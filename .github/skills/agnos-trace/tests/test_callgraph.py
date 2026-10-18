"""Tests of the optional call-graph analysis of agnos-trace (FTR-TRC-002, ADR-TRC-004), on tests/fixtures/repo.

Run from the repository root: python -m unittest discover -s .github/skills/agnos-trace/tests -v
The tests that parse need the packages of requirements-callgraph.txt and are skipped without them.
"""
import ast
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))

import callgraph as cg  # noqa: E402
import trace_matrix as tm  # noqa: E402
from test_trace_matrix import PROCESS, SKILL, SOURCES, data_block, generate, run_main  # noqa: E402

HAS_TREE_SITTER = importlib.util.find_spec("tree_sitter") is not None
NEEDS_TREE_SITTER = "tree-sitter is not installed (pip install -r .github/skills/agnos-trace/requirements-callgraph.txt)"
DATA_BEFORE_PLAN_SHA256 = "c43656a2d4ce43c171aff4ceb8477c82836225ee4074c19af25bb54793ca5dd2"   # the fixture page's data
# before PLAN-TRC-002, with its two machine-dependent fields (the process and source paths given) blanked


def location_free_sha256(page):
    data = json.loads(data_block(page))
    data["meta"]["process"] = data["meta"]["sources"] = None
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()


def summary_line(stdout):
    return stdout.strip().splitlines()[-1]


class OptionalModuleTest(unittest.TestCase):
    """TASK-TRC-009: RQ-TRC-026, RQ-TRC-027, RQ-TRC-039 (DEC-TRC-013)."""

    def test_RQ_TRC_026_given_no_call_graph_option_when_generated_then_the_data_is_the_one_before_this_feature(self):
        with tempfile.TemporaryDirectory() as tmp:
            page, _ = generate(Path(tmp) / "page.html")
        self.assertEqual(DATA_BEFORE_PLAN_SHA256, location_free_sha256(page))

    def test_RQ_TRC_039_given_no_call_graph_option_when_the_generator_runs_then_no_tree_sitter_module_is_imported(self):
        probe = ("import sys, tempfile, pathlib; sys.path.insert(0, sys.argv[1]); import trace_matrix as tm\n"
                 "out = pathlib.Path(tempfile.mkdtemp()) / 'page.html'\n"
                 "code = tm.main(['--process', sys.argv[2], '--sources', sys.argv[3], '--out', str(out)])\n"
                 "print(code, sorted(m for m in sys.modules if m.startswith(('tree_sitter', 'agnos_trace'))))")
        done = subprocess.run([sys.executable, "-c", probe, str(SKILL / "scripts"), str(PROCESS), str(SOURCES)],
                              capture_output=True, text=True, timeout=120, check=False)
        self.assertEqual("0 []", done.stdout.strip().splitlines()[-1], done.stderr)

    def test_RQ_TRC_027_given_no_tree_sitter_when_run_with_call_graph_then_it_exits_0_and_prints_the_install_command(
            self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(sys.modules, {"tree_sitter": None}):
            out = Path(tmp) / "page.html"
            code, stdout, err = run_main(["--process", str(PROCESS), "--sources", str(SOURCES), "--out", str(out),
                                          "--call-graph"])
            self.assertEqual(0, code, err)
            self.assertTrue(out.is_file())
        line = summary_line(stdout)
        self.assertIn("call graph skipped: tree-sitter not installed", line)
        self.assertIn("pip install -r ", line)
        self.assertIn("requirements-callgraph.txt", line)

    @unittest.skipUnless(HAS_TREE_SITTER, NEEDS_TREE_SITTER)
    def test_RQ_TRC_027_given_a_language_whose_grammar_is_missing_when_loaded_then_only_that_language_is_skipped(self):
        table = dict(cg.load_table())
        table["nolang"] = {"extensions": [".nolang"], "package": "tree-sitter-nolang",
                           "module": "tree_sitter_nolang_absent", "query": "cpp.scm"}
        grammars, missing = cg.load_grammars(table, cg.TreeSitter())
        self.assertEqual(["tree-sitter-nolang"], missing)
        self.assertNotIn(".nolang", grammars)
        self.assertEqual("cpp", grammars[".cpp"].name)

    def test_RQ_TRC_039_given_the_call_graph_module_when_its_imports_are_read_then_they_are_all_standard_library(self):
        tree = ast.parse((SKILL / "scripts" / "callgraph.py").read_text(encoding="utf-8"))
        imported = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        imported |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
        self.assertEqual(set(), imported - set(sys.stdlib_module_names))

    def test_RQ_TRC_039_given_the_requirements_file_when_read_then_it_pins_tree_sitter_and_every_grammar_of_the_table(
            self):
        pins = dict(line.split("==") for line in cg.REQUIREMENTS_PATH.read_text(encoding="utf-8").splitlines()
                    if line and not line.startswith("#"))
        self.assertEqual({cg.CORE_PACKAGE} | {e["package"] for e in cg.load_table().values()}, set(pins))
        if HAS_TREE_SITTER:
            import importlib.metadata
            self.assertEqual(pins, {p: importlib.metadata.version(p) for p in pins})


class LanguageTableTest(unittest.TestCase):
    """TASK-TRC-009: RQ-TRC-032 (DEC-TRC-014)."""

    def test_RQ_TRC_032_given_the_language_table_then_each_entry_names_its_extensions_package_module_and_query(self):
        table = cg.load_table()
        self.assertEqual({"c", "cpp"}, set(table))
        seen = []
        for name, entry in table.items():
            self.assertTrue(entry["extensions"] and all(x.startswith(".") for x in entry["extensions"]), name)
            self.assertTrue(entry["package"] and entry["module"], name)
            self.assertTrue((cg.ASSETS_DIR / entry["query"]).is_file(), name)
            seen += entry["extensions"]
        self.assertEqual(len(seen), len(set(seen)))
        self.assertIn(".h", table["cpp"]["extensions"])          # owner default: headers read with the C++ grammar


if __name__ == "__main__":
    unittest.main()
