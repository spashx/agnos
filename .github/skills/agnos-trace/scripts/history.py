"""agnos-trace history: who worked on the process elements and on the code, from the repository's git history.

Implements FTR-HST-001 after ADR-HST-001. Loaded by trace_matrix.py only with --history (DEC-HST-001, RQ-HST-015).
Python >= 3.9, standard library only; git is read through its command line, never through a library.
"""
import datetime
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

# RQ-TRC-067: a literal written more than once is a named constant.
ENCODING = "utf-8"
ERRORS = "replace"
HEAD = "HEAD"
KEY_NAME = "name"
KEY_EMAIL = "email"
KEY_KIND = "kind"
KEY_COMMITS = "commits"
KEY_CO_COMMITS = "coCommits"
KIND_HUMAN = "human"
KIND_AGENT = "agent"
KIND_TOGETHER = "together"
MERGED_BY_EMAIL = "email"
MERGED_BY_MAILMAP = "mailmap"
KEY_NAMES = "names"
KEY_EMAILS = "emails"
KEY_HASH = "hash"
KEY_PARENTS = "parents"
KEY_RAW = "raw"
KEY_AUTHOR = "author"
KEY_DATE = "date"
KEY_SUBJECT = "subject"
KEY_CO_AUTHORS = "coAuthors"
KEY_SPELLINGS = "spellings"
REV_PARSE = "rev-parse"
TOPO_ORDER = "--topo-order"

AGENTS_PATH = Path(__file__).resolve().parent.parent / "assets" / "agents.json"     # DEC-HST-003

# RQ-HST-012: the causes for which the page is built without history.
CAUSE_NO_GIT = "git is not installed"
CAUSE_NO_TREE = "the process folder is not inside a git working tree"
CAUSE_NO_COMMIT = "the repository has no commit"

# DEC-HST-002, DEC-HST-003: one record per commit, its fields split by unit separators; %aN and %aE apply .mailmap.
RECORD = "\x1e"
FIELD = "\x1f"
TRAILER_SEPARATOR = "\x1d"
LOG_FIELDS = ("%H", "%P", "%an", "%ae", "%aN", "%aE", "%aI", "%s",
              "%(trailers:key=Co-authored-by,valueonly,separator=%x1d)")
LOG_FORMAT = RECORD + "%x1f".join(LOG_FIELDS) + FIELD
SHORT_HASH = 10
CONTACT_RE = re.compile(r"^([^<>]*)<([^<>]*)>\s*$")
MAILMAP_CHUNK = 200                                # contacts per `git check-mailmap` call, within the command-line limit

# DEC-HST-002: zero-context patches with renames, paths written as they are, every parent of a merge walked.
QUOTE_OFF = ("-c", "core.quotepath=false")
PATCH_OPTIONS = ("-p", "-U0", "-M", "--no-color", "--no-ext-diff", "--no-textconv")
WALK_OPTIONS = ("-m", "--parents")
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
DIFF_PREFIX = "diff --git "
SECOND_SIDE = " b/"
OLD_PREFIX = "--- "
NEW_PREFIX = "+++ "
RENAME_FROM = "rename from "
RENAME_TO = "rename to "
NULL_PATH = "/dev/null"
SIDE_PREFIX = 2                                    # "a/" or "b/" before a path of a patch
NO_NEWLINE = "\\"                                  # "\ No newline at end of file", inside a hunk
MAX_AGE = "--max-age="
UTC_MARK = "Z"
UTC_OFFSET = "+00:00"
QUOTE = '"'
ESCAPE_RE = re.compile(rb"\\([0-7]{3}|.)")
ESCAPES = {b"t": b"\t", b"n": b"\n", b"r": b"\r", b"a": b"\a", b"b": b"\b", b"f": b"\f", b"v": b"\v"}
OCTAL = 8
OCTAL_DIGITS = 3


