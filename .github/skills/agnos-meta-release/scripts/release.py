#!/usr/bin/env python3
"""agnos-meta-release: a release rehearsed in a folder, without publishing anything.

Implements FTR-MTA-002 after ADR-MTA-002 (DEC-MTA-007): it selects the delivered files of a commit (RQ-MTA-007, RQ-MTA-008),
removes the workshop's IDs from them (RQ-MTA-009), checks the result (RQ-MTA-010), proves it behaves as the workshop does
(RQ-MTA-011) and writes only its output and report (RQ-MTA-006, RQ-MTA-012), the proof working on a temporary clone of the demo.
Python >= 3.10, standard library only. Procedure: ../SKILL.md.
"""
import argparse
import ast
import io
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))    # the layout's copy and its generator, beside this script
import agnos_layout  # noqa: E402  RQ-PLG-036 / DEC-PLG-027: every name of the process folder
import layout  # noqa: E402  RQ-PLG-037 / DEC-PLG-028: the check of the rehearsed commit

ASSETS = Path(__file__).resolve().parent.parent / "assets"
LAYERS_PATH = ASSETS / "layers.json"
MARKETPLACE_PATH = ASSETS / "marketplace.json"
ATTRIBUTES_PATH = ASSETS / "marketplace.gitattributes.txt"
# RQ-PLG-042 / DEC-PLG-034: the plugin's README, read from the commit rehearsed like the version
PLUGIN_README_SOURCE = ".github/skills/agnos-meta-release/assets/plugin-README.md"
# RQ-PLG-046 / DEC-PLG-036: the brand mark's shapes (template.html's brand-mark), its colours read from the commit's tokens
LOGO_TEMPLATE_PATH = ASSETS / "logo-template.svg"
TOKENS_SOURCE = ".github/skills/agnos-perf-center/assets/tokens.json"
BRAND_NAMES = ("tile", "light", "blue", "green", "yellow")
BRAND_TOKEN = "color.brand-{}"
AGENT_TABLE_PATH = ASSETS / "agent-frontmatter.json"
REPORT_CSS_PATH = ASSETS / "report.css"         # RQ-PLG-017 / DEC-PLG-012: only tokens of the perf center
REPORT_PAGE_PATH = ASSETS / "report.html"       # RQ-PLG-016 / DEC-PLG-011
PAGE_SUFFIX = ".report.html"
PAGE_MARKER_RE = re.compile(r"/\*@(TOKENS|CSS|DATA)@\*/")
JSON_IN_HTML = {"<": "\\u003c", ">": "\\u003e", "&": "\\u0026"}     # no text of the report can close its script element
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

INDEX_PATH = f"{agnos_layout.FOLDER}/{agnos_layout.INDEX}"
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
PERF_PAGE = f"{agnos_layout.FOLDER}/{agnos_layout.PERF_CENTER_PAGE}"
PERF_RESULTS = tuple(f"{PERF_PAGE.rsplit('.', 1)[0]}{suffix}" for suffix in (".json", ".data.js")) + (
    f"{agnos_layout.FOLDER}/{agnos_layout.GRAPH_FILE}",)     # RQ-TRC-132 (TASK-TRC-122): the graph agnos-graph built, compared too
INIT_RESULTS = ("CLAUDE.md", "AGENTS.md",
                *(f"{agnos_layout.FOLDER}/{sub}/{agnos_layout.FOLDER_README}" for sub in agnos_layout.SUBFOLDERS))
