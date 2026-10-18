"""agnos-trace call graph: the functions and calls of the scanned source files, parsed with tree-sitter.

Implements FTR-TRC-002 after ADR-TRC-004. trace_matrix.py loads this file only for --call-graph (DEC-TRC-013,
RQ-TRC-026, RQ-TRC-039): it imports the standard library only, py-tree-sitter and the grammar wheels when it runs.
Languages are data, assets/callgraph/languages.json and one query file each (DEC-TRC-014, RQ-TRC-032).
"""
import importlib
import json
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = SKILL_DIR / "assets" / "callgraph"
LANGUAGES_PATH = ASSETS_DIR / "languages.json"
REQUIREMENTS_PATH = SKILL_DIR / "requirements-callgraph.txt"
CORE_PACKAGE = "tree-sitter"
CORE_MODULE = "tree_sitter"
LANGUAGE_FUNCTION = "language"     # what a grammar wheel exposes, unless its table entry names another "function"
TABLE_NOTE_PREFIX = "_"            # a key of the language table that is a note, not a language


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


# RQ-TRC-026, RQ-TRC-027 (TASK-TRC-009)
def analyse(files, table=None):
    """The call graph of the scanned files [(shown path, path)]: the languages whose packages are installed only."""
    graph = CallGraph()
    try:
        api = TreeSitter()
    except ImportError:
        graph.core_missing = True
        return graph
    _, graph.missing = load_grammars(load_table() if table is None else table, api)
    return graph
