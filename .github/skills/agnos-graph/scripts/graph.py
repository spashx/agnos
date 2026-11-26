#!/usr/bin/env python3
"""agnos-graph: the state of an AGNOS project at a commit, as one dated JSON file (FTR-TRC-011; ADR-TRC-022).

Procedure and options: ../SKILL.md. Reads the process index and its documents, scans the sources for AGNOS IDs, and, on
request, parses the call graph (callgraph.py, tree-sitter) and reads the history (history.py, git), both beside this
script (DEC-TRC-074, RQ-TRC-129). Holds no coverage, finding nor score: those are the performance center's (RQ-TRC-129).
Python >= 3.9, standard library only (DEC-TRC-001, RQ-TRC-021). Extracted from perf_center.py (TASK-TRC-117).
"""
import argparse
import datetime
import fnmatch
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
# RQ-PLG-036 / DEC-TRC-077: the process folder's names, generated beside this script
import agnos_layout  # noqa: E402
# RQ-TRC-144 / DEC-TRC-084: the graph explorer page, beside this script
import explorer  # noqa: E402
# RQ-QLT-011: the suppression comments hold nothing but the rule, so SonarQube reads them

# RQ-TRC-067: a literal written more than once is a named constant.
PROG = "agnos-graph"
DURATION_FORMAT = ".3f"    # RQ-TRC-107: seconds, three decimals
KEY_UNDEFINED = "undefined"
KEY_KIND = "kind"
KEY_TYPE = "type"
KEY_FIRST = "first"
KEY_LAST = "last"
KEY_STATUS = "status"
KEY_TITLE = "title"
KEY_CODE = "code"
KEY_ELEMENT = "element"
KEY_CONTAINS = "contains"
KEY_REFS = "refs"
KEY_REPLACE = "replace"
KEY_DELIVERY = "delivery"
KEY_HISTORY = "history"
KEY_CALL_GRAPH = "callGraph"
KEY_APPEND = "append"
STORE_TRUE = "store_true"
ENCODING = "utf-8"
TYPE_TASK = "TASK"
TYPE_RQ = "RQ"
TIER_RE = re.compile(r"^- \*\*Tier\*\*:\s*([SML])\b")     # RQ-TRC-068: a task's tier, as the AGNOS template writes it

INDEX_NAME = agnos_layout.INDEX
ID_PATTERN = r"(?:FTR|RQ|ADR|DEC|PLAN|TASK)-[A-Z]{3}-[0-9]{3}"
NUMBER_LENGTH = 3
INDEX_TITLE_FIELD = 3                          # "ID|first-last|status|title": the title is the fourth field
INDEX_FIELDS = INDEX_TITLE_FIELD + 1
PREFIX_CUT = -(NUMBER_LENGTH + 1)              # "RQ-ABC-001"[:PREFIX_CUT] == "RQ-ABC"
LINE_TEXT_MAX = 200                            # characters of a line kept as evidence (DEC-TRC-003)
ELEMENT_FIELDS = ("id", KEY_KIND, KEY_TYPE, "tri", "doc", KEY_FIRST, KEY_LAST, KEY_STATUS, KEY_TITLE)

# RQ-TRC-134 to RQ-TRC-136, DEC-TRC-079, DEC-TRC-080: the sections of a feature, ADR or plan.
KEY_SECTIONS = "sections"
TYPE_SECTION = "SEC"
SECTIONED_TYPES = frozenset({"FTR", "ADR", "PLAN"})
SECTION_LEVEL, SUBSECTION_LEVEL = 2, 3                 # "##" and "###"
HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(\S.*)$")   # the closing '#' and blanks are stripped from the title
FENCE_PREFIXES = ("```", "~~~")
SECTION_MARK, SUBSECTION_MARK, REPEAT_MARK = "#", "/", "."
FIRST_REPEAT = 2                                       # the second heading of one title is suffixed ".2"

# RQ-TRC-138 to RQ-TRC-140, DEC-TRC-081 to DEC-TRC-083: the link field of each citation of a requirement, a decision, a
# task or a plan.
KEY_LINKS = "links"
FIELD_TEXT = "text"                                    # a citation held by no link field of its source's type
FIELD_REQUIREMENTS, FIELD_ADRS, FIELD_DEPENDENCIES = "Requirement refs", "ADR refs", "Dependencies"
LINK_FIELDS = {"RQ": frozenset({FIELD_DEPENDENCIES}),
               "DEC": frozenset({FIELD_REQUIREMENTS, FIELD_DEPENDENCIES}),
               "TASK": frozenset({FIELD_REQUIREMENTS, FIELD_ADRS, FIELD_DEPENDENCIES}),
               "PLAN": frozenset({FIELD_REQUIREMENTS, FIELD_ADRS})}
