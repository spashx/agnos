#!/usr/bin/env python3
"""agnos-meta-release: a release rehearsed in a folder, without publishing anything.

Implements FTR-MTA-002 after ADR-MTA-002 (DEC-MTA-007): it selects the delivered files of a commit (RQ-MTA-007, RQ-MTA-008),
removes the workshop's IDs from them (RQ-MTA-009), checks the result (RQ-MTA-010), proves it behaves as the workshop does
(RQ-MTA-011) and writes only its output and report (RQ-MTA-006, RQ-MTA-012), the proof working on a temporary clone of the demo.
Python >= 3.10, standard library only. Procedure: ../SKILL.md.
"""
import argparse
import ast
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
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

INDEX_PATH = "process/INDEX.idx.md"
ID_TYPES = "FTR|RQ|ADR|DEC|PLAN|TASK"
DEFINITION_RE = re.compile(rf"^(?:{ID_TYPES})-([A-Z]{{3}})-\d{{3}}\|", re.M)
NEVER_MATCHES = "(?!)"
MARK = ""                 # where a removal happened, until its line is cleaned
BYTE_TRANSPARENT = "latin-1"    # any byte reads as one character, so that a binary file can be searched
LINE_RE = re.compile(r"[^\n]*\n|[^\n]+")
ENDING_RE = re.compile(r"\r?\n$")
EMPTY_COMMENT_RE = re.compile(rf"[ \t]*(?:<!--[\s{MARK}]*-->|/\*[\s{MARK}]*\*/)")
TRAILING_MARKER_RE = re.compile(rf"[ \t]*(?:#|//)[ \t]*{MARK}+[ \t]*$")
DOUBLED_SEPARATOR_RE = re.compile(rf"([,;])\s*{MARK}+\s*[,;]")
NOTHING_LEFT_RE = re.compile(r"^[\s#/*<>!\-.,;:()]*$")
COMMENT_EDGE_RE = re.compile(r"-->|\*/|<!--|/\*")
TO_READ_RE = re.compile(rf"\b(?:in|by|of|per|from|see|and|to|for|with|at|on|the|as|after|implements|fulfils)[ \t]*{MARK}"
                        rf"|:[ \t]*{MARK}+[ \t]*(?:[;,.]|$)|[,;][ \t]*{MARK}+[ \t]*$")
COMMENT_OPEN = "<!--"
COMMENT_CLOSE = "-->"
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
COMMENT_LABEL_RE = re.compile(r"[\w /-]+:")
ONLY_PUNCTUATION_RE = re.compile(rf"^[\s{MARK}.,;:]*$")
CITED_PATH_RE = re.compile(r"(^|/)tests?/")      # a project has its own process/ and settings, not AGNOS's tests
TEST_FILE_PREFIX = "test"

# RQ-MTA-011 / DEC-MTA-010
DEMO_FOLDER_NAME = "agnos-lightweight-process.demo"
FIXED_TIME = "2000-01-01T00:00:00Z"
PERF_PAGE = "process/PERF-CENTER.html"
PERF_RESULTS = ("process/PERF-CENTER.json", "process/PERF-CENTER.data.js")
INIT_RESULTS = ("CLAUDE.md", "AGENTS.md")
PLACEHOLDER = b"<toolkit>"
INDEX_SCRIPT = ".github/skills/agnos-index/scripts/build-index"
INIT_SCRIPT = ".github/skills/agnos-init/scripts/init"
PERF_SCRIPT = ".github/skills/agnos-perf-center/scripts/perf_center.py"
PARSE_MESSAGE_LENGTH = 200
IS_WINDOWS = os.name == "nt"
POWERSHELL = "powershell"
BASH = "bash"
NODE = "node"
PS_PARSE = ("$e=$null;[void][System.Management.Automation.Language.Parser]::ParseFile($args[0],[ref]$null,[ref]$e);"
            "if($e.Count){$e[0].Message;exit 1}")
TOOL_PARSERS = {".js": (NODE, lambda p: [NODE, "--check", p]),
                ".sh": (BASH, lambda p: [BASH, "-n", p]),
                ".ps1": (POWERSHELL, lambda p: [POWERSHELL, "-NoProfile", "-Command", f"& {{{PS_PARSE}}} '{p}'"])}
MARKDOWN_RE = re.compile(r"\.md$", re.I)
NOT_SCANNED_FOR_CITATIONS_RE = re.compile(r"^process/|/tests?/|/assets/content/")


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


# RQ-MTA-009 / DEC-MTA-009
def index_trigrams(index_text):
    return set(DEFINITION_RE.findall(index_text))


