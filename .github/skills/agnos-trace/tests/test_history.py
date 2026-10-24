"""Tests of the contribution history of agnos-trace (FTR-HST-001, ADR-HST-001), on small git repositories built in a
temporary folder.

Run from the repository root: python -m unittest discover -s .github/skills/agnos-trace/tests -v
Every git command of these tests runs with an empty global configuration, so the user's own never applies.
"""
import ast
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

import history  # noqa: E402

HUMAN = "human"
AGENT = "agent"
TOGETHER = "together"
SPASHX_MAIL = "25369377+spashx@users.noreply.github.com"
CLAUDE = "Claude Opus 5.5 <noreply@anthropic.com>"
DAY = "2026-10-{:02d}T10:00:00+00:00"


class GitRepo:
    """A git repository in a temporary folder, whose commits are made with given authors, dates and trailers."""

    def __init__(self, folder):
        self.top = Path(folder)
        self.top.mkdir(parents=True, exist_ok=True)
        self.git("init", "-q", "-b", "main")
        self.day = 0

    def git(self, *args, env=None):
        full = dict(os.environ, **(env or {}))
        return subprocess.run(["git", *args], cwd=self.top, env=full, check=True, capture_output=True,
                              text=True, encoding="utf-8").stdout

    def write(self, path, text):
        target = self.top / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")

    def commit(self, files, author="Alice <alice@example.com>", message="change", co_authors=(),
               committer=None):
        for path, text in files.items():
            self.write(path, text)
        self.git("add", "-A")
        self.day += 1
        name, _, mail = author.partition(" <")
        committer_name, _, committer_mail = (committer or author).partition(" <")
        body = message + ("\n\n" + "\n".join(f"Co-Authored-By: {c}" for c in co_authors) if co_authors else "")
        self.git("commit", "-q", "-m", body, env={
            "GIT_AUTHOR_NAME": name, "GIT_AUTHOR_EMAIL": mail.rstrip(">"), "GIT_AUTHOR_DATE": DAY.format(self.day),
            "GIT_COMMITTER_NAME": committer_name, "GIT_COMMITTER_EMAIL": committer_mail.rstrip(">"),
            "GIT_COMMITTER_DATE": DAY.format(self.day)})


def setUpModule():
    folder = tempfile.mkdtemp(prefix="agnos-history-config-")
    empty = Path(folder) / "gitconfig"
    empty.write_text("[init]\n\tdefaultBranch = main\n", encoding="utf-8")
    patcher = mock.patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": str(empty), "GIT_CONFIG_NOSYSTEM": "1"})
    patcher.start()
    unittest.addModuleCleanup(patcher.stop)
    unittest.addModuleCleanup(shutil.rmtree, folder, ignore_errors=True)


class RepoTestCase(unittest.TestCase):
    def setUp(self):
        self.folder = Path(tempfile.mkdtemp(prefix="agnos-history-"))
        self.addCleanup(shutil.rmtree, self.folder, ignore_errors=True)
        self.repo = GitRepo(self.folder / "repo")

    def people(self, patterns=None):
        repo = history.check_repository(self.repo.top)
        commits = history.read_commits(repo)
        return history.identify(repo, commits, patterns or history.load_agent_patterns())