FIELD_LINE_RE = re.compile(r"^\s*-\s*\*\*([^*]+)\*\*\s*:")   # "- **<name>**:", as the templates write a field

# RQ-TRC-006, DEC-TRC-001: what a source folder holds that can carry an ID; every list is replaceable from the command
# line.
DEFAULT_EXTENSIONS = frozenset(
    ".c .cc .cpp .cxx .c++ .h .hh .hpp .hxx .h++ .inl .ipp .tpp .m .mm .cs .fs .vb .java .kt .kts .scala .groovy "
    ".gradle .go .rs .swift .dart .py .pyi .pyw .rb .php .pl .pm .lua .r .jl .ex .exs .erl .hs .clj .js .jsx .mjs "
    ".cjs .ts .tsx .vue .svelte .html .htm .css .scss .sass .less .sql .sh .bash .zsh .fish .ps1 .psm1 .psd1 .bat .cmd "
    ".cmake .mk .yml .yaml .toml .ini .cfg .xml .proto .graphql .tf .glsl .hlsl .metal .cu .asm .s .v .sv .vhd".split())
DEFAULT_NAMES = frozenset({"CMakeLists.txt", "Makefile", "makefile", "GNUmakefile", "Dockerfile", "Jenkinsfile",
                           "Rakefile", "Gemfile", "meson.build", "BUILD", "BUILD.bazel", "WORKSPACE"})
DEFAULT_EXCLUDES = (".git", ".hg", ".svn", "node_modules", "build", "build-*", "build_*", "cmake-build-*", "dist",
                    "out", "_deps", ".venv", "venv", "__pycache__", ".idea", ".vs", ".vscode", "target", "bin", "obj")
LIST_SEPARATOR = ", "                          # RQ-TRC-119: how a scan list is printed
ORIGIN_DEFAULT, ORIGIN_USER, ORIGIN_ALWAYS = "default", "user", "always"
MAX_SOURCE_BYTES = 2 * 1024 * 1024            # a larger file is taken as generated or as data (DEC-TRC-003)
BINARY_PROBE_BYTES = 8192                      # a NUL byte in this head marks a binary file
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%MZ"
GIT_TIMEOUT = 60                               # seconds allowed to read the HEAD commit (RQ-TRC-130)

SCRIPTS_DIR = Path(__file__).resolve().parent
CALLGRAPH_PATH = SCRIPTS_DIR / "callgraph.py"
CALLGRAPH_MODULE = "agnos_graph_callgraph"
HISTORY_PATH = SCRIPTS_DIR / "history.py"        # FTR-HST-001, ADR-HST-001
HISTORY_MODULE = "agnos_graph_history"

# DEC-TRC-003: an ID is not part of a longer word or number; a range is "<A> to <B>", "<A>–<B>", "<A>—<B>", "<A>..<B>"
# or "<A>-<B>".
ID_RE = re.compile(rf"(?<![A-Za-z0-9]){ID_PATTERN}(?![0-9])")
FULL_ID_RE = re.compile(rf"^{ID_PATTERN}$")
RANGE_RE = re.compile(rf"(?<![A-Za-z0-9])({ID_PATTERN})(?:\s+to\s+|\s*(?:–|—|\.\.|-)\s*)({ID_PATTERN})(?![0-9])")


class InputError(Exception):
    """An input the graph cannot be built from (RQ-TRC-002, RQ-TRC-129)."""


# ---- IDs ---------------------------------------------------------------------------------------------------------
# RQ-TRC-005, DEC-TRC-003
def extract_ids(text, defined):
    """Every AGNOS ID of the text, a range of one type and trigram counting as the defined IDs between its two ends."""
    found = {m.group(0) for m in ID_RE.finditer(text)}
    for m in RANGE_RE.finditer(text):
        low, high = m.group(1), m.group(2)
        prefix = low[:PREFIX_CUT]
        if prefix != high[:PREFIX_CUT] or low >= high:
            continue
        lo, hi = int(low[PREFIX_CUT + 1:]), int(high[PREFIX_CUT + 1:])
        found.update(i for i in defined if i[:PREFIX_CUT] == prefix and lo < int(i[PREFIX_CUT + 1:]) < hi)
    return found


# RQ-TRC-005
def id_type(element_id):
    """The type of an ID: its part before the first dash."""
    return element_id.split("-", 1)[0]


# DEC-TRC-003
def evidence(line_number, text):
    """A line kept as the proof of a link: its number and its text, trimmed (DEC-TRC-003)."""
    return [line_number, text.strip()[:LINE_TEXT_MAX]]