INDEX_SCRIPT = "agnos-index/scripts/build-index"
INIT_SCRIPT = "agnos-init/scripts/init"
PERF_SCRIPT = "agnos-perf-center/scripts/perf_center.py"
# RQ-PLG-001, RQ-PLG-002, DEC-PLG-001: where the delivered files go, and the marketplace around them.
WORKSHOP_SKILLS = ".github/skills/"
INSTRUCTIONS = ".github/instructions/agnos-sw-eng.instructions.md"
PLUGIN_FOLDER = "plugins/agnos"
PLUGIN_SKILLS = f"{PLUGIN_FOLDER}/skills/"
# RQ-PLG-035 / DEC-PLG-030: the generated skill takes its name from assets/marketplace.json
PROCESS_SKILL_FILE = f"{PLUGIN_SKILLS}{json.loads(MARKETPLACE_PATH.read_text(encoding=ENCODING))['process']['name']}/SKILL.md"
PERF_SCRIPT_FOLDER = f"{PLUGIN_SKILLS}{Path(PERF_SCRIPT).parent.as_posix()}"
SKILL_FILE = "SKILL.md"
CLAUDE_CATALOGUE = ".claude-plugin/marketplace.json"     # RQ-PLG-043 / DEC-PLG-033: the only catalogue
ROOT_MANIFEST = f"{PLUGIN_FOLDER}/plugin.json"
CLAUDE_MANIFEST = f"{PLUGIN_FOLDER}/.claude-plugin/plugin.json"
ATTRIBUTES_FILE = ".gitattributes"
PLUGIN_README = f"{PLUGIN_FOLDER}/README.md"     # RQ-PLG-042 / DEC-PLG-034: the README a tool shows for the plugin
LOGO_KEY = "logo"
LOGO_FILE = "assets/agnos.svg"     # RQ-PLG-046 / DEC-PLG-036: relative to the plugin's folder, as a manifest names it
LOGO_PLACE = f"{PLUGIN_FOLDER}/{LOGO_FILE}"
MARKETPLACE_FILES = (ROOT_MANIFEST, CLAUDE_MANIFEST, CLAUDE_CATALOGUE, ATTRIBUTES_FILE, PLUGIN_README, LOGO_PLACE)
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
EXTERNAL_LINK_RE = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|#)", re.I)
NO_BYTECODE = {"PYTHONDONTWRITEBYTECODE": "1"}     # RQ-PLG-012, DEC-PLG-008: the checks run Python from the output
AGENT_PLUGINS_SCHEMA ="https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
CHANGELOG = "CHANGELOG.md"
USER_DOCUMENTS = {"README.md"}      # RQ-PLG-008: its links lead into the plugin; RQ-PLG-022: the guide is agnos-init's template
# RQ-PLG-006, DEC-PLG-005: an agent defined once, one file per tool.
AGENT_SOURCE_RE = re.compile(r"^\.github/agents/(.+)\.agent\.md$")
AGENT_HEADER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n(.*)\Z", re.S)
CLAUDE_KEY = "claude"
COPILOT_KEY = "copilot"
AGENT_PLACES = {CLAUDE_KEY: f"{PLUGIN_FOLDER}/agents/{{}}.md", COPILOT_KEY: f"{PLUGIN_FOLDER}/com.github.copilot/agents/{{}}.agent.md"}
TOOLS_KEY = "tools"
MODEL_KEY = "model"
MODELS_KEY = "models"
LIST_SEPARATOR = ", "
# RQ-PLG-032 / DEC-PLG-025: the version's single source, and the regular expression of SemVer 2.0.0 (semver.org)
VERSION_FILE = f"{WORKSHOP_SKILLS}agnos-init/assets/templates/VERSION.txt"
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
                       r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
                       r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$")
# RQ-PLG-031 / DEC-PLG-024: the bullets of the changelog's [Unreleased] section, up to the next release heading
UNRELEASED_RE = re.compile(r"^## \[Unreleased\][^\n]*$", re.M | re.I)
NEXT_RELEASE_RE = re.compile(r"^## ", re.M)
BULLET_RE = re.compile(r"^[-*] ", re.M)
UNRELEASED_KEY = "unreleasedEntries"
PLUGINS_KEY = "plugins"
PLUGIN_MANIFESTS = ("plugin.json", ".claude-plugin/plugin.json")
SAME_EVERYWHERE = ("name", "version", "description")
METADATA_KEY = "metadata"
METADATA_VERSION = f"{METADATA_KEY}.version"
# RQ-PLG-045 / DEC-PLG-035: what every plugin declaration lists, and what the catalogue's entry repeats of the plugin
LISTING_REQUIRED = ("author.url", "homepage", "repository", "keywords")
ENTRY_FIELDS = (*SAME_EVERYWHERE, "author", "homepage", "repository", "license", "keywords")
# (fields of the file, fields of each plugin it declares), as documented and observed in the trial of ADR-PLG-001
REQUIRED_FIELDS = {ROOT_MANIFEST: ((), (*SAME_EVERYWHERE, *LISTING_REQUIRED, LOGO_KEY)),
                   CLAUDE_MANIFEST: ((), (*SAME_EVERYWHERE, *LISTING_REQUIRED, LOGO_KEY)),
                   CLAUDE_CATALOGUE: (("name", "owner.name", "owner.email", f"{METADATA_KEY}.description", METADATA_VERSION),
                                      (*SAME_EVERYWHERE, *LISTING_REQUIRED, "source", "license", "category"))}