class RepositoryCheckTest(RepoTestCase):
    """TASK-HST-001: RQ-HST-012."""

    def test_RQ_HST_012_given_a_folder_outside_git_then_the_check_names_the_cause(self):
        outside = Path(tempfile.mkdtemp(prefix="agnos-history-outside-", dir=os.environ.get("TEMP")))
        self.addCleanup(shutil.rmtree, outside, ignore_errors=True)
        with mock.patch.dict(os.environ, {"GIT_CEILING_DIRECTORIES": str(outside.parent)}):
            with self.assertRaises(history.HistoryUnavailable) as raised:
                history.check_repository(outside)
        self.assertIn("not inside a git working tree", str(raised.exception))

    def test_RQ_HST_012_given_a_repository_with_no_commit_then_the_check_names_the_cause(self):
        with self.assertRaises(history.HistoryUnavailable) as raised:
            history.check_repository(self.repo.top)
        self.assertIn("no commit", str(raised.exception))

    def test_RQ_HST_012_given_no_git_command_then_the_check_names_the_cause(self):
        with mock.patch.object(history.subprocess, "run", side_effect=FileNotFoundError("git")):
            with self.assertRaises(history.HistoryUnavailable) as raised:
                history.check_repository(self.repo.top)
        self.assertIn("git is not installed", str(raised.exception))

    def test_RQ_HST_012_given_a_shallow_clone_then_it_is_reported_shallow(self):
        for n in range(3):
            self.repo.commit({"a.txt": f"{n}\n"})
        full = history.check_repository(self.repo.top)
        self.assertFalse(full.shallow)
        clone = self.folder / "clone"
        subprocess.run(["git", "clone", "-q", "--depth", "1", self.repo.top.resolve().as_uri(), str(clone)], check=True,
                       capture_output=True)
        self.assertTrue(history.check_repository(clone).shallow)

    def test_RQ_HST_012_given_a_sub_folder_then_the_top_of_the_working_tree_is_found(self):
        self.repo.commit({"process/a.md": "x\n"})
        self.assertEqual(self.repo.top.resolve(), history.check_repository(self.repo.top / "process").top.resolve())


class IdentityTest(RepoTestCase):
    """TASK-HST-001: RQ-HST-004."""

    def test_RQ_HST_004_given_two_names_of_one_e_mail_then_they_are_one_identity_merged_by_e_mail(self):
        self.repo.commit({"a.txt": "1\n"}, author=f"spashx <{SPASHX_MAIL}>")
        self.repo.commit({"a.txt": "2\n"}, author=f"spashx <{SPASHX_MAIL}>")
        self.repo.commit({"a.txt": "3\n"}, author=f"{SPASHX_MAIL} <{SPASHX_MAIL.upper()}>")
        people, _ = self.people()
        self.assertEqual(1, len(people))
        person = people[0]
        self.assertEqual("spashx", person["name"])
        self.assertEqual(sorted(["spashx", SPASHX_MAIL]), person["names"])
        self.assertEqual([history.MERGED_BY_EMAIL], person["mergedBy"])
        self.assertEqual(3, person["commits"])
        self.assertEqual(HUMAN, person["kind"])

    def test_RQ_HST_004_given_a_merge_committed_by_a_hosting_service_then_the_service_is_no_identity(self):
        self.repo.commit({"a.txt": "1\n"})
        self.repo.git("checkout", "-q", "-b", "side")
        self.repo.commit({"b.txt": "1\n"}, author="Bob <bob@example.com>")
        self.repo.git("checkout", "-q", "main")
        self.repo.commit({"c.txt": "1\n"})
        self.repo.git("merge", "-q", "--no-ff", "-m", "Merge pull request #1", "side", env={
            "GIT_AUTHOR_NAME": "Alice", "GIT_AUTHOR_EMAIL": "alice@example.com",
            "GIT_COMMITTER_NAME": "GitHub", "GIT_COMMITTER_EMAIL": "noreply@github.com"})
        people, _ = self.people()
        self.assertEqual(["Alice", "Bob"], sorted(p["name"] for p in people))

    def test_RQ_HST_004_given_a_mailmap_then_the_mapped_commits_are_one_identity_merged_by_mailmap(self):
        self.repo.commit({"a.txt": "1\n"}, author="nina <n@old.example>")
        self.repo.commit({".mailmap": "Nina Dev <n@new.example> nina <n@old.example>\n", "a.txt": "2\n"},
                         author="Nina Dev <n@new.example>")
        people, _ = self.people()
        self.assertEqual(1, len(people))
        self.assertEqual("Nina Dev", people[0]["name"])
        self.assertIn(history.MERGED_BY_MAILMAP, people[0]["mergedBy"])
        self.assertIn("nina", people[0]["names"])
        self.assertIn("n@old.example", people[0]["emails"])

    def test_RQ_HST_004_given_a_tie_of_names_then_the_display_name_is_stable(self):
        self.repo.commit({"a.txt": "1\n"}, author="Zed <z@example.com>")
        self.repo.commit({"a.txt": "2\n"}, author="Ann <Z@example.com>")
        first, _ = self.people()
        second, _ = self.people()
        self.assertEqual("Ann", first[0]["name"])
        self.assertEqual(first, second)