# ---- model -------------------------------------------------------------------------------------------------------
# DEC-TRC-002, DEC-TRC-074
class Model:
    """The traceability graph: elements (process elements, undefined IDs), source files, and the links between them."""

    def __init__(self):
        self.elements = {}   # id -> element dict, in index order
        self.edges = {}      # (source, target, kind) -> list of [line, text]; kind: contains | refs | code
        self.files = {}      # source path -> {"path", "ids"}

    # DEC-TRC-002
    def add_element(self, element):
        """Adds or replaces an element, keyed by its ID."""
        self.elements[element["id"]] = element

    # RQ-TRC-007
    def ensure(self, element_id):
        """The element of an ID, made an undefined element when the index does not define it (RQ-TRC-007)."""
        if element_id not in self.elements:
            self.add_element({"id": element_id, KEY_KIND: KEY_UNDEFINED, KEY_TYPE: id_type(element_id),
                              "tri": element_id.split("-")[1], "doc": "", KEY_FIRST: 0, KEY_LAST: 0, KEY_STATUS: "",
                              KEY_TITLE: "Not defined in the index"})
        return self.elements[element_id]

    # DEC-TRC-002
    def add_edge(self, source, target, kind, proof=None):
        """Adds a link, with one more proof line when one is given."""
        lines = self.edges.setdefault((source, target, kind), [])
        if proof is not None:
            lines.append(proof)


# ---- process -----------------------------------------------------------------------------------------------------
# RQ-TRC-003
def parse_index(index_path):
    """The rows of the process index: one element per 'ID|first-last|status|title' row, under its '@document' line."""
    rows, doc = [], ""
    for raw in index_path.read_text(encoding=ENCODING).splitlines():
        if raw.startswith("@"):
            doc = raw[1:].strip()
            continue
        parts = raw.split("|", INDEX_TITLE_FIELD)
        if len(parts) != INDEX_FIELDS or not FULL_ID_RE.match(parts[0]):
            continue
        first, _, last = parts[1].partition("-")
        rows.append({"id": parts[0], KEY_KIND: KEY_ELEMENT, KEY_TYPE: id_type(parts[0]), "tri": parts[0].split("-")[1],
                     "doc": doc, KEY_FIRST: int(first), KEY_LAST: int(last or first), KEY_STATUS: parts[2].strip(),
                     KEY_TITLE: parts[INDEX_TITLE_FIELD].strip()})
    return rows


# RQ-TRC-003
def resolve_document(process_dir, doc):
    """A document path of the index: relative to the process folder's parent, else to the process folder itself."""
    candidates = [process_dir.parent / doc, process_dir / Path(*Path(doc).parts[1:]) if len(Path(doc).parts) > 1
                  else process_dir / doc, process_dir / doc]
    return next((c for c in candidates if c.is_file()), None)


# RQ-TRC-004, DEC-TRC-003
def add_containment(model, members):
    """Links each element of one document to the element whose range most closely encloses its own."""
    for child in members:
        parents = [p for p in members if p is not child
                   and p[KEY_FIRST] <= child[KEY_FIRST] and child[KEY_LAST] <= p[KEY_LAST]
                   and (p[KEY_FIRST], p[KEY_LAST]) != (child[KEY_FIRST], child[KEY_LAST])]
        if parents:
            parent = min(parents, key=lambda p: p[KEY_LAST] - p[KEY_FIRST])
            model.add_edge(parent["id"], child["id"], KEY_CONTAINS)


# RQ-TRC-005, RQ-TRC-007, DEC-TRC-003
def add_document_references(model, members, lines, defined):
    """Links each element to the IDs of its own lines: those of its range that no element it contains holds."""
    owner = [None] * (len(lines) + 1)
    for element in sorted(members, key=lambda e: e[KEY_LAST] - e[KEY_FIRST], reverse=True):
        for ln in range(element[KEY_FIRST], min(element[KEY_LAST], len(lines)) + 1):
            owner[ln] = element["id"]
    for ln, text in enumerate(lines, 1):
        if owner[ln] is None:
            continue
        for target in sorted(extract_ids(text, defined) - {owner[ln]}):
            model.ensure(target)
            model.add_edge(owner[ln], target, KEY_REFS, evidence(ln, text))