def id_pattern(trigrams):
    """An ID of the workshop: its trigram decides, so that an ID the index no longer defines goes too and examples stay."""
    names = "|".join(sorted(trigrams)) or NEVER_MATCHES
    return re.compile(rf"\b(?:{ID_TYPES})-(?:{names})-\d{{3}}\b")


def citation_list(pattern):
    """The regular expression of a list of IDs: abbreviated numbers (a number before a word is a quantity), ranges and separators."""
    token = rf"{pattern.pattern}(?:\s*(?:,|to\b|and\b)\s*\d{{3}}\b(?!\s+(?!to\b|and\b)[a-z]))*"
    separator = r"(?:\s*[,;:/]\s*|\s+(?:to|and)\s+)"
    return rf"{token}(?:{separator}{token})*"


def clean_line(line):
    """A line a removal touched, and whether a person should read it; None when nothing but punctuation is left.
    Every rule is anchored on the mark: what stands away from the removal, a CSS selector's spaces for one, is not touched."""
    ending = ENDING_RE.search(line)
    end = ending.group() if ending else ""
    body = line[:len(line) - len(end)]
    to_read = bool(TO_READ_RE.search(body))
    body = TRAILING_MARKER_RE.sub("", body)
    body = DOUBLED_SEPARATOR_RE.sub(r"\1", body).replace(MARK, "").rstrip()
    if NOTHING_LEFT_RE.match(body) and not COMMENT_EDGE_RE.search(body):
        return None, False
    return body + end, to_read


def without_empty_comment(comment):
    """A comment left with nothing but its labels goes whole; any other stays."""
    words = comment.group()[len(COMMENT_OPEN):-len(COMMENT_CLOSE)]
    if MARK in words and ONLY_PUNCTUATION_RE.match(COMMENT_LABEL_RE.sub("", words)):
        return MARK
    return comment.group()


def remove_ids(text, pattern):
    """The text without the workshop's IDs, how many went, and the (line, text) a person should read. Only lines holding a citation change."""
    count = len(pattern.findall(text))
    if not count:
        return text, 0, []
    citations = citation_list(pattern)
    text = re.sub(rf"({pattern.pattern})\s*\(\s*{citations}\s*\)", r"\1", text)     # ADR-X (DEC-Y) is one citation
    text = re.sub(rf"[ \t]*\(\s*{citations}\s*\)", MARK, text)
    text = re.sub(rf"\(\s*{citations}\s*[:;,]\s*", f"({MARK}", text)
    text = re.sub(rf"\s*[;,]\s*{citations}\s*\)", f"{MARK})", text)
    text = re.sub(rf"""(^[ \t]*|<!--[ \t]*|(?:\#|//|/\*|\*)[ \t]*|"|')(?:{citations})[ \t]*:[ \t]*(\S)""",
                  lambda found: f"{found.group(1)}{MARK}{found.group(2).upper()}", text, flags=re.M)
    text = re.sub(rf"[ \t]*(?:{citations})(?:[ \t]*:(?=\s))?", MARK, text)
    text = EMPTY_COMMENT_RE.sub(MARK, text)
    text = HTML_COMMENT_RE.sub(without_empty_comment, text)
    kept = []
    to_read = []
    for line in LINE_RE.findall(text):
        if MARK not in line:
            kept.append(line)
            continue
        cleaned, should_read = clean_line(line)
        if cleaned is None:
            continue
        kept.append(cleaned)
        if should_read:
            to_read.append((len(kept), cleaned.strip()))
    return "".join(kept), count, to_read


# RQ-MTA-010
def check_output(output, pattern, rules):
    """What the output should not hold, read from the output itself so as not to rely on the removal."""
    problems = []
    for path in sorted(p for p in output.rglob("*") if p.is_file()):
        name = path.relative_to(output).as_posix()
        if rules and layer_of(name, rules) == LAYER_META:
            problems.append(f"{name}: a file of the Meta layer")
        problems += [f"{name}: its path holds {found}" for found in pattern.findall(name)]
        for number, line in enumerate(path.read_bytes().decode(BYTE_TRANSPARENT).split("\n"), 1):
            problems += [f"{name}:{number}: {found}" for found in pattern.findall(line)]
    return problems


# RQ-MTA-012
def mentions(text, left_out, delivered_names=()):
    """(line, what) of each mention of a meta skill or of a test the release leaves out."""
    left_out = [path for path in left_out if CITED_PATH_RE.search(path)]
    names = {Path(path).name for path in left_out if Path(path).name.startswith(TEST_FILE_PREFIX)} - set(delivered_names)
    found = []
    for number, line in enumerate(text.split("\n"), 1):
        if META_PREFIX in line:
            found.append((number, META_PREFIX))
        full_paths = [path for path in left_out if path in line]
        found += [(number, path) for path in full_paths]
        named = {Path(path).name for path in full_paths}
        found += [(number, name) for name in sorted(names - named) if name in line]
    return found