ROOT_DESCRIPTION = "description"     # RQ-PLG-044: a catalogue holds it in metadata, never at its root
CATALOGUE_SOURCES = {CLAUDE_CATALOGUE: "source"}
FRONT_MATTER_RE = re.compile(r"\A---\r?\n.*?\r?\n---\r?\n\s*", re.S)
PARSE_MESSAGE_LENGTH = 200
EXIT_KEY = "exit"
EXIT_ZERO = b"exit 0"
IS_WINDOWS = os.name == "nt"
POWERSHELL = "powershell"
BASH = "bash"
NODE = "node"
PS_PARSE = ("$e=$null;[void][System.Management.Automation.Language.Parser]::ParseFile($args[0],[ref]$null,[ref]$e);"
            "if($e.Count){$e[0].Message;exit 1}")
TOOL_PARSERS = {".js": (NODE, lambda p: [NODE, "--check", p]),
                ".sh": (BASH, lambda p: [BASH, "-n"]),
                ".ps1": (POWERSHELL, lambda p: [POWERSHELL, "-NoProfile", "-Command", f"& {{{PS_PARSE}}} '{p}'"])}
# Windows may resolve bash to WSL's, which cannot read a Windows path: it gets the text instead.
PARSED_FROM_STDIN = {".sh"}
MARKDOWN_RE = re.compile(r"\.md$", re.I)
NOT_SCANNED_FOR_CITATIONS_RE = re.compile(rf"^{re.escape(agnos_layout.FOLDER)}/|/tests?/|/assets/content/")


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
# RQ-PLG-001 / DEC-PLG-001
def place_of(path):
    """Where a delivered file goes in the marketplace."""
    if path == INSTRUCTIONS:
        return PROCESS_SKILL_FILE
    if path.startswith(WORKSHOP_SKILLS):
        return PLUGIN_SKILLS + path[len(WORKSHOP_SKILLS):]
    return path


# RQ-PLG-002, RQ-PLG-032 / DEC-PLG-025
def release_version(text):
    """The version a `VERSION.txt` file holds, when it is one SemVer 2.0.0 line; None otherwise."""
    lines = text.splitlines()
    return lines[0] if len(lines) == 1 and SEMVER_RE.match(lines[0]) else None


# RQ-PLG-031 / DEC-PLG-024
def unreleased_entries(changelog):
    """How many bullets the changelog's [Unreleased] section holds."""
    found = UNRELEASED_RE.search(changelog)
    if not found:
        return 0
    section = changelog[found.end():]
    after = NEXT_RELEASE_RE.search(section)
    return len(BULLET_RE.findall(section[:after.start()] if after else section))


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding=ENCODING, newline="\n")


# RQ-PLG-046 / DEC-PLG-036
def brand_colours(tokens_text):
    """The five brand colours of a perf-center token file, by name, or None when one is missing."""
    found = json.loads(tokens_text).get("global", {})
    colours = {name: found.get(BRAND_TOKEN.format(name)) for name in BRAND_NAMES}
    return colours if all(colours.values()) else None


# RQ-PLG-046 / DEC-PLG-036
def commit_brand(repo):
    """The brand colours of the commit rehearsed, or None when its token file is absent, unreadable or lacks one."""
    try:
        return brand_colours(git(repo, "show", f"HEAD:{TOKENS_SOURCE}").decode(ENCODING))
    except (subprocess.CalledProcessError, ValueError):
        return None


