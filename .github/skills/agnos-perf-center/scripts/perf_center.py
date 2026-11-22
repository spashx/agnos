#!/usr/bin/env python3
"""agnos-perf-center: the traceability matrix of an AGNOS process and its sources, as one self-contained HTML page.

Procedure and options: ../SKILL.md (FTR-TRC-001; ADR-TRC-001, ADR-TRC-002, ADR-TRC-003).
Python >= 3.9, standard library only (DEC-TRC-001, RQ-TRC-021). Reads the project's state from the graph file written by the
sibling skill agnos-graph (FTR-TRC-011; ADR-TRC-022: DEC-TRC-075), then judges it: coverage, findings, quality score
(RQ-TRC-131). Kept free of quality findings (RQ-QLT-009, DEC-QLT-008).
"""
import argparse
import datetime
import html
import json
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))    # scorecard.py, beside this script (ADR-TRC-008)
import scorecard  # noqa: E402
import agnos_layout  # noqa: E402  RQ-PLG-036 / DEC-PLG-027: the process folder's names, generated beside this script

# RQ-TRC-067: a literal written more than once is a named constant.
DURATION_FORMAT = ".3f"    # RQ-TRC-107: seconds, three decimals
KEY_UNCOVERED = "uncovered"
KEY_COVERED = "covered"
KEY_INDIRECT = "indirect"
KEY_UNDEFINED = "undefined"
KEY_COVERAGE = "coverage"
KEY_KIND = "kind"
KEY_TYPE = "type"
KEY_FIRST = "first"
KEY_LAST = "last"
KEY_STATUS = "status"
KEY_TITLE = "title"
KEY_GLOBAL = "global"
ENCODING = "utf-8"
KEY_ELEMENT = "element"
KEY_CONTAINS = "contains"
KEY_REFS = "refs"
KEY_SEMANTIC = "semantic"
TYPE_TASK = "TASK"
TYPE_RQ = "RQ"
KEY_DELIVERY = "delivery"
KEY_CALL_GRAPH = "callGraph"
KEY_HISTORY = "history"
KEY_ELEMENTS = "elements"
KEY_META = "meta"
KEY_SUMMARIES = "summaries"
KEY_EDGES = "edges"
KEY_FILES = "files"
KEY_PROCESS = "process"
KEY_SOURCES = "sources"
# RQ-TRC-122, RQ-TRC-129: what the graph file adds to the page's call graph block, for the quality checks only
GRAPH_ONLY_CALL_KEYS = ("parsedFiles", "unparsedFiles")
# RQ-TRC-132, DEC-TRC-076: the sibling skill's script, run as a subprocess when the graph is absent or --rebuild is given
GRAPH_SCRIPT = Path(__file__).resolve().parent.parent.parent / "agnos-graph" / "scripts" / "graph.py"
GRAPH_VALUED = ("ext", "exclude", "history_since", "history_depth")    # repeatable or valued options passed on as given
GRAPH_FLAGS = ("call_graph", "history")
KEY_APPEND = "append"
OPT_PROCESS, OPT_SOURCES, OPT_OUT, OPT_GENERATED_AT = "--process", "--sources", "--out", "--generated-at"   # RQ-TRC-067
STORE_TRUE = "store_true"
SUMMARY_PARTS = (KEY_CALL_GRAPH, KEY_HISTORY)   # RQ-TRC-017: the summary line's parts the graph file gives, in order

INDEX_NAME = agnos_layout.INDEX
DEFAULT_OUT_NAME = agnos_layout.PERF_CENTER_PAGE
# DEC-TRC-005, DEC-TRC-008: the page's parts, beside this script in the skill folder.
SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = SKILL_DIR / "assets"
TEMPLATE_PATH = ASSETS_DIR / "matrix.html"
TOKENS_PATH = ASSETS_DIR / "tokens.json"
KEY_LIBRARIES = "libraries"
LIBRARIES_PATH = ASSETS_DIR / "libraries.json"     # RQ-TRC-082, DEC-TRC-040: the libraries loaded from cdnjs
# RQ-TRC-109, RQ-TRC-110, DEC-TRC-057: AGNOS's one version (RQ-PLG-032), in a sibling skill of this one, as one SemVer 2.0.0 line
# (the regular expression of semver.org); the foot of the page shows `v.<major>.<minor>`.
VERSION_PATH = SKILL_DIR.parent / "agnos-init" / "assets" / "templates" / agnos_layout.VERSION   # RQ-PLG-036 (TASK-TRC-101)
VERSION_PREFIX = "v."
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
                       r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$")
