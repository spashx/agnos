#!/usr/bin/env python3
"""agnos-meta-docs-sync report: what changed in the repository since each entry-point document was last changed.

Implements FTR-DOC-001 (RQ-DOC-001, RQ-DOC-004). Prints JSON: the head commit; for each target document the commit that
last changed it and the non-merge commits made since, each with its subject and changed files (the commits that touch only
generated or session files are left out); and the skills of the repository with their maintainer flag.
Python >= 3.9, standard library only.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

TARGETS = ("CHANGELOG.md", "AGENTS.md", "CLAUDE.md", "GETTING_STARTED.MD")
IGNORED_PREFIXES = ("process/INDEX.idx.md", "process/_sessionstate/")
SKILLS_DIR = ".github/skills"
SKILL_FILE = "SKILL.md"
META_PREFIX = "agnos-meta-"            # RQ-MTA-002, DEC-MTA-003: the only criterion
COMMIT_MARK = "@@@"
FIELD_SEPARATOR = "\x1f"
LOG_FORMAT = f"{COMMIT_MARK}%H{FIELD_SEPARATOR}%s"
ENCODING = "utf-8"
FRONT_MATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
FIELD_NAME = "name"
FIELD_DESCRIPTION = "description"
FIELD_RE = re.compile(rf"^({FIELD_NAME}|{FIELD_DESCRIPTION}):\s*(.*)$", re.M)
REV_HEAD = "HEAD"
FILES_SHOWN = 12                       # files listed per commit; the others are counted
NO_REPOSITORY = "not a git repository: "


class ReportError(Exception):
    """The folder cannot be read as a git repository."""


def git(repo, *args):
    done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding=ENCODING, check=False)
    if done.returncode:
        raise ReportError(NO_REPOSITORY + str(repo) if "not a git repository" in done.stderr else done.stderr.strip())
    return done.stdout


def is_ignored(path):
    return path.startswith(IGNORED_PREFIXES)


def commits_after(repo, since):
    """The non-merge commits after `since` (every commit when None), oldest first, with their changed files; a commit
    whose files are all generated or session files is left out."""
    span = [f"{since}..{REV_HEAD}"] if since else [REV_HEAD]
    text = git(repo, "log", "--no-merges", "--reverse", "--name-only", f"--format={LOG_FORMAT}", *span)
    found = []
    for block in text.split(COMMIT_MARK)[1:]:
        head, *files = block.strip("\n").split("\n")
        sha, subject = head.split(FIELD_SEPARATOR, 1)
        files = [f for f in files if f]
        if any(not is_ignored(f) for f in files):
            kept = [f for f in files if not is_ignored(f)]
            found.append({"sha": sha, "subject": subject, "files": kept[:FILES_SHOWN], "moreFiles": max(0, len(kept) - FILES_SHOWN)})
    return found


def last_change(repo, name):
    sha = git(repo, "log", "-1", "--format=%H", "--", name).strip()
    return sha or None


def skills_of(repo):
    """Name, path, description and maintainer flag of each skill, from the front matter of its SKILL.md."""
    found = []
    for path in sorted(Path(repo, SKILLS_DIR).glob(f"*/{SKILL_FILE}")):
        match = FRONT_MATTER_RE.match(path.read_text(encoding=ENCODING))
        fields = {k: v.strip().strip('"') for k, v in FIELD_RE.findall(match.group(1))} if match else {}
        name = fields.get(FIELD_NAME, path.parent.name)
        found.append({FIELD_NAME: name, "path": path.relative_to(repo).as_posix(),
                      FIELD_DESCRIPTION: fields.get(FIELD_DESCRIPTION, ""), "maintainer": name.startswith(META_PREFIX)})
    return found


# RQ-DOC-001
def collect(repo):
    repo = Path(repo)
    head = git(repo, "rev-parse", REV_HEAD).strip()
    targets = []
    for name in TARGETS:
        last = last_change(repo, name)
        targets.append({"file": name, "lastCommit": last, "commits": commits_after(repo, last)})
    return {"head": head, "targets": targets, "skills": skills_of(repo)}


def main(argv=None):
    parser = argparse.ArgumentParser(description="What changed since each entry-point document was last changed")  # FTR-DOC-001
    parser.add_argument("--repo", default=".", help="repository root (default: the current folder)")
    args = parser.parse_args(argv)
    try:
        report = collect(args.repo)
    except ReportError as error:
        print(f"agnos-meta-docs-sync: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