def write_marketplace(output, version, readme, brand):
    """The catalogues, the manifests, the attributes, the plugin's README and its logo: same name, version and
    description in each."""
    said = json.loads(MARKETPLACE_PATH.read_text(encoding=ENCODING))
    plugin = {**said["plugin"], "version": version, LOGO_KEY: LOGO_FILE}     # RQ-PLG-046: declared by both manifests
    # RQ-PLG-045 / DEC-PLG-035: the entry repeats the plugin's fields, plus its own
    listed = {**{key: plugin[key] for key in ENTRY_FIELDS}, "source": f"./{PLUGIN_FOLDER}", **said["entry"]}
    marketplace = said["marketplace"]
    # RQ-PLG-044 / DEC-PLG-035: the description and the version in metadata, as at the plugin's level
    catalogue = {**marketplace, METADATA_KEY: {**marketplace[METADATA_KEY], "version": version}, PLUGINS_KEY: [listed]}
    write_json(output / ROOT_MANIFEST, {"$schema": AGENT_PLUGINS_SCHEMA, **plugin})
    write_json(output / CLAUDE_MANIFEST, plugin)
    write_json(output / CLAUDE_CATALOGUE, catalogue)
    (output / ATTRIBUTES_FILE).write_bytes(ATTRIBUTES_PATH.read_bytes())
    (output / PLUGIN_README).write_bytes(readme)     # RQ-PLG-042 / DEC-PLG-034
    (output / LOGO_PLACE).parent.mkdir(parents=True, exist_ok=True)     # RQ-PLG-046 / DEC-PLG-036
    (output / LOGO_PLACE).write_text(LOGO_TEMPLATE_PATH.read_text(encoding=ENCODING).format(**brand),
                                     encoding=ENCODING, newline="\n")


# RQ-PLG-042 / DEC-PLG-034
def readme_problems(output):
    """Each relative link of the plugin's README that leads to no file of the plugin."""
    plugin = (output / PLUGIN_FOLDER).resolve()
    text = (output / PLUGIN_README).read_text(encoding=ENCODING)
    problems = []
    for link in LINK_RE.findall(text):
        if EXTERNAL_LINK_RE.match(link):
            continue
        target = (plugin / link.split("#")[0]).resolve()
        if plugin not in target.parents or not target.is_file():
            problems.append(f"{PLUGIN_README}: its link {link} leads to no file of the plugin")
    return problems


# RQ-PLG-003 / DEC-PLG-002
def process_skill(text):
    """The process instructions as a skill."""
    said = json.loads(MARKETPLACE_PATH.read_text(encoding=ENCODING))["process"]
    return f'---\nname: {said["name"]}\ndescription: "{said["description"]}"\n---\n\n{FRONT_MATTER_RE.sub("", text)}'


# RQ-PLG-006 / DEC-PLG-005
def agent_parts(text):
    """(the header's lines, the body) of an agent definition."""
    found = AGENT_HEADER_RE.match(text)
    return (found.group(1).splitlines(), found.group(2)) if found else ([], text)


def header_value(line):
    return line.partition(":")[2].strip()


def agent_values(lines):
    """The tools and the model a definition names."""
    said = {line.partition(":")[0]: header_value(line) for line in lines}
    return [tool.strip() for tool in said.get(TOOLS_KEY, "").split(",") if tool.strip()], said.get(MODEL_KEY)


def agent_refusals(path, text, table):
    """What the table does not know in this definition."""
    tools, model = agent_values(agent_parts(text)[0])
    unknown = [tool for tool in tools if tool not in table[TOOLS_KEY]]
    if model and model not in table[MODELS_KEY]:
        unknown.append(model)
    return [f"{path}: {value} is not in {AGENT_TABLE_PATH.name}" for value in unknown]


def agent_file(text, tool, table):
    """A definition as this tool reads it: its header translated, its body unchanged."""
    lines, body = agent_parts(text)
    tools, model = agent_values(lines)
    header = [line for line in lines if line.partition(":")[0] not in (TOOLS_KEY, MODEL_KEY)]
    if tools:
        header.append(f"{TOOLS_KEY}: {LIST_SEPARATOR.join(name for tool_name in tools for name in table[TOOLS_KEY][tool_name][tool])}")
    if model and table[MODELS_KEY][model][tool]:
        header.append(f"{MODEL_KEY}: {table[MODELS_KEY][model][tool]}")
    return "---\n" + "\n".join(header) + "\n---\n" + body


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
        if rules and name != ATTRIBUTES_FILE and layer_of(name, rules) == LAYER_META:    # the workshop's stays, this one is the marketplace's
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


def adapted(path, text):
    """A delivered text as the marketplace holds it (RQ-PLG-003, RQ-PLG-008)."""
    if path == INSTRUCTIONS:
        return process_skill(text)
    if path in USER_DOCUMENTS:
        return text.replace(INSTRUCTIONS, PROCESS_SKILL_FILE).replace(WORKSHOP_SKILLS, PLUGIN_SKILLS)
    return text