MARKER_RE = re.compile(r"/\*@(TOKENS|CSS|SCRIPT)@\*/|@(TITLE|DATA_SCRIPT|LIBRARIES|APP_VERSION)@")
DATA_JSON_SUFFIX = ".json"          # RQ-TRC-010: the data alone, for any other tool
DATA_SCRIPT_SUFFIX = ".data.js"     # RQ-TRC-010: the same data, loaded by the page (a page from disk fetches no file)
DATA_GLOBAL = "window.AGNOS_PERF_CENTER_DATA"
SCRIPT_END_RE = re.compile(r"</(script)", re.IGNORECASE)
TOKEN_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
THEMES = ("light", "dark")
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%MZ"

class InputError(Exception):
    """An input the generator cannot work from (RQ-TRC-002)."""


# ---- model -------------------------------------------------------------------------------------------------------
# DEC-TRC-002, DEC-TRC-075
class Model:
    """The traceability graph: elements (process elements, undefined IDs), source files, and the links between them,
    rebuilt from the graph file."""

    def __init__(self):
        self.elements = {}   # id -> element dict, in the graph file's order
        self.edges = {}      # (source, target, kind) -> list of [line, text]; kind: contains | refs | code
        self.files = {}      # source path -> {"path", "ids"}


# RQ-TRC-131, DEC-TRC-075 (TASK-TRC-118)
def load_graph(path):
    """The graph file's content, or InputError naming the file when it is absent, not JSON or holds no elements."""
    shown = Path(path).as_posix()
    try:
        data = json.loads(Path(path).read_text(encoding=ENCODING))
    except OSError as error:
        raise InputError(f"graph file {shown} not found: run the agnos-graph skill first ({error})") from error
    except ValueError as error:
        raise InputError(f"graph file {shown} is not valid JSON: {error}") from error
    if not isinstance(data, dict) or not isinstance(data.get(KEY_ELEMENTS), list):
        raise InputError(f"graph file {shown} holds no elements list")
    return data


# RQ-TRC-131, DEC-TRC-075
def model_of(graph):
    """The model of a graph file's elements, edges and files."""
    model = Model()
    model.elements = {e["id"]: e for e in graph[KEY_ELEMENTS]}
    model.edges = {(s, d, k): lines for s, d, k, lines in graph.get(KEY_EDGES, [])}
    model.files = {f["path"]: f for f in graph.get(KEY_FILES, [])}
    return model


# RQ-TRC-122, RQ-TRC-131, DEC-TRC-075 (TASK-TRC-118)
class CallGraphState:
    """The call graph of a graph file, as the quality checks and the page read it: one entry per function with the IDs
    it cites, the files read and those that did not parse, and the page's block."""

    core_missing = False

    def __init__(self, block):
        self.block = {k: v for k, v in block.items() if k not in GRAPH_ONLY_CALL_KEYS}
        self.functions = [{"ids": {}} for _ in block["functions"]]
        for index, target, lines in block["ids"]:
            self.functions[index]["ids"][target] = lines
        self.parsed = list(block.get(GRAPH_ONLY_CALL_KEYS[0], []))
        self.unparsed = list(block.get(GRAPH_ONLY_CALL_KEYS[1], []))

    # RQ-TRC-038
    def page_data(self, _file_index):
        """The page's call graph block, as the graph file holds it: its file indexes follow the same sorted paths."""
        return self.block


# ---- coverage and findings -------------------------------------------------------------------------------------------
RULE_KEYS = ("uncovered", "untasked", "task-no-rq", "adr-no-rq", "empty", "isolated", "undefined", "untraced-files")
CONTAINED_TYPE = {"FTR": "RQ", "ADR": "DEC", "PLAN": "TASK"}       # what a container type is empty without
COVERING_TYPES = frozenset({"DEC", "TASK", "ADR", "PLAN", "FTR"})  # elements through which coverage is indirect


