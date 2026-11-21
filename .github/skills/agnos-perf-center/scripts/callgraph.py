"""agnos-perf-center call graph: the functions and calls of the scanned source files, parsed with tree-sitter.

perf_center.py loads this file only for --call-graph (FTR-TRC-002, ADR-TRC-004, DEC-TRC-013,
RQ-TRC-026, RQ-TRC-039): it imports the standard library only, py-tree-sitter and the grammar wheels when it runs.
Languages are data, assets/callgraph/languages.json and one query file each (DEC-TRC-014, RQ-TRC-032).
"""
import importlib
import json
import re
from pathlib import Path

# RQ-TRC-067: a literal written more than once is a named constant.
KEY_SCOPE = "scope"
ENCODING = "utf-8"
KEY_REPLACE = "replace"
KEY_SCOPES = "scopes"
KEY_SCOPE_INDEX = "scope_index"
KEY_FUNCTIONS = "functions"
KEY_CALLS = "calls"
KEY_NODE = "node"
KEY_FILE = "file"
KEY_FIRST = "first"
KEY_LAST = "last"
KEY_QUALIFIED = "qualified"
KEY_NAME = "name"
KEY_TEXT = "text"

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
SCOPE, SCOPE_NAME = KEY_SCOPE, "scope.name"
CALL, CALL_NAME = "call", "call.name"
COMMENT = "comment"
# DEC-TRC-069: the optional captures, merged per captured node.
CALL_RECEIVER = "call.receiver"                    # the receiver, where the called name is a node of its own (Java)
KINDS = ((DEFINITION, DEFINITION_NAME), (SCOPE, SCOPE_NAME), (CALL, CALL_NAME), (COMMENT, None))
KEY_PREFIX = "fn"                                  # a function's key: fn:<file>:<first line> (DEC-TRC-016)
MAX_AMBIGUOUS = 5                                  # candidates linked at most for one ambiguous call (DEC-TRC-015)
NAMESPACE_KIND, CLASS_KIND = "namespace", "class"  # the box kinds of a scope (DEC-TRC-019)
NO_SCOPE = -1                                      # the scope index of a function without box (DEC-TRC-019)
FOLDER_SEPARATOR = "/"                             # in the shown paths of the files
TEMPLATE_ARGS_RE = re.compile(r"<[^<>]*>")         # innermost template or generic arguments, removed until none is left
MEMBER_RE = re.compile(r"::|\.|->")                # what separates a called name from its receiver or qualifier
# a name a call can be resolved by; "(*fp)" is not one; "$" and a leading "#" for JavaScript (DEC-TRC-026)
NAME_RE = re.compile(r"^[~#]?[A-Za-z_$][\w$]*$|^operator\W")
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
    """One language of the table, loaded: its name, tree-sitter language, compiled query, scope separator and the box
    kind of each scope node type (RQ-TRC-047, DEC-TRC-019), and its receiver words (RQ-TRC-124, DEC-TRC-070)."""

    def __init__(self, name, entry, language, query):
        self.name = name
        self.language = language
        self.query = query
        self.separator = entry["separator"]
        self.scopes = entry.get(KEY_SCOPES, {})
        self.self_words = frozenset(entry.get("self", ()))      # the receiver naming the caller's own object
        self.super_words = frozenset(entry.get("super", ()))    # the receiver naming its parent object


def load_table(path=LANGUAGES_PATH):
    """The language table: {language: {extensions, package, module, query, separator[, scopes][, function]}}."""
    table = json.loads(Path(path).read_text(encoding=ENCODING))
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
        query = api.query(language, (ASSETS_DIR / entry["query"]).read_text(encoding=ENCODING))
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
    """A declared or called name without its template arguments and spaces: 'h<int>' -> 'h'; the '::' a removed
    argument leaves at the end goes too, Rust's 'f::<u8>' -> 'f' (DEC-TRC-026)."""
    text = SPACE_RE.sub("", text)
    while True:
        stripped = TEMPLATE_ARGS_RE.sub("", text)
        if stripped == text:
            return text.strip(":")
        text = stripped