def contents_of(path, text, table):
    """The marketplace's file or files for a delivered path, with their text (None for a binary file)."""
    agent = AGENT_SOURCE_RE.match(path)
    if agent:
        return {place.format(agent.group(1)): agent_file(text, tool, table) for tool, place in AGENT_PLACES.items()}
    return {place_of(path): text}


def write_contents(output, contents, data, mode):
    """Writes the files and returns their places."""
    for place, content in contents.items():
        target = output / place
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data if content is None else content.encode(ENCODING))
        if mode == EXECUTABLE_MODE:
            os.chmod(target, target.stat().st_mode | stat.S_IXUSR)
    return list(contents)


def write_delivered(repo, output, entries, pattern, left_out):
    """Writes each delivered file without the workshop's IDs, and returns what the report says of them and the places written."""
    findings = {"removed": {}, "toRead": [], "mentions": []}
    placed = []
    delivered_names = {Path(path).name for path, _ in entries}
    table = json.loads(AGENT_TABLE_PATH.read_text(encoding=ENCODING))
    for path, mode in entries:
        data = git(repo, "show", f"HEAD:{path}")
        try:
            text, count, to_read = remove_ids(data.decode(ENCODING), pattern)
            text = adapted(path, text)
        except UnicodeDecodeError:      # a binary file: RQ-MTA-010 still reads it
            text = None
        placed += write_contents(output, contents_of(path, text, table), data, mode)
        if text is not None:
            if count:
                findings["removed"][path] = count
            findings["toRead"] += [{"file": path, "line": line, "text": said} for line, said in to_read]
            findings["mentions"] += [{"file": path, "line": line, "what": what}
                                     for line, what in mentions(text, left_out, delivered_names)]
    return findings, placed


# RQ-PLG-012 / DEC-PLG-008
def stray_files(output, declared):
    """The files on disk that were neither delivered nor generated."""
    on_disk = {p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file()}
    return [f"{name}: neither delivered nor generated" for name in sorted(on_disk - set(declared))]


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
        data = path.read_bytes() if path.suffix in PARSED_FROM_STDIN else None
        done = subprocess.run(TOOL_PARSERS[path.suffix][1](str(path)), input=data, capture_output=True)
        if done.returncode:
            return (done.stdout + done.stderr).decode(ENCODING, errors="replace").strip()[:PARSE_MESSAGE_LENGTH]
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


def compare_runs(baseline, output, workspace, runners):
    """Runs each skill from the workshop's files and from the output, and names the results that differ."""
    problems = []
    for label, runner in runners:
        expected = runner(baseline, workspace)
        obtained = runner(output, workspace)
        if expected.get(EXIT_KEY, EXIT_ZERO) != EXIT_ZERO:     # failing alike would prove nothing
            problems.append(f"{label}: {expected[EXIT_KEY].decode(ENCODING)} from the workshop's own files")
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
    done = subprocess.run(command, cwd=folder, capture_output=True, text=True, errors="replace", env={**os.environ, **NO_BYTECODE})
    return f"exit {done.returncode}".encode(ENCODING)


def run_index(toolkit, workspace):
    clone = workspace / "demo"
    code = run_tool(script_command(toolkit, INDEX_SCRIPT, [], []), clone)
    return {"exit": code, INDEX_PATH: (clone / INDEX_PATH).read_bytes()}


def run_perf_center(toolkit, workspace):
    clone = workspace / "demo"
    script = str(Path(toolkit) / PERF_SCRIPT)
    code = run_tool([sys.executable, script, "--process", agnos_layout.FOLDER, "--sources", ".", "--call-graph", "--history",
                     "--generated-at", FIXED_TIME, "--out", PERF_PAGE, "--rebuild"], clone)   # TASK-TRC-122: each toolkit builds its graph
    results = {"exit": code}
    for name in PERF_RESULTS:
        path = clone / name
        results[name] = path.read_bytes() if path.exists() else None
        path.unlink(missing_ok=True)
    (clone / PERF_PAGE).unlink(missing_ok=True)     # left there, the next run would scan it as a source
    return results