class Links:
    """The model's edges indexed per element: who it contains, references and is referenced by, and what code cites."""

    def __init__(self, model):
        self.children, self.parent, self.refs_out, self.refs_in, self.code_in = {}, {}, {}, {}, {}
        for (src, dst, kind) in model.edges:
            if kind == KEY_CONTAINS:
                self.children.setdefault(src, []).append(dst)
                self.parent[dst] = src
            elif kind == KEY_REFS:
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
        return KEY_COVERED
    neighbours = links.refs_in.get(rq, set()) | links.refs_out.get(rq, set())
    ancestor = links.parent.get(rq)
    while ancestor:
        neighbours.add(ancestor)
        ancestor = links.parent.get(ancestor)
    if any(model.elements[n][KEY_TYPE] in COVERING_TYPES and links.code_in.get(n) for n in neighbours):
        return KEY_INDIRECT
    return KEY_UNCOVERED


def refs_to_type(links, model, element_id, wanted):
    return any(model.elements[t][KEY_TYPE] == wanted for t in links.refs_out.get(element_id, ()))


def is_untasked(rq, links, model):
    return not any(model.elements[s][KEY_TYPE] == TYPE_TASK for s in links.refs_in.get(rq, ()))


def is_adr_without_rq(adr, links, model):
    return not any(refs_to_type(links, model, x, TYPE_RQ) for x in [adr] + links.descendants(adr))


def is_empty(element, links, model):
    """A feature, ADR or plan that holds none of the elements of its contained type."""
    contained = CONTAINED_TYPE[element[KEY_TYPE]]
    return not any(model.elements[c][KEY_TYPE] == contained for c in links.children.get(element["id"], ()))


def is_isolated(element_id, links):
    return not any(links.touched(x) for x in [element_id] + links.descendants(element_id))


def ids_by_type(defined):
    return {t: [e["id"] for e in defined if e[KEY_TYPE] == t] for t in (TYPE_RQ, TYPE_TASK, "ADR")}


def element_findings(defined, coverage, links, model):
    """The findings of the rules on the elements the index defines, IDs in index order."""
    of_type = ids_by_type(defined)
    return {
        KEY_UNCOVERED: [rq for rq, r in coverage.items() if r == KEY_UNCOVERED],
        "untasked": [rq for rq in of_type[TYPE_RQ] if is_untasked(rq, links, model)],
        "task-no-rq": [t for t in of_type[TYPE_TASK] if not refs_to_type(links, model, t, TYPE_RQ)],
        "adr-no-rq": [a for a in of_type["ADR"] if is_adr_without_rq(a, links, model)],
        "empty": [e["id"] for e in defined if e[KEY_TYPE] in CONTAINED_TYPE and is_empty(e, links, model)],
        "isolated": [e["id"] for e in defined if is_isolated(e["id"], links)],
    }


# RQ-TRC-009, DEC-TRC-004 (TASK-TRC-003)
def analyse(model):
    """The coverage of every requirement and the findings of each rule, IDs in index order, undefined IDs and files by
    name."""
    links = Links(model)
    defined = [e for e in model.elements.values() if e[KEY_KIND] == KEY_ELEMENT]
    coverage = {e["id"]: rate(e["id"], links, model) for e in defined if e[KEY_TYPE] == TYPE_RQ}
    findings = {
        **element_findings(defined, coverage, links, model),
        KEY_UNDEFINED: sorted(i for i, e in model.elements.items() if e[KEY_KIND] == KEY_UNDEFINED),
        "untraced-files": sorted(p for p, f in model.files.items() if not f["ids"]),
    }
    return {KEY_COVERAGE: coverage, "findings": findings}


def summary(model, analysis, quality):
    """The one line the generator ends with: element and file counts, coverage, the quality score (RQ-TRC-017,
    RQ-TRC-064)."""
    defined = sum(e[KEY_KIND] == KEY_ELEMENT for e in model.elements.values())
    rated = list(analysis[KEY_COVERAGE].values())
    return (f"agnos-perf-center: {defined} elements, {len(model.files)} files; RQ {len(rated)}: covered "
            f"{rated.count(KEY_COVERED)}, indirect {rated.count(KEY_INDIRECT)}, "
            f"uncovered {rated.count(KEY_UNCOVERED)}; {scorecard.summary_part(quality)}")