def ids_outside_comments(text, pattern):
    """(line, ID) of each ID a Markdown text shows outside a comment (RQ-MTA-014)."""
    visible = HTML_COMMENT_RE.sub(lambda comment: "\n" * comment.group().count("\n"), text)
    return [(number, found) for number, line in enumerate(visible.split("\n"), 1) for found in pattern.findall(line)]


def write_delivered(repo, output, entries, pattern, left_out):
    """Writes each delivered file without the workshop's IDs, and returns what the report says of them."""
    findings = {"removed": {}, "toRead": [], "mentions": []}
    delivered_names = {Path(path).name for path, _ in entries}
    for path, mode in entries:
        data = git(repo, "show", f"HEAD:{path}")
        try:
            text, count, to_read = remove_ids(data.decode(ENCODING), pattern)
        except UnicodeDecodeError:      # a binary file: RQ-MTA-010 still reads it
            text = None
        target = output / path
        target.parent.mkdir(parents=True, exist_ok=True)
        if text is None:
            target.write_bytes(data)
        else:
            target.write_bytes(text.encode(ENCODING))
            if count:
                findings["removed"][path] = count
            findings["toRead"] += [{"file": path, "line": line, "text": said} for line, said in to_read]
            findings["mentions"] += [{"file": path, "line": line, "what": what}
                                     for line, what in mentions(text, left_out, delivered_names)]
        if mode == EXECUTABLE_MODE:
            os.chmod(target, target.stat().st_mode | stat.S_IXUSR)
    return findings


def workshop_citations(repo, entries, pattern):
    """IDs shown outside a comment in the commit's Markdown (RQ-MTA-014): listed, blocking nothing."""
    found = []
    for path, _ in entries:
        if MARKDOWN_RE.search(path) and not NOT_SCANNED_FOR_CITATIONS_RE.search(path):
            text = git(repo, "show", f"HEAD:{path}").decode(ENCODING)
            found += [{"file": path, "line": line, "id": shown} for line, shown in ids_outside_comments(text, pattern)]
    return found


# RQ-MTA-011 / DEC-MTA-010
def tool_works(tool):
    """Whether a parser can run: Windows may hold a bash that only asks to install a distribution."""
    if not shutil.which(tool):
        return False
    if tool != BASH:
        return True
    return subprocess.run([BASH, "-c", "exit 0"], capture_output=True).returncode == 0


def parse_error(path, usable):
    """Why this file does not parse, or None; a file of no known language, or whose parser is absent, gives None."""
    readers = {".py": ast.parse, ".json": json.loads}
    if path.suffix in readers:
        try:
            readers[path.suffix](path.read_text(encoding=ENCODING))
        except (SyntaxError, ValueError) as error:
            return str(error)
    elif usable.get(path.suffix):
        done = subprocess.run(TOOL_PARSERS[path.suffix][1](str(path)), capture_output=True, text=True, errors="replace")
        if done.returncode:
            return (done.stdout + done.stderr).strip()[:PARSE_MESSAGE_LENGTH]
    return None


def parse_problems(folder):
    """The delivered scripts that no longer parse. A language whose parser is absent is said, and not checked."""
    usable = {suffix: tool_works(parser[0]) for suffix, parser in TOOL_PARSERS.items()}
    for suffix, works in usable.items():
        if not works and any(folder.rglob(f"*{suffix}")):
            print(f"agnos-meta-release: {TOOL_PARSERS[suffix][0]} is absent, {suffix} files are not parsed", file=sys.stderr)
    problems = []
    for path in sorted(p for p in folder.rglob("*") if p.is_file()):
        error = parse_error(path, usable)
        if error:
            problems.append(f"{path.relative_to(folder).as_posix()} no longer parses: {error}")
    return problems


def without_path(data, toolkit):
    """A result with the toolkit's path taken out, as agnos-init writes it as given."""
    return data.replace(str(toolkit).encode(ENCODING), PLACEHOLDER)


def compare_runs(baseline, output, workspace, runners):
    """Runs each skill from the workshop's files and from the output, and names the results that differ."""
    problems = []
    for label, runner in runners:
        expected = runner(baseline, workspace)
        obtained = runner(output, workspace)
        for name in sorted(set(expected) | set(obtained)):
            if expected.get(name) != obtained.get(name):
                problems.append(f"{label}: {name} differs from the workshop's")
    return problems


def script_command(toolkit, script, windows_args, posix_args):
    if IS_WINDOWS:
        return [POWERSHELL, "-NoProfile", "-File", str(Path(toolkit) / f"{script}.ps1"), *windows_args]
    return [BASH, str(Path(toolkit) / f"{script}.sh"), *posix_args]


