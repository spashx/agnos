#!/usr/bin/env python3
"""agnos-trace: the traceability matrix of an AGNOS process and its sources, as one self-contained HTML page.

Implements FTR-TRC-001 after ADR-TRC-001, ADR-TRC-002 and ADR-TRC-003. Procedure and options: ../SKILL.md.
Python >= 3.9, standard library only (DEC-TRC-001, RQ-TRC-021). Knows the AGNOS ID grammar and the INDEX.idx.md format,
nothing of the product being developed (RQ-TRC-019). --call-graph loads callgraph.py beside it (FTR-TRC-002,
ADR-TRC-004).
"""
import argparse
import datetime
import fnmatch
import html
import importlib.util
import json
import os
import re
import sys
from pathlib import Path

INDEX_NAME = "INDEX.idx.md"
DEFAULT_OUT_NAME = "TRACEABILITY.html"
TYPES = ("FTR", "RQ", "ADR", "DEC", "PLAN", "TASK")
ID_PATTERN = r"(?:FTR|RQ|ADR|DEC|PLAN|TASK)-[A-Z]{3}-[0-9]{3}"
NUMBER_LENGTH = 3
PREFIX_CUT = -(NUMBER_LENGTH + 1)              # "RQ-ABC-001"[:PREFIX_CUT] == "RQ-ABC"
LINE_TEXT_MAX = 200                            # characters of a line kept as evidence (DEC-TRC-003)

# RQ-TRC-006, DEC-TRC-001: what a source folder holds that can carry an ID; every list is replaceable from the command line.
DEFAULT_EXTENSIONS = frozenset(
    ".c .cc .cpp .cxx .c++ .h .hh .hpp .hxx .h++ .inl .ipp .tpp .m .mm .cs .fs .vb .java .kt .kts .scala .groovy .gradle "
    ".go .rs .swift .dart .py .pyi .pyw .rb .php .pl .pm .lua .r .jl .ex .exs .erl .hs .clj .js .jsx .mjs .cjs .ts .tsx "
    ".vue .svelte .html .htm .css .scss .sass .less .sql .sh .bash .zsh .fish .ps1 .psm1 .psd1 .bat .cmd .cmake .mk "
    ".yml .yaml .toml .ini .cfg .xml .proto .graphql .tf .glsl .hlsl .metal .cu .asm .s .v .sv .vhd".split())
DEFAULT_NAMES = frozenset({"CMakeLists.txt", "Makefile", "makefile", "GNUmakefile", "Dockerfile", "Jenkinsfile",
                           "Rakefile", "Gemfile", "meson.build", "BUILD", "BUILD.bazel", "WORKSPACE"})
DEFAULT_EXCLUDES = (".git", ".hg", ".svn", "node_modules", "build", "build-*", "build_*", "cmake-build-*", "dist", "out",
                    "_deps", ".venv", "venv", "__pycache__", ".idea", ".vs", ".vscode", "target", "bin", "obj")
MAX_SOURCE_BYTES = 2 * 1024 * 1024             # a larger file is taken as generated or as data (DEC-TRC-003)
BINARY_PROBE_BYTES = 8192                      # a NUL byte in this head marks a binary file

# DEC-TRC-005, DEC-TRC-008: the page's parts, beside this script in the skill folder.
SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = SKILL_DIR / "assets"
VENDOR_DIR = Path(__file__).resolve().parent / "vendor"
TEMPLATE_PATH = ASSETS_DIR / "matrix.html"
TOKENS_PATH = ASSETS_DIR / "tokens.json"
LIBRARY_FILE = "cytoscape.min.js"
CALLGRAPH_PATH = Path(__file__).resolve().parent / "callgraph.py"
CALLGRAPH_MODULE = "agnos_trace_callgraph"
MARKER_RE = re.compile(r"/\*@(TOKENS|CSS|LIBRARY|SCRIPT)@\*/|@(TITLE|DATA_SCRIPT)@")
DATA_JSON_SUFFIX = ".json"          # RQ-TRC-010: the data alone, for any other tool
DATA_SCRIPT_SUFFIX = ".data.js"     # RQ-TRC-010: the same data, loaded by the page (a page from disk cannot fetch a file)
DATA_GLOBAL = "window.AGNOS_TRACE_DATA"
SCRIPT_END_RE = re.compile(r"</(script)", re.IGNORECASE)
TOKEN_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
THEMES = ("light", "dark")
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%MZ"

