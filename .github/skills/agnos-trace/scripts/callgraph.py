"""agnos-trace call graph: the functions and calls of the scanned source files, parsed with tree-sitter.

Implements FTR-TRC-002 after ADR-TRC-004. trace_matrix.py loads this file only for --call-graph (DEC-TRC-013,
RQ-TRC-026, RQ-TRC-039): it imports the standard library only, py-tree-sitter and the grammar wheels when it runs.
Languages are data, assets/callgraph/languages.json and one query file each (DEC-TRC-014, RQ-TRC-032).
"""
import importlib
import json
import re
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = SKILL_DIR / "assets" / "callgraph"
LANGUAGES_PATH = ASSETS_DIR / "languages.json"
REQUIREMENTS_PATH = SKILL_DIR / "requirements-callgraph.txt"
CORE_PACKAGE = "tree-sitter"
CORE_MODULE = "tree_sitter"
LANGUAGE_FUNCTION = "language"     # what a grammar wheel exposes, unless its table entry names another "function"
TABLE_NOTE_PREFIX = "_"            # a key of the language table that is a note, not a language

# DEC-TRC-014: the fixed capture names of a query file.
DEFINITION, DEFINITION_NAME = "definition", "definition.name"
SCOPE, SCOPE_NAME = "scope", "scope.name"
CALL, CALL_NAME = "call", "call.name"
COMMENT = "comment"
KEY_PREFIX = "fn"                                  # a function's key: fn:<file>:<first line> (DEC-TRC-016)
TEMPLATE_ARGS_RE = re.compile(r"<[^<>]*>")         # innermost template or generic arguments, removed until none is left
MEMBER_RE = re.compile(r"::|\.|->")                # what separates a called name from its receiver or qualifier
NAME_RE = re.compile(r"^~?[A-Za-z_]\w*$|^operator\W")  # a name a call can be resolved by; "(*fp)" is not one
SPACE_RE = re.compile(r"\s+")


# ---- py-tree-sitter ----------------------------------------------------------------------------------------------
class TreeSitter:
    """The version-specific part of py-tree-sitter's API, in one place (DEC-TRC-013; written for 0.25). Raises
    ImportError when the package is not installed."""

    def __init__(self):
        self.api = importlib.import_module(CORE_MODULE)

    def language(self, grammar_module, function):
        return self.api.Language(getattr(grammar_module, function)())

    def query(self, language, text):
        return self.api.Query(language, text)

    def parse(self, language, data):
        return self.api.Parser(language).parse(data).root_node

    def matches(self, query, node):
        """The query's matches under the node: [(pattern index, {capture name: [nodes]})]."""
        return self.api.QueryCursor(query).matches(node)


# ---- languages ---------------------------------------------------------------------------------------------------
# RQ-TRC-032, DEC-TRC-014
class Grammar:
    """One language of the table, loaded: its name, tree-sitter language, compiled query and scope separator."""

    def __init__(self, name, entry, language, query):
        self.name = name
        self.language = language
        self.query = query
        self.separator = entry["separator"]


def load_table(path=LANGUAGES_PATH):
    """The language table: {language: {extensions, package, module, query, separator[, function]}}."""
    table = json.loads(Path(path).read_text(encoding="utf-8"))
    return {name: entry for name, entry in table.items() if not name.startswith(TABLE_NOTE_PREFIX)}


# RQ-TRC-027
def load_grammars(table, api):
    """({extension: Grammar}, [package of each language whose grammar wheel is not installed])."""
    grammars, missing = {}, []
    for name, entry in table.items():
        try:
            module = importlib.import_module(entry["module"])
        except ImportError:
            missing.append(entry["package"])
            continue
        language = api.language(module, entry.get("function", LANGUAGE_FUNCTION))
        query = api.query(language, (ASSETS_DIR / entry["query"]).read_text(encoding="utf-8"))
        grammar = Grammar(name, entry, language, query)
        for extension in entry["extensions"]:
            grammars[extension] = grammar
    return grammars, missing


def install_command():
    """The command that installs the supported packages, the requirements file shown from the current folder."""
    try:
        shown = REQUIREMENTS_PATH.relative_to(Path.cwd().resolve())
    except ValueError:
        shown = REQUIREMENTS_PATH
    return f"pip install -r {shown.as_posix()}"


# ---- functions ---------------------------------------------------------------------------------------------------
def plain_name(text):
    """A declared or called name without its template arguments and spaces: 'h<int>' -> 'h'."""
    text = SPACE_RE.sub("", text)
    while True:
        stripped = TEMPLATE_ARGS_RE.sub("", text)
        if stripped == text:
            return text.lstrip(":")
        text = stripped


def last_part(name):
    """The name a call is looked up by: the last part of 'a.b->c::d'."""
    return MEMBER_RE.split(name)[-1]