# RQ-TRC-124, DEC-TRC-071
def split_call(name):
    """(receiver or qualifier, name a call is looked up by) of 'a.b->c::d': ('a.b->c', 'd'); ('', 'd') of 'd'."""
    separators = list(MEMBER_RE.finditer(name))
    if not separators:
        return "", name
    return name[:separators[-1].start()], name[separators[-1].end():]


def node_key(node):
    return node.start_byte, node.end_byte, node.type


# DEC-TRC-069 (TASK-TRC-113)
def captures_of(grammar, api, root):
    """The query's captures under the root, by kind, in start order: one entry {capture name: [nodes]} per captured
    definition, scope, call or comment node, the captures of all the matches of that node merged, so that an optional
    capture or several bases of one scope are all kept; an entry without the name capture of its kind is dropped."""
    found = {kind: {} for kind, _ in KINDS}
    for _, caps in api.matches(grammar.query, root):
        for kind, _ in KINDS:
            if kind in caps:
                entry = found[kind].setdefault(node_key(caps[kind][0]), {})
                for capture, nodes in caps.items():
                    known = entry.setdefault(capture, [])
                    known += [node for node in nodes if node_key(node) not in {node_key(k) for k in known}]
                break
    return {kind: sorted((entry for entry in found[kind].values() if name is None or name in entry),
                         key=lambda entry: entry[kind][0].start_byte) for kind, name in KINDS}


def first(entry, capture):
    """The first node of a capture of an entry, None when the match had none."""
    return entry.get(capture, (None,))[0]


def comment_tops(comments, lines):
    """{last row of a comment that starts its line: first row of the comment block ending there} (rows from 0). A
    comment that holds its line's end, as Rust's line comments do, ends at column 0 of the next row: its last row is the
    one before (DEC-TRC-026)."""
    tops = {}
    for entry in comments:
        node = entry[COMMENT][0]
        row, column = node.start_point
        if lines[row][:column].strip():
            continue                       # a comment after code on its line ends no block above a definition
        end_row, end_column = node.end_point
        last = end_row - 1 if end_column == 0 and end_row > row else end_row
        tops[last] = tops.get(row - 1, row)
    return tops


def block_top(tops, first_row):
    """The first row of the comment block ending on the row just above first_row, else first_row."""
    return tops.get(first_row - 1, first_row)


def text_of(node):
    return node.text.decode(ENCODING, KEY_REPLACE)


def scope_names(node, scopes):
    """The names of the scopes enclosing the node, outermost first."""
    return [plain_name(text_of(entry[SCOPE_NAME][0])) for entry in scopes
            if entry[SCOPE][0].start_byte <= node.start_byte and node.end_byte <= entry[SCOPE][0].end_byte]


# RQ-TRC-028, RQ-TRC-031, DEC-TRC-016 (TASK-TRC-010)
def file_functions(shown, grammar, api, data, cited, evidence):
    """The functions defined in one file, in line order, each with the IDs of its lines and of the comment block just
    above it; the file's calls as (call node, called expression node); its declared scopes; and whether its tree holds an
    error or a missing node (RQ-TRC-122, DEC-TRC-067)."""
    root = api.parse(grammar.language, data)
    lines = data.decode(ENCODING, KEY_REPLACE).split("\n")
    caps = captures_of(grammar, api, root)
    tops = comment_tops(caps[COMMENT], lines)
    functions = []
    separator = grammar.separator
    for entry in caps[DEFINITION]:
        node, name_node = entry[DEFINITION][0], entry[DEFINITION_NAME][0]
        qualified = separator.join(scope_names(node, caps[SCOPE]) + [plain_name(text_of(name_node))])
        first, last = node.start_point[0] + 1, node.end_point[0] + 1
        top = block_top(tops, first - 1) + 1
        ids = {}
        for line, target, proof in cited.get(shown, ()):
            if top <= line <= last:
                ids.setdefault(target, []).append(proof)
        functions.append({KEY_FILE: shown, KEY_FIRST: first, KEY_LAST: last, KEY_QUALIFIED: qualified,
                          KEY_NAME: qualified.split(separator)[-1],
                          KEY_SCOPE: separator.join(qualified.split(separator)[:-1]),
                          LANGUAGE_FUNCTION: grammar.name, KEY_TEXT: evidence(first, lines[first - 1])[1], "ids": ids,
                          KEY_NODE: node})
    return functions, caps[CALL], declared_scopes(grammar, caps[SCOPE]), root.has_error