class AgentTest(RepoTestCase):
    """TASK-HST-001: RQ-HST-005."""

    def test_RQ_HST_005_given_an_agent_co_author_then_the_commit_has_two_contributors_and_is_together(self):
        self.repo.commit({"a.txt": "1\n"}, author=f"spashx <{SPASHX_MAIL}>", co_authors=[CLAUDE])
        people, commits = self.people()
        by_name = {p["name"]: p for p in people}
        self.assertEqual(HUMAN, by_name["spashx"]["kind"])
        self.assertEqual(AGENT, by_name["Claude Opus 5.5"]["kind"])
        self.assertEqual(1, by_name["Claude Opus 5.5"]["coCommits"])
        self.assertEqual(0, by_name["Claude Opus 5.5"]["commits"])
        commit = commits[0]
        self.assertEqual(TOGETHER, commit["kind"])
        self.assertEqual("spashx", people[commit["author"]]["name"])
        self.assertEqual(["Claude Opus 5.5"], [people[i]["name"] for i in commit["coAuthors"]])

    def test_RQ_HST_004_given_two_agents_sharing_a_no_reply_address_then_they_are_two_identities(self):
        self.repo.commit({"a.txt": "1\n"}, co_authors=[CLAUDE])
        self.repo.commit({"a.txt": "2\n"}, co_authors=["Claude Sonnet 5.5 <noreply@anthropic.com>"])
        self.repo.commit({"a.txt": "3\n"}, co_authors=["claude opus 5.5 <NoReply@anthropic.com>"])
        people, _ = self.people()
        agents = {p["name"]: p for p in people if p["kind"] == AGENT}
        self.assertEqual(["Claude Opus 5.5", "Claude Sonnet 5.5"], sorted(agents))
        self.assertEqual(2, agents["Claude Opus 5.5"]["coCommits"])

    def test_RQ_HST_005_given_a_lower_case_trailer_then_the_co_author_is_read(self):
        self.repo.commit({"a.txt": "1\n"}, message="x\n\nco-authored-by: Claude Sonnet 5.5 <noreply@anthropic.com>")
        people, commits = self.people()
        self.assertIn("Claude Sonnet 5.5", [p["name"] for p in people])
        self.assertEqual(TOGETHER, commits[0]["kind"])

    def test_RQ_HST_005_given_a_bot_author_then_the_commit_is_an_agent_commit(self):
        self.repo.commit({"a.txt": "1\n"}, author="dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>")
        people, commits = self.people()
        self.assertEqual(AGENT, people[0]["kind"])
        self.assertEqual(AGENT, commits[0]["kind"])

    def test_RQ_HST_005_given_a_human_alone_then_the_commit_is_a_human_commit(self):
        self.repo.commit({"a.txt": "1\n"}, author="Bob <bob@example.com>")
        _, commits = self.people()
        self.assertEqual(HUMAN, commits[0]["kind"])

    def test_RQ_HST_005_given_other_patterns_then_the_classing_follows_with_no_change_of_code(self):
        self.repo.commit({"a.txt": "1\n"}, author="Robo <robo@factory.example>")
        patterns = history.compile_agent_patterns({"name": [], "email": [r"@factory\.example$"]})
        people, _ = self.people(patterns)
        self.assertEqual(AGENT, people[0]["kind"])

    def test_RQ_HST_005_given_the_skill_patterns_file_then_it_names_the_usual_assistants(self):
        patterns = history.load_agent_patterns()
        for name, mail in (("Claude Opus 5.5", "noreply@anthropic.com"), ("Copilot", "copilot@github.com"),
                           ("github-actions[bot]", "41898282+github-actions[bot]@users.noreply.github.com")):
            self.assertTrue(patterns.is_agent(name, mail), name)
        self.assertFalse(patterns.is_agent("Claudette Martin", "claudette@example.com"))