class HistoryUnavailable(Exception):
    """The repository cannot give a history; the page is built without one (RQ-HST-012)."""


class GitError(Exception):
    """A git command failed."""


def git(args, cwd):
    """The standard output of one git command run in cwd."""
    try:
        done = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding=ENCODING,
                              errors=ERRORS)
    except FileNotFoundError:
        raise HistoryUnavailable(CAUSE_NO_GIT) from None
    if done.returncode != 0:
        raise GitError(done.stderr.strip() or f"git {args[0]} failed")
    return done.stdout


# ---- repository --------------------------------------------------------------------------------------------------
# RQ-HST-012, DEC-HST-001
class Repository:
    """The working tree holding a folder: its top folder and whether it is a shallow clone."""

    def __init__(self, top, shallow):
        self.top = top
        self.shallow = shallow


def check_repository(folder):
    """The repository holding folder, or HistoryUnavailable naming why there is none to read."""
    git(["--version"], folder)
    try:
        top = Path(git([REV_PARSE, "--show-toplevel"], folder).strip())
    except GitError:
        raise HistoryUnavailable(CAUSE_NO_TREE) from None
    try:
        git([REV_PARSE, "--verify", "--quiet", HEAD], top)
    except GitError:
        raise HistoryUnavailable(CAUSE_NO_COMMIT) from None
    shallow = git([REV_PARSE, "--is-shallow-repository"], top).strip() == "true"
    return Repository(top, shallow)


# ---- agents ------------------------------------------------------------------------------------------------------
# RQ-HST-005, DEC-HST-003
class AgentPatterns:
    """The patterns that class an identity as an agent, on its name and on its e-mail."""

    def __init__(self, names, emails):
        self.names = names
        self.emails = emails

    def is_agent(self, name, email):
        return any(p.search(name) for p in self.names) or any(p.search(email) for p in self.emails)


def compile_agent_patterns(spec):
    """AgentPatterns from {"name": [regex], "email": [regex]}, matched ignoring case."""
    return AgentPatterns([re.compile(p, re.I) for p in spec.get(KEY_NAME, [])],
                         [re.compile(p, re.I) for p in spec.get(KEY_EMAIL, [])])


def load_agent_patterns(path=AGENTS_PATH):
    return compile_agent_patterns(json.loads(Path(path).read_text(encoding=ENCODING)))


# ---- commits -----------------------------------------------------------------------------------------------------
# DEC-HST-002: the commits of the history read, newest first.
def parse_contact(text):
    """(name, e-mail) of 'Name <e-mail>', or None."""
    m = CONTACT_RE.match(text)
    return (m.group(1).strip(), m.group(2)) if m else None


def parse_header(record):
    """A commit of one log record: hash, parents, raw and mapped author, author date, subject, co-authors."""
    parts = record.split(FIELD)
    full, parents, raw_name, raw_mail, name, mail, date, subject, trailers = parts[:len(LOG_FIELDS)]
    co_authors = [c for c in (parse_contact(t) for t in trailers.split(TRAILER_SEPARATOR) if t.strip()) if c]
    return {KEY_HASH: full, KEY_PARENTS: parents.split(), KEY_RAW: (raw_name, raw_mail), KEY_AUTHOR: (name, mail),
            KEY_DATE: date, KEY_SUBJECT: subject, KEY_CO_AUTHORS: co_authors}


def log_args(since=None, depth=None, paths=(), options=()):
    """The options of `git log` for the history read (RQ-HST-001): git applies both limits."""
    args = [*QUOTE_OFF, "log", f"--format={LOG_FORMAT}", TOPO_ORDER, *options]
    if since:
        args.append(f"--since={since}")
    if depth:
        args.append(f"--max-count={depth}")
    return args + ["--", *paths] if paths else args


def read_commits(repo, paths=(), since=None, depth=None):
    """The commits of the history read, newest first, merges included (they are walked, never credited)."""
    out = git(log_args(since, depth, paths), repo.top)
    return [parse_header(r) for r in out.split(RECORD) if r.strip()]


