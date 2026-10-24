"""agnos-trace history: who worked on the process elements and on the code, from the repository's git history.

Implements FTR-HST-001 after ADR-HST-001. Loaded by trace_matrix.py only with --history (DEC-HST-001, RQ-HST-015).
Python >= 3.9, standard library only; git is read through its command line, never through a library.
"""
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

# RQ-TRC-067: a literal written more than once is a named constant.
ENCODING = "utf-8"
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
              f"%(trailers:key=Co-authored-by,valueonly,separator=%x1d)")
LOG_FORMAT = RECORD + "%x1f".join(LOG_FIELDS) + FIELD
SHORT_HASH = 10
CONTACT_RE = re.compile(r"^\s*(.*?)\s*<([^<>]*)>\s*$")
MAILMAP_CHUNK = 200                                # contacts per `git check-mailmap` call, within the command-line limit


class HistoryUnavailable(Exception):
    """The repository cannot give a history; the page is built without one (RQ-HST-012)."""


class GitError(Exception):
    """A git command failed."""


def git(args, cwd):
    """The standard output of one git command run in cwd."""
    try:
        done = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding=ENCODING,
                              errors="replace")
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
        git([REV_PARSE, "--verify", "--quiet", "HEAD"], top)
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
    return (m.group(1), m.group(2)) if m else None


def parse_header(record):
    """A commit of one log record: hash, parents, raw and mapped author, author date, subject, co-authors."""
    parts = record.split(FIELD)
    full, parents, raw_name, raw_mail, name, mail, date, subject, trailers = parts[:len(LOG_FIELDS)]
    co_authors = [c for c in (parse_contact(t) for t in trailers.split(TRAILER_SEPARATOR) if t.strip()) if c]
    return {KEY_HASH: full, KEY_PARENTS: parents.split(), KEY_RAW: (raw_name, raw_mail), KEY_AUTHOR: (name, mail),
            KEY_DATE: date, KEY_SUBJECT: subject, KEY_CO_AUTHORS: co_authors}


def log_args(since=None, depth=None, paths=()):
    """The options of `git log` for the history read (RQ-HST-001): git applies both limits."""
    args = ["log", f"--format={LOG_FORMAT}", "--topo-order"]
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
            name = min(names, key=lambda n: (-names[n], n))
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
