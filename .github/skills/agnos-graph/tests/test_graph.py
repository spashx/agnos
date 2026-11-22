"""Tests of the project state graph file written by agnos-graph (FTR-TRC-011; ADR-TRC-022: DEC-TRC-074, DEC-TRC-077).

TASK-TRC-117: RQ-TRC-129, RQ-TRC-130, RQ-TRC-133. Run: python -m unittest discover -s .github/skills/agnos-graph/tests
"""
import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import agnos_layout  # noqa: E402  RQ-PLG-036: the graph file's name, as the script reads it
import graph  # noqa: E402

FIXTURE = HERE / "fixtures" / "repo"
PROCESS = FIXTURE / "process"
SOURCES = FIXTURE / "src"
CALLS = FIXTURE / "calls"
GENERATED_AT = "2026-11-22T10:00Z"
HAS_TREE_SITTER = importlib.util.find_spec("tree_sitter") is not None
NEEDS_TREE_SITTER = "tree-sitter is not installed (pip install -r .github/skills/agnos-graph/requirements-callgraph.txt)"
STATE_KEYS = {"meta", "elements", "edges", "files", "tasks"}
JUDGEMENT_KEYS = {"coverage", "quality", "findings"}
OPTIONAL_KEYS = {"callGraph", "history", "delivery"}
GIT_IDENTITY = ["-c", "user.name=Tester", "-c", "user.email=tester@example.com"]


def run_main(args):
    """Runs the graph script's entry point; returns (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = graph.main(args)
    return code, out.getvalue(), err.getvalue()


def git(top, *args):
    """Runs git in a test repository, with a fixed identity and no user configuration (RQ-TRC-130)."""
    return subprocess.run(["git", *GIT_IDENTITY, *args], cwd=top, capture_output=True, text=True, check=True,
                          timeout=60).stdout.strip()


def committed_fixture(root):
    """The fixture copied into a git repository of one commit; returns (process folder, source folder, HEAD)."""
    top = root / "repo"
    shutil.copytree(FIXTURE, top)
    git(top, "init", "-q")
    git(top, "add", "-A")
    git(top, "commit", "-q", "-m", "fixture")
    return top / "process", top / "src", git(top, "rev-parse", "HEAD")


def isolated_git():
    """No global nor system git configuration: the tests do not depend on the machine's (RQ-TRC-130)."""
    folder = tempfile.mkdtemp(prefix="agnos-graph-config-")
    empty = Path(folder) / "gitconfig"
    empty.write_text("[init]\n\tdefaultBranch = main\n", encoding="utf-8")
    return folder, mock.patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": str(empty), "GIT_CONFIG_NOSYSTEM": "1"})


def setUpModule():
    folder, patcher = isolated_git()
    patcher.start()
    unittest.addModuleCleanup(patcher.stop)
    unittest.addModuleCleanup(shutil.rmtree, folder, ignore_errors=True)