# RQ-TRC-047, DEC-TRC-019 (TASK-TRC-023)
def declared_scopes(grammar, scopes):
    """{qualified name: kind} of the scopes of one file whose node type has a box kind in the language table."""
    nodes = [entry[SCOPE][0] for entry in scopes]
    return {grammar.separator.join(scope_names(node, scopes)): grammar.scopes[node.type]
            for node in nodes if node.type in grammar.scopes}


# RQ-TRC-123, DEC-TRC-068 (TASK-TRC-111): the causes of an unresolved call; the first three make up the external count.
LIBRARY, CONSTRUCTOR, CROSS_LANGUAGE, UNNAMED, TOP_LEVEL = "library", "constructor", "cross-language", "unnamed", "top-level"
CAUSES = (LIBRARY, CONSTRUCTOR, CROSS_LANGUAGE, UNNAMED, TOP_LEVEL)


def call_sites(functions, calls, unresolved):
    """(caller, called name, line, receiver) of each call whose name can be resolved, the caller being the innermost
    function holding the call, the receiver what stands before the name ('' for none, RQ-TRC-124); nodes in start
    order, one sweep with a stack of the open functions. A call outside any function counts as top-level, one whose
    expression is no name as unnamed, in unresolved (RQ-TRC-123)."""
    sites, stack, pending = [], [], list(reversed(functions))
    for entry in calls:
        call, expression = entry[CALL][0], entry[CALL_NAME][0]
        while pending and pending[-1][KEY_NODE].start_byte <= call.start_byte:
            function = pending.pop()
            while stack and stack[-1][KEY_NODE].end_byte <= function[KEY_NODE].start_byte:
                stack.pop()
            stack.append(function)
        while stack and stack[-1][KEY_NODE].end_byte <= call.start_byte:
            stack.pop()
        receiver, name = split_call(plain_name(text_of(expression)))
        receiver_node = first(entry, CALL_RECEIVER)
        if receiver_node is not None:
            receiver = plain_name(text_of(receiver_node))
        if not stack:
            unresolved[TOP_LEVEL] += 1
        elif not NAME_RE.match(name):
            unresolved[UNNAMED] += 1
        else:
            sites.append((stack[-1], name, call.start_point[0] + 1, receiver))
    return sites


# ---- resolution --------------------------------------------------------------------------------------------------
def folder_of(path):
    return path.rpartition(FOLDER_SEPARATOR)[0]


def preferred(caller, candidates, separator):
    """The candidates of the first non-empty level: the caller's class, its namespace, its file, its folder, the
    project (DEC-TRC-015, RQ-TRC-029)."""
    scope = caller[KEY_SCOPE]
    namespace = scope.rpartition(separator)[0]
    levels = (
        lambda f: scope and f[KEY_SCOPE] == scope,
        lambda f: namespace and f[KEY_SCOPE] == namespace,
        lambda f: f[KEY_FILE] == caller[KEY_FILE],
        lambda f: folder_of(f[KEY_FILE]) == folder_of(caller[KEY_FILE]),
    )
    for level in levels:
        chosen = [f for f in candidates if level(f)]
        if chosen:
            return chosen
    return candidates


# RQ-TRC-123, DEC-TRC-068 (TASK-TRC-111)
def unresolved_cause(language, name, scope_names, defined_names):
    """Why a name with no definition in the caller's language is unresolved: a scope of that language is instantiated,
    another language defines it, or nothing scanned does."""
    if (language, name) in scope_names:
        return CONSTRUCTOR
    return CROSS_LANGUAGE if name in defined_names else LIBRARY