# ---- identities --------------------------------------------------------------------------------------------------
# RQ-HST-004, DEC-HST-003
def map_contacts(repo, contacts):
    """{(name, e-mail): (name, e-mail) after .mailmap}, from `git check-mailmap`."""
    contacts = sorted(set(contacts))
    mapped = {}
    for start in range(0, len(contacts), MAILMAP_CHUNK):
        chunk = contacts[start:start + MAILMAP_CHUNK]
        lines = git(["check-mailmap", *(f"{n} <{m}>" for n, m in chunk)], repo.top).splitlines()
        for contact, line in zip(chunk, lines):
            mapped[contact] = parse_contact(line) or contact
    return mapped


class Identities:
    """The contributors of the history with every name and address seen: a human is one e-mail address, ignoring case;
    an agent is one name and e-mail, since the models of one vendor share a no-reply address (RQ-HST-004)."""

    def __init__(self, patterns):
        self.patterns = patterns
        self.by_key = {}

    def key_of(self, contact):
        name, mail = contact
        if self.patterns.is_agent(name, mail):
            return KIND_AGENT, f"{name.lower()} <{mail.lower()}>"
        return KIND_HUMAN, mail.lower()

    def add(self, raw, mapped, role):
        kind, key = self.key_of(mapped)
        person = self.by_key.setdefault(key, {KEY_KIND: kind, KEY_NAMES: Counter(), KEY_RAW: set(), KEY_SPELLINGS: set(),
                                              KEY_EMAILS: set(), MERGED_BY_MAILMAP: False, KEY_COMMITS: 0,
                                              KEY_CO_COMMITS: 0})
        person[KEY_NAMES][mapped[0]] += 1
        person[KEY_RAW].add(raw[0])
        person[KEY_SPELLINGS].add(mapped)
        person[KEY_EMAILS].update({raw[1].lower(), mapped[1].lower()})
        person[MERGED_BY_MAILMAP] |= raw != mapped
        person[role] += 1
        return key

    def people(self):
        """The identities as the data file holds them, by number of commits from the highest, then by name."""
        result = []
        for key, person in self.by_key.items():
            names = person[KEY_NAMES]
            name = min(names, key=lambda n, seen=names: (-seen[n], n))
            merged = ([MERGED_BY_EMAIL] if len(person[KEY_SPELLINGS]) > 1 else []) +                      ([MERGED_BY_MAILMAP] if person[MERGED_BY_MAILMAP] else [])
            result.append({"key": key, KEY_NAME: name, KEY_NAMES: sorted(set(names) | person[KEY_RAW]),
                           KEY_EMAILS: sorted(person[KEY_EMAILS]), "mergedBy": sorted(merged), KEY_KIND: person[KEY_KIND],
                           KEY_COMMITS: person[KEY_COMMITS], KEY_CO_COMMITS: person[KEY_CO_COMMITS]})
        result.sort(key=lambda p: (-(p[KEY_COMMITS] + p[KEY_CO_COMMITS]), p[KEY_NAME], p["key"]))
        return result


def commit_kind(kinds):
    """human, agent or together, from the kinds of a commit's contributors (RQ-HST-005)."""
    if KIND_AGENT not in kinds:
        return KIND_HUMAN
    return KIND_AGENT if KIND_HUMAN not in kinds else KIND_TOGETHER