# ---- design tokens -----------------------------------------------------------------------------------------------
# RQ-TRC-018, DEC-TRC-009
def load_tokens(path):
    try:
        return json.loads(Path(path).read_text(encoding=ENCODING))
    except (OSError, ValueError) as error:
        raise InputError(f"design tokens {path}: {error}") from error


def global_value(tokens, ref, owner):
    if ref not in tokens[KEY_GLOBAL]:
        raise InputError(f"design token '{owner}' refers to '{ref}', which is not a global token")
    return tokens[KEY_GLOBAL][ref]


def tokens_css(tokens):
    """The custom properties of the page: --s-<semantic> per theme, --c-<component> as var(--s-<semantic>); an
    unresolved reference is an input error (DEC-TRC-009)."""
    light, dark = [], []
    for name, ref in tokens[KEY_SEMANTIC].items():
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
        if not TOKEN_NAME_RE.match(name) or ref not in tokens[KEY_SEMANTIC]:
            raise InputError(f"component token '{name}' refers to '{ref}', which is not a semantic token")
        light.append(f"  --c-{name}: var(--s-{ref});")
    dark_block = ["  color-scheme: dark;", *dark]
    return "\n".join([":root {", "  color-scheme: light;", *light, "}", "@media (prefers-color-scheme: dark) {",
                      ':root:not([data-theme="light"]) {', *dark_block, "}", "}", ':root[data-theme="dark"] {',
                      *dark_block, "}"])


# ---- page --------------------------------------------------------------------------------------------------------
# RQ-TRC-080, RQ-TRC-082, DEC-TRC-040
def load_libraries():
    """The libraries of the page, as `assets/libraries.json` records them."""
    try:
        return json.loads(Path(LIBRARIES_PATH).read_text(encoding=ENCODING))[KEY_LIBRARIES]
    except (OSError, ValueError, KeyError) as error:
        raise InputError(f"library record {LIBRARIES_PATH}: {error}") from error


def library_scripts(libraries):
    """One script element per library, from cdnjs, checked by its integrity hash (RQ-TRC-080)."""
    return "\n".join(f'<script src="{html.escape(lib["url"])}" integrity="{html.escape(lib["integrity"])}" '
                     f'crossorigin="anonymous" referrerpolicy="no-referrer"></script>' for lib in libraries)


def library_meta(libraries):
    """What the page says of its libraries: name, version, licence, the global it defines and what needs it."""
    return [{k: lib[k] for k in ("name", "version", "licence", "global", "use")} for lib in libraries]


# RQ-TRC-109, RQ-TRC-110, RQ-TRC-116, DEC-TRC-057, DEC-TRC-061
def version_label():
    """The version the foot of the page and the About name show, `v.<major>.<minor>`, from the version file; the empty string when the file
    is absent or is not one SemVer 2.0.0 line, so that both then show "AGNOS" alone and the run is not failed."""
    try:
        lines = Path(VERSION_PATH).read_text(encoding=ENCODING).splitlines()
    except (OSError, ValueError):
        return ""
    match = SEMVER_RE.match(lines[0]) if len(lines) == 1 else None
    return f"{VERSION_PREFIX}{match.group(1)}.{match.group(2)}" if match else ""


def page_elements(model):
    """The elements as the page reads them: those defined in index order, then the undefined ones by name."""
    defined = [e for e in model.elements.values() if e[KEY_KIND] == KEY_ELEMENT]
    undefined = sorted((e for e in model.elements.values() if e[KEY_KIND] == KEY_UNDEFINED), key=lambda e: e["id"])
    fields = ("id", KEY_KIND, KEY_TYPE, "tri", "doc", KEY_FIRST, KEY_LAST, KEY_STATUS, KEY_TITLE)
    return [{f: e[f] for f in fields} for e in defined + undefined]


