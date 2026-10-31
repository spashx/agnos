#!/usr/bin/env python3
"""agnos-meta-qa: a code quality report on demand, for an AI or a tool to correct from.

Implements FTR-QLT-001 after ADR-QLT-001. `setup` installs the pinned analysers (RQ-QLT-006); `check` runs them and
writes one normalised JSON report (RQ-QLT-002). It never changes the code (RQ-QLT-007), and findings never fail it
(RQ-QLT-005).
Python >= 3.9, standard library only. Procedure: ../SKILL.md.
"""
import argparse
import ast
import json
import os
import re
import shutil
import subprocess
import sys
import venv
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS = SKILL_DIR / "assets"
REPOSITORY = SKILL_DIR.parents[2]
ENCODING = "utf-8"
REPLACE = "replace"

SCHEMA_VERSION = 1
TOOLS_DIR = ".agnos-qa"
REPORT_NAME = "report.json"
VENV_DIR = "venv"
ESLINT_CONFIG = "eslint.config.mjs"
PACKAGE_FILES = ("package.json", "package-lock.json", ESLINT_CONFIG)
REQUIREMENTS = "requirements.txt"
RUFF_CONFIG = "ruff.toml"
ESLINT_PACKAGE = "eslint"
SONARJS_PACKAGE = "eslint-plugin-sonarjs"
ESLINT_ENTRY = Path("node_modules") / ESLINT_PACKAGE / "bin" / "eslint.js"
COMPLEXITY_OUTPUT = "complexipy.json"
SETUP_HINT = "run: python .github/skills/agnos-meta-qa/scripts/qa.py setup"

TOOL_RUFF = "ruff"
TOOL_COMPLEXIPY = "complexipy"
TOOL_ESLINT = "eslint"
COMPLEXITY_RULE = "cognitive-complexity"
COMPLEXITY_MAX = 15                                  # DEC-QLT-006, SonarQube's default
PARSING_RULE = "parsing-error"
SEVERITY_ERROR = "error"
SEVERITY_WARNING = "warning"
RUFF_DEFECTS = ("F", "E9", "PLE")                    # rule prefixes that mean the code is wrong, not only hard to read
ESLINT_ERROR_LEVEL = 2
ESLINT_FAILED = 2                                    # 0 and 1 are "no finding" and "findings"
FUNCTION_SEPARATOR = "::"

SCOPE_CHANGED = "changed"
SCOPE_ALL = "all"
SCOPE_PATHS = "paths"
PYTHON_SUFFIX = ".py"
SCRIPT_SUFFIXES = (PYTHON_SUFFIX, ".js")
EXCLUDED_PARTS = frozenset({"tests", "fixtures", "vendor", "node_modules"})     # RQ-QLT-003
EXCLUDED_PREFIX = ".github/skills/agnos-meta-demo/assets/content/"
STATUS_PREFIX = 3                                    # "XY " before a path of `git status --porcelain`
STATUS_RENAMED = "R"
STATUS_COPIED = "C"

EXCEPTION_RE = re.compile(r"agnos-qa-exception:[ \t]*(\S+)[ \t]+(\S.*)")      # RQ-QLT-004, DEC-QLT-004
COMMENT_ENDS = ("-->", "*/")
PIN_SEPARATOR = "=="


class QaError(Exception):
    """The analysis cannot complete (RQ-QLT-005)."""


# ---- findings ----------------------------------------------------------------------------------------------------
# RQ-QLT-002, DEC-QLT-003
def finding(location, tool, rule, severity, message, fixable=False):
    """One finding, the same fields for every analyser; location is (file, line, column, end line, end column)."""
    file, line, column, end_line, end_column = location
    return {"file": file, "line": line, "column": column, "endLine": end_line, "endColumn": end_column, "tool": tool,
            "rule": rule, "severity": severity, "message": message, "fixable": fixable, "exception": None}


def relative(path, root):
    """A path as the report shows it: from the repository's root, with '/'."""
    resolved, top = Path(path).resolve(), Path(root).resolve()
    try:
        return resolved.relative_to(top).as_posix()
    except ValueError:
        return resolved.as_posix()