def identify(repo, commits, patterns):
    """(people, commits): the identities of the non-merge commits, and those commits with their author and co-authors
    as indexes into people and their kind; a merge's committer and author are never read as contributors."""
    authored = [c for c in commits if len(c[KEY_PARENTS]) <= 1]
    mapped = map_contacts(repo, [a for c in authored for a in c[KEY_CO_AUTHORS]])
    identities = Identities(patterns)
    keys = []
    for commit in authored:
        author = identities.add(commit[KEY_RAW], commit[KEY_AUTHOR], KEY_COMMITS)
        co = [identities.add(a, mapped[a], KEY_CO_COMMITS) for a in commit[KEY_CO_AUTHORS]]
        keys.append((author, [k for k in dict.fromkeys(co) if k != author]))
    people = identities.people()
    index = {p.pop("key"): n for n, p in enumerate(people)}
    result = []
    for commit, (author, co) in zip(authored, keys):
        contributors = [index[author]] + [index[k] for k in co]
        result.append({KEY_HASH: commit[KEY_HASH][:SHORT_HASH], KEY_DATE: commit[KEY_DATE],
                       KEY_SUBJECT: commit[KEY_SUBJECT], KEY_AUTHOR: index[author], KEY_CO_AUTHORS: [index[k] for k in co],
                       KEY_KIND: commit_kind({people[i][KEY_KIND] for i in contributors})})
    return people, result