# DEC-TRC-002: everything the page shows, computed here; sorted so that two runs write the same bytes (RQ-TRC-023).
def page_data(model, analysis, quality, meta, call_graph=None, history=None):
    paths = sorted(model.files)
    data = {
        "meta": meta,
        "elements": page_elements(model),
        KEY_FILES: [model.files[p] for p in paths],
        KEY_EDGES: [[s, d, k, lines] for (s, d, k), lines in sorted(model.edges.items())],
        KEY_COVERAGE: analysis[KEY_COVERAGE],
        "quality": quality,
    }
    if call_graph is not None and not call_graph.core_missing:      # RQ-TRC-026: no key at all without a call graph
        data["callGraph"] = call_graph.page_data({p: n for n, p in enumerate(paths)})
    if history is not None:                                         # RQ-HST-015: no key at all without a history
        data["history"] = {k: v for k, v in history.items() if k != KEY_DELIVERY}
        if KEY_DELIVERY in history:                                 # RQ-TRC-069, DEC-TRC-037: beside the history
            data[KEY_DELIVERY] = history[KEY_DELIVERY]
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
        "CSS": (ASSETS_DIR / "matrix.css").read_text(encoding=ENCODING),
        "LIBRARIES": library_scripts(load_libraries()),
        "SCRIPT": embed_script((ASSETS_DIR / "matrix.js").read_text(encoding=ENCODING)),
        "TITLE": html.escape(title),
        "DATA_SCRIPT": html.escape(data_script),
        "APP_VERSION": html.escape(version_label()),                # RQ-TRC-109, RQ-TRC-116, DEC-TRC-061: the version of the foot and of the About name, never in the data
    }
    template = TEMPLATE_PATH.read_text(encoding=ENCODING)
    return MARKER_RE.sub(lambda m: parts[m.group(1) or m.group(2)], template)


def data_paths(page_path):
    """(<page>.json, <page>.data.js) beside the page (RQ-TRC-010, DEC-TRC-005 as amended)."""
    stem = page_path.stem
    return page_path.with_name(stem + DATA_JSON_SUFFIX), page_path.with_name(stem + DATA_SCRIPT_SUFFIX)


def write_outputs(path, data, title):
    """The page and its two data files, the same JSON in both."""
    json_path, script_path = data_paths(path)
    text = embed_json(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_page(title, script_path.name), encoding=ENCODING, newline="\n")
    json_path.write_text(text + "\n", encoding=ENCODING, newline="\n")
    script_path.write_text(f"{DATA_GLOBAL} = {text};\n", encoding=ENCODING, newline="\n")


# ---- command line ------------------------------------------------------------------------------------------------
# RQ-TRC-001, RQ-TRC-131
def parse_args(argv):
    """The page's options, and the scan options passed to agnos-graph when it builds the graph (RQ-TRC-132)."""
    parser = argparse.ArgumentParser(prog="perf_center.py", description="AGNOS performance center")  # FTR-TRC-001
    parser.add_argument(OPT_PROCESS, required=True, help=f"AGNOS process folder holding {INDEX_NAME}")
    parser.add_argument("--graph", help=f"graph file written by agnos-graph (default: <process>/{agnos_layout.GRAPH_FILE})")
    parser.add_argument("--rebuild", action=STORE_TRUE, help="run agnos-graph even when the graph file exists")
    scan = parser.add_argument_group("scan options, passed to agnos-graph when it builds the graph (see its --help)")
    scan.add_argument(OPT_SOURCES, action=KEY_APPEND, help="source folder to scan (repeatable); needed to build the graph")
    scan.add_argument("--ext", action=KEY_APPEND, help="source extension to scan, replaces agnos-graph's list (repeatable)")
    scan.add_argument("--exclude", action=KEY_APPEND, help="name pattern to skip, replaces agnos-graph's list (repeatable)")
    scan.add_argument("--call-graph", action=STORE_TRUE, help="add the functions and calls, parsed with tree-sitter")
    scan.add_argument("--history", action=STORE_TRUE, help="add who worked on each element and on the code, from git")
    scan.add_argument("--history-since", help="with --history: only the commits authored since this date or duration")
    scan.add_argument("--history-depth", help="with --history: only the N most recent commits")
    parser.add_argument(OPT_OUT, help=f"output page (default: <process>/{DEFAULT_OUT_NAME})")
    parser.add_argument("--title", help="page title (default: the name of the process folder's parent)")
    parser.add_argument(OPT_GENERATED_AT, help="generation time shown by the page (default: now, UTC); fixing it "
                                               "makes the output reproducible")
    return parser.parse_args(argv)


