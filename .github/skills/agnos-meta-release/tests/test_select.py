"""Tests of what the release rehearsal selects, and of what it leaves alone (RQ-MTA-006 to RQ-MTA-008, TASK-MTA-005;
ADR-MTA-002: DEC-MTA-007, DEC-MTA-008, DEC-MTA-011).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-meta-release/tests -v
"""
import contextlib
import filecmp
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import release  # noqa: E402
import agnos_layout  # noqa: E402  RQ-PLG-036: the process folder's names, as the scripts read them

ROOT = HERE.parents[3]
EXIT_OK = 0
EXIT_FAILED = 1
TOOLKIT_FILE = "README.md"
SKILL_FILE = ".github/skills/agnos-index/SKILL.md"
SKILL_PLACE = "plugins/agnos/skills/agnos-index/SKILL.md"
PROCESS_PLACE = "plugins/agnos/skills/agnos-instructions/SKILL.md"     # RQ-PLG-035
INSTRUCTIONS_FILE = ".github/instructions/agnos-sw-eng.instructions.md"
CHANGELOG_FILE = "CHANGELOG.md"
VERSION_FILE = ".github/skills/agnos-init/assets/templates/VERSION.txt"     # RQ-PLG-032: the version's single source
VERSION_PLACE = "plugins/agnos/skills/agnos-init/assets/templates/VERSION.txt"
GENERATED = (".claude-plugin/marketplace.json", ".gitattributes",     # RQ-PLG-043 / DEC-PLG-033: no Codex catalogue
             "plugins/agnos/.claude-plugin/plugin.json", "plugins/agnos/plugin.json")
SKILL_TEST = ".github/skills/agnos-index/tests/test_a.py"
META_SKILL = ".github/skills/agnos-meta-other/SKILL.md"
PROCESS_FILE = f"{agnos_layout.FOLDER}/{agnos_layout.INDEX}"
SETTINGS = ".claude/settings.json"
UNKNOWN_FILE = "stray.txt"
PUBLIC_FILES = ("LICENSE.md", ".gitignore")
TOOLKIT_FILES = ("README.md", "COMPATIBILITY.md", ".github/skills/agnos-init/assets/templates/AGNOS-GETTING-STARTED.md", "CHANGELOG.md", "agnos-overview.png",
                 ".github/instructions/agnos-sw-eng.instructions.md", ".github/skills/agnos-init/SKILL.md")
WORKSHOP_FILES = ("CLAUDE.md", "AGENTS.md", "SECURITY.md", "CODE_OF_CONDUCT.md", "CONTRIBUTING.md", ".github/ISSUE_TEMPLATE.md",
                  ".github/PULL_REQUEST_TEMPLATE.md", ".gitattributes", ".claude/skills/agnos-init/SKILL.md")
REPORT_SUFFIX = ".report.json"
INDEX_TEXT = "RQ-ABC-001|1-2||A requirement\n"


def git(repo, *args):
    done = subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.org",
                           "-c", "core.autocrlf=false", *args],
                          capture_output=True, text=True, encoding="utf-8", check=True)
    return done.stdout.strip()


def files_under(folder):
    return sorted(p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file())


def no_proof(repo, output, demo):
    """These test repositories have no demo: the proof has its own tests (RQ-MTA-011)."""
    return []


def run(*args):
    """The script's exit code and error stream, its normal output kept quiet."""
    errors = io.StringIO()
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(errors):
        code = release.main([str(a) for a in args], proof=no_proof)
    return code, errors.getvalue()


class RehearsalCase(unittest.TestCase):
    def setUp(self):
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.base = Path(holder.name)
        self.repo = self.base / "repo"
        self.output = self.base / "out"
        self.repo.mkdir()
        git(self.repo, "init", "-q")
        self.commit({TOOLKIT_FILE: "# Toolkit\n", SKILL_FILE: "skill\n", SKILL_TEST: "test\n", META_SKILL: "meta\n",
                     PROCESS_FILE: INDEX_TEXT, SETTINGS: "{}\n", INSTRUCTIONS_FILE: "# Process\n", CHANGELOG_FILE: "## [v1.2]\n",
                     VERSION_FILE: "1.2.0\n"})

    def commit(self, files):
        for name, text in files.items():
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-q", "-m", "commit")

    def rehearse(self, output=None):
        return run("--repo", self.repo, "--dry-run", "--output", output or self.output)

    def state(self):
        return (git(self.repo, "status", "--porcelain"), git(self.repo, "rev-parse", "HEAD"),
                git(self.repo, "branch", "--list"), git(self.repo, "tag", "--list"))