# ---- line tracking -----------------------------------------------------------------------------------------------
# RQ-HST-002, RQ-HST-003, DEC-HST-002
def git_lines(args, cwd):
    """The output lines of one git command, read as bytes so that a carriage return inside a line stays in it."""
    try:
        process = subprocess.Popen(["git", *args], cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        raise HistoryUnavailable(CAUSE_NO_GIT) from None
    with process:
        for raw in process.stdout:
            yield raw.rstrip(b"\n").decode(ENCODING, errors=ERRORS)
        error = process.stderr.read().decode(ENCODING, errors=ERRORS).strip()
    if process.returncode != 0:
        raise GitError(error or f"git {args[0]} failed")


def unquote(path):
    """A path as git writes it, quoted with C escapes when it holds a quote, a backslash or a control character."""
    if not (len(path) > 1 and path.startswith(QUOTE) and path.endswith(QUOTE)):
        return path

    def one(m):
        code = m.group(1)
        return bytes([int(code, OCTAL)]) if len(code) == OCTAL_DIGITS else ESCAPES.get(code, code)
    return ESCAPE_RE.sub(one, path[1:-1].encode(ENCODING)).decode(ENCODING, errors=ERRORS)


def side_path(text):
    """The path of a '--- a/x' or '+++ b/x' line, or None for /dev/null."""
    path = unquote(text)
    return None if path == NULL_PATH else path[SIDE_PREFIX:]


def same_path(header):
    """The path of 'diff --git a/x b/x' when both sides are the same path, else None (the next lines tell)."""
    rest = header[len(DIFF_PREFIX):]
    size = (len(rest) - len(SECOND_SIDE) - SIDE_PREFIX) // 2
    middle = SIDE_PREFIX + size
    first, second = rest[SIDE_PREFIX:middle], rest[middle + len(SECOND_SIDE):]
    return first if first == second and rest[middle:middle + len(SECOND_SIDE)] == SECOND_SIDE else None


class FileDiff:
    """One file of a patch: its old and new paths (None when absent) and its hunks (old start, old count, new start,
    new count)."""

    def __init__(self, path):
        self.old = self.new = path
        self.hunks = []


def parse_patch(lines):
    """[(header record or None, [FileDiff])] in the order of the output; a hunk's lines are counted, never parsed, so
    that a changed line that looks like a header is read as a line."""
    entries, diffs, diff, pending = [], None, None, 0
    for line in lines:
        if pending:
            if not line.startswith(NO_NEWLINE):
                pending -= 1
            continue
        if line.startswith(RECORD):
            diffs, diff = [], None
            entries.append((line[1:], diffs))
            continue
        if diffs is None:
            diffs = []
            entries.append((None, diffs))
        if line.startswith(DIFF_PREFIX):
            diff = FileDiff(same_path(line))
            diffs.append(diff)
        elif diff is None:
            continue
        elif line.startswith(RENAME_FROM):
            diff.old = unquote(line[len(RENAME_FROM):])
        elif line.startswith(RENAME_TO):
            diff.new = unquote(line[len(RENAME_TO):])
        elif line.startswith(OLD_PREFIX):
            diff.old = side_path(line[len(OLD_PREFIX):])
        elif line.startswith(NEW_PREFIX):
            diff.new = side_path(line[len(NEW_PREFIX):])
        else:
            m = HUNK_RE.match(line)
            if m:
                old_start, old_count, new_start, new_count = (int(g) if g is not None else 1 for g in m.groups())
                diff.hunks.append((old_start, old_count, new_start, new_count))
                pending = old_count + new_count
    return entries


def shift(first, last, hunks):
    """(the range [first, last] of a file's new version in its old version, or None when all its lines were added; the
    lines the hunks changed in it). The old range spans the unchanged lines of the range and the old lines of the hunks
    that touch it, as `git log -L` follows a range; a hunk's removed lines count in proportion of its added lines in the
    range, a pure removal inside the range counts whole."""
    low = high = None
    delta = changed = 0                        # old line = new line + delta, for the unchanged lines past the hunks seen
    position = first

    def keep(start, end):
        nonlocal low, high
        low = start if low is None else min(low, start)
        high = end if high is None else max(high, end)

    for old_start, old_count, new_start, new_count in hunks:
        start = new_start if new_count else new_start + 1
        if start > last:
            break
        if max(position, first) <= start - 1:
            keep(max(position, first) + delta, min(start - 1, last) + delta)
        if new_count:
            overlap = min(new_start + new_count - 1, last) - max(new_start, first) + 1
            touched = overlap > 0
            if touched:
                changed += overlap + (old_count * overlap + new_count // 2) // new_count
        else:
            touched = first <= new_start < last
            if touched:
                changed += old_count
        if touched and old_count:
            keep(old_start, old_start + old_count - 1)
        delta += old_count - new_count
        position = start + new_count
    if max(position, first) <= last:
        keep(max(position, first) + delta, last + delta)
    return ((low, high) if low is not None else None), changed


def transform(state, diffs, commit, tally):
    """The ranges of state, {path: [(key, first, last)]} in a version's coordinates (first None: the whole file), in the
    coordinates of the version the diffs start from; each range the diffs touch is credited to commit in tally, unless None."""
    by_new = {d.new: d for d in diffs if d.new is not None}
    moved = {}
    for path, items in state.items():
        diff = by_new.get(path)
        if diff is None:
            moved.setdefault(path, []).extend(items)
            continue
        kept = []
        for key, first, last in items:
            if first is None:
                span, changed = (None, None), sum(old + new for _, old, _, new in diff.hunks)
            else:
                span, changed = shift(first, last, diff.hunks)
            if commit is not None and changed:
                by_commit = tally.setdefault(key, {})
                by_commit[commit] = by_commit.get(commit, 0) + changed
            if span is not None:
                kept.append((key, *span))
        if diff.old is not None and kept:
            moved.setdefault(diff.old, []).extend(kept)
    return moved


def union(into, state):
    """Adds state's ranges to into; a range of one key met twice spans both, since two children of a commit can carry
    it back slightly differently."""
    for path, items in state.items():
        by_key = {(key, first is None): (key, first, last) for key, first, last in into.get(path, [])}
        for key, first, last in items:
            seen = by_key.get((key, first is None))
            if seen is not None and first is not None:
                first, last = min(first, seen[1]), max(last, seen[2])
            by_key[(key, first is None)] = (key, first, last)
        into[path] = sorted(by_key.values(), key=lambda item: (item[0], item[1] or 0))


def author_cutoff(repo, since):
    """The time stamp before which a commit was not authored in the period read, or None (RQ-HST-001): git's --since
    is on the committer date, so the author date is checked here."""
    if not since:
        return None
    answer = git([REV_PARSE, f"--since={since}"], repo.top).strip()
    return int(answer[len(MAX_AGE):]) if answer.startswith(MAX_AGE) else None


def timestamp(commit):
    """The author time stamp of a commit; git writes UTC as 'Z', which Python reads only from 3.11."""
    date = commit[KEY_DATE]
    return datetime.datetime.fromisoformat(date[:-1] + UTC_OFFSET if date.endswith(UTC_MARK) else date).timestamp()


def authored_since(commit, cutoff):
    return cutoff is None or timestamp(commit) >= cutoff


def commit_groups(entries):
    """[(commit, [diffs per parent])] from the log's entries: git writes a merge once per parent, one after the other."""
    groups = []
    for record, diffs in entries:
        if record is None:
            continue
        commit = parse_header(record)
        if groups and groups[-1][0][KEY_HASH] == commit[KEY_HASH]:
            groups[-1][1].append(diffs)
        else:
            groups.append((commit, [diffs]))
    return groups


def tracked_files(repo, paths):
    out = git([*QUOTE_OFF, "ls-files", "-z", "--", *paths], repo.top)
    return set(filter(None, out.split("\0")))


def read_history(repo, ranges, wholes, paths=(), since=None, depth=None):
    """(commits, credits): the commits authored in the period read, newest first, merges included; and
    {key: {full hash: changed lines}}, the non-merge commits that changed each range. ranges is {path: [(key, first,
    last)]} and wholes {path: [key]}, at the working tree, paths relative to the top of the repository; paths limits
    the history read to these folders. The uncommitted changes credit no one."""
    tracked = tracked_files(repo, paths)
    state = {}
    for path, items in ranges.items():
        state.setdefault(path, []).extend(items)
    for path, keys in wholes.items():
        state.setdefault(path, []).extend((key, None, None) for key in keys)
    state = {path: items for path, items in state.items() if path in tracked}
    tally = {}
    for _, diffs in parse_patch(git_lines([*QUOTE_OFF, "diff", *PATCH_OPTIONS, HEAD, "--", *paths], repo.top)):
        state = transform(state, diffs, None, tally)
    cutoff = author_cutoff(repo, since)
    groups = commit_groups(parse_patch(git_lines(log_args(since, depth, paths, PATCH_OPTIONS + WALK_OPTIONS), repo.top)))
    commits, states = [], {}
    for position, (commit, per_parent) in enumerate(groups):
        here = state if position == 0 else states.pop(commit[KEY_HASH], None)
        authored = authored_since(commit, cutoff)
        if authored:
            commits.append(commit)
        if here is None:
            continue                                         # reached by no commit read: nothing to carry back
        parents = commit[KEY_PARENTS]
        credited = commit[KEY_HASH] if authored and len(parents) <= 1 else None
        if not parents:
            transform(here, per_parent[0], credited, tally)
            continue
        for number, parent in enumerate(parents):
            diffs = per_parent[number] if number < len(per_parent) else []
            union(states.setdefault(parent, {}), transform(here, diffs, credited, tally))
    return commits, tally


# ---- the commit graph --------------------------------------------------------------------------------------------
# RQ-HST-024, DEC-HST-010: the path-limited log's parents are rewritten by git's history simplification, so the graph
# is read by a light log of its own, with no path and no patch.
KEY_GRAPH = "graph"
KEY_BRANCHES = "branches"
KEY_NODES = "nodes"
KEY_BRANCH = "branch"
KEY_COMMIT = "commit"
DEFAULT_BRANCHES = ("main", "master")
GRAPH_FORMAT = RECORD + "%x1f".join(("%H", "%P", "%aI", "%s"))
TIP_FORMAT = "%(objectname)%1f%(refname:short)"
MERGE_NAMES = (re.compile(r"^Merge branch '([^']+)'"),                   # git merge
               re.compile(r"^Merge pull request #\d+ from [^/\s]+/(\S+)"),  # GitHub
               re.compile(r"^Merge (?!branch )(\S+) into \S+"))             # Merge X into Y


def read_graph(repo, since=None):
    """The commits of the repository from HEAD, newest first in topological order: hash, parents, date, subject."""
    out = git(["log", f"--format={GRAPH_FORMAT}", TOPO_ORDER, *([f"--since={since}"] if since else [])], repo.top)
    nodes = []
    for record in out.split(RECORD):
        if record.strip():
            full, parents, date, subject = record.rstrip("\n").split(FIELD)
            nodes.append({KEY_HASH: full, KEY_PARENTS: parents.split(), KEY_DATE: date, KEY_SUBJECT: subject})
    return nodes


def branch_tips(repo):
    """[(tip hash, name)] of the local branches, and the name of the branch checked out, or None."""
    out = git(["for-each-ref", f"--format={TIP_FORMAT}", "refs/heads"], repo.top)
    tips = [tuple(line.split(FIELD, 1)) for line in out.splitlines() if FIELD in line]
    try:
        current = git(["symbolic-ref", "-q", "--short", HEAD], repo.top).strip() or None
    except GitError:
        current = None                                       # a detached HEAD
    return tips, current


def merge_name(subject):
    """The branch a merge's message names as merged, or None."""
    for pattern in MERGE_NAMES:
        m = pattern.match(subject)
        if m:
            return m.group(1)
    return None


def assign_branches(nodes, tips, current):
    """(names, branch of each node): from the default branch's tip, the other tips oldest first, then the second parent
    of each merge naming its branch, newest first, the first parents are followed until a commit already claimed; the
    commits left take one unnamed branch (None) per first-parent chain."""
    index = {n[KEY_HASH]: i for i, n in enumerate(nodes)}
    branch_of = [None] * len(nodes)
    names, numbers = [], {}

    def claim(start, name):
        if start is None or branch_of[start] is not None:
            return
        if name is None or name not in numbers:
            names.append(name)
            if name is not None:
                numbers[name] = len(names) - 1
        number = len(names) - 1 if name is None else numbers[name]
        i = start
        while i is not None and branch_of[i] is None:
            branch_of[i] = number
            parents = nodes[i][KEY_PARENTS]
            i = index.get(parents[0]) if parents else None

    present = {name: index[tip] for tip, name in tips if tip in index}
    default = next((b for b in DEFAULT_BRANCHES if b in present), current if current in present else None)
    if default is not None:
        claim(present[default], default)
    for name in sorted((n for n in present if n != default), key=lambda n: (-present[n], n)):
        claim(present[name], name)
    for node in nodes:
        name = merge_name(node[KEY_SUBJECT]) if len(node[KEY_PARENTS]) > 1 else None
        if name is not None:
            claim(index.get(node[KEY_PARENTS][1]), name)
    for i in range(len(nodes)):
        claim(i, None)
    return names, branch_of


def graph_block(nodes, names, branch_of, position):
    """The data file's graph: the nodes down to the oldest commit of the timeline, each with its parents among them, its
    branch and its commit index, or, with no commit index, its date and subject; the branches in the order found."""
    last = max((i for i, n in enumerate(nodes) if n[KEY_HASH] in position), default=-1)
    kept = nodes[:last + 1]
    index = {n[KEY_HASH]: i for i, n in enumerate(kept)}
    used = sorted({branch_of[i] for i in range(len(kept))})
    renumber = {old: new for new, old in enumerate(used)}
    result = []
    for i, node in enumerate(kept):
        commit = position.get(node[KEY_HASH])
        item = {KEY_HASH: node[KEY_HASH][:SHORT_HASH], KEY_PARENTS: [index[p] for p in node[KEY_PARENTS] if p in index],
                KEY_BRANCH: renumber[branch_of[i]], KEY_COMMIT: commit}
        if commit is None:
            item[KEY_DATE] = node[KEY_DATE]
            item[KEY_SUBJECT] = node[KEY_SUBJECT]
        result.append(item)
    return {KEY_BRANCHES: [names[old] for old in used], KEY_NODES: result}


def build_graph(repo, since, position):
    nodes = read_graph(repo, since)
    tips, current = branch_tips(repo)
    names, branch_of = assign_branches(nodes, tips, current)
    return graph_block(nodes, names, branch_of, position)


# ---- the history block -------------------------------------------------------------------------------------------
# RQ-HST-006, DEC-HST-004
KIND_ELEMENT = "elements"
KIND_FILE = "files"
KIND_FUNCTION = "functions"
KEY_LIMITS = "limits"
KEY_PEOPLE = "people"


def relative_to(path, top):
    """A path relative to the top of the repository, or None when it lies outside."""
    try:
        return Path(path).resolve().relative_to(top.resolve()).as_posix()
    except ValueError:
        return None


def ranges_to_track(top, documents, files, functions):
    """(ranges, wholes) of read_history: the process elements and the functions by their lines, the files whole; a
    path outside the repository is left out."""
    ranges, wholes = {}, {}
    for path, elements in documents.items():
        where = relative_to(path, top)
        if where is not None:
            ranges.setdefault(where, []).extend(((KIND_ELEMENT, i), first, last) for i, first, last in elements)
    where_of = {shown: relative_to(path, top) for shown, path in files.items()}
    for shown, where in where_of.items():
        if where is not None:
            wholes.setdefault(where, []).append((KIND_FILE, shown))
    for number, (shown, first, last) in enumerate(functions):
        if where_of.get(shown) is not None:
            ranges.setdefault(where_of[shown], []).append(((KIND_FUNCTION, number), first, last))
    return ranges, wholes


def build(folder, documents, files, functions, scope, since=None, depth=None, patterns=None):
    """The data file's history block, for the repository holding folder. documents is {path: [(ID, first, last)]} of
    the process documents, files {shown path: path} of the scanned files, functions [(shown path, first, last)] of the
    call graph in its order (empty without one), scope the folders whose history is read. HistoryUnavailable or
    GitError when the repository cannot be read (RQ-HST-012)."""
    repo = check_repository(folder)
    ranges, wholes = ranges_to_track(repo.top, documents, files, functions)
    paths = sorted({p for p in (relative_to(f, repo.top) for f in scope) if p is not None}) or ["."]
    commits, tally = read_history(repo, ranges, wholes, paths, since, depth)
    authored = sorted((c for c in commits if len(c[KEY_PARENTS]) <= 1), key=lambda c: (timestamp(c), c[KEY_HASH]))
    people, listed = identify(repo, authored, patterns or load_agent_patterns())
    position = {c[KEY_HASH]: n for n, c in enumerate(authored)}
    interventions = {KIND_ELEMENT: {}, KIND_FILE: {}}
    if functions:
        interventions[KIND_FUNCTION] = {}
    for (kind, name), by_commit in tally.items():
        interventions[kind][str(name)] = sorted([position[h], lines] for h, lines in by_commit.items() if h in position)
    dates = [c[KEY_DATE] for c in listed]
    limits = {"since": since or None, "depth": depth or None, KEY_COMMITS: len(listed),
              "first": dates[0] if dates else None, "last": dates[-1] if dates else None, "shallow": repo.shallow}
    return {KEY_LIMITS: limits, KEY_PEOPLE: people, KEY_COMMITS: listed, "interventions": interventions,
            KEY_GRAPH: build_graph(repo, since, position)}


def summary(block):
    """The part of the generator's last line about the history (RQ-HST-006)."""
    kinds = Counter(p[KEY_KIND] for p in block[KEY_PEOPLE])
    return (f"history: {block[KEY_LIMITS][KEY_COMMITS]} commits, {kinds[KIND_HUMAN]} humans, "
            f"{kinds[KIND_AGENT]} agents")