def numbered(first, last, tag="line"):
    return "".join(f"{tag} {n}\n" for n in range(first, last + 1))


FEATURE = "process/FTR-A.md"
ALICE = "Alice <alice@example.com>"
BOB = "Bob <bob@example.com>"
CAROL = "Carol <carol@example.com>"


class LineTrackingTest(RepoTestCase):
    """TASK-HST-002: RQ-HST-001, RQ-HST-002, RQ-HST-003."""

    def setUp(self):
        super().setUp()
        # RQ-A on lines 5 to 10, RQ-B on lines 12 to 20, written by Carol
        self.lines = numbered(1, 20).splitlines(keepends=True)
        self.repo.commit({FEATURE: "".join(self.lines)}, author=CAROL, message="feature")

    def change(self, number, text, author, path=FEATURE, message="change"):
        self.lines[number - 1] = text + "\n"
        self.repo.commit({path: "".join(self.lines)}, author=author, message=message)

    def credits(self, ranges, wholes=None, **limits):
        repo = history.check_repository(self.repo.top)
        commits, credited = history.read_history(repo, ranges, wholes or {}, **limits)
        names = {c["hash"]: c["author"][0] for c in commits}
        return commits, {key: {names[h]: lines for h, lines in by.items()} for key, by in credited.items()}

    def test_RQ_HST_002_given_a_commit_on_one_line_of_rq_a_then_it_is_credited_to_rq_a_only(self):
        self.change(7, "changed by Alice", ALICE)
        _, credits = self.credits({FEATURE: [("RQ-A", 5, 10), ("RQ-B", 12, 20)]})
        self.assertEqual({"Carol": 6, "Alice": 2}, credits["RQ-A"])
        self.assertEqual({"Carol": 9}, credits["RQ-B"])

    def test_RQ_HST_002_given_lines_inserted_above_later_then_the_earlier_credit_stays_on_rq_a(self):
        self.change(7, "changed by Alice", ALICE)
        self.lines[0:0] = ["new 1\n", "new 2\n", "new 3\n"]
        self.repo.commit({FEATURE: "".join(self.lines)}, author=BOB)
        _, credits = self.credits({FEATURE: [("RQ-A", 8, 13), ("RQ-B", 15, 23)]})
        self.assertEqual({"Carol", "Alice"}, set(credits["RQ-A"]))
        self.assertNotIn("Bob", credits["RQ-B"])

    def test_RQ_HST_002_given_the_file_renamed_then_the_credit_is_kept(self):
        self.change(7, "changed by Alice", ALICE)
        self.repo.git("mv", FEATURE, "process/FTR-A-renamed.md")
        self.repo.commit({}, author=BOB, message="rename")
        _, credits = self.credits({"process/FTR-A-renamed.md": [("RQ-A", 5, 10)]})
        self.assertEqual({"Carol": 6, "Alice": 2}, credits["RQ-A"])

    def test_RQ_HST_002_given_a_side_branch_merged_then_its_commit_is_credited_and_the_merge_is_not(self):
        self.repo.git("checkout", "-q", "-b", "side")
        self.change(15, "changed by Bob on a branch", BOB)
        self.repo.git("checkout", "-q", "main")
        self.lines[14] = "line 15\n"
        self.change(7, "changed by Alice on main", ALICE)
        self.repo.git("merge", "-q", "--no-ff", "-m", "merge side", "side", env={
            "GIT_AUTHOR_NAME": "Dan", "GIT_AUTHOR_EMAIL": "dan@example.com",
            "GIT_COMMITTER_NAME": "Dan", "GIT_COMMITTER_EMAIL": "dan@example.com"})
        commits, credits = self.credits({FEATURE: [("RQ-A", 5, 10), ("RQ-B", 12, 20)]})
        self.assertEqual({"Carol": 6, "Alice": 2}, credits["RQ-A"])
        self.assertEqual({"Carol": 9, "Bob": 2}, credits["RQ-B"])
        self.assertIn("Dan", {c["author"][0] for c in commits})          # walked, never credited

    def test_RQ_HST_002_given_an_uncommitted_change_then_it_credits_no_one(self):
        self.change(7, "changed by Alice", ALICE)
        self.repo.write(FEATURE, "top 1\ntop 2\n" + "".join(self.lines).replace("line 15", "uncommitted"))
        _, credits = self.credits({FEATURE: [("RQ-A", 7, 12), ("RQ-B", 14, 22)]})
        self.assertEqual({"Carol": 6, "Alice": 2}, credits["RQ-A"])
        self.assertEqual({"Carol": 9}, credits["RQ-B"])

    def test_RQ_HST_002_given_a_range_added_by_a_commit_then_the_tracking_stops_there(self):
        self.lines[20:] = ["new rq " + str(n) + "\n" for n in range(1, 4)]
        self.repo.commit({FEATURE: "".join(self.lines)}, author=ALICE, message="RQ-C")
        _, credits = self.credits({FEATURE: [("RQ-C", 21, 23)]})
        self.assertEqual({"Alice": 3}, credits["RQ-C"])

    def test_RQ_HST_003_given_two_functions_and_a_commit_on_g_then_it_is_credited_to_g_and_the_file(self):
        code = "src/app.py"
        body = ["def f():\n", "    return 1\n", "\n", "\n", "def g():\n", "    return 2\n"]
        self.repo.commit({code: "".join(body)}, author=CAROL)
        body[5] = "    return 3\n"
        self.repo.commit({code: "".join(body)}, author=BOB)
        _, credits = self.credits({code: [("f", 1, 2), ("g", 5, 6)]}, {code: ["file"]})
        self.assertEqual({"Carol": 2}, credits["f"])
        self.assertEqual({"Carol": 2, "Bob": 2}, credits["g"])
        self.assertEqual({"Carol": 6, "Bob": 2}, credits["file"])

    def test_RQ_HST_001_given_a_depth_then_only_that_many_commits_are_read(self):
        for n in range(4):
            self.change(6, f"edit {n}", ALICE)
        commits, _ = self.credits({FEATURE: [("RQ-A", 5, 10)]}, depth=2)
        self.assertEqual(2, len(commits))

    def test_RQ_HST_001_given_a_since_date_then_only_the_commits_authored_since_are_read(self):
        for n in range(4):
            self.change(6, f"edit {n}", ALICE)                   # authored on days 2 to 5
        commits, credits = self.credits({FEATURE: [("RQ-A", 5, 10)]}, since="2026-10-04T00:00:00+00:00")
        self.assertEqual(2, len(commits))
        self.assertNotIn("Carol", credits["RQ-A"])

    def test_RQ_HST_002_given_the_same_repository_twice_then_the_result_is_equal(self):
        self.change(7, "changed by Alice", ALICE)
        ranges = {FEATURE: [("RQ-A", 5, 10), ("RQ-B", 12, 20)]}
        first, second = self.credits(ranges), self.credits(ranges)
        self.assertEqual(first, second)

    def test_RQ_HST_002_given_a_line_that_looks_like_a_diff_header_then_the_counts_are_right(self):
        self.change(7, "++ b/elsewhere", ALICE)
        self.change(8, "-- a/elsewhere\r", BOB)
        _, credits = self.credits({FEATURE: [("RQ-A", 5, 10)]})
        self.assertEqual({"Carol": 6, "Alice": 2, "Bob": 2}, credits["RQ-A"])


class IndependenceTest(unittest.TestCase):
    """TASK-HST-001: RQ-HST-015."""

    def test_RQ_HST_015_given_the_history_module_then_it_imports_only_the_standard_library(self):
        tree = ast.parse((HERE.parent / "scripts" / "history.py").read_text(encoding="utf-8"))
        imported = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)
                    for alias in node.names}
        imported |= {node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertEqual(set(), imported - set(sys.stdlib_module_names))


if __name__ == "__main__":
    unittest.main()