def from_ruff(rows, root):
    found = []
    for row in rows:
        start, end = row["location"], row["end_location"]
        severity = SEVERITY_ERROR if row["code"].startswith(RUFF_DEFECTS) else SEVERITY_WARNING
        location = (relative(row["filename"], root), start["row"], start["column"], end["row"], end["column"])
        found.append(finding(location, TOOL_RUFF, row["code"], severity, row["message"], row["fix"] is not None))
    return found


def from_eslint(results, root):
    found = []
    for result in results:
        file = relative(result["filePath"], root)
        for message in result["messages"]:
            severity = SEVERITY_ERROR if message["severity"] == ESLINT_ERROR_LEVEL else SEVERITY_WARNING
            location = (file, message.get("line", 1), message.get("column", 1), message.get("endLine"),
                        message.get("endColumn"))
            found.append(finding(location, TOOL_ESLINT, message["ruleId"] or PARSING_RULE, severity, message["message"],
                                 "fix" in message))
    return found


def function_position(path, name):
    """(line, column) of the first definition of a function in a file; complexipy gives only its name."""
    tree = ast.parse(Path(path).read_text(encoding=ENCODING))
    short = name.split(FUNCTION_SEPARATOR)[-1]
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == short:
            return node.lineno, node.col_offset + 1
    return 1, 1


def from_complexipy(rows, root):
    found = []
    for row in rows:
        if row["complexity"] <= COMPLEXITY_MAX:
            continue
        path = Path(root) / row["path"]
        line, column = function_position(path, row["function_name"])
        message = f"Cognitive complexity of {row['function_name']} is {row['complexity']}, above {COMPLEXITY_MAX}"
        found.append(finding((relative(path, root), line, column, None, None), TOOL_COMPLEXIPY, COMPLEXITY_RULE,
                             SEVERITY_WARNING, message))
    return found


def comment_text(text):
    """A comment's text, without the mark that closes it."""
    text = text.strip()
    for end in COMMENT_ENDS:
        if text.endswith(end):
            text = text[:-len(end)]
    return text.strip()


# RQ-QLT-004, DEC-QLT-004
def exception_reason(lines, line, rule):
    """The reason of the exception comment for this rule on the finding's line or the line above, or None."""
    for number in (line, line - 1):
        if 1 <= number <= len(lines):
            match = EXCEPTION_RE.search(lines[number - 1])
            if match and match.group(1) == rule:
                return comment_text(match.group(2))
    return None


def mark_exceptions(findings, root):
    lines_of = {}
    for item in findings:
        file = item["file"]
        if file not in lines_of:
            lines_of[file] = (Path(root) / file).read_text(encoding=ENCODING, errors=REPLACE).splitlines()
        item["exception"] = exception_reason(lines_of[file], item["line"], item["rule"])


def count_findings(findings):
    opened = [f for f in findings if f["exception"] is None]
    by_rule = {}
    for item in opened:
        by_rule[item["rule"]] = by_rule.get(item["rule"], 0) + 1
    return {"total": len(findings), "open": len(opened), "exceptions": len(findings) - len(opened),
            "openByRule": dict(sorted(by_rule.items()))}


# ---- scope -------------------------------------------------------------------------------------------------------
# RQ-QLT-003
def git(root, *args):
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, encoding=ENCODING,
                          check=False)
    if done.returncode:
        raise QaError(f"git {args[0]} failed: {done.stderr.strip()}")
    return done.stdout


def is_excluded(path):
    return path.startswith(EXCLUDED_PREFIX) or bool(EXCLUDED_PARTS.intersection(path.split("/")))


def changed_files(root):
    """The paths git reports as changed, staged or not, untracked included."""
    fields = git(root, "status", "--porcelain", "-z", "--untracked-files=all").split("\0")
    paths, skip = [], False
    for field in filter(None, fields):
        if skip:
            skip = False
            continue
        paths.append(field[STATUS_PREFIX:])
        skip = STATUS_RENAMED in field[:STATUS_PREFIX - 1] or STATUS_COPIED in field[:STATUS_PREFIX - 1]
    return paths


