"""Tests of agnos-session: each case runs both scripts on the same files (FTR-INI-002, TASK-INI-006; ADR-INI-002).

Run from the repository root: python -m unittest discover -s .github/skills/agnos-session/tests -v
The sh version is run by `bash` started from Git Bash when found, else from `bash` on the PATH; set AGNOS_BASH to choose another one.
Linux, macOS and PowerShell 7 are simulated (a fake `uname`, a preset `IsLinux` or `IsMacOS`); only the host's platform runs for real.
"""
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
ROOT = SKILL_DIR.parents[2]
PS_SCRIPT = SKILL_DIR / "scripts" / "session.ps1"
SH_SCRIPT = SKILL_DIR / "scripts" / "session.sh"
GIT_BASH = Path(r"C:\Program Files\Git\bin\bash.exe")
SKILL_NAME = "agnos-session"
ENTRY_FILES = ("CLAUDE.md", "AGENTS.md")
MAX_DESCRIPTION = 1024
MAX_SKILL_LINES = 500
# RQ-INI-018 / DEC-PLG-027: the paths come from the layout the scripts' copies are generated from.
LAYOUT = json.loads((ROOT / ".github/skills/agnos-init/assets/layout.json").read_text(encoding="utf-8"))
FOLDER = LAYOUT["folder"]
STATE = f"{FOLDER}/{LAYOUT['sessionState']}"
LOG = f"{FOLDER}/{LAYOUT['metricsLog']}"
# RQ-INI-015 / DEC-TRC-045: the row is checked against the pattern agnos-perf-center reads it with.
sys.path.insert(0, str(ROOT / ".github/skills/agnos-perf-center/scripts"))
from history import FRICTION_ROW_RE  # noqa: E402
LOG_HEADER = b"".join((ROOT / LOG).read_bytes().splitlines(keepends=True)[:4]).replace(b"\r\n", b"\n")
HOST_PLATFORM = {"Windows": "windows", "Linux": "linux", "Darwin": "macos"}[platform.system()]
PROJECT = {f"{FOLDER}/1.requirements/readme.md": b"# Requirements\n"}
FORMER_STATE = b"unit_tests: true\nplatform: windows\nextra: kept\n"
# RQ-INI-013: bash reads `uname -s` from the PATH, so a fake one placed first simulates another system.
SH_WRAPPER = ('fake=$(cygpath -u "$0" 2>/dev/null || printf %s "$0"); '
              '[ -n "$0" ] && [ "$0" != none ] && PATH="$fake:$PATH"; exec bash "$@"')
UNAME_CASES = {"Linux": "linux", "Darwin": "macos", "MINGW64_NT-10.0-26100": "windows",
               "MSYS_NT-10.0": "windows", "CYGWIN_NT-10.0": "windows"}
UNKNOWN_UNAME = "SunOS"
PS_CASES = {"IsLinux": "linux", "IsMacOS": "macos"}


def bash_command():
    configured = os.environ.get("AGNOS_BASH")
    if configured:
        return configured
    return str(GIT_BASH) if GIT_BASH.exists() else "bash"


def run_powershell(project, *arguments, preset=None):
    """Runs session.ps1; `preset` names an automatic variable set to true first, as PowerShell 7 does (RQ-INI-013)."""
    if preset is None:
        command = ["powershell", "-NoProfile", "-File", str(PS_SCRIPT), *arguments]
    else:
        quoted = " ".join(f"'{a}'" for a in arguments)
        command = ["powershell", "-NoProfile", "-Command",
                   f"${preset} = $true; & '{PS_SCRIPT}' {quoted}; exit $LASTEXITCODE"]
    return subprocess.run(command, cwd=project, capture_output=True, text=True, encoding="utf-8")


def run_sh(project, *arguments, fake_bin="none"):
    """Runs session.sh with bash, a fake `uname` first on the PATH when `fake_bin` is given (RQ-INI-013)."""
    return subprocess.run([bash_command(), "-c", SH_WRAPPER, str(fake_bin), SH_SCRIPT.as_posix(), *arguments],
                          cwd=project, capture_output=True, text=True, encoding="utf-8")