def run_init(toolkit, workspace):
    target = Path(tempfile.mkdtemp(dir=workspace))
    code = run_tool(script_command(toolkit, INIT_SCRIPT, ["-Target", str(target)], ["--target", str(target)]), target)
    results = {"exit": code}
    for name in INIT_RESULTS:
        path = target / name
        results[name] = path.read_bytes() if path.exists() else None
    return results


RUNNERS = (("agnos-index", run_index), ("agnos-perf-center", run_perf_center), ("agnos-init", run_init))


# RQ-PLG-002, RQ-PLG-015 / DEC-PLG-010: the manifests checked by the release itself, the same on any machine; each tool's own
# validation and a real install stay in agnos-meta-plugin-proof (RQ-PLG-010).
def field(data, dotted):
    """The value at a dotted path of a JSON object, or None."""
    for key in dotted.split("."):
        data = data.get(key) if isinstance(data, dict) else None
    return data


def plugin_folder_problem(output, name, source):
    folder = (output / source).resolve() if isinstance(source, str) else None
    if folder is None or not folder.is_dir() or not any((folder / manifest).is_file() for manifest in PLUGIN_MANIFESTS):
        return f"{name}: its plugin source {source} is no plugin folder of the output"
    return None


# RQ-PLG-044 / DEC-PLG-035
def catalogue_metadata_problems(name, data, entries):
    """A description at the catalogue's root, and a metadata version other than its plugins'."""
    problems = [f"{name}: {ROOT_DESCRIPTION} at its root, not in {METADATA_KEY}"] if ROOT_DESCRIPTION in data else []
    version = field(data, METADATA_VERSION)
    return problems + [f"{name}: {METADATA_VERSION} differs from its plugin's version"
                       for entry in entries if version is not None and field(entry, "version") != version]


# RQ-PLG-046 / DEC-PLG-036
def logo_problem(output, name, manifest):
    """A manifest's logo that names no file of the plugin's folder, or None."""
    logo = manifest.get(LOGO_KEY)
    if isinstance(logo, str) and not (output / PLUGIN_FOLDER / logo).is_file():
        return f"{name}: its {LOGO_KEY} {logo} is no file of the plugin"
    return None


def manifest_problems(output):
    """What the four manifests and catalogues lack, name wrongly, or say differently."""
    problems, said = [], {}
    for name, required in REQUIRED_FIELDS.items():
        try:
            data = json.loads((output / name).read_text(encoding=ENCODING))
        except (OSError, ValueError) as error:
            problems.append(f"{name}: not readable as JSON ({error})")
            continue
        entries = data.get(PLUGINS_KEY) if name in CATALOGUE_SOURCES else [data]
        if not isinstance(entries, list) or not entries:
            problems.append(f"{name}: no plugin declared")
            continue
        problems += [f"{name}: no {key}" for key in required[0] if field(data, key) in (None, "")]
        if name in CATALOGUE_SOURCES:     # RQ-PLG-044 / DEC-PLG-035
            problems += catalogue_metadata_problems(name, data, entries)
        for entry in entries:
            problems += [f"{name}: no {key} for a plugin" for key in required[1] if field(entry, key) in (None, "")]
            problems.append(plugin_folder_problem(output, name, field(entry, CATALOGUE_SOURCES[name]))
                            if name in CATALOGUE_SOURCES else logo_problem(output, name, entry))
            said[name] = {key: entry.get(key) for key in SAME_EVERYWHERE}
    reference = said.get(ROOT_MANIFEST)
    problems += [f"{name}: {key} differs from {ROOT_MANIFEST}" for name, values in said.items() if reference
                 for key in SAME_EVERYWHERE if values[key] != reference[key]]
    return [problem for problem in problems if problem]


# RQ-PLG-017 / DEC-PLG-012: the design system of the commit rehearsed, by its own perf center; -B keeps the output clean.
TOKENS_PROGRAM = "import sys; sys.path.insert(0, sys.argv[1]); import perf_center as p; print(p.tokens_css(p.load_tokens(p.TOKENS_PATH)))"


def page_tokens(output):
    """The custom properties of the report page, compiled from the output's perf-center tokens."""
    scripts = output / PERF_SCRIPT_FOLDER
    done = subprocess.run([sys.executable, "-B", "-c", TOKENS_PROGRAM, str(scripts)], capture_output=True, text=True,
                          encoding=ENCODING, env={**os.environ, **NO_BYTECODE}, check=True)
    return done.stdout