# RQ-TRC-003 to RQ-TRC-005, RQ-TRC-129 (TASK-TRC-001, TASK-TRC-117)
def build_process_model(process_dir):
    """The elements of the process folder's index, their containment and their references."""
    process_dir = Path(process_dir)
    index_path = process_dir / INDEX_NAME
    if not index_path.is_file():
        raise InputError(f"{index_path} not found: run the agnos-index skill first, or give the folder holding it")
    model = Model()
    rows = parse_index(index_path)
    for row in rows:
        model.add_element(row)
    defined = set(model.elements)
    by_doc = {}
    for row in rows:
        by_doc.setdefault(row["doc"], []).append(row)
    for doc, members in by_doc.items():
        add_containment(model, members)
        path = resolve_document(process_dir, doc)
        if path is None:
            print(f"{PROG}: warning: {doc} not found, its references are not read", file=sys.stderr)
            continue
        lines = path.read_text(encoding=ENCODING, errors=KEY_REPLACE).splitlines()
        add_document_references(model, members, lines, defined)
    return model


# ---- document sections -------------------------------------------------------------------------------------------
# RQ-TRC-134, RQ-TRC-135, DEC-TRC-079
def headings(lines):
    """[(line, level, title)] of the Markdown headings of a document, those inside a code fence left out."""
    found, fenced = [], False
    for ln, text in enumerate(lines, 1):
        if text.lstrip().startswith(FENCE_PREFIXES):
            fenced = not fenced
            continue
        m = None if fenced else HEADING_RE.match(text)
        if m:
            found.append((ln, len(m.group(1)), m.group(2).rstrip().rstrip(SECTION_MARK).rstrip()))
    return found


# RQ-TRC-134, RQ-TRC-135
def heading_ranges(found, last, level):
    """[(first, last, title)] of the headings of one level: each ends before the next heading of that level or above."""
    ranges = []
    for n, (ln, lvl, title) in enumerate(found):
        if lvl != level:
            continue
        end = next((h[0] - 1 for h in found[n + 1:] if h[1] <= level), last)
        ranges.append((ln, min(end, last), title))
    return ranges


# RQ-TRC-136, DEC-TRC-080
def unique_name(title, taken):
    """The title, suffixed '.2', '.3' from its second occurrence among one parent's children."""
    count = taken.get(title, 0) + 1
    taken[title] = count
    return title if count < FIRST_REPEAT else f"{title}{REPEAT_MARK}{count}"


# RQ-TRC-136, DEC-TRC-080
def section_refs(lines, first, last, inner, defined):
    """[[ID, proofs]] of the IDs cited on a section's own lines, those of its subsections ([(first, last)]) left out."""
    refs = {}
    for ln in range(first, last + 1):
        if any(a <= ln <= b for a, b in inner):
            continue
        for target in sorted(extract_ids(lines[ln - 1], defined)):
            refs.setdefault(target, []).append(evidence(ln, lines[ln - 1]))
    return [[target, proofs] for target, proofs in sorted(refs.items())]


# RQ-TRC-134 to RQ-TRC-136, DEC-TRC-079, DEC-TRC-080
def sections_of_document(document, members, lines, defined):
    """The section nodes of one document: its '##' holding no indexed element, and their '###', in line order."""
    last = min(document[KEY_LAST], len(lines))
    found = [h for h in headings(lines) if document[KEY_FIRST] <= h[0] <= last]
    starts = [m[KEY_FIRST] for m in members if m is not document]
    nodes, top_taken = [], {}

    def node(sid, level, parent, first, end, title, inner):
        return {"id": sid, KEY_TYPE: TYPE_SECTION, "level": level, "parent": parent, "doc": document["doc"],
                KEY_FIRST: first, KEY_LAST: end, KEY_TITLE: title,
                KEY_REFS: section_refs(lines, first, end, inner, defined)}

    for first, end, title in heading_ranges(found, last, SECTION_LEVEL):
        if any(first <= s <= end for s in starts):
            continue
        sid = f"{document['id']}{SECTION_MARK}{unique_name(title, top_taken)}"
        inside = [h for h in found if first < h[0] <= end]
        subs = heading_ranges(inside, end, SUBSECTION_LEVEL)
        nodes.append(node(sid, SECTION_LEVEL, document["id"], first, end, title, [(a, b) for a, b, _ in subs]))
        sub_taken = {}
        for a, b, sub_title in subs:
            nodes.append(node(f"{sid}{SUBSECTION_MARK}{unique_name(sub_title, sub_taken)}", SUBSECTION_LEVEL, sid,
                              a, b, sub_title, []))
    return nodes


