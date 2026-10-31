#!/usr/bin/env python3
"""agnos-meta-release: a release rehearsed in a folder, without publishing anything.

Implements FTR-MTA-002 after ADR-MTA-002 (DEC-MTA-007): it selects the delivered files of a commit (RQ-MTA-007, RQ-MTA-008)
and writes only its output and report (RQ-MTA-006). Python >= 3.9, standard library only. Procedure: ../SKILL.md.
"""
import argparse
import json
import os
import re
import stat
import subprocess
import sys
import time
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
LAYERS_PATH = ASSETS / "layers.json"
ENCODING = "utf-8"
EXIT_OK = 0
EXIT_FAILED = 1

META_PREFIX = "agnos-meta-"     # RQ-MTA-002: the only criterion for a skill or sub-agent
LAYER_META = "meta"
LAYER_DELIVERED = "delivered"
REPORT_SUFFIX = ".report.json"
EXECUTABLE_MODE = "100755"
TREE_FIELDS = 3                 # git ls-tree: mode, type, hash
DURATION_FORMAT = ".3f"


def fail(message):
    print(f"agnos-meta-release: {message}", file=sys.stderr)
    return EXIT_FAILED


def git(repo, *args):
    """The bytes a git command prints; a failure raises CalledProcessError."""
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True).stdout


# RQ-MTA-008 / DEC-MTA-008
def load_rules():
    layers = json.loads(LAYERS_PATH.read_text(encoding=ENCODING))
    return {name: [re.compile(pattern) for pattern in layers[name]] for name in (LAYER_META, LAYER_DELIVERED)}


def layer_of(path, rules):
    """The layer of a repository path, or None when no rule knows it. Meta is read first."""
    if any(part.startswith(META_PREFIX) for part in path.split("/")):
        return LAYER_META
    for name in (LAYER_META, LAYER_DELIVERED):
        if any(pattern.search(path) for pattern in rules[name]):
            return name
    return None


# RQ-MTA-007
def tracked_files(repo):
    """(path, mode) of each file tracked at HEAD."""
    listed = git(repo, "ls-tree", "-r", "-z", "HEAD").decode(ENCODING)
    entries = []
    for entry in filter(None, listed.split("\0")):
        fields, path = entry.split("\t", 1)
        entries.append((path, fields.split(" ", TREE_FIELDS)[0]))
    return entries


# RQ-MTA-006
def output_refusal(repo, output):
    """Why this output cannot be used, or None."""
    if output == repo or repo in output.parents:
        return f"the output {output} is inside the repository"
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        return f"the output {output} is not empty"
    return None


def write_delivered(repo, output, entries):
    for path, mode in entries:
        target = output / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(git(repo, "show", f"HEAD:{path}"))
        if mode == EXECUTABLE_MODE:
            os.chmod(target, target.stat().st_mode | stat.S_IXUSR)


def no_proof_yet(repo, output, demo):
    return []


def rehearse(repo, output, demo, proof):
    """Classify every file before writing any, so that a refusal delivers nothing."""
    rules = load_rules()
    entries = tracked_files(repo)
    unknown = [path for path, _ in entries if layer_of(path, rules) is None]
    if unknown:
        return fail(f"no layer in {LAYERS_PATH.name} for: {', '.join(unknown)}")
    delivered = [entry for entry in entries if layer_of(entry[0], rules) == LAYER_DELIVERED]
    left_out = [path for path, _ in entries if layer_of(path, rules) == LAYER_META]
    output.mkdir(parents=True, exist_ok=True)
    write_delivered(repo, output, delivered)
    problems = proof(repo, output, demo)
    report = {"commit": git(repo, "rev-parse", "HEAD").decode(ENCODING).strip(), "delivered": [path for path, _ in delivered],
              "leftOut": left_out, "problems": problems}
    Path(f"{output}{REPORT_SUFFIX}").write_text(json.dumps(report, indent=2) + "\n", encoding=ENCODING, newline="\n")
    for problem in problems:
        fail(problem)
    return EXIT_FAILED if problems else EXIT_OK


def parse_args(argv):
    parser = argparse.ArgumentParser(prog="release.py", description="AGNOS release rehearsal, publishing nothing")
    parser.add_argument("--dry-run", action="store_true", help="rehearse; the only mode that exists")
    parser.add_argument("--output", required=True, help="folder to write, outside the repository and empty")
    parser.add_argument("--repo", default=".", help="repository root (default: the current folder)")
    parser.add_argument("--demo", help="the demo repository (default: agnos-lightweight-process.demo beside the repository)")
    return parser.parse_args(argv)


def main(argv=None, proof=no_proof_yet):
    args = parse_args(argv)
    if not args.dry_run:    # RQ-MTA-006 / DEC-MTA-011
        return fail("only the rehearsal exists: call it with --dry-run; publishing is not available")
    started = time.perf_counter()
    try:
        repo = Path(git(args.repo, "rev-parse", "--show-toplevel").decode(ENCODING).strip()).resolve()
    except subprocess.CalledProcessError:
        return fail(f"{args.repo} is not a git repository")
    output = Path(args.output).resolve()
    refusal = output_refusal(repo, output)
    if refusal:
        return fail(refusal)
    code = rehearse(repo, output, args.demo, proof)
    if code == EXIT_OK:
        print(f"agnos-meta-release: {output} written in {time.perf_counter() - started:{DURATION_FORMAT}} s")
    return code


if __name__ == "__main__":
    sys.exit(main())