# DEC-TRC-003: an ID is not part of a longer word or number; a range is "<A> to <B>", "<A>–<B>", "<A>—<B>", "<A>..<B>"
# or "<A>-<B>".
ID_RE = re.compile(rf"(?<![A-Za-z0-9]){ID_PATTERN}(?![0-9])")
FULL_ID_RE = re.compile(rf"^{ID_PATTERN}$")
RANGE_RE = re.compile(rf"(?<![A-Za-z0-9])({ID_PATTERN})(?:\s+to\s+|\s*(?:–|—|\.\.|-)\s*)({ID_PATTERN})(?![0-9])")


class InputError(Exception):
    """An input the generator cannot work from (RQ-TRC-002)."""


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


def id_type(element_id):
    return element_id.split("-", 1)[0]


def evidence(line_number, text):
    """A line kept as the proof of a link: its number and its text, trimmed (DEC-TRC-003)."""
    return [line_number, text.strip()[:LINE_TEXT_MAX]]


# ---- model -------------------------------------------------------------------------------------------------------
# DEC-TRC-002
class Model:
    """The traceability graph: elements (process elements, undefined IDs), source files, and the links between them."""

    def __init__(self):
        self.elements = {}   # id -> element dict, in index order
        self.edges = {}      # (source, target, kind) -> list of [line, text]; kind: contains | refs | code
        self.files = {}      # source path -> {"path", "ids"}

    def add_element(self, element):
        self.elements[element["id"]] = element

    def ensure(self, element_id):
        """The element of an ID, made an undefined element when the index does not define it (RQ-TRC-007)."""
        if element_id not in self.elements:
            self.add_element({"id": element_id, "kind": "undefined", "type": id_type(element_id),
                              "tri": element_id.split("-")[1], "doc": "", "first": 0, "last": 0, "status": "",
                              "title": "Not defined in the index"})
        return self.elements[element_id]

    def add_edge(self, source, target, kind, proof=None):
        lines = self.edges.setdefault((source, target, kind), [])
        if proof is not None:
            lines.append(proof)


# ---- process -----------------------------------------------------------------------------------------------------
# RQ-TRC-003
def parse_index(index_path):
    """The rows of INDEX.idx.md: one element per 'ID|first-last|status|title' row, under its '@document' line."""
    rows, doc = [], ""
    for raw in index_path.read_text(encoding="utf-8").splitlines():
        if raw.startswith("@"):
            doc = raw[1:].strip()
            continue
        parts = raw.split("|", 3)
        if len(parts) != 4 or not FULL_ID_RE.match(parts[0]):
            continue
        first, _, last = parts[1].partition("-")
        rows.append({"id": parts[0], "kind": "element", "type": id_type(parts[0]), "tri": parts[0].split("-")[1],
                     "doc": doc, "first": int(first), "last": int(last or first), "status": parts[2].strip(),
                     "title": parts[3].strip()})
    return rows


def resolve_document(process_dir, doc):
    """A document path of the index: relative to the process folder's parent, else to the process folder itself."""
    candidates = [process_dir.parent / doc, process_dir / Path(*Path(doc).parts[1:]) if len(Path(doc).parts) > 1
                  else process_dir / doc, process_dir / doc]
    return next((c for c in candidates if c.is_file()), None)


# RQ-TRC-004, DEC-TRC-003
def add_containment(model, members):
    """Links each element of one document to the element whose range most closely encloses its own."""
    for child in members:
        parents = [p for p in members if p is not child and p["first"] <= child["first"] and child["last"] <= p["last"]
                   and (p["first"], p["last"]) != (child["first"], child["last"])]
        if parents:
            parent = min(parents, key=lambda p: p["last"] - p["first"])
            model.add_edge(parent["id"], child["id"], "contains")