def report_tokens(output):
    """The page's tokens, and why they could not be compiled; an output without the perf center gets an unstyled page."""
    if not (output / PERF_SCRIPT_FOLDER / Path(PERF_SCRIPT).name).is_file():
        return "", []
    try:
        return page_tokens(output), []
    except subprocess.CalledProcessError as error:
        return "", [f"report page: the perf center's tokens do not compile: {error.stderr.strip()[-PARSE_MESSAGE_LENGTH:]}"]


# RQ-PLG-016 / DEC-PLG-011
def report_page(report, tokens):
    """The report as one page: the template's markers replaced in one pass, so that no value is read as a marker."""
    data = json.dumps(report, ensure_ascii=False)
    for character, escaped in JSON_IN_HTML.items():
        data = data.replace(character, escaped)
    parts = {"TOKENS": tokens, "CSS": REPORT_CSS_PATH.read_text(encoding=ENCODING).strip(), "DATA": data}
    return PAGE_MARKER_RE.sub(lambda marker: parts[marker.group(1)], REPORT_PAGE_PATH.read_text(encoding=ENCODING))


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
        problems += compare_runs(baseline / WORKSHOP_SKILLS, output / PLUGIN_SKILLS, workspace, RUNNERS)
    return problems


def refused(message):
    """A refusal before anything is written: no report."""
    return fail(message), None


def layout_findings(repo):
    """layout.py --check run on the files of HEAD, each finding naming its file and line; a commit holding no layout.json
    has nothing to check (RQ-PLG-037, DEC-PLG-028)."""
    try:
        git(repo, "cat-file", "-e", f"HEAD:{layout.LAYOUT_PATH.as_posix()}")
    except subprocess.CalledProcessError:
        return []
    with tempfile.TemporaryDirectory() as folder:
        with tarfile.open(fileobj=io.BytesIO(git(repo, "archive", "--format=tar", "HEAD"))) as archive:
            archive.extractall(folder, filter="data")
        root = Path(folder)
        return [f"layout: {finding}" for finding in layout.check(root, layout.load(root))]


def rehearse(repo, output, demo, proof):
    """Classify every file before writing any, so that a refusal delivers nothing. Returns the exit code and the report, if written."""
    rules = load_rules()
    entries = tracked_files(repo)
    unknown = [path for path, _ in entries if layer_of(path, rules) is None]
    if unknown:
        return refused(f"no layer in {LAYERS_PATH.name} for: {', '.join(unknown)}")
    delivered = [entry for entry in entries if layer_of(entry[0], rules) == LAYER_DELIVERED]
    table = json.loads(AGENT_TABLE_PATH.read_text(encoding=ENCODING))
    refusals = [refusal for path, _ in delivered if AGENT_SOURCE_RE.match(path)
                for refusal in agent_refusals(path, git(repo, "show", f"HEAD:{path}").decode(ENCODING), table)]
    if refusals:
        return refused("; ".join(refusals))
    if INSTRUCTIONS not in [path for path, _ in delivered]:
        return refused(f"no {INSTRUCTIONS} at HEAD: the plugin would hold no process")
    delivered_paths = [path for path, _ in delivered]
    version = release_version(git(repo, "show", f"HEAD:{VERSION_FILE}").decode(ENCODING)) if VERSION_FILE in delivered_paths else None
    if not version:
        return refused(f"{VERSION_FILE} at HEAD is absent or not one SemVer 2.0.0 line: the plugin would have no version")
    try:
        readme = git(repo, "show", f"HEAD:{PLUGIN_README_SOURCE}")     # RQ-PLG-042 / DEC-PLG-034
    except subprocess.CalledProcessError:
        return refused(f"no {PLUGIN_README_SOURCE} at HEAD: the plugin would have no README")
    brand = commit_brand(repo)
    if not brand:
        return refused(f"no brand colours in {TOKENS_SOURCE} at HEAD: the plugin would have no logo")
    unreleased = unreleased_entries(git(repo, "show", f"HEAD:{CHANGELOG}").decode(ENCODING)) if CHANGELOG in delivered_paths else 0
    left_out = [path for path, _ in entries if layer_of(path, rules) == LAYER_META]
    try:
        pattern = id_pattern(index_trigrams(git(repo, "show", f"HEAD:{INDEX_PATH}").decode(ENCODING)))
    except subprocess.CalledProcessError:
        return refused(f"no {INDEX_PATH} at HEAD: the IDs to remove cannot be known")
    drifted = layout_findings(repo)
    output.mkdir(parents=True, exist_ok=True)
    findings, placed = write_delivered(repo, output, delivered, pattern, left_out)
    write_marketplace(output, version, readme, brand)
    left = check_output(output, pattern, rules)
    unsound = manifest_problems(output) + readme_problems(output)
    unproved = proof(repo, output, demo)
    tokens, unstyled = report_tokens(output)
    problems = drifted + left + unsound + unproved + unstyled + stray_files(output, [*placed, *MARKETPLACE_FILES])
    report = {"commit": git(repo, "rev-parse", "HEAD").decode(ENCODING).strip(), "delivered": [path for path, _ in delivered],
              "version": version, UNRELEASED_KEY: unreleased, "leftOut": left_out, **findings, "idsOutsideComments": workshop_citations(repo, entries, pattern),
              "checks": {"noIdLeft": not left, "manifests": not unsound, "sameBehaviour": not unproved}, "problems": problems}
    Path(f"{output}{REPORT_SUFFIX}").write_text(json.dumps(report, indent=2) + "\n", encoding=ENCODING, newline="\n")
    Path(f"{output}{PAGE_SUFFIX}").write_text(report_page(report, tokens), encoding=ENCODING, newline="\n")
    return (EXIT_FAILED if problems else EXIT_OK), report