def run_tool(command, folder):
    """A failure is a result, compared like any other."""
    done = subprocess.run(command, cwd=folder, capture_output=True, text=True, errors="replace")
    return f"exit {done.returncode}".encode(ENCODING)


def run_index(toolkit, workspace):
    clone = workspace / "demo"
    code = run_tool(script_command(toolkit, INDEX_SCRIPT, [], []), clone)
    return {"exit": code, INDEX_PATH: (clone / INDEX_PATH).read_bytes()}


def run_perf_center(toolkit, workspace):
    clone = workspace / "demo"
    script = str(Path(toolkit) / PERF_SCRIPT)
    code = run_tool([sys.executable, script, "--process", "process", "--sources", ".", "--call-graph", "--history",
                     "--generated-at", FIXED_TIME, "--out", PERF_PAGE], clone)
    results = {"exit": code}
    for name in PERF_RESULTS:
        path = clone / name
        results[name] = path.read_bytes() if path.exists() else None
        path.unlink(missing_ok=True)
    (clone / PERF_PAGE).unlink(missing_ok=True)     # left there, the next run would scan it as a source
    return results


def run_init(toolkit, workspace):
    target = Path(tempfile.mkdtemp(dir=workspace))
    code = run_tool(script_command(toolkit, INIT_SCRIPT, ["-Target", str(target), "-Toolkit", str(toolkit)],
                                   ["--target", str(target), "--toolkit", str(toolkit)]), target)
    results = {"exit": code}
    for name in INIT_RESULTS:
        path = target / name
        results[name] = without_path(path.read_bytes(), toolkit) if path.exists() else None
    return results


RUNNERS = (("agnos-index", run_index), ("agnos-perf-center", run_perf_center), ("agnos-init", run_init))


def write_baseline(repo, folder):
    """The delivered files as committed, IDs included: what the output is compared with, whatever the working tree holds."""
    rules = load_rules()
    for path, _ in tracked_files(repo):
        if layer_of(path, rules) == LAYER_DELIVERED:
            target = folder / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(git(repo, "show", f"HEAD:{path}"))


def demo_folder(repo, demo):
    """The demo, as an absolute path since the proof clones it from a temporary folder."""
    return Path(demo).resolve() if demo else Path(repo).parent / DEMO_FOLDER_NAME


def prove(repo, output, demo):
    """Parses the output, then compares what its skills write with the workshop's, on a clone so that the demo stays."""
    demo_path = demo_folder(repo, demo)
    if not demo_path.is_dir():
        return [f"no demo at {demo_path}: build it with agnos-meta-demo"]
    problems = parse_problems(output)
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as holder:
        workspace = Path(holder)
        baseline = workspace / "baseline"
        write_baseline(repo, baseline)
        git(workspace, "clone", "--quiet", str(demo_path), "demo")
        problems += compare_runs(baseline, output, workspace, RUNNERS)
    return problems


def rehearse(repo, output, demo, proof):
    """Classify every file before writing any, so that a refusal delivers nothing."""
    rules = load_rules()
    entries = tracked_files(repo)
    unknown = [path for path, _ in entries if layer_of(path, rules) is None]
    if unknown:
        return fail(f"no layer in {LAYERS_PATH.name} for: {', '.join(unknown)}")
    delivered = [entry for entry in entries if layer_of(entry[0], rules) == LAYER_DELIVERED]
    left_out = [path for path, _ in entries if layer_of(path, rules) == LAYER_META]
    try:
        pattern = id_pattern(index_trigrams(git(repo, "show", f"HEAD:{INDEX_PATH}").decode(ENCODING)))
    except subprocess.CalledProcessError:
        return fail(f"no {INDEX_PATH} at HEAD: the IDs to remove cannot be known")
    output.mkdir(parents=True, exist_ok=True)
    findings = write_delivered(repo, output, delivered, pattern, left_out)
    left = check_output(output, pattern, rules)
    unproved = proof(repo, output, demo)
    problems = left + unproved
    report = {"commit": git(repo, "rev-parse", "HEAD").decode(ENCODING).strip(), "delivered": [path for path, _ in delivered],
              "leftOut": left_out, **findings, "idsOutsideComments": workshop_citations(repo, entries, pattern),
              "checks": {"noIdLeft": not left, "sameBehaviour": not unproved}, "problems": problems}
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


def main(argv=None, proof=prove):
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
        report = json.loads(Path(f"{output}{REPORT_SUFFIX}").read_text(encoding=ENCODING))
        print(f"agnos-meta-release: {len(report['delivered'])} files, {sum(report['removed'].values())} IDs removed, "
              f"{len(report['toRead'])} lines to read, {output} written in {time.perf_counter() - started:{DURATION_FORMAT}} s")
    return code


if __name__ == "__main__":
    sys.exit(main())