# RQ-TRC-124, RQ-TRC-126, DEC-TRC-071, DEC-TRC-072 (TASK-TRC-113)
class Hierarchy:
    """The scopes of each language, by qualified name and by last part, their kind, and the classes each class derives
    from; walked breadth first, nearest ancestors first, each class once."""

    def __init__(self, kinds=None, separators=None):
        self.kinds = dict(kinds or {})                 # {(language, qualified scope): kind}
        self.by_last = {}
        for language, scope in self.kinds:
            last = scope.split(separators[language])[-1] if separators else scope
            self.by_last.setdefault((language, last), set()).add(scope)
        self.parents = {}                              # {(language, class): {qualified scope it derives from}}

    def is_class(self, language, scope):
        return self.kinds.get((language, scope)) == CLASS_KIND

    def named(self, language, name):
        """The qualified scopes whose last part is name."""
        return set(self.by_last.get((language, name), ()))

    def ancestors(self, language, scopes):
        """[{scopes}] of the ancestors of the given scopes, one set per generation, nearest first."""
        seen, levels, current = set(scopes), [], set(scopes)
        while current:
            current = {parent for scope in current for parent in self.parents.get((language, scope), ())} - seen
            seen |= current
            if current:
                levels.append(current)
        return levels


def restriction(caller, receiver, grammar, hierarchy):
    """The levels of scopes [{scope}] a certain receiver confines the callee to, nearest first: the caller's class then
    its ancestors for its own object, its ancestors for its parent, a named scope then its ancestors; None for no
    receiver or one of unknown type (RQ-TRC-124, DEC-TRC-071)."""
    language, scope = grammar.name, caller[KEY_SCOPE]
    if receiver in grammar.self_words or receiver in grammar.super_words:
        if not hierarchy.is_class(language, scope):
            return None                               # 'this' in a function of no class: nothing is certain
        ancestors = hierarchy.ancestors(language, {scope})
        return ancestors if receiver in grammar.super_words else [{scope}, *ancestors]
    targets = hierarchy.named(language, split_call(receiver)[1]) if receiver else set()
    return [targets, *hierarchy.ancestors(language, targets)] if targets else None


def nearest(candidates, levels):
    """The candidates of the first level holding one, else none."""
    for level in levels:
        chosen = [f for f in candidates if f[KEY_SCOPE] in level]
        if chosen:
            return chosen
    return []


# RQ-TRC-029, RQ-TRC-124 (TASK-TRC-113)
def choose(caller, signature, grammar, definitions, hierarchy):
    """(the candidates of one call signature (name, receiver), whether a certain receiver confined them): those of the
    receiver's scopes first, then the preferred ones (DEC-TRC-071)."""
    name, receiver = signature
    candidates = definitions.get((grammar.name, name), [])
    levels = restriction(caller, receiver, grammar, hierarchy) if candidates else None
    if levels is not None:
        candidates = nearest(candidates, levels)
    return (preferred(caller, candidates, grammar.separator) if candidates else []), levels is not None


# RQ-TRC-029, RQ-TRC-030, RQ-TRC-040, RQ-TRC-123, RQ-TRC-124 (TASK-TRC-011, TASK-TRC-111, TASK-TRC-113)
def resolve(graph, sites, grammars, scope_names=frozenset(), hierarchy=None):
    """Links each (caller, call signature) to its definitions, in the caller's language: those a certain receiver
    confines it to first, then the preferred ones; one plain link, two to five ambiguous ones, else none and counted as
    ambiguous; no definition counts as external, by cause, a certain receiver with none in its scopes as library;
    grammars: {language: Grammar}; scope_names: {(language, last part of a declared scope)}."""
    hierarchy = hierarchy or Hierarchy()
    index = {id(f): n for n, f in enumerate(graph.functions)}
    definitions = {}
    for function in graph.functions:
        definitions.setdefault((function[LANGUAGE_FUNCTION], function[KEY_NAME]), []).append(function)
    defined_names = {key[1] for key in definitions}
    grouped = {}
    for caller, name, line, *rest in sites:
        grouped.setdefault((index[id(caller)], (name, *rest)), []).append(line)
    links = {}
    for (caller_index, signature), lines in grouped.items():
        caller = graph.functions[caller_index]
        grammar = grammars[caller[LANGUAGE_FUNCTION]]
        chosen, certain = choose(caller, signature, grammar, definitions, hierarchy)
        if not chosen:
            graph.external += 1
            name = signature[0]
            cause = LIBRARY if certain else unresolved_cause(grammar.name, name, scope_names, defined_names)
            graph.unresolved[cause] += 1
        elif len(chosen) > MAX_AMBIGUOUS:
            graph.ambiguous += 1
        else:
            ambiguous = len(chosen) > 1
            graph.ambiguous += int(ambiguous)
            for callee in chosen:
                link = links.setdefault((caller_index, index[id(callee)]), [ambiguous, set()])
                link[1].update(lines)
    graph.calls = [[caller, callee, ambiguous, sorted(lines)] for (caller, callee), (ambiguous, lines)
                   in sorted(links.items())]


