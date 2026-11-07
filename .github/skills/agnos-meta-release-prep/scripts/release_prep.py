#!/usr/bin/env python3
"""agnos-meta-release-prep: the deterministic steps of a release preparation, ordered by ../SKILL.md.

Implements FTR-PLG-005 after ADR-PLG-005 (DEC-PLG-022, DEC-PLG-023, DEC-PLG-025):
- `check` stops on a changed working tree or duplicate IDs, else lists the tasks not Done (RQ-PLG-027);
- `review` shows the changed files and their diff, the changelog's [Unreleased] and a proposed version (RQ-PLG-028);
- `set-version <X.Y.Z>` writes an approved version into VERSION.txt and the changelog's heading (RQ-PLG-029, RQ-PLG-032).
It never commits, and publishes nothing. Python >= 3.10, standard library and this folder's modules only (RQ-MTA-013).
"""
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))    # the layout's generated copy, beside this script
import agnos_layout  # noqa: E402  RQ-PLG-036 / DEC-PLG-027

PROG = "agnos-meta-release-prep"
ENCODING = "utf-8"
EXIT_OK = 0
EXIT_FAILED = 1
INDEX_DUPLICATES = 2                    # agnos-index's exit code for duplicate IDs (RQ-IDX-013)
IS_WINDOWS = os.name == "nt"
INDEX_SCRIPTS = Path(__file__).resolve().parents[2] / "agnos-index" / "scripts"
INDEX_PATH = f"{agnos_layout.FOLDER}/{agnos_layout.INDEX}"
VERSION_FILE = ".github/skills/agnos-init/assets/templates/VERSION.txt"     # RQ-PLG-032 / DEC-PLG-025
CHANGELOG = "CHANGELOG.md"
# RQ-PLG-028: the four files agnos-meta-docs-sync edits; any other change is unexpected
SYNCED = (CHANGELOG, "AGENTS.md", "CLAUDE.md", ".github/skills/agnos-init/assets/templates/AGNOS-GETTING-STARTED.md")
STATUS_PATH_START = 3                   # git status --porcelain: two status letters and a space
RENAME_ARROW = " -> "
TASK_ROW_RE = re.compile(r"^(TASK-[A-Z]{3}-\d{3})\|[^|]*\|([^|]*)\|(.*)$", re.M)
DONE = "Done"
# The regular expression of SemVer 2.0.0, from semver.org; the same as agnos-meta-release's (RQ-PLG-032)
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
                       r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
                       r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$")
UNRELEASED_RE = re.compile(r"^## \[Unreleased\][^\n]*$", re.M | re.I)
NEXT_RELEASE_RE = re.compile(r"^## ", re.M)
SECTION_RE = re.compile(r"^### +(\w+)", re.M)
BULLET_RE = re.compile(r"^[-*] ", re.M)
# DEC-PLG-023: the part of the version each Keep a Changelog section raises; Deprecated and Security are read as SemVer reads them
MAJOR, MINOR, PATCH = 0, 1, 2
RAISES = {"removed": MAJOR, "added": MINOR, "changed": MINOR, "deprecated": MINOR, "fixed": PATCH, "security": PATCH}
PRE_RELEASE_GROUP = 4
IDENTIFIER_SEPARATOR = "."


def fail(message):
    print(f"{PROG}: {message}", file=sys.stderr)
    return EXIT_FAILED


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding=ENCODING,
                          check=True).stdout


# RQ-PLG-027
def changed_files(repo):
    """The paths git status names, untracked ones included."""
    paths = []
    for line in filter(None, git(repo, "status", "--porcelain", "--untracked-files=all").split("\n")):
        paths.append(line[STATUS_PATH_START:].split(RENAME_ARROW)[-1].strip('"'))
    return paths


def build_index(repo):
    """agnos-index's exit code and what it printed, run as its procedure says for this platform."""
    if IS_WINDOWS:
        command = ["powershell", "-NoProfile", "-File", str(INDEX_SCRIPTS / "build-index.ps1")]
    else:
        command = ["bash", str(INDEX_SCRIPTS / "build-index.sh")]
    done = subprocess.run(command, cwd=repo, capture_output=True, text=True, encoding=ENCODING, errors="replace")
    return done.returncode, (done.stdout + done.stderr).strip()


def open_tasks(index_text):
    """(ID, status, title) of each task of the index whose status is not Done."""
    return [(task, status.strip(), title.strip()) for task, status, title in TASK_ROW_RE.findall(index_text)
            if status.strip() != DONE]