class NothingElseChangesTest(RehearsalCase):
    """RQ-MTA-006."""

    def test_RQ_MTA_006_given_a_repository_when_the_rehearsal_runs_then_its_status_branches_tags_and_head_stay(self):
        before = self.state()
        code, _ = self.rehearse()
        self.assertEqual(EXIT_OK, code)
        self.assertEqual(before, self.state())

    def test_RQ_MTA_006_given_an_output_inside_the_repository_when_it_runs_then_it_exits_1_and_writes_nothing(self):
        inside = self.repo / "out"
        code, errors = self.rehearse(inside)
        self.assertEqual(EXIT_FAILED, code)
        self.assertIn("inside the repository", errors)
        self.assertFalse(inside.exists())

    def test_RQ_MTA_006_given_an_output_not_empty_when_it_runs_then_it_exits_1_and_writes_nothing(self):
        self.output.mkdir()
        (self.output / "kept.txt").write_text("kept", encoding="utf-8")
        code, errors = self.rehearse()
        self.assertEqual(EXIT_FAILED, code)
        self.assertIn("not empty", errors)
        self.assertEqual(["kept.txt"], files_under(self.output))

    def test_RQ_MTA_006_given_no_dry_run_when_it_runs_then_it_exits_1_says_so_and_writes_nothing(self):
        code, errors = run("--repo", self.repo, "--output", self.output)
        self.assertEqual(EXIT_FAILED, code)
        self.assertIn("--dry-run", errors)
        self.assertFalse(self.output.exists())


    def test_RQ_MTA_006_given_a_folder_that_is_no_repository_when_it_runs_then_it_exits_1_and_writes_nothing(self):
        plain = self.base / "plain"
        plain.mkdir()
        code, errors = run("--repo", plain, "--dry-run", "--output", self.output)
        self.assertEqual(EXIT_FAILED, code)
        self.assertIn("not a git repository", errors)
        self.assertFalse(self.output.exists())


class FromACommitTest(RehearsalCase):
    """RQ-MTA-007."""

    def test_RQ_MTA_007_given_an_untracked_file_and_an_edit_when_it_runs_then_neither_is_in_the_output(self):
        (self.repo / "untracked.md").write_text("untracked\n", encoding="utf-8")
        (self.repo / TOOLKIT_FILE).write_text("uncommitted\n", encoding="utf-8")
        self.assertEqual(EXIT_OK, self.rehearse()[0])
        self.assertNotIn("untracked.md", files_under(self.output))
        self.assertEqual("# Toolkit\n", (self.output / TOOLKIT_FILE).read_text(encoding="utf-8"))

    def test_RQ_MTA_007_given_one_commit_when_it_runs_twice_then_both_outputs_are_the_same_and_the_report_has_the_hash(self):
        second = self.base / "second"
        self.assertEqual(EXIT_OK, self.rehearse()[0])
        self.assertEqual(EXIT_OK, self.rehearse(second)[0])
        names = files_under(self.output)
        self.assertEqual(names, files_under(second))
        self.assertEqual([], filecmp.cmpfiles(self.output, second, names, shallow=False)[1])
        report = json.loads(Path(f"{self.output}{REPORT_SUFFIX}").read_text(encoding="utf-8"))
        self.assertEqual(git(self.repo, "rev-parse", "HEAD"), report["commit"])


class LayersTest(RehearsalCase):
    """RQ-MTA-008."""

    def test_RQ_MTA_008_given_the_rules_then_the_meta_layer_is_left_out_and_the_rest_delivered(self):
        self.assertEqual(EXIT_OK, self.rehearse()[0])
        self.assertEqual(sorted((CHANGELOG_FILE, PROCESS_PLACE, SKILL_PLACE, TOOLKIT_FILE, VERSION_PLACE) + GENERATED), files_under(self.output))
        report = json.loads(Path(f"{self.output}{REPORT_SUFFIX}").read_text(encoding="utf-8"))
        self.assertEqual(sorted([SKILL_TEST, META_SKILL, PROCESS_FILE, SETTINGS]), sorted(report["leftOut"]))

    def test_RQ_MTA_008_given_a_tracked_file_matching_no_rule_when_it_runs_then_it_exits_1_names_it_and_delivers_nothing(self):
        self.commit({UNKNOWN_FILE: "stray\n"})
        code, errors = self.rehearse()
        self.assertEqual(EXIT_FAILED, code)
        self.assertIn(UNKNOWN_FILE, errors)
        self.assertFalse(self.output.exists())

    def test_RQ_MTA_002_given_a_skill_or_agent_with_the_prefix_then_it_is_meta_without_any_list_of_names(self):
        rules = release.load_rules()
        for path in (".github/skills/agnos-meta-new/x.py", ".claude/skills/agnos-meta-new/SKILL.md", ".claude/agents/agnos-meta-new.md"):
            self.assertEqual(release.LAYER_META, release.layer_of(path, rules), path)

    def test_RQ_MTA_008_given_an_agent_in_github_then_its_prefix_decides_its_layer(self):
        rules = release.load_rules()
        self.assertEqual(release.LAYER_META, release.layer_of(".github/agents/agnos-meta-new.agent.md", rules))
        self.assertEqual(release.LAYER_DELIVERED, release.layer_of(".github/agents/agnos-new.agent.md", rules))

    def test_RQ_PLG_022_given_a_guide_at_the_root_then_it_has_no_layer_so_the_release_refuses_it(self):
        self.assertIsNone(release.layer_of("GETTING_STARTED.MD", release.load_rules()))

    def test_RQ_MTA_008_given_this_repository_then_every_tracked_file_has_a_layer_and_the_delivered_ones_are_right(self):
        rules = release.load_rules()
        layers = {path: release.layer_of(path, rules) for path, _ in release.tracked_files(ROOT)}
        self.assertEqual([], [path for path, layer in layers.items() if layer is None])
        delivered = {path for path, layer in layers.items() if layer == release.LAYER_DELIVERED}
        for path in PUBLIC_FILES + TOOLKIT_FILES:
            self.assertIn(path, delivered)
        for path in WORKSHOP_FILES:
            self.assertNotIn(path, delivered)
        for path in delivered:
            self.assertFalse(path.startswith(f"{agnos_layout.FOLDER}/"), path)
            self.assertNotIn("agnos-meta-", path)
            self.assertNotIn("/tests/", path)
            self.assertNotEqual(SETTINGS, path)


if __name__ == "__main__":
    unittest.main()