# RQ-TRC-134, RQ-TRC-137, DEC-TRC-078: reads the model, never changes it.
def document_sections(process_dir, model):
    """The section nodes of every feature, ADR and plan of the index, in index then line order."""
    process_dir = Path(process_dir)
    defined = {i for i, e in model.elements.items() if e[KEY_KIND] == KEY_ELEMENT}
    by_doc = {}
    for element in model.elements.values():
        if element[KEY_KIND] == KEY_ELEMENT:
            by_doc.setdefault(element["doc"], []).append(element)
    nodes = []
    for doc, members in by_doc.items():
        documents = [m for m in members if m[KEY_TYPE] in SECTIONED_TYPES]
        path = resolve_document(process_dir, doc)
        if not documents or path is None:
            continue
        document = max(documents, key=lambda m: m[KEY_LAST] - m[KEY_FIRST])
        lines = path.read_text(encoding=ENCODING, errors=KEY_REPLACE).splitlines()
        nodes.extend(sections_of_document(document, members, lines, defined))
    return nodes


# ---- element link fields -----------------------------------------------------------------------------------------
# RQ-TRC-139, RQ-TRC-140, DEC-TRC-082, DEC-TRC-083
def line_fields(lines, element):
    """{line: field} over an element's range: a field runs from its line to the next field line or heading; a field
    outside the element type's table, and a line before any field, give FIELD_TEXT."""
    allowed = LINK_FIELDS[element[KEY_TYPE]]
    fields, current = {}, None
    for ln in range(element[KEY_FIRST], min(element[KEY_LAST], len(lines)) + 1):
        text = lines[ln - 1]
        match = FIELD_LINE_RE.match(text)
        if HEADING_RE.match(text):
            current = None
        elif match:
            name = match.group(1).strip()
            current = name if name in allowed else None
        fields[ln] = current or FIELD_TEXT
    return fields


# RQ-TRC-138, RQ-TRC-141, DEC-TRC-081: reads the model, never changes it.
def element_links(process_dir, model):
    """[[source, target, [[line, field]]]] of every refs edge whose source is a requirement, a decision, a task or a plan,
    in edge order, one field per proof line."""
    process_dir = Path(process_dir)
    lines_of, fields_of, rows = {}, {}, []
    for (source, target, kind), proofs in sorted(model.edges.items()):
        element = model.elements.get(source)
        if kind != KEY_REFS or element is None or element[KEY_KIND] != KEY_ELEMENT or element[KEY_TYPE] not in LINK_FIELDS:
            continue
        if source not in fields_of:
            doc = element["doc"]
            if doc not in lines_of:
                path = resolve_document(process_dir, doc)
                lines_of[doc] = path.read_text(encoding=ENCODING, errors=KEY_REPLACE).splitlines() if path else []
            fields_of[source] = line_fields(lines_of[doc], element)
        rows.append([source, target, [[ln, fields_of[source].get(ln, FIELD_TEXT)] for ln, _ in proofs]])
    return rows


# ---- sources -----------------------------------------------------------------------------------------------------
# RQ-TRC-006, DEC-TRC-003
def is_excluded(name, excludes):
    """True when a file or folder name matches one of the exclusion patterns."""
    return any(fnmatch.fnmatchcase(name, pattern) for pattern in excludes)


# RQ-TRC-006
def source_files(root, extensions, excludes):
    """The files of a source folder to scan, in path order, excluded folders pruned."""
    found = []
    for folder, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if not is_excluded(d, excludes))
        for name in sorted(files):
            if is_excluded(name, excludes):
                continue
            if name in DEFAULT_NAMES or os.path.splitext(name)[1].lower() in extensions:
                found.append(Path(folder) / name)
    return found


# DEC-TRC-003
def read_source(path):
    """The lines of a source file, or None for a binary or oversized one (DEC-TRC-003)."""
    if path.stat().st_size > MAX_SOURCE_BYTES:
        return None
    data = path.read_bytes()
    if b"\x00" in data[:BINARY_PROBE_BYTES]:
        return None
    return data.decode(ENCODING, errors=KEY_REPLACE).splitlines()


# RQ-TRC-006
def display_path(path, root, base):
    """A file's path as the page shows it: relative to the base folder, else prefixed by its source folder's name."""
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return (Path(root.resolve().name) / path.relative_to(root)).as_posix()


# RQ-TRC-006
def link_file_lines(model, shown, lines, defined):
    """Links a source file to the IDs of its lines, with their numbers and texts; returns how many links it holds."""
    count = 0
    for ln, text in enumerate(lines, 1):
        for target in sorted(extract_ids(text, defined)):
            model.ensure(target)
            model.add_edge(shown, target, KEY_CODE, evidence(ln, text))
            count += 1
    return count