# RQ-PLG-008: a system runs the scripts it can; the two are compared where both run.
RUNNERS = {name: runner for name, tool, runner in (("powershell", "powershell", run_powershell), ("bash", bash_command(), run_sh))
           if shutil.which(tool)}


def snapshot(project):
    return {p.relative_to(project).as_posix(): p.read_bytes() for p in project.rglob("*") if p.is_file()}


def state(tri, tests, platform_name):
    return f"tri: {tri}\ntests: {tests}\nplatform: {platform_name}\n".encode()


class SessionCase(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp(prefix="agnos-session-"))
        self.addCleanup(shutil.rmtree, self.base, ignore_errors=True)

    def project(self, name, files=None):
        project = self.base / name
        project.mkdir()
        for path, data in {**PROJECT, **(files or {})}.items():
            target = project / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        return project

    def each_script(self, arguments, files=None):
        """Runs both scripts, checks they wrote the same bytes and said the same, returns (name, project, result) for each."""
        runs = []
        for name, runner in RUNNERS.items():
            project = self.project(name, files)
            runs.append((name, project, runner(project, *arguments)))
        for _, project, result in runs[1:]:
            self.assertEqual(snapshot(runs[0][1]), snapshot(project))
            self.assertEqual(runs[0][2].stdout, result.stdout)
        return runs


class InitTest(SessionCase):
    """RQ-INI-011, RQ-INI-012."""

    def test_RQ_INI_011_given_a_former_state_when_init_runs_then_the_file_holds_only_the_three_keys(self):
        for name, project, result in self.each_script(("init", "--tri", "ABC", "--tests", "false"), {STATE: FORMER_STATE}):
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(state("ABC", "false", HOST_PLATFORM), (project / STATE).read_bytes(), name)

    def test_RQ_INI_011_given_init_when_it_succeeds_then_it_prints_the_table_of_the_three_values(self):
        for name, _project, result in self.each_script(("init", "--tests", "true", "--tri", "XYZ")):
            self.assertEqual(0, result.returncode, result.stderr)
            for row in ("| tri | XYZ |", "| tests | true |", f"| platform | {HOST_PLATFORM} |"):
                self.assertIn(row, result.stdout, name)

    def test_RQ_INI_011_given_no_process_folder_when_init_runs_then_it_exits_1_and_writes_nothing(self):
        for name, runner in RUNNERS.items():
            project = self.base / f"{name}-empty"
            project.mkdir()
            result = runner(project, "init", "--tri", "ABC", "--tests", "true")
            self.assertEqual(1, result.returncode, name)
            self.assertEqual({}, snapshot(project), name)
            self.assertIn(FOLDER, result.stderr, name)

    def test_RQ_INI_012_given_invalid_arguments_when_init_runs_then_it_names_the_argument_and_changes_nothing(self):
        cases = {"lowercase trigram": (("--tri", "abc", "--tests", "true"), "--tri"),
                 "long trigram": (("--tri", "ABCD", "--tests", "true"), "--tri"),
                 "missing trigram": (("--tests", "true"), "--tri"),
                 "missing tests": (("--tri", "ABC"), "--tests"),
                 "tests yes": (("--tri", "ABC", "--tests", "yes"), "--tests"),
                 "unknown argument": (("--tri", "ABC", "--tests", "true", "--other", "x"), "--other")}
        for label, (arguments, named) in cases.items():
            for name, runner in RUNNERS.items():
                with self.subTest(case=label, script=name):
                    project = self.project(f"{name}-{label.replace(' ', '-')}", {STATE: FORMER_STATE})
                    result = runner(project, "init", *arguments)
                    self.assertEqual(1, result.returncode, result.stdout)
                    self.assertIn(named, result.stderr)
                    self.assertEqual(FORMER_STATE, (project / STATE).read_bytes())