def check(repo):
    changed = changed_files(repo)
    if changed:
        for path in changed:
            print(f"changed: {path}")
        return fail("the working tree holds changes: commit or stash them, nothing was edited")
    code, said = build_index(repo)
    if code:
        print(said)
        reason = "duplicate IDs" if code == INDEX_DUPLICATES else "an error"
        return fail(f"agnos-index reported {reason}: correct them first")
    for task, status, title in open_tasks((Path(repo) / INDEX_PATH).read_text(encoding=ENCODING)):
        print(f"open: {task} | {status} | {title}")
    print(f"{PROG}: check passed")
    return EXIT_OK


# RQ-PLG-028 / DEC-PLG-023
def unreleased(changelog):
    """The text under the changelog's [Unreleased] heading, up to the next release; None when there is no such heading."""
    found = UNRELEASED_RE.search(changelog)
    if not found:
        return None
    section = changelog[found.end():]
    after = NEXT_RELEASE_RE.search(section)
    return (section[:after.start()] if after else section).strip("\n")


def raised_part(section_text):
    """The version part the section raises, or None when it holds no entry."""
    if not section_text or not BULLET_RE.search(section_text):
        return None
    parts = [RAISES[name.lower()] for name in SECTION_RE.findall(section_text) if name.lower() in RAISES]
    return min(parts, default=PATCH)


def proposed_version(current, section_text):
    """The next version from the current one and the [Unreleased] text, or None when there is nothing to release."""
    part = raised_part(section_text)
    if part is None:
        return None
    numbers = [int(number) for number in SEMVER_RE.match(current).groups()[:3]]
    numbers[part] += 1
    numbers[part + 1:] = [0] * (len(numbers) - part - 1)
    return IDENTIFIER_SEPARATOR.join(map(str, numbers))


def review(repo):
    root = Path(repo)
    for path in changed_files(repo):
        print(f"changed: {path}" if path in SYNCED else f"changed: {path} (unexpected: not one of docs-sync's four files)")
    print(git(repo, "diff", "--no-color"), end="")
    for path in git(repo, "ls-files", "--others", "--exclude-standard").split():
        print(f"new file {path}:\n{(root / path).read_text(encoding=ENCODING)}")
    section = unreleased((root / CHANGELOG).read_text(encoding=ENCODING))
    print(f"## [Unreleased]\n{section or ''}")
    current = (root / VERSION_FILE).read_text(encoding=ENCODING).strip()
    version = proposed_version(current, section)
    print(f"current: {current}")
    print(f"proposed: {version}" if version else f"{PROG}: nothing to release, no version proposed")
    return EXIT_OK


# RQ-PLG-029 / DEC-PLG-023: SemVer 2.0.0 precedence, section 11
def identifier_key(identifier):
    """Numeric identifiers sort numerically and before alphanumeric ones, which sort in ASCII order."""
    return (0, int(identifier), "") if identifier.isdigit() else (1, 0, identifier)


def precedence_key(version):
    found = SEMVER_RE.match(version)
    core = tuple(int(number) for number in found.groups()[:3])
    pre = found.group(PRE_RELEASE_GROUP)
    if pre is None:
        return core, (1,)            # a release follows each of its pre-releases
    return core, (0, tuple(identifier_key(part) for part in pre.split(IDENTIFIER_SEPARATOR)))


def is_above(version, current):
    return precedence_key(version) > precedence_key(current)


def set_version(repo, version):
    root = Path(repo)
    current = (root / VERSION_FILE).read_text(encoding=ENCODING).strip()
    if not SEMVER_RE.match(version):
        return fail(f"{version} is not a SemVer 2.0.0 version: nothing changed")
    if not is_above(version, current):
        return fail(f"{version} is not above the current version {current}: nothing changed")
    changelog = (root / CHANGELOG).read_bytes().decode(ENCODING)
    found = UNRELEASED_RE.search(changelog)
    if not found:
        return fail(f"{CHANGELOG} has no ## [Unreleased] heading: nothing changed")
    (root / VERSION_FILE).write_bytes(f"{version}\n".encode(ENCODING))
    (root / CHANGELOG).write_bytes((changelog[:found.start()] + f"## [{version}]" + changelog[found.end():]).encode(ENCODING))
    print(f"{PROG}: version {version} written into {VERSION_FILE} and {CHANGELOG}")
    return EXIT_OK


def parse_args(argv):
    parser = argparse.ArgumentParser(prog="release_prep.py", description="AGNOS release preparation: check, review, set-version")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("check", "review"):
        commands.add_parser(name).add_argument("--repo", default=".")
    setter = commands.add_parser("set-version")
    setter.add_argument("version")
    setter.add_argument("--repo", default=".")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if args.command == "check":
        return check(args.repo)
    if args.command == "review":
        return review(args.repo)
    return set_version(args.repo, args.version)


if __name__ == "__main__":
    sys.exit(main())