# RQ-TRC-006, RQ-TRC-007 (TASK-TRC-002)
def scan_sources(model, roots, base=None, extensions=DEFAULT_EXTENSIONS, excludes=DEFAULT_EXCLUDES):
    """Links every scanned source file to the IDs its lines hold, with the line numbers and texts; returns the files
    scanned, [(shown path, path)], for the call graph (DEC-TRC-013: no second walk)."""
    base = Path(base) if base is not None else Path.cwd()
    defined = {i for i, e in model.elements.items() if e[KEY_KIND] == KEY_ELEMENT}
    extensions = {e.lower() if e.startswith(".") else "." + e.lower() for e in extensions}
    scanned = []
    for root in map(Path, roots):
        for path in source_files(root, extensions, excludes):
            lines = read_source(path)
            if lines is not None:
                shown = display_path(path, root, base)
                model.files[shown] = {"path": shown, "ids": link_file_lines(model, shown, lines, defined)}
                scanned.append((shown, path))
    return scanned


# RQ-TRC-031, DEC-TRC-016: a function cites the IDs its file cites on its lines, with the same proofs.
def code_citations(model):
    """{source file: [(line, ID, proof)]} in line order, from the files' code links."""
    cited = {}
    for (src, dst, kind), proofs in model.edges.items():
        if kind == KEY_CODE:
            cited.setdefault(src, []).extend((proof[0], dst, proof) for proof in proofs)
    return {path: sorted(lines) for path, lines in cited.items()}


# ---- optional modules --------------------------------------------------------------------------------------------
# RQ-TRC-026, RQ-TRC-039, DEC-TRC-013: the module, and through it tree-sitter, are loaded only when asked for.
def load_module(name, path):
    """A module of this skill loaded from its file, under a name of its own."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# RQ-TRC-026
def load_call_graph_module():
    """callgraph.py, beside this script."""
    return load_module(CALLGRAPH_MODULE, CALLGRAPH_PATH)


# RQ-HST-015, DEC-HST-001: the history module, and through it git, only with --history.
def load_history_module():
    """history.py, beside this script."""
    return load_module(HISTORY_MODULE, HISTORY_PATH)


# RQ-HST-001
def history_depth(text):
    """The --history-depth value as a positive integer, or InputError."""
    if text is None:
        return None
    if not text.isdigit() or int(text) == 0:
        raise InputError(f"--history-depth must be a positive integer, not {text!r}")
    return int(text)


# RQ-TRC-068, RQ-TRC-071, DEC-TRC-036 (TASK-TRC-057)
def task_tiers(process, model):
    """{task ID: (tier S, M or L, or None; [requirement IDs it cites])} in index order, the tier read from the task's
    lines in the working tree."""
    refs_out = {}
    for (src, dst, kind) in model.edges:
        if kind == KEY_REFS:
            refs_out.setdefault(src, set()).add(dst)
    lines_of = {}
    tasks = {}
    for element in model.elements.values():
        if element[KEY_KIND] != KEY_ELEMENT or element[KEY_TYPE] != TYPE_TASK:
            continue
        path = resolve_document(process, element["doc"])
        if path not in lines_of:
            lines_of[path] = path.read_text(encoding=ENCODING, errors=KEY_REPLACE).splitlines() if path else []
        own = lines_of[path][element[KEY_FIRST] - 1:element[KEY_LAST]]
        tier = next((m.group(1) for m in map(TIER_RE.match, own) if m), None)
        cited = sorted(t for t in refs_out.get(element["id"], ()) if model.elements[t][KEY_TYPE] == TYPE_RQ)
        tasks[element["id"]] = (tier, cited)
    return tasks


# RQ-HST-002, RQ-HST-003, RQ-HST-012 (TASK-HST-003)
def build_history(args, process, model, scanned, call_graph, tasks):
    """The history block with its delivery, or None with a warning when the repository cannot be read; returns
    (module, block)."""
    module = load_history_module()
    documents = {}
    for element in model.elements.values():
        if element[KEY_KIND] == KEY_ELEMENT:
            path = resolve_document(process, element["doc"])
            if path is not None:
                documents.setdefault(path, []).append((element["id"], element[KEY_FIRST], element[KEY_LAST]))
    functions = [] if call_graph is None or call_graph.core_missing else \
        [(f["file"], f[KEY_FIRST], f[KEY_LAST]) for f in call_graph.functions]
    try:
        return module, module.build(process, documents, dict(scanned), functions, [process, *map(Path, args.sources)],
                                    args.history_since, depth=history_depth(args.history_depth),
                                    tasks=tasks, friction_log=agnos_layout.METRICS_LOG)
    except (module.HistoryUnavailable, module.GitError) as error:
        print(f"{PROG}: warning: no history: {error}", file=sys.stderr)
        return module, None


# ---- the state ---------------------------------------------------------------------------------------------------
# RQ-TRC-130
def head_commit(folder):
    """The HEAD commit of the repository holding the folder, or None outside git or without git."""
    try:
        done = subprocess.run(["git", "rev-parse", "HEAD"], cwd=folder, capture_output=True, text=True,
                              timeout=GIT_TIMEOUT, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    if done.returncode != 0:
        return None
    return done.stdout.strip() or None


# DEC-TRC-002: the elements defined in index order, then the undefined ones by name.
def state_elements(model):
    """The elements as the graph file holds them."""
    defined = [e for e in model.elements.values() if e[KEY_KIND] == KEY_ELEMENT]
    undefined = sorted((e for e in model.elements.values() if e[KEY_KIND] == KEY_UNDEFINED), key=lambda e: e["id"])
    return [{f: e[f] for f in ELEMENT_FIELDS} for e in defined + undefined]


# RQ-TRC-122, RQ-TRC-129: the page's call graph block, and the files read and not parsed the quality checks count.
def call_graph_block(call_graph, paths):
    """The call graph as the graph file holds it: the page's block, plus `parsedFiles` and `unparsedFiles`."""
    block = call_graph.page_data({p: n for n, p in enumerate(paths)})
    block["parsedFiles"] = sorted(call_graph.parsed)
    block["unparsedFiles"] = sorted(call_graph.unparsed)
    return block