class PlatformTest(SessionCase):
    """RQ-INI-013: simulated systems, the host's for real."""

    def fake_uname(self, output):
        folder = self.base / f"bin-{output}"
        folder.mkdir()
        (folder / "uname").write_bytes(f"#!/bin/sh\necho '{output}'\n".encode())
        (folder / "uname").chmod(0o755)
        return folder

    def test_RQ_INI_013_given_a_simulated_uname_when_bash_runs_then_the_platform_follows_it(self):
        if "bash" not in RUNNERS:
            self.skipTest("no bash on this system")
        for output, expected in UNAME_CASES.items():
            with self.subTest(uname=output):
                project = self.project(f"bash-{expected}-{output[:5]}")
                result = run_sh(project, "init", "--tri", "ABC", "--tests", "true", fake_bin=self.fake_uname(output))
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual(state("ABC", "true", expected), (project / STATE).read_bytes())

    def test_RQ_INI_013_given_an_unknown_uname_when_bash_runs_then_it_exits_1_and_writes_nothing(self):
        if "bash" not in RUNNERS:
            self.skipTest("no bash on this system")
        project = self.project("bash-unknown", {STATE: FORMER_STATE})
        result = run_sh(project, "init", "--tri", "ABC", "--tests", "true", fake_bin=self.fake_uname(UNKNOWN_UNAME))
        self.assertEqual(1, result.returncode, result.stdout)
        self.assertIn(UNKNOWN_UNAME, result.stderr)
        self.assertEqual(FORMER_STATE, (project / STATE).read_bytes())

    def test_RQ_INI_013_given_a_preset_automatic_variable_when_powershell_runs_then_the_platform_follows_it(self):
        if "powershell" not in RUNNERS:
            self.skipTest("no powershell on this system")
        for variable, expected in PS_CASES.items():
            with self.subTest(variable=variable):
                project = self.project(f"ps-{expected}")
                result = run_powershell(project, "init", "--tri", "ABC", "--tests", "true", preset=variable)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual(state("ABC", "true", expected), (project / STATE).read_bytes())


class ShowTest(SessionCase):
    """RQ-INI-014."""

    def test_RQ_INI_014_given_a_state_written_by_init_when_show_runs_then_it_prints_one_line(self):
        for name, runner in RUNNERS.items():
            project = self.project(f"{name}-show")
            self.assertEqual(0, runner(project, "init", "--tri", "ABC", "--tests", "false").returncode)
            result = runner(project, "show")
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(f"tri=ABC tests=false platform={HOST_PLATFORM}\n", result.stdout, name)

    def test_RQ_INI_014_given_no_state_when_show_runs_then_it_exits_1(self):
        for name, runner in RUNNERS.items():
            result = runner(self.project(f"{name}-nostate"), "show")
            self.assertEqual(1, result.returncode, name)
            self.assertIn(LAYOUT["sessionState"], result.stderr, name)


class CloseTest(SessionCase):
    """RQ-INI-015."""

    STATE_FILES = {STATE: state("ABC", "true", "windows")}

    def test_RQ_INI_015_given_no_log_when_close_runs_then_it_creates_the_header_and_one_readable_row(self):
        for name, project, result in self.each_script(("close", "1", "0", "0", "2"), self.STATE_FILES):
            self.assertEqual(0, result.returncode, result.stderr)
            data = (project / LOG).read_bytes()
            self.assertTrue(data.startswith(LOG_HEADER), name)
            rows = data[len(LOG_HEADER):].decode().splitlines()
            self.assertEqual(1, len(rows), name)
            match = FRICTION_ROW_RE.match(rows[0])
            self.assertIsNotNone(match, rows[0])
            self.assertEqual(("ABC", "1", "0", "0", "2"), match.groups()[1:])
            self.assertIn(rows[0], result.stdout, name)

    def test_RQ_INI_015_given_a_crlf_log_when_close_runs_then_only_one_crlf_line_is_added_at_its_end(self):
        former = LOG_HEADER.replace(b"\n", b"\r\n") + b"| 2026-01-01 | OLD | 0 | 0 | 0 | 0 |\r\n"
        for name, project, result in self.each_script(("close", "3", "1", "0", "0"), {**self.STATE_FILES, LOG: former}):
            self.assertEqual(0, result.returncode, result.stderr)
            data = (project / LOG).read_bytes()
            self.assertTrue(data.startswith(former), name)
            added = data[len(former):]
            self.assertEqual(1, added.count(b"\r\n"), name)
            self.assertTrue(added.endswith(b"\r\n"), name)
            self.assertIsNotNone(FRICTION_ROW_RE.match(added.decode().rstrip()), name)

    def test_RQ_INI_015_given_an_invalid_counter_or_no_state_when_close_runs_then_it_exits_1_and_writes_nothing(self):
        former = LOG_HEADER
        cases = {"letter": (("1", "x", "0", "0"), self.STATE_FILES),
                 "negative": (("1", "-1", "0", "0"), self.STATE_FILES),
                 "three counters": (("1", "0", "0"), self.STATE_FILES),
                 "no state": (("1", "0", "0", "0"), {})}
        for label, (counters, files) in cases.items():
            for name, runner in RUNNERS.items():
                with self.subTest(case=label, script=name):
                    project = self.project(f"{name}-{label.replace(' ', '-')}", {**files, LOG: former})
                    before = snapshot(project)
                    result = runner(project, "close", *counters)
                    self.assertEqual(1, result.returncode, result.stdout)
                    self.assertEqual(before, snapshot(project))