class GraphFileTest(unittest.TestCase):
    """TASK-TRC-117: RQ-TRC-129 (DEC-TRC-074)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="agnos-graph-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.out = self.tmp / "graph.json"

    def written(self, *extra):
        code, _, err = run_main(["--process", str(PROCESS), "--sources", str(SOURCES), "--out", str(self.out),
                                 "--generated-at", GENERATED_AT, *extra])
        self.assertEqual(0, code, err)
        return json.loads(self.out.read_text(encoding="utf-8"))

    def test_RQ_TRC_129_given_the_fixture_when_the_graph_runs_then_it_holds_the_state_and_no_judgement(self):
        data = self.written()
        self.assertEqual(STATE_KEYS, set(data))
        self.assertEqual(set(), JUDGEMENT_KEYS & set(data))
        self.assertIn("RQ-DEM-001", {e["id"] for e in data["elements"]})
        self.assertTrue(any(kind == "code" for _, _, kind, _ in data["edges"]))
        self.assertTrue(any(f["path"].endswith("src/a.py") for f in data["files"]))   # shown relative to the run's folder

    def test_RQ_TRC_129_given_the_fixture_tasks_then_each_holds_its_tier_and_cited_requirements(self):
        tasks = self.written()["tasks"]
        self.assertTrue(tasks)
        for task_id, task in tasks.items():
            self.assertTrue(task_id.startswith("TASK-"))
            self.assertIn(task["tier"], ("S", "M", "L", None))
            self.assertTrue(all(rq.startswith("RQ-") for rq in task["requirements"]))

    @unittest.skipUnless(HAS_TREE_SITTER, NEEDS_TREE_SITTER)
    def test_RQ_TRC_129_given_call_graph_and_history_then_it_also_holds_the_call_graph_history_and_delivery(self):
        process, sources, _ = committed_fixture(self.tmp)
        code, _, err = run_main(["--process", str(process), "--sources", str(sources), "--sources",
                                 str(process.parent / "calls"), "--out", str(self.out), "--generated-at", GENERATED_AT,
                                 "--call-graph", "--history"])
        self.assertEqual(0, code, err)
        data = json.loads(self.out.read_text(encoding="utf-8"))
        self.assertEqual(STATE_KEYS | OPTIONAL_KEYS, set(data))
        self.assertTrue(data["callGraph"]["functions"])
        self.assertEqual(sorted(data["callGraph"]["parsedFiles"]), data["callGraph"]["parsedFiles"])
        self.assertIn("callGraph", data["meta"]["summaries"])
        self.assertIn("history", data["meta"]["summaries"])

    def test_RQ_TRC_129_given_a_fixed_date_when_run_twice_then_the_two_files_are_byte_identical(self):
        self.written()
        first = self.out.read_bytes()
        self.written()
        self.assertEqual(first, self.out.read_bytes())

    def test_RQ_TRC_129_given_a_missing_source_folder_then_it_exits_1_and_writes_nothing(self):
        code, _, err = run_main(["--process", str(PROCESS), "--sources", str(self.tmp / "absent"),
                                 "--out", str(self.out)])
        self.assertEqual(1, code)
        self.assertIn("source folder not found", err)
        self.assertFalse(self.out.exists())

    def test_RQ_TRC_129_given_a_process_folder_without_index_then_it_exits_1_and_writes_nothing(self):
        code, _, err = run_main(["--process", str(self.tmp), "--sources", str(SOURCES), "--out", str(self.out)])
        self.assertEqual(1, code)
        self.assertIn(agnos_layout.INDEX, err)
        self.assertFalse(self.out.exists())

    def test_RQ_TRC_129_given_no_out_option_then_the_graph_is_written_to_the_knowledge_folder(self):
        process = self.tmp / "process"
        shutil.copytree(PROCESS, process)
        code, stdout, err = run_main(["--process", str(process), "--sources", str(SOURCES)])
        self.assertEqual(0, code, err)
        self.assertTrue((process / agnos_layout.GRAPH_FILE).is_file())
        self.assertIn("agnos-graph:", stdout.strip().splitlines()[-1])


class StateDateTest(unittest.TestCase):
    """TASK-TRC-117: RQ-TRC-130 (DEC-TRC-074)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="agnos-graph-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.out = self.tmp / "graph.json"

    def meta_of(self, process, sources, *extra):
        code, _, err = run_main(["--process", str(process), "--sources", str(sources), "--out", str(self.out),
                                 "--generated-at", GENERATED_AT, *extra])
        self.assertEqual(0, code, err)
        return json.loads(self.out.read_text(encoding="utf-8"))["meta"]

    def test_RQ_TRC_130_given_a_git_repository_then_meta_holds_the_date_the_head_commit_and_the_scan(self):
        process, sources, head = committed_fixture(self.tmp)
        meta = self.meta_of(process, sources, "--ext", ".py", "--exclude", "dist")
        self.assertEqual(GENERATED_AT, meta["generatedAt"])
        self.assertEqual(head, meta["commit"])
        self.assertEqual(process.as_posix(), meta["process"])
        self.assertEqual([sources.as_posix()], meta["sources"])
        self.assertEqual([".py"], meta["extensions"])
        self.assertEqual(["dist"], meta["excludes"])
        self.assertEqual(sorted(graph.DEFAULT_NAMES), meta["names"])

    def test_RQ_TRC_130_given_the_default_scan_lists_then_meta_holds_them(self):
        meta = self.meta_of(PROCESS, SOURCES)
        self.assertEqual(sorted(graph.DEFAULT_EXTENSIONS), meta["extensions"])
        self.assertEqual(list(graph.DEFAULT_EXCLUDES), meta["excludes"])

    def test_RQ_TRC_130_given_a_folder_outside_git_then_commit_is_null_and_the_graph_is_written(self):
        process = self.tmp / "process"
        sources = self.tmp / "src"
        shutil.copytree(PROCESS, process)
        shutil.copytree(SOURCES, sources)
        with mock.patch.dict(os.environ, {"GIT_CEILING_DIRECTORIES": str(self.tmp)}):
            meta = self.meta_of(process, sources)
        self.assertIsNone(meta["commit"])


class IndependenceTest(unittest.TestCase):
    """TASK-TRC-117: RQ-TRC-133, RQ-TRC-039 (DEC-TRC-074): the graph script needs only the standard library."""

    def test_RQ_TRC_133_given_the_graph_script_then_it_imports_only_the_standard_library_and_its_own_modules(self):
        import ast
        tree = ast.parse((HERE.parent / "scripts" / "graph.py").read_text(encoding="utf-8"))
        imported = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        imported |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
        self.assertEqual({"agnos_layout"}, imported - set(sys.stdlib_module_names))


if __name__ == "__main__":
    unittest.main()
