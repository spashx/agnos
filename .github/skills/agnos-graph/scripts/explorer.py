"""The graph explorer page of agnos-graph (FTR-TRC-014; ADR-TRC-025: DEC-TRC-084, DEC-TRC-085, DEC-TRC-088).

graph.py calls write_explorer() after writing the graph file, only with --explorer (RQ-TRC-144): the page and its data
script are written beside the graph, and the graph file is left as written (RQ-TRC-156). The page is assembled from
assets/explorer/ by replacing markers, as the performance center assembles its own (DEC-TRC-084); the tokens are compiled to
CSS custom properties as the performance center does (DEC-TRC-009), from the explorer's own copy (owner's option A).
Python >= 3.9, standard library only.
"""
import html
import json
import re
from pathlib import Path

import agnos_layout  # RQ-PLG-036: the version file's name, generated beside this script

# RQ-TRC-067: a literal written more than once is a named constant.
ENCODING = "utf-8"
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "explorer"
TEMPLATE_PATH = ASSETS_DIR / "explorer.html"
STYLE_PATH = ASSETS_DIR / "explorer.css"
SCRIPT_PATH = ASSETS_DIR / "explorer.js"
TOKENS_PATH = ASSETS_DIR / "tokens.json"
LIBRARIES_PATH = ASSETS_DIR / "libraries.json"
PRESETS_PATH = ASSETS_DIR / "presets.json"      # RQ-TRC-153, DEC-TRC-093: the default saved query buttons
PAGE_NAME = "graph-explorer.html"               # RQ-TRC-144, DEC-TRC-085: lowercase, beside the graph file
DATA_SCRIPT_NAME = "agnos-graph.data.js"        # RQ-TRC-145, DEC-TRC-088
DATA_GLOBAL = "window.AGNOS_GRAPH"              # DEC-TRC-088: the global the page reads
PAGE_TITLE = "Graph explorer"                   # RQ-TRC-155: English
KEY_GLOBAL, KEY_SEMANTIC, KEY_COMPONENT, KEY_LIBRARIES = "global", "semantic", "component", "libraries"
MARKER_RE = re.compile(r"/\*@(TOKENS|CSS|SCRIPT)@\*/|@(TITLE|DATA_SCRIPT|LIBRARIES|PRESETS|APP_VERSION|LIBRARY_RECORD)@")
# RQ-GXP-004, DEC-GXP-002: the version of the About name, read as perf_center.py reads it (DEC-TRC-061), copied (option A)
VERSION_PATH = Path(__file__).resolve().parent.parent.parent / "agnos-init" / "assets" / "templates" / agnos_layout.VERSION
VERSION_PREFIX = "v."
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
                       r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$")
LIBRARY_KEYS = ("name", "version", "licence")   # RQ-GXP-003: what a licence badge says of a library
TOKEN_NAME_RE = re.compile(r"^[a-z][a-z0-9-]*$")
SCRIPT_END_RE = re.compile(r"</(script)", re.I)


class ExplorerError(Exception):
    """An asset of the explorer that cannot be read or holds an unresolved token."""


# RQ-TRC-147, RQ-TRC-157, DEC-TRC-009, DEC-TRC-091
def tokens_css(tokens):
    """The custom properties of the page: --s-<semantic> from a global value, --c-<component> as var(--s-<semantic>);
    an unresolved reference is an error (DEC-TRC-009). Light theme only (FTR-TRC-014)."""
    lines = [":root {", "  color-scheme: light;"]
    for name, ref in tokens[KEY_SEMANTIC].items():
        if not TOKEN_NAME_RE.match(name) or ref not in tokens[KEY_GLOBAL]:
            raise ExplorerError(f"design token '{name}' refers to '{ref}', which is not a global token")
        lines.append(f"  --s-{name}: {tokens[KEY_GLOBAL][ref]};")
    for name, ref in tokens[KEY_COMPONENT].items():
        if not TOKEN_NAME_RE.match(name) or ref not in tokens[KEY_SEMANTIC]:
            raise ExplorerError(f"component token '{name}' refers to '{ref}', which is not a semantic token")
        lines.append(f"  --c-{name}: var(--s-{ref});")
    return "\n".join([*lines, "}"])