class UsageTest(SessionCase):
    """RQ-INI-011: an unknown or missing sub-command writes nothing."""

    def test_RQ_INI_011_given_an_unknown_sub_command_when_run_then_it_exits_1_with_the_usage(self):
        for name, runner in RUNNERS.items():
            for arguments in (("start",), ()):
                with self.subTest(script=name, arguments=arguments):
                    project = self.project(f"{name}-usage-{len(arguments)}")
                    before = snapshot(project)
                    result = runner(project, *arguments)
                    self.assertEqual(1, result.returncode)
                    self.assertIn("init", result.stderr)
                    self.assertEqual(before, snapshot(project))


class SkillPracticesTest(unittest.TestCase):
    """RQ-INI-018."""

    def setUp(self):
        self.text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    def test_RQ_INI_018_given_the_skill_then_it_runs_its_script_with_bash_as_the_other_skills(self):
        # TASK-INI-012 / DEC-INI-008: bash, not sh.
        self.assertIn("bash <skill-folder>/scripts/session.sh", self.text)
        self.assertNotIn("sh <skill-folder>", self.text.replace("bash <skill-folder>", ""))
        self.assertTrue(SH_SCRIPT.read_bytes().startswith(b"#!/usr/bin/env bash" + bytes([10])))

    def test_RQ_INI_018_given_the_skill_then_its_front_matter_and_size_follow_the_practices(self):
        self.assertEqual(SKILL_NAME, re.search(r"^name:\s*(\S+)\s*$", self.text, re.M).group(1))
        description = re.search(r'^description:\s*"(.*)"\s*$', self.text, re.M).group(1)
        self.assertLessEqual(len(description), MAX_DESCRIPTION)
        self.assertIn("USE FOR", description)
        self.assertLess(len(self.text.splitlines()), MAX_SKILL_LINES)
        self.assertNotIn("disable-model-invocation", self.text)

    def test_RQ_INI_018_given_the_repository_then_the_pointer_and_both_lists_name_the_skill(self):
        pointer = (ROOT / ".claude/skills" / SKILL_NAME / "SKILL.md").read_text(encoding="utf-8")
        self.assertEqual(SKILL_NAME, re.search(r"^name:\s*(\S+)\s*$", pointer, re.M).group(1))
        for name in ENTRY_FILES:
            self.assertIn(f"`{SKILL_NAME}`", (ROOT / name).read_text(encoding="utf-8"), name)

    def test_RQ_INI_018_given_the_scripts_then_they_read_their_paths_from_the_layout_copies(self):
        for script, copy in ((PS_SCRIPT, "agnos-layout.ps1"), (SH_SCRIPT, "agnos-layout.sh")):
            text = script.read_text(encoding="utf-8")
            self.assertIn(copy, text, script.name)
            self.assertNotIn(FOLDER, text, script.name)
            self.assertTrue((SKILL_DIR / "scripts" / copy).is_file(), copy)


if __name__ == "__main__":
    unittest.main()