def known_files(root, *pathspec):
    """The paths git tracks, and those it would add, under the pathspec."""
    listed = git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", *pathspec)
    return filter(None, listed.split("\0"))


def is_script(root, path):
    return path.endswith(SCRIPT_SUFFIXES) and (Path(root) / path).is_file()


def files_of_paths(root, paths):
    found = []
    for path in paths:
        target = Path(path) if Path(path).is_absolute() else Path(root) / path
        if target.is_file():
            found.append(relative(target, root))                     # named directly: analysed whatever its folder
        elif target.is_dir():
            found.extend(p for p in known_files(root, relative(target, root)) if not is_excluded(p))
        else:
            raise QaError(f"path not found: {path}")
    return found


def select_files(root, every, paths):
    """The files to analyse, sorted, from the repository's root."""
    if paths:
        candidates = files_of_paths(root, paths)
    else:
        candidates = [p for p in (known_files(root) if every else changed_files(root)) if not is_excluded(p)]
    return sorted({p for p in candidates if is_script(root, p)})


# ---- analysers ---------------------------------------------------------------------------------------------------
def venv_tool(root, name):
    folder = "Scripts" if os.name == "nt" else "bin"
    return Path(root) / TOOLS_DIR / VENV_DIR / folder / (name + (".exe" if os.name == "nt" else ""))


def eslint_entry(root):
    return Path(root) / TOOLS_DIR / ESLINT_ENTRY


def analysers_ready(root):
    tools = (venv_tool(root, TOOL_RUFF), venv_tool(root, TOOL_COMPLEXIPY), eslint_entry(root))
    return all(path.is_file() for path in tools)


def require(path, name):
    if not path.is_file():
        raise QaError(f"{name} is not installed, {SETUP_HINT}")


def run_tool(command, root, name, failed=lambda code: code != 0):
    """The standard output of an analyser, or QaError when it could not complete."""
    try:
        done = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding=ENCODING, errors=REPLACE,
                              check=False)
    except OSError as error:
        raise QaError(f"{name} cannot run: {error}") from error
    if failed(done.returncode):
        raise QaError(f"{name} failed: {done.stderr.strip() or done.stdout.strip()}")
    return done.stdout


def run_ruff(root, files):
    tool = venv_tool(root, TOOL_RUFF)
    require(tool, TOOL_RUFF)
    command = [str(tool), "check", "--config", str(ASSETS / RUFF_CONFIG), "--output-format", "json", "--no-cache",
               "--exit-zero", *files]
    return from_ruff(json.loads(run_tool(command, root, TOOL_RUFF) or "[]"), root)


def run_complexipy(root, files):
    tool = venv_tool(root, TOOL_COMPLEXIPY)
    require(tool, TOOL_COMPLEXIPY)
    output = Path(root) / TOOLS_DIR / COMPLEXITY_OUTPUT
    command = [str(tool), *files, "--max-complexity-allowed", str(COMPLEXITY_MAX), "--quiet", "--output-format", "json",
               "--output", str(output)]
    output.unlink(missing_ok=True)
    run_tool(command, root, TOOL_COMPLEXIPY, failed=lambda code: False)      # it exits 1 on a function above the limit
    if not output.is_file():
        raise QaError(f"{TOOL_COMPLEXIPY} failed: it wrote no result")
    return from_complexipy(json.loads(output.read_text(encoding=ENCODING)), root)


def run_eslint(root, files):
    entry = eslint_entry(root)
    require(entry, TOOL_ESLINT)
    config = Path(root) / TOOLS_DIR / ESLINT_CONFIG
    command = ["node", str(entry), "--config", str(config), "--format", "json", *files]
    output = run_tool(command, root, TOOL_ESLINT, failed=lambda code: code >= ESLINT_FAILED)
    return from_eslint(json.loads(output), root)