# RQ-TRC-017, RQ-TRC-131
def graph_summary_parts(graph):
    """The call graph and history parts of the summary line, as the graph file wrote them."""
    summaries = graph.get(KEY_META, {}).get(KEY_SUMMARIES, {})
    return [summaries[key] for key in SUMMARY_PARTS if key in summaries]


# RQ-TRC-131, DEC-TRC-075 (TASK-TRC-118)
def page_from_graph(graph, title, generated_at):
    """The page's data and summary line, computed from the graph file."""
    model = model_of(graph)
    analysis = analyse(model)
    call_graph = CallGraphState(graph[KEY_CALL_GRAPH]) if KEY_CALL_GRAPH in graph else None
    quality = scorecard.build(model, analysis, scorecard.load_scoring(), call_graph)    # RQ-TRC-064
    line = "; ".join([summary(model, analysis, quality), *graph_summary_parts(graph)])
    history = None
    if KEY_HISTORY in graph:                                    # RQ-HST-015, RQ-TRC-069: the delivery beside it
        history = dict(graph[KEY_HISTORY])
        if KEY_DELIVERY in graph:
            history[KEY_DELIVERY] = graph[KEY_DELIVERY]
    state = graph.get(KEY_META, {})
    meta = {KEY_TITLE: title, "generatedAt": generated_at, KEY_PROCESS: state.get(KEY_PROCESS),
            KEY_SOURCES: state.get(KEY_SOURCES, []), "summary": line, KEY_LIBRARIES: library_meta(load_libraries())}
    return page_data(model, analysis, quality, meta, call_graph, history), line


# RQ-TRC-132, DEC-TRC-076 (TASK-TRC-119)
def graph_command(args, process, graph_path, generated_at):
    """The command line of agnos-graph's script, with the scan options given to the generator."""
    command = [sys.executable, str(GRAPH_SCRIPT), OPT_PROCESS, str(process), OPT_OUT, str(graph_path),
               OPT_GENERATED_AT, generated_at]
    for source in args.sources:
        command += [OPT_SOURCES, source]
    for name in GRAPH_VALUED:
        value = getattr(args, name)
        for item in value if isinstance(value, list) else [] if value is None else [value]:
            command += ["--" + name.replace("_", "-"), item]
    command += ["--" + name.replace("_", "-") for name in GRAPH_FLAGS if getattr(args, name)]
    return command


# RQ-TRC-132, DEC-TRC-076 (TASK-TRC-119)
def ensure_graph(args, process, graph_path, generated_at):
    """Runs agnos-graph when the graph file is absent or --rebuild is given, its output shown; InputError when it
    cannot be built."""
    if graph_path.is_file() and not args.rebuild:
        return
    if not args.sources:
        raise InputError(f"graph file {graph_path.as_posix()} not found: --sources is needed to build it")
    done = subprocess.run(graph_command(args, process, graph_path, generated_at), capture_output=True, text=True,
                          encoding=ENCODING, check=False)
    sys.stdout.write(done.stdout)
    sys.stderr.write(done.stderr)
    if done.returncode != 0:
        raise InputError(f"agnos-graph could not build {graph_path.as_posix()} (exit {done.returncode})")


# RQ-TRC-131, RQ-TRC-132
def main(argv=None):
    """Writes the page and its data from the graph file and prints the summary line; 1 on an input error."""
    started = time.perf_counter()    # RQ-TRC-107
    args = parse_args(argv)
    process = Path(args.process)
    out = Path(args.out) if args.out else process / DEFAULT_OUT_NAME
    graph_path = Path(args.graph) if args.graph else process / agnos_layout.GRAPH_FILE
    title = args.title or process.resolve().parent.name
    generated_at = args.generated_at or datetime.datetime.now(datetime.timezone.utc).strftime(TIMESTAMP_FORMAT)
    try:
        ensure_graph(args, process, graph_path, generated_at)
        data, line = page_from_graph(load_graph(graph_path), title, generated_at)
    except (InputError, scorecard.ScoringError) as error:
        print(f"agnos-perf-center: {error}", file=sys.stderr)
        return 1
    write_outputs(out, data, title)
    # RQ-TRC-107: the duration is printed only, never put in the generated files.
    print(f"{line}; {out.as_posix()} written in {time.perf_counter() - started:{DURATION_FORMAT}} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