# RQ-PLG-014 / DEC-PLG-009: one stream, so that what is said keeps its order whatever the terminal does with two.
PRINTED = (("problems", None), ("toRead", "text"), ("mentions", "what"), ("idsOutsideComments", "id"))


def print_findings(report):
    if report[UNRELEASED_KEY]:      # RQ-PLG-031 / DEC-PLG-024: said, failing nothing
        print(f"unreleased: {report[UNRELEASED_KEY]} entries, version {report['version']} delivered")
    for key, field in PRINTED:
        for item in report[key]:
            print(f"{key}: {item}" if field is None else f"{key}: {item['file']}:{item['line']}: {item[field]}")


def last_line(code, output, report, started):
    took = f"in {time.perf_counter() - started:{DURATION_FORMAT}} s"
    if report is None:
        return f"agnos-meta-release: exit={code}, nothing written {took}"
    files = sum(1 for path in output.rglob("*") if path.is_file())
    return (f"agnos-meta-release: exit={code}, {files} files, {sum(report['removed'].values())} IDs removed, "
            f"{len(report['toRead'])} lines to read, {output} written {took}")


def parse_args(argv):
    parser = argparse.ArgumentParser(prog="release.py", description="AGNOS release rehearsal: writes the marketplace in a folder, publishing nothing")
    parser.add_argument("--dry-run", action="store_true", help="rehearse; the only mode that exists")
    parser.add_argument("--output", required=True, help="folder to write, outside the repository and empty")
    parser.add_argument("--repo", default=".", help="repository root (default: the current folder)")
    parser.add_argument("--demo", help="the demo repository (default: agnos-lightweight-process.demo beside the repository)")
    return parser.parse_args(argv)


def run_rehearsal(args, output, proof):
    """The exit code and the report, if one was written."""
    if not args.dry_run:    # RQ-MTA-006 / DEC-MTA-011
        return refused("only the rehearsal exists: call it with --dry-run; publishing is not available")
    try:
        repo = Path(git(args.repo, "rev-parse", "--show-toplevel").decode(ENCODING).strip()).resolve()
    except subprocess.CalledProcessError:
        return refused(f"{args.repo} is not a git repository")
    refusal = output_refusal(repo, output)
    if refusal:
        return refused(refusal)
    return rehearse(repo, output, args.demo, proof)


def main(argv=None, proof=prove):
    args = parse_args(argv)
    started = time.perf_counter()
    output = Path(args.output).resolve()
    code, report = run_rehearsal(args, output, proof)
    sys.stderr.flush()
    if report is not None:
        print_findings(report)
    print(last_line(code, output, report, started))     # RQ-PLG-014: always the last line
    return code


if __name__ == "__main__":
    sys.exit(main())