def tool_versions():
    """The pinned versions, from the assets (DEC-QLT-005)."""
    pins = (line.partition(PIN_SEPARATOR) for line in (ASSETS / REQUIREMENTS).read_text(encoding=ENCODING).split())
    versions = {name: version for name, _, version in pins}
    versions.update(json.loads((ASSETS / PACKAGE_FILES[0]).read_text(encoding=ENCODING))["dependencies"])
    return versions


def analyse(root, files):
    python = [f for f in files if f.endswith(PYTHON_SUFFIX)]
    script = [f for f in files if not f.endswith(PYTHON_SUFFIX)]
    findings = []
    if python:
        findings += run_ruff(root, python) + run_complexipy(root, python)
    if script:
        findings += run_eslint(root, script)
    mark_exceptions(findings, root)
    return sorted(findings, key=lambda f: (f["file"], f["line"], f["column"], f["rule"]))


# ---- sub-commands ------------------------------------------------------------------------------------------------
# RQ-QLT-006, DEC-QLT-005
def setup(root):
    tools = Path(root) / TOOLS_DIR
    tools.mkdir(exist_ok=True)
    venv.create(tools / VENV_DIR, with_pip=True, clear=True)
    pip = [str(venv_tool(root, "python")), "-m", "pip", "install", "--quiet", "--disable-pip-version-check",
           "-r", str(ASSETS / REQUIREMENTS)]
    run_tool(pip, root, "pip")
    for name in PACKAGE_FILES:
        shutil.copyfile(ASSETS / name, tools / name)
    npm = shutil.which("npm")
    if npm is None:
        raise QaError("npm not found: Node.js is needed for the JavaScript analysers")
    run_tool([npm, "ci", "--silent", "--no-audit", "--no-fund"], tools, "npm")
    print(f"agnos-meta-qa: analysers installed in {TOOLS_DIR}/")
    return 0


def summary_line(counts, files, report_path):
    return (f"agnos-meta-qa: {counts['open']} open, {counts['exceptions']} exceptions, {len(files)} files; "
            f"report: {report_path}")


def scope_of(every, paths):
    if paths:
        return SCOPE_PATHS
    return SCOPE_ALL if every else SCOPE_CHANGED


# RQ-QLT-002, RQ-QLT-003, RQ-QLT-005, RQ-QLT-007
def check(root, every, paths, out):
    """Writes the report. A previous report is removed first, so that a failed analysis cannot leave a stale one."""
    report_path = Path(out) if out else Path(root) / TOOLS_DIR / REPORT_NAME
    report_path.unlink(missing_ok=True)
    files = select_files(root, every, paths)
    findings = analyse(root, files)
    counts = count_findings(findings)
    report = {"schemaVersion": SCHEMA_VERSION, "head": git(root, "rev-parse", "--short", "HEAD").strip(),
              "scope": scope_of(every, paths), "files": files, "tools": tool_versions(),
              "limits": {"cognitiveComplexity": COMPLEXITY_MAX}, "summary": counts, "findings": findings}
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding=ENCODING, newline="\n")
    print(summary_line(counts, files, report_path))
    for rule, count in counts["openByRule"].items():
        print(f"  {count:4} {rule}")
    return 0


def parse_args(argv):
    parser = argparse.ArgumentParser(prog="qa.py", description="AGNOS code quality report")  # FTR-QLT-001
    parser.add_argument("--root", default=str(REPOSITORY), help="repository to analyse (default: this one)")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("setup", help="install the pinned analysers into " + TOOLS_DIR)
    run = commands.add_parser("check", help="write the report: the changed files, or --all, or the given paths")
    run.add_argument("paths", nargs="*", help="files or folders to analyse instead of the changed files")
    run.add_argument("--all", action="store_true", dest="every",
                     help="every script git knows, tests and vendored files left out")
    run.add_argument("--out", help=f"report path (default: {TOOLS_DIR}/{REPORT_NAME})")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    try:
        if args.command == "setup":
            return setup(args.root)
        return check(args.root, args.every, args.paths, args.out)
    except QaError as error:
        print(f"agnos-meta-qa: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