# RQ-TRC-129, RQ-TRC-130, DEC-TRC-074: sorted so that two runs on the same inputs write the same bytes.
def state_data(model, meta, tasks, call_graph=None, history=None, sections=(), links=()):
    """The graph file's content: meta, elements, edges, files, tasks, sections (RQ-TRC-137, DEC-TRC-078), links
    (RQ-TRC-141, DEC-TRC-081) and, when asked, callGraph, history, delivery."""
    paths = sorted(model.files)
    data = {
        "meta": meta,
        "elements": state_elements(model),
        "files": [model.files[p] for p in paths],
        "edges": [[s, d, k, lines] for (s, d, k), lines in sorted(model.edges.items())],
        "tasks": {task: {"tier": tier, "requirements": cited} for task, (tier, cited) in tasks.items()},
        KEY_SECTIONS: list(sections),
        KEY_LINKS: list(links),
    }
    if call_graph is not None and not call_graph.core_missing:      # RQ-TRC-026: no key at all without a call graph
        data[KEY_CALL_GRAPH] = call_graph_block(call_graph, paths)
    if history is not None:                                         # RQ-HST-015: no key at all without a history
        data[KEY_HISTORY] = {k: v for k, v in history.items() if k != KEY_DELIVERY}
        if KEY_DELIVERY in history:                                 # RQ-TRC-069, DEC-TRC-037: beside the history
            data[KEY_DELIVERY] = history[KEY_DELIVERY]
    return data


# RQ-TRC-129, RQ-TRC-156
def write_state(path, data):
    """The graph file, one sorted JSON document; returns its text, which the explorer's data script holds (DEC-TRC-085)."""
    text = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding=ENCODING, newline="\n")
    return text


# ---- command line ------------------------------------------------------------------------------------------------
# RQ-TRC-129, RQ-TRC-001
def parse_args(argv):
    """The options of the performance center's scan, plus the graph file's path."""
    parser = argparse.ArgumentParser(prog="graph.py", description="AGNOS project state graph")  # FTR-TRC-011
    parser.add_argument("--process", required=True, help=f"AGNOS process folder holding {INDEX_NAME}")
    parser.add_argument("--sources", required=True, action=KEY_APPEND, help="source folder to scan (repeatable)")
    parser.add_argument("--out", help=f"graph file (default: <process>/{agnos_layout.GRAPH_FILE})")
    # RQ-TRC-119: the default lists are shown, so the user knows what a replacement drops.
    parser.add_argument("--ext", action=KEY_APPEND,
                        help="source extension to scan, replaces the default list (repeatable); default: "
                             f"{LIST_SEPARATOR.join(sorted(DEFAULT_EXTENSIONS))}; always scanned, whatever --ext: "
                             f"{LIST_SEPARATOR.join(sorted(DEFAULT_NAMES))}")
    parser.add_argument("--exclude", action=KEY_APPEND,
                        help="file or folder name pattern to skip, replaces the default list (repeatable); default: "
                             f"{LIST_SEPARATOR.join(DEFAULT_EXCLUDES)}")
    parser.add_argument("--generated-at", help="the state's date (default: now, UTC); fixing it makes the output "
                                               "reproducible")
    parser.add_argument("--call-graph", action=STORE_TRUE,
                        help="add the functions and calls of the sources, parsed with tree-sitter")  # FTR-TRC-002
    parser.add_argument("--history", action=STORE_TRUE,
                        help="add who worked on each element and on the code, read from git")  # FTR-HST-001
    parser.add_argument("--history-since", help="with --history: only the commits authored since this date or duration "
                                                "(a form git reads: 6.months, 2.weeks, 2026-01-01)")
    parser.add_argument("--history-depth", help="with --history: only the N most recent commits")
    parser.add_argument("--explorer", action=STORE_TRUE,                 # RQ-TRC-144, DEC-TRC-085
                        help=f"also write {explorer.PAGE_NAME} and {explorer.DATA_SCRIPT_NAME} beside the graph file")
    return parser.parse_args(argv)