def read_json(path):
    """A JSON asset of the explorer, or ExplorerError."""
    try:
        return json.loads(path.read_text(encoding=ENCODING))
    except (OSError, ValueError) as error:
        raise ExplorerError(f"{path.name}: {error}") from error


# RQ-TRC-150, DEC-TRC-090: the libraries the page loads from cdnjs, checked by their integrity hash.
def library_scripts():
    """One script element per library recorded in libraries.json; none when the file is absent."""
    if not LIBRARIES_PATH.is_file():
        return ""
    return "\n".join(f'<script src="{html.escape(lib["url"])}" integrity="{html.escape(lib["integrity"])}" '
                     f'crossorigin="anonymous" referrerpolicy="no-referrer"></script>'
                     for lib in read_json(LIBRARIES_PATH)[KEY_LIBRARIES])


# RQ-GXP-003, DEC-GXP-002: the libraries the Licenses topic names, one badge each
def library_record():
    """Name, version and licence of each library recorded in libraries.json; an empty list when the file is absent."""
    if not LIBRARIES_PATH.is_file():
        return []
    return [{key: lib[key] for key in LIBRARY_KEYS} for lib in read_json(LIBRARIES_PATH)[KEY_LIBRARIES]]


# RQ-GXP-004, DEC-GXP-002: copied from perf_center.version_label() (RQ-TRC-109, RQ-TRC-116, DEC-TRC-061)
def version_label():
    """The version the About name shows, `v.<major>.<minor>`, from the version file; the empty string when the file is absent
    or is not one SemVer 2.0.0 line, so that the name then reads "AGNOS" alone and the run is not failed."""
    try:
        lines = Path(VERSION_PATH).read_text(encoding=ENCODING).splitlines()
    except (OSError, ValueError):
        return ""
    match = SEMVER_RE.match(lines[0]) if len(lines) == 1 else None
    return f"{VERSION_PREFIX}{match.group(1)}.{match.group(2)}" if match else ""


# RQ-TRC-153: JSON safe inside a <script> element, no "<" at all (as the performance center embeds its data)
def embed_json(data):
    return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


# RQ-TRC-145, DEC-TRC-084
def render_page():
    """The page: the template with its markers replaced in one pass, so inserted text is never scanned again."""
    parts = {
        "TOKENS": tokens_css(read_json(TOKENS_PATH)),
        "CSS": STYLE_PATH.read_text(encoding=ENCODING),
        "SCRIPT": SCRIPT_END_RE.sub(r"<\\/\1", SCRIPT_PATH.read_text(encoding=ENCODING)),
        "TITLE": html.escape(PAGE_TITLE),
        "DATA_SCRIPT": html.escape(DATA_SCRIPT_NAME),
        "LIBRARIES": library_scripts(),
        "PRESETS": embed_json(read_json(PRESETS_PATH)),      # RQ-TRC-153, DEC-TRC-093
        "APP_VERSION": html.escape(version_label()),          # RQ-GXP-004, DEC-GXP-002
        "LIBRARY_RECORD": embed_json(library_record()),       # RQ-GXP-003, DEC-GXP-002
    }
    return MARKER_RE.sub(lambda m: parts[m.group(1) or m.group(2)], TEMPLATE_PATH.read_text(encoding=ENCODING))


# RQ-TRC-144, RQ-TRC-145, RQ-TRC-156, DEC-TRC-085, DEC-TRC-088
def write_explorer(graph_path, graph_text):
    """Writes the page and its data script beside the graph file, whose text is given as written; returns the page."""
    page = graph_path.with_name(PAGE_NAME)
    page.write_text(render_page(), encoding=ENCODING, newline="\n")
    graph_path.with_name(DATA_SCRIPT_NAME).write_text(f"{DATA_GLOBAL} = {graph_text.rstrip()};\n", encoding=ENCODING,
                                                      newline="\n")
    return page