# RQ-TRC-005, RQ-TRC-007, DEC-TRC-003
def add_document_references(model, members, lines, defined):
    """Links each element to the IDs of its own lines: those of its range that no element it contains holds."""
    owner = [None] * (len(lines) + 1)
    for element in sorted(members, key=lambda e: e["last"] - e["first"], reverse=True):
        for ln in range(element["first"], min(element["last"], len(lines)) + 1):
            owner[ln] = element["id"]
    for ln, text in enumerate(lines, 1):
        if owner[ln] is None:
            continue
        for target in sorted(extract_ids(text, defined) - {owner[ln]}):
            model.ensure(target)
            model.add_edge(owner[ln], target, "refs", evidence(ln, text))


def build_process_model(process_dir):
    """The elements of the process folder's index, their containment and their references (TASK-TRC-001)."""
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
            print(f"agnos-trace: warning: {doc} not found, its references are not read", file=sys.stderr)
            continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        add_document_references(model, members, lines, defined)
    return model


# ---- sources -----------------------------------------------------------------------------------------------------
# RQ-TRC-006, DEC-TRC-003
def is_excluded(name, excludes):
    return any(fnmatch.fnmatchcase(name, pattern) for pattern in excludes)


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


def read_source(path):
    """The lines of a source file, or None for a binary or oversized one (DEC-TRC-003)."""
    if path.stat().st_size > MAX_SOURCE_BYTES:
        return None
    data = path.read_bytes()
    if b"\x00" in data[:BINARY_PROBE_BYTES]:
        return None
    return data.decode("utf-8", errors="replace").splitlines()


def display_path(path, root, base):
    """A file's path as the page shows it: relative to the base folder, else prefixed by its source folder's name."""
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return (Path(root.resolve().name) / path.relative_to(root)).as_posix()


# RQ-TRC-006, RQ-TRC-007 (TASK-TRC-002)
def scan_sources(model, roots, base=None, extensions=DEFAULT_EXTENSIONS, excludes=DEFAULT_EXCLUDES):
    """Links every scanned source file to the IDs its lines hold, with the line numbers and texts; returns the files
    scanned, [(shown path, path)], for the call graph (DEC-TRC-013: no second walk)."""
    base = Path(base) if base is not None else Path.cwd()
    defined = {i for i, e in model.elements.items() if e["kind"] == "element"}
    extensions = {e.lower() if e.startswith(".") else "." + e.lower() for e in extensions}
    scanned = []
    for root in map(Path, roots):
        for path in source_files(root, extensions, excludes):
            lines = read_source(path)
            if lines is None:
                continue
            shown = display_path(path, root, base)
            count = 0
            for ln, text in enumerate(lines, 1):
                for target in sorted(extract_ids(text, defined)):
                    model.ensure(target)
                    model.add_edge(shown, target, "code", evidence(ln, text))
                    count += 1
            model.files[shown] = {"path": shown, "ids": count}
            scanned.append((shown, path))
    return scanned


# RQ-TRC-031, DEC-TRC-016: a function cites the IDs its file cites on its lines, with the same proofs.
def code_citations(model):
    """{source file: [(line, ID, proof)]} in line order, from the files' code links."""
    cited = {}
    for (src, dst, kind), proofs in model.edges.items():
        if kind == "code":
            cited.setdefault(src, []).extend((proof[0], dst, proof) for proof in proofs)
    return {path: sorted(lines) for path, lines in cited.items()}