# RQ-TRC-002, RQ-TRC-129
def check_sources(sources):
    """InputError naming every source folder that does not exist."""
    missing = [s for s in sources if not Path(s).is_dir()]
    if missing:
        raise InputError("source folder not found: " + ", ".join(missing))


# RQ-HST-001
def check_history_options(args):
    """InputError when a history limit is given without --history, or the depth is not a positive integer."""
    if not args.history and (args.history_since is not None or args.history_depth is not None):
        raise InputError("--history-since and --history-depth need --history")
    history_depth(args.history_depth)


# RQ-TRC-119
def print_scan_lists(extensions, user_extensions, excludes, user_excludes):
    """Prints the lists in effect, each saying whether it is the default or the user's, before the summary line."""
    origin = lambda given: ORIGIN_USER if given else ORIGIN_DEFAULT  # noqa: E731
    print(f"{PROG}: scanned extensions ({origin(user_extensions)}): {LIST_SEPARATOR.join(sorted(extensions))}")
    print(f"{PROG}: scanned names ({ORIGIN_ALWAYS}): {LIST_SEPARATOR.join(sorted(DEFAULT_NAMES))}")
    print(f"{PROG}: excluded ({origin(user_excludes)}): {LIST_SEPARATOR.join(excludes)}")


# RQ-TRC-129, RQ-TRC-130 (TASK-TRC-117)
def build_state(args, process, extensions, excludes, generated_at):
    """The graph file's content and its summary line, or InputError."""
    check_sources(args.sources)
    check_history_options(args)
    model = build_process_model(process)
    scanned = scan_sources(model, args.sources, extensions=extensions, excludes=excludes)
    tasks = task_tiers(process, model)
    defined = sum(e[KEY_KIND] == KEY_ELEMENT for e in model.elements.values())
    line = f"{PROG}: {defined} elements, {len(model.files)} files, {len(tasks)} tasks"
    summaries = {}
    call_graph = None
    if args.call_graph:
        call_graph = load_call_graph_module().analyse(scanned, code_citations(model), evidence)
        summaries[KEY_CALL_GRAPH] = call_graph.summary()
    history = None
    if args.history:
        module, history = build_history(args, process, model, scanned, call_graph, tasks)
        if history is not None:
            summaries[KEY_HISTORY] = module.summary(history)
    line = "; ".join([line, *summaries.values()])
    meta = {"generatedAt": generated_at, "commit": head_commit(process), "process": process.as_posix(),
            "sources": [Path(s).as_posix() for s in args.sources], "extensions": sorted(extensions),
            "names": sorted(DEFAULT_NAMES), "excludes": list(excludes), "summaries": summaries}
    return state_data(model, meta, tasks, call_graph, history, document_sections(process, model),
                      element_links(process, model)), line


# RQ-TRC-129
def main(argv=None):
    """Writes the graph file and prints its summary line; 1 on an input error, nothing written."""
    started = time.perf_counter()    # RQ-TRC-107
    args = parse_args(argv)
    process = Path(args.process)
    out = Path(args.out) if args.out else process / agnos_layout.GRAPH_FILE
    generated_at = args.generated_at or datetime.datetime.now(datetime.timezone.utc).strftime(TIMESTAMP_FORMAT)
    extensions, excludes = args.ext or DEFAULT_EXTENSIONS, args.exclude or DEFAULT_EXCLUDES
    try:
        data, line = build_state(args, process, extensions, excludes, generated_at)
    except InputError as error:
        print(f"{PROG}: {error}", file=sys.stderr)
        return 1
    text = write_state(out, data)
    written = out.as_posix()
    if args.explorer:                                   # RQ-TRC-144, RQ-TRC-156: after the graph, which stays as written
        try:
            written += f", {explorer.write_explorer(out, text).as_posix()}"
        except explorer.ExplorerError as error:
            print(f"{PROG}: explorer not written: {error}", file=sys.stderr)
            return 1
    print_scan_lists(extensions, args.ext, excludes, args.exclude)
    # RQ-TRC-107: the duration is printed only, never put in the generated file.
    print(f"{line}; {written} written in {time.perf_counter() - started:{DURATION_FORMAT}} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