def captures_of(grammar, api, root):
    """The query's captures under the root, by kind: definitions and scopes as (node, name node), calls as (node,
    called expression node), comments as nodes; each node once."""
    found = {DEFINITION: {}, SCOPE: {}, CALL: {}, COMMENT: {}}
    for _, caps in api.matches(grammar.query, root):
        for kind, name in ((DEFINITION, DEFINITION_NAME), (SCOPE, SCOPE_NAME), (CALL, CALL_NAME), (COMMENT, None)):
            if kind in caps:
                node = caps[kind][0]
                found[kind][(node.start_byte, node.end_byte)] = (node, caps[name][0] if name else None)
                break
    return {kind: sorted(nodes.values(), key=lambda pair: pair[0].start_byte) for kind, nodes in found.items()}


def comment_tops(comments, lines):
    """{last row of a comment that starts its line: first row of the comment block ending there} (rows from 0)."""
    tops = {}
    for node, _ in comments:
        row, column = node.start_point
        if lines[row][:column].strip():
            continue                       # a comment after code on its line ends no block above a definition
        tops[node.end_point[0]] = tops.get(row - 1, row)
    return tops


def block_top(tops, first_row):
    """The first row of the comment block ending on the row just above first_row, else first_row."""
    return tops.get(first_row - 1, first_row)


def text_of(node):
    return node.text.decode("utf-8", "replace")


def scope_names(node, scopes):
    """The names of the scopes enclosing the node, outermost first."""
    return [plain_name(text_of(name)) for scope, name in scopes
            if scope.start_byte <= node.start_byte and node.end_byte <= scope.end_byte]


# RQ-TRC-028, RQ-TRC-031, DEC-TRC-016 (TASK-TRC-010)
def file_functions(shown, grammar, api, data, cited, evidence):
    """The functions defined in one file, in line order, each with the IDs of its lines and of the comment block just
    above it; and the file's calls as (call node, called expression node)."""
    root = api.parse(grammar.language, data)
    lines = data.decode("utf-8", "replace").split("\n")
    caps = captures_of(grammar, api, root)
    tops = comment_tops(caps[COMMENT], lines)
    functions = []
    separator = grammar.separator
    for node, name_node in caps[DEFINITION]:
        qualified = separator.join(scope_names(node, caps[SCOPE]) + [plain_name(text_of(name_node))])
        first, last = node.start_point[0] + 1, node.end_point[0] + 1
        top = block_top(tops, first - 1) + 1
        ids = {}
        for line, target, proof in cited.get(shown, ()):
            if top <= line <= last:
                ids.setdefault(target, []).append(proof)
        functions.append({"file": shown, "first": first, "last": last, "qualified": qualified,
                          "name": qualified.split(separator)[-1], "scope": separator.join(qualified.split(separator)[:-1]),
                          "language": grammar.name, "text": evidence(first, lines[first - 1])[1], "ids": ids,
                          "node": node})
    return functions, caps[CALL]


def assign_keys(functions):
    """fn:<file>:<first line>, made unique by '.<n>' when two definitions start on one line (DEC-TRC-016)."""
    taken = set()
    for function in functions:
        key = f"{KEY_PREFIX}:{function['file']}:{function['first']}"
        candidate, n = key, 1
        while candidate in taken:
            n += 1
            candidate = f"{key}.{n}"
        taken.add(candidate)
        function["key"] = candidate


# ---- the call graph ----------------------------------------------------------------------------------------------
class CallGraph:
    """The functions and calls found, the ambiguous and external call counts, and the packages that were missing."""

    def __init__(self):
        self.functions = []
        self.calls = []
        self.ambiguous = 0
        self.external = 0
        self.core_missing = False
        self.missing = []

    def summary(self):
        """The part of the generator's last line about the call graph (RQ-TRC-017, RQ-TRC-027)."""
        if self.core_missing:
            return f"call graph skipped: {CORE_PACKAGE} not installed, run: {install_command()}"
        line = (f"call graph: {len(self.functions)} functions, {len(self.calls)} calls, ambiguous {self.ambiguous}, "
                f"external {self.external}")
        if self.missing:
            line += f"; skipped: {', '.join(self.missing)} not installed, run: {install_command()}"
        return line


# RQ-TRC-026, RQ-TRC-027, RQ-TRC-040 (TASK-TRC-009, TASK-TRC-010)
def analyse(files, cited, evidence, table=None):
    """The call graph of the scanned files [(shown path, path)], for the languages whose packages are installed;
    cited: {shown path: [(line, ID, proof)]}, the file's ID citations; evidence(line, text): a proof line. Functions
    come in file path, then line order."""
    graph = CallGraph()
    try:
        api = TreeSitter()
    except ImportError:
        graph.core_missing = True
        return graph
    grammars, graph.missing = load_grammars(load_table() if table is None else table, api)
    for shown, path in sorted(files):
        grammar = grammars.get(path.suffix.lower())
        if grammar is not None:
            functions, _ = file_functions(shown, grammar, api, path.read_bytes(), cited, evidence)
            graph.functions += functions
    assign_keys(graph.functions)
    return graph