def assign_keys(functions):
    """fn:<file>:<first line>, made unique by '.<n>' when two definitions start on one line (DEC-TRC-016)."""
    taken = set()
    for function in functions:
        key = f"{KEY_PREFIX}:{function[KEY_FILE]}:{function[KEY_FIRST]}"
        candidate, n = key, 1
        while candidate in taken:
            n += 1
            candidate = f"{key}.{n}"
        taken.add(candidate)
        function["key"] = candidate
        function["dup"] = n if n > 1 else 0


# RQ-TRC-047, DEC-TRC-019 (TASK-TRC-023)
def assign_scopes(graph, declared, grammars):
    """graph.scopes, [qualified name, kind, parent index] of each scope holding a function, in name order, and each
    function's scope_index (NO_SCOPE: none, or a language without scopes). A part of a function's scope that no
    scanned file declares is a class when it is the innermost part, else a namespace; a class guess wins over a
    namespace one."""
    kinds = {}
    for function in graph.functions:
        grammar = grammars[function[LANGUAGE_FUNCTION]]
        if not (grammar.scopes and function[KEY_SCOPE]):
            continue
        parts = function[KEY_SCOPE].split(grammar.separator)
        for n in range(len(parts)):
            name = grammar.separator.join(parts[:n + 1])
            was_class = kinds.get(name, (None,))[0] == CLASS_KIND
            guessed = CLASS_KIND if was_class or n == len(parts) - 1 else NAMESPACE_KIND
            kinds[name] = (declared.get(name, guessed), grammar.separator)
    index = {name: n for n, name in enumerate(sorted(kinds))}
    graph.scopes = [[name, kind, index.get(name.rpartition(separator)[0], NO_SCOPE)]
                    for name, (kind, separator) in sorted(kinds.items())]
    for function in graph.functions:
        scoped = grammars[function[LANGUAGE_FUNCTION]].scopes
        function[KEY_SCOPE_INDEX] = index.get(function[KEY_SCOPE], NO_SCOPE) if scoped else NO_SCOPE


# RQ-TRC-124, DEC-TRC-072 (TASK-TRC-113)
def scope_hierarchy(graph, declared, grammars):
    """The Hierarchy of the declared scopes {(language, qualified): kind} and of the scopes holding a function, with the
    kinds assign_scopes gave them."""
    kinds = dict(declared)
    given = {name: kind for name, kind, _ in graph.scopes}
    for function in graph.functions:
        scope, language = function[KEY_SCOPE], function[LANGUAGE_FUNCTION]
        if scope and scope in given:
            kinds.setdefault((language, scope), given[scope])
    return Hierarchy(kinds, {name: grammar.separator for name, grammar in grammars.items()})