# RQ-TRC-026, RQ-TRC-039, DEC-TRC-013: the module, and through it tree-sitter, are loaded only when asked for.
def load_call_graph_module():
    spec = importlib.util.spec_from_file_location(CALLGRAPH_MODULE, CALLGRAPH_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---- coverage and gaps -------------------------------------------------------------------------------------------
GAP_KINDS = ("uncovered", "untasked", "task-no-rq", "adr-no-rq", "empty", "isolated", "undefined", "untraced-files")
CONTAINED_TYPE = {"FTR": "RQ", "ADR": "DEC", "PLAN": "TASK"}       # what a container type is empty without
COVERING_TYPES = frozenset({"DEC", "TASK", "ADR", "PLAN", "FTR"})  # elements through which coverage is indirect


class Links:
    """The model's edges indexed per element: who it contains, references and is referenced by, and what code cites."""

    def __init__(self, model):
        self.children, self.parent, self.refs_out, self.refs_in, self.code_in = {}, {}, {}, {}, {}
        for (src, dst, kind) in model.edges:
            if kind == "contains":
                self.children.setdefault(src, []).append(dst)
                self.parent[dst] = src
            elif kind == "refs":
                self.refs_out.setdefault(src, set()).add(dst)
                self.refs_in.setdefault(dst, set()).add(src)
            else:
                self.code_in.setdefault(dst, set()).add(src)

    def descendants(self, element_id):
        found, stack = [], list(self.children.get(element_id, []))
        while stack:
            child = stack.pop()
            found.append(child)
            stack.extend(self.children.get(child, []))
        return found

    def touched(self, element_id):
        """True when a refs or code edge touches the element."""
        return bool(self.refs_out.get(element_id) or self.refs_in.get(element_id) or self.code_in.get(element_id))


# RQ-TRC-008, DEC-TRC-004
def rate(rq, links, model):
    """covered: code cites the requirement; indirect: code cites a decision, task, ADR, plan or feature linked to it or
    holding it (another requirement does not count); else uncovered."""
    if links.code_in.get(rq):
        return "covered"
    neighbours = links.refs_in.get(rq, set()) | links.refs_out.get(rq, set())
    ancestor = links.parent.get(rq)
    while ancestor:
        neighbours.add(ancestor)
        ancestor = links.parent.get(ancestor)
    if any(model.elements[n]["type"] in COVERING_TYPES and links.code_in.get(n) for n in neighbours):
        return "indirect"
    return "uncovered"


def refs_to_type(links, model, element_id, wanted):
    return any(model.elements[t]["type"] == wanted for t in links.refs_out.get(element_id, ()))


# RQ-TRC-009, DEC-TRC-004 (TASK-TRC-003)
def analyse(model):
    """The coverage of every requirement and the gap lists, IDs in index order, undefined IDs and files by name."""
    links = Links(model)
    defined = [e for e in model.elements.values() if e["kind"] == "element"]
    coverage = {e["id"]: rate(e["id"], links, model) for e in defined if e["type"] == "RQ"}
    of_type = lambda t: [e["id"] for e in defined if e["type"] == t]  # noqa: E731
    gaps = {
        "uncovered": [rq for rq, r in coverage.items() if r == "uncovered"],
        "untasked": [rq for rq in of_type("RQ")
                     if not any(model.elements[s]["type"] == "TASK" for s in links.refs_in.get(rq, ()))],
        "task-no-rq": [t for t in of_type("TASK") if not refs_to_type(links, model, t, "RQ")],
        "adr-no-rq": [a for a in of_type("ADR") if not any(refs_to_type(links, model, x, "RQ")
                                                           for x in [a] + links.descendants(a))],
        "empty": [e["id"] for e in defined if e["type"] in CONTAINED_TYPE
                  and not any(model.elements[c]["type"] == CONTAINED_TYPE[e["type"]]
                              for c in links.children.get(e["id"], ()))],
        "isolated": [e["id"] for e in defined
                     if not any(links.touched(x) for x in [e["id"]] + links.descendants(e["id"]))],
        "undefined": sorted(i for i, e in model.elements.items() if e["kind"] == "undefined"),
        "untraced-files": sorted(p for p, f in model.files.items() if not f["ids"]),
    }
    return {"coverage": coverage, "gaps": gaps}


def summary(model, analysis):
    """The one line the generator ends with: element and file counts, coverage, gap counts (RQ-TRC-017)."""
    defined = sum(e["kind"] == "element" for e in model.elements.values())
    rated = list(analysis["coverage"].values())
    gaps = ", ".join(f"{k} {len(analysis['gaps'][k])}" for k in GAP_KINDS)
    return (f"agnos-trace: {defined} elements, {len(model.files)} files; RQ {len(rated)}: covered "
            f"{rated.count('covered')}, indirect {rated.count('indirect')}, uncovered {rated.count('uncovered')}; "
            f"gaps: {gaps}")


# ---- design tokens -----------------------------------------------------------------------------------------------
# RQ-TRC-018, DEC-TRC-009
def load_tokens(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise InputError(f"design tokens {path}: {error}") from error


def global_value(tokens, ref, owner):
    if ref not in tokens["global"]:
        raise InputError(f"design token '{owner}' refers to '{ref}', which is not a global token")
    return tokens["global"][ref]


def tokens_css(tokens):
    """The custom properties of the page: --s-<semantic> per theme, --c-<component> as var(--s-<semantic>); an
    unresolved reference is an input error (DEC-TRC-009)."""
    light, dark = [], []
    for name, ref in tokens["semantic"].items():
        if not TOKEN_NAME_RE.match(name):
            raise InputError(f"design token name '{name}' is not kebab-case")
        if isinstance(ref, dict):
            if set(ref) != set(THEMES):
                raise InputError(f"design token '{name}' needs exactly a light and a dark value")
            light.append(f"  --s-{name}: {global_value(tokens, ref['light'], name)};")
            dark.append(f"  --s-{name}: {global_value(tokens, ref['dark'], name)};")
        else:
            light.append(f"  --s-{name}: {global_value(tokens, ref, name)};")
    for name, ref in tokens["component"].items():
        if not TOKEN_NAME_RE.match(name) or ref not in tokens["semantic"]:
            raise InputError(f"component token '{name}' refers to '{ref}', which is not a semantic token")
        light.append(f"  --c-{name}: var(--s-{ref});")
    dark_block = ["  color-scheme: dark;", *dark]
    return "\n".join([":root {", "  color-scheme: light;", *light, "}", "@media (prefers-color-scheme: dark) {",
                      ':root:not([data-theme="light"]) {', *dark_block, "}", "}", ':root[data-theme="dark"] {',
                      *dark_block, "}"])


# ---- page --------------------------------------------------------------------------------------------------------
def library_label():
    """'Cytoscape.js 3.30.2', read from VENDOR.md so that the version is written once (RQ-TRC-024)."""
    text = (VENDOR_DIR / "VENDOR.md").read_text(encoding="utf-8")
    m = re.search(rf"^\| `{re.escape(LIBRARY_FILE)}` \| ([^|]+?) \| ([^|]+?) \|", text, re.M)
    return f"{m.group(1)} {m.group(2)}" if m else LIBRARY_FILE


# DEC-TRC-002: everything the page shows, computed here; sorted so that two runs write the same bytes (RQ-TRC-023).
def page_data(model, analysis, meta, call_graph=None):
    defined = [e for e in model.elements.values() if e["kind"] == "element"]
    undefined = sorted((e for e in model.elements.values() if e["kind"] == "undefined"), key=lambda e: e["id"])
    fields = ("id", "kind", "type", "tri", "doc", "first", "last", "status", "title")
    paths = sorted(model.files)
    data = {
        "meta": meta,
        "elements": [{f: e[f] for f in fields} for e in defined + undefined],
        "files": [model.files[p] for p in paths],
        "edges": [[s, d, k, lines] for (s, d, k), lines in sorted(model.edges.items())],
        "coverage": analysis["coverage"],
        "gaps": analysis["gaps"],
        "gapKinds": list(GAP_KINDS),
    }
    if call_graph is not None and not call_graph.core_missing:      # RQ-TRC-026: no key at all without a call graph
        data["callGraph"] = call_graph.page_data({p: n for n, p in enumerate(paths)})
    return data


def embed_json(data):
    """JSON safe inside a <script> element: no '<' at all, so no file content can close the block (DEC-TRC-005)."""
    return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


def embed_script(code):
    return SCRIPT_END_RE.sub(r"<\\/\1", code)


# RQ-TRC-010 (TASK-TRC-004, TASK-TRC-031)
def render_page(title, data_script):
    """The page: the template with its markers replaced in one pass, so inserted text is never scanned again;
    data_script is the file name of the data script written beside it."""
    parts = {
        "TOKENS": tokens_css(load_tokens(TOKENS_PATH)),
        "CSS": (ASSETS_DIR / "matrix.css").read_text(encoding="utf-8"),
        "LIBRARY": embed_script((VENDOR_DIR / LIBRARY_FILE).read_text(encoding="utf-8")),
        "SCRIPT": embed_script((ASSETS_DIR / "matrix.js").read_text(encoding="utf-8")),
        "TITLE": html.escape(title),
        "DATA_SCRIPT": html.escape(data_script),
    }
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    return MARKER_RE.sub(lambda m: parts[m.group(1) or m.group(2)], template)


def data_paths(page_path):
    """(<page>.json, <page>.data.js) beside the page (RQ-TRC-010, DEC-TRC-005 as amended)."""
    return page_path.with_name(page_path.stem + DATA_JSON_SUFFIX), page_path.with_name(page_path.stem + DATA_SCRIPT_SUFFIX)


def write_outputs(path, data, title):
    """The page and its two data files, the same JSON in both."""
    json_path, script_path = data_paths(path)
    text = embed_json(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_page(title, script_path.name), encoding="utf-8", newline="\n")
    json_path.write_text(text + "\n", encoding="utf-8", newline="\n")
    script_path.write_text(f"{DATA_GLOBAL} = {text};\n", encoding="utf-8", newline="\n")


# ---- command line ------------------------------------------------------------------------------------------------
# RQ-TRC-001
def parse_args(argv):
    parser = argparse.ArgumentParser(prog="trace_matrix.py", description="AGNOS traceability matrix (FTR-TRC-001)")
    parser.add_argument("--process", required=True, help=f"AGNOS process folder holding {INDEX_NAME}")
    parser.add_argument("--sources", required=True, action="append", help="source folder to scan (repeatable)")
    parser.add_argument("--out", help=f"output page (default: <process>/{DEFAULT_OUT_NAME})")
    parser.add_argument("--ext", action="append", help="source extension to scan, replaces the default list (repeatable)")
    parser.add_argument("--exclude", action="append",
                        help="file or folder name pattern to skip, replaces the default list (repeatable)")
    parser.add_argument("--title", help="page title (default: the name of the process folder's parent)")
    parser.add_argument("--generated-at", help="generation time shown by the page (default: now, UTC); fixing it "
                                               "makes the output reproducible")
    parser.add_argument("--call-graph", action="store_true",
                        help="add the functions and calls of the sources, parsed with tree-sitter (FTR-TRC-002)")
    return parser.parse_args(argv)


# RQ-TRC-002
def check_sources(sources):
    missing = [s for s in sources if not Path(s).is_dir()]
    if missing:
        raise InputError("source folder not found: " + ", ".join(missing))


def main(argv=None):
    args = parse_args(argv)
    process = Path(args.process)
    out = Path(args.out) if args.out else process / DEFAULT_OUT_NAME
    title = args.title or process.resolve().parent.name
    generated_at = args.generated_at or datetime.datetime.now(datetime.timezone.utc).strftime(TIMESTAMP_FORMAT)
    try:
        check_sources(args.sources)
        model = build_process_model(process)
        scanned = scan_sources(model, args.sources, extensions=args.ext or DEFAULT_EXTENSIONS,
                               excludes=args.exclude or DEFAULT_EXCLUDES)
        analysis = analyse(model)
        line = summary(model, analysis)
        graph = None
        if args.call_graph:
            graph = load_call_graph_module().analyse(scanned, code_citations(model), evidence)
            line += "; " + graph.summary()
        meta = {"title": title, "generatedAt": generated_at, "process": process.as_posix(),
                "sources": [Path(s).as_posix() for s in args.sources], "summary": line, "library": library_label()}
        data = page_data(model, analysis, meta, graph)
    except InputError as error:
        print(f"agnos-trace: {error}", file=sys.stderr)
        return 1
    write_outputs(out, data, title)
    print(f"{line}; {out.as_posix()} written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