# ---- the call graph ----------------------------------------------------------------------------------------------
class CallGraph:
    """The functions and calls found, the ambiguous and external call counts, the files read and those that did not
    parse (RQ-TRC-122), the unresolved calls by cause (RQ-TRC-123), and the packages that were missing."""

    def __init__(self):
        self.functions = []
        self.calls = []
        self.scopes = []
        self.ambiguous = 0
        self.external = 0
        self.parsed = []
        self.unparsed = []
        self.unresolved = dict.fromkeys(CAUSES, 0)            # RQ-TRC-123, DEC-TRC-068
        self.core_missing = False
        self.missing = []

    def summary(self):
        """The part of the generator's last line about the call graph (RQ-TRC-017, RQ-TRC-027)."""
        if self.core_missing:
            return f"call graph skipped: {CORE_PACKAGE} not installed, run: {install_command()}"
        line = (f"call graph: {len(self.functions)} functions, {len(self.calls)} calls, ambiguous {self.ambiguous}, "
                f"external {self.external}, unparsed {len(self.unparsed)}")    # RQ-TRC-122
        if self.missing:
            line += f"; skipped: {', '.join(self.missing)} not installed, run: {install_command()}"
        return line

    # RQ-TRC-038, DEC-TRC-016 (TASK-TRC-012)
    def page_data(self, file_index):
        """The call graph as the page reads it, names stored once:
        functions [file index, first, last, qualified name, language index, first-line text, key suffix (0: none),
        scope index (-1: none)]; scopes [qualified name, kind, parent index (-1: none)] (RQ-TRC-047, DEC-TRC-019);
        calls, one flat list of integers per caller in function order: caller - previous caller, callee count, then per
        callee: callee - caller, ambiguous + 2 * line count, each call-site line - the caller's first line;
        ids [function index, ID, [lines]] (the proofs' texts are the file's). The functions citing no ID are the
        findings of the quality block's "functions traced" check, stored there once (ADR-TRC-008)."""
        languages = sorted({f[LANGUAGE_FUNCTION] for f in self.functions})
        functions = [[file_index[f[KEY_FILE]], f[KEY_FIRST], f[KEY_LAST], f[KEY_QUALIFIED],
                      languages.index(f[LANGUAGE_FUNCTION]), f[KEY_TEXT], f["dup"], f[KEY_SCOPE_INDEX]]
                     for f in self.functions]
        by_caller = {}
        for caller, callee, ambiguous, lines in self.calls:
            by_caller.setdefault(caller, []).append((callee, ambiguous, lines))
        calls, previous = [], 0
        for caller, callees in by_caller.items():
            first = self.functions[caller][KEY_FIRST]
            calls += [caller - previous, len(callees)]
            for callee, ambiguous, lines in callees:
                calls += [callee - caller, int(ambiguous) + 2 * len(lines), *(line - first for line in lines)]
            previous = caller
        ids = [[n, target, [proof[0] for proof in proofs]] for n, f in enumerate(self.functions)
               for target, proofs in sorted(f["ids"].items())]
        return {KEY_FUNCTIONS: functions, "languages": languages, KEY_SCOPES: self.scopes, KEY_CALLS: calls, "ids": ids,
                "counts": {KEY_FUNCTIONS: len(self.functions), KEY_CALLS: len(self.calls), "ambiguous": self.ambiguous,
                           "external": self.external, "parsed": len(self.parsed),
                           "unparsed": len(self.unparsed),                               # RQ-TRC-122
                           "unresolved": dict(self.unresolved)}}                         # RQ-TRC-123


# RQ-TRC-026, RQ-TRC-027, RQ-TRC-040, RQ-TRC-122, RQ-TRC-123 (TASK-TRC-009, TASK-TRC-010, TASK-TRC-110, TASK-TRC-111)
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
    sites, declared, scope_names, kinds = [], {}, set(), {}
    for shown, path in sorted(files):
        grammar = grammars.get(path.suffix.lower())
        if grammar is not None:
            functions, calls, scopes, broken = file_functions(shown, grammar, api, path.read_bytes(), cited, evidence)
            graph.parsed.append(shown)                     # RQ-TRC-122, DEC-TRC-067: the population of files-parsed
            if broken:
                graph.unparsed.append(shown)
            graph.functions += functions
            sites += call_sites(functions, calls, graph.unresolved)
            for name, kind in scopes.items():
                declared.setdefault(name, kind)
                kinds.setdefault((grammar.name, name), kind)                           # RQ-TRC-124
                scope_names.add((grammar.name, name.split(grammar.separator)[-1]))     # RQ-TRC-123
    assign_keys(graph.functions)
    by_name = {g.name: g for g in grammars.values()}
    assign_scopes(graph, declared, by_name)
    resolve(graph, sites, by_name, scope_names, scope_hierarchy(graph, kinds, by_name))
    for function in graph.functions:
        del function[KEY_NODE]
    return graph
